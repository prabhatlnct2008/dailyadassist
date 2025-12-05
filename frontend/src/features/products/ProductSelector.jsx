import { useState } from 'react';
import { usePageProducts } from './hooks/usePageProducts';

export function ProductSelector({ workspaceId, pageId, activeProductId, onChange }) {
  const { data: products, isLoading } = usePageProducts(workspaceId, pageId);
  const [isOpen, setIsOpen] = useState(false);

  const activeProduct = products?.find((p) => p.id === activeProductId);

  const handleSelect = (product) => {
    onChange(product);
    setIsOpen(false);
  };

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2 text-sm text-gray-500">
        <div className="animate-spin h-4 w-4 border-2 border-primary-600 border-t-transparent rounded-full" />
        <span>Loading products...</span>
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm"
      >
        {activeProduct?.image_url && (
          <img
            src={activeProduct.image_url}
            alt={activeProduct.name}
            className="w-6 h-6 rounded object-cover"
          />
        )}
        <span className="text-gray-700">
          {activeProduct ? activeProduct.name : 'No product selected'}
        </span>
        <svg
          className={`w-4 h-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)} />

          {/* Dropdown */}
          <div className="absolute top-full left-0 mt-1 w-72 bg-white border border-gray-200 rounded-lg shadow-lg z-20 max-h-80 overflow-y-auto">
            {/* No product option */}
            <button
              onClick={() => handleSelect(null)}
              className={`w-full flex items-center space-x-3 px-4 py-3 hover:bg-gray-50 transition-colors text-left ${
                !activeProductId ? 'bg-primary-50' : ''
              }`}
            >
              <div className="w-10 h-10 bg-gray-200 rounded flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-700">No product selected</p>
                <p className="text-xs text-gray-500">General page chat</p>
              </div>
            </button>

            {/* Divider */}
            {products && products.length > 0 && (
              <div className="border-t border-gray-200 my-1" />
            )}

            {/* Products */}
            {products?.map((product) => (
              <button
                key={product.id}
                onClick={() => handleSelect(product)}
                className={`w-full flex items-center space-x-3 px-4 py-3 hover:bg-gray-50 transition-colors text-left ${
                  activeProductId === product.id ? 'bg-primary-50' : ''
                }`}
              >
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="w-10 h-10 rounded object-cover"
                  />
                ) : (
                  <div className="w-10 h-10 bg-gray-200 rounded flex items-center justify-center">
                    <svg
                      className="w-5 h-5 text-gray-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                      />
                    </svg>
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {product.name}
                  </p>
                  {product.short_description && (
                    <p className="text-xs text-gray-500 truncate">
                      {product.short_description}
                    </p>
                  )}
                  {product.price_range && (
                    <p className="text-xs text-primary-600 mt-0.5">
                      {product.price_range}
                    </p>
                  )}
                </div>
                {activeProductId === product.id && (
                  <svg
                    className="w-5 h-5 text-primary-600 flex-shrink-0"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </button>
            ))}

            {/* No products message */}
            {products && products.length === 0 && (
              <div className="px-4 py-6 text-center text-sm text-gray-500">
                <p>No products tagged to this page yet.</p>
                <p className="mt-1 text-xs">Add products in settings.</p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default ProductSelector;
