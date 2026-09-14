import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-canvas-bg disabled:opacity-50 disabled:pointer-events-none cursor-pointer',
          {
            'bg-primary text-on-primary hover:bg-primary/90': variant === 'primary',
            'bg-surface-secondary text-text-primary hover:bg-surface-header': variant === 'secondary',
            'bg-status-escalated-bg text-status-escalated-text hover:bg-status-escalated-bg/80': variant === 'danger',
            'bg-transparent text-text-secondary hover:text-text-primary hover:bg-surface-secondary': variant === 'ghost',
            'h-8 px-3 text-[12px]': size === 'sm',
            'h-9 px-4 text-[13px] gap-1.5': size === 'md',
            'h-11 px-6 text-[15px]': size === 'lg',
          },
          className
        )}
        {...props}
      />
    );
  }
);
Button.displayName = 'Button';

export { Button };
