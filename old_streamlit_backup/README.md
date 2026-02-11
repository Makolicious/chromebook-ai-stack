# AI Stack Desktop

A powerful dual-LLM chat interface combining Claude 3.5 and GLM-4.7 in one unified UI. Built with Streamlit for easy deployment and usage.

## Features

- 🤖 **Dual Model Support**: Switch between GLM-4.7 (free/fast) and Claude 3.5 (paid/smart/vision)
- 📸 **Vision Mode**: Upload screenshots for Claude to analyze
- 💾 **Chat History**: Auto-saves conversations with archival system
- 🧠 **Memory Engine**: Remembers user preferences and facts across sessions
- 💻 **Built-in Terminal**: Execute bash commands without leaving the app
- 📝 **Code Editor**: Edit files directly in the interface
- 🔄 **Model Switching**: Use `/claude` or `/glm` commands to switch models mid-conversation

## Setup

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/Makolicious/chromebook-ai-stack.git
cd chromebook-ai-stack
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```bash
cp .env.example .env
```

Then edit `.env` and add your keys:
```
ZHIPUAI_API_KEY=your_zhipu_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

4. Run the app:
```bash
streamlit run ai.py
```

The app will open at `http://localhost:8501`

### Vercel Deployment

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Add your environment variables in Vercel:
```bash
vercel env add ZHIPUAI_API_KEY
vercel env add ANTHROPIC_API_KEY
```

4. Deploy:
```bash
vercel --prod
```

## Usage

### Model Selection

Use the sidebar radio buttons to select between:
- **GLM-4.7 (Free/Fast)**: Text-only model, great for quick responses
- **Claude 3.5 (Paid/Smart/Vision)**: Advanced model with image analysis capabilities

### Vision Mode

When using Claude 3.5:
1. Upload a screenshot using the sidebar file uploader
2. Ask questions about the image
3. Claude will analyze the screenshot and respond

### Chat Commands (Coming Soon)

- `/claude` - Switch to Claude 3.5 model
- `/glm` - Switch to GLM-4.7 model

### Memory System

The app automatically remembers facts about you:
- Say "remember that..." to explicitly save information
- Say "forget..." to remove stored facts
- Memory persists across chat sessions

### Terminal

Navigate to the Terminal tab to:
- Run bash commands
- Check git status
- Execute system operations

### Code Editor

Use the Code Editor tab to:
- Edit Python files
- Create new scripts
- Save changes directly

## Project Structure

```
chromebook-ai-stack/
├── ai.py                 # Main Streamlit app
├── requirements.txt      # Python dependencies
├── .env.example         # Example environment variables
├── vercel.json          # Vercel deployment configuration
├── chats/               # Stored chat history (auto-created)
├── memory_bank.json     # User facts and preferences (auto-created)
└── chat_archive.json    # Archived old chats (auto-created)
```

## API Keys

### ZhipuAI (GLM-4.7)
Get your free API key at [https://open.bigmodel.cn/](https://open.bigmodel.cn/)

### Anthropic (Claude)
Get your API key at [https://console.anthropic.com/](https://console.anthropic.com/)

## Tech Stack

- **Streamlit**: Web UI framework
- **OpenAI SDK**: For ZhipuAI API calls
- **LiteLLM**: For Claude API integration
- **Streamlit-Ace**: Code editor component

## Contributing

Feel free to submit issues and pull requests!

## License

MIT
