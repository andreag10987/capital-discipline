import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { getAccount, createAccount } from '../services/account'
import { getSessions } from '../services/sessions'
import { useToastStore } from '../store/toastStore'
import DashboardSummary from '../components/dashboard/DashboardSummary'
import BlockedWarning from '../components/dashboard/BlockedWarning'
import Card from '../components/common/Card'
import Input from '../components/common/Input'
import Button from '../components/common/Button'
import styles from './DashboardPage.module.css'

export default function DashboardPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { addToast } = useToastStore()
  const [account, setAccount] = useState(null)
  const [sessions, setSessions] = useState([])
  const [isBlocked, setIsBlocked] = useState(false)
  const [loading, setLoading] = useState(true)
  const [showCreateAccount, setShowCreateAccount] = useState(false)
  const [capital, setCapital] = useState('')
  const [payout, setPayout] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [accountData, sessionsData] = await Promise.all([
        getAccount(),
        getSessions(),
      ])
      setAccount(accountData)
      setSessions(sessionsData)
      setIsBlocked(false)
    } catch (error) {
      if (error.response?.status === 404) {
        setShowCreateAccount(true)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleCreateAccount = async (e) => {
    e.preventDefault()
    try {
      await createAccount(parseFloat(capital), parseFloat(payout) / 100)
      addToast(t('common.success'), 'success')
      loadData()
      setShowCreateAccount(false)
    } catch (error) {
      addToast(error.response?.data?.detail || t('common.error'), 'error')
    }
  }

  if (loading) {
    return <div className={styles.loading}>{t('common.loading')}</div>
  }

  if (showCreateAccount) {
    return (
      <div className={styles.container}>
        <Card title={t('dashboard.createAccount')}>
          <form className={styles.form} onSubmit={handleCreateAccount}>
            <Input
              label={t('dashboard.initialCapital')}
              type="number"
              step="0.01"
              value={capital}
              onChange={(e) => setCapital(e.target.value)}
              required
            />
            <Input
              label={t('dashboard.payoutPercent')}
              type="number"
              step="1"
              min="80"
              max="92"
              value={payout}
              onChange={(e) => setPayout(e.target.value)}
              required
            />
            <Button type="submit">{t('common.save')}</Button>
          </form>
        </Card>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>{t('dashboard.title')}</h1>
      {isBlocked ? (
        <BlockedWarning />
      ) : (
        <>
          <DashboardSummary account={account} sessions={sessions} />
          <div className={styles.actions}>
            <Button onClick={() => navigate('/sessions')}>
              {t('sessions.title')}
            </Button>
            <Button onClick={() => navigate('/reports')} variant="secondary">
              {t('reports.title')}
            </Button>
          </div>
        </>
      )}
    </div>
  )
}
