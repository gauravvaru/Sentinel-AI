import * as React from 'react';
import { cn } from '@/lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'primary' | 'danger' | 'warning' | 'success';
}

function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        'inline-flex items-center rounded-full px-2 py-0.5 font-mono text-[11px] tracking-wider uppercase',
        {
          'bg-surface-secondary text-text-secondary': variant === 'default',
          'bg-primary/10 text-primary': variant === 'primary',
          'bg-status-escalated-bg text-status-escalated-text': variant === 'danger',
          'bg-status-derived-bg text-status-derived-text': variant === 'warning',
          'bg-status-observed-bg text-status-observed-text': variant === 'success',
        },
        className
      )}
      {...props}
    />
  );
}

export { Badge };
