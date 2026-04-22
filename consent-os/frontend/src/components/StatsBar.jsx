import { ShieldAlert, ShieldCheck, Mail } from 'lucide-react'

export default function StatsBar({ stats, loading }) {
  if (loading) return null;

  const cards = [
    {
      title: "Privacy Status",
      icon: <ShieldCheck size={14} className="text-kanto-text"/>,
      value: stats?.total ? `${Math.round((stats.revoked / stats.total) * 100)}%` : '0%',
      subtitle1: "Total",
      val1: stats?.total || 0,
      subtitle2: "Revoked",
      val2: stats?.revoked || 0,
      progressColor: '#10b981'
    },
    {
      title: "Data Risks",
      icon: <ShieldAlert size={14} className="text-kanto-text"/>,
      value: `${stats?.high_risk || 0}`,
      subtitle1: "Detected",
      val1: stats?.high_risk || 0,
      subtitle2: "Resolved",
      val2: stats?.revoked || 0,
      progressColor: '#ef4444'
    },
    {
      title: "Active Connections",
      icon: <Mail size={14} className="text-kanto-text"/>,
      value: `${stats?.active || 0}`,
      subtitle1: "Monitored",
      val1: stats?.active || 0,
      subtitle2: "To Review",
      val2: (stats?.active || 0) - (stats?.high_risk || 0),
      progressColor: '#8a9eff'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 mt-6">
      {cards.map((c, i) => (
        <div key={i} className="glass-card kanto-card-hover p-5 flex flex-col bg-white">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-1.5 text-xs font-bold text-kanto-text">
              {c.icon} {c.title}
            </div>
            <div className="w-5 h-5 rounded bg-gray-50 border border-gray-100 flex items-center justify-center text-gray-400">
               <span className="text-[10px]">↗</span>
            </div>
          </div>
          
          <div className="text-xs text-kanto-secondary mb-3">Last update: Nov 7</div>

          <div className="flex items-end gap-2 mb-6">
            <div className="text-[32px] font-bold leading-none text-kanto-text">{c.value}</div>
            <div className="w-4 h-4 rounded-full bg-green-50 text-risk-green flex items-center justify-center -mb-0.5">
               <span className="text-[10px] leading-none">↗</span>
            </div>
          </div>

          <div className="flex justify-between text-[10px] text-kanto-secondary mb-1.5 font-medium">
             <span>{c.subtitle1}</span>
             <span>{c.subtitle2}</span>
          </div>
           
           <div className="flex gap-[3px] mb-2 overflow-hidden h-3">
               {[...Array(30)].map((_, j) => (
                  <div key={j} className="h-full flex-1 rounded-sm min-w-[2px]" style={{ background: c.progressColor, opacity: j < 15 ? 1 - (j*0.04) : 0.1 }} />
               ))}
           </div>
           
           <div className="flex justify-between text-[11px] font-medium text-kanto-secondary mt-1">
             <span>{c.val1}</span>
             <span>{c.val2}</span>
           </div>
        </div>
      ))}
    </div>
  )
}
