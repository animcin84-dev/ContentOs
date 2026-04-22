import { useMemo, useState } from 'react'
import { Calendar as CalendarIcon, Info, ShieldAlert, ShieldCheck, Zap, ArrowUpRight, MousePointer2 } from 'lucide-react'

const DAYS_IN_YEAR = 365;
const WEEKS = 52;
const DAYS_PER_WEEK = 7;

function getRiskBlockColor(maxRisk, count) {
  if (count === 0) return 'rgba(241, 245, 249, 0.5)'; // Slate-100 semi-transparent
  if (maxRisk >= 70) return '#ef4444'; // Red-500
  if (maxRisk >= 40) return '#f59e0b'; // Amber-500
  return '#10b981'; // Emerald-500
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

export default function RiskCalendar({ consents }) {
  const [tooltip, setTooltip] = useState(null);

  const { grid, maxCount, stats, monthLabels } = useMemo(() => {
    const today = new Date();
    today.setHours(23, 59, 59, 999);
    const startDate = new Date(today);
    startDate.setDate(startDate.getDate() - DAYS_IN_YEAR);

    // Group consents by date
    const dateMap = {};
    let totalGrants = 0;
    let highRiskDays = 0;
    let peakDay = { date: null, count: 0 };

    consents.forEach(c => {
      if (!c || !c.granted_at) return;
      const d = new Date(c.granted_at);
      if (isNaN(d.getTime())) return;
      
      const key = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
      if (!dateMap[key]) dateMap[key] = { count: 0, maxRisk: 0, items: [], details: [] };
      
      dateMap[key].count += 1;
      dateMap[key].maxRisk = Math.max(dateMap[key].maxRisk, c.risk_score || 0);
      dateMap[key].items.push(c.service?.name || 'Unknown');
      dateMap[key].details.push({
        name: c.service?.name,
        risk: c.risk_score,
        emoji: c.service?.logo_emoji
      });

      totalGrants++;
      if (c.risk_score >= 70) highRiskDays++;
      if (dateMap[key].count > peakDay.count) {
        peakDay = { date: key, count: dateMap[key].count };
      }
    });

    // Build grid
    const newGrid = [];
    const labels = [];
    let current = new Date(startDate);
    // Align to start of week (Sunday)
    while (current.getDay() !== 0) current.setDate(current.getDate() - 1);

    let maxFound = 0;
    for (let w = 0; w < WEEKS; w++) {
      const week = [];
      // Collect month labels
      if (current.getDate() <= 7) {
        labels.push({ x: w, label: MONTHS[current.getMonth()] });
      }

      for (let d = 0; d < DAYS_PER_WEEK; d++) {
        const key = `${current.getFullYear()}-${String(current.getMonth()+1).padStart(2,'0')}-${String(current.getDate()).padStart(2,'0')}`;
        const data = dateMap[key];
        if (data && data.count > maxFound) maxFound = data.count;
        
        week.push({
          date: new Date(current),
          dateStr: key,
          count: data ? data.count : 0,
          maxRisk: data ? data.maxRisk : null,
          details: data ? data.details : []
        });
        current.setDate(current.getDate() + 1);
      }
      newGrid.push(week);
    }

    return { 
      grid: newGrid, 
      maxCount: maxFound,
      monthLabels: labels,
      stats: {
        totalGrants,
        highRiskDays,
        peakDay,
        activeWeeks: newGrid.filter(w => w.some(d => d.count > 0)).length
      }
    };
  }, [consents]);

  return (
    <div className="flex flex-col gap-6">
      {/* ── Calendar Stats Row ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-50/50 rounded-2xl p-4 border border-gray-100">
          <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Total Grants</div>
          <div className="text-xl font-black text-kanto-text flex items-center gap-2">
            {stats.totalGrants} <Zap size={14} className="text-accent-blue" />
          </div>
        </div>
        <div className="bg-gray-50/50 rounded-2xl p-4 border border-gray-100">
          <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">High Risk Days</div>
          <div className="text-xl font-black text-red-500 flex items-center gap-2">
            {stats.highRiskDays} <ShieldAlert size={14} />
          </div>
        </div>
        <div className="bg-gray-50/50 rounded-2xl p-4 border border-gray-100">
          <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Peak Activity</div>
          <div className="text-xl font-black text-kanto-text">
            {stats.peakDay.count} <span className="text-xs font-medium text-gray-400">items/day</span>
          </div>
        </div>
        <div className="bg-gray-50/50 rounded-2xl p-4 border border-gray-100">
          <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Active Weeks</div>
          <div className="text-xl font-black text-emerald-500 flex items-center gap-2">
            {stats.activeWeeks} <ShieldCheck size={14} />
          </div>
        </div>
      </div>

      {/* ── Main Heatmap Container ── */}
      <div className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm relative overflow-hidden">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-indigo-50 rounded-lg">
              <CalendarIcon size={16} className="text-indigo-600" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-kanto-text">Activity Heatmap</h3>
              <p className="text-[10px] text-gray-400 font-medium">Visualization of authorization events over 365 days</p>
            </div>
          </div>
          <div className="flex items-center gap-3 text-[10px] font-bold text-gray-400">
            <span>LESS</span>
            <div className="flex gap-1">
              {[0, 25, 50, 75, 100].map((v) => (
                <div key={v} className="w-3 h-3 rounded-[2px]" style={{ backgroundColor: getRiskBlockColor(v, 1), opacity: 0.2 + (v/125) }} />
              ))}
            </div>
            <span>MORE RISK</span>
          </div>
        </div>

        <div className="relative">
          {/* Month Labels */}
          <div className="flex mb-2 text-[9px] font-bold text-gray-300 uppercase tracking-tighter">
            <div className="w-8" /> {/* Offset for day labels */}
            <div className="flex-1 flex relative h-4">
              {monthLabels.map((m, i) => (
                <span key={i} className="absolute" style={{ left: `${(m.x / WEEKS) * 100}%` }}>{m.label}</span>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            {/* Day of week labels */}
            <div className="flex flex-col justify-between py-1 text-[9px] font-bold text-gray-300 w-5">
              <span>Mon</span>
              <span>Wed</span>
              <span>Fri</span>
            </div>

            {/* The Grid */}
            <div className="flex-1 overflow-x-auto pb-4 custom-scrollbar">
              <div className="flex gap-[4px]" style={{ minWidth: 'fit-content' }}>
                {grid.map((week, wIdx) => (
                  <div key={wIdx} className="flex flex-col gap-[4px]">
                    {week.map((day, dIdx) => {
                      const color = getRiskBlockColor(day.maxRisk, day.count);
                      const opacity = day.count > 0 ? Math.min(0.4 + (day.count / Math.max(maxCount, 1)) * 0.6, 1) : 1;
                      
                      return (
                        <div
                          key={dIdx}
                          className={`w-3 h-3 rounded-[3px] transition-all duration-300 cursor-pointer hover:ring-2 hover:ring-indigo-400 hover:ring-offset-1 ${day.count > 0 ? 'shadow-sm' : ''}`}
                          style={{
                            backgroundColor: color,
                            opacity: opacity,
                          }}
                          onMouseEnter={(e) => {
                            const rect = e.currentTarget.getBoundingClientRect();
                            setTooltip({ 
                              ...day,
                              x: rect.left + rect.width / 2,
                              y: rect.top - 12
                            });
                          }}
                          onMouseLeave={() => setTooltip(null)}
                        />
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* ── Tooltip ── */}
        {tooltip && (
          <div 
            className="fixed z-[9999] pointer-events-none bg-white/95 backdrop-blur-md border border-gray-200 rounded-2xl shadow-2xl p-4 fade-in min-w-[220px]"
            style={{ 
              left: tooltip.x, 
              top: tooltip.y, 
              transform: 'translate(-50%, -100%)',
            }}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                {new Date(tooltip.dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
              </div>
              <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600 text-[9px] font-bold">
                <MousePointer2 size={8} /> Details
              </div>
            </div>

            {tooltip.count > 0 ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-bold text-kanto-text">Activity Detected</div>
                  <div className="text-xs font-black text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-lg">{tooltip.count} events</div>
                </div>
                
                <div className="space-y-1.5">
                  {tooltip.details.slice(0, 4).map((item, i) => (
                    <div key={i} className="flex items-center justify-between bg-gray-50 p-2 rounded-xl border border-gray-100/50">
                      <div className="flex items-center gap-2">
                        <span className="text-sm">{item.emoji || '🌐'}</span>
                        <span className="text-[11px] font-bold text-kanto-text truncate max-w-[100px]">{item.name}</span>
                      </div>
                      <div className="text-[10px] font-black" style={{ color: getRiskBlockColor(item.risk, 1) }}>
                        {item.risk}%
                      </div>
                    </div>
                  ))}
                  {tooltip.details.length > 4 && (
                    <div className="text-[9px] text-center font-bold text-gray-400 pt-1">
                      + {tooltip.details.length - 4} more connections
                    </div>
                  )}
                </div>

                <div className="pt-2 border-t border-gray-100 flex items-center justify-between">
                  <span className="text-[9px] font-bold text-gray-400 uppercase">System Status</span>
                  <span className={`text-[9px] font-black uppercase ${tooltip.maxRisk >= 70 ? 'text-red-500' : 'text-emerald-500'}`}>
                    {tooltip.maxRisk >= 70 ? 'Action Required' : 'Monitored'}
                  </span>
                </div>
              </div>
            ) : (
              <div className="py-2 flex flex-col items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-gray-50 flex items-center justify-center text-gray-300">
                  <Info size={14} />
                </div>
                <div className="text-[11px] font-bold text-gray-400">No activity recorded</div>
              </div>
            )}
            
            {/* Tooltip Arrow */}
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[6px] border-t-white" />
          </div>
        )}
      </div>

      {/* ── Detailed Activity Feed (Simulated Intelligence) ── */}
      <div className="bg-gradient-to-r from-indigo-600 to-violet-700 rounded-3xl p-6 text-white shadow-lg overflow-hidden relative">
        <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 blur-3xl rounded-full -translate-y-1/2 translate-x-1/2" />
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-4">
            <Zap size={18} className="text-yellow-300" />
            <h3 className="text-sm font-black uppercase tracking-widest">Autonomous Insights</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <p className="text-xs text-indigo-100 leading-relaxed">
                Our privacy engine detected <span className="text-white font-bold">{stats.totalGrants} authorizations</span> across <span className="text-white font-bold">{stats.activeWeeks} active weeks</span>. 
                {stats.highRiskDays > 0 ? ` Warning: ${stats.highRiskDays} days contained high-risk grants that bypass standard security filters.` : ' All grants currently follow established safety protocols.'}
              </p>
              <button className="flex items-center gap-1.5 text-[10px] font-black text-yellow-300 hover:text-white transition-colors group">
                GENERATE FULL AUDIT REPORT <ArrowUpRight size={12} className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </button>
            </div>
            <div className="flex flex-col justify-center border-l border-white/10 pl-6">
              <div className="text-[10px] font-bold text-indigo-200 uppercase mb-1">Security Score</div>
              <div className="text-3xl font-black text-white">
                {Math.max(0, 100 - (stats.highRiskDays * 15))}
                <span className="text-sm text-indigo-200 font-medium ml-1">/100</span>
              </div>
              <div className="h-1.5 w-full bg-white/10 rounded-full mt-3 overflow-hidden">
                <div 
                  className="h-full bg-emerald-400 transition-all duration-1000" 
                  style={{ width: `${Math.max(5, 100 - (stats.highRiskDays * 15))}%` }} 
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
