import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { conversationsApi } from '../../api/conversations';
import { AgentMessage } from './AgentMessage';
import { UserMessage } from './UserMessage';
import { Loader } from '../shared/Loader';

export function LegacyArchiveViewer({ workspaceId }) {
  const [expandedId, setExpandedId] = useState(null);

  const { data: conversations, isLoading, error } = useQuery({
    queryKey: ['legacy-conversations', workspaceId],
    queryFn: async () => {
      // Fetch archived conversations
      const response = await conversationsApi.list();
      return response.filter((conv) => conv.is_archived);
    },
    enabled: !!workspaceId,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-center">
          <svg
            className="w-12 h-12 text-red-500 mx-auto mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Failed to load archive</h3>
          <p className="text-sm text-gray-600">{error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <Link
          to="/app"
          className="inline-flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900 mb-4"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span>Back to Overview</span>
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Archived Conversations</h1>
        <p className="text-gray-600">
          Your previous conversations have been archived. They are read-only but available for
          reference.
        </p>
      </div>

      {/* Conversations List */}
      {conversations && conversations.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <svg
            className="w-12 h-12 text-gray-400 mx-auto mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"
            />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No archived conversations</h3>
          <p className="text-sm text-gray-600">
            You don't have any archived conversations yet.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {conversations?.map((conversation) => (
            <ConversationCard
              key={conversation.id}
              conversation={conversation}
              isExpanded={expandedId === conversation.id}
              onToggle={() =>
                setExpandedId(expandedId === conversation.id ? null : conversation.id)
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ConversationCard({ conversation, isExpanded, onToggle }) {
  const { data: messages, isLoading } = useQuery({
    queryKey: ['conversation-messages', conversation.id],
    queryFn: () => conversationsApi.getMessages(conversation.id),
    enabled: isExpanded,
  });

  const messagePreview = conversation.archived_summary || 'Click to view conversation';
  const archivedDate = new Date(conversation.archived_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Card Header */}
      <button
        onClick={onToggle}
        className="w-full flex items-start justify-between px-6 py-4 hover:bg-gray-50 transition-colors"
      >
        <div className="flex-1 text-left">
          <div className="flex items-center space-x-2 mb-1">
            <h3 className="text-lg font-semibold text-gray-900">
              {conversation.title || 'Untitled Conversation'}
            </h3>
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700">
              Archived
            </span>
          </div>
          <p className="text-sm text-gray-600 mb-2">{messagePreview}</p>
          <div className="flex items-center space-x-4 text-xs text-gray-500">
            <span>Archived on {archivedDate}</span>
            {conversation.messages && (
              <span>{conversation.messages.length} messages</span>
            )}
          </div>
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 flex-shrink-0 ml-4 transition-transform ${
            isExpanded ? 'rotate-180' : ''
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expanded Messages */}
      {isExpanded && (
        <div className="border-t border-gray-200 bg-gray-50 px-6 py-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader />
            </div>
          ) : messages && messages.length > 0 ? (
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {messages.map((message) => {
                if (message.role === 'assistant') {
                  return <AgentMessage key={message.id} message={message} />;
                } else if (message.role === 'user') {
                  return <UserMessage key={message.id} message={message} />;
                }
                return null;
              })}
            </div>
          ) : (
            <p className="text-sm text-gray-500 text-center py-4">No messages found</p>
          )}
        </div>
      )}
    </div>
  );
}

export default LegacyArchiveViewer;
