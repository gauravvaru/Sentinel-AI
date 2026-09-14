import * as React from 'react';
import { Panel } from '@/components/ui/Panel';
import { usePolling } from '@/hooks/usePolling';
import { api } from '@/api/client';
import { LoadingState, ErrorState, EmptyState } from '@/components/ui/State';
import { useSearchParams } from 'react-router-dom';

export function Network() {
  const [searchParams] = useSearchParams();
  const topicId = searchParams.get('topic') || undefined;

  const { data: influencers, isLoading: loadingInfluencers } = usePolling({
    fetcher: () => api.getInfluencers(24, topicId),
    intervalMs: 30000
  });

  const { data: communities, isLoading: loadingCommunities } = usePolling({
    fetcher: () => api.getCommunities(24, topicId),
    intervalMs: 30000
  });

  return (
    <div className="flex flex-col w-full h-full min-h-0 gap-6">
      {/* Header Banner */}
      <section className="w-full bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] px-6 lg:px-8 py-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-5 shrink-0">
        <div className="flex items-start gap-4 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-surface-secondary flex items-center justify-center shrink-0 text-text-secondary mt-0.5">
            <span className="material-symbols-outlined text-[18px] text-primary">hub</span>
          </div>
          <div className="flex flex-col min-w-0">
            <div className="flex flex-col xl:flex-row xl:items-baseline gap-x-3 gap-y-0.5">
              <h1 className="font-sans text-[20px] text-text-primary font-semibold tracking-tight">
                Network Topology
              </h1>
              <p className="font-sans text-[13px] text-text-secondary">
                Global influence and interaction network
              </p>
            </div>
          </div>
        </div>
      </section>

      <div className="grid gap-6 grid-cols-1 lg:grid-cols-12 flex-1 min-h-0">
        <section className="lg:col-span-8 bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] flex flex-col overflow-hidden">
          <div className="flex items-center justify-between px-6 py-4 border-b border-border-subtle bg-surface-header shrink-0">
            <h3 className="font-sans text-[14px] text-text-primary font-semibold">Interaction Graph</h3>
          </div>
          <div className="flex-1 min-h-[400px] flex items-center justify-center text-text-muted relative overflow-hidden bg-surface-secondary/20">
             <div className="z-10 text-center flex flex-col items-center gap-3">
               <EmptyState 
                 title="Network Visualization Unavailable" 
                 message="D3 network graph renderer is not initialized or insufficient nodes available." 
               />
             </div>
          </div>
        </section>

        <div className="lg:col-span-4 flex flex-col gap-6 overflow-y-auto pr-1">
          <section className="bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] flex flex-col overflow-hidden shrink-0">
            <div className="flex items-center justify-between px-6 py-4 border-b border-border-subtle bg-surface-header">
              <h3 className="font-sans text-[14px] text-text-primary font-semibold">Global Influencers</h3>
            </div>
            <div className="p-4">
              {loadingInfluencers && !influencers ? (
                <div className="text-center text-text-muted text-[13px] font-sans py-4">Loading influencers...</div>
              ) : (
                <div className="space-y-2">
                  {influencers?.slice(0, 10).map((inf, idx) => (
                    <div key={inf.user_id} className="flex items-center justify-between p-2.5 rounded hover:bg-surface-secondary/60 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="w-6 text-center font-mono text-[11px] text-text-muted">{idx + 1}</div>
                        <div className="font-medium text-[13px] font-sans text-text-primary">{inf.user_id}</div>
                      </div>
                      <div className="text-primary font-mono text-[12px]">{inf.pagerank.toFixed(3)}</div>
                    </div>
                  ))}
                  {(!influencers || influencers.length === 0) && (
                    <div className="text-text-muted text-[13px] font-sans py-4 text-center">No influencers detected.</div>
                  )}
                </div>
              )}
            </div>
          </section>

          <section className="bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] flex flex-col overflow-hidden shrink-0">
            <div className="flex items-center justify-between px-6 py-4 border-b border-border-subtle bg-surface-header">
              <h3 className="font-sans text-[14px] text-text-primary font-semibold">Major Communities</h3>
            </div>
            <div className="p-4">
              {loadingCommunities && !communities ? (
                <div className="text-center text-text-muted text-[13px] font-sans py-4">Loading communities...</div>
              ) : (
                <div className="space-y-3">
                  {communities?.map((com) => (
                    <div key={com.community_id} className="p-3.5 border border-border-subtle rounded-lg bg-surface-secondary/30 flex flex-col gap-2">
                      <div className="flex justify-between items-center">
                        <span className="font-sans font-semibold text-[13px] text-text-primary">Cluster {com.community_id}</span>
                        <span className="text-[11px] text-text-muted font-mono">{com.users_count} nodes</span>
                      </div>
                      <div className="text-[12px] text-text-secondary font-sans leading-relaxed truncate">
                        <span className="font-medium text-text-primary">Key nodes:</span> {com.top_influencers.slice(0, 3).map(inf => inf.user_id || inf).join(', ')}
                      </div>
                    </div>
                  ))}
                  {(!communities || communities.length === 0) && (
                    <div className="text-text-muted text-[13px] font-sans py-4 text-center">No communities detected.</div>
                  )}
                </div>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
