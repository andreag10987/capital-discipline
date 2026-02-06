import { useTranslation } from 'react-i18next'
import Card from '../common/Card'
import styles from './ProjectionsView.module.css'

export default function ProjectionsView({ projection15, projection30 }) {
  const { t } = useTranslation()

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>{t('reports.projections')}</h2>
      <div className={styles.grid}>
        <Card title="15 Days">
          <div className={styles.projection}>
            <div className={styles.metric}>
              <span className={styles.label}>{t('reports.estimatedCapital')}</span>
              <span className={styles.value}>${projection15?.estimated_capital.toFixed(2)}</span>
            </div>
            <div className={styles.metric}>
              <span className={styles.label}>{t('reports.estimatedProfit')}</span>
              <span className={`${styles.value} ${projection15?.estimated_profit >= 0 ? styles.positive : styles.negative}`}>
                ${projection15?.estimated_profit.toFixed(2)}
              </span>
            </div>
          </div>
        </Card>

        <Card title="30 Days">
          <div className={styles.projection}>
            <div className={styles.metric}>
              <span className={styles.label}>{t('reports.estimatedCapital')}</span>
              <span className={styles.value}>${projection30?.estimated_capital.toFixed(2)}</span>
            </div>
            <div className={styles.metric}>
              <span className={styles.label}>{t('reports.estimatedProfit')}</span>
              <span className={`${styles.value} ${projection30?.estimated_profit >= 0 ? styles.positive : styles.negative}`}>
                ${projection30?.estimated_profit.toFixed(2)}
              </span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}