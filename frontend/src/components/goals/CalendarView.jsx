import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import goalsService from '../../services/goals';
import styles from './CalendarView.module.css';

const CalendarView = ({ goalId }) => {
  const { t } = useTranslation();
  const [calendar, setCalendar] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedDay, setSelectedDay] = useState(null);
  const [viewDays, setViewDays] = useState(30);

  useEffect(() => {
    if (goalId) loadCalendar();
  }, [goalId, viewDays]);

  const loadCalendar = async () => {
    try {
      setLoading(true);
      const data = await goalsService.getGoalCalendar(goalId, { days: viewDays });
      setCalendar(data);
    } catch (error) {
      console.error('Error loading calendar:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className={styles.loading}>{t('common.loading')}</div>;
  if (!calendar) return null;

  const statusColor = {
    PLANNED: '#aaa',
    IN_PROGRESS: '#667eea',
    COMPLETED: '#28a745',
    BLOCKED: '#dc3545',
  };

  return (
    <div className={styles.container}>
      {/* Filtro de días */}
      <div className={styles.filterRow}>
        <span className={styles.filterLabel}>{t('goals.calendar.showDays')}:</span>
        <div className={styles.filterButtons}>
          {[7, 30, 60, 90].map(d => (
            <button
              key={d}
              className={`${styles.filterBtn} ${viewDays === d ? styles.filterBtnActive : ''}`}
              onClick={() => setViewDays(d)}
            >
              {d}
            </button>
          ))}
        </div>
      </div>

      {/* Resumen superior */}
      <div className={styles.summaryRow}>
        <div className={styles.summaryItem}>
          <span className={styles.summaryLabel}>{t('goals.calendar.totalDays')}</span>
          <span className={styles.summaryValue}>{calendar.total_days}</span>
        </div>
        <div className={styles.summaryItem}>
          <span className={styles.summaryLabel}>{t('goals.calendar.completed')}</span>
          <span className={`${styles.summaryValue} ${styles.green}`}>{calendar.completed_days}</span>
        </div>
        <div className={styles.summaryItem}>
          <span className={styles.summaryLabel}>{t('goals.calendar.blocked')}</span>
          <span className={`${styles.summaryValue} ${styles.red}`}>{calendar.blocked_days}</span>
        </div>
        <div className={styles.summaryItem}>
          <span className={styles.summaryLabel}>{t('goals.calendar.totalPnl')}</span>
          <span className={`${styles.summaryValue} ${calendar.total_pnl >= 0 ? styles.green : styles.red}`}>
            {calendar.total_pnl >= 0 ? '+' : ''}{calendar.total_pnl.toFixed(2)}
          </span>
        </div>
        <div className={styles.summaryItem}>
          <span className={styles.summaryLabel}>{t('goals.calendar.winrate')}</span>
          <span className={styles.summaryValue}>
            {calendar.real_winrate !== null ? `${(calendar.real_winrate * 100).toFixed(1)}%` : '—'}
          </span>
        </div>
      </div>

      {/* Lista de días */}
      <div className={styles.daysList}>
        {calendar.daily_plans.length === 0 ? (
          <div className={styles.emptyState}>{t('goals.calendar.noData')}</div>
        ) : (
          [...calendar.daily_plans].reverse().map((plan) => (
            <div
              key={plan.id}
              className={`${styles.dayCard} ${selectedDay === plan.id ? styles.dayCardSelected : ''}`}
              onClick={() => setSelectedDay(selectedDay === plan.id ? null : plan.id)}
            >
              <div className={styles.dayHeader}>
                <div className={styles.dayLeft}>
                  <div
                    className={styles.statusDot}
                    style={{ background: statusColor[plan.status] }}
                  />
                  <span className={styles.dayDate}>{new Date(plan.date).toLocaleDateString()}</span>
                </div>
                <div className={styles.dayRight}>
                  <span className={`${styles.dayPnl} ${plan.realized_pnl >= 0 ? styles.green : styles.red}`}>
                    {plan.realized_pnl >= 0 ? '+' : ''}{plan.realized_pnl.toFixed(2)}
                  </span>
                  <span className={`${styles.dayStatus} ${styles[`status${plan.status}`]}`}>
                    {t(`goals.calendar.status.${plan.status.toLowerCase()}`)}
                  </span>
                </div>
              </div>

              {/* Detalle expandido */}
              {selectedDay === plan.id && (
                <div className={styles.dayDetail}>
                  <div className={styles.detailGrid}>
                    <div className={styles.detailItem}>
                      <span className={styles.detailLabel}>{t('goals.calendar.capitalStart')}</span>
                      <span className={styles.detailValue}>${plan.capital_start_of_day.toFixed(2)}</span>
                    </div>
                    <div className={styles.detailItem}>
                      <span className={styles.detailLabel}>{t('goals.calendar.plannedOps')}</span>
                      <span className={styles.detailValue}>{plan.planned_ops_total}</span>
                    </div>
                    <div className={styles.detailItem}>
                      <span className={styles.detailLabel}>{t('goals.calendar.actualOps')}</span>
                      <span className={styles.detailValue}>{plan.actual_ops}</span>
                    </div>
                    <div className={styles.detailItem}>
                      <span className={styles.detailLabel}>{t('goals.calendar.stake')}</span>
                      <span className={styles.detailValue}>${plan.planned_stake.toFixed(2)}</span>
                    </div>
                    <div className={styles.detailItem}>
                      <span className={styles.detailLabel}>{t('goals.calendar.wins')}</span>
                      <span className={`${styles.detailValue} ${styles.green}`}>{plan.wins}</span>
                    </div>
                    <div className={styles.detailItem}>
                      <span className={styles.detailLabel}>{t('goals.calendar.losses')}</span>
                      <span className={`${styles.detailValue} ${styles.red}`}>{plan.losses}</span>
                    </div>
                    <div className={styles.detailItem}>
                      <span className={styles.detailLabel}>{t('goals.calendar.draws')}</span>
                      <span className={styles.detailValue}>{plan.draws}</span>
                    </div>
                    <div className={styles.detailItem}>
                      <span className={styles.detailLabel}>{t('goals.calendar.sessions')}</span>
                      <span className={styles.detailValue}>{plan.actual_sessions} / {plan.planned_sessions}</span>
                    </div>
                  </div>
                  {plan.blocked_reason && (
                    <div className={styles.blockedReason}>🚫 {plan.blocked_reason}</div>
                  )}
                  {plan.notes && (
                    <div className={styles.notes}>📝 {plan.notes}</div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default CalendarView;