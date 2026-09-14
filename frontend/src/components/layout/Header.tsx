import * as React from 'react';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { useNavigate } from 'react-router-dom';

export function Header({ setMobileOpen }: { setMobileOpen: (open: boolean) => void }) {
  const navigate = useNavigate();
  return (
    <header className="fixed top-0 left-0 lg:left-60 right-0 h-14 bg-surface-primary/95 backdrop-blur-md shadow-[0_1px_8px_rgba(0,0,0,0.04)] z-40 px-6 flex items-center justify-between">
      <div className="flex items-center gap-4 flex-1 max-w-2xl">
        <Button
          variant="ghost"
          className="-ml-3 p-2 text-text-secondary lg:hidden"
          onClick={() => setMobileOpen(true)}
        >
          <span className="sr-only">Open sidebar</span>
          <Menu className="h-6 w-6" aria-hidden="true" />
        </Button>

        <div className="relative w-full flex items-center hidden sm:flex">
          <span className="material-symbols-outlined absolute left-4 text-text-muted text-[18px]">search</span>
          <button 
            onClick={() => navigate('/search')}
            className="w-full h-9 pl-10 pr-12 bg-surface-secondary rounded-lg font-sans text-[12px] text-text-muted text-left outline-none hover:bg-surface-elevated transition-all flex items-center" 
          >
            Search conversations, emerging narratives, accounts...
          </button>
          <div className="absolute right-3 flex items-center pointer-events-none">
            <kbd className="font-mono text-[11px] px-1.5 py-0.5 bg-surface-primary text-text-muted rounded shadow-[0_1px_2px_rgba(0,0,0,0.05)]">⌘K</kbd>
          </div>
        </div>

        <div className="hidden xl:flex items-center gap-2">
          <div className="flex items-center gap-2 px-3 py-1 bg-surface-secondary rounded-lg text-text-secondary cursor-default">
            <span className="font-mono text-[11px] uppercase text-text-muted">Scope:</span>
            <span className="font-sans text-[12px] font-medium text-text-primary">Global Public</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 bg-surface-secondary rounded-lg text-text-secondary cursor-default">
            <span className="font-sans text-[12px] font-medium text-text-primary">Last 7 Days</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden sm:inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-secondary text-text-secondary font-mono text-[11px]">
          <span className="material-symbols-outlined text-[14px]">history</span>
          TELEMETRY: 24H
        </div>
      </div>
    </header>
  );
}
