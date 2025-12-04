import client from './client';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export const agentApi = {
  // Chat with agent (streaming)
  chat: async function* (conversationId, message) {
    const token = localStorage.getItem('access_token');

    const response = await fetch(`${API_BASE_URL}/agent/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ conversation_id: conversationId, message }),
    });

    if (!response.ok) {
      throw new Error('Chat request failed');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            yield data;
          } catch (e) {
            // Skip invalid JSON
          }
        }
      }
    }
  },

  // Get daily brief
  getDailyBrief: async () => {
    const response = await client.get('/agent/daily-brief');
    return response.data;
  },

  // Generate ad copy
  generateCopy: async (data) => {
    const response = await client.post('/agent/generate-copy', data);
    return response.data;
  },

  // Analyze performance
  analyzePerformance: async (timeRange = 'last_7_days') => {
    const response = await client.post('/agent/analyze-performance', { time_range: timeRange });
    return response.data;
  },
};

export default agentApi;
