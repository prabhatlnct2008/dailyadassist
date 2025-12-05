import client from './client';

export const workspacesApi = {
  // List all workspaces
  listWorkspaces: async () => {
    const response = await client.get('/workspaces');
    return response.data;
  },

  // Create a new workspace
  createWorkspace: async (data) => {
    const response = await client.post('/workspaces', data);
    return response.data;
  },

  // Get a specific workspace
  getWorkspace: async (id) => {
    const response = await client.get(`/workspaces/${id}`);
    return response.data;
  },

  // Update a workspace
  updateWorkspace: async (id, data) => {
    const response = await client.put(`/workspaces/${id}`, data);
    return response.data;
  },

  // Delete a workspace
  deleteWorkspace: async (id) => {
    const response = await client.delete(`/workspaces/${id}`);
    return response.data;
  },

  // Activate a workspace
  activateWorkspace: async (id) => {
    const response = await client.post(`/workspaces/${id}/activate`);
    return response.data;
  },

  // Setup pages for a workspace
  setupPages: async (workspaceId, pages) => {
    const response = await client.post(`/workspaces/${workspaceId}/pages/setup`, {
      pages,
    });
    return response.data;
  },
};

export default workspacesApi;
