import React, { useEffect, useState } from 'react';
import { fetchHealth } from './lib/api';
import { useGenomeStore } from './store/useGenomeStore';
import { UploadPanel } from './components/UploadPanel';
import { StatsPanel } from './components/StatsPanel';
import { OrfList } from './components/OrfList';
import { HelixViewer } from './components/HelixViewer';
import { BasePanel } from './components/BasePanel';
import { MutationPanel } from './components/MutationPanel';
import { ExplainPanel } from './components/ExplainPanel';

type BottomTab = 'statistics' | 'orfs' | 'mutations' | 'explain';

export function App(): React.ReactElement {
  const { setHealth, setHealthStatus } = useGenomeStore();
  const [activeTab, setActiveTab] = useState<BottomTab>('statistics');
  const [showUpload, setShowUpload] = useState<boolean>(false);

  useEffect(() => {
    setHealthStatus('loading');
    fetchHealth()
      .then((res) => setHealth(res))
      .catch((err: Error) => setHealthStatus('error', err.message));
  }, [setHealth, setHealthStatus]);

  return (
    <div className="h-screen bg-white text-[#1A1F24] flex flex-col overflow-hidden text-[15px]">
      <header className="h-12 px-6 border-b border-[#E3E7EA] flex items-center justify-between shrink-0">
        <div className="flex items-baseline gap-6">
          <h1 className="text-[20px] font-bold">Genome Explorer AI</h1>
          <span className="text-[13px] text-[#6B7680]">
            <span className="font-mono text-[#1A1F24]">GFP</span> ·{' '}
            <span className="font-mono text-[#1A1F24]">379 bp</span>
          </span>
        </div>
        <div className="flex items-center gap-6">
          <button
            type="button"
            onClick={() => setShowUpload((v) => !v)}
            className="hover:underline text-[15px]"
          >
            Load FASTA
          </button>
          <button type="button" className="hover:underline text-[15px]">
            Export
          </button>
        </div>
      </header>

      {showUpload && (
        <div className="border-b border-[#E3E7EA] bg-[#F5F6F7] px-6 py-3">
          <UploadPanel title="Load FASTA" />
        </div>
      )}

      <section className="h-[100px] px-6 py-2 border-b border-[#E3E7EA] shrink-0 flex flex-col justify-between text-[13px] text-[#6B7680]">
        <div>ruler</div>
        <div>bases</div>
        <div>ORFs</div>
        <div>mutations</div>
      </section>

      <div className="flex-1 grid grid-cols-1 md:grid-cols-[1fr_280px] min-h-0">
        <main className="bg-white h-full">
          <HelixViewer title="3D helix" />
        </main>
        <aside className="border-l border-[#E3E7EA] px-6 py-5 bg-white">
          <BasePanel title="Base 66" />
        </aside>
      </div>

      <section className="border-t border-[#E3E7EA] bg-white shrink-0">
        <nav className="px-6 border-b border-[#E3E7EA] flex items-center gap-7">
          {(['statistics', 'orfs', 'mutations', 'explain'] as const).map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`py-2.5 border-b-2 text-[15px] ${
                activeTab === tab
                  ? 'border-[#E4572E] font-bold text-[#1A1F24]'
                  : 'border-transparent text-[#6B7680] hover:underline'
              }`}
            >
              {tab === 'statistics'
                ? 'Statistics'
                : tab === 'orfs'
                ? 'ORFs'
                : tab === 'mutations'
                ? 'Mutations'
                : 'Explain'}
            </button>
          ))}
        </nav>
        <div className="h-44 px-6 py-4 overflow-y-auto">
          {activeTab === 'statistics' && <StatsPanel title="Statistics" />}
          {activeTab === 'orfs' && <OrfList title="ORFs" />}
          {activeTab === 'mutations' && <MutationPanel title="Mutations" />}
          {activeTab === 'explain' && <ExplainPanel title="Explain" />}
        </div>
      </section>
    </div>
  );
}

export default App;
