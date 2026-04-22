import { useState } from 'react'
import { ShieldOff, Clock, AlertTriangle, ShieldCheck, Mail, Check } from 'lucide-react'
import { revokeConsent } from '../api.js'

const SCOPE_MAP = {
  'google_account_access': { label: 'Basic Account', icon: '🌐' },
  'email':    { label: 'Email Address',  icon: '✉️' },
  'profile':  { label: 'Profile',        icon: '👤' },
  'openid':   { label: 'Auth (OpenID)',  icon: '🔑' },
  'drive':    { label: 'Drive Files',    icon: '🗂' },
  'contacts': { label: 'Contacts',       icon: '👥' },
  'calendar': { label: 'Calendar',       icon: '📅' },
  'youtube':  { label: 'YouTube',        icon: '▶️' },
  'photos':   { label: 'Photos',         icon: '🖼' },
}

function getScopeInfo(dt) {
  const norm = dt.replace(/_/g, ' ').toLowerCase()
  for (const [k, v] of Object.entries(SCOPE_MAP)) {
    if (norm.includes(k.replace(/_/g, ' '))) return v
  }
  return { label: dt.replace(/_/g, ' '), icon: '⚙️' }
}

function getRiskColor(score) {
  if (score >= 70) return '#ef4444'
  if (score >= 40) return '#f59e0b'
  return '#10b981'
}

function getRiskLabel(score) {
  if (score >= 70) return 'High'
  if (score >= 40) return 'Medium'
  return 'Low'
}

export default function ConsentCard({ consent, onRevoked }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const isRevoked = consent.status === 'revoked'
  const riskColor = getRiskColor(consent.risk_score)

  const handleRevoke = async () => {
    if (!window.confirm(`Revoke access for "${consent.service.name}"?\n\nConsent OS will automatically remove this service from your Google Account.`)) return
    setLoading(true)
    setError('')
    try {
      window.postMessage({
        type: 'CONSENT_OS_REAL_REVOKE',
        externalId: consent.service.external_id || null,
        searchName: consent.service.name,
      }, '*')
      await revokeConsent(consent.id)
      onRevoked(consent.id)
    } catch (e) {
      setError(e.response?.data?.detail || 'Revocation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      id={`consent-${consent.id}`}
      className="glass-card kanto-card-hover bg-white fade-in transition-all duration-300 overflow-hidden"
      style={{ opacity: isRevoked ? 0.65 : 1 }}
    >
      {/* ── Body ── */}
      <div className="p-5">

        {/* Header row */}
        <div className="flex items-start gap-3 mb-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0 bg-gray-50 border border-gray-100">
            {consent.service.logo_emoji}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-semibold text-sm text-kanto-text leading-tight">{consent.service.name}</h3>
              <span className="badge">{consent.service.category}</span>
            </div>
            <div className="text-xs mt-0.5 text-kanto-secondary">{consent.service.domain}</div>
          </div>

          {/* Risk score */}
          <div className="flex-shrink-0 flex flex-col items-end gap-0.5">
            <div className="text-xl font-extrabold leading-none" style={{ color: riskColor }}>
              {consent.risk_score}<span className="text-xs opacity-60">%</span>
            </div>
            <span
              className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
              style={{ background: `${riskColor}18`, color: riskColor }}
            >
              {getRiskLabel(consent.risk_score)}
            </span>
          </div>
        </div>

        {/* AI recommendation */}
        {consent.recommendation && (
          <div
            className="px-3 py-2 rounded-xl text-xs mb-3 border"
            style={{
              backgroundColor: consent.risk_score >= 70 ? '#fef2f2' : '#f5f7ff',
              borderColor:     consent.risk_score >= 70 ? '#fee2e2' : '#e0e7ff',
              color:           consent.risk_score >= 70 ? '#dc2626' : '#4f46e5',
            }}
          >
            <strong>🧠 AI:</strong> {consent.recommendation}
          </div>
        )}

        {/* OSINT status */}
        <div className="mb-3 text-xs">
          {consent.verified_revoke ? (
            <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-emerald-50 text-emerald-600 border border-emerald-100">
              <ShieldCheck size={12} />
              <span><strong>Verified:</strong> Access revoked from Google.</span>
            </div>
          ) : consent.risk_score >= 60 ? (
            <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-red-50 text-red-500 border border-red-100">
              <AlertTriangle size={12} />
              <span><strong>OSINT:</strong> Data exposure risk. Revocation recommended.</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-emerald-50 text-emerald-600 border border-emerald-100">
              <Check size={12} />
              <span><strong>Radar:</strong> Security scan passed.</span>
            </div>
          )}
        </div>

        {/* Scope badges */}
        {!isRevoked && Array.isArray(consent.data_types) && (
          <div className="flex flex-wrap gap-1.5">
            {consent.data_types.slice(0, 5).map((dt) => {
              const info = getScopeInfo(dt)
              return (
                <span key={dt} className="badge flex items-center gap-1" title={dt}>
                  {info.icon} {info.label}
                </span>
              )
            })}
          </div>
        )}
      </div>

      {/* ── Footer action bar ── */}
      <div className="flex items-center justify-between px-5 py-3 bg-gray-50/80 border-t border-gray-100">
        <div className="flex items-center gap-1.5 text-[10px] text-kanto-secondary">
          <Clock size={10} />
          {isRevoked ? (
            <span className="text-emerald-600 font-semibold">
              Revoked {new Date(consent.revoked_at).toLocaleDateString()}
            </span>
          ) : (
            <span>Granted {new Date(consent.granted_at).toLocaleDateString()}</span>
          )}
        </div>

        {!isRevoked ? (
          <button
            onClick={handleRevoke}
            disabled={loading}
            className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold rounded-xl btn-danger"
          >
            {loading ? <span className="spinner" style={{ width: 11, height: 11 }} /> : <ShieldOff size={12} />}
            {loading ? 'Revoking...' : 'Revoke'}
          </button>
        ) : (
          <div className="flex items-center gap-2">
            <button
              onClick={() => window.open(`mailto:privacy@${consent.service.domain}?subject=Data Deletion Request&body=I have revoked access. Please delete my data.`)}
              className="px-2.5 py-1 text-[10px] font-semibold rounded-lg border border-violet-200 text-violet-500 hover:bg-violet-50 transition-all flex items-center gap-0.5"
            >
              <Mail size={10} /> GDPR
            </button>
            {consent.verified_revoke && (
              <div className="flex items-center gap-0.5 text-emerald-600 text-[10px] font-bold">
                <Check size={10} /> VERIFIED
              </div>
            )}
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="mx-5 mb-3 text-[10px] text-red-500 bg-red-50 p-2 rounded-lg border border-red-100">
          {error}
        </div>
      )}
    </div>
  )
}
