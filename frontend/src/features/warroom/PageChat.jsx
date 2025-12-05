import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useConversation } from '../../context/ConversationContext';
import { DraftProvider } from '../../context/DraftContext';
import { ChatPanel } from './ChatPanel';
import { LiveStage } from './LiveStage';

export function PageChat() {
  const { pageId } = useParams();
  const { loadConversations, createConversation, currentConversation } = useConversation();

  useEffect(() => {
    loadConversations();
    // Start a new conversation if none exists for this page
    // TODO: In the future, this should load/create a page-specific conversation
    if (!currentConversation) {
      createConversation();
    }
  }, [pageId]);

  return (
    <DraftProvider>
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Panel - Left */}
        <div className="w-1/2 border-r border-gray-200 flex flex-col bg-white">
          <ChatPanel />
        </div>

        {/* Live Stage - Right */}
        <div className="w-1/2 flex flex-col bg-gray-50">
          <LiveStage />
        </div>
      </div>
    </DraftProvider>
  );
}

export default PageChat;
