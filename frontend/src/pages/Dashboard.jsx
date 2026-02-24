// Dashboard.jsx — Overview page with stats and activity
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Server, Briefcase, CheckCircle, XCircle, Play } from 'lucide-react';
import { getDevices, getHealth, triggerBackup } from '../api.js';

const FADE_UP = {
    hidden: { opacity: 0, y: 16 },
    visible: (i) => ({ opacity: 1, y: 0, transition: { delay: i * 0.08, duration: 0.4, ease: 'easeOut' } }),
};

function StatCard({ icon: Icon, label, value, color, index }) {
    return (
        <motion.div className="card" variants={FADE_UP} custom={index} initial="hidden" animate="visible">
            <div className="card-title">
                <Icon size={14} style={{ color }} />
                {label}
            </div>
            <div className="stat-value" style={{ color }}>{value}</div>
        </motion.div>
    );
}

export default function Dashboard({ onNavigate }) {
    const [devices, setDevices] = useState([]);
    const [apiStatus, setApiStatus] = useState('checking');
    const [lastJob, setLastJob] = useState(null);
    const [launching, setLaunching] = useState(false);

    useEffect(() => {
        getHealth()
            .then(() => setApiStatus('online'))
            .catch(() => setApiStatus('offline'));
        getDevices().then(setDevices).catch(() => { });
    }, []);

    const handleQuickBackup = async () => {
        setLaunching(true);
        try {
            const res = await triggerBackup();
            setLastJob(res);
        } catch (e) {
            setLastJob({ error: 'API unreachable' });
        }
        setLaunching(false);
    };

    const onlineDevices = devices.filter(d => d.is_online).length;

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">Tableau de Bord</h1>
                <p className="page-breadcrumb">Plateforme NRE · <span>Vue d'ensemble</span></p>
            </div>

            {/* Stats row */}
            <div className="stats-grid">
                <StatCard index={0} icon={Server} label="Équipements" value={devices.length || 0} color="var(--accent-blue)" />
                <StatCard index={1} icon={CheckCircle} label="En Ligne" value={onlineDevices} color="var(--accent-green)" />
                <StatCard index={2} icon={XCircle} label="Hors Ligne" value={devices.length - onlineDevices || 0} color="var(--accent-red)" />
                <StatCard index={3} icon={Briefcase} label="API Status" value={apiStatus === 'online' ? '✓ OK' : '✗ Offline'} color={apiStatus === 'online' ? 'var(--accent-green)' : 'var(--accent-red)'} />
            </div>

            {/* Quick action */}
            <motion.div className="card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
                <div className="section-header">
                    <div>
                        <div className="section-title">Action rapide</div>
                        <div className="section-subtitle">Déclenche une opération sur tout le parc réseau</div>
                    </div>
                    <button className="btn btn-primary" onClick={handleQuickBackup} disabled={launching}>
                        <Play size={14} />
                        {launching ? 'Lancement...' : 'Backup de Flotte'}
                    </button>
                </div>

                {lastJob && (
                    <div style={{ marginTop: 16, padding: '12px 16px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', fontFamily: 'var(--font-mono)', fontSize: 13 }}>
                        {lastJob.error
                            ? <span style={{ color: 'var(--accent-red)' }}>❌ {lastJob.error}</span>
                            : <>✔ Job créé · <span style={{ color: 'var(--accent-blue)' }}>{lastJob.job_id}</span></>
                        }
                    </div>
                )}
            </motion.div>

            {/* Device quick view */}
            {devices.length > 0 && (
                <motion.div className="card" style={{ marginTop: 24 }} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
                    <div className="section-header">
                        <div className="section-title">Équipements ({devices.length})</div>
                        <button className="btn btn-ghost" onClick={() => onNavigate('devices')}>Voir tout →</button>
                    </div>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Hostname</th>
                                <th>Statut</th>
                                <th>Dernier Backup</th>
                            </tr>
                        </thead>
                        <tbody>
                            {devices.slice(0, 5).map(d => (
                                <tr key={d.hostname}>
                                    <td>{d.hostname}</td>
                                    <td><span className={`badge ${d.is_online ? 'badge-success' : 'badge-danger'}`}>{d.is_online ? 'UP' : 'DOWN'}</span></td>
                                    <td className="tag">{d.last_backup_date ? new Date(d.last_backup_date).toLocaleString('fr-FR') : '—'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </motion.div>
            )}
        </div>
    );
}
