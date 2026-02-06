import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import Card from '../common/Card'
import Button from '../common/Button'
import styles from './PlanCalculator.module.css'

export default function PlanCalculator({ onCalculate }) {
  const { t } = useTranslation()
  const [sessionsPerDay, setSessionsPerDay] = useState(2)
  const [opsPerSession, setOpsPerSession] = useState(5)
  const [riskPercent, setRiskPercent] = useState(2)
  const [winrate, setWinrate] = useState(60)
  const [loading, setLoading] = useState(false)

  const handleCalculate = async () => {
    setLoading(true)
    await onCalculate({
      sessions_per_day: sessionsPerDay,
      ops_per_session: opsPerSession,
      risk_percent: riskPercent,
      winrate: winrate / 100
    })
    setLoading(false)
  }

  return (
    <Card title={t('goalPlanner.planCalculator')}>
      <div className={styles.calculator}>
        <div className={styles.field}>
          <label className={styles.label}>{t('goalPlanner.sessionsPerDay')}</label>
          <div className={styles.options}>
            <button
              type="button"
              className={`${styles.option} ${sessionsPerDay === 2 ? styles.active : ''}`}
              onClick={() => setSessionsPerDay(2)}
            >
              2
            </button>
            <button
              type="button"
              className={`${styles.option} ${sessionsPerDay === 3 ? styles.active : ''}`}
              onClick={() => setSessionsPerDay(3)}
            >
              3
            </button>
          </div>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>{t('goalPlanner.opsPerSession')}</label>
          <div className={styles.options}>
            <button
              type="button"
              className={`${styles.option} ${opsPerSession === 4 ? styles.active : ''}`}
              onClick={() => setOpsPerSession(4)}
            >
              4
            </button>
            <button
              type="button"
              className={`${styles.option} ${opsPerSession === 5 ? styles.active : ''}`}
              onClick={() => setOpsPerSession(5)}
            >
              5
            </button>
          </div>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>{t('goalPlanner.riskPercent')}</label>
          <div className={styles.options}>
            <button
              type="button"
              className={`${styles.option} ${riskPercent === 2 ? styles.active : ''}`}
              onClick={() => setRiskPercent(2)}
            >
              2%
            </button>
            <button
              type="button"
              className={`${styles.option} ${riskPercent === 3 ? styles.active : ''}`}
              onClick={() => setRiskPercent(3)}
            >
              3%
            </button>
          </div>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>
            {t('goalPlanner.winrate')}: {winrate}%
          </label>
          <input
            type="range"
            min="50"
            max="80"
            value={winrate}
            onChange={(e) => setWinrate(parseInt(e.target.value))}
            className={styles.slider}
          />
          <div className={styles.sliderLabels}>
            <span>50%</span>
            <span>65%</span>
            <span>80%</span>
          </div>
        </div>

        <Button onClick={handleCalculate} disabled={loading}>
          {loading ? t('common.loading') : t('goalPlanner.calculate')}
        </Button>
      </div>
    </Card>
  )
}