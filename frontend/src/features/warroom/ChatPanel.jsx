import { useState, useRef, useEffect } from 'react';
import { useConversation } from '../../context/ConversationContext';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { TypingIndicator } from './TypingIndicator';

export function ChatPanel({ pageId = null, productId = null, chatType = 'general' }) {
  const { messages, isStreaming, sendMessage } = useConversation();
  const scrollRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Enhanced send message handler that includes context
  const handleSendMessage = (content) => {
    const contextData = {
      content,
      page_id: pageId,
      product_id: productId,
    };
    sendMessage(contextData);
  };

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Chat Type Indicator */}
      {chatType !== 'general' && (
        <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center space-x-2 text-xs">
            <div className={`w-2 h-2 rounded-full ${chatType === 'overview' ? 'bg-blue-500' : 'bg-green-500'}`} />
            <span className="text-gray-600 font-medium">
              {chatType === 'overview' ? 'Account Overview Chat' : 'Page War Room Chat'}
            </span>
          </div>
        </div>
      )}

      {/* Messages */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-4 chat-scroll"
      >
        {messages.length === 0 ? (
          <WelcomeMessage chatType={chatType} />
        ) : (
          <MessageList messages={messages} />
        )}
        {isStreaming && <TypingIndicator />}
      </div>

      {/* Input */}
      <MessageInput onSend={handleSendMessage} disabled={isStreaming} />
    </div>
  );
}

function WelcomeMessage({ chatType = 'general' }) {
  const suggestions = {
    overview: [
      "Show me yesterday's performance",
      "Which page performed best?",
      "Give me a cross-page summary",
    ],
    page: [
      "Let's create an ad for this page",
      "Show me past performance",
      "Suggest today's strategy",
    ],
    general: [
      "Show me my stats",
      "Create an ad for my product",
      "What's performing best?",
    ],
  };

  const titles = {
    overview: "Account Overview",
    page: "Page War Room",
    general: "Welcome to Daily Ad Agent",
  };

  const descriptions = {
    overview: "Get cross-page insights, performance summaries, and strategic recommendations for your entire ad account.",
    page: "Create, iterate, and publish ads for this specific Facebook Page. I'll keep context focused on this page's audience and history.",
    general: "I'm your AI Media Buyer. Tell me what you'd like to promote, and I'll help you create high-performing Facebook ads.",
  };

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
        {titles[chatType] || titles.general}
      </h2>
      <p className="text-gray-600 mb-6 max-w-md">
        {descriptions[chatType] || descriptions.general}
      </p>
      <div className="space-y-2 text-sm text-gray-500">
        <p>Try saying:</p>
        <div className="flex flex-wrap gap-2 justify-center">
          {(suggestions[chatType] || suggestions.general).map((text) => (
            <SuggestionChip key={text} text={text} />
          ))}
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
