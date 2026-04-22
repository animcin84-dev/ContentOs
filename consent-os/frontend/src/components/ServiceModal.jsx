import { X, ExternalLink, ShieldCheck, ShieldAlert, Mail } from 'lucide-react'

export default function ServiceModal({ consent, onClose, onRevoke }) {
  if (!consent) return null

  const isHighRisk = consent.risk_score >= 70
  
  // Real working simulated GDPR Draft Generator
  const generateGDPRDraft = () => {
    const subject = `Right to Erasure Request (GDPR Article 17) - ${consent.service.name}`
    const body = `To the Data Protection Officer / Privacy Team at ${consent.service.name},\n\nI am writing to formally request the erasure of my personal data under Article 17 of the General Data Protection Regulation (GDPR) - the Right to be Forgotten.\n\nPlease delete any personal or account data you hold regarding this email address and confirm when this action is complete.\n\nThank you.`
    const mailtoLink = `mailto:privacy@${consent.service.domain}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
    window.location.href = mailtoLink
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-gray-900/40 backdrop-blur-md" onClick={onClose} />
      <div className="relative w-full max-w-lg bg-white rounded-3xl shadow-2xl p-8 fade-in-up border border-gray-100">
        
        <button onClick={onClose} className="absolute top-6 right-6 text-gray-400 hover:text-gray-700 bg-gray-100/50 hover:bg-gray-100 rounded-full p-2 transition-all">
          <X size={20} />
        </button>

        <div className="flex items-start gap-5 mb-8">
           <div className="w-16 h-16 rounded-2xl bg-gray-50 flex items-center justify-center text-4xl shadow-sm border border-gray-100">
             {consent.service.logo_emoji || '🔌'}
           </div>
           <div>
             <h2 className="text-2xl font-bold text-kanto-text tracking-tight leading-none mb-2">{consent.service.name}</h2>
             <a href={`https://${consent.service.domain}`} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 text-xs font-semibold text-accent-blue hover:text-accent-purple transition-colors">
               {consent.service.domain} <ExternalLink size={12}/>
             </a>
           </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-8">
           <div className="bg-gray-50 rounded-2xl p-4 border border-gray-100">
              <div className="text-[10px] uppercase font-bold text-gray-400 mb-1">Status</div>
              <div className={`font-semibold text-sm flex items-center gap-2 ${consent.status === 'active' ? 'text-emerald-600' : 'text-gray-500'}`}>
                {consent.status === 'active' ? <><span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"/> Active Link</> : 'Revoked'}
              </div>
           </div>
           
           <div className={`rounded-2xl p-4 border ${isHighRisk ? 'bg-red-50 border-red-100' : 'bg-gray-50 border-gray-100'}`}>
              <div className="text-[10px] uppercase font-bold text-gray-400 mb-1">Risk Score</div>
              <div className={`font-bold text-lg flex items-center gap-2 ${isHighRisk ? 'text-red-600' : 'text-kanto-text'}`}>
                {consent.risk_score} / 100
                {isHighRisk ? <ShieldAlert size={16}/> : <ShieldCheck size={16} className="text-emerald-500"/>}
              </div>
           </div>
        </div>

        <div className="mb-8">
          <div className="text-[11px] font-bold text-gray-400 uppercase tracking-widest mb-3">Exposed Data Vectors</div>
          <div className="flex flex-wrap gap-2">
            {consent.data_types.map(dt => (
              <span key={dt} className="px-3 py-1.5 bg-indigo-50/50 border border-indigo-100 text-indigo-700 text-xs font-semibold rounded-lg shadow-sm">
                {dt.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>

        {/* Action Panel */}
        <div className="pt-6 border-t border-gray-100 flex flex-col gap-3">
          {consent.status === 'active' && (
             <button onClick={() => { onRevoke(consent.id); onClose() }} className="w-full py-3.5 bg-red-50 hover:bg-red-100 border border-red-200 text-red-600 font-bold rounded-xl text-sm transition-all shadow-[0_2px_10px_rgba(239,68,68,0.1)]">
                Revoke App Access (OAuth API)
             </button>
          )}
          <button onClick={generateGDPRDraft} className="w-full py-3.5 bg-gray-50 hover:bg-gray-100 border border-gray-200 text-kanto-text font-bold rounded-xl text-sm transition-all flex items-center justify-center gap-2">
             <Mail size={16} className="text-accent-purple"/> Generate GDPR Deletion Request
          </button>
        </div>
      </div>
    </div>
  )
}
