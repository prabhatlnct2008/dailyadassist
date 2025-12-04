import client from './client';

export const userApi = {
  // Get preferences
  getPreferences: async () => {
    const response = await client.get('/users/preferences');
    return response.data;
  },

  // Update preferences
  updatePreferences: async (data) => {
    const response = await client.put('/users/preferences', data);
    return response.data;
  },

  // Get ad accounts
  getAdAccounts: async () => {
    const response = await client.get('/users/ad-accounts');
    return response.data;
  },

  // Set primary ad account
  setPrimaryAdAccount: async (accountId) => {
    const response = await client.put(`/users/ad-accounts/${accountId}/primary`);
    return response.data;
  },

  // Get Facebook pages
  getPages: async () => {
    const response = await client.get('/users/pages');
    return response.data;
  },

  // Set primary page
  setPrimaryPage: async (pageId) => {
    const response = await client.put(`/users/pages/${pageId}/primary`);
    return response.data;
  },
};

export default userApi;
