import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { conversationsApi } from '../../api/conversations';
import { useConversation } from '../../context/ConversationContext';
import { ChatPanel } from './ChatPanel';
import { ProductSelector } from '../products/ProductSelector';
import { Loader } from '../shared/Loader';
import { Button } from '../shared/Button';

export function PageWarRoomChat({ workspaceId }) {
  const { pageId } = useParams();
  const navigate = useNavigate();
  const { loadConversation, setCurrentConversation } = useConversation();
  const [activeProduct, setActiveProduct] = useState(null);

  // Fetch page conversation
  const { data: conversation, isLoading, error } = useQuery({
    queryKey: ['conversation', 'page', pageId],
    queryFn: () => conversationsApi.getPageConversation(pageId),
    enabled: !!pageId,
  });

  // Fetch page details (assuming we have a pages API)
  const { data: page, isLoading: pageLoading } = useQuery({
    queryKey: ['page', pageId],
    queryFn: async () => {
      // This would be a pages API call
      // For now, using conversation data
      return conversation?.page || { id: pageId, name: 'Loading...' };
    },
    enabled: !!conversation,
  });

  // Load conversation into context when available
  useEffect(() => {
    if (conversation) {
      setCurrentConversation(conversation);
      loadConversation(conversation.id);

      // Set active product if conversation has one
      if (conversation.active_product_id) {
        setActiveProduct({ id: conversation.active_product_id });
      }
    }
  }, [conversation, loadConversation, setCurrentConversation]);

  // Update active product in conversation when changed
  const handleProductChange = async (product) => {
    setActiveProduct(product);

    if (conversation?.id) {
      try {
        await conversationsApi.updateActiveProduct(
          conversation.id,
          product?.id || null
        );
      } catch (error) {
        console.error('Failed to update active product:', error);
      }
    }
  };

  if (isLoading || pageLoading) {
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
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Failed to load page conversation
          </h3>
          <p className="text-sm text-gray-600 mb-4">{error.message}</p>
          <div className="flex gap-2 justify-center">
            <Button variant="outline" onClick={() => navigate('/app')}>
              Back to Overview
            </Button>
            <Button onClick={() => window.location.reload()}>Retry</Button>
          </div>
        </div>
      </div>
    );
  }

  if (!page) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-600">Page not found</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-3">
            {/* Back Button */}
            <button
              onClick={() => navigate('/app')}
              className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
              title="Back to Overview"
            >
              <svg className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            {/* Page Info */}
            <div>
              <div className="flex items-center space-x-2">
                {page.profile_picture_url && (
                  <img
                    src={page.profile_picture_url}
                    alt={page.name}
                    className="w-8 h-8 rounded-lg"
                  />
                )}
                <h1 className="text-xl font-bold text-gray-900">{page.name}</h1>
              </div>
              <p className="text-sm text-gray-600 mt-0.5">Page War Room</p>
            </div>
          </div>

          {/* Page Settings Button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate(`/app/page/${pageId}/settings`)}
          >
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
            Page Settings
          </Button>
        </div>

        {/* Product Selector */}
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600 font-medium">Active Product:</span>
          <ProductSelector
            workspaceId={workspaceId}
            pageId={pageId}
            activeProductId={activeProduct?.id}
            onChange={handleProductChange}
          />
        </div>
      </div>

      {/* Chat Panel */}
      <div className="flex-1 min-h-0">
        <ChatPanel
          pageId={pageId}
          productId={activeProduct?.id}
          chatType="page"
        />
      </div>

      {/* Ad Account Info Footer */}
      {page.ad_account && (
        <div className="px-6 py-3 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2 text-gray-600">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
              <span>Ad Account: {page.ad_account.name || page.ad_account.id}</span>
            </div>
            {page.default_tone && (
              <div className="flex items-center space-x-2 text-gray-600">
                <span>Default Tone: {page.default_tone}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default PageWarRoomChat;
