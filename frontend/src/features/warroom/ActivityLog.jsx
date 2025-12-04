import { useState, useEffect } from 'react';
import { Loader } from '../shared/Loader';

// Mock activity data
const mockActivities = [
  {
    id: '1',
    action_type: 'campaign_published',
    entity_type: 'campaign',
    rationale: 'Published "Red Hoodie - Winter Sale" campaign',
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    is_agent_action: false,
  },
  {
    id: '2',
    action_type: 'recommendation_made',
    entity_type: 'campaign',
    rationale: 'Suggested increasing budget by 30% for "Red Hoodie - Winter Sale"',
    created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    is_agent_action: true,
  },
  {
    id: '3',
    action_type: 'draft_created',
    entity_type: 'draft',
    rationale: 'Created 3 ad copy variants for new campaign',
    created_at: new Date(Date.now() - 25 * 60 * 60 * 1000).toISOString(),
    is_agent_action: true,
  },
  {
    id: '4',
    action_type: 'budget_changed',
    entity_type: 'adset',
    rationale: 'Increased daily budget from $50 to $75',
    created_at: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString(),
    is_agent_action: false,
  },
];

export function ActivityLog() {
  const [activities, setActivities] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Mock loading
    setTimeout(() => {
      setActivities(mockActivities);
      setIsLoading(false);
    }, 500);
  }, []);

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader />
      </div>
    );
  }

  const getActionIcon = (actionType) => {
    const icons = {
      campaign_published: '🚀',
      recommendation_made: '💡',
      draft_created: '📝',
      budget_changed: '💰',
      campaign_paused: '⏸️',
      recommendation_applied: '✅',
    };
    return icons[actionType] || '📌';
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="space-y-4">
        {activities.map((activity) => (
          <div
            key={activity.id}
            className="flex items-start space-x-3 p-3 bg-white rounded-lg border border-gray-100"
          >
            <div className="flex-shrink-0 w-7 h-7 bg-gray-100 rounded-full flex items-center justify-center text-base">
              {getActionIcon(activity.action_type)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-900">{activity.rationale}</p>
              <div className="flex items-center space-x-2 mt-1">
                <span className="text-xs text-gray-500">
                  {formatTimeAgo(activity.created_at)}
                </span>
                {activity.is_agent_action && (
                  <span className="inline-flex items-center px-1.5 py-0.5 bg-primary-100 text-primary-700 text-xs rounded">
                    Agent
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ActivityLog;
