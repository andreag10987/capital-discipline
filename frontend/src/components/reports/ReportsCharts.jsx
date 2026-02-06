import { useState } from 'react'
import { Line, Bar } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend } from 'chart.js'
import { useTranslation } from 'react-i18next'
import Card from '../common/Card'
import Button from '../common/Button'
import styles from './ReportsCharts.module.css'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend)

const PERIODS = [1, 2, 3, 7, 15]

export default function ReportsCharts({ reports, onPeriodChange }) {
  const { t } = useTranslation()
  const [period, setPeriod] = useState(7)

  const handlePeriodChange = (newPeriod) => {
    setPeriod(newPeriod)
    onPeriodChange(newPeriod)
  }

  const equityData = {
    labels: reports.metrics?.map(m => new Date(m.date).toLocaleDateString()) || [],
    datasets: [
      {
        label: t('reports.equityCurve'),
        data: reports.metrics?.map(m => m.capital) || [],
        borderColor: 'rgb(37, 99, 235)',
        backgroundColor: 'rgba(37, 99, 235, 0.1)',
        tension: 0.4
      }
    ]
  }

  const profitLossData = {
    labels: reports.metrics?.map(m => new Date(m.date).toLocaleDateString()) || [],
    datasets: [
      {
        label: t('reports.totalProfit'),
        data: reports.metrics?.map(m => m.profit) || [],
        backgroundColor: 'rgba(16, 185, 129, 0.8)'
      },
      {
        label: t('reports.totalLoss'),
        data: reports.metrics?.map(m => m.loss) || [],
        backgroundColor: 'rgba(239, 68, 68, 0.8)'
      }
    ]
  }

  return (
    <div className={styles.container}>
      <Card>
        <div className={styles.header}>
          <h3>{t('reports.selectPeriod')}</h3>
          <div className={styles.periods}>
            {PERIODS.map((p) => (
              <Button
                key={p}
                variant={period === p ? 'primary' : 'secondary'}
                onClick={() => handlePeriodChange(p)}
              >
                {p} {t('reports.days')}
              </Button>
            ))}
          </div>
        </div>

        <div className={styles.stats}>
          <div className={styles.stat}>
            <span className={styles.label}>{t('reports.totalOperations')}</span>
            <span className={styles.value}>{reports.total_operations}</span>
          </div>
          <div className={styles.stat}>
            <span className={styles.label}>{t('reports.winrate')}</span>
            <span className={styles.value}>{reports.winrate?.toFixed(1)}%</span>
          </div>
          <div className={styles.stat}>
            <span className={styles.label}>{t('reports.totalProfit')}</span>
            <span className={`${styles.value} ${styles.positive}`}>
              ${reports.total_profit?.toFixed(2)}
            </span>
          </div>
          <div className={styles.stat}>
            <span className={styles.label}>{t('reports.totalLoss')}</span>
            <span className={`${styles.value} ${styles.negative}`}>
              ${reports.total_loss?.toFixed(2)}
            </span>
          </div>
        </div>
      </Card>

      <Card title={t('reports.equityCurve')}>
        <div className={styles.chart}>
          <Line data={equityData} options={{ responsive: true, maintainAspectRatio: false }} />
        </div>
      </Card>

      <Card title={t('reports.totalProfit') + ' / ' + t('reports.totalLoss')}>
        <div className={styles.chart}>
          <Bar data={profitLossData} options={{ responsive: true, maintainAspectRatio: false }} />
        </div>
      </Card>
    </div>
  )
}