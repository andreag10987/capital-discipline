import React from 'react';
import styles from './ErrorBoundary.module.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
    this.setState({ error, errorInfo });
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className={styles.errorContainer}>
          <div className={styles.errorCard}>
            <div className={styles.errorIcon}>⚠️</div>
            <h1 className={styles.errorTitle}>Oops! Something went wrong</h1>
            <p className={styles.errorMessage}>
              We're sorry, but something unexpected happened. Please try reloading the page.
            </p>
            
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className={styles.errorDetails}>
                <summary>Error details (dev only)</summary>
                <pre className={styles.errorStack}>
                  {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}

            <div className={styles.errorActions}>
              <button onClick={this.handleReload} className={styles.reloadButton}>
                Reload Page
              </button>
              <button onClick={() => window.history.back()} className={styles.backButton}>
                Go Back
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;