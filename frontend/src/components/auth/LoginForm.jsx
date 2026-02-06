import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { login } from '../../services/auth'
import { useAuthStore } from '../../store/authStore'
import { useToastStore } from '../../store/toastStore'
import Input from '../common/Input'
import Button from '../common/Button'
import styles from './AuthForm.module.css'

export default function LoginForm() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const { addToast } = useToastStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const data = await login(email, password)
      setAuth(data.access_token, { email })
      addToast(t('common.success'), 'success')
      navigate('/')
    } catch (error) {
      addToast(error.response?.data?.detail || t('common.error'), 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <Input
        label={t('auth.email')}
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <Input
        label={t('auth.password')}
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <Button type="submit" disabled={loading}>
        {loading ? t('common.loading') : t('auth.loginButton')}
      </Button>
    </form>
  )
}