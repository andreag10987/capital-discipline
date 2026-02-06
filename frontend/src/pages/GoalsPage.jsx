import React, { useState, useCallback, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAccountStore } from '../store/accountStore';
import GoalManager from '../components/goals/GoalManager';
import CalendarView from '../components/goals/CalendarView';
import WithdrawalForm from '../components/goals/WithdrawalForm';
import WithdrawalList from '../components/goals/WithdrawalList';
import ReportDownload from '../components/goals/ReportDownload';
import styles from './GoalsPage.module.css';

const GoalsPage = () => {
  const { t } = useTranslation();
  const { fetchAccount } = useAccountStore();
  const [activeGoalId, setActiveGoalId] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [withdrawalRefresh, setWithdrawalRefresh] = useState(0);

  useEffect(() => {
    fetchAccount();
  }, []);

  // Se llama cuando GoalManager detecta un objetivo activo (al cargar o crear)
  const handleActiveGoalChange = useCallback((goalId) => {
    setActiveGoalId(goalId);
    if (!goalId) setActiveTab('overview');
  }, []);

  const handleGoalCreated = useCallback((goal) => {
    setActiveGoalId(goal.id);
    setActiveTab('overview');
  }, []);

  const handleGoalDeleted = useCallback(() => {
    setActiveGoalId(null);
    setActiveTab('overview');
  }, []);

  const handleWithdrawalCreated = useCallback(() => {
    setWithdrawalRefresh(prev => prev + 1);
    fetchAccount();
  }, []);

  const tabs = [
    { id: 'overview', label: t('goals.tabs.overview'), icon: '📈' },
    { id: 'calendar', label: t('goals.tabs.calendar'), icon: '📅' },
    { id: 'withdrawals', label: t('goals.tabs.withdrawals'), icon: '💰' },
  ];

  return (
    <div className={styles.page}>
      <div className={styles.pageHeader}>
        <h1 className={styles.pageTitle}>{t('goals.pageTitle')}</h1>
        <p className={styles.pageSubtitle}>{t('goals.pageSubtitle')}</p>
      </div>

      <div className={styles.content}>
        <GoalManager
          onGoalCreated={handleGoalCreated}
          onGoalDeleted={handleGoalDeleted}
          onActiveGoalChange={handleActiveGoalChange}
        />

        {/* Tabs solo si hay objetivo activo */}
        {activeGoalId && (
          <div className={styles.tabSection}>
            <div className={styles.tabs}>
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  className={`${styles.tab} ${activeTab === tab.id ? styles.tabActive : ''}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  <span className={styles.tabIcon}>{tab.icon}</span>
                  <span className={styles.tabLabel}>{tab.label}</span>
                </button>
              ))}
            </div>

            <div className={styles.tabContent}>
              {activeTab === 'overview' && (
                <div className={styles.overviewTab}>
                  <ReportDownload goalId={activeGoalId} />
                </div>
              )}

              {activeTab === 'calendar' && (
                <CalendarView goalId={activeGoalId} />
              )}

              {activeTab === 'withdrawals' && (
                <div className={styles.withdrawalsTab}>
                  <WithdrawalForm onWithdrawalCreated={handleWithdrawalCreated} />
                  <WithdrawalList
                    goalId={activeGoalId}
                    refreshKey={withdrawalRefresh}
                  />
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GoalsPage;