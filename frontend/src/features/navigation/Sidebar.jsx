import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { AccountOverviewItem } from './AccountOverviewItem';
import { PageListItem } from './PageListItem';
import { pagesApi } from '../../api/pages';
import { workspacesApi } from '../../api/workspaces';

export function Sidebar({ isOpen, onClose }) {
  const [workspace, setWorkspace] = useState(null);
  const [pages, setPages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [hasLegacyConversations, setHasLegacyConversations] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);

      // Get workspaces (assuming first one is active)
      const workspaces = await workspacesApi.getWorkspaces();
      if (workspaces && workspaces.length > 0) {
        const activeWorkspace = workspaces[0];
        setWorkspace(activeWorkspace);

        // Get workspace pages
        const workspacePages = await pagesApi.getWorkspacePages(activeWorkspace.id);
        setPages(workspacePages);

        // Check if any pages have legacy conversations
        // This would need to be determined by a backend API
        // For now, setting to false
        setHasLegacyConversations(false);
      }
    } catch (error) {
      console.error('Error loading sidebar data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 ease-in-out lg:transform-none ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="h-full flex flex-col">
          {/* Workspace Header */}
          <div className="px-4 py-5 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center">
                  <svg
                    className="w-6 h-6 text-white"
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
                <div className="flex-1 min-w-0">
                  <h2 className="text-sm font-semibold text-gray-900 truncate">
                    {loading ? 'Loading...' : workspace?.name || 'My Workspace'}
                  </h2>
                  <p className="text-xs text-gray-500">Daily Ad Agent</p>
                </div>
              </div>

              {/* Mobile close button */}
              <button
                onClick={onClose}
                className="lg:hidden text-gray-400 hover:text-gray-600"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex-1 overflow-y-auto px-3 py-4">
            {loading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              </div>
            ) : (
              <>
                {/* Account Section */}
                <div className="mb-6">
                  <h3 className="px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Account
                  </h3>
                  <AccountOverviewItem />
                </div>

                {/* Pages Section */}
                <div className="mb-6">
                  <div className="flex items-center justify-between px-3 mb-2">
                    <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      Pages
                    </h3>
                    <span className="text-xs text-gray-400">{pages.length}</span>
                  </div>
                  <div className="space-y-1">
                    {pages.length > 0 ? (
                      pages.map((page) => (
                        <PageListItem key={page.id} page={page} />
                      ))
                    ) : (
                      <p className="px-3 py-2 text-sm text-gray-500">No pages yet</p>
                    )}
                  </div>
                </div>

                {/* Archive Link */}
                {hasLegacyConversations && (
                  <div className="pt-4 border-t border-gray-200">
                    <Link
                      to="/app/archive"
                      className="flex items-center space-x-3 px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <svg
                        className="w-5 h-5"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"
                        />
                      </svg>
                      <span className="text-sm">Archived Conversations</span>
                    </Link>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Settings Link at Bottom */}
          <div className="border-t border-gray-200 p-3">
            <Link
              to="/settings"
              className="flex items-center space-x-3 px-3 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
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
              <span className="text-sm">Settings</span>
            </Link>
          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
