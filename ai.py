import os
import json
import base64
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from litellm import completion
import streamlit as st

# --- 1. SETUP ---
load_dotenv()

ZAI_KEY = os.environ.get("ZHIPUAI_API_KEY")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")

zai_client = OpenAI(
    api_key=ZAI_KEY,
    base_url="https://api.z.ai/api/paas/v4/"
)

# Setup Paths
CHAT_DIR = "chats"
os.makedirs(CHAT_DIR, exist_ok=True)
MEMORY_FILE = "memory_bank.json"

st.set_page_config(page_title="My AI Stack", layout="wide")
st.title("🚀 Claude + GLM Stack")

# Initialize Uploaded File variable
uploaded_file = None

# --- 2. SIDEBAR ---
# --- MODEL SELECTOR (TOP) ---
model_choice = st.sidebar.radio("Select Engine:", ("GLM-4.7 (Free/Fast)", "Claude 3.5 (Paid/Smart/Vision)"))

# --- VISION MODE (ONLY SHOW IF CLAUDE) ---
if "Claude" in model_choice:
    st.sidebar.title("📸 Vision Mode")
    st.sidebar.caption("Upload a screenshot here to ask Claude about it.")
    uploaded_file = st.sidebar.file_uploader("Upload Screenshot", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        st.sidebar.success("Image Loaded! Ask Claude a question in the chat.")
    else:
        st.sidebar.info("No image selected (Text Mode)")
else:
    st.sidebar.caption("GLM is Text-Only. Switch to Claude to use Vision.")

st.sidebar.divider()

# --- 3. THE MEMORY ENGINE (SILENT) ---

def get_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                mem = json.load(f)
                if len(mem) > 20: return mem[-20:]
                return mem
        except: return []
    return []

def update_memory(user_input, ai_response):
    """
    Handles 3 modes silently (No UI).
    1. EXPLICIT FORGET
    2. EXPLICIT REMEMBER
    3. AUTO LEARN (With Deduplication)
    """
    existing_facts = get_memory()
    text_lower = f"{user_input} {ai_response}".lower()
    
    updated_memory = existing_facts

    # --- MODE 1: EXPLICIT FORGET ---
    if "forget" in text_lower or "delete" in text_lower or "erase" in text_lower:
        prompt = f"""
        The user wants to forget something. Look at their input.
        Return a JSON list of facts to KEEP (Remove the relevant ones).
        Existing Facts: {json.dumps(existing_facts)}
        User Input: {user_input}
        """
        try:
            response = zai_client.chat.completions.create(
                model="glm-4.7-flash",
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.choices[0].message.content
            clean = raw.strip()
            if "```json" in clean: clean = clean.split("```json")[1].split("```")[0]
            updated_memory = json.loads(clean)
        except:
            pass
        # Save silently
        with open(MEMORY_FILE, 'w') as f:
            json.dump(updated_memory, f)
        return

    # --- MODE 2: EXPLICIT REMEMBER ---
    if "remember" in text_lower or "new name is" in text_lower or "my name is" in text_lower:
        prompt = f"""
        Extract the specific fact the user wants remembered.
        User: {user_input}
        Return ONLY a JSON list with the new fact.
        """
        try:
            response = zai_client.chat.completions.create(
                model="glm-4.7-flash",
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.choices[0].message.content
            clean = raw.strip()
            if "```json" in clean: clean = clean.split("```json")[1].split("```")[0]
            new_facts = json.loads(clean)
            if not isinstance(new_facts, list): new_facts = []
            
            for fact in new_facts:
                if fact not in updated_memory:
                    updated_memory.append(fact)
        except:
            pass
        # Save silently
        with open(MEMORY_FILE, 'w') as f:
            json.dump(updated_memory, f)
        return

    # --- MODE 3: AUTO LEARN (Background) ---
    prompt = f"""
    Extract NEW facts about the user from this text.
    Return ONLY a JSON list.
    Existing Knowledge (DO NOT REPEAT): {json.dumps(existing_facts)}
    
    Text: {user_input}
    AI Response: {ai_response}
    """
    try:
        response = zai_client.chat.completions.create(
            model="glm-4.7-flash",
            messages=[{"role": "user", "content": prompt}]
        )
        raw_text = response.choices[0].message.content
        clean_json = raw_text.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0]
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0]
        
        try:
            new_facts = json.loads(clean_json)
            if not isinstance(new_facts, list): new_facts = []
        except:
            new_facts = []
            
        for fact in new_facts:
            if fact not in updated_memory:
                updated_memory.append(fact)
        
        with open(MEMORY_FILE, 'w') as f:
            json.dump(updated_memory, f)
            
    except Exception as e:
        pass

# --- 4. CHAT HISTORY ---
st.sidebar.title("💾 Chat History")

chat_files = [f for f in os.listdir(CHAT_DIR) if f.endswith('.json')]
chat_files.sort(reverse=True)

if st.sidebar.button("➕ New Chat"):
    st.session_state['current_chat_id'] = None
    st.session_state.messages = []
    st.rerun()

selected_chat = st.sidebar.selectbox("Previous Chats", options=["Select a chat..."] + chat_files)

if st.sidebar.button("🗑️ Delete Current Chat"):
    if st.session_state['current_chat_id']:
        file_to_delete = os.path.join(CHAT_DIR, st.session_state['current_chat_id'])
        if os.path.exists(file_to_delete):
            os.remove(file_to_delete)
        st.session_state['current_chat_id'] = None
        st.session_state.messages = []
        st.rerun()

if 'current_chat_id' not in st.session_state:
    st.session_state['current_chat_id'] = None
    st.session_state.messages = []

if selected_chat and selected_chat != "Select a chat...":
    if selected_chat != st.session_state.get('current_chat_id'):
        file_path = os.path.join(CHAT_DIR, selected_chat)
        with open(file_path, 'r') as f:
            st.session_state.messages = json.load(f)
        st.session_state['current_chat_id'] = selected_chat
        st.rerun()

# --- 5. HELPER: TRIM HISTORY ---
def trim_history(messages, limit=20):
    return messages[-limit:]

# --- 6. DISPLAY CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 7. INPUT & VISION PROCESSING ---
if prompt := st.chat_input("Ask a question..."):
    
    has_image = uploaded_file is not None

    if has_image:
        if "GLM" in model_choice:
            st.error("🚫 **GLM is text-only!** Please switch sidebar to **Claude** to analyze screenshots.")
            st.stop()
        if not prompt:
            prompt = "What is this?"

    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        if has_image:
            st.image(uploaded_file, caption="Uploaded Screenshot")
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        api_messages = trim_history(st.session_state.messages)
        memories = get_memory() # Get memory silently for context
        
        # --- VISION MODE LOGIC ---
        if has_image:
            base64_image = base64.b64encode(uploaded_file.read()).decode('utf-8')
            
            vision_message = [
                {
                    "type": "image", 
                    "source": {
                        "type": "base64", 
                        "media_type": uploaded_file.type, 
                        "data": base64_image
                    }
                },
                {
                    "type": "text", 
                    "text": f"Context about user: {json.dumps(memories)}. \n\nUser Question: {prompt}"
                }
            ]
            
            try:
                response = completion(
                    model="anthropic/claude-3-5-sonnet-20240620",
                    messages=api_messages + [vision_message],
                    api_key=ANTHROPIC_KEY
                )
                full_response = response.choices[0]['message']['content']
            except Exception as e:
                full_response = f"Claude Error: {e}"

        # --- TEXT MODE LOGIC ---
        else:
            memory_string = ". ".join(memories)
            system_prompt = f"Here is what you know about user: {memory_string}\n\nConversation:"
            api_messages.insert(0, {"role": "system", "content": system_prompt})

            if "GLM" in model_choice:
                try:
                    response = zai_client.chat.completions.create(
                        model="glm-4.7-flash",
                        messages=api_messages
                    )
                    full_response = response.choices[0].message.content
                except Exception as e:
                    full_response = f"GLM Error: {e}"

            elif "Claude" in model_choice:
                if not ANTHROPIC_KEY:
                    full_response = "⚠️ No Claude Key found."
                else:
                    try:
                        response = completion(
                            model="anthropic/claude-3-5-sonnet-20240620",
                            messages=api_messages,
                            api_key=ANTHROPIC_KEY
                        )
                        full_response = response.choices[0]['message']['content']
                    except Exception as e:
                        full_response = f"Claude Error: {e}"

        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # --- SILENT MEMORY UPDATE ---
    update_memory(prompt, full_response)

    # SAVE CHAT
    if st.session_state['current_chat_id'] is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}.json"
        st.session_state['current_chat_id'] = filename
    
    file_path = os.path.join(CHAT_DIR, st.session_state['current_chat_id'])
    with open(file_path, 'w') as f:
        json.dump(st.session_state.messages, f)
