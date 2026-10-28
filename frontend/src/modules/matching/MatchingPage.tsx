import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { SkillMatchingPage } from './SkillMatchingPage';
import { HeatmapPage } from './HeatmapPage';

export const MatchingPage: React.FC = () => {
  const { currentProfile, parsedResume, selectedJd } = useApp();
  const [currentView, setCurrentView] = useState<'matching' | 'heatmap'>('matching');
  const [selectedCandidate, setSelectedCandidate] = useState<string | undefined>(
    (currentProfile?.skills?.length || parsedResume?.skills?.length) ? 'active_candidate' : undefined
  );
  const [selectedJdId, setSelectedJdId] = useState<string | undefined>(
    selectedJd ? ('id' in selectedJd ? selectedJd.id : 'active_jd') : undefined
  );

  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {currentView === 'matching' ? (
        <SkillMatchingPage
          initialCandidateId={selectedCandidate}
          initialJdId={selectedJdId}
          onOpenHeatmap={() => setCurrentView('heatmap')}
        />
      ) : (
        <HeatmapPage
          onSelectCandidateAndJD={(candId, jdId) => {
            setSelectedCandidate(candId);
            setSelectedJdId(jdId);
            setCurrentView('matching');
          }}
          onBackToMatching={() => setCurrentView('matching')}
        />
      )}
    </div>
  );
};

export default MatchingPage;
