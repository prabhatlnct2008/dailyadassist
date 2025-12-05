import { useState } from 'react';
import { Link } from 'react-router-dom';

export function PinnedSummary({ pinnedContent, archivedCount = 0 }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!pinnedContent) {
    return null;
  }

  return (
    <div className="mb-6 bg-amber-50 border border-amber-200 rounded-lg overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-amber-100 transition-colors"
      >
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0 w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center">
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
                d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
              />
            </svg>
          </div>
          <div className="text-left">
            <h3 className="text-sm font-semibold text-amber-900">
              Legacy Migration Summary
            </h3>
            <p className="text-xs text-amber-700">
              {archivedCount > 0
                ? `You have ${archivedCount} archived conversation${archivedCount !== 1 ? 's' : ''}`
                : 'Your previous conversation history'}
            </p>
          </div>
        </div>
        <svg
          className={`w-5 h-5 text-amber-700 transition-transform ${
            isExpanded ? 'rotate-180' : ''
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expandable Content */}
      {isExpanded && (
        <div className="px-4 pb-4 space-y-3 border-t border-amber-200">
          {/* Summary Content */}
          <div className="mt-3 prose prose-sm max-w-none">
            <div
              className="text-sm text-amber-900 leading-relaxed whitespace-pre-wrap"
              dangerouslySetInnerHTML={{ __html: formatContent(pinnedContent) }}
            />
          </div>

          {/* Actions */}
          {archivedCount > 0 && (
            <div className="flex items-center justify-between pt-3 border-t border-amber-200">
              <p className="text-xs text-amber-700">
                This summary was generated from your previous conversations
              </p>
              <Link
                to="/app/archive"
                className="inline-flex items-center space-x-1 px-3 py-1.5 bg-amber-500 hover:bg-amber-600 text-white text-xs font-medium rounded-lg transition-colors"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"
                  />
                </svg>
                <span>View Archive</span>
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Simple content formatter
function formatContent(content) {
  if (!content) return '';

  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/^### (.*$)/gm, '<h4 class="font-semibold text-base mt-2 mb-1">$1</h4>')
    .replace(/^## (.*$)/gm, '<h3 class="font-bold text-base mt-3 mb-2">$1</h3>')
    .replace(/^\* (.*$)/gm, '<li class="ml-4">$1</li>')
    .replace(/^- (.*$)/gm, '<li class="ml-4">$1</li>')
    .replace(/\n\n/g, '</p><p class="mt-2">')
    .replace(/\n/g, '<br/>');
}

export default PinnedSummary;
