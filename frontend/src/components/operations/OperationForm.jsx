import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import Card from '../common/Card'
import Button from '../common/Button'
import Input from '../common/Input'
import styles from './OperationForm.module.css'

const PREDEFINED_COMMENTS = [
  'Entrada tardía',
  'No esperé confirmación',
  'Contra tendencia',
  'Señal débil',
  'Gestión emocional deficiente'
]

export default function OperationForm({ sessionId, onSubmit }) {
  const { t } = useTranslation()
  const [result, setResult] = useState('WIN')
  const [risk, setRisk] = useState(2)
  const [comment, setComment] = useState('')
  const [useCustomComment, setUseCustomComment] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    await onSubmit({
      session_id: sessionId,
      result,
      risk_percent: risk,
      comment: comment || undefined
    })
    setLoading(false)
    setComment('')
    setUseCustomComment(false)
  }

  return (
    <Card title={t('operations.addOperation')}>
      <form className={styles.form} onSubmit={handleSubmit}>
        <div className={styles.field}>
          <label className={styles.label}>{t('operations.result')}</label>
          <div className={styles.resultOptions}>
            <button
              type="button"
              className={`${styles.resultButton} ${styles.win} ${result === 'WIN' ? styles.active : ''}`}
              onClick={() => setResult('WIN')}
            >
              {t('operations.win')}
            </button>
            <button
              type="button"
              className={`${styles.resultButton} ${styles.loss} ${result === 'LOSS' ? styles.active : ''}`}
              onClick={() => setResult('LOSS')}
            >
              {t('operations.loss')}
            </button>
            <button
              type="button"
              className={`${styles.resultButton} ${styles.draw} ${result === 'DRAW' ? styles.active : ''}`}
              onClick={() => setResult('DRAW')}
            >
              {t('operations.draw')}
            </button>
          </div>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>{t('operations.risk')}</label>
          <div className={styles.riskOptions}>
            <button
              type="button"
              className={`${styles.riskButton} ${risk === 2 ? styles.active : ''}`}
              onClick={() => setRisk(2)}
            >
              2%
            </button>
            <button
              type="button"
              className={`${styles.riskButton} ${risk === 3 ? styles.active : ''}`}
              onClick={() => setRisk(3)}
            >
              3%
            </button>
          </div>
        </div>

        {(result === 'LOSS' || result === 'DRAW' || result === 'WIN') && (
          <div className={styles.field}>
            <label className={styles.label}>{t('operations.comment')}</label>
            
            {result === 'LOSS' && (
              <>
                {!useCustomComment ? (
                  <>
                    <div className={styles.predefinedComments}>
                      {PREDEFINED_COMMENTS.map((c) => (
                        <button
                          key={c}
                          type="button"
                          className={`${styles.commentButton} ${comment === c ? styles.active : ''}`}
                          onClick={() => setComment(c)}
                        >
                          {c}
                        </button>
                      ))}
                    </div>
                    <button
                      type="button"
                      className={styles.customButton}
                      onClick={() => setUseCustomComment(true)}
                    >
                      {t('operations.customComment')}
                    </button>
                  </>
                ) : (
                  <Input
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    placeholder={t('operations.comment')}
                    required
                  />
                )}
              </>
            )}
            
            {result !== 'LOSS' && (
              <Input
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder={t('operations.comment')}
              />
            )}
          </div>
        )}

        <Button type="submit" disabled={loading || (result === 'LOSS' && !comment)}>
          {loading ? t('common.loading') : t('common.save')}
        </Button>
      </form>
    </Card>
  )
}