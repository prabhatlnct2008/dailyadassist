import client from './client';

export const draftsApi = {
  // List drafts
  list: async (status = null) => {
    const params = status ? { status } : {};
    const response = await client.get('/drafts', { params });
    return response.data;
  },

  // Get draft
  get: async (id) => {
    const response = await client.get(`/drafts/${id}`);
    return response.data;
  },

  // Update draft
  update: async (id, data) => {
    const response = await client.put(`/drafts/${id}`, data);
    return response.data;
  },

  // Publish draft
  publish: async (id) => {
    const response = await client.post(`/drafts/${id}/publish`);
    return response.data;
  },

  // Get variants
  getVariants: async (id) => {
    const response = await client.get(`/drafts/${id}/variants`);
    return response.data;
  },
};

export default draftsApi;
