import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { Filter, Maximize, ZoomIn, ZoomOut } from 'lucide-react'

function getRiskColor(score) {
  if (score >= 70) return '#ef4444' // Red
  if (score >= 40) return '#f59e0b' // Amber
  return '#10b981' // Emerald
}

export default function DataGraph({ consents, userName, onNodeClick, searchQuery }) {
  const svgRef = useRef(null)
  const simRef = useRef(null)
  const zoomRef = useRef(null)
  const dimRef = useRef({ w: 0, h: 0 })
  const [highlightMode, setHighlightMode] = useState('all') // all | high | revoked

  useEffect(() => {
    if (!consents || consents.length === 0 || !svgRef.current) return
    const el = svgRef.current.parentElement

    const W = el.clientWidth  || 800
    const H = el.clientHeight || 400
    dimRef.current = { w: W, h: H }

      const svg = d3.select(svgRef.current)
      svg.selectAll('*').remove()
      if (simRef.current) simRef.current.stop()

      // Define patterns and filters
      const defs = svg.append('defs')
      
      const pattern = defs.append('pattern')
        .attr('id', 'dots')
        .attr('x', 0).attr('y', 0)
        .attr('width', 24).attr('height', 24)
        .attr('patternUnits', 'userSpaceOnUse')
      pattern.append('circle').attr('cx', 2).attr('cy', 2).attr('r', 1.5).attr('fill', '#e2e8f0')

      const nodeShadow = defs.append('filter').attr('id', 'kanto-node-shadow')
      nodeShadow.append('feDropShadow').attr('dx', 0).attr('dy', 5).attr('stdDeviation', 8).attr('flood-color', 'rgba(0,0,0,0.06)')
      
      const userShadow = defs.append('filter').attr('id', 'kanto-user-shadow')
      userShadow.append('feDropShadow').attr('dx', 0).attr('dy', 5).attr('stdDeviation', 10).attr('flood-color', 'rgba(138,158,255,0.4)')

      // Background
      svg.append('rect').attr('width', '100%').attr('height', '100%').attr('fill', 'url(#dots)')

      const userNode = { id: '__user__', label: userName || 'You', isUser: true, r: 28, col: '#8a9eff' }
      const nodes = [userNode]
      const links = []

      consents.forEach(c => {
        if (!c || !c.service) return
        const active = c.status === 'active'
        nodes.push({
          id: String(c.id),
          label: c.service.name || 'Unknown',
          emoji: c.service.logo_emoji || '🌐',
          active,
          risk: c.risk_score || 0,
          r: active ? Math.max(12, Math.min(24, (Array.isArray(c.data_types) ? c.data_types.length : 0) * 2.5)) : 10,
          col: active ? getRiskColor(c.risk_score || 0) : '#cbd5e1',
          fullConsent: c,
        })
        links.push({ source: '__user__', target: String(c.id), active, weight: active ? 2 : 1 })
      })

      const g = svg.append('g').attr('class', 'graph-container')
      
      // Setup Zoom
      const zoom = d3.zoom()
        .scaleExtent([0.2, 4])
        .on('zoom', e => g.attr('transform', e.transform))
      
      svg.call(zoom)
      // Disable double click zoom correctly in D3 v6+
      svg.on('dblclick.zoom', null)

      // Store zoom object in DOM for external buttons
      svg.node().__zoom = zoom
      svg.node().__g = g
      svg.node().__W = W
      svg.node().__H = H

      const linkG  = g.append('g')
      const nodeG  = g.append('g')
      const labelG = g.append('g')

      // Much wider spread for max view
      simRef.current = d3.forceSimulation(nodes)
        .force('link',      d3.forceLink(links).id(d => d.id).distance(d => d.active ? 200 + Math.random()*150 : 120))
        .force('charge',    d3.forceManyBody().strength(d => d.isUser ? -2500 : -600).distanceMax(1000))
        .force('center',    d3.forceCenter(W/2, H/2))
        .force('collision', d3.forceCollide().radius(d => d.r + 30).iterations(3))

      const link = linkG.selectAll('line').data(links).enter().append('line')
        .attr('class', 'link')
        .attr('stroke', d => d.active ? '#cbd5e1' : '#f1f5f9')
        .attr('stroke-width', d => d.weight)
        .attr('stroke-dasharray', d => d.active ? null : '4,4')
        .attr('opacity', 0)

      link.transition().duration(1000).delay((d,i) => i*25).attr('opacity', 1)

      const nodeGroup = nodeG.selectAll('g').data(nodes).enter().append('g')
        .attr('class', 'node-group')
        .style('cursor', d => d.isUser ? 'default' : 'pointer')
        .call(d3.drag()
          .on('start', (e, d) => { if (!e.active) simRef.current.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y })
          .on('drag',  (e, d) => { d.fx=e.x; d.fy=e.y })
          .on('end',   (e, d) => { if (!e.active) simRef.current.alphaTarget(0); d.fx=null; d.fy=null })
        )
        .on('click', (e, d) => { if (!d.isUser && d.fullConsent && onNodeClick) onNodeClick(d.fullConsent) })

      // Node rings
      nodeGroup.append('circle')
        .attr('class', 'outer-ring')
        .attr('r', 0) 
        .attr('fill', '#ffffff')
        .attr('stroke', d => d.col)
        .attr('stroke-width', d => d.isUser ? 3.5 : 2.5)
        .attr('filter', d => d.isUser ? 'url(#kanto-user-shadow)' : 'url(#kanto-node-shadow)')
        .transition().duration(800).ease(d3.easeElasticOut.amplitude(1).period(0.6)).delay((d,i)=>i*20)
        .attr('r', d => d.r)

      nodeGroup.append('circle')
        .attr('r', 0)
        .attr('fill', d => d.col)
        .attr('opacity', d => d.isUser ? 1 : 0.8)
        .transition().duration(600).ease(d3.easeBackOut).delay((d,i)=>i*20 + 200)
        .attr('r', d => d.isUser ? d.r * 0.45 : d.r * 0.4)

      // Initial call isn't strictly needed if we run another useEffect, but we'll do it from the second useEffect.

      // Tooltip handling
      let mapTooltip = d3.select('body').select('.kanto-map-tooltip')
      if (mapTooltip.empty()) {
        mapTooltip = d3.select('body').append('div')
          .attr('class', 'kanto-map-tooltip')
          .style('position', 'absolute')
          .style('pointer-events', 'none')
          .style('z-index', '9999')
          .style('background', '#fff')
          .style('border', '1px solid #eef0f4')
          .style('border-radius', '16px')
          .style('padding', '12px 16px')
          .style('color', '#1a1f36')
          .style('box-shadow', '0 10px 40px rgba(0,0,0,0.1)')
          .style('opacity', 0)
          .style('transition', 'opacity 0.2s ease')
      }

      nodeGroup
        .on('mouseover', (e, hD) => {
          if (highlightMode !== 'all') return // Disable hover dimming if mode is active
          nodeGroup.selectAll('.outer-ring').style('opacity', d => (d.id===hD.id||d.isUser) ? 1 : 0.4)
          link.style('opacity', d => (d.target.id===hD.id||d.source.id===hD.id) ? 1 : 0.1)
              .attr('stroke', d => (d.target.id===hD.id||d.source.id===hD.id) ? hD.col : '#e2e8f0')
          labelG.selectAll('text').style('opacity', d => (d.id===hD.id||d.isUser) ? 1 : 0)
          
          if (!hD.isUser) {
            mapTooltip
              .style('opacity', 1)
              .style('left', (e.pageX + 20) + 'px')
              .style('top',  (e.pageY - 20) + 'px')
              .html(`
                <div class="flex items-center gap-3">
                  <span class="text-2xl">${hD.emoji || '🔌'}</span>
                  <div>
                    <div class="font-bold text-base tracking-tight">${hD.label}</div>
                    <div class="text-[10px] uppercase font-bold mt-1 px-2 py-0.5 rounded-full inline-block" 
                         style="background: ${hD.col}20; color: ${hD.col}">
                      ${hD.active ? (hD.risk >= 70 ? 'High Risk' : 'Active') : 'Revoked access'}
                    </div>
                  </div>
                </div>
              `)
          }
        })
        .on('mouseout', () => {
          if (highlightMode === 'all') {
             nodeGroup.selectAll('.outer-ring').style('opacity', 1)
             link.style('opacity', 1).attr('stroke', d => d.active ? '#cbd5e1' : '#f1f5f9')
             labelG.selectAll('text').style('opacity', d => d.isUser ? 1 : 0)
          }
          mapTooltip.style('opacity', 0)
        })

      const label = labelG.selectAll('text').data(nodes).enter().append('text')
        .attr('dx', d => d.r + 10)
        .attr('dy', 5)
        .attr('font-size', d => d.isUser ? '15px' : '12px')
        .attr('font-weight', d => d.isUser ? '800' : '600')
        .attr('fill', d => d.isUser ? '#1a1f36' : '#475569')
        .attr('font-family', 'Inter, sans-serif')
        .style('pointer-events', 'none')
        .style('opacity', d => d.isUser ? 1 : 0)
        .text(d => d.isUser ? d.label : d.label)

      simRef.current.on('tick', () => {
        link.attr('x1', d=>d.source.x).attr('y1', d=>d.source.y).attr('x2', d=>d.target.x).attr('y2', d=>d.target.y)
        nodeGroup.attr('transform', d => `translate(${d.x},${d.y})`)
        label.attr('x', d=>d.x).attr('y', d=>d.y)
      })

    // Soft zoom into center gracefully
    svg.call(zoom.transform, d3.zoomIdentity.translate(W/2, H/2).scale(0.3).translate(-W/2, -H/2))
    svg.transition().duration(1500).ease(d3.easeCubicOut).call(zoom.transform, d3.zoomIdentity.translate(W/2, H/2).scale(1).translate(-W/2, -H/2))

  }, [consents, userName, onNodeClick])

  // Separate effect for rapid state changes so we don't restart physics!
  useEffect(() => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)
    const nodeGroup = svg.selectAll('.node-group')
    const link = svg.selectAll('.link')

    const sq = (searchQuery || '').toLowerCase()

    nodeGroup.transition().duration(300).style('opacity', d => {
      if (!d) return 1
      if (d.isUser) return 1
      if (sq && !d.label.toLowerCase().includes(sq)) return 0.05
      if (highlightMode === 'all') return 1
      if (highlightMode === 'high') return (d.active && d.risk >= 70) ? 1 : 0.05
      if (highlightMode === 'revoked') return (!d.active) ? 1 : 0.05
      return 1
    })
    
    link.transition().duration(300).style('opacity', d => {
      if (!d) return 1
      if (sq && !d.target.label.toLowerCase().includes(sq)) return 0.01
      if (highlightMode === 'all') return 1
      if (highlightMode === 'high') return (d.target.active && d.target.risk >= 70) ? 0.8 : 0.02
      if (highlightMode === 'revoked') return (!d.target.active) ? 0.8 : 0.02
      return 1
    })
  }, [searchQuery, highlightMode])

  // Map Controls functions
  const handleZoom = (factor) => {
    if (svgRef.current && zoomRef.current) {
      d3.select(svgRef.current).transition().duration(300).call(zoomRef.current.scaleBy, factor)
    }
  }

  const handleReset = () => {
    if (svgRef.current && zoomRef.current) {
      const { w, h } = dimRef.current
      d3.select(svgRef.current).transition().duration(700)
        .call(zoomRef.current.transform, d3.zoomIdentity.translate(w/2, h/2).scale(1).translate(-w/2, -h/2))
      setHighlightMode('all')
    }
  }

  return (
    <div className="w-full h-full relative group">
      <svg ref={svgRef} width="100%" height="100%" style={{ cursor:'grab' }} />
      
      {/* ── Overlay Controls ────────────────────────────────────────────── */}
      <div className="absolute top-6 left-6 flex flex-col gap-3">
         <div className="bg-white/80 backdrop-blur-xl border border-gray-200/50 p-2 rounded-xl shadow-kanto flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <button title="Zoom In" onClick={()=>handleZoom(1.3)} className="p-1.5 hover:bg-gray-100 rounded-lg text-kanto-secondary hover:text-kanto-text transition-colors">
               <ZoomIn size={16} />
            </button>
            <div className="w-px h-4 bg-gray-200" />
            <button title="Zoom Out" onClick={()=>handleZoom(0.7)} className="p-1.5 hover:bg-gray-100 rounded-lg text-kanto-secondary hover:text-kanto-text transition-colors">
               <ZoomOut size={16} />
            </button>
            <div className="w-px h-4 bg-gray-200" />
            <button title="Reset Map" onClick={handleReset} className="p-1.5 hover:bg-gray-100 rounded-lg text-kanto-secondary hover:text-kanto-text transition-colors">
               <Maximize size={16} />
            </button>
         </div>
         
         <div className="bg-white/80 backdrop-blur-xl border border-gray-200/50 p-1.5 rounded-xl shadow-kanto flex flex-col gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300 delay-75">
            <button 
              onClick={() => setHighlightMode(highlightMode === 'high' ? 'all' : 'high')}
              className={`text-[10px] font-bold px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all ${highlightMode === 'high' ? 'bg-red-50 text-red-600' : 'hover:bg-gray-100 text-kanto-secondary'}`}>
              <div className="w-2 h-2 rounded-full bg-red-500" />
              Focus High Risk
            </button>
            <button 
              onClick={() => setHighlightMode(highlightMode === 'revoked' ? 'all' : 'revoked')}
              className={`text-[10px] font-bold px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all ${highlightMode === 'revoked' ? 'bg-amber-50 text-amber-600' : 'hover:bg-gray-100 text-kanto-secondary'}`}>
              <div className="w-2 h-2 rounded-full bg-amber-500" />
              Focus Revoked
            </button>
         </div>
      </div>

      <div className="absolute bottom-6 right-6 flex items-center gap-4 text-[11px] font-semibold text-kanto-secondary pointer-events-none bg-white/90 backdrop-blur-xl shadow-lg rounded-xl px-4 py-2 border border-gray-200/50 fade-in">
        {[['#10b981','Safe'],['#f59e0b','Medium Risk'],['#ef4444','Critical Risk']].map(([col,lbl]) => (
          <span key={lbl} className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full shadow-sm" style={{background:col}}/>
            {lbl}
          </span>
        ))}
      </div>
    </div>
  )
}
