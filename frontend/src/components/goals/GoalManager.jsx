import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import goalsService from '../../services/goals';
import { useAccountStore } from '../../store/accountStore';
import GoalForm from './GoalForm';
import ProgressCard from './ProgressCard';
import styles from './GoalManager.module.css';

const GoalManager = ({ onGoalCreated, onGoalDeleted, onActiveGoalChange }) => {
  const { t } = useTranslation();
  const { account, fetchAccount } = useAccountStore();
  const [goals, setGoals] = useState([]);
  const [activeGoal, setActiveGoal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetchAccount();
    loadGoals();
  }, []);

  const loadGoals = async () => {
    try {
      setLoading(true);
      const data = await goalsService.getGoals();
      setGoals(data);

      const active = data.find(g => g.status === 'ACTIVE' || g.status === 'PAUSED');
      setActiveGoal(active || null);

      // Notificar al padre con el ID del objetivo activo
      if (onActiveGoalChange) {
        onActiveGoalChange(active ? active.id : null);
      }

      setShowForm(!active);
    } catch (error) {
      console.error('Error loading goals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGoal = async (goalData) => {
    try {
      const newGoal = await goalsService.createGoal(goalData);
      await fetchAccount();
      await loadGoals();
      setShowForm(false);
      if (onGoalCreated) onGoalCreated(newGoal);
    } catch (error) {
      console.error('Error creating goal:', error);
      throw error;
    }
  };

  const handleDeleteGoal = async (goalId) => {
    if (!confirm(t('goals.confirmDelete'))) return;
    try {
      await goalsService.deleteGoal(goalId);
      await loadGoals();
      if (onGoalDeleted) onGoalDeleted(goalId);
    } catch (error) {
      console.error('Error deleting goal:', error);
    }
  };

  const handlePauseGoal = async (goalId) => {
    try {
      await goalsService.updateGoal(goalId, { status: 'PAUSED' });
      await loadGoals();
    } catch (error) {
      console.error('Error pausing goal:', error);
    }
  };

  const handleResumeGoal = async (goalId) => {
    try {
      await goalsService.updateGoal(goalId, { status: 'ACTIVE' });
      await loadGoals();
    } catch (error) {
      console.error('Error resuming goal:', error);
    }
  };

  if (loading) {
    return <div className={styles.loading}>{t('common.loading')}</div>;
  }

  return (
    <div className={styles.manager}>
      {activeGoal ? (
        <ProgressCard
          goal={activeGoal}
          onPause={() => handlePauseGoal(activeGoal.id)}
          onResume={() => handleResumeGoal(activeGoal.id)}
          onDelete={() => handleDeleteGoal(activeGoal.id)}
        />
      ) : showForm ? (
        <GoalForm
          account={account}
          onSubmit={handleCreateGoal}
          onCancel={() => setShowForm(false)}
        />
      ) : (
        <div className={styles.noGoal}>
          <p>{t('goals.noActiveGoal')}</p>
          <button
            className={styles.createButton}
            onClick={() => setShowForm(true)}
          >
            {t('goals.createNew')}
          </button>
        </div>
      )}

      {/* Historial de objetivos completados/cancelados */}
      {goals.filter(g => g.status === 'COMPLETED' || g.status === 'CANCELLED').length > 0 && (
        <div className={styles.history}>
          <h3>{t('goals.history')}</h3>
          <div className={styles.goalsList}>
            {goals
              .filter(g => g.status === 'COMPLETED' || g.status === 'CANCELLED')
              .map(goal => (
                <div key={goal.id} className={styles.goalCard}>
                  <div className={styles.goalHeader}>
                    <span className={styles.goalTarget}>
                      ${goal.target_capital.toFixed(2)}
                    </span>
                    <span className={`${styles.status} ${styles[goal.status.toLowerCase()]}`}>
                      {t(`goals.status.${goal.status.toLowerCase()}`)}
                    </span>
                  </div>
                  <div className={styles.goalDates}>
                    {new Date(goal.start_date).toLocaleDateString()} -
                    {goal.completed_at ? ` ${new Date(goal.completed_at).toLocaleDateString()}` : ''}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default GoalManager;