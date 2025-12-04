export function UserMessage({ message }) {
  return (
    <div className="flex items-start justify-end space-x-3 animate-fade-in">
      {/* Message */}
      <div className="bg-primary-600 text-white rounded-2xl rounded-tr-none px-4 py-3 max-w-[85%]">
        <p className="text-sm leading-relaxed">{message.content}</p>
        <p className="text-xs text-primary-200 mt-2">
          {new Date(message.created_at).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>

      {/* Avatar */}
      <div className="flex-shrink-0 w-8 h-8 bg-gray-300 rounded-lg flex items-center justify-center">
        <svg
          className="w-5 h-5 text-gray-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
          />
        </svg>
      </div>
    </div>
  );
}

export default UserMessage;
