import client from './client';

export const conversationsApi = {
  // List conversations
  list: async () => {
    const response = await client.get('/conversations');
    return response.data;
  },

  // Create conversation
  create: async (data = {}) => {
    const response = await client.post('/conversations', data);
    return response.data;
  },

  // Get conversation with messages
  get: async (id) => {
    const response = await client.get(`/conversations/${id}`);
    return response.data;
  },

  // Get messages
  getMessages: async (conversationId, page = 1, perPage = 50) => {
    const response = await client.get(`/conversations/${conversationId}/messages`, {
      params: { page, per_page: perPage },
    });
    return response.data;
  },

  // Send message
  sendMessage: async (conversationId, content) => {
    const response = await client.post(`/conversations/${conversationId}/messages`, {
      content,
    });
    return response.data;
  },

  // Get account overview conversation
  getAccountOverview: async (workspaceId) => {
    const response = await client.get(`/workspaces/${workspaceId}/conversations/overview`);
    return response.data;
  },

  // Get page conversation
  getPageConversation: async (pageId) => {
    const response = await client.get(`/pages/${pageId}/conversation`);
    return response.data;
  },

  // Get legacy (archived) conversations
  getLegacyConversations: async () => {
    const response = await client.get('/conversations/legacy');
    return response.data;
  },

  // Update conversation's active product
  updateActiveProduct: async (conversationId, productId) => {
    const response = await client.put(`/conversations/${conversationId}/active-product`, {
      product_id: productId,
    });
    return response.data;
  },
};

export default conversationsApi;
