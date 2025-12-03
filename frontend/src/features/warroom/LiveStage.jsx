import { useState } from 'react';
import { Tabs } from '../shared/Tabs';
import { CurrentDraft } from './CurrentDraft';
import { PastPerformance } from './PastPerformance';
import { ActivityLog } from './ActivityLog';

const TABS = [
  { id: 'draft', label: 'Current Draft' },
  { id: 'performance', label: 'Past Performance' },
  { id: 'activity', label: 'Activity Log' },
];

export function LiveStage() {
  const [activeTab, setActiveTab] = useState('draft');

  return (
    <div className="flex-1 flex flex-col min-h-0 p-4">
      <Tabs tabs={TABS} activeTab={activeTab} onChange={setActiveTab} />

      <div className="flex-1 mt-4 overflow-hidden">
        {activeTab === 'draft' && <CurrentDraft />}
        {activeTab === 'performance' && <PastPerformance />}
        {activeTab === 'activity' && <ActivityLog />}
      </div>
    </div>
  );
}

export default LiveStage;
