import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { workspacesApi } from '../api/workspaces';

const WorkspaceContext = createContext(null);

export function WorkspaceProvider({ children }) {
  const [workspaces, setWorkspaces] = useState([]);
  const [activeWorkspace, setActiveWorkspace] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadWorkspaces = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await workspacesApi.listWorkspaces();
      setWorkspaces(data);

      // Set active workspace if not already set
      if (!activeWorkspace && data.length > 0) {
        // Find the active workspace or default to first
        const active = data.find((ws) => ws.is_active) || data[0];
        setActiveWorkspace(active);
      }
    } catch (error) {
      console.error('Failed to load workspaces:', error);
    } finally {
      setIsLoading(false);
    }
  }, [activeWorkspace]);

  const refetch = useCallback(() => {
    return loadWorkspaces();
  }, [loadWorkspaces]);

  const selectWorkspace = useCallback(
    async (workspace) => {
      try {
        // Activate the workspace on the backend
        await workspacesApi.activateWorkspace(workspace.id);
        setActiveWorkspace(workspace);
      } catch (error) {
        console.error('Failed to activate workspace:', error);
        throw error;
      }
    },
    []
  );

  useEffect(() => {
    loadWorkspaces();
  }, []);

  const value = {
    workspaces,
    activeWorkspace,
    setActiveWorkspace: selectWorkspace,
    isLoading,
    refetch,
  };

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error('useWorkspace must be used within a WorkspaceProvider');
  }
  return context;
}

export default WorkspaceContext;
