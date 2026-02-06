import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import Card from '../common/Card'
import Button from '../common/Button'
import styles from './SessionList.module.css'

export default function SessionList({ sessions }) {
  const { t } = useTranslation()
  const navigate = useNavigate()

  return (
    <div className={styles.list}>
      {sessions.map((session) => (
        <Card key={session.id}>
          <div className={styles.session}>
            <div className={styles.info}>
              <h3 className={styles.title}>
                {t('sessions.sessionNumber')} {session.session_number}
              </h3>
              <div className={styles.details}>
                <span className={`${styles.status} ${styles[session.status]}`}>
                  {session.status}
                </span>
                <span>{t('sessions.losses')}: {session.loss_count}/2</span>
              </div>
            </div>
            <Button onClick={() => navigate(`/operations/${session.id}`)}>
              {t('sessions.viewOperations')}
            </Button>
          </div>
        </Card>
      ))}
    </div>
  )
}