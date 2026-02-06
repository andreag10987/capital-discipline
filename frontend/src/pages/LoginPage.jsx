import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../store/authStore';
import { useToastStore } from '../store/toastStore';
import { login } from '../services/auth';
import styles from './LoginPage.module.css';

const LoginPage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);
  const showToast = useToastStore((state) => state.showToast);

  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await login(formData.email, formData.password);
      setAuth(response.access_token);
      showToast(t('auth.loginSuccess'), 'success');
      navigate('/');
    } catch (error) {
      showToast(error.response?.data?.detail?.message || t('auth.loginError'), 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    showToast(t('auth.oauthComingSoon'), 'info');
    // TODO: Implementar Google Sign-In en Etapa 7
    // const googleUser = await signInWithGoogle();
    // const response = await fetch('/auth/google', { ... });
  };

  const handleFacebookLogin = async () => {
    showToast(t('auth.oauthComingSoon'), 'info');
    // TODO: Implementar Facebook Login en Etapa 7
    // const fbUser = await signInWithFacebook();
    // const response = await fetch('/auth/facebook', { ... });
  };

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.header}>
          <h1 className={styles.title}>{t('auth.login')}</h1>
          <p className={styles.subtitle}>{t('auth.welcomeBack')}</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.inputGroup}>
            <label className={styles.label}>{t('auth.email')}</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={styles.input}
              required
              autoComplete="email"
            />
          </div>

          <div className={styles.inputGroup}>
            <label className={styles.label}>{t('auth.password')}</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={styles.input}
              required
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className={styles.submitButton}
            disabled={loading}
          >
            {loading ? t('common.loading') : t('auth.login')}
          </button>
        </form>

        <div className={styles.divider}>
          <span className={styles.dividerText}>{t('auth.orContinueWith')}</span>
        </div>

        <div className={styles.oauthButtons}>
          <button
            type="button"
            onClick={handleGoogleLogin}
            className={styles.googleButton}
          >
            <svg className={styles.oauthIcon} viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            {t('auth.continueWithGoogle')}
          </button>

          <button
            type="button"
            onClick={handleFacebookLogin}
            className={styles.facebookButton}
          >
            <svg className={styles.oauthIcon} viewBox="0 0 24 24" fill="#1877F2">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
            </svg>
            {t('auth.continueWithFacebook')}
          </button>
        </div>

        <div className={styles.footer}>
          <p className={styles.footerText}>
            {t('auth.dontHaveAccount')}{' '}
            <Link to="/register" className={styles.link}>
              {t('auth.register')}
            </Link>
          </p>
          <div className={styles.legalLinks}>
            <Link to="/privacy" className={styles.legalLink}>{t('auth.privacy')}</Link>
            <span className={styles.separator}>•</span>
            <Link to="/disclaimer" className={styles.legalLink}>{t('auth.disclaimer')}</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;