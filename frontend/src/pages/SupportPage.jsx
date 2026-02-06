import React from 'react';
import { useTranslation } from 'react-i18next';
import styles from './StaticPage.module.css';

const SupportPage = () => {
  const { i18n } = useTranslation();
  const isES = i18n.language === 'es';

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <h1 className={styles.title}>{isES ? 'Soporte' : 'Support'}</h1>

        {isES ? (
          <>
            <h2 className={styles.section}>Preguntas frecuentes</h2>

            <div className={styles.faq}>
              <h3 className={styles.faqQ}>¿Cómo cambio mi contraseña?</h3>
              <p className={styles.faqA}>Esta funcionalidad estará disponible próximamente. Por ahora, elimina tu cuenta y crea una nueva.</p>
            </div>
            <div className={styles.faq}>
              <h3 className={styles.faqQ}>¿Por qué mi día de trading se bloqueó?</h3>
              <p className={styles.faqA}>El día se bloquea automáticamente al acumular 4 pérdidas consecutivas o al superar un drawdown del 10%. Es un mecanismo de protección psicológica. El bloqueo se levanta a las 6:00 AM.</p>
            </div>
            <div className={styles.faq}>
              <h3 className={styles.faqQ}>¿Puedo tener más de un objetivo activo?</h3>
              <p className={styles.faqA}>No. Solo se permite un objetivo activo a la vez por cuenta. Puedes pausar o completar el actual antes de crear uno nuevo. El historial de objetivos anteriores se conserva.</p>
            </div>
            <div className={styles.faq}>
              <h3 className={styles.faqQ}>¿Qué planes de suscripción hay disponibles?</h3>
              <p className={styles.faqA}>Los planes (FREE, BASIC, PRO) se lanzarán próximamente. La versión actual incluye todas las funcionalidades de forma gratuita durante la fase beta.</p>
            </div>
            <div className={styles.faq}>
              <h3 className={styles.faqQ}>¿Cómo elimino mi cuenta?</h3>
              <p className={styles.faqA}>Contáctanos por correo electrónico (ver abajo) solicitando la eliminación. Procesaremos la solicitud en máximo 30 días.</p>
            </div>

            <h2 className={styles.section}>Contacto</h2>
            <p className={styles.text}>
              Si tienes dudas que no están cubiertas aquí, no dudes en escribirnos:
            </p>
            <div className={styles.contactBlock}>
              <p className={styles.contactItem}><strong>Email:</strong> soporte@capitalmanager.app</p>
              <p className={styles.contactItem}><strong>Tiempo de respuesta:</strong> 24–48 horas</p>
            </div>
          </>
        ) : (
          <>
            <h2 className={styles.section}>Frequently Asked Questions</h2>

            <div className={styles.faq}>
              <h3 className={styles.faqQ}>How do I change my password?</h3>
              <p className={styles.faqA}>This feature will be available soon. For now, delete your account and create a new one.</p>
            </div>
            <div className={styles.faq}>
              <h3 className={styles.faqQ}>Why was my trading day blocked?</h3>
              <p className={styles.faqA}>The day is automatically blocked after 4 consecutive losses or when the drawdown exceeds 10%. This is a psychological protection mechanism. The block lifts at 6:00 AM.</p>
            </div>
            <div className={styles.faq}>
              <h3 className={styles.faqQ}>Can I have more than one active goal?</h3>
              <p className={styles.faqA}>No. Only one active goal per account is allowed at a time. You can pause or complete the current one before creating a new one. Your goal history is preserved.</p>
            </div>
            <div className={styles.faq}>
              <h3 className={styles.faqQ}>What subscription plans are available?</h3>
              <p className={styles.faqA}>Plans (FREE, BASIC, PRO) will launch soon. The current version includes all features for free during the beta phase.</p>
            </div>
            <div className={styles.faq}>
              <h3 className={styles.faqQ}>How do I delete my account?</h3>
              <p className={styles.faqA}>Contact us via email (see below) requesting deletion. We will process the request within 30 days.</p>
            </div>

            <h2 className={styles.section}>Contact</h2>
            <p className={styles.text}>
              If you have questions not covered here, feel free to reach out:
            </p>
            <div className={styles.contactBlock}>
              <p className={styles.contactItem}><strong>Email:</strong> support@capitalmanager.app</p>
              <p className={styles.contactItem}><strong>Response time:</strong> 24–48 hours</p>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default SupportPage;