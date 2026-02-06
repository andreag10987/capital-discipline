import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import withdrawalsService from '../../services/withdrawals';
import styles from './WithdrawalList.module.css';

const WithdrawalList = ({ goalId, refreshKey }) => {
  const { t } = useTranslation();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWithdrawals();
  }, [goalId, refreshKey]);

  const loadWithdrawals = async () => {
    try {
      setLoading(true);
      const result = await withdrawalsService.getWithdrawals(goalId);
      setData(result);
    } catch (error) {
      console.error('Error loading withdrawals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm(t('withdrawals.confirmDelete'))) return;
    try {
      await withdrawalsService.deleteWithdrawal(id);
      await loadWithdrawals();
    } catch (error) {
      console.error('Error deleting withdrawal:', error);
    }
  };

  if (loading) return <div className={styles.loading}>{t('common.loading')}</div>;
  if (!data || data.withdrawals.length === 0) {
    return <div className={styles.empty}>{t('withdrawals.noWithdrawals')}</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.summary}>
        <span className={styles.summaryText}>
          {data.count} {t('withdrawals.total')} — {t('withdrawals.totalWithdrawn')}: <strong>${data.total_withdrawn.toFixed(2)}</strong>
        </span>
      </div>

      <div className={styles.list}>
        {data.withdrawals.map((w) => (
          <div key={w.id} className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={styles.cardLeft}>
                <span className={styles.amount}>-${w.amount.toFixed(2)}</span>
                <span className={styles.date}>{new Date(w.withdrawn_at).toLocaleDateString()}</span>
              </div>
              <button className={styles.deleteBtn} onClick={() => handleDelete(w.id)} title={t('common.delete')}>
                🗑
              </button>
            </div>
            <div className={styles.cardBody}>
              <div className={styles.capitals}>
                <span className={styles.capitalItem}>
                  {t('withdrawals.before')}: <strong>${w.capital_before.toFixed(2)}</strong>
                </span>
                <span className={styles.arrow}>→</span>
                <span className={styles.capitalItem}>
                  {t('withdrawals.after')}: <strong>${w.capital_after.toFixed(2)}</strong>
                </span>
              </div>
              {w.note && <p className={styles.note}>📝 {w.note}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WithdrawalList;