import { useState, useEffect } from 'react';
import { performanceApi } from '../../api/performance';
import { Loader } from '../shared/Loader';

export function PastPerformance() {
  const [campaigns, setCampaigns] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('last_7_days');

  useEffect(() => {
    loadCampaigns();
  }, [timeRange]);

  const loadCampaigns = async () => {
    setIsLoading(true);
    try {
      const data = await performanceApi.getCampaigns(timeRange);
      setCampaigns(data.campaigns || []);
    } catch (error) {
      console.error('Failed to load campaigns:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Time Range Selector */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-gray-900">Campaign Performance</h3>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="input w-auto text-sm"
        >
          <option value="today">Today</option>
          <option value="yesterday">Yesterday</option>
          <option value="last_7_days">Last 7 Days</option>
          <option value="last_14_days">Last 14 Days</option>
          <option value="last_30_days">Last 30 Days</option>
        </select>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        {campaigns.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            No campaign data available
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Campaign</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Spend</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">ROAS</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">CTR</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Conv.</th>
                <th className="text-center px-4 py-3 font-medium text-gray-600">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {campaigns.map((campaign) => (
                <tr key={campaign.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-medium text-gray-900">{campaign.name}</p>
                      <p className="text-xs text-gray-500">{campaign.objective}</p>
                    </div>
                  </td>
                  <td className="text-right px-4 py-3 text-gray-900">
                    ${campaign.spend?.toFixed(2)}
                  </td>
                  <td className="text-right px-4 py-3">
                    <span
                      className={`font-medium ${
                        campaign.roas >= 3
                          ? 'text-green-600'
                          : campaign.roas >= 1
                          ? 'text-yellow-600'
                          : 'text-red-600'
                      }`}
                    >
                      {campaign.roas?.toFixed(1)}x
                    </span>
                  </td>
                  <td className="text-right px-4 py-3 text-gray-900">
                    {campaign.ctr?.toFixed(2)}%
                  </td>
                  <td className="text-right px-4 py-3 text-gray-900">
                    {campaign.conversions}
                  </td>
                  <td className="text-center px-4 py-3">
                    <span
                      className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        campaign.status === 'ACTIVE'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {campaign.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default PastPerformance;
