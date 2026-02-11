export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface Chat {
  id: string;
  title: string;
  messages: Message[];
  model: 'claude' | 'glm' | 'mako';
  createdAt: number;
  updatedAt: number;
}

/**
 * Safe localStorage wrapper with error handling
 */
class ChatStorage {
  private STORAGE_KEY = 'ai-stack-chats';

  /**
   * Get all saved chats
   */
  getAllChats(): Chat[] {
    if (typeof window === 'undefined') return [];

    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (!stored) return [];

      const chats = JSON.parse(stored);
      return Array.isArray(chats) ? chats : [];
    } catch (error) {
      console.error('Error loading chats:', error);
      return [];
    }
  }

  /**
   * Get a specific chat by ID
   */
  getChat(id: string): Chat | null {
    const chats = this.getAllChats();
    return chats.find(chat => chat.id === id) || null;
  }

  /**
   * Save or update a chat
   */
  saveChat(chat: Chat): void {
    if (typeof window === 'undefined') return;

    try {
      const chats = this.getAllChats();
      const existingIndex = chats.findIndex(c => c.id === chat.id);

      if (existingIndex !== -1) {
        // Update existing
        chats[existingIndex] = { ...chat, updatedAt: Date.now() };
      } else {
        // Add new
        chats.unshift(chat); // Add to beginning
      }

      // Limit to 100 chats to prevent storage bloat
      const trimmedChats = chats.slice(0, 100);

      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(trimmedChats));
    } catch (error) {
      console.error('Error saving chat:', error);
    }
  }

  /**
   * Delete a chat
   */
  deleteChat(id: string): void {
    if (typeof window === 'undefined') return;

    try {
      const chats = this.getAllChats();
      const filtered = chats.filter(chat => chat.id !== id);
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(filtered));
    } catch (error) {
      console.error('Error deleting chat:', error);
    }
  }

  /**
   * Create a new chat
   */
  createNewChat(model: 'claude' | 'glm' | 'mako' = 'glm'): Chat {
    return {
      id: generateId(),
      title: 'New Chat',
      messages: [],
      model,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };
  }

  /**
   * Generate title from first user message
   */
  generateTitle(messages: Message[]): string {
    const firstUserMessage = messages.find(m => m.role === 'user');
    if (!firstUserMessage) return 'New Chat';

    // Take first 50 chars of first message
    const title = firstUserMessage.content.slice(0, 50);
    return title.length < firstUserMessage.content.length ? title + '...' : title;
  }
}

/**
 * Generate unique ID
 */
function generateId(): string {
  return `chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export const chatStorage = new ChatStorage();
