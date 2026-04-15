import React from 'react';

/**
 * ErrorBoundary
 * ─────────────
 * Top-level: wrap <App /> — shows a full branded recovery screen.
 * Section-level: pass `fallback` prop — shows a compact inline message
 *   instead of crashing the whole page.
 *
 * Example (section):
 *   <ErrorBoundary fallback={<p className="text-gray-400 text-sm p-4">Could not load this section.</p>}>
 *     <Suspense fallback={…}><LazyComponent /></Suspense>
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
        console.error('[Pyramyd] Unhandled render error:', error, info?.componentStack);
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null });
        if (!this.props.fallback) window.location.reload();
    };

    render() {
        if (!this.state.hasError) return this.props.children;

        // Section-level: return the caller's compact fallback
        if (this.props.fallback) return this.props.fallback;

        // App-level: full-screen recovery UI
        return (
            <div style={{
                minHeight: '100vh', display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'center', padding: '2rem',
                background: '#f8fafc', fontFamily: 'Inter, system-ui, sans-serif',
                textAlign: 'center',
            }}>
                {/* Icon */}
                <div style={{
                    width: 72, height: 72, borderRadius: '50%', background: '#dcfce7',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    marginBottom: '1.5rem',
                }}>
                    <svg width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="#16a34a" strokeWidth="2">
                        <path strokeLinecap="round" strokeLinejoin="round"
                            d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                    </svg>
                </div>

                <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#111827', margin: '0 0 0.5rem' }}>
                    Something went wrong
                </h1>
                <p style={{ color: '#6b7280', fontSize: '0.95rem', maxWidth: 400, margin: '0 0 2rem', lineHeight: 1.6 }}>
                    An unexpected error occurred. Your account and data are safe.
                    Please reload the page to continue using Pyramyd.
                </p>

                <button
                    onClick={this.handleReset}
                    style={{
                        padding: '0.75rem 2rem', background: '#16a34a', color: '#fff',
                        border: 'none', borderRadius: '0.75rem', fontSize: '0.9rem',
                        fontWeight: 600, cursor: 'pointer', marginBottom: '0.75rem',
                    }}
                >
                    Reload Page
                </button>

                <a href="/" style={{ color: '#6b7280', fontSize: '0.85rem', textDecoration: 'none' }}>
                    ← Return to Home
                </a>

                {/* Dev-only error dump */}
                {process.env.NODE_ENV === 'development' && this.state.error && (
                    <details style={{
                        marginTop: '2rem', textAlign: 'left', background: '#fef2f2',
                        border: '1px solid #fecaca', borderRadius: '0.5rem', padding: '1rem',
                        maxWidth: 600, width: '100%', fontSize: '0.75rem',
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
