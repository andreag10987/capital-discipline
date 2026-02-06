import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import api from '../../services/api';
import styles from './ReportDownload.module.css';

const ReportDownload = ({ goalId }) => {
  const { t } = useTranslation();
  const [downloading, setDownloading] = useState(null);
  const [error, setError] = useState(null);

  const downloadReport = async (format) => {
    setDownloading(format);
    setError(null);
    try {
      const response = await api.get(`/reports/goals/${goalId}/${format}`, {
        responseType: 'blob',
      });

      const mimeTypes = {
        pdf: 'application/pdf',
        excel: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        csv: 'text/csv',
      };

      const extensions = { pdf: 'pdf', excel: 'xlsx', csv: 'csv' };

      const blob = new Blob([response.data], { type: mimeTypes[format] });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `goal_${goalId}_report.${extensions[format]}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      const detail = err.response?.data?.detail || t('reports.downloadFailed');
      setError(detail);
    } finally {
      setDownloading(null);
    }
  };

  if (!goalId) return null;

  return (
    <div className={styles.container}>
      <h4 className={styles.title}>📊 {t('reports.downloadTitle')}</h4>
      {error && <div className={styles.error}>{error}</div>}
      <div className={styles.buttons}>
        <button
          className={`${styles.btn} ${styles.btnCsv}`}
          onClick={() => downloadReport('csv')}
          disabled={downloading === 'csv'}
        >
          {downloading === 'csv' ? '⏳' : '📄'} CSV
        </button>
        <button
          className={`${styles.btn} ${styles.btnExcel}`}
          onClick={() => downloadReport('excel')}
          disabled={downloading === 'excel'}
        >
          {downloading === 'excel' ? '⏳' : '📊'} Excel
        </button>
        <button
          className={`${styles.btn} ${styles.btnPdf}`}
          onClick={() => downloadReport('pdf')}
          disabled={downloading === 'pdf'}
        >
          {downloading === 'pdf' ? '⏳' : '📕'} PDF
        </button>
      </div>
    </div>
  );
};

export default ReportDownload;