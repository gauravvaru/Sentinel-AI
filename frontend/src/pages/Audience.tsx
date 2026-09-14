import * as React from 'react';
import { Panel } from '@/components/ui/Panel';
import { Badge } from '@/components/ui/Badge';
import { usePolling } from '@/hooks/usePolling';
import { api } from '@/api/client';
import { LoadingState, ErrorState, EmptyState } from '@/components/ui/State';

export function Audience() {
  const { data: audience, isLoading, error } = usePolling({
    fetcher: () => api.getAudienceCohorts(undefined, 1000),
    intervalMs: 30000
  });

  if (isLoading && !audience) {
    return <LoadingState message="Loading audience clusters..." />;
  }

  if (error) {
    return <ErrorState message="Failed to load audience cohorts. Verify connection to the ingestion pipeline." />;
  }

  return (
    <div className="flex flex-col w-full gap-6">
      {/* Header Banner */}
      <section className="w-full bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] px-6 lg:px-8 py-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-5">
        <div className="flex items-start gap-4 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-surface-secondary flex items-center justify-center shrink-0 text-text-secondary mt-0.5">
            <span className="material-symbols-outlined text-[18px] text-primary">groups</span>
          </div>
          <div className="flex flex-col min-w-0">
            <div className="flex flex-col xl:flex-row xl:items-baseline gap-x-3 gap-y-0.5">
              <h1 className="font-sans text-[20px] text-text-primary font-semibold tracking-tight">
                Audience Clustering
              </h1>
              <p className="font-sans text-[13px] text-text-secondary">
                Behavioral segmentation of network participants
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* KPI Strip */}
      <section className="w-full bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] p-5 grid grid-cols-1 sm:grid-cols-3 divide-y sm:divide-y-0 sm:divide-x divide-border-subtle gap-y-4">
        <div className="flex flex-col px-4 xl:px-6">
          <span className="font-mono text-[11px] text-text-muted uppercase tracking-wider">Total Users</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="font-mono text-[22px] font-semibold text-text-primary tracking-tight">
              {audience?.total_users?.toLocaleString() || 0}
            </span>
          </div>
          <span className="font-sans text-[12px] text-text-muted mt-0.5">Observed in window</span>
        </div>
        
        <div className="flex flex-col px-4 xl:px-6">
          <span className="font-mono text-[11px] text-text-muted uppercase tracking-wider">Usable for Clustering</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="font-mono text-[22px] font-semibold text-text-primary tracking-tight text-nominal">
              {audience?.usable_users?.toLocaleString() || 0}
            </span>
          </div>
          <span className="font-sans text-[12px] text-text-muted mt-0.5">Sufficient behavioral data</span>
        </div>
        
        <div className="flex flex-col px-4 xl:px-6">
          <span className="font-mono text-[11px] text-text-muted uppercase tracking-wider">Insufficient Data</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="font-mono text-[22px] font-semibold text-text-primary tracking-tight text-warning">
              {audience?.insufficient_data_users?.toLocaleString() || 0}
            </span>
          </div>
          <span className="font-sans text-[12px] text-text-muted mt-0.5">Excluded from cohorts</span>
        </div>
      </section>

      {/* Main Grid */}
      <div className="grid gap-6 grid-cols-1 xl:grid-cols-2 items-start">
        <section className="bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] flex flex-col overflow-hidden min-h-[500px]">
          <div className="flex items-center justify-between px-6 py-4 border-b border-border-subtle bg-surface-header">
            <h3 className="font-sans text-[14px] text-text-primary font-semibold">Identified Cohorts</h3>
          </div>
          <div className="p-6 overflow-y-auto">
            <div className="space-y-4">
              {audience?.cohorts?.map((cohort) => (
                <div key={cohort.cohort_id} className="p-5 bg-surface-secondary/30 border border-border-subtle rounded-xl flex flex-col gap-4">
                  <div className="flex justify-between items-start">
                    <div className="flex flex-col gap-1">
                      <h4 className="font-sans font-semibold text-[15px] text-text-primary">{cohort.label}</h4>
                      <div className="text-[11px] text-text-muted font-mono uppercase tracking-wider">ID: {cohort.cohort_id}</div>
                    </div>
                    <Badge variant={cohort.confidence > 0.7 ? 'success' : 'warning'}>
                      Conf: {(cohort.confidence * 100).toFixed(1)}%
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-y-4 gap-x-6 pt-4 border-t border-border-subtle/50">
                    <div className="flex flex-col gap-1">
                      <div className="text-[11px] text-text-muted uppercase font-mono tracking-wider">User Count</div>
                      <div className="font-sans font-medium text-[13px] text-text-primary">{cohort.user_count?.toLocaleString()}</div>
                    </div>
                    <div className="flex flex-col gap-1">
                      <div className="text-[11px] text-text-muted uppercase font-mono tracking-wider">Total Events</div>
                      <div className="font-sans font-medium text-[13px] text-text-primary">{cohort.total_events?.toLocaleString()}</div>
                    </div>
                    <div className="flex flex-col gap-1">
                      <div className="text-[11px] text-text-muted uppercase font-mono tracking-wider">Avg Engagement</div>
                      <div className="font-sans font-medium text-[13px] text-text-primary">{cohort.average_engagement.toFixed(2)}</div>
                    </div>
                    <div className="flex flex-col gap-1">
                      <div className="text-[11px] text-text-muted uppercase font-mono tracking-wider">Demographics</div>
                      <div className="font-sans font-medium text-[13px] text-text-primary line-clamp-1">{cohort.demographics}</div>
                    </div>
                  </div>
                </div>
              ))}
              {(!audience?.cohorts || audience.cohorts.length === 0) && (
                <div className="text-text-muted text-[13px] font-sans text-center py-12">
                  Not enough usable data to identify meaningful cohorts.
                </div>
              )}
            </div>
          </div>
        </section>
        
        <section className="bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] flex flex-col overflow-hidden min-h-[500px]">
          <div className="flex items-center justify-between px-6 py-4 border-b border-border-subtle bg-surface-header">
            <h3 className="font-sans text-[14px] text-text-primary font-semibold">Cohort Distribution</h3>
          </div>
          <div className="flex-1 flex flex-col items-center justify-center text-text-muted gap-6 p-6">
            <EmptyState 
              title="Distribution Visualization Unavailable" 
              message="Insufficient distinct cohort segments to generate distribution visualization." 
            />
          </div>
        </section>
      </div>
    </div>
  );
}
