import React, { useState } from 'react';
import { postAnalyze } from '../lib/api';
import { BASE_COLORS } from '../lib/colors';
import { useGenomeStore } from '../store/useGenomeStore';

export const StatsPanel: React.FC = () => {
  const { analysis, rawInputText, setAnalysis } = useGenomeStore();
  const [loadingComp, setLoadingComp] = useState<boolean>(false);

  if (!analysis) {
    return (
      <div className="text-[13px] text-[#6B7680]">
        Load a FASTA file or click Load sample to inspect sequence statistics.
      </div>
    );
  }

  const { counts, length, gc_percent, at_percent, molecular_weight_da, molecular_weight_note, gc_profile } =
    analysis;

  const polylinePoints = gc_profile
    .map((pt, i) => {
      const x = gc_profile.length > 1 ? Math.round((i / (gc_profile.length - 1)) * 280) : 140;
      const y = Math.round(52 - (pt.gc_percent / 100) * 44);
      return `${x},${y}`;
    })
    .join(' ');

  async function handleRequestComplements(): Promise<void> {
    if (!rawInputText || !analysis) return;
    setLoadingComp(true);
    try {
      const res = await postAnalyze({
        sequence: rawInputText,
        sequence_id: analysis.id,
        include_complements: true,
        gc_window_size: 100,
      });
      setAnalysis(res);
    } finally {
      setLoadingComp(false);
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
      <div className="flex flex-col gap-1">
        <div className="text-[13px] text-[#6B7680]">Sequence metrics</div>
        <div className="text-[15px]">
          Length <span className="font-mono">{length.toLocaleString()} bp</span> · GC{' '}
          <span className="font-mono">{gc_percent.toFixed(2)}%</span> · AT{' '}
          <span className="font-mono">{at_percent.toFixed(2)}%</span>
        </div>
        <div className="text-[13px] text-[#6B7680]">
          Single-stranded weight{' '}
          <span className="font-mono text-[#1A1F24]">
            {molecular_weight_da.toLocaleString()} Da
          </span>{' '}
          ({molecular_weight_note})
        </div>
        {!analysis.complement ? (
          <button
            type="button"
            onClick={() => void handleRequestComplements()}
            className="hover:underline text-[13px] text-[#1A1F24] text-left mt-1"
          >
            {loadingComp ? 'Computing complement strands...' : 'Load complement & reverse complement'}
          </button>
        ) : (
          <div className="text-[13px] text-[#6B7680] font-mono truncate">
            RevComp 5&apos;→3&apos;: {analysis.reverse_complement?.slice(0, 36)}...
          </div>
        )}
      </div>

      <div className="flex flex-col gap-1.5">
        <div className="text-[13px] text-[#6B7680]">Base composition</div>
        {(['A', 'T', 'G', 'C', 'N'] as const).map((base) => {
          const count = counts[base];
          const pct = length > 0 ? Math.round((count / length) * 100) : 0;
          return (
            <div key={base} className="grid grid-cols-[20px_1fr_72px] items-center gap-2 text-[13px]">
              <span className="font-mono font-bold" style={{ color: BASE_COLORS[base] }}>
                {base}
              </span>
              <div className="h-2 bg-[#F5F6F7] overflow-hidden">
                <div
                  className="h-full"
                  style={{ width: `${pct}%`, backgroundColor: BASE_COLORS[base] }}
                />
              </div>
              <span className="font-mono text-right text-[#1A1F24]">{count}</span>
            </div>
          );
        })}
      </div>

      <div className="flex flex-col gap-1">
        <div className="text-[13px] text-[#6B7680]">Sliding window GC (100 bp)</div>
        <svg viewBox="0 0 280 56" className="w-full h-14 overflow-visible">
          <line x1="0" y1="28" x2="280" y2="28" stroke="#E3E7EA" strokeWidth="1" />
          <polyline
            fill="none"
            stroke="#1A1F24"
            strokeWidth="1.5"
            points={polylinePoints}
          />
        </svg>
      </div>
    </div>
  );
};
