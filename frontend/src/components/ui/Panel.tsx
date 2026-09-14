import * as React from 'react';
import { cn } from '@/lib/utils';

export interface PanelProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'title'> {
  title?: React.ReactNode;
  headerAction?: React.ReactNode;
}

const Panel = React.forwardRef<HTMLDivElement, PanelProps>(
  ({ className, title, headerAction, children, ...props }, ref) => {
    return (
      <section
        ref={ref}
        className={cn('flex flex-col bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] overflow-hidden', className)}
        {...props}
      >
        {(title || headerAction) && (
          <div className="flex items-center justify-between px-6 py-4 border-b border-border-subtle bg-surface-primary">
            {title && (
              <h3 className="font-sans text-[15px] font-semibold text-text-primary tracking-tight">
                {title}
              </h3>
            )}
            {headerAction && <div>{headerAction}</div>}
          </div>
        )}
        <div className="flex-1 overflow-auto p-6">
          {children}
        </div>
      </section>
    );
  }
);
Panel.displayName = 'Panel';

export { Panel };
