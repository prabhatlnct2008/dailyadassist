import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { PageSettingsDrawer } from '../navigation/PageSettingsDrawer';
import { pagesApi } from '../../api/pages';
import { workspacesApi } from '../../api/workspaces';

export function WarRoomHeader({ onMenuClick }) {
  const { pageId } = useParams();
  const [currentPage, setCurrentPage] = useState(null);
  const [workspace, setWorkspace] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, [pageId]);

  const loadData = async () => {
    try {
      setLoading(true);

      // Get workspace
      const workspaces = await workspacesApi.getWorkspaces();
      if (workspaces && workspaces.length > 0) {
        const activeWorkspace = workspaces[0];
        setWorkspace(activeWorkspace);

        // If on a page route, load page data
        if (pageId) {
          const page = await pagesApi.getWorkspacePage(activeWorkspace.id, pageId);
          setCurrentPage(page);

          // Load page products
          const pageProducts = await pagesApi.getPageProducts(activeWorkspace.id, pageId);
          setProducts(pageProducts);

          // Set default product
          const defaultProduct = pageProducts.find((p) => p.is_default);
          setSelectedProduct(defaultProduct || pageProducts[0]);
        } else {
          setCurrentPage(null);
          setProducts([]);
          setSelectedProduct(null);
        }
      }
    } catch (error) {
      console.error('Error loading header data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSettingsClose = (saved) => {
    setShowSettings(false);
    if (saved) {
      loadData(); // Reload data if settings were saved
    }
  };

  return (
    <>
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {/* Mobile menu button */}
          <button
            onClick={onMenuClick}
            className="lg:hidden text-gray-500 hover:text-gray-700"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          {/* Title and Status */}
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 bg-primary-600 rounded-xl flex items-center justify-center">
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
            <div>
              <h1 className="font-semibold text-gray-900">
                {currentPage ? `Active Page: ${currentPage.facebook_page?.name}` : 'Daily Ad Agent'}
              </h1>
              <p className="text-xs text-gray-500">
                {loading ? 'Loading...' : currentPage ? 'Page Chat' : 'Account Overview'}
              </p>
            </div>
          </div>
        </div>

        {/* Right side controls */}
        <div className="flex items-center space-x-4">
          {/* Product Selector (only on page routes) */}
          {currentPage && products.length > 0 && (
            <div className="flex items-center space-x-2">
              <label className="text-sm text-gray-600">Product:</label>
              <select
                value={selectedProduct?.id || ''}
                onChange={(e) => {
                  const product = products.find((p) => p.id === e.target.value);
                  setSelectedProduct(product);
                }}
                className="text-sm border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
              >
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Settings button (only on page routes) */}
          {currentPage && (
            <button
              onClick={() => setShowSettings(true)}
              className="text-gray-500 hover:text-gray-700"
              title="Page Settings"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
            </button>
          )}

          {/* Status indicator */}
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-xs text-gray-500">Ready</span>
          </div>
        </div>
      </header>

      {/* Page Settings Drawer */}
      {currentPage && workspace && (
        <PageSettingsDrawer
          isOpen={showSettings}
          onClose={handleSettingsClose}
          workspaceId={workspace.id}
          pageId={pageId}
          page={currentPage}
        />
      )}
    </>
  );
}

export default WarRoomHeader;
