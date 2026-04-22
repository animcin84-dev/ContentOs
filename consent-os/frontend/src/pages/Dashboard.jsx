import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, LayoutDashboard, History, RefreshCw, Search, DownloadCloud, BrainCircuit, ShieldAlert, Cpu, MoonStar, Zap } from 'lucide-react'
import { getConsents, getHistory, getStats, revokeConsent, verifyExternalRevoke, runRescan, massRevoke, deepWebScan } from '../api.js'
import StatsBar from '../components/StatsBar.jsx'
import ConsentCard from '../components/ConsentCard.jsx'
import DataGraph from '../components/DataGraph.jsx'
import HistoryLog from '../components/HistoryLog.jsx'
import RiskCalendar from '../components/RiskCalendar.jsx'
import PanicModal from '../components/PanicModal.jsx'
import ServiceModal from '../components/ServiceModal.jsx'

const TABS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'history',   label: 'Activity',  icon: History },
]

const FILTERS = [
  { id: 'all', label: 'All Connections' },
  { id: 'active', label: 'Active Only' },
  { id: 'revoked', label: 'Revoked' },
  { id: 'high_risk', label: '🔴 Critical Risk' },
]

const SORTS = [
  { id: 'risk_desc', label: 'Risk Scale (High to Low)' },
  { id: 'risk_asc', label: 'Risk Scale (Low to High)' },
  { id: 'date_desc', label: 'Most Recent First' },
]

export default function Dashboard() {
  const navigate = useNavigate()
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  const [tab, setTab] = useState('dashboard')
  const [consents, setConsents] = useState([])
  const [history, setHistory] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [histLoading, setHistLoading] = useState(false)
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')
  const [sort, setSort] = useState('risk_desc')
  const [toast, setToast] = useState(null)
  const [selectedGraphNode, setSelectedGraphNode] = useState(null)
  const [showPanicModal, setShowPanicModal] = useState(false)
  const [showProfileMenu, setShowProfileMenu] = useState(false)

  // ── Data Fetching ──────────────────────────────────────────────────────────
  const loadConsents = useCallback(async () => {
    setLoading(true)
    try {
      const [cRes, sRes] = await Promise.all([getConsents(), getStats()])
      setConsents(cRes.data)
      setStats(sRes.data)
      setToast(`Loaded connections successfully.`)
      setTimeout(() => setToast(null), 3000)
    } catch (e) {
      console.error('Failed to load consents', e)
      setToast(`❌ Dashboard connection failed: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }, [])

  const loadHistory = useCallback(async () => {
    setHistLoading(true)
    try {
      const res = await getHistory()
      setHistory(res.data)
    } catch (e) {
      console.error('Failed to load history', e)
    } finally {
      setHistLoading(false)
    }
  }, [])

  useEffect(() => { loadConsents() }, [loadConsents])
  useEffect(() => { if (tab === 'history') loadHistory() }, [tab, loadHistory])

  // ── Functions ──────────────────────────────────────────────────────────────
  const handleRevoked = useCallback((id) => {
    setConsents(prev =>
      prev.map(c => c.id === id
        ? { ...c, status: 'revoked', revoked_at: new Date().toISOString() }
        : c
      )
    )
    setStats(prev => {
      if (!prev) return prev
      const item = consents.find(c => c.id === id)
      return {
        ...prev,
        active: Math.max(0, prev.active - 1),
        revoked: prev.revoked + 1,
        high_risk: prev.high_risk - (item?.risk_score >= 70 ? 1 : 0)
      }
    })
  }, [consents])

  const exportToCSV = () => {
    if (consents.length === 0) return
    const header = "ID,Service Name,Domain,Status,Risk Score,Data Scopes,Date Granted\n"
    const rows = consents.map(c => 
      `${c.id},"${c.service.name}","${c.service.domain}",${c.status},${c.risk_score},"${c.data_types.join(', ')}",${new Date(c.granted_at).toISOString()}`
    ).join("\n")
    const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement("a")
    link.href = URL.createObjectURL(blob)
    link.download = `consent_os_audit_${new Date().toISOString().slice(0,10)}.csv`
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    setToast("Audit report exported to CSV.")
    setTimeout(() => setToast(null), 3000)
  }

  // Generate REAL insights based on user's actual DB states
  const generateInsights = () => {
    const active = consents.filter(c => c?.status === 'active')
    if (active.length === 0) return "System secure. No third-party applications currently possess active access privileges to your data."

    const totalRisks = active.filter(c => (c?.risk_score || 0) >= 70).length
    let highlyShared = {}
    active.forEach(c => {
      if (Array.isArray(c?.data_types)) {
        c.data_types.forEach(dt => { highlyShared[dt] = (highlyShared[dt] || 0) + 1 })
      }
    })
    const entries = Object.entries(highlyShared)
    const mostShared = entries.length > 0 ? entries.sort((a,b) => b[1] - a[1])[0] : null

    let insight = `Scanning ${active.length} active connections... `
    if (mostShared) insight += `Your most exposed data type is "${mostShared[0].replace(/_/g, ' ')}" (shared across ${mostShared[1]} services). `
    if (totalRisks > 0) insight += `Critical warning: ${totalRisks} service(s) flagged for immediate revocation due to unsafe access scopes.`
    else insight += `Security scan passed. All active connections are within acceptable risk thresholds.`
    return insight
  }

  const visible = consents
    .filter(c => {
      if (!c || !c.service) return false
      if (search) {
        const q = search.toLowerCase()
        return (c.service.name || "").toLowerCase().includes(q) || (c.service.domain || "").toLowerCase().includes(q)
      }
      return true
    })
    .filter(c => {
      if (filter === 'active') return c.status === 'active'
      if (filter === 'revoked') return c.status === 'revoked'
      if (filter === 'high_risk') return c.status === 'active' && (c.risk_score || 0) >= 70
      return true
    })
    .sort((a, b) => {
      if (sort === 'risk_desc') return b.risk_score - a.risk_score
      if (sort === 'risk_asc') return a.risk_score - b.risk_score
      if (sort === 'date_desc') return new Date(b.granted_at) - new Date(a.granted_at)
      return 0
    })

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  const toggleDarkMode = () => {
    document.documentElement.classList.toggle('dark')
  }

  const handleRescan = async () => {
    setLoading(true)
    setToast('Starting massive re-scan of active connections...')
    try {
      await runRescan()
      await loadConsents()
      setToast('✅ Rescan complete. Dashboard synced with MyAccount.')
    } catch (e) {
      setToast(e.response?.data?.detail || 'Rescan failed.')
    } finally {
      setLoading(false)
    }
  }

  const handleMassRevoke = async () => {
    setLoading(true)
    setShowPanicModal(false)
    setToast('Executing Mass Revoker...')
    try {
      await massRevoke()
      await loadConsents()
      setToast('🚨 Mass Revoker completed successfully.')
    } catch (e) {
      setToast('Failed to execute Mass Revoke.')
    } finally {
      setLoading(false)
    }
  }

  const handleDeepScan = async () => {
    setLoading(true)
    setToast('Initiating Deep Web Scan for leaks...')
    try {
      const res = await deepWebScan()
      setToast(`Deep Scan finished: ${res.data.status}`)
    } catch (e) {
      setToast('Deep web scan failed.')
    } finally {
      setLoading(false)
    }
  }

  const apiRevokeItem = async (id, serviceName) => {
    // Revoke internally
    await revokeConsent(id)
    handleRevoked(id)
    setToast(`Disconnected API access for ${serviceName}.`)
    
    // Auto-invoke extension to physically remove from Google
    window.postMessage({ type: 'CONSENT_OS_REAL_REVOKE', searchName: serviceName }, '*')
  }

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className={`min-h-screen flex flex-col transition-all duration-500 ${showPanicModal ? 'blur-md bg-gray-100' : 'bg-transparent'}`}>

      {/* ── Navbar ── */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 h-16 bg-white/80 backdrop-blur-md border-b border-gray-200/50 shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
        <div className="flex items-center gap-2 font-bold text-lg text-kanto-text w-[200px]">
          <Shield size={24} className="text-accent-purple" />
          <span className="tracking-tight">Consent OS</span>
        </div>

        <div className="flex gap-4 items-center bg-gray-50/50 p-1 rounded-xl">
          {TABS.map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className="text-sm font-semibold transition-all duration-300 px-5 py-1.5 rounded-lg"
              style={{
                color: tab === id ? '#ffffff' : 'var(--text-secondary)',
                background: tab === id ? '#1a1f36' : 'transparent',
                boxShadow: tab === id ? '0 4px 12px rgba(0,0,0,0.1)' : 'none'
              }}>
              {label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-4 justify-end">
          <div className="relative group">
             <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-accent-blue" />
             <input
               className="pl-9 pr-4 py-1.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-kanto-text outline-none focus:bg-white focus:border-accent-blue focus:ring-2 focus:ring-accent-blue/20 transition-all w-[220px]"
               placeholder="Search registry..."
               value={search}
               onChange={e => setSearch(e.target.value)}
             />
          </div>
          <button className="p-2 bg-gray-50 hover:bg-gray-100 rounded-xl text-gray-500 hover:text-kanto-text transition-colors">
            <RefreshCw size={16} onClick={loadConsents} />
          </button>
          
          <div className="relative">
             <div className="w-9 h-9 rounded-full overflow-hidden bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm cursor-pointer hover:border-accent-purple transition-colors" onClick={() => setShowProfileMenu(!showProfileMenu)} title="Profile">
                 <img src={`https://ui-avatars.com/api/?name=${user.name || 'Admin'}&background=b58eff&color=fff&bold=true`} alt="User" className="w-full h-full object-cover" />
             </div>
             {showProfileMenu && (
                <div className="absolute right-0 top-12 w-56 bg-white/90 dark:bg-gray-800/95 backdrop-blur-xl border border-gray-100 dark:border-gray-700 shadow-2xl rounded-2xl p-2 z-[100] fade-in transform origin-top-right transition-all">
                   <div className="px-3 py-2 mb-1 border-b border-gray-100 dark:border-gray-700">
                      <div className="text-xs font-bold text-kanto-text dark:text-gray-100">{user.name}</div>
                      <div className="text-[10px] font-semibold text-gray-400">{user.email}</div>
                   </div>
                   <button onClick={toggleDarkMode} className="flex items-center gap-2 w-full text-left px-3 py-2 text-xs font-semibold text-kanto-text dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors">
                     <MoonStar size={14}/> Toggle Dark Mode
                   </button>
                   <button onClick={handleRescan} className="flex items-center gap-2 w-full text-left px-3 py-2 text-xs font-semibold text-kanto-text dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors">
                     <RefreshCw size={14} className="text-accent-blue"/> Sync with Google
                   </button>
                   <button onClick={handleDeepScan} className="flex items-center gap-2 w-full text-left px-3 py-2 text-xs font-semibold text-kanto-text dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors">
                     <Search size={14} className="text-accent-purple"/> Deep Web Scan
                   </button>
                   <button onClick={exportToCSV} className="flex items-center gap-2 w-full text-left px-3 py-2 text-xs font-semibold text-kanto-text dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors">
                     <DownloadCloud size={14}/> Export Data
                   </button>
                   <button onClick={handleLogout} className="flex items-center gap-2 w-full text-left px-3 py-2 text-xs font-semibold text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors mt-1 border-t border-gray-100 dark:border-gray-700">
                     Logout
                   </button>
                </div>
             )}
          </div>
        </div>
      </nav>

      {/* ── Main Content ── */}
      <main className="flex-1 pt-24 px-4 md:px-8 pb-10 max-w-[1500px] mx-auto w-full fade-in">
        
        {/* Top Action Bar */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 gap-4">
           <div>
              <div className="text-[11px] font-bold text-accent-purple uppercase tracking-widest mb-2 flex items-center gap-1.5">
                 <ShieldAlert size={12} /> Autonomous Privacy Engine
              </div>
              <h1 className="text-4xl font-extrabold text-kanto-text tracking-tight h-10">Data Intelligence</h1>
           </div>
           
           <div className="flex items-center gap-3">
              <button onClick={exportToCSV} className="px-4 py-2 bg-white border border-gray-200 hover:bg-gray-50 rounded-xl text-sm font-semibold text-kanto-text shadow-sm transition-all flex items-center gap-2">
                 <DownloadCloud size={16} className="text-accent-blue"/> Audit Report (CSV)
              </button>
              <button onClick={() => setShowPanicModal(true)} className="px-5 py-2 bg-red-50 hover:bg-red-100 border border-red-200 rounded-xl text-sm font-bold text-red-600 shadow-[0_4px_14px_rgba(239,68,68,0.15)] hover:shadow-[0_6px_20px_rgba(239,68,68,0.25)] transition-all flex items-center gap-2">
                 <ShieldAlert size={16}/> Lock Down High Risks
              </button>
           </div>
        </div>

        {tab === 'dashboard' ? (
           <div className="flex flex-col gap-8">
             
             {/* 1. HERO MAP SECTION (Full width) */}
             <div className="w-full bg-white rounded-3xl shadow-kanto border border-gray-100 relative group overflow-hidden fade-in-up" style={{ height: '520px' }}>
                <div className="absolute top-6 left-1/2 -translate-x-1/2 px-4 py-1.5 bg-white/80 backdrop-blur-lg border border-gray-200 rounded-full text-[11px] font-bold text-kanto-secondary z-10 shadow-sm flex items-center gap-2">
                   <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> Live connection mapping active
                </div>
                {loading ? (
                   <div className="flex items-center justify-center w-full h-full min-h-[400px]"><span className="spinner" /></div>
                ) : (
                   <DataGraph consents={consents} userName={user.name} onNodeClick={setSelectedGraphNode} searchQuery={search} />
                )}
             </div>

             {/* 2. OVERVIEW ROW */}
             <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 fade-in-up" style={{ animationDelay: '0.1s' }}>
                <div className="xl:col-span-2">
                   <StatsBar stats={stats} />
                </div>
                
                {/* REAL AI Insights Panel */}
                <div className="bg-gradient-to-br from-indigo-900 to-slate-900 rounded-3xl p-6 text-white shadow-xl relative overflow-hidden flex flex-col justify-between">
                   <div className="absolute top-0 right-0 w-64 h-64 bg-accent-purple/20 blur-[60px] rounded-full pointer-events-none -translate-y-1/2 translate-x-1/2" />
                   
                   <div>
                     <div className="flex items-center gap-2 text-indigo-200 text-xs font-bold uppercase tracking-widest mb-4">
                        <BrainCircuit size={14} /> Intelligence Scan
                     </div>
                     <p className="text-sm text-indigo-50 leading-relaxed font-medium">
                        {loading ? 'Analyzing active data vectors...' : generateInsights()}
                     </p>
                   </div>
                   
                   <div className="mt-6 flex items-center gap-3">
                      <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                         <div className="h-full bg-emerald-400 w-full animate-[pulse_2s_ease-in-out_infinite] rounded-full" />
                      </div>
                      <span className="text-[10px] text-indigo-200 font-mono tracking-widest">SYSTEM SECURE</span>
                   </div>
                </div>
             </div>

             {/* 3. LIST CONTROLS & GRID */}
             <div className="mt-4 pt-8 border-t border-gray-100 fade-in-up" style={{ animationDelay: '0.2s' }}>
                <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4 bg-white p-2 rounded-2xl shadow-sm border border-gray-100">
                  <div className="flex bg-gray-50 p-1 rounded-xl w-full md:w-auto">
                    {FILTERS.map(f => (
                      <button key={f.id} onClick={() => setFilter(f.id)}
                        className={`flex-1 md:flex-none px-4 py-2 text-xs font-bold rounded-lg transition-all
                          ${filter === f.id ? 'bg-white text-kanto-text shadow-[0_2px_8px_rgba(0,0,0,0.06)]' : 'text-gray-500 hover:bg-gray-100/50'}`}>
                        {f.label}
                      </button>
                    ))}
                  </div>
                  <div className="flex items-center gap-3 w-full md:w-auto px-2">
                     <span className="text-xs font-semibold text-gray-400">Sort by:</span>
                     <select className="bg-transparent text-sm font-semibold text-kanto-text outline-none cursor-pointer"
                       value={sort} onChange={e => setSort(e.target.value)}>
                       {SORTS.map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
                     </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                  {visible.length === 0 ? (
                    <div className="col-span-full py-20 text-center text-kanto-secondary flex items-center justify-center gap-2">
                      <Cpu size={18}/> No connections matching the filter.
                    </div>
                  ) : (
                    visible.map((c, i) => (
                      <div key={c.id} className="fade-in-up" style={{ animationDelay: `${i * 0.05}s` }}>
                        <ConsentCard consent={c} onRevoked={handleRevoked} />
                      </div>
                    ))
                  )}
                </div>
             </div>

           </div>
        ) : (
          <div className="flex flex-col gap-8 fade-in-up">
            <div className="w-full bg-white rounded-3xl p-6 shadow-kanto border border-gray-100 flex flex-col gap-4">
               <h2 className="text-xl font-bold text-kanto-text mb-2">Risk Calendar</h2>
               <div className="text-sm text-kanto-secondary mb-4 leading-relaxed">
                  Historical tracking of authorizations and security alerts over the past year.
               </div>
               <div className="w-full min-h-[300px]">
                  <RiskCalendar consents={consents} />
               </div>
            </div>

            <div className="w-full bg-white rounded-3xl p-8 shadow-kanto border border-gray-100">
              <h2 className="text-xl font-bold text-kanto-text mb-6 pb-4 border-b border-gray-100">Audit Trail Logs</h2>
              {histLoading ? <div className="py-10 text-center"><span className="spinner" /></div> : <HistoryLog logs={history} />}
            </div>
          </div>
        )}
      </main>

      {/* Modals and Toasts */}
      {showPanicModal && (
        <PanicModal consents={consents} onRevoke={handleMassRevoke} onClose={() => setShowPanicModal(false)} />
      )}

      {selectedGraphNode && (
        <ServiceModal consent={selectedGraphNode} onClose={() => setSelectedGraphNode(null)} onRevoke={(id) => apiRevokeItem(id, selectedGraphNode.service.name)} />
      )}

      {toast && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-kanto-text text-white px-5 py-3 rounded-full text-sm font-semibold shadow-[0_10px_40px_rgba(0,0,0,0.2)] fade-in z-[100] flex items-center gap-2">
          {toast}
        </div>
      )}
    </div>
  )
}
