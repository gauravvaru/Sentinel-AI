import * as React from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';

const navigation = [
  { name: 'Overview', href: '/', icon: 'insights' },
  { name: 'Narratives', href: '/inspector', icon: 'forum' },
  { name: 'Audience', href: '/audience', icon: 'groups' },
  { name: 'Influence', href: '/influence', icon: 'troubleshoot' },
  { name: 'Propagation', href: '/propagation', icon: 'alt_route' },
  { name: 'Network', href: '/network', icon: 'hub' },
];

const operations = [
  { name: 'Data Sources', href: '/data-sources', icon: 'database' },
  { name: 'Search & Queries', href: '/search', icon: 'manage_search' },
  { name: 'Settings', href: '/settings', icon: 'tune' },
];

export function Sidebar({ mobileOpen, setMobileOpen }: { mobileOpen: boolean, setMobileOpen: (open: boolean) => void }) {
  const toggleMobile = () => setMobileOpen(!mobileOpen);

  return (
    <>
      {mobileOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}
      
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex w-60 flex-col justify-between bg-canvas-panel shadow-[0_1px_8px_rgba(0,0,0,0.04)] transition-transform duration-200 ease-in-out py-6 lg:translate-x-0',
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-2 px-6 py-1">
            <div className="w-8 h-8 rounded-lg bg-surface-elevated flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-[18px] text-primary">bolt</span>
            </div>
            <div className="flex flex-col leading-none">
              <span className="font-sans font-semibold text-[15px] text-text-primary tracking-tight">SentinelAI</span>
              <span className="font-mono text-[11px] text-text-muted mt-1 tracking-wider uppercase">Telemetry V2</span>
            </div>
          </div>
          
          <div className="px-6 pt-2">
            <span className="font-mono text-[11px] text-text-muted uppercase tracking-wider px-2">Core Intelligence</span>
          </div>
          
          <nav className="flex flex-col gap-1 px-4">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-4 py-2 rounded-lg font-sans text-[15px] font-medium transition-all',
                    isActive
                      ? 'bg-canvas-elevated text-text-primary shadow-[0_1px_3px_rgba(20,30,40,0.06)]'
                      : 'text-text-secondary hover:bg-canvas-elevated hover:text-text-primary'
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    <span className={cn("material-symbols-outlined text-[18px]", isActive && "text-primary")}>{item.icon}</span>
                    <span className="flex-1">{item.name}</span>
                    {isActive && <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>}
                  </>
                )}
              </NavLink>
            ))}
          </nav>

          <div className="px-6 pt-4">
            <span className="font-mono text-[11px] text-text-muted uppercase tracking-wider px-2">Operations</span>
          </div>
          <nav className="flex flex-col gap-1 px-4">
            {operations.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-4 py-2 rounded-lg font-sans text-[15px] font-medium transition-all',
                    isActive
                      ? 'bg-canvas-elevated text-text-primary shadow-[0_1px_3px_rgba(20,30,40,0.06)]'
                      : 'text-text-secondary hover:bg-canvas-elevated hover:text-text-primary'
                  )
                }
              >
                <span className="material-symbols-outlined text-[18px]">{item.icon}</span>
                <span className="flex-1">{item.name}</span>
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="px-6 flex flex-col gap-3 pt-6 pb-6">
          {/* Optional: Future area for user profile or global settings */}
        </div>
      </aside>
    </>
  );
}
