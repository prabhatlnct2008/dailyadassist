import client from './client';

export const pagesApi = {
  // List all workspace pages
  listWorkspacePages: async (workspaceId) => {
    const response = await client.get(`/workspaces/${workspaceId}/pages`);
    return response.data;
  },

  // Get a specific workspace page
  getWorkspacePage: async (workspaceId, pageId) => {
    const response = await client.get(`/workspaces/${workspaceId}/pages/${pageId}`);
    return response.data;
  },

  // Update page settings
  updatePageSettings: async (workspaceId, pageId, settings) => {
    const response = await client.put(
      `/workspaces/${workspaceId}/pages/${pageId}/settings`,
      settings
    );
    return response.data;
  },

  // Get products for a specific page
  getPageProducts: async (workspaceId, pageId) => {
    const response = await client.get(`/workspaces/${workspaceId}/pages/${pageId}/products`);
    return response.data;
  },
};

export default pagesApi;
