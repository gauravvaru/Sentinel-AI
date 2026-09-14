import * as React from 'react';
import { cn } from '@/lib/utils';

export function LoadingState({ message = 'Loading...', className }: { message?: string; className?: string }) {
  return (
    <div className={cn("flex flex-col items-center justify-center p-12 min-h-[300px] h-full w-full", className)}>
      <div className="w-12 h-12 rounded-full border-[3px] border-surface-secondary border-t-primary animate-spin mb-4" />
      <div className="font-sans text-[14px] font-medium text-text-primary">{message}</div>
    </div>
  );
}

export function ErrorState({ message = 'An error occurred.', className }: { message?: string; className?: string }) {
  return (
    <div className={cn("flex flex-col items-center justify-center p-12 min-h-[300px] h-full w-full", className)}>
      <div className="w-12 h-12 rounded-full bg-threat/10 flex items-center justify-center mb-4">
        <span className="material-symbols-outlined text-[24px] text-threat">error</span>
      </div>
      <div className="font-sans text-[15px] font-semibold text-text-primary mb-1">Unable to load data</div>
      <div className="font-sans text-[13px] text-text-secondary text-center max-w-sm">{message}</div>
    </div>
  );
}

export function EmptyState({ title = 'Insufficient Signal', message = 'No data available.', className }: { title?: string; message?: string; className?: string }) {
  return (
    <div className={cn("flex flex-col items-center justify-center p-12 min-h-[200px] h-full w-full", className)}>
      <div className="w-12 h-12 rounded-full bg-surface-secondary flex items-center justify-center mb-4">
        <span className="material-symbols-outlined text-[24px] text-text-muted">info</span>
      </div>
      <div className="font-sans text-[15px] font-semibold text-text-primary mb-1">{title}</div>
      <div className="font-sans text-[13px] text-text-secondary text-center max-w-sm">{message}</div>
    </div>
  );
}

export function ComingSoonState({ title = 'Coming Soon', message = 'This feature is currently under development.', className }: { title?: string; message?: string; className?: string }) {
  return (
    <div className={cn("flex flex-col items-center justify-center p-12 min-h-[300px] h-full w-full", className)}>
      <div className="w-12 h-12 rounded-full bg-surface-secondary flex items-center justify-center mb-4">
        <span className="material-symbols-outlined text-[24px] text-text-muted">construction</span>
      </div>
      <div className="font-sans text-[15px] font-semibold text-text-primary mb-1">{title}</div>
      <div className="font-sans text-[13px] text-text-secondary text-center max-w-sm">{message}</div>
    </div>
  );
}
