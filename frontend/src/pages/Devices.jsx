// Devices.jsx — Full network inventory page
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw } from 'lucide-react';
import { getDevices } from '../api.js';

export default function Devices() {
    const [devices, setDevices] = useState([]);
    const [loading, setLoading] = useState(true);

    const load = () => {
        setLoading(true);
        getDevices()
            .then(setDevices)
            .catch(() => setDevices([]))
            .finally(() => setLoading(false));
    };

    useEffect(() => { load(); }, []);

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">Inventaire Réseau</h1>
                <p className="page-breadcrumb">Plateforme NRE · <span>Équipements</span></p>
            </div>

            <motion.div className="card" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
                <div className="section-header">
                    <div>
                        <div className="section-title">{devices.length} équipement(s)</div>
                        <div className="section-subtitle">État synchronisé depuis le cache interne</div>
                    </div>
                    <button className="btn btn-ghost" onClick={load}>
                        <RefreshCw size={14} />
                        Actualiser
                    </button>
                </div>

                {loading ? (
                    <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text-muted)' }}>Chargement...</div>
                ) : devices.length === 0 ? (
                    <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
                        <p>Aucun équipement en base de données.</p>
                        <p style={{ fontSize: 13, marginTop: 8 }}>Déclenchez un job de collecte pour peupler l'inventaire.</p>
                    </div>
                ) : (
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Hostname</th>
                                <th>Statut</th>
                                <th>Version OS</th>
                                <th>Dernier Backup</th>
                            </tr>
                        </thead>
                        <tbody>
                            {devices.map(d => (
                                <motion.tr key={d.hostname} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                                    <td><strong style={{ color: 'var(--text-primary)' }}>{d.hostname}</strong></td>
                                    <td>
                                        <span className={`badge ${d.is_online ? 'badge-success' : 'badge-danger'}`}>
                                            {d.is_online ? '● UP' : '● DOWN'}
                                        </span>
                                    </td>
                                    <td><span className="tag">{d.software_version || 'N/A'}</span></td>
                                    <td style={{ color: 'var(--text-secondary)' }}>
                                        {d.last_backup_date ? new Date(d.last_backup_date).toLocaleString('fr-FR') : '—'}
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
