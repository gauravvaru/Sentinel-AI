import * as React from 'react';
import { ComingSoonState } from '@/components/ui/State';

export function Settings() {
  return (
    <div className="flex flex-col w-full h-full min-h-0 gap-6">
      <section className="w-full bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] px-6 lg:px-8 py-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-5 shrink-0">
        <div className="flex items-start gap-4 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-surface-secondary flex items-center justify-center shrink-0 text-text-secondary mt-0.5">
            <span className="material-symbols-outlined text-[18px] text-primary">tune</span>
          </div>
          <div className="flex flex-col min-w-0">
            <div className="flex flex-col xl:flex-row xl:items-baseline gap-x-3 gap-y-0.5">
              <h1 className="font-sans text-[20px] text-text-primary font-semibold tracking-tight">
                Settings
              </h1>
              <p className="font-sans text-[13px] text-text-secondary">
                Global application preferences
              </p>
            </div>
          </div>
        </div>
      </section>
      
      <section className="bg-surface-primary rounded-xl shadow-[0_2px_8px_rgba(20,30,40,0.04),0_8px_24px_rgba(20,30,40,0.05)] flex-1 overflow-hidden flex flex-col">
        <ComingSoonState 
          title="Settings Configuration Unavailable" 
          message="User preferences are currently handled through environmental configuration. Dashboard controls will be available in a future release."
        />
      </section>
    </div>
  );
}
