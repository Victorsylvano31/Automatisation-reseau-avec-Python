// Sidebar.jsx — Left navigation panel
import { Network, Server, Briefcase, Activity, Settings, Zap } from 'lucide-react';

const NAV = [
    { icon: Activity, label: 'Dashboard', id: 'dashboard' },
    { icon: Server, label: 'Équipements', id: 'devices' },
    { icon: Briefcase, label: 'Jobs', id: 'jobs' },
];

export default function Sidebar({ active, onNavigate }) {
    return (
        <aside className="sidebar">
            {/* Logo */}
            <div className="sidebar-logo">
                <div className="sidebar-logo-icon">
                    <Zap size={18} color="#fff" />
                </div>
                <div>
                    <h2>NRE Platform</h2>
                    <p>v2.0 · Network Engine</p>
                </div>
            </div>

            {/* Navigation */}
            <span className="nav-label">Navigation</span>
            {NAV.map(({ icon: Icon, label, id }) => (
                <button
                    key={id}
                    className={`nav-item ${active === id ? 'active' : ''}`}
                    onClick={() => onNavigate(id)}
                >
                    <Icon size={16} />
                    {label}
                </button>
            ))}

            {/* Footer: API Status */}
            <div className="sidebar-footer">
                <div className="status-indicator">
                    <span className="status-dot" />
                    API FastAPI: <strong style={{ color: 'var(--accent-green)', marginLeft: 4 }}>Online</strong>
                </div>
            </div>
        </aside>
    );
}
