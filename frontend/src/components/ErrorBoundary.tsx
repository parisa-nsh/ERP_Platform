import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError && this.state.error) {
      return (
        <div style={{ padding: 24, fontFamily: 'sans-serif', maxWidth: 600 }}>
          <h1>Something went wrong</h1>
          <pre style={{ background: '#f5f5f5', padding: 16, overflow: 'auto' }}>
            {this.state.error.message}
          </pre>
          <p>Check the browser console (F12) for details.</p>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
