import { useToastStore } from '../../store/toastStore'
import styles from './Toast.module.css'

export default function Toast() {
  const { toasts, removeToast } = useToastStore()

  return (
    <div className={styles.container}>
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`${styles.toast} ${styles[toast.type]}`}
          onClick={() => removeToast(toast.id)}
        >
          {toast.message}
        </div>
      ))}
    </div>
  )
}