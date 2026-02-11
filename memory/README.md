# Memory System

This folder contains persistent memory files that are loaded with every chat conversation, regardless of which chat you're in.

## How It Works

1. **Persistent Context**: Files here provide background context to AI models
2. **Always Loaded**: Memory is included in every API request
3. **User Control**: You can edit these files anytime to update what AI remembers
4. **Privacy**: All files stay local on your computer

## Files

- `user-profile.md` - Your preferences, style, and personal information
- `project-context.md` - Information about your projects and tech stack
- `custom-instructions.md` - Specific instructions for how AI should behave

## Editing Memory

Simply open any `.md` file and edit it. Changes take effect immediately on the next chat message.

## Benefits

- AI remembers your preferences across all chats
- No need to repeat context
- Consistent responses aligned with your style
- Project knowledge always available

## Safety

- All data stays local (never uploaded to external servers)
- You control what's remembered
- Delete any file to remove that context
- Memory files are plain text (no code execution)
