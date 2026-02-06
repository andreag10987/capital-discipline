import styles from './Card.module.css'

export default function Card({ children, title, ...props }) {
  return (
    <div className={styles.card} {...props}>
      {title && <h3 className={styles.title}>{title}</h3>}
      {children}
    </div>
  )
}