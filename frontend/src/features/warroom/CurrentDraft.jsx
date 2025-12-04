import { useDraft } from '../../context/DraftContext';
import { Button } from '../shared/Button';
import { AdMockup } from './AdMockup';

export function CurrentDraft() {
  const { currentDraft, variants, selectedVariant, setSelectedVariant, isEditing, setIsEditing, publishDraft } = useDraft();

  if (!currentDraft) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center px-8">
        <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <svg
            className="w-6 h-6 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Draft Yet</h3>
        <p className="text-gray-500 max-w-sm">
          Start a conversation with the agent to create your first ad draft. It will appear here for preview.
        </p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Variant Selector */}
      {variants.length > 1 && (
        <div className="flex items-center space-x-2 mb-4">
          <span className="text-sm text-gray-500">Variant:</span>
          <div className="flex space-x-1">
            {variants.map((_, index) => (
              <button
                key={index}
                onClick={() => setSelectedVariant(index)}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  selectedVariant === index
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Ad Mockup */}
      <div className="flex-1 overflow-y-auto">
        <AdMockup draft={currentDraft} />
      </div>

      {/* Action Buttons */}
      <div className="mt-4 flex items-center space-x-3">
        <Button
          variant="secondary"
          onClick={() => setIsEditing(true)}
          className="flex-1"
        >
          Edit Manually
        </Button>
        <Button
          variant="primary"
          onClick={() => publishDraft(currentDraft.id)}
          className="flex-1"
        >
          Approve & Publish
        </Button>
      </div>
    </div>
  );
}

export default CurrentDraft;
