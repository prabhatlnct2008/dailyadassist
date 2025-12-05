import client from './client';

export const productsApi = {
  // List all products in a workspace
  listProducts: async (workspaceId) => {
    const response = await client.get(`/workspaces/${workspaceId}/products`);
    return response.data;
  },

  // Create a new product
  createProduct: async (workspaceId, data) => {
    const response = await client.post(`/workspaces/${workspaceId}/products`, data);
    return response.data;
  },

  // Get a specific product
  getProduct: async (workspaceId, productId) => {
    const response = await client.get(`/workspaces/${workspaceId}/products/${productId}`);
    return response.data;
  },

  // Update a product
  updateProduct: async (workspaceId, productId, data) => {
    const response = await client.put(
      `/workspaces/${workspaceId}/products/${productId}`,
      data
    );
    return response.data;
  },

  // Delete a product
  deleteProduct: async (workspaceId, productId) => {
    const response = await client.delete(`/workspaces/${workspaceId}/products/${productId}`);
    return response.data;
  },

  // Tag product to pages
  tagProductToPages: async (workspaceId, productId, pageIds) => {
    const response = await client.post(
      `/workspaces/${workspaceId}/products/${productId}/tag-pages`,
      { page_ids: pageIds }
    );
    return response.data;
  },
};

export default productsApi;
