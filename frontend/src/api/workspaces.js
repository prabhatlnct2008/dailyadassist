import client from './client';

export const workspacesApi = {
  // Get all workspaces
  getWorkspaces: async () => {
    const response = await client.get('/workspaces');
    return response.data;
  },

  // Get a specific workspace with details
  getWorkspace: async (workspaceId) => {
    const response = await client.get(`/workspaces/${workspaceId}`);
    return response.data;
  },

  // Create a workspace
  createWorkspace: async (data) => {
    const response = await client.post('/workspaces', data);
    return response.data;
  },

  // Update a workspace
  updateWorkspace: async (workspaceId, data) => {
    const response = await client.put(`/workspaces/${workspaceId}`, data);
    return response.data;
  },
};

export default workspacesApi;
