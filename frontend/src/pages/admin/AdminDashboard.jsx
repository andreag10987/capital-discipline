import React, { useState, useEffect } from 'react';
import { useToastStore } from '../../store/toastStore';
import { getSystemMetrics } from '../../services/admin';
import styles from './AdminDashboard.module.css';

const AdminDashboard = () => {
  const showToast = useToastStore((state) => state.showToast);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const data = await getSystemMetrics();
      setMetrics(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching metrics:', error);
      showToast('Error al cargar métricas', 'error');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Cargando métricas...</div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>Error al cargar métricas</div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Usuarios',
      value: metrics.total_users,
      icon: '👥',
      color: '#667eea'
    },
    {
      title: 'Usuarios Activos (7d)',
      value: metrics.active_users_7d,
      icon: '✨',
      color: '#48bb78'
    },
    {
      title: 'Usuarios Bloqueados',
      value: metrics.blocked_users,
      icon: '🚫',
      color: '#f56565'
    },
    {
      title: 'Nuevos Usuarios (30d)',
      value: metrics.new_users_30d,
      icon: '🆕',
      color: '#ed8936'
    },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Dashboard de Administración</h1>
        <p className={styles.subtitle}>Métricas y estadísticas del sistema</p>
      </div>

      {/* Stats Cards */}
      <div className={styles.statsGrid}>
        {statCards.map((stat, index) => (
          <div key={index} className={styles.statCard} style={{ borderLeftColor: stat.color }}>
            <div className={styles.statIcon} style={{ color: stat.color }}>
              {stat.icon}
            </div>
            <div className={styles.statContent}>
              <div className={styles.statTitle}>{stat.title}</div>
              <div className={styles.statValue}>{stat.value}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Plan Distribution */}
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Distribución de Planes</h2>
        <div className={styles.planCards}>
          {Object.entries(metrics.plan_distribution).map(([plan, count]) => (
            <div key={plan} className={styles.planCard}>
              <div className={styles.planName}>{plan}</div>
              <div className={styles.planCount}>{count} usuarios</div>
              <div className={styles.planPercentage}>
                {((count / metrics.total_users) * 100).toFixed(1)}%
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Conversion & Abuse */}
      <div className={styles.twoColumns}>
        <div className={styles.infoCard}>
          <h3 className={styles.infoTitle}>Tasa de Conversión</h3>
          <div className={styles.infoValue}>{metrics.conversion_rate}%</div>
          <div className={styles.infoSubtext}>FREE → PAID</div>
        </div>

        <div className={styles.infoCard}>
          <h3 className={styles.infoTitle}>Eventos de Abuso (30d)</h3>
          <div className={styles.infoValue}>{metrics.abuse_events_30d}</div>
          <div className={styles.infoSubtext}>
            {Object.entries(metrics.abuse_by_severity).map(([sev, count]) => (
              <span key={sev} className={styles.severityBadge}>
                {sev}: {count}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;