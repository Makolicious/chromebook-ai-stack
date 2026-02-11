import fs from 'fs';
import path from 'path';

export interface MemoryContext {
  userProfile: string;
  projectContext: string;
  customInstructions: string;
  combined: string;
}

/**
 * Loads all memory files from the memory/ folder
 * Returns combined context to prepend to chat messages
 */
export function loadMemory(): MemoryContext {
  const memoryDir = path.join(process.cwd(), 'memory');

  try {
    const userProfile = readMemoryFile(memoryDir, 'user-profile.md');
    const projectContext = readMemoryFile(memoryDir, 'project-context.md');
    const customInstructions = readMemoryFile(memoryDir, 'custom-instructions.md');

    // Combine all memory into a single context string
    const combined = `# Persistent Memory Context

${userProfile}

${projectContext}

${customInstructions}

---
*This context is automatically loaded from memory files and should inform your responses.*
`;

    return {
      userProfile,
      projectContext,
      customInstructions,
      combined,
    };
  } catch (error) {
    console.warn('Memory files not found or error loading:', error);
    return {
      userProfile: '',
      projectContext: '',
      customInstructions: '',
      combined: '',
    };
  }
}

/**
 * Safely reads a memory file
 */
function readMemoryFile(memoryDir: string, filename: string): string {
  const filePath = path.join(memoryDir, filename);

  try {
    if (fs.existsSync(filePath)) {
      return fs.readFileSync(filePath, 'utf-8');
    }
    return '';
  } catch (error) {
    console.warn(`Could not read ${filename}:`, error);
    return '';
  }
}

/**
 * Prepends memory context to messages for Claude/GLM
 * Only adds to the first user message to avoid repetition
 */
export function injectMemoryContext(messages: any[], memory: MemoryContext): any[] {
  if (!memory.combined || messages.length === 0) {
    return messages;
  }

  // Find first user message and prepend memory
  const updatedMessages = [...messages];
  const firstUserIndex = updatedMessages.findIndex(m => m.role === 'user');

  if (firstUserIndex !== -1) {
    updatedMessages[firstUserIndex] = {
      ...updatedMessages[firstUserIndex],
      content: `${memory.combined}\n\n---\n\nUser Message:\n${updatedMessages[firstUserIndex].content}`,
    };
  }

  return updatedMessages;
}
