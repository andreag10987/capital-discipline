import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { getOperations, createOperation } from '../services/operations'
import { useToastStore } from '../store/toastStore'
import OperationForm from '../components/operations/OperationForm'
import OperationHistory from '../components/operations/OperationHistory'
import styles from './OperationsPage.module.css'

export default function OperationsPage() {
  const { sessionId } = useParams()
  const { t } = useTranslation()
  const { addToast } = useToastStore()
  const [operations, setOperations] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadOperations()
  }, [sessionId])

  const loadOperations = async () => {
    try {
      const data = await getOperations(parseInt(sessionId))
      setOperations(data)
    } catch (error) {
      addToast(t('common.error'), 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateOperation = async (data) => {
    try {
      await createOperation(data)
      addToast(t('common.success'), 'success')
      loadOperations()
    } catch (error) {
      addToast(error.response?.data?.detail || t('common.error'), 'error')
    }
  }

  if (loading) {
    return <div className={styles.loading}>{t('common.loading')}</div>
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>{t('operations.title')}</h1>
      <div className={styles.grid}>
        <OperationForm sessionId={parseInt(sessionId)} onSubmit={handleCreateOperation} />
        <OperationHistory operations={operations} />
      </div>
    </div>
  )
}