import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { getReports, getProjections } from '../services/reports'
import { useToastStore } from '../store/toastStore'
import ReportsCharts from '../components/reports/ReportsCharts'
import ProjectionsView from '../components/reports/ProjectionsView'
import styles from './ReportsPage.module.css'

export default function ReportsPage() {
  const { t } = useTranslation()
  const { addToast } = useToastStore()
  const [reports, setReports] = useState({})
  const [projection15, setProjection15] = useState(null)
  const [projection30, setProjection30] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData(7)
  }, [])

  const loadData = async (days) => {
    try {
      const reportsData = await getReports(days)
      setReports(reportsData)
      const proj15 = await getProjections(15)
      setProjection15(proj15)
      const proj30 = await getProjections(30)
      setProjection30(proj30)
    } catch (error) {
      addToast(t('common.error'), 'error')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className={styles.loading}>{t('common.loading')}</div>
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>{t('reports.title')}</h1>
      <ReportsCharts reports={reports} onPeriodChange={loadData} />
      <ProjectionsView projection15={projection15} projection30={projection30} />
    </div>
  )
}