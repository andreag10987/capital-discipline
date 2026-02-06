import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import goalsService from '../../services/goals';
import styles from './ProgressCard.module.css';

const ProgressCard = ({ goal, onPause, onResume, onDelete }) => {
  const { t } = useTranslation();
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showMenu, setShowMenu] = useState(false);

  useEffect(() => {
    loadProgress();
  }, [goal?.id]);

  const loadProgress = async () => {
    if (!goal?.id) return;
    try {
      setLoading(true);
      const data = await goalsService.getGoalProgress(goal.id);
      setProgress(data);
    } catch (error) {
      console.error('Error loading progress:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !progress) {
    return <div className={styles.card}><div className={styles.loading}>{t('common.loading')}</div></div>;
  }

  const progressPercent = Math.min(progress.progress_percent, 100);
  const isCompleted = progress.goal.status === 'COMPLETED';
  const isPaused = progress.goal.status === 'PAUSED';

  return (
    <div className={`${styles.card} ${isCompleted ? styles.completed : ''} ${isPaused ? styles.paused : ''}`}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <span className={`${styles.statusBadge} ${styles[progress.goal.status.toLowerCase()]}`}>
            {t(`goals.status.${progress.goal.status.toLowerCase()}`)}
          </span>
          <h2 className={styles.target}>
            {t('goals.targetLabel')}: ${progress.goal.target_capital.toFixed(2)}
          </h2>
        </div>
        <div className={styles.menuWrapper}>
          <button className={styles.menuBtn} onClick={() => setShowMenu(!showMenu)}>⋮</button>
          {showMenu && (
            <div className={styles.menu}>
              {isPaused ? (
                <button className={styles.menuItem} onClick={() => { onResume && onResume(); setShowMenu(false); }}>
                  ▶ {t('goals.resume')}
                </button>
              ) : (
                <button className={styles.menuItem} onClick={() => { onPause && onPause(); setShowMenu(false); }}>
                  ⏸ {t('goals.pause')}
                </button>
              )}
              <button className={`${styles.menuItem} ${styles.menuDelete}`} onClick={() => { onDelete && onDelete(); setShowMenu(false); }}>
                🗑 {t('goals.delete')}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Barra de progreso */}
      <div className={styles.progressSection}>
        <div className={styles.progressBar}>
          <div
            className={styles.progressFill}
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        <div className={styles.progressLabels}>
          <span className={styles.progressPercent}>{progressPercent.toFixed(1)}%</span>
          <span className={styles.progressCurrent}>${progress.current_capital.toFixed(2)} / ${progress.goal.target_capital.toFixed(2)}</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className={styles.statsGrid}>
        <div className={styles.statItem}>
          <span className={styles.statLabel}>{t('goals.stats.capitalGained')}</span>
          <span className={`${styles.statValue} ${progress.capital_gained >= 0 ? styles.positive : styles.negative}`}>
            {progress.capital_gained >= 0 ? '+' : ''}{progress.capital_gained.toFixed(2)}
          </span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statLabel}>{t('goals.stats.daysElapsed')}</span>
          <span className={styles.statValue}>{progress.days_elapsed}</span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statLabel}>{t('goals.stats.realWinrate')}</span>
          <span className={styles.statValue}>
            {progress.real_winrate !== null ? `${(progress.real_winrate * 100).toFixed(1)}%` : '—'}
          </span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statLabel}>{t('goals.stats.eta')}</span>
          <span className={styles.statValue}>
            {progress.estimated_days_to_goal !== null ? `${progress.estimated_days_to_goal} ${t('goals.preview.days')}` : '—'}
          </span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statLabel}>{t('goals.stats.dailyGrowth')}</span>
          <span className={`${styles.statValue} ${progress.daily_growth_factor >= 1 ? styles.positive : styles.negative}`}>
            {((progress.daily_growth_factor - 1) * 100).toFixed(2)}%
          </span>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statLabel}>{t('goals.stats.startDate')}</span>
          <span className={styles.statValue}>{new Date(progress.goal.start_date).toLocaleDateString()}</span>
        </div>
      </div>

      {progress.goal.not_recommended && (
        <div className={styles.warningBanner}>⚠️ {t('goals.warning.lowPayout')}</div>
      )}
    </div>
  );
};

export default ProgressCard;