import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, Mail, Lock, User, ArrowRight, Loader2 } from 'lucide-react'
import { authLogin, authRegister } from '../api.js'

export default function Login() {
  const [mode, setMode] = useState('login') // 'login' | 'register'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      let data
      if (mode === 'login') {
        const res = await authLogin(email, password)
        data = res.data
      } else {
        if (!name.trim()) { setError('Please enter your name'); setLoading(false); return }
        const res = await authRegister(email, name, password)
        data = res.data
      }

      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify({ id: data.user_id, name: data.name, email: data.email }))
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-stretch">

      {/* ── Left Promo Panel ── */}
      <div className="hidden lg:flex flex-col justify-between w-[45%] p-12 relative overflow-hidden"
        style={{ background: 'linear-gradient(135deg, #1a1f36 0%, #2d3561 100%)' }}>

        {/* Background orbs */}
        <div className="absolute -top-32 -left-32 w-96 h-96 rounded-full opacity-20"
          style={{ background: 'radial-gradient(circle, #8a9eff 0%, transparent 70%)' }} />
        <div className="absolute -bottom-16 -right-16 w-80 h-80 rounded-full opacity-15"
          style={{ background: 'radial-gradient(circle, #b58eff 0%, transparent 70%)' }} />

        {/* Logo */}
        <div className="relative z-10 flex items-center gap-2.5">
          <Shield size={28} style={{ color: 'var(--accent-blue)' }} />
          <span className="text-white text-xl font-bold">Consent <span style={{ color: 'var(--accent-blue)' }}>OS</span></span>
        </div>

        {/* Center content */}
        <div className="relative z-10">
          <div className="inline-block px-3 py-1.5 rounded-full text-xs font-semibold mb-6 text-white/70"
            style={{ background: 'rgba(138,158,255,0.15)', border: '1px solid rgba(138,158,255,0.3)' }}>
            Privacy Management Platform
          </div>
          <h2 className="text-white text-4xl font-bold leading-tight mb-4">
            Your digital privacy,<br />
            <span style={{ color: 'var(--accent-blue)' }}>automated.</span>
          </h2>
          <p className="text-white/50 text-sm leading-relaxed max-w-xs">
            Consent OS automatically discovers, monitors and revokes third-party data permissions across your digital services.
          </p>

          {/* Stats row */}
          <div className="flex gap-8 mt-10">
            {[['100%', 'Automation'], ['Zero', 'Manual steps'], ['GDPR', 'Compliant']].map(([val, lbl]) => (
              <div key={lbl}>
                <div className="text-white font-bold text-lg">{val}</div>
                <div className="text-white/40 text-xs mt-0.5">{lbl}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="relative z-10 text-white/25 text-xs">
          OAuth 2.0 + JWT · End-to-end encrypted
        </div>
      </div>

      {/* ── Right Form Panel ── */}
      <div className="flex-1 flex items-center justify-center px-8 py-16 bg-white">
        <div className="w-full max-w-sm fade-in">

          {/* Mobile Logo */}
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <Shield size={22} style={{ color: 'var(--accent-blue)' }} />
            <span className="text-kanto-text font-bold">Consent <span style={{ color: 'var(--accent-blue)' }}>OS</span></span>
          </div>

          <h1 className="text-2xl font-bold text-kanto-text mb-1">
            {mode === 'login' ? 'Welcome back' : 'Create account'}
          </h1>
          <p className="text-kanto-secondary text-sm mb-8">
            {mode === 'login' ? 'Sign in to your privacy dashboard.' : 'Start managing your data consents.'}
          </p>

          {/* Tab Switcher */}
          <div className="flex rounded-xl p-1 mb-6 bg-gray-100 border border-gray-200">
            {['login', 'register'].map((m) => (
              <button
                key={m}
                onClick={() => { setMode(m); setError('') }}
                className="flex-1 py-2 rounded-lg text-sm font-semibold transition-all duration-200"
                style={{
                  background: mode === m ? '#ffffff' : 'transparent',
                  color: mode === m ? '#1a1f36' : '#697386',
                  boxShadow: mode === m ? '0 2px 8px rgba(0,0,0,0.06)' : 'none'
                }}>
                {m === 'login' ? 'Sign In' : 'Register'}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'register' && (
              <div className="relative">
                <User size={15} className="absolute left-3.5 top-3.5 text-kanto-secondary" />
                <input id="reg-name" className="inp pl-10" placeholder="Full name" value={name} onChange={e => setName(e.target.value)} />
              </div>
            )}
            <div className="relative">
              <Mail size={15} className="absolute left-3.5 top-3.5 text-kanto-secondary" />
              <input id="auth-email" className="inp pl-10" type="email" placeholder="Email address" value={email} onChange={e => setEmail(e.target.value)} required />
            </div>
            <div className="relative">
              <Lock size={15} className="absolute left-3.5 top-3.5 text-kanto-secondary" />
              <input id="auth-password" className="inp pl-10" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required />
            </div>

            {error && (
              <div className="text-sm px-3 py-2.5 rounded-xl bg-red-50 text-red-500 border border-red-100">
                {error}
              </div>
            )}

            <button id="submit-auth" type="submit" disabled={loading}
              className="btn-primary w-full py-3.5 flex items-center justify-center gap-2 mt-6 text-sm">
              {loading
                ? <Loader2 size={18} className="animate-spin" />
                : <>{mode === 'login' ? 'Sign In' : 'Create Account'} <ArrowRight size={16} /></>
              }
            </button>
          </form>

          <p className="text-center text-xs text-kanto-secondary mt-6">
            {mode === 'login' ? "Don't have an account?" : 'Already have an account?'}{' '}
            <button onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}
              className="font-semibold text-kanto-text hover:underline transition-colors">
              {mode === 'login' ? 'Register' : 'Sign In'}
            </button>
          </p>

          <div className="mt-8 text-center">
            <span className="badge">🔐 OAuth 2.0 + JWT Bearer</span>
          </div>
        </div>
      </div>
    </div>
  )
}
