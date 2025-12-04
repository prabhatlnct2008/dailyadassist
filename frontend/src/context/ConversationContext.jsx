import { createContext, useContext, useState, useCallback } from 'react';
import { conversationsApi } from '../api/conversations';
import { agentApi } from '../api/agent';

const ConversationContext = createContext(null);

export function ConversationProvider({ children }) {
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);

  const loadConversations = useCallback(async () => {
    try {
      const data = await conversationsApi.list();
      setConversations(data);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  }, []);

  const loadConversation = useCallback(async (id) => {
    setIsLoading(true);
    try {
      const data = await conversationsApi.get(id);
      setCurrentConversation(data);
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createConversation = useCallback(async () => {
    try {
      const data = await conversationsApi.create();
      setConversations((prev) => [data, ...prev]);
      setCurrentConversation(data);
      setMessages([]);
      return data;
    } catch (error) {
      console.error('Failed to create conversation:', error);
      return null;
    }
  }, []);

  const sendMessage = useCallback(async (content) => {
    if (!content.trim()) return;

    // Add user message immediately
    const userMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Start streaming response
    setIsStreaming(true);
    let assistantContent = '';
    const assistantMessage = {
      id: `temp-assistant-${Date.now()}`,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, assistantMessage]);

    try {
      const conversationId = currentConversation?.id;

      for await (const chunk of agentApi.chat(conversationId, content)) {
        if (chunk.content) {
          assistantContent += chunk.content;
          setMessages((prev) => {
            const updated = [...prev];
            const lastIdx = updated.length - 1;
            updated[lastIdx] = {
              ...updated[lastIdx],
              content: assistantContent,
            };
            return updated;
          });
        }

        if (chunk.done) {
          if (chunk.conversation_id && !currentConversation) {
            loadConversation(chunk.conversation_id);
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => {
        const updated = [...prev];
        const lastIdx = updated.length - 1;
        updated[lastIdx] = {
          ...updated[lastIdx],
          content: 'Sorry, I encountered an error. Please try again.',
        };
        return updated;
      });
    } finally {
      setIsStreaming(false);
    }
  }, [currentConversation, loadConversation]);

  const value = {
    conversations,
    currentConversation,
    messages,
    isLoading,
    isStreaming,
    loadConversations,
    loadConversation,
    createConversation,
    sendMessage,
    setCurrentConversation,
  };

  return (
    <ConversationContext.Provider value={value}>
      {children}
    </ConversationContext.Provider>
  );
}

export function useConversation() {
  const context = useContext(ConversationContext);
  if (!context) {
    throw new Error('useConversation must be used within a ConversationProvider');
  }
  return context;
}

export default ConversationContext;
