import * as React from 'react';
import { usePolling } from '@/hooks/usePolling';
import { api } from '@/api/client';
import { LoadingState, ErrorState, EmptyState } from '@/components/ui/State';

export function Influence() {
  const { data: influencers, isLoading, error } = usePolling({
    fetcher: () => api.getInfluencers(24),
    intervalMs: 30000
  });

  return (
    <div className="flex flex-col w-full h-full min-h-0 gap-6">
      {/* Header Banner */}
      <section className="w-full bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] px-6 lg:px-8 py-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-5 shrink-0">
        <div className="flex items-start gap-4 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-surface-secondary flex items-center justify-center shrink-0 text-text-secondary mt-0.5">
            <span className="material-symbols-outlined text-[18px] text-primary">troubleshoot</span>
          </div>
          <div className="flex flex-col min-w-0">
            <div className="flex flex-col xl:flex-row xl:items-baseline gap-x-3 gap-y-0.5">
              <h1 className="font-sans text-[20px] text-text-primary font-semibold tracking-tight">
                Global Influence
              </h1>
              <p className="font-sans text-[13px] text-text-secondary">
                Top nodes ordered by PageRank across the entire telemetry window
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] flex-1 overflow-hidden flex flex-col">
        {isLoading && !influencers ? (
          <LoadingState message="Loading global influencers..." />
        ) : error ? (
          <ErrorState message="Failed to load influence data. Check API connectivity." />
        ) : !influencers || influencers.length === 0 ? (
          <EmptyState title="Insufficient Signal" message="Not enough network activity to determine significant influencers." />
        ) : (
          <div className="w-full overflow-y-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-surface-header border-b border-border-subtle text-text-muted font-mono text-[11px] uppercase tracking-wider sticky top-0 z-10">
                  <th className="py-4 px-6 font-semibold w-16 text-center">Rank</th>
                  <th className="py-4 px-6 font-semibold">User Node</th>
                  <th className="py-4 px-6 font-semibold text-right">PageRank</th>
                  <th className="py-4 px-6 font-semibold text-right">In-Degree</th>
                  <th className="py-4 px-6 font-semibold text-right">Out-Degree</th>
                  <th className="py-4 px-6 font-semibold text-right">Centrality</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-subtle font-sans text-[13px]">
                {influencers.map((inf, idx) => (
                  <tr key={inf.user_id} className="hover:bg-surface-secondary/60 transition-colors">
                    <td className="py-3 px-6 text-center text-text-muted font-mono">{idx + 1}</td>
                    <td className="py-3 px-6 font-medium text-text-primary">{inf.user_id}</td>
                    <td className="py-3 px-6 text-right font-mono text-primary font-medium">{inf.pagerank.toFixed(4)}</td>
                    <td className="py-3 px-6 text-right font-mono text-text-secondary">{inf.in_degree.toFixed(2)}</td>
                    <td className="py-3 px-6 text-right font-mono text-text-secondary">{inf.out_degree.toFixed(2)}</td>
                    <td className="py-3 px-6 text-right font-mono text-text-secondary">{inf.degree_centrality.toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
