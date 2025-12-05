import { useEffect } from 'react';
import { useConversation } from '../../context/ConversationContext';
import { DraftProvider } from '../../context/DraftContext';
import { ChatPanel } from './ChatPanel';
import { LiveStage } from './LiveStage';

export function AccountOverview() {
  const { loadConversations, createConversation, currentConversation } = useConversation();

  useEffect(() => {
    loadConversations();
    // Start a new conversation if none exists
    if (!currentConversation) {
      createConversation();
    }
  }, []);

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

export default AccountOverview;
