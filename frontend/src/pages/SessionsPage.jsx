import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { getSessions, createSession } from '../services/sessions'
import { useToastStore } from '../store/toastStore'
import SessionList from '../components/sessions/SessionList'
import CreateSessionModal from '../components/sessions/CreateSessionModal'
import Button from '../components/common/Button'
import styles from './SessionsPage.module.css'

export default function SessionsPage() {
  const { t } = useTranslation()
  const { addToast } = useToastStore()
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      const data = await getSessions()
      setSessions(data)
    } catch (error) {
      addToast(t('common.error'), 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSession = async (risk) => {
    try {
      await createSession(risk)
      addToast(t('common.success'), 'success')
      loadSessions()
    } catch (error) {
      addToast(error.response?.data?.detail || t('common.error'), 'error')
    }
  }

  if (loading) {
    return <div className={styles.loading}>{t('common.loading')}</div>
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>{t('sessions.title')}</h1>
        <Button onClick={() => setShowModal(true)}>
          {t('sessions.createSession')}
        </Button>
      </div>

      <SessionList sessions={sessions} />

      <CreateSessionModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onCreate={handleCreateSession}
      />
    </div>
  )
}