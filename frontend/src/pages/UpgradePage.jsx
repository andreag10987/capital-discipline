import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import PlanCard from '../components/plans/PlanCard';
import { useToastStore } from '../store/toastStore';
import styles from './UpgradePage.module.css';

const UpgradePage = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const showToast = useToastStore((state) => state.showToast);
  const isES = i18n.language === 'es';

  const [plans, setPlans] = useState([]);
  const [currentPlan, setCurrentPlan] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      // TODO: Implementar endpoint /plans en backend
      // Por ahora, datos mockeados
      const mockPlans = [
        {
          id: 1,
          name: 'FREE',
          display_name_es: 'Gratis',
          display_name_en: 'Free',
          price_usd: 0,
          features: {
            max_daily_sessions: 1,
            max_ops_per_session: 3,
            max_active_goals: 1,
            history_days: 3,
            can_export_pdf: false,
            can_export_excel: false,
            can_see_projections: false,
            can_recalculate_withdrawals: false
          }
        },
        {
          id: 2,
          name: 'BASIC',
          display_name_es: 'Básico',
          display_name_en: 'Basic',
          price_usd: 10,
          features: {
            max_daily_sessions: 2,
            max_ops_per_session: 5,
            max_active_goals: 1,
            history_days: 30,
            can_export_pdf: false,
            can_export_excel: false,
            can_see_projections: true,
            can_recalculate_withdrawals: false
          }
        },
        {
          id: 3,
          name: 'PRO',
          display_name_es: 'Pro',
          display_name_en: 'Pro',
          price_usd: 20,
          features: {
            max_daily_sessions: 999,
            max_ops_per_session: 999,
            max_active_goals: 999,
            history_days: 999,
            can_export_pdf: true,
            can_export_excel: true,
            can_see_projections: true,
            can_recalculate_withdrawals: true
          }
        }
      ];

      setPlans(mockPlans);
      setCurrentPlan('FREE'); // Por ahora todos son FREE
      setLoading(false);
    } catch (error) {
      console.error('Error fetching plans:', error);
      showToast(isES ? 'Error al cargar planes' : 'Error loading plans', 'error');
      setLoading(false);
    }
  };

  const handleUpgrade = (plan) => {
    if (plan.name === 'FREE') {
      showToast(
        isES 
          ? 'Ya estás en el plan gratuito' 
          : 'You are already on the free plan',
        'info'
      );
      return;
    }

    // TODO: Integrar con Google Play Billing en Etapa 6
    showToast(
      isES 
        ? `Compras dentro de la app estarán disponibles próximamente. Plan seleccionado: ${plan.display_name_es}` 
        : `In-app purchases coming soon. Selected plan: ${plan.display_name_en}`,
      'info'
    );
  };

  if (loading) {
    return (
      <div className={styles.page}>
        <div className={styles.loading}>
          {isES ? 'Cargando planes...' : 'Loading plans...'}
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>
          {isES ? 'Elige tu Plan' : 'Choose Your Plan'}
        </h1>
        <p className={styles.subtitle}>
          {isES 
            ? 'Mejora tu experiencia con más funcionalidades y límites más altos'
            : 'Upgrade your experience with more features and higher limits'
          }
        </p>
      </div>

      <div className={styles.plansGrid}>
        {plans.map((plan) => (
          <PlanCard
            key={plan.id}
            plan={plan}
            isCurrentPlan={plan.name === currentPlan}
            onUpgrade={handleUpgrade}
          />
        ))}
      </div>

      <div className={styles.footer}>
        <button onClick={() => navigate('/')} className={styles.backButton}>
          {isES ? '← Volver al Dashboard' : '← Back to Dashboard'}
        </button>
      </div>
    </div>
  );
};

export default UpgradePage;