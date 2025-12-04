import { useState, useRef, useEffect } from 'react';
import { useConversation } from '../../context/ConversationContext';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { TypingIndicator } from './TypingIndicator';

export function ChatPanel() {
  const { messages, isStreaming, sendMessage } = useConversation();
  const scrollRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Messages */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-4 chat-scroll"
      >
        {messages.length === 0 ? (
          <WelcomeMessage />
        ) : (
          <MessageList messages={messages} />
        )}
        {isStreaming && <TypingIndicator />}
      </div>

      {/* Input */}
      <MessageInput onSend={sendMessage} disabled={isStreaming} />
    </div>
  );
}

function WelcomeMessage() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-8">
      <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center mb-4">
        <svg
          className="w-6 h-6 text-primary-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
      </div>
      <h2 className="text-xl font-semibold text-gray-900 mb-2">
        Welcome to Daily Ad Agent
      </h2>
      <p className="text-gray-600 mb-6 max-w-md">
        I'm your AI Media Buyer. Tell me what you'd like to promote, and I'll help
        you create high-performing Facebook ads.
      </p>
      <div className="space-y-2 text-sm text-gray-500">
        <p>Try saying:</p>
        <div className="flex flex-wrap gap-2 justify-center">
          <SuggestionChip text="Show me my stats" />
          <SuggestionChip text="Create an ad for my product" />
          <SuggestionChip text="What's performing best?" />
        </div>
      </div>
    </div>
  );
}

function SuggestionChip({ text }) {
  const { sendMessage } = useConversation();

  return (
    <button
      onClick={() => sendMessage(text)}
      className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
    >
      {text}
    </button>
  );
}

export default ChatPanel;
