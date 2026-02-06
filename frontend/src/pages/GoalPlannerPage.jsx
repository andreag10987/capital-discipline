import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { getAccount } from '../services/account'
import { getGoal, createOrUpdateGoal, deleteGoal, calculatePlan } from '../services/goalPlanner'
import { useToastStore } from '../store/toastStore'
import GoalForm from '../components/goalPlanner/GoalForm'
import PlanCalculator from '../components/goalPlanner/PlanCalculator'
import PlanResults from '../components/goalPlanner/PlanResults'
import styles from './GoalPlannerPage.module.css'

export default function GoalPlannerPage() {
  const { t } = useTranslation()
  const { addToast } = useToastStore()
  const [account, setAccount] = useState(null)
  const [goal, setGoal] = useState(null)
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const accountData = await getAccount()
      setAccount(accountData)
      
      const goalData = await getGoal()
      setGoal(goalData)
    } catch (error) {
      if (error.response?.status !== 404) {
        addToast(t('common.error'), 'error')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleCreateGoal = async (targetCapital) => {
    try {
      const newGoal = await createOrUpdateGoal(targetCapital)
      setGoal(newGoal)
      addToast(t('common.success'), 'success')
    } catch (error) {
      addToast(error.response?.data?.detail || t('common.error'), 'error')
    }
  }

  const handleDeleteGoal = async () => {
    try {
      await deleteGoal()
      setGoal(null)
      setPlan(null)
      addToast(t('common.success'), 'success')
    } catch (error) {
      addToast(error.response?.data?.detail || t('common.error'), 'error')
    }
  }

  const handleCalculatePlan = async (planData) => {
    try {
      const calculatedPlan = await calculatePlan(planData)
      setPlan(calculatedPlan)
      addToast(t('common.success'), 'success')
    } catch (error) {
      addToast(error.response?.data?.detail || t('common.error'), 'error')
    }
  }

  if (loading) {
    return <div className={styles.loading}>{t('common.loading')}</div>
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>{t('goalPlanner.title')}</h1>
      
      <div className={styles.grid}>
        <div className={styles.left}>
          <GoalForm
            currentGoal={goal}
            currentCapital={account?.capital}
            onSubmit={handleCreateGoal}
            onDelete={handleDeleteGoal}
          />
          
          <PlanCalculator onCalculate={handleCalculatePlan} />
        </div>

        <div className={styles.right}>
          <PlanResults plan={plan} />
        </div>
      </div>
    </div>
  )
}