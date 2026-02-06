import React from 'react';
import { useTranslation } from 'react-i18next';
import styles from './StaticPage.module.css';

const DisclaimerPage = () => {
  const { i18n } = useTranslation();
  const isES = i18n.language === 'es';

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <h1 className={styles.title}>{isES ? 'Disclaimer / Aviso Legal' : 'Disclaimer'}</h1>

        {isES ? (
          <>
            <div className={styles.warningBox}>
              <p className={styles.warningText}>
                ⚠️ Esta aplicación es una herramienta de gestión y planificación personal. No constituye asesoría financiera ni garantiza resultados.
              </p>
            </div>

            <h2 className={styles.section}>1. Naturaleza de la aplicación</h2>
            <p className={styles.text}>
              Capital Manager es una aplicación de seguimiento y planificación personal para operaciones de opciones binarias. Su propósito es ayudarte a organizar, registrar y analizar tus operaciones desde un punto de vista educativo y de gestión del riesgo.
            </p>

            <h2 className={styles.section}>2. No es asesoría financiera</h2>
            <p className={styles.text}>
              La información proporcionada por esta aplicación no debe interpretarse como asesoría financiera, bursátil ni de inversión. Las proyecciones y cálculos son estimaciones basadas en parámetros que introduces tú mismo.
            </p>

            <h2 className={styles.section}>3. Riesgo de pérdida</h2>
            <p className={styles.text}>
              Las opciones binarias son instrumentos financieros de alto riesgo. Es posible perder toda la inversión. El historial pasado de resultados no garantiza resultados futuros.
            </p>

            <h2 className={styles.section}>4. Responsabilidad limitada</h2>
            <p className={styles.text}>
              En ningún caso el desarrollador de esta aplicación será responsable por pérdidas financieras, daños o perjuicios que puedan derivar del uso de la misma. El usuario asume toda la responsabilidad de sus decisiones de inversión.
            </p>

            <h2 className={styles.section}>5. Edad mínima</h2>
            <p className={styles.text}>
              El uso de esta aplicación está restringido a personas mayores de 18 años o la edad legal establecida por tu jurisdicción para participar en actividades financieras.
            </p>

            <h2 className={styles.section}>6. Datos ficticios</h2>
            <p className={styles.text}>
              Durante la fase beta, los datos que introduces (capital, operaciones, retiros) son ficticios y solo existen dentro de la aplicación. No se conectan con ninguna plataforma de trading real.
            </p>
          </>
        ) : (
          <>
            <div className={styles.warningBox}>
              <p className={styles.warningText}>
                ⚠️ This application is a personal management and planning tool. It does not constitute financial advice and does not guarantee any results.
              </p>
            </div>

            <h2 className={styles.section}>1. Nature of the Application</h2>
            <p className={styles.text}>
              Capital Manager is a personal tracking and planning application for binary options trading. Its purpose is to help you organize, record, and analyze your trades from an educational and risk management perspective.
            </p>

            <h2 className={styles.section}>2. Not Financial Advice</h2>
            <p className={styles.text}>
              The information provided by this application should not be interpreted as financial, stock, or investment advice. Projections and calculations are estimates based on parameters you input yourself.
            </p>

            <h2 className={styles.section}>3. Risk of Loss</h2>
            <p className={styles.text}>
              Binary options are high-risk financial instruments. It is possible to lose your entire investment. Past performance does not guarantee future results.
            </p>

            <h2 className={styles.section}>4. Limited Liability</h2>
            <p className={styles.text}>
              Under no circumstances will the developer of this application be liable for financial losses, damages, or harm that may result from its use. The user assumes full responsibility for their own investment decisions.
            </p>

            <h2 className={styles.section}>5. Minimum Age</h2>
            <p className={styles.text}>
              Use of this application is restricted to individuals aged 18 or over, or the legal age established by your jurisdiction for participating in financial activities.
            </p>

            <h2 className={styles.section}>6. Fictitious Data</h2>
            <p className={styles.text}>
              During the beta phase, the data you enter (capital, operations, withdrawals) is fictitious and exists only within the application. It is not connected to any real trading platform.
            </p>
          </>
        )}
      </div>
    </div>
  );
};

export default DisclaimerPage;