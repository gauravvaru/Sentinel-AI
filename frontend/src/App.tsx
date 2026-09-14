import * as React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Shell } from '@/components/layout/Shell';

// Pages
import { Overview } from '@/pages/Overview';
import { Network } from '@/pages/Network';
import { Audience } from '@/pages/Audience';
import { Inspector } from '@/pages/Inspector';
import { Search } from '@/pages/Search';
import { Influence } from '@/pages/Influence';
import { Propagation } from '@/pages/Propagation';
import { DataSources } from '@/pages/DataSources';
import { Settings } from '@/pages/Settings';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Shell />}>
          <Route path="/" element={<Overview />} />
          <Route path="/network" element={<Network />} />
          <Route path="/audience" element={<Audience />} />
          <Route path="/inspector" element={<Inspector />} />
          <Route path="/search" element={<Search />} />
          <Route path="/influence" element={<Influence />} />
          <Route path="/propagation" element={<Propagation />} />
          <Route path="/data-sources" element={<DataSources />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
