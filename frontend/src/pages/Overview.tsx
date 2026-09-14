import * as React from 'react';
import { Panel } from '@/components/ui/Panel';
import { Badge } from '@/components/ui/Badge';
import { usePolling } from '@/hooks/usePolling';
import { api } from '@/api/client';
import { LoadingState, ErrorState, EmptyState } from '@/components/ui/State';
import { useNavigate } from 'react-router-dom';

export function Overview() {
  const navigate = useNavigate();
  const { data: insights, isLoading: loadingInsights, error: errorInsights } = usePolling({
    fetcher: () => api.getInsights(24),
    intervalMs: 30000
  });

  const { data: trending, isLoading: loadingTrending } = usePolling({
    fetcher: () => api.getTrendingTopics(24, 10),
    intervalMs: 30000
  });

  if (loadingInsights && !insights) {
    return <LoadingState message="Loading telemetry..." />;
  }

  if (errorInsights) {
    return <ErrorState message="Failed to load system insights. Verify connection to the ingestion pipeline." />;
  }

  return (
    <div className="flex flex-col w-full gap-6">
      {/* Intelligence Brief Banner */}
      <section className="w-full bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] px-6 lg:px-8 py-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-5">
        <div className="flex items-start gap-4 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-surface-secondary flex items-center justify-center shrink-0 text-text-secondary mt-0.5">
            <span className="material-symbols-outlined text-[18px] text-primary">bolt</span>
          </div>
          <div className="flex flex-col min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-mono text-[11px] text-text-muted uppercase tracking-wider font-semibold">INTELLIGENCE BRIEF</span>
              <Badge variant="warning">DERIVED</Badge>
              <span className="font-mono text-[11px] text-text-muted">• Updated just now · Realtime Stream</span>
            </div>
            <div className="flex flex-col xl:flex-row xl:items-baseline gap-x-3 gap-y-0.5 mt-0.5">
              <h2 className="font-sans text-[15px] text-text-primary font-semibold tracking-tight">
                {insights?.headline || "Monitoring influence networks"}
              </h2>
              <p className="font-sans text-[13px] text-text-secondary line-clamp-1 xl:line-clamp-none">
                {insights?.summary || "Analyzing node signatures and emerging narratives."}
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3 shrink-0 self-end md:self-center">
          <button className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-surface-secondary hover:bg-surface-elevated text-text-primary font-sans text-[13px] transition-colors cursor-pointer" type="button">
            <span>Explore Evidence</span>
            <span className="material-symbols-outlined text-[16px] text-primary">arrow_forward</span>
          </button>
        </div>
      </section>

      {/* KPI Strip */}
      <section className="w-full bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] p-5 grid grid-cols-2 sm:grid-cols-4 xl:grid-cols-4 divide-y sm:divide-y-0 sm:divide-x divide-border-subtle gap-y-4">
        <div className="flex flex-col px-4 xl:px-6">
          <span className="font-mono text-[11px] text-text-muted uppercase tracking-wider">Nodes Tracked</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="font-mono text-[22px] font-semibold text-text-primary tracking-tight">{insights?.evidence.network.node_count?.toLocaleString() || 0}</span>
          </div>
          <span className="font-sans text-[12px] text-text-muted mt-0.5">Telemetry window 24h</span>
        </div>
        
        <div className="flex flex-col px-4 xl:px-6">
          <span className="font-mono text-[11px] text-text-muted uppercase tracking-wider">Active Communities</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="font-mono text-[22px] font-semibold text-text-primary tracking-tight">{insights?.evidence.network.community_count?.toLocaleString() || 0}</span>
          </div>
          <span className="font-sans text-[12px] text-text-muted mt-0.5">Unique clusters</span>
        </div>
        
        <div className="flex flex-col px-4 xl:px-6">
          <span className="font-mono text-[11px] text-text-muted uppercase tracking-wider">Emerging Narratives</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="font-mono text-[22px] font-semibold text-text-primary tracking-tight">{insights?.evidence.trends.trending_topics_count || 0}</span>
          </div>
          <span className="font-sans text-[12px] text-text-muted mt-0.5">Above velocity limit</span>
        </div>
        
        <div className="flex flex-col px-4 xl:px-6">
          <span className="font-mono text-[11px] text-text-muted uppercase tracking-wider">Data Quality</span>
          <div className="flex items-baseline gap-2 mt-1">
            <Badge variant={insights?.data_quality === 'high' ? 'success' : 'warning'}>
              {insights?.data_quality || 'UNKNOWN'}
            </Badge>
          </div>
          <span className="font-sans text-[12px] text-text-muted mt-0.5">Ingestion state</span>
        </div>
      </section>

      {/* Main Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        {/* Left Main Column */}
        <div className="xl:col-span-8 flex flex-col gap-6 min-w-0">
          
          <Panel title="Conversation Trends" className="min-h-[300px]">
             {/* Chart placeholder */}
             <div className="flex h-full min-h-[200px] items-center justify-center text-text-muted font-sans text-[13px]">
               <EmptyState 
                 title="Insufficient Historical Signal" 
                 message="Not enough continuous data points to generate conversation trends visualization." 
               />
             </div>
          </Panel>

          <section className="bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] flex flex-col overflow-hidden">
            <div className="flex items-center justify-between px-6 py-3 border-b border-border-subtle bg-surface-header flex-wrap gap-4">
              <div className="flex items-center gap-6">
                <button className="font-sans text-[13px] text-text-primary font-semibold relative py-1 after:content-[''] after:absolute after:-bottom-[13px] after:left-0 after:right-0 after:h-0.5 after:bg-primary">
                  Emerging Narratives
                </button>
              </div>
            </div>
            <div className="w-full overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-surface-header/60 text-text-muted font-mono text-[11px] uppercase tracking-wider">
                    <th className="py-3 px-6 font-semibold">Narrative / Topic Cluster</th>
                    <th className="py-3 px-6 font-semibold">Score</th>
                    <th className="py-3 px-6 font-semibold">Keywords</th>
                    <th className="py-3 px-6 font-semibold text-right">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-subtle font-sans text-[13px]">
                  {loadingTrending && !trending ? (
                    <tr>
                      <td colSpan={4} className="py-8 text-center text-text-muted">Loading trends...</td>
                    </tr>
                  ) : !trending?.trending || trending.trending.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="py-12">
                        <EmptyState title="No Emerging Narratives" message="No topics have breached the narrative velocity threshold." />
                      </td>
                    </tr>
                  ) : trending.trending.map((topic) => (
                    <tr 
                      key={topic.topic_id} 
                      className="hover:bg-surface-secondary/60 transition-colors group cursor-pointer"
                      onClick={() => navigate(`/inspector?topicId=${topic.topic_id}`)}
                    >
                      <td className="py-3 px-6 text-text-primary font-medium">
                        {topic.name}
                      </td>
                      <td className="py-3 px-6 whitespace-nowrap">
                        <Badge variant="primary">{topic.trend_score.toFixed(2)}</Badge>
                      </td>
                      <td className="py-3 px-6">
                        <div className="flex flex-wrap gap-2">
                          {topic.keywords.slice(0, 3).map((kw, i) => (
                            <span key={i} className="text-text-secondary bg-surface-secondary px-2 py-0.5 rounded font-mono text-[11px]">{kw}</span>
                          ))}
                        </div>
                      </td>
                      <td className="py-3 px-6 text-right text-text-muted group-hover:text-text-primary">
                        <span className="material-symbols-outlined text-[18px]">expand_more</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

        </div>

        {/* Right Intelligence Rail */}
        <div className="xl:col-span-4 flex flex-col gap-6 min-w-0">
          <Panel title="Executive Summary">
            <div className="prose prose-sm text-text-secondary font-sans text-[13px]">
              <p>{insights?.summary}</p>
              {insights?.key_findings && insights.key_findings.length > 0 && (
                <>
                  <h4 className="text-text-primary font-mono text-[11px] mt-6 mb-3 uppercase tracking-wider">Key Findings</h4>
                  <ul className="space-y-3">
                    {insights.key_findings.map((finding, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="material-symbols-outlined text-primary text-[16px] shrink-0 mt-0.5">check_circle</span>
                        <span>{finding}</span>
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          </Panel>
        </div>
      </div>
    </div>
  );
}
