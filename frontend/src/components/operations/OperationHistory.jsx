import { useTranslation } from 'react-i18next'
import Card from '../common/Card'
import styles from './OperationHistory.module.css'

export default function OperationHistory({ operations }) {
  const { t } = useTranslation()

  return (
    <Card title={t('operations.title')}>
      <div className={styles.history}>
        {operations.length === 0 ? (
          <p className={styles.empty}>No operations yet</p>
        ) : (
          <div className={styles.list}>
            {operations.map((op) => (
              <div key={op.id} className={styles.operation}>
                <div className={styles.header}>
                  <span className={`${styles.result} ${styles[op.result.toLowerCase()]}`}>
                    {op.result}
                  </span>
                  <span className={styles.date}>
                    {new Date(op.created_at).toLocaleString()}
                  </span>
                </div>
                <div className={styles.details}>
                  <span>{t('operations.risk')}: {op.risk_percent}%</span>
                  <span>{t('operations.amount')}: ${op.amount.toFixed(2)}</span>
                  <span className={op.profit >= 0 ? styles.positive : styles.negative}>
                    {t('operations.profit')}: ${op.profit.toFixed(2)}
                  </span>
                </div>
                {op.comment && (
                  <p className={styles.comment}>{op.comment}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </Card>
  )
}