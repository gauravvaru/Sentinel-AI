import * as React from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { usePolling } from '@/hooks/usePolling';
import { api } from '@/api/client';
import { LoadingState, ErrorState, EmptyState } from '@/components/ui/State';

export function Propagation() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const topicIdParam = searchParams.get('topicId');
  const topicId = topicIdParam ? parseInt(topicIdParam, 10) : null;

  const { data: timeline, isLoading, error } = usePolling({
    fetcher: () => topicId ? api.getPropagationTimeline(topicId) : Promise.resolve([]),
    intervalMs: 30000,
    enabled: !!topicId
  });

  return (
    <div className="flex flex-col w-full h-full min-h-0 gap-6">
      {/* Header Banner */}
      <section className="w-full bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] px-6 lg:px-8 py-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-5 shrink-0">
        <div className="flex items-start gap-4 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-surface-secondary flex items-center justify-center shrink-0 text-text-secondary mt-0.5">
            <span className="material-symbols-outlined text-[18px] text-primary">alt_route</span>
          </div>
          <div className="flex flex-col min-w-0">
            <div className="flex flex-col xl:flex-row xl:items-baseline gap-x-3 gap-y-0.5">
              <h1 className="font-sans text-[20px] text-text-primary font-semibold tracking-tight">
                Event Propagation
              </h1>
              <p className="font-sans text-[13px] text-text-secondary">
                Chronological timeline of narrative spread
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] flex-1 overflow-hidden flex flex-col">
        {!topicId ? (
          <div className="flex flex-col items-center justify-center flex-1">
            <EmptyState 
              title="No Topic Selected" 
              message="Select an emerging narrative to view its propagation timeline." 
            />
            <button 
              onClick={() => navigate('/inspector')}
              className="mt-4 px-4 py-2 bg-primary text-on-primary rounded-lg font-sans text-[13px] font-medium"
            >
              Go to Narratives
            </button>
          </div>
        ) : isLoading && !timeline ? (
          <LoadingState message="Loading propagation timeline..." />
        ) : error ? (
          <ErrorState message="Failed to load propagation timeline. Check API connectivity." />
        ) : !timeline || timeline.length === 0 ? (
          <EmptyState title="Insufficient Signal" message="No propagation events detected for this topic." />
        ) : (
          <div className="w-full overflow-y-auto p-6">
            <div className="relative border-l-2 border-border-strong ml-4 space-y-8 pb-8">
              {timeline.map((event, idx) => (
                <div key={event.event_id} className="relative pl-6">
                  <div className="absolute -left-[9px] top-1.5 w-4 h-4 rounded-full bg-primary border-4 border-surface-primary" />
                  <div className="bg-surface-secondary/30 border border-border-subtle rounded-xl p-4 flex flex-col gap-2">
                    <div className="flex items-start justify-between gap-4 flex-wrap">
                      <div className="flex items-center gap-2 font-mono text-[11px] text-text-muted">
                        <span className="uppercase tracking-wider">{event.platform}</span>
                        <span>•</span>
                        <span>{event.event_type.toUpperCase()}</span>
                        {event.event_time && (
                          <>
                            <span>•</span>
                            <span>{new Date(event.event_time).toLocaleString()}</span>
                          </>
                        )}
                      </div>
                      <div className="font-mono text-[11px] text-text-muted">
                        User: <span className="text-text-primary font-medium">{event.user_id}</span>
                      </div>
                    </div>
                    
                    <p className="font-sans text-[13px] text-text-primary leading-relaxed mt-1">
                      {event.text}
                    </p>
                    
                    {event.mentions && event.mentions.length > 0 && (
                      <div className="flex items-center gap-2 mt-2">
                        <span className="material-symbols-outlined text-[14px] text-text-muted">alternate_email</span>
                        <div className="flex flex-wrap gap-1">
                          {event.mentions.map((m, i) => (
                            <span key={i} className="text-[11px] font-mono text-primary bg-primary/10 px-1.5 py-0.5 rounded">@{m}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
