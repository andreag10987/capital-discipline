import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useToastStore } from '../../store/toastStore';
import { getUserDetail } from '../../services/admin';
import UserDetailCard from '../../components/admin/UserDetailCard';
import UserActions from '../../components/admin/UserActions';
import styles from './AdminUserDetail.module.css';

const AdminUserDetail = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const showToast = useToastStore((state) => state.showToast);
  
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserDetail();
  }, [userId]);

  const fetchUserDetail = async () => {
    try {
      setLoading(true);
      const data = await getUserDetail(userId);
      setUser(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching user detail:', error);
      showToast('Error al cargar usuario', 'error');
      setLoading(false);
    }
  };

  const handleActionComplete = () => {
    fetchUserDetail(); // Refresh data
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Cargando detalles...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>Usuario no encontrado</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <button onClick={() => navigate('/admin/users')} className={styles.backButton}>
          ← Volver a la lista
        </button>
        <h1 className={styles.title}>Detalle de Usuario</h1>
      </div>

      {/* User Info Grid */}
      <div className={styles.grid}>
        {/* Basic Info */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>📧 Información Básica</h2>
          <UserDetailCard user={user} />
        </div>

        {/* Actions */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>⚙️ Acciones</h2>
          <UserActions user={user} onActionComplete={handleActionComplete} />
        </div>
      </div>

      {/* Plan Info */}
      {user.plan && (
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>💎 Plan Actual</h2>
          <div className={styles.planCard}>
            <div className={styles.planInfo}>
              <div className={styles.planName}>{user.plan.display_name}</div>
              <div className={styles.planPrice}>${user.plan.price_usd}/mes</div>
              <div className={styles.planDate}>
                Desde: {new Date(user.plan.started_at).toLocaleDateString('es-ES')}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Devices */}
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>📱 Dispositivos ({user.devices.length})</h2>
        {user.devices.length > 0 ? (
          <div className={styles.deviceGrid}>
            {user.devices.map((device) => (
              <div key={device.id} className={styles.deviceCard}>
                <div className={styles.devicePlatform}>{device.platform || 'Unknown'}</div>
                <div className={styles.deviceHash}>{device.fingerprint_hash}</div>
                <div className={styles.deviceStats}>
                  <span>🔑 {device.login_count} logins</span>
                  <span>🕐 Último: {new Date(device.last_seen).toLocaleDateString('es-ES')}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className={styles.empty}>Sin dispositivos registrados</div>
        )}
      </div>

      {/* OAuth Identities */}
      {user.oauth_identities.length > 0 && (
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>🔐 Identidades OAuth ({user.oauth_identities.length})</h2>
          <div className={styles.oauthGrid}>
            {user.oauth_identities.map((identity, index) => (
              <div key={index} className={styles.oauthCard}>
                <div className={styles.oauthProvider}>
                  {identity.provider === 'google' ? '🔵 Google' : '🔷 Facebook'}
                </div>
                <div className={styles.oauthEmail}>{identity.provider_email}</div>
                <div className={styles.oauthDate}>
                  Último login: {new Date(identity.last_login).toLocaleDateString('es-ES')}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Abuse Score */}
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>⚠️ Score de Abuso</h2>
        <div className={styles.abuseCard}>
          <div className={styles.abuseScore}>
            <div className={styles.abuseScoreValue}>{user.abuse_score.score}/100</div>
            <div className={`${styles.abuseLevel} ${styles[`level${user.abuse_score.risk_level}`]}`}>
              {user.abuse_score.risk_level === 'low' && '🟢 Riesgo Bajo'}
              {user.abuse_score.risk_level === 'medium' && '🟡 Riesgo Medio'}
              {user.abuse_score.risk_level === 'high' && '🔴 Riesgo Alto'}
            </div>
          </div>
          {user.abuse_score.flags.length > 0 && (
            <div className={styles.abuseFlags}>
              <strong>Flags:</strong>
              <ul>
                {user.abuse_score.flags.map((flag, index) => (
                  <li key={index}>{flag}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Abuse Events */}
      {user.abuse_events.length > 0 && (
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>🚨 Eventos de Abuso ({user.abuse_events.length})</h2>
          <div className={styles.eventsList}>
            {user.abuse_events.map((event) => (
              <div key={event.id} className={styles.eventCard}>
                <div className={styles.eventHeader}>
                  <span className={`${styles.eventSeverity} ${styles[event.severity]}`}>
                    {event.severity.toUpperCase()}
                  </span>
                  <span className={styles.eventType}>{event.event_type}</span>
                  <span className={styles.eventDate}>
                    {new Date(event.created_at).toLocaleString('es-ES')}
                  </span>
                </div>
                {event.description && (
                  <div className={styles.eventDescription}>{event.description}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminUserDetail;