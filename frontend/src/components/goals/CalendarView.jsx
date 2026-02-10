import React, { useMemo, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import goalsService from '../../services/goals';
import styles from './CalendarView.module.css';

const DAYS_FILTER = [7, 30, 60, 90];

const toISODate = (rawDate) => {
  const d = new Date(rawDate);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const getDayVisualStatus = (plan) => {
  if (!plan) return 'no_data';
  if (plan.status === 'BLOCKED') return 'blocked';
  if (!plan.actual_ops || plan.actual_ops === 0) return 'no_trade';
  if (plan.realized_pnl > 0) return 'profit';
  if (plan.realized_pnl < 0) return 'loss';
  return 'draw';
};

const buildMonthGrid = (monthDate) => {
  const year = monthDate.getFullYear();
  const month = monthDate.getMonth();
  const firstDay = new Date(year, month, 1);
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  const mondayBasedStart = (firstDay.getDay() + 6) % 7;
  const totalCells = 42;
  const cells = [];

  for (let i = 0; i < totalCells; i += 1) {
    const dayNumber = i - mondayBasedStart + 1;
    const inCurrentMonth = dayNumber > 0 && dayNumber <= daysInMonth;
    const date = new Date(year, month, dayNumber);

    cells.push({
      inCurrentMonth,
      date,
      isoDate: inCurrentMonth ? toISODate(date) : null,
      dayNumber: inCurrentMonth ? dayNumber : null,
    });
  }

  return cells;
};

const CalendarView = ({ goalId }) => {
  const { t, i18n } = useTranslation();
  const [calendar, setCalendar] = useState(null);
  const [loading, setLoading] = useState(true);
  const [viewDays, setViewDays] = useState(90);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedPlan, setSelectedPlan] = useState(null);

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

  const plansByDate = useMemo(() => {
    const map = new Map();
    if (!calendar?.daily_plans) return map;

    calendar.daily_plans.forEach((plan) => {
      map.set(toISODate(plan.date), plan);
    });

    return map;
  }, [calendar]);

  const monthCells = useMemo(() => buildMonthGrid(currentMonth), [currentMonth]);

  const weekDayNames = useMemo(() => {
    const lang = (i18n.language || '').toLowerCase();
    if (lang.startsWith('es')) {
      return ['LUN', 'MAR', 'MIE', 'JUE', 'VIE', 'SAB', 'DOM'];
    }
    return ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
  }, [i18n.language]);

  const monthTitle = useMemo(
    () => currentMonth.toLocaleDateString(i18n.language, { month: 'long', year: 'numeric' }),
    [currentMonth, i18n.language],
  );

  const closeModal = () => setSelectedPlan(null);

  if (loading) return <div className={styles.loading}>{t('common.loading')}</div>;
  if (!calendar) return null;

  return (
    <div className={styles.container}>
      <div className={styles.filterRow}>
        <span className={styles.filterLabel}>{t('goals.calendar.showDays')}:</span>
        <div className={styles.filterButtons}>
          {DAYS_FILTER.map((d) => (
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
            {calendar.real_winrate !== null ? `${(calendar.real_winrate * 100).toFixed(1)}%` : '-'}
          </span>
        </div>
      </div>

      <div className={styles.legend}>
        <span className={styles.legendItem}><i className={`${styles.dot} ${styles.dotProfit}`} />Profit</span>
        <span className={styles.legendItem}><i className={`${styles.dot} ${styles.dotLoss}`} />Loss</span>
        <span className={styles.legendItem}><i className={`${styles.dot} ${styles.dotDraw}`} />Draw</span>
        <span className={styles.legendItem}><i className={`${styles.dot} ${styles.dotNoTrade}`} />Sin operar</span>
        <span className={styles.legendItem}><i className={`${styles.dot} ${styles.dotBlocked}`} />Bloqueado</span>
      </div>

      <div className={styles.monthHeader}>
        <button
          type="button"
          className={styles.monthNavBtn}
          onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1))}
        >
          {'<'}
        </button>
        <h3 className={styles.monthTitle}>{monthTitle}</h3>
        <button
          type="button"
          className={styles.monthNavBtn}
          onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1))}
        >
          {'>'}
        </button>
      </div>

      <div className={styles.calendarGrid}>
        {weekDayNames.map((name) => (
          <div key={name} className={styles.weekDay}>{name}</div>
        ))}

        {monthCells.map((cell, idx) => {
          const plan = cell.isoDate ? plansByDate.get(cell.isoDate) : null;
          const visualStatus = getDayVisualStatus(plan);

          return (
            <button
              key={`${cell.isoDate || 'empty'}-${idx}`}
              type="button"
              disabled={!cell.inCurrentMonth || !plan}
              onClick={() => plan && setSelectedPlan(plan)}
              className={[
                styles.dayCell,
                !cell.inCurrentMonth ? styles.dayCellOut : '',
                plan ? styles.dayCellActive : '',
                plan ? styles[`status_${visualStatus}`] : '',
              ].join(' ')}
            >
              <span className={styles.dayNumber}>{cell.dayNumber || ''}</span>
              {plan && (
                <span className={styles.dayPnl}>
                  {plan.realized_pnl > 0 ? '+' : ''}{plan.realized_pnl.toFixed(2)}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {selectedPlan && (
        <div className={styles.modalBackdrop} onClick={closeModal}>
          <div className={styles.modalCard} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h4>
                {new Date(selectedPlan.date).toLocaleDateString(i18n.language, {
                  weekday: 'long',
                  day: '2-digit',
                  month: 'long',
                  year: 'numeric',
                })}
              </h4>
              <button type="button" className={styles.closeBtn} onClick={closeModal}>X</button>
            </div>

            <div className={styles.modalStatusRow}>
              <span className={`${styles.dayStatus} ${styles[`status_${getDayVisualStatus(selectedPlan)}`]}`}>
                {selectedPlan.status}
              </span>
              <span className={`${styles.modalPnl} ${selectedPlan.realized_pnl >= 0 ? styles.green : styles.red}`}>
                {selectedPlan.realized_pnl >= 0 ? '+' : ''}${selectedPlan.realized_pnl.toFixed(2)}
              </span>
            </div>

            <div className={styles.detailGrid}>
              <div className={styles.detailItem}><span>{t('goals.calendar.capitalStart')}</span><strong>${selectedPlan.capital_start_of_day.toFixed(2)}</strong></div>
              <div className={styles.detailItem}><span>{t('goals.calendar.stake')}</span><strong>${selectedPlan.planned_stake.toFixed(2)}</strong></div>
              <div className={styles.detailItem}><span>{t('goals.calendar.plannedOps')}</span><strong>{selectedPlan.planned_ops_total}</strong></div>
              <div className={styles.detailItem}><span>{t('goals.calendar.actualOps')}</span><strong>{selectedPlan.actual_ops}</strong></div>
              <div className={styles.detailItem}><span>{t('goals.calendar.wins')}</span><strong>{selectedPlan.wins}</strong></div>
              <div className={styles.detailItem}><span>{t('goals.calendar.losses')}</span><strong>{selectedPlan.losses}</strong></div>
              <div className={styles.detailItem}><span>{t('goals.calendar.draws')}</span><strong>{selectedPlan.draws}</strong></div>
              <div className={styles.detailItem}><span>{t('goals.calendar.sessions')}</span><strong>{selectedPlan.actual_sessions}/{selectedPlan.planned_sessions}</strong></div>
            </div>

            {selectedPlan.blocked_reason && (
              <div className={styles.blockedReason}>Bloqueado: {selectedPlan.blocked_reason}</div>
            )}

            {selectedPlan.notes && (
              <div className={styles.notes}>Notas: {selectedPlan.notes}</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CalendarView;
