import os
import json
import base64
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from litellm import completion
import streamlit as st
from streamlit_ace import st_ace

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
ARCHIVE_FILE = "chat_archive.json"

st.set_page_config(page_title="My AI Stack", layout="wide")
st.title("🚀 Claude + GLM Stack")

# --- 2. STATE INIT ---
if 'tab' not in st.session_state:
    st.session_state['tab'] = 'Chat' # Options: Chat, Terminal, Code

uploaded_file = None

# --- 3. SIDEBAR ---
# --- MODEL SELECTOR ---
model_choice = st.sidebar.radio("Select Engine:", ("GLM-4.7 (Free/Fast)", "Claude 3.5 (Paid/Smart/Vision)"))

# --- VISION MODE ---
if "Claude" in model_choice and st.session_state['tab'] == 'Chat':
    st.sidebar.title("📸 Vision Mode")
    st.sidebar.caption("Upload a screenshot here to ask Claude about it.")
    uploaded_file = st.sidebar.file_uploader("Upload Screenshot", type=['png', 'jpg', 'jpeg'])
    if uploaded_file:
        st.sidebar.success("Image Loaded!")
    else:
        st.sidebar.info("No image selected")
elif "GLM" in model_choice and st.session_state['tab'] == 'Chat':
    st.sidebar.caption("Switch to Claude for Vision.")

st.sidebar.divider()

# --- TAB NAVIGATION ---
st.sidebar.title("🎛 Control Center")
if st.sidebar.button("💬 Chat"):
    st.session_state['tab'] = 'Chat'
    st.rerun()
if st.sidebar.button("💻 Terminal"):
    st.session_state['tab'] = 'Terminal'
    st.rerun()
if st.sidebar.button("📝 Code Editor"):
    st.session_state['tab'] = 'Code'
    st.rerun()

st.sidebar.divider()

# --- CHAT HISTORY & ARCHIVE (ONLY IN CHAT TAB) ---
if st.session_state['tab'] == 'Chat':
    
    # 3a. ARCHIVAL SYSTEM
    def manage_archive():
        chat_files = sorted([f for f in os.listdir(CHAT_DIR) if f.endswith('.json')])
        if len(chat_files) > 10:
            oldest_file = chat_files[0]
            file_path = os.path.join(CHAT_DIR, oldest_file)
            with open(file_path, 'r') as f:
                chat_history = json.load(f)
            prompt_text = "Empty Chat"
            if len(chat_history) > 0:
                start = chat_history[0]['content'][:200]
                end = chat_history[-1]['content'][:200]
                prompt_text = f"Start: {start} ... End: {end}"
            try:
                summary_response = zai_client.chat.completions.create(
                    model="glm-4.7-flash",
                    messages=[{"role": "user", "content": f"Summarize in 3 bullets. Date: {oldest_file}. Context: {prompt_text}"}]
                )
                summary = summary_response.choices[0].message.content
            except:
                summary = "Summary failed."
            archive = []
            if os.path.exists(ARCHIVE_FILE):
                with open(ARCHIVE_FILE, 'r') as f:
                    archive = json.load(f)
            archive.insert(0, {"date": oldest_file, "summary": summary})
            if len(archive) > 50:
                archive = archive[:50]
            with open(ARCHIVE_FILE, 'w') as f:
                json.dump(archive, f)
            os.remove(file_path)

    # 3b. MEMORY ENGINE
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
        existing_facts = get_memory()
        text_lower = f"{user_input} {ai_response}".lower()
        updated_memory = existing_facts
        
        if "forget" in text_lower or "delete" in text_lower or "erase" in text_lower:
            prompt = f"Return JSON list of facts to KEEP. Existing: {json.dumps(existing_facts)} User: {user_input}"
            try:
                response = zai_client.chat.completions.create(model="glm-4.7-flash", messages=[{"role": "user", "content": prompt}])
                clean = response.choices[0].message.content.strip()
                if "```json" in clean: clean = clean.split("```json")[1].split("```")[0]
                updated_memory = json.loads(clean)
            except: pass
            with open(MEMORY_FILE, 'w') as f:
                json.dump(updated_memory, f)
            return

        if "remember" in text_lower or "new name is" in text_lower or "my name is" in text_lower:
            prompt = f"Extract fact. JSON list. User: {user_input}"
            try:
                response = zai_client.chat.completions.create(model="glm-4.7-flash", messages=[{"role": "user", "content": prompt}])
                clean = response.choices[0].message.content.strip()
                if "```json" in clean: clean = clean.split("```json")[1].split("```")[0]
                new_facts = json.loads(clean)
                if not isinstance(new_facts, list): new_facts = []
                for fact in new_facts:
                    if fact not in updated_memory:
                        updated_memory.append(fact)
            except: pass
            with open(MEMORY_FILE, 'w') as f:
                json.dump(updated_memory, f)
            return

        prompt = f"Extract NEW facts. Existing: {json.dumps(existing_facts)} Text: {user_input} AI: {ai_response}"
        try:
            response = zai_client.chat.completions.create(model="glm-4.7-flash", messages=[{"role": "user", "content": prompt}])
            clean = response.choices[0].message.content.strip()
            if "```json" in clean: clean = clean.split("```json")[1].split("```")[0]
            try:
                new_facts = json.loads(clean)
                if not isinstance(new_facts, list): new_facts = []
            except: new_facts = []
            for fact in new_facts:
                if fact not in updated_memory:
                    updated_memory.append(fact)
            with open(MEMORY_FILE, 'w') as f:
                json.dump(updated_memory, f)
        except: pass

    # 3c. SIDEBAR UI
    st.sidebar.title("💾 Chat History")
    st.sidebar.caption("Archives old chats after 10.")
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

    archive_data = []
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, 'r') as f:
            archive_data = json.load(f)
    
    with st.sidebar.expander("📜 Archived Wisdom"):
        if not archive_data:
            st.sidebar.caption("No archives yet.")
        else:
            for item in archive_data[:5]:
                st.sidebar.markdown(f"**{item['date']}**")
                st.sidebar.caption(f"🔹 {item['summary']}")

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

    def trim_history(messages, limit=20):
        return messages[-limit:]

    # 3d. CHAT INPUT LOGIC
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
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
            memories = get_memory()
            
            if has_image:
                base64_image = base64.b64encode(uploaded_file.read()).decode('utf-8')
                vision_message = [
                    {"type": "image", "source": {"type": "base64", "media_type": uploaded_file.type, "data": base64_image}},
                    {"type": "text", "text": f"Context: {json.dumps(memories)}. \n\nQuestion: {prompt}"}
                ]
                try:
                    response = completion(model="anthropic/claude-3-5-sonnet-20240620", messages=api_messages + [vision_message], api_key=ANTHROPIC_KEY)
                    full_response = response.choices[0]['message']['content']
                except Exception as e:
                    full_response = f"Claude Error: {e}"
            else:
                memory_string = ". ".join(memories)
                system_prompt = f"Here is what you know about user: {memory_string}\n\nConversation:"
                api_messages.insert(0, {"role": "system", "content": system_prompt})
                if "GLM" in model_choice:
                    try:
                        response = zai_client.chat.completions.create(model="glm-4.7-flash", messages=api_messages)
                        full_response = response.choices[0].message.content
                    except Exception as e:
                        full_response = f"GLM Error: {e}"
                elif "Claude" in model_choice:
                    if not ANTHROPIC_KEY:
                        full_response = "⚠️ No Claude Key found."
                    else:
                        try:
                            response = completion(model="anthropic/claude-3-5-sonnet-20240620", messages=api_messages, api_key=ANTHROPIC_KEY)
                            full_response = response.choices[0]['message']['content']
                        except Exception as e:
                            full_response = f"Claude Error: {e}"
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        update_memory(prompt, full_response)
        manage_archive()
        if st.session_state['current_chat_id'] is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{timestamp}.json"
            st.session_state['current_chat_id'] = filename
        file_path = os.path.join(CHAT_DIR, st.session_state['current_chat_id'])
        with open(file_path, 'w') as f:
            json.dump(st.session_state.messages, f)

# --- 4. TERMINAL TAB (THE NEW FEATURE) ---
elif st.session_state['tab'] == 'Terminal':
    st.header("💻 System Terminal")
    st.caption("Execute bash commands without leaving the app.")
    
    # Input for Command
    command = st.text_input("Enter command (e.g., ls, git status, save):", key="term_input")
    
    # Execute Button
        if st.button("Run Command", key="term_run"):
            if command:
                st.subheader(f"Output of: `{command}`")
                
                # SECURITY FIX: Create a clean environment without sensitive keys
                # This prevents commands like 'env' from exposing your API Keys
                clean_env = os.environ.copy()
                
                # List of keys we want to hide
                sensitive_keys = ["ZHIPUAI_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
                for key in sensitive_keys:
                    if key in clean_env:
                        del clean_env[key]
                
                # Run the command with the CLEAN environment
                result = subprocess.run(command, shell=True, capture_output=True, text=True, env=clean_env)
                
                if result.stdout:
                    st.code(result.stdout, language="bash")
                
                if result.stderr:
                    st.error(result.stderr)
                    
                if result.returncode == 0:
                    st.success("✅ Command Completed")
                else:
                    st.warning("⚠️ Command Failed")
# --- 5. CODE EDITOR TAB ---
elif st.session_state['tab'] == 'Code':
    st.header("📝 Code Editor")
    
    # Filename to edit/create
    filename = st.text_input("Filename (e.g., app.py, test.py):", value="app.py", key="code_filename")
    
    if filename:
        file_path = os.path.join(os.getcwd(), filename)
        
        # Read existing file content
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                current_content = f.read()
        else:
            current_content = "# New File"
            
        # Editor
        new_content = st_ace(current_content, language="python", theme="monokai")
        
        # Save Button
        if st.button("💾 Save File"):
            with open(file_path, 'w') as f:
                f.write(new_content)
            st.success(f"Saved {filename}!")
