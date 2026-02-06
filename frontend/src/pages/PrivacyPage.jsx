import React from 'react';
import { useTranslation } from 'react-i18next';
import styles from './StaticPage.module.css';

const PrivacyPage = () => {
  const { i18n } = useTranslation();
  const isES = i18n.language === 'es';

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <h1 className={styles.title}>{isES ? 'Política de Privacidad' : 'Privacy Policy'}</h1>
        <p className={styles.date}>{isES ? 'Última actualización: febrero 2026' : 'Last updated: February 2026'}</p>

        {isES ? (
          <>
            <h2 className={styles.section}>1. Información que recopilamos</h2>
            <p className={styles.text}>
              Recopilamos únicamente la información necesaria para el funcionamiento de la aplicación: dirección de correo electrónico y contraseña (almacenada cifrada mediante bcrypt). No recopilamos datos personales adicionales ni información de pago directamente.
            </p>

            <h2 className={styles.section}>2. Cómo usamos la información</h2>
            <p className={styles.text}>
              Tu correo electrónico se utiliza exclusivamente para identificar tu cuenta y permitir el inicio de sesión. No se comparte con terceros ni se utiliza para marketing.
            </p>

            <h2 className={styles.section}>3. Almacenamiento y seguridad</h2>
            <p className={styles.text}>
              Los datos se almacenan en servidores seguros. Las contraseñas se cifran con bcrypt antes de ser guardadas. El token de autenticación se almacena localmente en tu dispositivo y tiene una vida útil limitada.
            </p>
            <p className={styles.text}>
              <strong>Nota de riesgo:</strong> El token de sesión se almacena en localStorage del navegador. Aunque esto es necesario para la compatibilidad con la versión móvil (Android/Capacitor), te recomendamos no usar esta aplicación en dispositivos compartidos o redes públicas no confiables.
            </p>

            <h2 className={styles.section}>4. Derechos del usuario</h2>
            <p className={styles.text}>
              Puedes solicitar la eliminación de tu cuenta y todos los datos asociados en cualquier momento escribiendo a nuestro soporte. Responderemos en un plazo máximo de 30 días.
            </p>

            <h2 className={styles.section}>5. Cookies</h2>
            <p className={styles.text}>
              No utilizamos cookies de terceros ni rastreadores publicitarios. El almacenamiento local se usa únicamente para mantener tu sesión activa.
            </p>

            <h2 className={styles.section}>6. Cambios en esta política</h2>
            <p className={styles.text}>
              Si modificamos esta política, te notificaremos dentro de la aplicación. El uso continuo de la aplicación implica aceptación de los cambios.
            </p>
          </>
        ) : (
          <>
            <h2 className={styles.section}>1. Information We Collect</h2>
            <p className={styles.text}>
              We collect only the information necessary for the app to function: your email address and password (stored hashed using bcrypt). We do not collect additional personal data or payment information directly.
            </p>

            <h2 className={styles.section}>2. How We Use Your Information</h2>
            <p className={styles.text}>
              Your email is used solely to identify your account and enable login. It is not shared with third parties or used for marketing purposes.
            </p>

            <h2 className={styles.section}>3. Storage and Security</h2>
            <p className={styles.text}>
              Data is stored on secure servers. Passwords are hashed with bcrypt before being saved. Your authentication token is stored locally on your device and has a limited lifespan.
            </p>
            <p className={styles.text}>
              <strong>Risk note:</strong> The session token is stored in the browser's localStorage. While this is required for mobile (Android/Capacitor) compatibility, we recommend not using this app on shared devices or untrusted public networks.
            </p>

            <h2 className={styles.section}>4. User Rights</h2>
            <p className={styles.text}>
              You may request the deletion of your account and all associated data at any time by contacting our support. We will respond within 30 days.
            </p>

            <h2 className={styles.section}>5. Cookies</h2>
            <p className={styles.text}>
              We do not use third-party cookies or advertising trackers. Local storage is used only to maintain your active session.
            </p>

            <h2 className={styles.section}>6. Changes to This Policy</h2>
            <p className={styles.text}>
              If we update this policy, you will be notified within the app. Continued use implies acceptance of changes.
            </p>
          </>
        )}
      </div>
    </div>
  );
};

export default PrivacyPage;