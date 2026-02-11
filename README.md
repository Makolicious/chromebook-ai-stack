# MAIKO

```
 __  __    _    ___ _  _____
|  \/  |  / \  |_ _| |/ / _ \
| |\/| | / _ \  | || ' / | | |
| |  | |/ ___ \ | || . \ |_| |
|_|  |_/_/   \_\___|_|\_\___/

// Hybrid Intelligence System
```

**Maiko** is a next-generation AI chat interface that combines multiple LLM models into a unified, intelligent system. Built with Next.js, TypeScript, and cutting-edge AI technology.

## 🚀 Features

### Three Intelligence Modes

- **⚡ GLM-4.7 Flash** - Lightning-fast responses for quick queries
- **🤖 Claude 3 Haiku** - Smart, balanced intelligence for complex reasoning
- **🚀 Mako Hybrid** - Innovative dual-LLM pipeline (80% GLM planning + 20% Claude refinement)

### Persistent Memory System

- **Universal Context**: Memory files loaded across ALL models
- **Instant Updates**: Edit `.md` files to update what AI remembers
- **Always Available**: Your preferences, projects, and context persist forever

### Chat Persistence

- **Auto-Save**: Every conversation automatically saved
- **Browse History**: Resume any previous chat instantly
- **Never Lose Work**: All conversations stored locally in your browser

### Beautiful UX

- **Claude Desktop-inspired** dark theme
- **Retro terminal** aesthetics with JetBrains Mono font
- **Smooth animations** and professional design
- **Model switching** with simple commands: `/glm`, `/claude`, `/mako`

## 🛠️ Tech Stack

- **Framework**: Next.js 16 with App Router & Turbopack
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **AI Models**:
  - Anthropic Claude 3 Haiku
  - ZhipuAI GLM-4.7 Flash
- **Storage**: localStorage (client-side persistence)

## 📦 Installation

### Prerequisites

- Node.js 18+ installed
- API keys for Anthropic and ZhipuAI

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Makolicious/maiko.git
   cd maiko
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**

   Create `.env.local` in the root directory:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_key_here
   ZHIPUAI_API_KEY=your_zhipuai_key_here
   ```

4. **Run development server**
   ```bash
   npm run dev
   ```

5. **Open in browser**

   Navigate to [http://localhost:3000](http://localhost:3000)

## 🧠 Memory System

Maiko includes a persistent memory system that provides context to all AI models.

### Memory Files

Located in `memory/` folder:

- **`user-profile.md`** - Your preferences, background, and personal info
- **`project-context.md`** - Information about your projects
- **`custom-instructions.md`** - How AI should respond to you

### How It Works

1. Memory files are automatically loaded with every API request
2. All three models (GLM, Claude, Mako) receive the same context
3. Edit any `.md` file to instantly update what AI remembers
4. Add new `.md` files to expand the knowledge base

## 💬 Using Maiko

### Quick Commands

- `/glm` - Switch to GLM-4.7 Flash (fast mode)
- `/claude` - Switch to Claude 3 Haiku (smart mode)
- `/mako` - Switch to Mako Hybrid (best of both)

### Chat History

- Click **"+ New Chat"** to start fresh
- Click **"Show"** under Chat History to see saved conversations
- Click any saved chat to resume it
- Click **"Delete"** to remove a chat

### Model Selection

Use the sidebar buttons to switch between models, or type commands in the chat.

## 🌐 Deployment

### Deploy to Vercel

1. Push your code to GitHub
2. Import project in Vercel
3. Add environment variables in Vercel dashboard:
   - `ANTHROPIC_API_KEY`
   - `ZHIPUAI_API_KEY`
4. Deploy!

## 🎨 Customization

### Update Memory

Edit files in `memory/` folder to customize:
- Your personal information
- How AI should respond
- Project-specific context
- Coding preferences

### Modify UI

- Theme colors: `app/globals.css`
- Components: `components/` folder
- Layout: `app/layout.tsx`

## 📝 Project Structure

```
maiko/
├── app/
│   ├── api/chat/route.ts    # API endpoint for LLM calls
│   ├── layout.tsx            # Root layout with fonts
│   ├── page.tsx              # Main chat interface
│   └── globals.css           # Global styles
├── components/
│   ├── ChatInput.tsx         # Message input component
│   ├── ChatMessage.tsx       # Message display component
│   └── ModelSelector.tsx     # Model selection buttons
├── lib/
│   ├── chatHistory.ts        # localStorage chat persistence
│   └── memory.ts             # Memory system loader
├── memory/
│   ├── user-profile.md       # Your personal context
│   ├── project-context.md    # Project information
│   └── custom-instructions.md # AI behavior instructions
└── .env.local                # Environment variables (not in git)
```

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a PR.

## 📄 License

MIT License - feel free to use this project however you like!

## 🙏 Acknowledgments

- Built with [Next.js](https://nextjs.org/)
- Powered by [Anthropic Claude](https://www.anthropic.com/)
- Enhanced with [ZhipuAI GLM](https://www.zhipuai.cn/)
- Inspired by Claude Desktop's beautiful UX

---

**Made with ❤️ by Marco | 2026**
