/**
 * map3d.js – Three.js 3D Satellite City Map
 * FBI/satellite aesthetic with neon grid, animated routes, bloom post-processing
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

let scene, camera, renderer, composer, controls;
let animationId = null;
let nodeObjects = {};
let edgeObjects = [];
let routeAnimators = [];
let particleSystem = null;

const SCALE = 6;  // World units per graph unit
const ROUTE_COLORS = [0x00ff9d, 0x00d4ff, 0xbf5af2, 0xff9a00, 0xff3a5c, 0xf5ff00];

export function initMap() {
    const canvas = document.getElementById('map-canvas');
    const container = document.getElementById('map-container');

    // Renderer
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setClearColor(0x030b0f);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;

    // Scene
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x030b0f, 0.012);

    // Camera
    camera = new THREE.PerspectiveCamera(50, container.clientWidth / container.clientHeight, 0.1, 500);
    camera.position.set(0, 45, 55);
    camera.lookAt(0, 0, 0);

    // Controls
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 15;
    controls.maxDistance = 120;
    controls.maxPolarAngle = Math.PI / 2.2;

    // Post-processing
    composer = new EffectComposer(renderer);
    composer.addPass(new RenderPass(scene, camera));
    const bloomPass = new UnrealBloomPass(
        new THREE.Vector2(container.clientWidth, container.clientHeight),
        1.4,   // strength
        0.6,   // radius
        0.15   // threshold
    );
    composer.addPass(bloomPass);
    composer.addPass(new OutputPass());

    // Build scene
    _buildGrid();
    _buildAmbientParticles();
    _buildLights();

    // Resize handler
    window.addEventListener('resize', _onResize);

    // Start render loop
    _animate();

    // Hide loader after short delay
    setTimeout(() => {
        const loader = document.getElementById('map-loading');
        if (loader) loader.classList.add('hidden');
    }, 1200);

    // Dispatch ready event
    window.dispatchEvent(new CustomEvent('map3d:ready'));
}

function _buildGrid() {
    // Ground plane
    const groundGeo = new THREE.PlaneGeometry(120, 120);
    const groundMat = new THREE.MeshBasicMaterial({
        color: 0x030b0f,
        transparent: true,
        opacity: 1,
    });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    scene.add(ground);

    // Neon grid lines
    const gridHelper = new THREE.GridHelper(100, 40, 0x00d4ff, 0x001830);
    gridHelper.material.opacity = 0.4;
    gridHelper.material.transparent = true;
    scene.add(gridHelper);

    // Secondary subtle grid
    const grid2 = new THREE.GridHelper(100, 10, 0x00ff9d, 0x001830);
    grid2.material.opacity = 0.15;
    grid2.material.transparent = true;
    scene.add(grid2);

    // Sector boundary lines (cyber borders)
    const borderMat = new THREE.LineBasicMaterial({ color: 0x00d4ff, transparent: true, opacity: 0.3 });
    const borderGeo = new THREE.BufferGeometry();
    const pts = [
        -50, 0.05, -50, 50, 0.05, -50,
        50, 0.05, 50, -50, 0.05, 50,
        -50, 0.05, -50,
    ].reduce((acc, v, i) => { acc.push(v); return acc; }, []);
    borderGeo.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
    scene.add(new THREE.Line(borderGeo, borderMat));
}

function _buildAmbientParticles() {
    const count = 600;
    const geo = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
        positions[i * 3] = (Math.random() - 0.5) * 100;
        positions[i * 3 + 1] = Math.random() * 30;
        positions[i * 3 + 2] = (Math.random() - 0.5) * 100;
    }
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const mat = new THREE.PointsMaterial({
        color: 0x00d4ff, size: 0.15,
        transparent: true, opacity: 0.35,
        sizeAttenuation: true,
    });
    particleSystem = new THREE.Points(geo, mat);
    scene.add(particleSystem);
}

function _buildLights() {
    scene.add(new THREE.AmbientLight(0x001830, 0.5));
    const dirLight = new THREE.DirectionalLight(0x00d4ff, 0.5);
    dirLight.position.set(10, 30, 10);
    scene.add(dirLight);
}

function _graphToWorld(x, y) {
    // Center around 0,0 by normalizing the grid (0-9 range → -27 to +27)
    return { x: (x - 4.5) * SCALE, z: (y - 4.5) * SCALE };
}

export function renderGraph(nodes, edges, highlightPath = null) {
    _clearGraph();

    // Draw edges
    edges.forEach(edge => {
        const from = nodes.find(n => n.id === edge.from);
        const to = nodes.find(n => n.id === edge.to);
        if (!from || !to) return;

        const fp = _graphToWorld(from.x, from.y);
        const tp = _graphToWorld(to.x, to.y);
        const isHighlighted = highlightPath && _pathContainsEdge(highlightPath, edge.from, edge.to);

        const pts = [new THREE.Vector3(fp.x, 0.1, fp.z), new THREE.Vector3(tp.x, 0.1, tp.z)];
        const geo = new THREE.BufferGeometry().setFromPoints(pts);
        const mat = new THREE.LineBasicMaterial({
            color: isHighlighted ? 0x00ff9d : 0x00305a,
            transparent: true,
            opacity: isHighlighted ? 0.9 : 0.5,
        });
        const line = new THREE.Line(geo, mat);
        scene.add(line);
        edgeObjects.push(line);
    });

    // Draw nodes
    nodes.forEach(node => {
        const pos = _graphToWorld(node.x, node.y);
        const isDepot = node.type === 'depot';

        const geo = new THREE.SphereGeometry(isDepot ? 0.9 : 0.55, 12, 12);
        const color = isDepot ? 0xff9a00 : 0x00d4ff;
        const mat = new THREE.MeshStandardMaterial({
            color,
            emissive: color,
            emissiveIntensity: 0.8,
            roughness: 0.2,
        });
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.set(pos.x, 0.55, pos.z);
        mesh.userData = { nodeId: node.id, nom: node.nom };
        scene.add(mesh);
        nodeObjects[node.id] = mesh;

        // Vertical beacon beam
        const beamGeo = new THREE.CylinderGeometry(0.05, 0.05, 6, 6);
        const beamMat = new THREE.MeshBasicMaterial({
            color, transparent: true, opacity: 0.15,
        });
        const beam = new THREE.Mesh(beamGeo, beamMat);
        beam.position.set(pos.x, 3, pos.z);
        scene.add(beam);
        edgeObjects.push(beam);
    });
}

export function renderRoutes(routes) {
    _clearRoutes();
    routes.forEach((route, idx) => {
        if (!route.nodes || route.nodes.length < 2) return;
        const color = ROUTE_COLORS[idx % ROUTE_COLORS.length];
        _animateRoute(route.nodes, color, idx * 0.3);
    });
}

function _animateRoute(routeNodes, color, delay) {
    const worldPts = routeNodes.map(n => {
        const p = _graphToWorld(n.x, n.y);
        return new THREE.Vector3(p.x, 0.4, p.z);
    });

    // Draw static path
    const geo = new THREE.BufferGeometry().setFromPoints(worldPts);
    const mat = new THREE.LineBasicMaterial({
        color, transparent: true, opacity: 0.6, linewidth: 1,
    });
    const line = new THREE.Line(geo, mat);
    scene.add(line);
    routeAnimators.push(line);

    // Animated "truck" sphere
    const sphereGeo = new THREE.SphereGeometry(0.4, 8, 8);
    const sphereMat = new THREE.MeshStandardMaterial({
        color, emissive: color, emissiveIntensity: 1.2,
    });
    const truck = new THREE.Mesh(sphereGeo, sphereMat);
    truck.position.copy(worldPts[0]);
    scene.add(truck);
    routeAnimators.push(truck);

    // Drive animation
    let segIdx = 0, t = 0;
    const speed = 0.008;
    let started = false;
    const startTime = performance.now() + delay * 1000;

    const drive = (now) => {
        if (now < startTime) { requestAnimationFrame(drive); return; }
        if (!started) { started = true; }

        t += speed;
        if (t >= 1) {
            t = 0;
            segIdx = (segIdx + 1) % (worldPts.length - 1);
        }
        const a = worldPts[segIdx];
        const b = worldPts[segIdx + 1];
        truck.position.lerpVectors(a, b, t);
        if (routeAnimators.includes(truck)) requestAnimationFrame(drive);
    };
    requestAnimationFrame(drive);
}

export function highlightAlertZones(zoneIds, nodes) {
    zoneIds.forEach(zid => {
        const mesh = nodeObjects[zid];
        if (mesh) {
            mesh.material.color.setHex(0xff3a5c);
            mesh.material.emissive.setHex(0xff3a5c);
        }
    });
}

export function resetNodeColors(nodes) {
    nodes.forEach(node => {
        const mesh = nodeObjects[node.id];
        if (mesh) {
            const color = node.type === 'depot' ? 0xff9a00 : 0x00d4ff;
            mesh.material.color.setHex(color);
            mesh.material.emissive.setHex(color);
        }
    });
}

function _clearGraph() {
    edgeObjects.forEach(o => scene.remove(o));
    edgeObjects = [];
    Object.values(nodeObjects).forEach(o => scene.remove(o));
    nodeObjects = {};
    _clearRoutes();
}

function _clearRoutes() {
    routeAnimators.forEach(o => scene.remove(o));
    routeAnimators = [];
}

function _pathContainsEdge(paths, from, to) {
    return paths.some(p => {
        for (let i = 0; i < p.path.length - 1; i++) {
            if ((p.path[i] === from && p.path[i + 1] === to) ||
                (p.path[i] === to && p.path[i + 1] === from)) return true;
        }
        return false;
    });
}

function _animate() {
    animationId = requestAnimationFrame(_animate);
    const t = performance.now() * 0.001;

    controls.update();

    // Rotate particles slowly
    if (particleSystem) particleSystem.rotation.y = t * 0.03;

    // Pulse node sizes
    Object.values(nodeObjects).forEach((mesh, i) => {
        const pulse = 1 + 0.06 * Math.sin(t * 2 + i * 0.8);
        mesh.scale.setScalar(pulse);
    });

    composer.render();
}

function _onResize() {
    const container = document.getElementById('map-container');
    if (!container) return;
    const w = container.clientWidth, h = container.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
    composer.setSize(w, h);
}
