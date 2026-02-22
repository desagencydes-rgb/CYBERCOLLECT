/**
 * app.js – Main Application Controller
 * Orchestrates the 3D map, algorithm panels, simulation loop, and KPI bar.
 */
import { initMap, renderGraph, renderRoutes, highlightAlertZones } from './map3d.js';
import {
    renderLevel1Output,
    renderLevel2Output,
    renderLevel3Output,
    renderLevel4Output,
    renderLevel5Output,
} from './panels.js';
import { initChat, setContext } from './chat.js';

const API = '';  // Same-origin

// ─── State ───────────────────────────────────────────────────────
let currentNodes = [];
let simInterval = null;
let simRunning = false;

// ─── Boot ─────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
    initMap();
    initChat();
    initClock();
    initPanelToggles();
    bindButtons();
});

// ─── Clock ────────────────────────────────────────────────────────
function initClock() {
    const el = document.getElementById('hud-clock');
    setInterval(() => {
        el.textContent = new Date().toLocaleTimeString('fr-FR', { hour12: false });
    }, 1000);
}

// ─── Panel accordion ──────────────────────────────────────────────
function initPanelToggles() {
    document.querySelectorAll('.panel-header').forEach(header => {
        header.addEventListener('click', () => {
            header.closest('.level-panel').classList.toggle('collapsed');
        });
    });
}

// ─── Buttons ──────────────────────────────────────────────────────
function bindButtons() {
    document.getElementById('btn-l1').addEventListener('click', runLevel1);
    document.getElementById('btn-l2').addEventListener('click', runLevel2);
    document.getElementById('btn-l3').addEventListener('click', runLevel3);
    document.getElementById('btn-l4').addEventListener('click', runLevel4);
    document.getElementById('btn-sim-start').addEventListener('click', toggleSimulation);
    document.getElementById('btn-sim-reset').addEventListener('click', resetSimulation);
}

// ─── Level 1 ──────────────────────────────────────────────────────
async function runLevel1() {
    const btn = document.getElementById('btn-l1');
    const out = document.getElementById('out-l1');
    setButtonLoading(btn, true);
    setActiveLevel('L1 // DIJKSTRA');

    try {
        const data = await post('/api/level1/run');
        currentNodes = data.nodes;
        renderGraph(data.nodes, data.edges, data.shortest_paths);
        renderLevel1Output(data, out);
        setContext('l1', data);
        updateKPIs({ nodes: data.stats.total_nodes });
    } catch (e) { showError(out, e); }
    finally { setButtonLoading(btn, false); }
}

// ─── Level 2 ──────────────────────────────────────────────────────
async function runLevel2() {
    const btn = document.getElementById('btn-l2');
    const out = document.getElementById('out-l2');
    setButtonLoading(btn, true);
    setActiveLevel('L2 // TRUCK ASSIGNMENT');

    try {
        const data = await post('/api/level2/run');
        // Color nodes by truck assignment on the map
        if (currentNodes.length) {
            const colors = [0x00ff9d, 0x00d4ff, 0xbf5af2, 0xff9a00, 0xff3a5c];
            data.assignments.forEach((a, i) => {
                a.zones_affectees.forEach(zid => {
                    const node = currentNodes.find(n => n.id === zid);
                    if (node) node._assignColor = colors[i % colors.length];
                });
            });
        }
        renderLevel2Output(data, out);
        setContext('l2', data);
        updateKPIs({ nodes: data.assignments.length });
    } catch (e) { showError(out, e); }
    finally { setButtonLoading(btn, false); }
}

// ─── Level 3 ──────────────────────────────────────────────────────
async function runLevel3() {
    const btn = document.getElementById('btn-l3');
    const out = document.getElementById('out-l3');
    setButtonLoading(btn, true);
    setActiveLevel('L3 // WEEKLY SCHEDULE');

    try {
        const data = await post('/api/level3/run');
        renderLevel3Output(data, out);
        setContext('l3', data);
    } catch (e) { showError(out, e); }
    finally { setButtonLoading(btn, false); }
}

// ─── Level 4 ──────────────────────────────────────────────────────
async function runLevel4() {
    const btn = document.getElementById('btn-l4');
    const out = document.getElementById('out-l4');
    const nbTrucks = parseInt(document.getElementById('vrp-trucks').value) || 3;
    setButtonLoading(btn, true);
    setActiveLevel('L4 // VRP OPTIMIZATION');

    try {
        const data = await post('/api/level4/run', { nombre_camions: nbTrucks });
        currentNodes = data.nodes;
        renderGraph(data.nodes, data.edges);
        renderRoutes(data.routes);
        renderLevel4Output(data, out);
        setContext('l4', data);
        updateKPIs({
            nodes: data.nodes.length,
            routes: data.routes.length,
            gain: data.performance.amelioration_pct + '%',
        });
    } catch (e) { showError(out, e); }
    finally { setButtonLoading(btn, false); }
}

// ─── Level 5 – Simulation ─────────────────────────────────────────
async function toggleSimulation() {
    if (simRunning) {
        clearInterval(simInterval);
        simRunning = false;
        document.getElementById('btn-sim-start').textContent = '▶ START SIM';
        return;
    }
    setActiveLevel('L5 // LIVE SIMULATION');
    document.getElementById('btn-sim-start').textContent = '⏸ PAUSE SIM';
    simRunning = true;
    await tickSimulation();
    simInterval = setInterval(tickSimulation, 2500);
}

async function tickSimulation() {
    const out = document.getElementById('out-l5');
    try {
        const data = await post('/api/level5/tick');
        renderLevel5Output(data, out);
        setContext('l5', data);

        // Alert zones on map
        if (currentNodes.length && data.kpis.zones_critiques.length) {
            highlightAlertZones(data.kpis.zones_critiques, currentNodes);
            setTimeout(() => {
                // Reset after 1.5s if still simulating
            }, 1500);
        }

        updateKPIs({
            alerts: data.kpis.nb_alertes,
            efficiency: data.kpis.efficacite_collecte + '%',
            tick: data.tick,
        });
    } catch (e) { showError(out, e); }
}

async function resetSimulation() {
    if (simRunning) {
        clearInterval(simInterval);
        simRunning = false;
        document.getElementById('btn-sim-start').textContent = '▶ START SIM';
    }
    try {
        await post('/api/level5/reset');
        document.getElementById('out-l5').innerHTML =
            '<div class="output-placeholder"><span class="ph-icon">⬡</span><span>Simulation reset.</span></div>';
        updateKPIs({ alerts: 0, efficiency: '100%', tick: 0 });
    } catch { }
}

// ─── Helpers ──────────────────────────────────────────────────────
async function post(url, body = {}) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

function setButtonLoading(btn, loading) {
    btn.disabled = loading;
    btn.classList.toggle('loading', loading);
}

function setActiveLevel(label) {
    const el = document.getElementById('map-active-level');
    if (el) el.textContent = label;
}

function showError(container, err) {
    container.innerHTML = `<div class="stat-row" style="color:var(--neon-red)">
    ERROR: ${err.message || err}
  </div>`;
}

function updateKPIs({ nodes, routes, gain, alerts, efficiency, tick } = {}) {
    if (nodes !== undefined) document.getElementById('kpi-nodes').textContent = nodes;
    if (routes !== undefined) document.getElementById('kpi-routes').textContent = routes;
    if (gain !== undefined) document.getElementById('kpi-gain').textContent = gain;
    if (alerts !== undefined) document.getElementById('kpi-alerts').textContent = alerts;
    if (efficiency !== undefined) document.getElementById('kpi-eff').textContent = efficiency;
    if (tick !== undefined) document.getElementById('kpi-tick').textContent = tick;
}
