import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-rose-50 to-rose-100 dark:from-neutral-950 dark:to-neutral-900 p-8">
                    <div className="max-w-md w-full bg-white dark:bg-neutral-900 rounded-2xl shadow-2xl p-8 text-center">
                        <div className="w-16 h-16 mx-auto mb-6 bg-rose-100 dark:bg-rose-500/20 rounded-full flex items-center justify-center">
                            <AlertCircle className="text-rose-600 dark:text-rose-400" size={32} />
                        </div>
                        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
                            Something went wrong
                        </h1>
                        <p className="text-slate-600 dark:text-neutral-400 mb-6">
                            The application encountered an unexpected error. Please try refreshing the page.
                        </p>
                        <button
                            onClick={() => window.location.reload()}
                            className="inline-flex items-center gap-2 px-6 py-3 bg-rose-600 hover:bg-rose-700 text-white font-medium rounded-lg transition-colors"
                        >
                            <RefreshCw size={18} />
                            Reload Application
                        </button>
                        {this.state.error && (
                            <details className="mt-6 text-left">
                                <summary className="cursor-pointer text-sm text-slate-500 dark:text-neutral-500 hover:text-slate-700 dark:hover:text-neutral-300">
                                    Error Details
                                </summary>
                                <pre className="mt-2 p-4 bg-slate-100 dark:bg-black/50 rounded-lg text-xs overflow-auto text-rose-600 dark:text-rose-400">
                                    {this.state.error.toString()}
                                </pre>
                            </details>
                        )}
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
