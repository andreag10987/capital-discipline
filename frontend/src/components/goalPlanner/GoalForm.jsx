import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import Card from '../common/Card'
import Input from '../common/Input'
import Button from '../common/Button'
import styles from './GoalForm.module.css'

export default function GoalForm({ currentGoal, currentCapital, onSubmit, onDelete }) {
  const { t } = useTranslation()
  const [targetCapital, setTargetCapital] = useState(currentGoal?.target_capital || '')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    await onSubmit(parseFloat(targetCapital))
    setLoading(false)
  }

  const handleDelete = async () => {
    if (window.confirm(t('goalPlanner.confirmDelete'))) {
      await onDelete()
    }
  }

  return (
    <Card title={t('goalPlanner.setGoal')}>
      <form className={styles.form} onSubmit={handleSubmit}>
        <div className={styles.info}>
          <span className={styles.label}>{t('goalPlanner.currentCapital')}:</span>
          <span className={styles.value}>${currentCapital?.toFixed(2)}</span>
        </div>

        <Input
  label={t('goalPlanner.targetCapital')}
  type="number"
  step="any"  // ← CAMBIADO
  min={currentCapital ? currentCapital + 0.01 : 0}
  value={targetCapital}
  onChange={(e) => setTargetCapital(e.target.value)}
  required
/>

        {currentGoal && (
          <div className={styles.progress}>
            <span className={styles.progressLabel}>{t('goalPlanner.progress')}</span>
            <div className={styles.progressBar}>
              <div 
                className={styles.progressFill} 
                style={{ width: `${Math.min(currentGoal.progress_percent, 100)}%` }}
              />
            </div>
            <span className={styles.progressValue}>{currentGoal.progress_percent.toFixed(1)}%</span>
          </div>
        )}

        <div className={styles.actions}>
          <Button type="submit" disabled={loading}>
            {loading ? t('common.loading') : (currentGoal ? t('common.save') : t('goalPlanner.createGoal'))}
          </Button>
          {currentGoal && (
            <Button variant="danger" type="button" onClick={handleDelete}>
              {t('goalPlanner.deleteGoal')}
            </Button>
          )}
        </div>
      </form>
    </Card>
  )
}