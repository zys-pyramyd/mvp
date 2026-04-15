import React from 'react';

/**
 * ErrorBoundary — catches any JavaScript error in its child tree,
 * logs it, and shows a friendly recovery screen instead of a blank page.
 *
 * Usage:
 *   <ErrorBoundary>
 *     <App />
 *   </ErrorBoundary>
 *
 * For section-level isolation (lazy-loaded panels, modals, etc.) pass a
 * compact fallback via the `fallback` prop:
 *   <ErrorBoundary fallback={<p>Could not load this section.</p>}>
 *     <Suspense>...</Suspense>
 *   </ErrorBoundary>
 */
class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, info) {
        // Log to console — swap for Sentry / LogRocket in production
        console.error('[ErrorBoundary] Caught error:', error, info?.componentStack);
    }

    handleReload = () => {
        // Try a soft reset first (clear state); falls back to hard reload
        this.setState({ hasError: false, error: null });
        // If we're at the top level, a hard reload is the safest recovery
        if (!this.props.fallback) {
            window.location.reload();
        }
    };

    render() {
        if (!this.state.hasError) return this.props.children;

        // Section-level: compact inline fallback
        if (this.props.fallback) return this.props.fallback;

        // App-level: full-screen recovery UI
        return (
            <div
                style={{
                    minHeight: '100vh',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '2rem',
                    background: '#f8fafc',
                    fontFamily: 'Inter, system-ui, sans-serif',
                    textAlign: 'center',
                }}
            >
                {/* Logo / brand mark */}
                <div style={{
                    width: 72, height: 72,
                    borderRadius: '50%',
                    background: '#dcfce7',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    marginBottom: '1.5rem',
                }}>
                    <svg width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="#16a34a" strokeWidth="2">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                    </svg>
                </div>

                <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#111827', margin: '0 0 0.5rem' }}>
                    Something went wrong
                </h1>
                <p style={{ color: '#6b7280', fontSize: '0.95rem', maxWidth: 420, margin: '0 0 2rem', lineHeight: 1.6 }}>
                    An unexpected error occurred. Don't worry — your account and data are safe.
                    Please reload the page to continue.
                </p>

                <button
                    onClick={this.handleReload}
                    style={{
                        padding: '0.75rem 2rem',
                        background: '#16a34a',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '0.75rem',
                        fontSize: '0.9rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        marginBottom: '1rem',
                    }}
                >
                    Reload Page
                </button>

                <a
                    href="/"
                    style={{ color: '#6b7280', fontSize: '0.85rem', textDecoration: 'none' }}
                >
                    ← Return to Home
                </a>

                {/* Dev-only error detail — stripped in production by CRA */}
                {process.env.NODE_ENV === 'development' && this.state.error && (
                    <details style={{
                        marginTop: '2rem', textAlign: 'left',
                        background: '#fef2f2', border: '1px solid #fecaca',
                        borderRadius: '0.5rem', padding: '1rem',
                        maxWidth: 600, width: '100%', fontSize: '0.78rem',
                        color: '#991b1b', whiteSpace: 'pre-wrap', wordBreak: 'break-word',
                    }}>
                        <summary style={{ cursor: 'pointer', fontWeight: 600, marginBottom: '0.5rem' }}>
                            Developer Details
                        </summary>
                        {String(this.state.error)}
                    </details>
                )}
            </div>
        );
    }
}

export default ErrorBoundary;
