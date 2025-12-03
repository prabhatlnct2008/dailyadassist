export function AdMockup({ draft }) {
  const ctaLabels = {
    learn_more: 'Learn More',
    shop_now: 'Shop Now',
    sign_up: 'Sign Up',
    contact_us: 'Contact Us',
    book_now: 'Book Now',
    download: 'Download',
    get_offer: 'Get Offer',
  };

  return (
    <div className="card overflow-hidden max-w-md mx-auto">
      {/* Header */}
      <div className="flex items-center space-x-3 p-4">
        <div className="w-10 h-10 bg-gray-300 rounded-full" />
        <div>
          <p className="font-semibold text-sm">Your Page Name</p>
          <p className="text-xs text-gray-500">Sponsored</p>
        </div>
      </div>

      {/* Primary Text */}
      <div className="px-4 pb-3">
        <p className="text-sm text-gray-800 whitespace-pre-wrap">
          {draft?.primary_text || 'Your ad primary text will appear here...'}
        </p>
      </div>

      {/* Media */}
      <div className="aspect-[1.91/1] bg-gray-200 relative">
        {draft?.media_url ? (
          <img
            src={draft.media_url}
            alt="Ad creative"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-center text-gray-400">
              <svg
                className="w-12 h-12 mx-auto mb-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <p className="text-sm">Image Preview</p>
            </div>
          </div>
        )}
      </div>

      {/* Link Preview */}
      <div className="bg-gray-50 p-4">
        <p className="text-xs text-gray-500 uppercase mb-1">yourwebsite.com</p>
        <h3 className="font-semibold text-gray-900 mb-1">
          {draft?.headline || 'Your Headline Here'}
        </h3>
        <p className="text-sm text-gray-500">
          {draft?.description || 'Your description text will appear here'}
        </p>
      </div>

      {/* CTA Button */}
      <div className="p-4 border-t border-gray-100">
        <button className="w-full py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold text-sm rounded transition-colors">
          {ctaLabels[draft?.cta] || 'Learn More'}
        </button>
      </div>

      {/* Engagement Bar */}
      <div className="px-4 py-3 border-t border-gray-100 flex items-center justify-between text-gray-500 text-sm">
        <div className="flex items-center space-x-4">
          <button className="flex items-center space-x-1 hover:text-blue-600">
            <span>👍</span>
            <span>Like</span>
          </button>
          <button className="flex items-center space-x-1 hover:text-blue-600">
            <span>💬</span>
            <span>Comment</span>
          </button>
          <button className="flex items-center space-x-1 hover:text-blue-600">
            <span>↗️</span>
            <span>Share</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default AdMockup;
