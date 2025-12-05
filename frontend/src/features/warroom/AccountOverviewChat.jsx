import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { conversationsApi } from '../../api/conversations';
import { useConversation } from '../../context/ConversationContext';
import { ChatPanel } from './ChatPanel';
import { PinnedSummary } from './PinnedSummary';
import { Loader } from '../shared/Loader';
import { Button } from '../shared/Button';

export function AccountOverviewChat({ workspaceId }) {
  const navigate = useNavigate();
  const { loadConversation, setCurrentConversation } = useConversation();

  // Fetch account overview conversation
  const { data: conversation, isLoading, error } = useQuery({
    queryKey: ['conversation', 'overview', workspaceId],
    queryFn: () => conversationsApi.getAccountOverview(workspaceId),
    enabled: !!workspaceId,
  });

  // Load conversation into context when available
  useEffect(() => {
    if (conversation) {
      setCurrentConversation(conversation);
      loadConversation(conversation.id);
    }
  }, [conversation, loadConversation, setCurrentConversation]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <div className="text-center max-w-md">
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
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Failed to load overview</h3>
          <p className="text-sm text-gray-600 mb-4">{error.message}</p>
          <Button onClick={() => window.location.reload()}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Account Overview</h1>
            <p className="text-sm text-gray-600 mt-0.5">
              Cross-page insights and strategic recommendations
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/app/archive')}
          >
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"
              />
            </svg>
            View Archive
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {/* Pinned Summary (if exists) */}
        {conversation?.is_pinned && conversation?.pinned_content && (
          <div className="px-6 pt-4">
            <PinnedSummary
              pinnedContent={conversation.pinned_content}
              archivedCount={conversation.archived_count || 0}
            />
          </div>
        )}

        {/* Chat Panel */}
        <div className="flex-1 min-h-0">
          <ChatPanel chatType="overview" />
        </div>

        {/* Quick Actions */}
        {conversation?.suggested_pages && conversation.suggested_pages.length > 0 && (
          <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
            <p className="text-xs font-medium text-gray-700 mb-3">Quick Actions</p>
            <div className="flex flex-wrap gap-2">
              {conversation.suggested_pages.map((page) => (
                <Button
                  key={page.id}
                  variant="outline"
                  size="sm"
                  onClick={() => navigate(`/app/page/${page.id}`)}
                >
                  Open {page.name} Plan
                </Button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AccountOverviewChat;
