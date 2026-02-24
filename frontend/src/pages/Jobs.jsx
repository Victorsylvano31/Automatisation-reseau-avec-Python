// Jobs.jsx — Job management page
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Search } from 'lucide-react';
import { triggerBackup, getJobStatus } from '../api.js';

const STATUS_BADGE = {
    PENDING: 'badge-warning',
    RUNNING: 'badge-info',
    SUCCESS: 'badge-success',
    PARTIAL_SUCCESS: 'badge-warning',
    FAILED: 'badge-danger',
};

export default function Jobs() {
    const [jobs, setJobs] = useState([]);
    const [searchId, setSearchId] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    const handleBackup = async () => {
        setLoading(true);
        setMessage('');
        try {
            const res = await triggerBackup();
            setMessage(`✅ Job déclenché : ${res.job_id}`);
            // Refresh status right away
            const status = await getJobStatus(res.job_id);
            setJobs(prev => [status, ...prev]);
        } catch {
            setMessage('❌ Impossible de contacter l\'API. Vérifiez que FastAPI est lancé.');
        }
        setLoading(false);
    };

    const handleSearch = async () => {
        if (!searchId.trim()) return;
        try {
            const status = await getJobStatus(searchId.trim());
            setJobs(prev => {
                const exists = prev.find(j => j.job_id === status.job_id);
                return exists
                    ? prev.map(j => j.job_id === status.job_id ? status : j)
                    : [status, ...prev];
            });
        } catch {
            setMessage('❌ Job introuvable.');
        }
    };

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">Gestion des Jobs</h1>
                <p className="page-breadcrumb">Plateforme NRE · <span>Jobs d'automatisation</span></p>
            </div>

            {/* Actions bar */}
            <motion.div className="card" style={{ marginBottom: 24 }} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
                <div className="section-header" style={{ flexWrap: 'wrap', gap: 12 }}>
                    <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                        <div className="topbar-search" style={{ minWidth: 260 }}>
                            <Search size={14} color="var(--text-muted)" />
                            <input
                                placeholder="Rechercher un Job ID..."
                                value={searchId}
                                onChange={e => setSearchId(e.target.value)}
                                onKeyDown={e => e.key === 'Enter' && handleSearch()}
                            />
                        </div>
                        <button className="btn btn-ghost" onClick={handleSearch}>Rechercher</button>
                    </div>
                    <button className="btn btn-primary" onClick={handleBackup} disabled={loading}>
                        <Play size={14} />
                        {loading ? 'En cours...' : 'Nouveau Backup'}
                    </button>
                </div>
                {message && (
                    <div style={{
                        fontFamily: 'var(--font-mono)', fontSize: 13, marginTop: 12,
                        padding: '10px 14px', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)',
                        color: message.startsWith('✅') ? 'var(--accent-green)' : 'var(--accent-red)'
                    }}>
                        {message}
                    </div>
                )}
            </motion.div>

            {/* Jobs table */}
            <motion.div className="card" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.15 }}>
                <div className="section-title" style={{ marginBottom: 16 }}>Historique ({jobs.length})</div>
                {jobs.length === 0 ? (
                    <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text-muted)', fontSize: 14 }}>
                        Déclenchez un job pour voir l'historique ici.
                    </div>
                ) : (
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Job ID</th>
                                <th>Type</th>
                                <th>Statut</th>
                                <th>Démarré le</th>
                            </tr>
                        </thead>
                        <tbody>
                            {jobs.map(job => (
                                <motion.tr key={job.job_id} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}>
                                    <td style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{job.job_id}</td>
                                    <td><span className="badge badge-info">{job.type}</span></td>
                                    <td><span className={`badge ${STATUS_BADGE[job.status] || 'badge-muted'}`}>{job.status}</span></td>
                                    <td style={{ color: 'var(--text-secondary)', fontSize: 12 }}>
                                        {job.started_at ? new Date(job.started_at).toLocaleString('fr-FR') : '—'}
                                    </td>
                                </motion.tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </motion.div>
        </div>
    );
}
