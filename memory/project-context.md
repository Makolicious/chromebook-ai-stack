# Project Context - AI Stack Desktop

## Overview
A Next.js application that combines multiple LLM models into a unified chat interface.

## Architecture
- **Frontend**: Next.js 15, TypeScript, Tailwind CSS
- **API Routes**: Server-side LLM calls to protect API keys
- **Models**: GLM-4.7 Flash, Claude 3 Haiku, Mako Hybrid

## Three Intelligence Modes

### 1. GLM Mode (⚡)
- Fast and free
- Good for quick queries
- Uses GLM-4.7 Flash

### 2. Claude Mode (🤖)
- Smart and balanced
- Currently using Claude 3 Haiku
- Better reasoning quality

### 3. Mako Hybrid Mode (🚀)
- Innovative dual-LLM pipeline
- 80% GLM (planning/brainstorming)
- 20% Claude (refinement/execution)
- Best of both worlds

## Key Features
- Dark theme UI inspired by Claude Desktop
- Command switching: `/glm`, `/claude`, `/mako`
- Real-time model switching
- Chat persistence and memory system

## Tech Stack Details
- Anthropic SDK for Claude
- OpenAI SDK for ZhipuAI (GLM)
- localStorage for chat history
- Memory files for persistent context

---
*Auto-loaded context for all conversations*
