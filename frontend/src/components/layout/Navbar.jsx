import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '../../store/authStore'
import Button from '../common/Button'
import styles from './Navbar.module.css'

export default function Navbar() {
  const { t, i18n } = useTranslation()
  const { logout } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const toggleLanguage = () => {
    i18n.changeLanguage(i18n.language === 'en' ? 'es' : 'en')
  }

  const navLinks = [
    { to: '/', label: t('dashboard.title') },
    { to: '/sessions', label: t('sessions.title') },
    { to: '/reports', label: t('reports.title') },
    { to: '/goal-planner', label: t('goalPlanner.title') },
    { to: '/goals', label: t('goals.pageTitle') },
  ]

  return (
    <nav className={styles.navbar}>
      <div className={styles.container}>
        <Link to="/" className={styles.brand}>
          Binary Options
        </Link>
        <div className={styles.menu}>
          {navLinks.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`${styles.link} ${location.pathname === link.to ? styles.linkActive : ''}`}
            >
              {link.label}
            </Link>
          ))}
        </div>
        <div className={styles.actions}>
          <button className={styles.langButton} onClick={toggleLanguage}>
            {i18n.language.toUpperCase()}
          </button>
          <Button variant="secondary" onClick={handleLogout}>
            {t('auth.logout')}
          </Button>
        </div>
      </div>
    </nav>
  )
}