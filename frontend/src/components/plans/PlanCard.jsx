import React from 'react';
import { useTranslation } from 'react-i18next';
import styles from './PlanCard.module.css';

const PlanCard = ({ plan, isCurrentPlan, onUpgrade }) => {
  const { i18n } = useTranslation();
  const isES = i18n.language === 'es';
  
  const displayName = isES ? plan.display_name_es : plan.display_name_en;
  const features = plan.features;
  
  const getFeatureLabel = (key, value) => {
    const labels = {
      max_daily_sessions: isES ? 'Sesiones diarias' : 'Daily sessions',
      max_ops_per_session: isES ? 'Operaciones por sesión' : 'Operations per session',
      max_active_goals: isES ? 'Objetivos activos' : 'Active goals',
      history_days: isES ? 'Historial (días)' : 'History (days)',
      can_export_pdf: isES ? 'Exportar PDF' : 'Export PDF',
      can_export_excel: isES ? 'Exportar Excel' : 'Export Excel',
      can_see_projections: isES ? 'Proyecciones' : 'Projections',
      can_recalculate_withdrawals: isES ? 'Recalcular retiros' : 'Recalculate withdrawals'
    };
    
    const label = labels[key] || key;
    
    if (typeof value === 'boolean') {
      return `${value ? '✓' : '✗'} ${label}`;
    }
    if (value === 999) {
      return `${label}: ${isES ? 'Ilimitado' : 'Unlimited'}`;
    }
    return `${label}: ${value}`;
  };

  return (
    <div className={`${styles.card} ${isCurrentPlan ? styles.current : ''} ${plan.name === 'PRO' ? styles.featured : ''}`}>
      {plan.name === 'PRO' && (
        <div className={styles.badge}>{isES ? 'Más Popular' : 'Most Popular'}</div>
      )}
      
      <div className={styles.header}>
        <h3 className={styles.name}>{displayName}</h3>
        <div className={styles.price}>
          <span className={styles.currency}>$</span>
          <span className={styles.amount}>{plan.price_usd.toFixed(0)}</span>
          <span className={styles.period}>/{isES ? 'mes' : 'month'}</span>
        </div>
      </div>

      <ul className={styles.features}>
        {Object.entries(features).map(([key, value]) => (
          <li key={key} className={styles.feature}>
            {getFeatureLabel(key, value)}
          </li>
        ))}
      </ul>

      <div className={styles.actions}>
        {isCurrentPlan ? (
          <button className={styles.currentButton} disabled>
            {isES ? 'Plan Actual' : 'Current Plan'}
          </button>
        ) : (
          <button 
            className={styles.upgradeButton}
            onClick={() => onUpgrade(plan)}
          >
            {plan.price_usd === 0 
              ? (isES ? 'Cambiar a Free' : 'Switch to Free')
              : (isES ? 'Actualizar' : 'Upgrade')
            }
          </button>
        )}
      </div>
    </div>
  );
};

export default PlanCard;