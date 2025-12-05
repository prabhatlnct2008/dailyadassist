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

  // Get workspace conversations
  getWorkspaceConversations: async (workspaceId) => {
    const response = await client.get(`/workspaces/${workspaceId}/conversations`);
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

  // Get legacy conversations (pre-workspace)
  getLegacyConversations: async () => {
    const response = await client.get('/conversations/legacy');
    return response.data;
  },

  // Archive a conversation
  archiveConversation: async (conversationId) => {
    const response = await client.post(`/conversations/${conversationId}/archive`);
    return response.data;
  },
};

export default conversationsApi;
