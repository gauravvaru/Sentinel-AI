import * as React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export function Shell() {
  const [mobileOpen, setMobileOpen] = React.useState(false);

  return (
    <div className="bg-canvas-bg font-sans text-[13px] text-text-primary antialiased min-h-screen">
      <Sidebar mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />
      
      <div className="lg:pl-60 min-h-screen flex flex-col">
        <Header setMobileOpen={setMobileOpen} />
        
        <main className="w-full pt-14 px-4 sm:px-6 lg:px-8 py-6 bg-canvas-bg flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
