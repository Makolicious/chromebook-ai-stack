import os
import json
import base64
import subprocess
import requests
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from litellm import completion
import streamlit as st
from anthropic import Anthropic

# --- 1. SETUP ---
load_dotenv()

ZAI_KEY = os.environ.get("ZHIPUAI_API_KEY")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
EXECUTE_API_URL = os.environ.get("EXECUTE_API_URL", "http://localhost:5000")

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
    st.session_state['tab'] = 'Chat'

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
        st.sidebar.info("No image selected (Text Mode)")
elif "GLM" in model_choice and st.session_state['tab'] == 'Chat':
    st.sidebar.caption("GLM is Text-Only. Switch to Claude to use Vision.")

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
if st.sidebar.button("⚙️ Code Execution"):
    st.session_state['tab'] = 'CodeExecution'
    st.rerun()

st.sidebar.divider()

# --- 4. CHAT TAB LOGIC ---
if st.session_state['tab'] == 'Chat':

    # 4a. CODE EXECUTION (Agentic)
    def execute_code_remote(code: str, language: str = "javascript", timeout: int = 5000):
        """Execute code through the Node.js backend"""
        try:
            response = requests.post(
                f"{EXECUTE_API_URL}/api/execute/run",
                json={"code": code, "language": language, "timeout": timeout},
                timeout=timeout // 1000 + 2
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"Server error: {response.status_code}", "output": None}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Cannot connect to execution server", "output": None}
        except Exception as e:
            return {"success": False, "error": str(e), "output": None}

    def chat_with_code_execution(messages, model_choice):
        """Claude chat with agentic code execution capability"""
        if "Claude" not in model_choice or not ANTHROPIC_KEY:
            return None

        client = Anthropic(api_key=ANTHROPIC_KEY)

        # Define code execution tool
        tools = [
            {
                "name": "execute_code",
                "description": "Execute Python or JavaScript code to solve problems, analyze data, or test hypotheses",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code to execute"
                        },
                        "language": {
                            "type": "string",
                            "enum": ["python", "javascript"],
                            "description": "Programming language: python or javascript"
                        }
                    },
                    "required": ["code", "language"]
                }
            }
        ]

        # Convert messages format for Anthropic
        api_messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]

        # Initial Claude response
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=tools,
            messages=api_messages
        )

        # Handle tool use in an agentic loop
        while response.stop_reason == "tool_use":
            tool_use_block = next(b for b in response.content if b.type == "tool_use")
            tool_name = tool_use_block.name
            tool_input = tool_use_block.input

            if tool_name == "execute_code":
                result = execute_code_remote(tool_input["code"], tool_input.get("language", "javascript"))

                # Add assistant response and tool result to messages
                api_messages.append({"role": "assistant", "content": response.content})
                api_messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_block.id,
                            "content": json.dumps(result)
                        }
                    ]
                })

                # Get next response
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4096,
                    tools=tools,
                    messages=api_messages
                )

        # Extract final text response
        text_blocks = [b for b in response.content if hasattr(b, 'text')]
        return "".join(b.text for b in text_blocks) if text_blocks else ""

    # 4b. ARCHIVAL SYSTEM
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
            archive.insert(0, {
                "date": oldest_file,
                "summary": summary
            })
            if len(archive) > 50:
                archive = archive[:50]
            with open(ARCHIVE_FILE, 'w') as f:
                json.dump(archive, f)
            os.remove(file_path)

    # 4b. MEMORY ENGINE
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
            prompt = f"The user wants to forget something. Look at their input. Return a JSON list of facts to KEEP (Remove the relevant ones). Existing Facts: {json.dumps(existing_facts)} User: {user_input}"
            try:
                response = zai_client.chat.completions.create(
                    model="glm-4.7-flash",
                    messages=[{"role": "user", "content": prompt}]
                )
                raw = response.choices[0].message.content
                clean = raw.strip()
                if "```json" in clean: clean = clean.split("```json")[1].split("```")[0]
                updated_memory = json.loads(clean)
            except: pass
            with open(MEMORY_FILE, 'w') as f:
                json.dump(updated_memory, f)
            return

        if "remember" in text_lower or "new name is" in text_lower or "my name is" in text_lower:
            prompt = f"Extract the specific fact the user wants remembered. User: {user_input}. Return ONLY a JSON list with the new fact."
            try:
                response = zai_client.chat.completions.create(
                    model="glm-4.7-flash",
                    messages=[{"role": "user", "content": prompt}]
                )
                raw = response.choices[0].message.content.strip()
                if "```json" in raw: raw = raw.split("```json")[1].split("```")[0]
                new_facts = json.loads(raw)
                if not isinstance(new_facts, list): new_facts = []
                
                for fact in new_facts:
                    if fact not in updated_memory:
                        updated_memory.append(fact)
            except: pass
            with open(MEMORY_FILE, 'w') as f:
                json.dump(updated_memory, f)
            return

        prompt = f"Extract NEW facts about the user from this text. Return ONLY a JSON list. Existing Knowledge (DO NOT REPEAT): {json.dumps(existing_facts)} \n\n Text: {user_input} \n\n AI Response: {ai_response}"
        try:
            response = zai_client.chat.completions.create(
                model="glm-4.7-flash",
                messages=[{"role": "user", "content": prompt}]
            )
            raw_text = response.choices[0].message.content
            clean_json = raw_text.strip()
            if "```json" in clean_json: clean_json = clean_json.split("```json")[1].split("```")[0]
            elif "```" in clean_json: clean_json = clean_json.split("```")[1].split("```")[0]
            
            try:
                new_facts = json.loads(clean_json)
                if not isinstance(new_facts, list): new_facts = []
            except: new_facts = []
                
            for fact in new_facts:
                if fact not in updated_memory:
                    updated_memory.append(fact)
            
            with open(MEMORY_FILE, 'w') as f:
                json.dump(updated_memory, f)
            
        except Exception as e: pass

    # 4c. SIDEBAR UI
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

    # 4d. CHAT DISPLAY
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 4e. CHAT INPUT
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
                    # Use agentic code execution with vision
                    full_response = chat_with_code_execution(api_messages + [vision_message], model_choice)
                    if not full_response:
                        full_response = "Claude Error: No response generated"
                except Exception as e:
                    full_response = f"Claude Error: {e}"

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
                            # Use agentic code execution
                            full_response = chat_with_code_execution(api_messages, model_choice)
                            if not full_response:
                                full_response = "Claude Error: No response generated"
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

# --- 5. TERMINAL TAB ---
elif st.session_state['tab'] == 'Terminal':
    st.header("💻 System Terminal")
    st.caption("Execute bash commands without leaving the app.")
    command = st.text_input("Enter command (e.g., ls, git status, save):")
    
    if st.button("Run Command"):
        if command:
            st.subheader(f"Output of: `{command}`")
            clean_env = os.environ.copy()
            sensitive_keys = ["ZHIPUAI_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
            for key in sensitive_keys:
                if key in clean_env:
                    del clean_env[key]
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True, env=clean_env)
            
            if result.stdout:
                st.code(result.stdout, language="bash")
            
            if result.stderr:
                st.error(result.stderr)
                
            if result.returncode == 0:
                st.success("✅ Command Completed")
            else:
                st.warning("⚠️ Command Failed")

# --- 6. CODE EDITOR TAB ---
elif st.session_state['tab'] == 'Code':
    st.header("📝 Code Editor")
    filename = st.text_input("Filename (e.g., app.py, test.py):", value="app.py")
    if filename:
        file_path = os.path.join(os.getcwd(), filename)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                current_content = f.read()
        else:
            current_content = "# New File"
        new_content = st_ace(current_content, language="python", theme="monokai")
        if st.button("💾 Save File"):
            with open(file_path, 'w') as f:
                f.write(new_content)
            st.success(f"Saved {filename}!")

# --- 7. CODE EXECUTION TAB ---
elif st.session_state['tab'] == 'CodeExecution':
    st.header("⚙️ Code Execution Engine")
    st.caption("Execute code snippets safely using the backend execution server.")

    # Configuration
    SERVER_URL = st.sidebar.text_input("Server URL", value=EXECUTE_API_URL)

    # Language selection
    language = st.selectbox("Select Language", ["python", "javascript"])

    # Code editor
    code_input = st.text_area(
        "Enter your code:",
        height=300,
        placeholder=f"# Write your {language} code here\nprint('Hello, World!')"
    )

    # Execution controls
    col1, col2, col3 = st.columns(3)

    with col1:
        execute_btn = st.button("▶️ Execute Code", key="execute_btn")

    with col2:
        st.button("🗑️ Clear", key="clear_btn")

    with col3:
        show_help = st.button("❓ Help", key="help_btn")

    # Help section
    if show_help:
        st.info("""
        **Code Execution Engine Help:**
        - **Python**: Execute Python code snippets (import libraries as needed)
        - **JavaScript**: Execute Node.js code snippets
        - **Output**: View execution results in real-time
        - **Errors**: Error messages are displayed if execution fails
        - **Timeout**: Code that takes >5 seconds will timeout
        """)

    # Execute code
    if execute_btn and code_input:
        st.subheader("Execution Results")

        try:
            with st.spinner(f"Executing {language} code..."):
                response = requests.post(
                    f"{SERVER_URL}/api/execute/run",
                    json={"code": code_input, "language": language},
                    timeout=10
                )

            if response.status_code == 200:
                result = response.json()

                if result.get('success'):
                    st.success("✅ Execution Successful")
                    if result.get('output'):
                        st.subheader("Output:")
                        st.code(result['output'], language="text")
                else:
                    st.error("❌ Execution Failed")
                    if result.get('error'):
                        st.subheader("Error:")
                        st.code(result['error'], language="text")
            else:
                st.error(f"Server Error: {response.status_code}")
                st.code(response.text, language="text")

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to execution server. Make sure it's running on " + SERVER_URL)
            st.info("Start the server with: `cd server && npm install && npm start`")
        except requests.exceptions.Timeout:
            st.error("❌ Code execution timed out (>10 seconds)")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
