import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import Modal from '../common/Modal'
import Button from '../common/Button'
import styles from './CreateSessionModal.module.css'

export default function CreateSessionModal({ isOpen, onClose, onCreate }) {
  const { t } = useTranslation()
  const [risk, setRisk] = useState(2)
  const [loading, setLoading] = useState(false)

  const handleCreate = async () => {
    setLoading(true)
    await onCreate(risk)
    setLoading(false)
    onClose()
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t('sessions.createSession')}>
      <div className={styles.content}>
        <p className={styles.label}>{t('sessions.selectRisk')}</p>
        <div className={styles.riskOptions}>
          <button
            className={`${styles.riskButton} ${risk === 2 ? styles.active : ''}`}
            onClick={() => setRisk(2)}
          >
            2%
          </button>
          <button
            className={`${styles.riskButton} ${risk === 3 ? styles.active : ''}`}
            onClick={() => setRisk(3)}
          >
            3%
          </button>
        </div>
        <div className={styles.actions}>
          <Button variant="secondary" onClick={onClose}>
            {t('common.cancel')}
          </Button>
          <Button onClick={handleCreate} disabled={loading}>
            {loading ? t('common.loading') : t('common.confirm')}
          </Button>
        </div>
      </div>
    </Modal>
  )
}