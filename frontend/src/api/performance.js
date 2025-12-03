import client from './client';

export const performanceApi = {
  // Get performance summary
  getSummary: async (timeRange = 'last_7_days') => {
    const response = await client.get('/performance/summary', {
      params: { time_range: timeRange },
    });
    return response.data;
  },

  // Get top performers
  getTopPerformers: async (metric = 'roas', timeRange = 'last_7_days', limit = 5) => {
    const response = await client.get('/performance/top-performers', {
      params: { metric, time_range: timeRange, limit },
    });
    return response.data;
  },

  // Get underperformers
  getUnderperformers: async (metric = 'roas', threshold = 1.0, timeRange = 'last_7_days') => {
    const response = await client.get('/performance/underperformers', {
      params: { metric, threshold, time_range: timeRange },
    });
    return response.data;
  },

  // Get campaign metrics
  getCampaigns: async (timeRange = 'last_7_days', status = null) => {
    const params = { time_range: timeRange };
    if (status) params.status = status;
    const response = await client.get('/performance/campaigns', { params });
    return response.data;
  },
};

export default performanceApi;
