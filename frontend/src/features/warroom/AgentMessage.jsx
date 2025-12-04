export function AgentMessage({ message }) {
  // Simple markdown-like rendering
  const formatContent = (content) => {
    // Split by code blocks first
    const parts = content.split(/(```[\s\S]*?```)/g);

    return parts.map((part, index) => {
      if (part.startsWith('```')) {
        const code = part.replace(/```\w*\n?/g, '').trim();
        return (
          <pre key={index} className="bg-gray-800 text-gray-100 rounded-lg p-3 my-2 overflow-x-auto text-sm">
            <code>{code}</code>
          </pre>
        );
      }

      // Process other markdown-like elements
      let processed = part
        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Headers
        .replace(/^### (.*$)/gm, '<h4 class="font-semibold text-lg mt-3 mb-1">$1</h4>')
        .replace(/^## (.*$)/gm, '<h3 class="font-bold text-lg mt-4 mb-2">$1</h3>')
        // Lists
        .replace(/^\* (.*$)/gm, '<li class="ml-4">$1</li>')
        .replace(/^- (.*$)/gm, '<li class="ml-4">$1</li>')
        .replace(/^\d+\. (.*$)/gm, '<li class="ml-4 list-decimal">$1</li>')
        // Line breaks
        .replace(/\n\n/g, '</p><p class="mt-2">')
        .replace(/\n/g, '<br/>');

      return (
        <div
          key={index}
          className="prose prose-sm max-w-none"
          dangerouslySetInnerHTML={{ __html: `<p>${processed}</p>` }}
        />
      );
    });
  };

  return (
    <div className="flex items-start space-x-3 animate-fade-in">
      {/* Avatar */}
      <div className="flex-shrink-0 w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
        <svg
          className="w-5 h-5 text-white"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 10V3L4 14h7v7l9-11h-7z"
          />
        </svg>
      </div>

      {/* Message */}
      <div className="flex-1 bg-gray-50 rounded-2xl rounded-tl-none px-4 py-3 max-w-[85%]">
        <div className="text-gray-800 text-sm leading-relaxed">
          {formatContent(message.content)}
        </div>
        <p className="text-xs text-gray-400 mt-2">
          {new Date(message.created_at).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>
    </div>
  );
}

export default AgentMessage;
