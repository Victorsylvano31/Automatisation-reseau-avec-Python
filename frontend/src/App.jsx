// App.jsx — Application root: routing between pages
import { useState } from 'react';
import Sidebar from './components/Sidebar.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Devices from './pages/Devices.jsx';
import Jobs from './pages/Jobs.jsx';
import './index.css';

const PAGES = {
  dashboard: Dashboard,
  devices: Devices,
  jobs: Jobs,
};

export default function App() {
  const [page, setPage] = useState('dashboard');
  const Page = PAGES[page] || Dashboard;

  return (
    <div className="app-shell">
      {/* Left column: sidebar nav */}
      <Sidebar active={page} onNavigate={setPage} />

      {/* Right column: page content */}
      <main className="main-content">
        <Page onNavigate={setPage} />
      </main>
    </div>
  );
}
