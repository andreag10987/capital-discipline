import React from 'react';
import styles from './UserTable.module.css';

const UserTable = ({ users, onUserClick }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getPlanBadgeClass = (plan) => {
    switch (plan) {
      case 'FREE':
        return styles.badgeFree;
      case 'BASIC':
        return styles.badgeBasic;
      case 'PRO':
        return styles.badgePro;
      default:
        return styles.badgeFree;
    }
  };

  if (users.length === 0) {
    return (
      <div className={styles.empty}>
        <div className={styles.emptyIcon}>🔍</div>
        <div className={styles.emptyText}>No se encontraron usuarios</div>
      </div>
    );
  }

  return (
    <div className={styles.tableContainer}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Email</th>
            <th>Plan</th>
            <th>Estado</th>
            <th>Verificado</th>
            <th>Dispositivos</th>
            <th>Eventos</th>
            <th>Fecha Registro</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr
              key={user.id}
              onClick={() => onUserClick(user.id)}
              className={styles.row}
            >
              <td className={styles.emailCell}>
                {user.is_admin && <span className={styles.adminBadge}>👑</span>}
                {user.email}
              </td>
              
              <td>
                <span className={`${styles.badge} ${getPlanBadgeClass(user.plan)}`}>
                  {user.plan}
                </span>
              </td>
              
              <td>
                {user.is_blocked ? (
                  <span className={styles.statusBlocked}>🚫 Bloqueado</span>
                ) : (
                  <span className={styles.statusActive}>✅ Activo</span>
                )}
              </td>
              
              <td>
                {user.email_verified ? (
                  <span className={styles.verified}>✓</span>
                ) : (
                  <span className={styles.unverified}>✗</span>
                )}
              </td>
              
              <td className={styles.centered}>{user.device_count}</td>
              
              <td className={styles.centered}>
                {user.abuse_events > 0 ? (
                  <span className={styles.abuseWarning}>{user.abuse_events}</span>
                ) : (
                  <span className={styles.abuseNone}>0</span>
                )}
              </td>
              
              <td className={styles.dateCell}>
                {formatDate(user.created_at)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default UserTable;