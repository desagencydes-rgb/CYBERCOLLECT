/**
 * panels.js – Algorithm Output Renderers
 * Renders visual charts for all 5 algorithm levels inside the sidebar panels.
 */

// ─────────────────────────────────────────────
// LEVEL 1 – Dijkstra Results
// ─────────────────────────────────────────────
export function renderLevel1Output(data, container) {
    const { nodes, edges, shortest_paths, stats } = data;
    container.innerHTML = `
    <div class="stat-row"><span class="stat-label">ALGORITHM</span><span class="stat-value blue">${stats.algorithm}</span></div>
    <div class="stat-row"><span class="stat-label">NODES</span><span class="stat-value">${stats.total_nodes}</span></div>
    <div class="stat-row"><span class="stat-label">EDGES</span><span class="stat-value">${stats.total_edges}</span></div>
    <div class="stat-row"><span class="stat-label">MAX DIST</span><span class="stat-value orange">${stats.max_distance}</span></div>
    <div style="margin-top:8px; font-size:9px; color:var(--text-muted); letter-spacing:1px;">SHORTEST PATHS FROM DEPOT</div>
    ${shortest_paths.map(p => `
      <div class="stat-row fade-in">
        <span class="stat-label">→ ${nodes.find(n => n.id === p.to)?.nom || p.to}</span>
        <span class="stat-value">${p.distance}</span>
      </div>
    `).join('')}
  `;
}

// ─────────────────────────────────────────────
// LEVEL 2 – Truck Assignment Bar Charts
// ─────────────────────────────────────────────
export function renderLevel2Output(data, container) {
    const { assignments, stats } = data;
    container.innerHTML = `
    <div class="stat-row"><span class="stat-label">ALGORITHM</span><span class="stat-value blue">${stats.algorithm}</span></div>
    <div class="stat-row"><span class="stat-label">AVG LOAD</span><span class="stat-value">${stats.charge_moyenne}</span></div>
    <div class="stat-row"><span class="stat-label">STD DEV</span><span class="stat-value orange">${stats.ecart_type}</span></div>
    <div class="stat-row"><span class="stat-label">AVG UTIL</span><span class="stat-value">${stats.utilisation_moyenne_pct}%</span></div>
    <div style="margin-top:8px;"></div>
    ${assignments.map(a => {
        const pct = Math.min(a.pourcentage_utilisation, 100);
        const color = pct > 85 ? 'var(--neon-red)' : pct > 60 ? 'var(--neon-orange)' : 'var(--neon-green)';
        return `
        <div class="truck-bar-wrap fade-in">
          <div class="truck-bar-label">
            <span>Truck #${a.camion_id} (${a.zones_affectees.length} zones)</span>
            <span style="color:${color}">${a.pourcentage_utilisation}%</span>
          </div>
          <div class="truck-bar-track">
            <div class="truck-bar-fill" style="width:0%; background: linear-gradient(90deg, ${color}, ${color}88)"
                 data-target="${pct}"></div>
          </div>
        </div>
      `;
    }).join('')}
  `;
    // Animate bars
    setTimeout(() => {
        container.querySelectorAll('.truck-bar-fill').forEach(bar => {
            bar.style.width = bar.dataset.target + '%';
        });
    }, 50);
}

// ─────────────────────────────────────────────
// LEVEL 3 – Weekly Schedule Gantt
// ─────────────────────────────────────────────
export function renderLevel3Output(data, container) {
    const { schedule, kpis, stats } = data;

    const dayNames = Object.keys(schedule || {});
    const totalSlots = 13; // 6am to 19pm

    const colors = ['var(--l1-color)', 'var(--l2-color)', 'var(--l3-color)'];

    container.innerHTML = `
    <div class="stat-row"><span class="stat-label">ALGORITHM</span><span class="stat-value blue">${stats.algorithm}</span></div>
    <div class="stat-row"><span class="stat-label">DAYS PLANNED</span><span class="stat-value">${stats.jours_planifies}</span></div>
    ${kpis ? Object.entries(kpis).slice(0, 3).map(([k, v]) =>
        `<div class="stat-row"><span class="stat-label">${k.toUpperCase().replace(/_/g, ' ')}</span><span class="stat-value">${v}</span></div>`
    ).join('') : ''}
    <div style="margin-top:8px; font-size:9px; color:var(--text-muted); letter-spacing:1px;">WEEKLY SCHEDULE</div>
    ${dayNames.slice(0, 5).map((day, di) => {
        const slots = schedule[day] || [];
        return `
        <div class="gantt-row fade-in">
          <div class="gantt-label">${day.slice(0, 3).toUpperCase()}</div>
          <div class="gantt-track">
            ${slots.map((slot, si) => {
            const startPct = ((slot.debut || 6) - 6) / 13 * 100;
            const widthPct = ((slot.fin || slot.debut + 1) - (slot.debut || 6)) / 13 * 100;
            const c = colors[si % colors.length];
            return `<div class="gantt-fill" style="left:${startPct}%; width:${widthPct}%; background:${c}; opacity:0.8">
                C${slot.camion_id || si + 1}
              </div>`;
        }).join('')}
          </div>
        </div>
      `;
    }).join('')}
  `;
}

// ─────────────────────────────────────────────
// LEVEL 4 – VRP Routes + Convergence Chart
// ─────────────────────────────────────────────
export function renderLevel4Output(data, container) {
    const { routes, performance } = data;
    const gain = performance.amelioration_pct;
    const gainColor = gain > 0 ? 'var(--neon-green)' : 'var(--neon-red)';

    container.innerHTML = `
    <div class="stat-row"><span class="stat-label">ALGORITHM</span><span class="stat-value blue" style="font-size:9px">${performance.algorithm}</span></div>
    <div class="stat-row"><span class="stat-label">INITIAL DIST</span><span class="stat-value orange">${performance.distance_initiale}</span></div>
    <div class="stat-row"><span class="stat-label">OPTIMIZED</span><span class="stat-value">${performance.distance_optimisee}</span></div>
    <div class="stat-row"><span class="stat-label">GAIN</span><span class="stat-value" style="color:${gainColor}">▼ ${gain}%</span></div>
    <div style="margin-top:8px; font-size:9px; color:var(--text-muted); letter-spacing:1px;">OPTIMIZED ROUTES</div>
    ${routes.map((r, i) => {
        const colors = ['var(--neon-green)', 'var(--neon-blue)', 'var(--neon-purple)', 'var(--neon-orange)', 'var(--neon-red)'];
        const c = colors[i % colors.length];
        return `
        <div class="stat-row fade-in" style="border-left: 2px solid ${c}; padding-left:6px">
          <span class="stat-label">Truck #${r.camion_id} (${r.sequence.length} stops)</span>
          <span class="stat-value" style="color:${c}">${r.distance}</span>
        </div>
      `;
    }).join('')}
    <canvas id="conv-chart" class="convergence-chart" style="margin-top:8px"></canvas>
  `;

    // Draw convergence mini-chart
    setTimeout(() => drawConvergenceChart(performance), 50);
}

function drawConvergenceChart(perf) {
    const canvas = document.getElementById('conv-chart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    const w = canvas.width, h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    // Synthetic convergence curve
    const steps = 20;
    const start = perf.distance_initiale;
    const end = perf.distance_optimisee;

    const points = [];
    for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        const noise = Math.random() * (start - end) * 0.05;
        const y = start - (start - end) * (1 - Math.pow(1 - t, 2.5)) + noise;
        points.push({ x: (i / steps) * w, y: h - (y - end) / (start - end + 1) * (h - 10) });
    }

    // Fill
    const grad = ctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, 'rgba(0, 255, 157, 0.25)');
    grad.addColorStop(1, 'rgba(0, 255, 157, 0)');
    ctx.beginPath(); ctx.moveTo(0, h);
    points.forEach(p => ctx.lineTo(p.x, p.y));
    ctx.lineTo(w, h); ctx.closePath();
    ctx.fillStyle = grad; ctx.fill();

    // Line
    ctx.beginPath(); ctx.moveTo(points[0].x, points[0].y);
    points.slice(1).forEach(p => ctx.lineTo(p.x, p.y));
    ctx.strokeStyle = '#00ff9d'; ctx.lineWidth = 1.5;
    ctx.shadowColor = '#00ff9d'; ctx.shadowBlur = 8;
    ctx.stroke();
}

// ─────────────────────────────────────────────
// LEVEL 5 – Live Dashboard
// ─────────────────────────────────────────────
export function renderLevel5Output(data, container) {
    const { kpis, events, zone_levels, tick } = data;
    const hasAlerts = kpis.nb_alertes > 0;

    container.innerHTML = `
    <div class="sim-gauge-row">
      <div class="sim-gauge">
        <div class="sim-gauge-val ${hasAlerts ? 'alert' : ''}">${kpis.nb_alertes}</div>
        <div class="sim-gauge-key">ALERTS</div>
      </div>
      <div class="sim-gauge">
        <div class="sim-gauge-val">${kpis.efficacite_collecte}%</div>
        <div class="sim-gauge-key">EFFICIENCY</div>
      </div>
      <div class="sim-gauge">
        <div class="sim-gauge-val">${kpis.camions_actifs}</div>
        <div class="sim-gauge-key">TRUCKS</div>
      </div>
      <div class="sim-gauge">
        <div class="sim-gauge-val">${kpis.temps_ecoule_min}m</div>
        <div class="sim-gauge-key">ELAPSED</div>
      </div>
    </div>
    <div style="margin-top:8px; font-size:9px; color:var(--text-muted); letter-spacing:1px;">ZONE FILL LEVELS</div>
    ${zone_levels.map(z => {
        const pct = Math.min(z.fill_percent, 100);
        const color = z.alerte ? 'var(--neon-red)' : pct > 70 ? 'var(--neon-orange)' : 'var(--neon-green)';
        return `
        <div class="truck-bar-wrap fade-in">
          <div class="truck-bar-label">
            <span>Zone ${z.zone_id} ${z.alerte ? '⚠' : ''}</span>
            <span style="color:${color}">${pct.toFixed(0)}%</span>
          </div>
          <div class="truck-bar-track">
            <div class="truck-bar-fill" style="width:${pct}%; background:${color}"></div>
          </div>
        </div>
      `;
    }).join('')}
    <div style="margin-top:8px; font-size:9px; color:var(--text-muted); letter-spacing:1px;">EVENT FEED</div>
    <div class="event-feed">
      ${(events && events.length > 0) ? events.map(e =>
        `<div class="event-item ${e.type === 'ALERTE_REMPLISSAGE' ? 'alert-event' : ''}">
          [T${tick}] ${e.type} – Zone ${e.zone_id || '?'}
        </div>`
    ).join('') : '<div class="event-item">No events at this tick.</div>'}
    </div>
  `;
}
