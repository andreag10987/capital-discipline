import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styles from './GoalForm.module.css';

const GoalForm = ({ account, onSubmit, onCancel }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    target_capital: '',
    risk_percent: 2,
    sessions_per_day: 2,
    ops_per_session: 5,
    winrate_estimate: 0.60,
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const currentCapital = account ? account.capital : 0;
  const payout = account ? account.payout : 0.85;

  const validate = () => {
    const newErrors = {};
    if (!formData.target_capital || Number(formData.target_capital) <= 0) {
      newErrors.target_capital = t('goals.errors.targetRequired');
    } else if (Number(formData.target_capital) <= currentCapital) {
      newErrors.target_capital = t('goals.errors.targetMustBeGreater');
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => { const updated = { ...prev }; delete updated[name]; return updated; });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      await onSubmit({
        target_capital: Number(formData.target_capital),
        risk_percent: Number(formData.risk_percent),
        sessions_per_day: Number(formData.sessions_per_day),
        ops_per_session: Number(formData.ops_per_session),
        winrate_estimate: Number(formData.winrate_estimate),
      });
    } catch (error) {
      setErrors({ form: error.response?.data?.detail || t('goals.errors.createFailed') });
    } finally {
      setLoading(false);
    }
  };

  // Preview cálculos en tiempo real
  const stake = currentCapital * (formData.risk_percent / 100);
  const opsPerDay = Number(formData.sessions_per_day) * Number(formData.ops_per_session);
  const wr = Number(formData.winrate_estimate);
  const expectedReturn = wr * payout - (1 - wr);
  const dailyGrowth = 1 + (Number(formData.risk_percent) / 100) * opsPerDay * expectedReturn;
  const targetNum = Number(formData.target_capital) || 0;
  const daysToGoal = dailyGrowth > 1 && targetNum > currentCapital
    ? Math.ceil(Math.log(targetNum / currentCapital) / Math.log(dailyGrowth))
    : null;

  return (
    <div className={styles.formContainer}>
      <h2 className={styles.title}>{t('goals.createTitle')}</h2>
      {errors.form && <div className={styles.errorBanner}>{errors.form}</div>}

      <form onSubmit={handleSubmit} className={styles.form}>
        {/* Capital Objetivo */}
        <div className={styles.fieldGroup}>
          <label className={styles.label}>{t('goals.fields.targetCapital')}</label>
          <div className={styles.inputWrapper}>
            <span className={styles.currencySymbol}>$</span>
            <input
              type="number"
              name="target_capital"
              value={formData.target_capital}
              onChange={handleChange}
              placeholder="2000"
              className={`${styles.input} ${errors.target_capital ? styles.inputError : ''}`}
              step="0.01"
            />
          </div>
          {errors.target_capital && <span className={styles.error}>{errors.target_capital}</span>}
          <span className={styles.hint}>{t('goals.currentCapital')}: ${currentCapital.toFixed(2)}</span>
        </div>

        {/* Riesgo */}
        <div className={styles.fieldGroup}>
          <label className={styles.label}>{t('goals.fields.riskPercent')}</label>
          <div className={styles.radioGroup}>
            {[2, 3].map(val => (
              <label key={val} className={`${styles.radioLabel} ${Number(formData.risk_percent) === val ? styles.radioActive : ''}`}>
                <input
                  type="radio"
                  name="risk_percent"
                  value={val}
                  checked={Number(formData.risk_percent) === val}
                  onChange={handleChange}
                  className={styles.radioInput}
                />
                <span className={styles.radioText}>{val}%</span>
              </label>
            ))}
          </div>
        </div>

        {/* Sesiones por día */}
        <div className={styles.fieldGroup}>
          <label className={styles.label}>{t('goals.fields.sessionsPerDay')}</label>
          <div className={styles.radioGroup}>
            {[2, 3].map(val => (
              <label key={val} className={`${styles.radioLabel} ${Number(formData.sessions_per_day) === val ? styles.radioActive : ''}`}>
                <input
                  type="radio"
                  name="sessions_per_day"
                  value={val}
                  checked={Number(formData.sessions_per_day) === val}
                  onChange={handleChange}
                  className={styles.radioInput}
                />
                <span className={styles.radioText}>{val}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Ops por sesión */}
        <div className={styles.fieldGroup}>
          <label className={styles.label}>{t('goals.fields.opsPerSession')}</label>
          <div className={styles.radioGroup}>
            {[4, 5].map(val => (
              <label key={val} className={`${styles.radioLabel} ${Number(formData.ops_per_session) === val ? styles.radioActive : ''}`}>
                <input
                  type="radio"
                  name="ops_per_session"
                  value={val}
                  checked={Number(formData.ops_per_session) === val}
                  onChange={handleChange}
                  className={styles.radioInput}
                />
                <span className={styles.radioText}>{val}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Winrate estimado */}
        <div className={styles.fieldGroup}>
          <label className={styles.label}>
            {t('goals.fields.winrateEstimate')}: <strong>{(formData.winrate_estimate * 100).toFixed(0)}%</strong>
          </label>
          <input
            type="range"
            name="winrate_estimate"
            min="0.50"
            max="0.80"
            step="0.01"
            value={formData.winrate_estimate}
            onChange={handleChange}
            className={styles.rangeInput}
          />
          <div className={styles.rangeLabels}>
            <span>50%</span>
            <span>65%</span>
            <span>80%</span>
          </div>
        </div>

        {/* Preview */}
        <div className={styles.preview}>
          <h3 className={styles.previewTitle}>{t('goals.preview')}</h3>
          <div className={styles.previewGrid}>
            <div className={styles.previewItem}>
              <span className={styles.previewLabel}>{t('goals.preview.stake')}</span>
              <span className={styles.previewValue}>${stake.toFixed(2)}</span>
            </div>
            <div className={styles.previewItem}>
              <span className={styles.previewLabel}>{t('goals.preview.opsPerDay')}</span>
              <span className={styles.previewValue}>{opsPerDay}</span>
            </div>
            <div className={styles.previewItem}>
              <span className={styles.previewLabel}>{t('goals.preview.dailyGrowth')}</span>
              <span className={`${styles.previewValue} ${dailyGrowth > 1 ? styles.positive : styles.negative}`}>
                {((dailyGrowth - 1) * 100).toFixed(2)}%
              </span>
            </div>
            <div className={styles.previewItem}>
              <span className={styles.previewLabel}>{t('goals.preview.daysToGoal')}</span>
              <span className={styles.previewValue}>
                {daysToGoal !== null ? `${daysToGoal} ${t('goals.preview.days')}` : '—'}
              </span>
            </div>
          </div>
          {payout < 0.80 && (
            <div className={styles.warningBanner}>
              ⚠️ {t('goals.warning.lowPayout')}
            </div>
          )}
        </div>

        {/* Botones */}
        <div className={styles.buttons}>
          {onCancel && (
            <button type="button" className={styles.cancelButton} onClick={onCancel}>
              {t('common.cancel')}
            </button>
          )}
          <button type="submit" className={styles.submitButton} disabled={loading}>
            {loading ? t('common.loading') : t('goals.create')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default GoalForm;