import React from 'react'
import { ShieldAlert, RefreshCw } from 'lucide-react'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6 text-center">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mb-6">
            <ShieldAlert size={40} className="text-red-500" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Something went wrong</h1>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            The application encountered an unexpected error and could not continue. 
            We've logged the issue and are looking into it.
          </p>
          <div className="bg-white border border-gray-200 rounded-xl p-4 mb-8 text-left max-w-lg w-full overflow-auto">
            <div className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Error Details</div>
            <code className="text-sm text-red-600 font-mono break-all">
              {this.state.error?.toString()}
            </code>
          </div>
          <button 
            onClick={() => window.location.reload()}
            className="flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl transition-all shadow-lg"
          >
            <RefreshCw size={18} /> Reload Application
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
