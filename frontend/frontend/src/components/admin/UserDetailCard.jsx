import React from 'react';
import styles from './UserDetailCard.module.css';

const UserDetailCard = ({ user }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={styles.card}>
      <div className={styles.row}>
        <div className={styles.label}>ID</div>
        <div className={styles.value}>{user.id}</div>
      </div>

      <div className={styles.row}>
        <div className={styles.label}>Email</div>
        <div className={styles.value}>
          {user.email}
          {user.is_admin && <span className={styles.adminBadge}>👑 Admin</span>}
        </div>
      </div>

      <div className={styles.row}>
        <div className={styles.label}>Email Verificado</div>
        <div className={styles.value}>
          {user.email_verified ? (
            <span className={styles.verified}>✓ Verificado</span>
          ) : (
            <span className={styles.unverified}>✗ No verificado</span>
          )}
        </div>
      </div>

      <div className={styles.row}>
        <div className={styles.label}>Estado</div>
        <div className={styles.value}>
          {user.is_blocked ? (
            <span className={styles.blocked}>🚫 Bloqueado</span>
          ) : (
            <span className={styles.active}>✅ Activo</span>
          )}
        </div>
      </div>

      {user.is_blocked && user.blocked_reason && (
        <div className={styles.row}>
          <div className={styles.label}>Razón de Bloqueo</div>
          <div className={styles.value}>
            <div className={styles.blockReason}>{user.blocked_reason}</div>
            <div className={styles.blockDate}>
              Bloqueado el: {formatDate(user.blocked_at)}
            </div>
          </div>
        </div>
      )}

      <div className={styles.row}>
        <div className={styles.label}>Fecha de Registro</div>
        <div className={styles.value}>{formatDate(user.created_at)}</div>
      </div>
    </div>
  );
};

export default UserDetailCard;