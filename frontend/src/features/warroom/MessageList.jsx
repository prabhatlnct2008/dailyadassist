import { AgentMessage } from './AgentMessage';
import { UserMessage } from './UserMessage';

export function MessageList({ messages }) {
  return (
    <div className="space-y-4">
      {messages.map((message) => {
        if (message.role === 'assistant') {
          return <AgentMessage key={message.id} message={message} />;
        } else if (message.role === 'user') {
          return <UserMessage key={message.id} message={message} />;
        }
        return null;
      })}
    </div>
  );
}

export default MessageList;
