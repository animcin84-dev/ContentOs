import { Clock, ShieldOff, ShieldCheck, LogIn, UserPlus, Scan } from 'lucide-react'

const ACTION_ICONS = {
  revoked: { icon: ShieldOff,    color: '#ef4444', label: 'Revoked' },
  granted: { icon: ShieldCheck,  color: '#10b981', label: 'Granted' },
  login:   { icon: LogIn,        color: '#8a9eff', label: 'Login' },
  register:{ icon: UserPlus,     color: '#b58eff', label: 'Register' },
  scan:    { icon: Scan,         color: '#f59e0b', label: 'Scan' },
}

export default function HistoryLog({ history, loading }) {
  if (loading) return (
    <div className="flex items-center justify-center py-12">
      <span className="spinner" />
    </div>
  )

  if (!history || history.length === 0) return (
    <div className="py-12 text-center text-sm text-kanto-secondary">
      No activity yet
    </div>
  )

  return (
    <div className="flex flex-col gap-3">
      {history.map((item) => {
        const meta = ACTION_ICONS[item.action] || ACTION_ICONS.scan
        const Icon = meta.icon
        return (
          <div
            key={item.id}
            id={`history-item-${item.id}`}
            className="fade-in flex items-start gap-4 p-4 rounded-2xl bg-white border border-[var(--border)] transition-shadow hover:shadow-kanto kanto-card-hover">

            {/* Icon bubble */}
            <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
              style={{ background: `${meta.color}12`, border: `1px solid ${meta.color}30` }}>
              <Icon size={16} style={{ color: meta.color }} />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap mb-1">
                <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full"
                  style={{ background: `${meta.color}12`, color: meta.color }}>
                  {meta.label}
                </span>
                {item.service && (
                  <span className="text-xs text-kanto-secondary">
                    {item.service.logo_emoji} {item.service.name}
                  </span>
                )}
              </div>
              <div className="text-xs text-kanto-secondary leading-relaxed">
                {item.detail}
              </div>
            </div>

            {/* Timestamp */}
            <div className="flex-shrink-0 flex items-center gap-1 text-xs font-mono text-kanto-secondary">
              <Clock size={10} />
              {new Date(item.timestamp).toLocaleString('en-US', {
                day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}
