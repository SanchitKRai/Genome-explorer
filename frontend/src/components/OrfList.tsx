import React from 'react';

export interface OrfListProps {
  title?: string;
}

export const OrfList: React.FC<OrfListProps> = ({ title = 'OrfList' }) => {
  return (
    <section
      aria-label={title}
      className="rounded-xl border border-slate-800 bg-slate-900/80 p-4 shadow-sm"
    >
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {title}
        </h2>
        <span className="rounded bg-slate-800 px-2 py-0.5 text-[11px] font-mono text-emerald-400">
          Phase 1 Shell
        </span>
      </div>
      <p className="text-xs text-slate-400 leading-relaxed">
        Component slot initialized and wired to <code className="text-slate-200">useGenomeStore</code>.
      </p>
    </section>
  );
};
