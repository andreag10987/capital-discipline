import { useTranslation } from 'react-i18next'
import Card from '../common/Card'
import styles from './PlanResults.module.css'

export default function PlanResults({ plan }) {
  const { t } = useTranslation()

  if (!plan) return null

  return (
    <div className={styles.container}>
      {/* Warnings */}
      {plan.warnings.length > 0 && (
        <Card>
          <div className={styles.warnings}>
            <h3 className={styles.warningTitle}>⚠️ {t('goalPlanner.warnings')}</h3>
            <ul className={styles.warningList}>
              {plan.warnings.map((warning, idx) => (
                <li key={idx} className={styles.warningItem}>{warning}</li>
              ))}
            </ul>
          </div>
        </Card>
      )}

      {/* Plan Summary */}
      <Card title={t('goalPlanner.planSummary')}>
        <div className={styles.grid}>
          <div className={styles.metric}>
            <span className={styles.metricLabel}>{t('goalPlanner.opsPerDay')}</span>
            <span className={styles.metricValue}>{plan.ops_per_day}</span>
          </div>
          <div className={styles.metric}>
            <span className={styles.metricLabel}>{t('goalPlanner.stakePerOp')}</span>
            <span className={styles.metricValue}>${plan.stake_per_operation}</span>
          </div>
          <div className={styles.metric}>
            <span className={styles.metricLabel}>{t('goalPlanner.winProfit')}</span>
            <span className={`${styles.metricValue} ${styles.positive}`}>
              +${plan.win_profit}
            </span>
          </div>
          <div className={styles.metric}>
            <span className={styles.metricLabel}>{t('goalPlanner.lossAmount')}</span>
            <span className={`${styles.metricValue} ${styles.negative}`}>
              -${plan.loss_amount}
            </span>
          </div>
        </div>
      </Card>

      {/* Projections */}
      <Card title={t('goalPlanner.projections')}>
        <div className={styles.projections}>
          <div className={styles.projection}>
            <span className={styles.projectionLabel}>15 {t('reports.days')}</span>
            <span className={styles.projectionValue}>${plan.projection_15_days.toFixed(2)}</span>
          </div>
          <div className={styles.projection}>
            <span className={styles.projectionLabel}>30 {t('reports.days')}</span>
            <span className={styles.projectionValue}>${plan.projection_30_days.toFixed(2)}</span>
          </div>
          {plan.days_to_goal && (
            <div className={styles.projection}>
              <span className={styles.projectionLabel}>{t('goalPlanner.daysToGoal')}</span>
              <span className={`${styles.projectionValue} ${styles.highlight}`}>
                {plan.days_to_goal} {t('reports.days')}
              </span>
            </div>
          )}
        </div>
      </Card>

      {/* Limits Reminder */}
      <Card title={t('goalPlanner.limitsReminder')}>
        <ul className={styles.limitsList}>
          {Object.entries(plan.limits_reminder).map(([key, value]) => (
            <li key={key} className={styles.limitItem}>{value}</li>
          ))}
        </ul>
      </Card>
    </div>
  )
}