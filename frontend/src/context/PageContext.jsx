import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { pagesApi } from '../api/pages';
import { useWorkspace } from './WorkspaceContext';

const PageContext = createContext(null);

export function PageProvider({ children }) {
  const { activeWorkspace } = useWorkspace();
  const [pages, setPages] = useState([]);
  const [activePage, setActivePage] = useState(null);
  const [activeProduct, setActiveProduct] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadPages = useCallback(async (workspaceId) => {
    if (!workspaceId) {
      setPages([]);
      setActivePage(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    try {
      const data = await pagesApi.listWorkspacePages(workspaceId);
      setPages(data);

      // Set first page as active if none selected
      if (!activePage && data.length > 0) {
        setActivePage(data[0]);
      }
    } catch (error) {
      console.error('Failed to load pages:', error);
    } finally {
      setIsLoading(false);
    }
  }, [activePage]);

  const selectPage = useCallback((page) => {
    setActivePage(page);
    // Reset product selection when changing pages
    setActiveProduct(null);
  }, []);

  const selectProduct = useCallback((product) => {
    setActiveProduct(product);
  }, []);

  // Load pages when workspace changes
  useEffect(() => {
    if (activeWorkspace) {
      loadPages(activeWorkspace.id);
    } else {
      setPages([]);
      setActivePage(null);
      setIsLoading(false);
    }
  }, [activeWorkspace]);

  const value = {
    pages,
    activePage,
    setActivePage: selectPage,
    activeProduct,
    setActiveProduct: selectProduct,
    isLoading,
  };

  return (
    <PageContext.Provider value={value}>
      {children}
    </PageContext.Provider>
  );
}

export function usePage() {
  const context = useContext(PageContext);
  if (!context) {
    throw new Error('usePage must be used within a PageProvider');
  }
  return context;
}

export default PageContext;
