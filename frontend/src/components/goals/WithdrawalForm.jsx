import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import withdrawalsService from '../../services/withdrawals';
import { useAccountStore } from '../../store/accountStore';
import styles from './WithdrawalForm.module.css';

const WithdrawalForm = ({ onWithdrawalCreated }) => {
  const { t } = useTranslation();
  const { account, fetchAccount } = useAccountStore();
  const [amount, setAmount] = useState('');
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetchAccount();
  }, []);

  const validate = () => {
    if (!amount || Number(amount) <= 0) {
      setError(t('withdrawals.errors.amountRequired'));
      return false;
    }
    if (account && Number(amount) > account.capital) {
      setError(t('withdrawals.errors.insufficientCapital'));
      return false;
    }
    setError(null);
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      await withdrawalsService.createWithdrawal({
        amount: Number(amount),
        note: note || null,
      });
      setAmount('');
      setNote('');
      setShowForm(false);
      await fetchAccount();
      if (onWithdrawalCreated) onWithdrawalCreated();
    } catch (err) {
      setError(err.response?.data?.detail || t('withdrawals.errors.createFailed'));
    } finally {
      setLoading(false);
    }
  };

  if (!showForm) {
    return (
      <button className={styles.toggleButton} onClick={() => setShowForm(true)}>
        💰 {t('withdrawals.registerNew')}
      </button>
    );
  }

  return (
    <div className={styles.formContainer}>
      <div className={styles.formHeader}>
        <h3 className={styles.formTitle}>{t('withdrawals.title')}</h3>
        <button className={styles.closeBtn} onClick={() => { setShowForm(false); setError(null); }}>✕</button>
      </div>

      {error && <div className={styles.errorBox}>{error}</div>}

      <form onSubmit={handleSubmit} className={styles.form}>
        <div className={styles.fieldGroup}>
          <label className={styles.label}>{t('withdrawals.amount')}</label>
          <div className={styles.inputWrapper}>
            <span className={styles.symbol}>$</span>
            <input
              type="number"
              value={amount}
              onChange={(e) => { setAmount(e.target.value); setError(null); }}
              placeholder="100"
              min="0.01"
              step="0.01"
              className={`${styles.input} ${error ? styles.inputError : ''}`}
            />
          </div>
          {account && (
            <span className={styles.hint}>
              {t('withdrawals.available')}: ${account.capital.toFixed(2)}
            </span>
          )}
        </div>

        <div className={styles.fieldGroup}>
          <label className={styles.label}>{t('withdrawals.note')} ({t('common.optional')})</label>
          <input
            type="text"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder={t('withdrawals.notePlaceholder')}
            className={styles.input}
            maxLength={500}
          />
        </div>

        <div className={styles.buttons}>
          <button type="button" className={styles.cancelBtn} onClick={() => { setShowForm(false); setError(null); }}>
            {t('common.cancel')}
          </button>
          <button type="submit" className={styles.submitBtn} disabled={loading}>
            {loading ? t('common.loading') : t('withdrawals.confirm')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default WithdrawalForm;