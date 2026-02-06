import { useTranslation } from 'react-i18next'
import Card from '../common/Card'
import styles from './DashboardSummary.module.css'

export default function DashboardSummary({ account, sessions }) {
  const { t } = useTranslation()

  return (
    <div className={styles.grid}>
      <Card>
        <div className={styles.metric}>
          <span className={styles.label}>{t('dashboard.currentCapital')}</span>
          <span className={styles.value}>${account?.capital.toFixed(2)}</span>
        </div>
      </Card>
      <Card>
        <div className={styles.metric}>
          <span className={styles.label}>{t('dashboard.payout')}</span>
          <span className={styles.value}>{(account?.payout * 100).toFixed(0)}%</span>
        </div>
      </Card>
      <Card>
        <div className={styles.metric}>
          <span className={styles.label}>{t('dashboard.sessionsToday')}</span>
          <span className={styles.value}>{sessions?.length || 0}/3</span>
        </div>
      </Card>
    </div>
  )
}