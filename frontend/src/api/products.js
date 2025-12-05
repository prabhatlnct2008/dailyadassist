import client from './client';

export const productsApi = {
  // List products for workspace
  list: async (workspaceId) => {
    const response = await client.get(`/workspaces/${workspaceId}/products`);
    return response.data;
  },

  // Get products tagged to a specific page
  listForPage: async (workspaceId, pageId) => {
    const response = await client.get(`/workspaces/${workspaceId}/products`, {
      params: { page_id: pageId },
    });
    return response.data;
  },

  // Get product by ID
  get: async (workspaceId, productId) => {
    const response = await client.get(`/workspaces/${workspaceId}/products/${productId}`);
    return response.data;
  },

  // Create product
  create: async (workspaceId, data) => {
    const response = await client.post(`/workspaces/${workspaceId}/products`, data);
    return response.data;
  },

  // Update product
  update: async (workspaceId, productId, data) => {
    const response = await client.put(`/workspaces/${workspaceId}/products/${productId}`, data);
    return response.data;
  },

  // Delete product
  delete: async (workspaceId, productId) => {
    const response = await client.delete(`/workspaces/${workspaceId}/products/${productId}`);
    return response.data;
  },

  // Tag product to pages
  tagPages: async (workspaceId, productId, pageIds) => {
    const response = await client.post(
      `/workspaces/${workspaceId}/products/${productId}/tag-pages`,
      { page_ids: pageIds }
    );
    return response.data;
  },
};

export default productsApi;
