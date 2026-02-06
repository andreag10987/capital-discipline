import { useTranslation } from 'react-i18next'
import Card from '../common/Card'
import styles from './BlockedWarning.module.css'

export default function BlockedWarning() {
  const { t } = useTranslation()

  return (
    <Card>
      <div className={styles.blocked}>
        <h2 className={styles.title}>{t('blocked.title')}</h2>
        <p className={styles.subtitle}>{t('blocked.subtitle')}</p>
        
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>{t('blocked.psychoTips')}</h3>
          <ul className={styles.list}>
            <li>{t('blocked.tip1')}</li>
            <li>{t('blocked.tip2')}</li>
            <li>{t('blocked.tip3')}</li>
          </ul>
        </div>

        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>{t('blocked.activities')}</h3>
          <ul className={styles.list}>
            <li>{t('blocked.activity1')}</li>
            <li>{t('blocked.activity2')}</li>
            <li>{t('blocked.activity3')}</li>
            <li>{t('blocked.activity4')}</li>
          </ul>
        </div>
      </div>
    </Card>
  )
}