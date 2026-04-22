import { useState, useEffect } from 'react'
import { ShieldAlert, Shield, ShieldOff, CheckCircle, X, AlertTriangle, Cpu } from 'lucide-react'

export default function PanicModal({ consents, onClose, onRevokeItem }) {
  const [selectedIds, setSelectedIds] = useState(new Set())
  const [status, setStatus] = useState('select') // 'select' | 'running' | 'done'
  const [progressQueue, setProgressQueue] = useState([])

  const activeConsents = consents.filter(c => c.status === 'active')
  const highRisk = activeConsents.filter(c => c.risk_score >= 60).sort((a,b) => b.risk_score - a.risk_score)
  const lowRisk  = activeConsents.filter(c => c.risk_score <  60).sort((a,b) => b.risk_score - a.risk_score)

  useEffect(() => {
    setSelectedIds(new Set(highRisk.map(c => c.id)))
  }, []) // eslint-disable-line

  const toggleSelect = (id) => {
    const next = new Set(selectedIds)
    if (next.has(id)) { next.delete(id) } else { next.add(id) }
    setSelectedIds(next)
  }

  const startPanic = async () => {
    if (selectedIds.size === 0) return
    setStatus('running')
    const targets = activeConsents.filter(c => selectedIds.has(c.id))
    setProgressQueue(targets.map(c => ({ id: c.id, c, state: 'pending' })))

    for (let i = 0; i < targets.length; i++) {
      setProgressQueue(prev => prev.map((item, idx) => idx === i ? { ...item, state: 'running' } : item))
      await new Promise(r => setTimeout(r, 600))
      try {
        await onRevokeItem(targets[i].id)
        setProgressQueue(prev => prev.map((item, idx) => idx === i ? { ...item, state: 'success' } : item))
      } catch {
        setProgressQueue(prev => prev.map((item, idx) => idx === i ? { ...item, state: 'error' } : item))
      }
      await new Promise(r => setTimeout(r, 1200))
    }
    setStatus('done')
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 fade-in"
      style={{ background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(6px)' }}>
      <div className="relative w-full max-w-2xl bg-white rounded-2xl overflow-hidden flex flex-col max-h-[85vh] shadow-2xl border border-gray-100">

        {/* ─── Header ─── */}
        <div className="p-5 flex items-center justify-between border-b border-gray-100" style={{ background: '#fff9f9' }}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-red-50 border border-red-100">
              <ShieldAlert size={20} className="text-red-500" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-kanto-text">Isolation Mode</h2>
              <p className="text-xs text-kanto-secondary">Mass revocation of active access keys.</p>
            </div>
          </div>
          {status !== 'running' && (
            <button onClick={onClose} className="p-2 rounded-xl bg-gray-100 hover:bg-gray-200 transition-colors text-kanto-secondary">
              <X size={18} />
            </button>
          )}
        </div>

        {/* ─── Body ─── */}
        <div className="flex-1 overflow-y-auto p-5">
          {status === 'select' && (
            <div className="space-y-6 fade-in">
              {/* Warning notice */}
              <div className="p-4 rounded-xl text-sm bg-amber-50 border border-amber-100">
                <p className="font-semibold text-amber-700 mb-1">⚠️ Warning</p>
                <p className="text-amber-600 text-xs leading-relaxed">
                  You are about to mass-revoke access to your digital identity. AI has pre-selected high-risk services (≥ 60). 
                  Including safe services may reset sessions (e.g. "Sign in with Google" will stop working).
                </p>
              </div>

              {/* High risk */}
              <div>
                <h3 className="text-sm font-bold mb-3 flex items-center gap-2 text-red-500">
                  <AlertTriangle size={15} /> High Threat ({highRisk.length})
                </h3>
                <div className="grid gap-2">
                  {highRisk.length === 0 && <div className="text-xs text-kanto-secondary">All clear.</div>}
                  {highRisk.map(c => (
                    <label key={c.id}
                      className="flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-colors"
                      style={{
                        background: selectedIds.has(c.id) ? '#fef2f2' : '#f9fafb',
                        border: `1px solid ${selectedIds.has(c.id) ? '#fca5a5' : '#e5e7eb'}`
                      }}>
                      <input type="checkbox" className="accent-red-500 w-4 h-4"
                        checked={selectedIds.has(c.id)} onChange={() => toggleSelect(c.id)} />
                      <span className="text-xl">{c.service.logo_emoji}</span>
                      <span className="flex-1 text-sm font-medium text-kanto-text truncate">{c.service.name}</span>
                      <span className="text-xs text-red-500 font-bold bg-red-50 px-2 py-0.5 rounded-full">{c.risk_score}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Low risk */}
              <div>
                <h3 className="text-sm font-bold mb-3 flex items-center gap-2 text-emerald-600 mt-2">
                  <Shield size={15} /> Safe Services ({lowRisk.length})
                </h3>
                <div className="grid gap-2 opacity-80">
                  {lowRisk.map(c => (
                    <label key={c.id}
                      className="flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-colors"
                      style={{
                        background: selectedIds.has(c.id) ? '#f0fdf4' : '#f9fafb',
                        border: `1px solid ${selectedIds.has(c.id) ? '#86efac' : '#e5e7eb'}`
                      }}>
                      <input type="checkbox" className="accent-green-500 w-4 h-4"
                        checked={selectedIds.has(c.id)} onChange={() => toggleSelect(c.id)} />
                      <span className="text-xl">{c.service.logo_emoji}</span>
                      <span className="flex-1 text-sm font-medium text-kanto-text truncate">{c.service.name}</span>
                      <span className="text-xs text-emerald-600 font-bold bg-emerald-50 px-2 py-0.5 rounded-full">{c.risk_score}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}

          {(status === 'running' || status === 'done') && (
            <div className="fade-in space-y-4">
              <div className="text-center py-6">
                <Cpu size={40} className={`mx-auto mb-4 ${status === 'running' ? 'animate-pulse text-red-500' : 'text-emerald-500'}`} />
                <h3 className="text-lg font-bold text-kanto-text">
                  {status === 'running' ? 'Sending revocation commands...' : 'Complete'}
                </h3>
                <p className="text-sm text-kanto-secondary mt-1">
                  {progressQueue.filter(q => q.state === 'success').length} of {progressQueue.length} successfully cleared.
                </p>
              </div>

              <div className="grid gap-2">
                {progressQueue.map((q, idx) => (
                  <div key={q.id} className="flex items-center gap-3 p-3 rounded-xl bg-gray-50 border border-gray-100">
                    <span className="text-xl">{q.c.service.logo_emoji}</span>
                    <span className="flex-1 text-sm text-kanto-text truncate">{q.c.service.name}</span>
                    <div className="text-xs font-medium w-24 text-right">
                      {q.state === 'pending' && <span className="text-kanto-secondary">Waiting</span>}
                      {q.state === 'running' && <span className="text-red-500 flex items-center justify-end gap-1"><span className="spinner" style={{width:11,height:11}} /> Revoking</span>}
                      {q.state === 'success' && <span className="text-emerald-600 flex items-center justify-end gap-1"><CheckCircle size={12}/> Done</span>}
                      {q.state === 'error'   && <span className="text-red-500">Error</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ─── Footer ─── */}
        {status === 'select' && (
          <div className="p-5 border-t border-gray-100 flex items-center justify-between bg-gray-50/50">
            <div className="text-xs text-kanto-secondary font-mono">
              Selected: {selectedIds.size} / {activeConsents.length}
            </div>
            <button onClick={startPanic} disabled={selectedIds.size === 0}
              className="px-6 py-2.5 bg-red-500 hover:bg-red-600 disabled:opacity-50 text-white text-sm font-bold rounded-xl transition-all shadow-sm flex items-center gap-2">
              <ShieldOff size={15} /> Revoke Selected ({selectedIds.size})
            </button>
          </div>
        )}
        {status === 'done' && (
          <div className="p-5 border-t border-gray-100 flex justify-end bg-gray-50/50">
            <button onClick={onClose}
              className="px-6 py-2.5 bg-kanto-text hover:opacity-90 text-white text-sm font-bold rounded-xl transition-all btn-primary">
              Close Report
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
