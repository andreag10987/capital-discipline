import React, { useState } from 'react';
import { useToastStore } from '../../store/toastStore';
import { blockUser, unblockUser, changeUserPlan } from '../../services/admin';
import ConfirmModal from './ConfirmModal';
import styles from './UserActions.module.css';

const UserActions = ({ user, onActionComplete }) => {
  const showToast = useToastStore((state) => state.showToast);
  const [showBlockModal, setShowBlockModal] = useState(false);
  const [showUnblockModal, setShowUnblockModal] = useState(false);
  const [showChangePlanModal, setShowChangePlanModal] = useState(false);
  const [blockReason, setBlockReason] = useState('');
  const [selectedPlan, setSelectedPlan] = useState('FREE');
  const [loading, setLoading] = useState(false);

  const handleBlock = async () => {
    if (!blockReason.trim()) {
      showToast('Debes proporcionar una razón', 'error');
      return;
    }

    try {
      setLoading(true);
      await blockUser(user.id, blockReason);
      showToast('Usuario bloqueado exitosamente', 'success');
      setShowBlockModal(false);
      setBlockReason('');
      onActionComplete();
    } catch (error) {
      console.error('Error blocking user:', error);
      showToast('Error al bloquear usuario', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleUnblock = async () => {
    try {
      setLoading(true);
      await unblockUser(user.id);
      showToast('Usuario desbloqueado exitosamente', 'success');
      setShowUnblockModal(false);
      onActionComplete();
    } catch (error) {
      console.error('Error unblocking user:', error);
      showToast('Error al desbloquear usuario', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePlan = async () => {
    try {
      setLoading(true);
      await changeUserPlan(user.id, selectedPlan);
      showToast(`Plan cambiado a ${selectedPlan} exitosamente`, 'success');
      setShowChangePlanModal(false);
      onActionComplete();
    } catch (error) {
      console.error('Error changing plan:', error);
      showToast('Error al cambiar plan', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      {/* Block/Unblock */}
      {user.is_blocked ? (
        <button
          onClick={() => setShowUnblockModal(true)}
          className={`${styles.button} ${styles.unblockButton}`}
        >
          🔓 Desbloquear Usuario
        </button>
      ) : (
        <button
          onClick={() => setShowBlockModal(true)}
          className={`${styles.button} ${styles.blockButton}`}
        >
          🚫 Bloquear Usuario
        </button>
      )}

      {/* Change Plan */}
      <button
        onClick={() => setShowChangePlanModal(true)}
        className={`${styles.button} ${styles.planButton}`}
      >
        💎 Cambiar Plan
      </button>

      {/* Block Modal */}
      <ConfirmModal
        isOpen={showBlockModal}
        onClose={() => setShowBlockModal(false)}
        onConfirm={handleBlock}
        title="Bloquear Usuario"
        confirmText="Bloquear"
        confirmColor="danger"
        loading={loading}
      >
        <p>¿Estás seguro de que deseas bloquear a este usuario?</p>
        <p><strong>{user.email}</strong></p>
        <div className={styles.inputGroup}>
          <label>Razón del bloqueo:</label>
          <textarea
            value={blockReason}
            onChange={(e) => setBlockReason(e.target.value)}
            placeholder="Explica por qué bloqueas este usuario..."
            rows={4}
            className={styles.textarea}
          />
        </div>
      </ConfirmModal>

      {/* Unblock Modal */}
      <ConfirmModal
        isOpen={showUnblockModal}
        onClose={() => setShowUnblockModal(false)}
        onConfirm={handleUnblock}
        title="Desbloquear Usuario"
        confirmText="Desbloquear"
        confirmColor="success"
        loading={loading}
      >
        <p>¿Estás seguro de que deseas desbloquear a este usuario?</p>
        <p><strong>{user.email}</strong></p>
      </ConfirmModal>

      {/* Change Plan Modal */}
      <ConfirmModal
        isOpen={showChangePlanModal}
        onClose={() => setShowChangePlanModal(false)}
        onConfirm={handleChangePlan}
        title="Cambiar Plan"
        confirmText="Cambiar Plan"
        confirmColor="primary"
        loading={loading}
      >
        <p>Cambiar el plan de:</p>
        <p><strong>{user.email}</strong></p>
        <div className={styles.inputGroup}>
          <label>Nuevo plan:</label>
          <select
            value={selectedPlan}
            onChange={(e) => setSelectedPlan(e.target.value)}
            className={styles.select}
          >
            <option value="FREE">FREE</option>
            <option value="BASIC">BASIC</option>
            <option value="PRO">PRO</option>
          </select>
        </div>
      </ConfirmModal>
    </div>
  );
};

export default UserActions;