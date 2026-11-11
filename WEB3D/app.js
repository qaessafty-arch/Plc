// SPM-420 interactive viewer. Model: model/spm420.glb (one named node per part, millimetres,
// CAD Z-up under a root node rotated to glTF Y-up). Part data: model/parts.json.
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const $ = (id) => document.getElementById(id);
const canvas = $("c");
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(38, 1, 0.05, 200);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = !reduceMotion;
controls.dampingFactor = 0.08;
controls.autoRotateSpeed = 0.6;

scene.add(new THREE.HemisphereLight(0xdfe8ee, 0x1a1f24, 1.4));
const key = new THREE.DirectionalLight(0xffffff, 2.2); key.position.set(-6, 9, 7); scene.add(key);
const rim = new THREE.DirectionalLight(0x9fc4ff, 0.9); rim.position.set(7, 5, -8); scene.add(rim);

const grid = new THREE.GridHelper(12, 12, 0x3d8bff, 0x2a3238);
grid.material.opacity = 0.55; grid.material.transparent = true;
scene.add(grid);

const parts = new Map();          // id -> {info, node, base, meshes}
let selected = null, explode = 0, envelopeText = "";

function resize() {
  const r = canvas.getBoundingClientRect();
  renderer.setSize(r.width, r.height, false);
  camera.aspect = r.width / Math.max(1, r.height);
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(canvas);

// ---------- camera views (world: X right, Y up, Z toward the operator) ----------
let center = new THREE.Vector3(), radius = 3;
const VIEWS = {
  iso:    () => ({ pos: new THREE.Vector3(-0.85, 0.55, 1.0), target: center, dist: 2.9 }),
  front:  () => ({ pos: new THREE.Vector3(0, 0.08, 1), target: center, dist: 2.5 }),
  side:   () => ({ pos: new THREE.Vector3(1, 0.08, 0), target: center, dist: 2.4 }),
  top:    () => ({ pos: new THREE.Vector3(0, 1, 0.001), target: center, dist: 2.6 }),
  bagger: () => ({ pos: new THREE.Vector3(-0.5, 0.25, 1), target: new THREE.Vector3(0, 0.85, 0.1), dist: 0.95 }),
};
let tween = null;
function goTo(pos, target) {
  if (reduceMotion) { camera.position.copy(pos); controls.target.copy(target); controls.update(); return; }
  tween = { p0: camera.position.clone(), t0: controls.target.clone(), p1: pos, t1: target.clone(), k: 0 };
}
function setView(name) {
  const v = VIEWS[name]();
  goTo(v.target.clone().add(v.pos.clone().normalize().multiplyScalar(radius * v.dist)), v.target);
  document.querySelectorAll(".views button").forEach((b) => b.classList.toggle("on", b.dataset.view === name));
}
document.querySelectorAll(".views button").forEach((b) => b.addEventListener("click", () => setView(b.dataset.view)));
$("c").addEventListener("dblclick", () => setView("iso"));

// ---------- load ----------
const [gltf, data] = await Promise.all([
  new GLTFLoader().loadAsync("model/spm420.glb", (e) => { if (e.total) $("loading").textContent = `Loading model… ${Math.round((100 * e.loaded) / e.total)} %`; }),
  fetch("model/parts.json").then((r) => r.json()),
]).catch((err) => { $("loading").textContent = "The model could not be loaded. Reload the page to try again."; throw err; });

const model = gltf.scene;
model.scale.setScalar(0.001);                      // mm -> m
scene.add(model);
for (const info of data.parts) {
  const node = model.getObjectByName(info.id);
  if (!node) continue;
  const meshes = [];
  node.traverse((o) => {
    if (!o.isMesh) return;
    const c = new THREE.Color(...info.color);
    const film = info.id === "B17_film_web" || info.id === "B02_film_roll";
    o.material = new THREE.MeshStandardMaterial({
      color: c, metalness: film ? 0.0 : 0.35, roughness: film ? 0.7 : 0.5, side: THREE.DoubleSide,
    });
    o.userData.partId = info.id;
    meshes.push(o);
  });
  parts.set(info.id, { info, node, base: node.position.clone(), meshes });
}
const box = new THREE.Box3().setFromObject(model);
box.getCenter(center); radius = box.getSize(new THREE.Vector3()).length() / 2;
grid.position.y = box.min.y;
const env = data.envelope_mm;
envelopeText = `Envelope ${env[0]} × ${env[1]} × ${env[2]} mm`;
$("dims").textContent = envelopeText;
$("loading").hidden = true;
{ const v = VIEWS.iso(); camera.position.copy(center.clone().add(v.pos.normalize().multiplyScalar(radius * v.dist))); controls.target.copy(center); controls.update(); }

// ---------- part list ----------
const plist = $("plist");
const groups = [...new Set(data.parts.map((p) => p.group))];
for (const g of groups) {
  const head = document.createElement("li"); head.className = "grouphead"; head.textContent = g; plist.appendChild(head);
  for (const info of data.parts.filter((p) => p.group === g)) {
    const li = document.createElement("li"); li.dataset.id = info.id;
    const cb = document.createElement("input"); cb.type = "checkbox"; cb.checked = true; cb.id = "v_" + info.id;
    cb.setAttribute("aria-label", `Show ${info.label}`);
    cb.addEventListener("change", () => { parts.get(info.id).node.visible = cb.checked; });
    const sw = document.createElement("span"); sw.className = "sw";
    sw.style.background = `rgb(${info.color.map((v) => Math.round(v * 255)).join(",")})`;
    const nb = document.createElement("button"); nb.type = "button"; nb.className = "pn"; nb.textContent = info.label;
    nb.addEventListener("click", () => select(info.id, true));
    li.append(cb, sw, nb); plist.appendChild(li);
  }
}

// ---------- selection ----------
function select(id, focus = false) {
  if (selected) parts.get(selected).meshes.forEach((m) => m.material.emissive.setHex(0x000000));
  selected = id;
  document.querySelectorAll("#plist li[data-id]").forEach((li) => li.classList.toggle("sel", li.dataset.id === id));
  if (!id) { $("infoNone").hidden = false; $("infoBody").hidden = true; $("dims").textContent = envelopeText; return; }
  const p = parts.get(id);
  p.meshes.forEach((m) => m.material.emissive.setHex(0x1d4fa8));
  const i = p.info;
  $("iName").textContent = i.label; $("iGroup").textContent = i.group; $("iMat").textContent = i.material;
  $("iBox").textContent = i.bbox_mm.map((v) => Math.round(v)).join(" × ") + " mm";
  $("iMass").textContent = `≈ ${i.mass_kg} kg (estimate)`; $("iId").textContent = i.id;
  $("infoNone").hidden = true; $("infoBody").hidden = false;
  $("dims").textContent = `${i.label}: ${i.bbox_mm.map((v) => Math.round(v)).join(" × ")} mm`;
  if (focus) {
    p.node.visible = true; $("v_" + id).checked = true;
    if (["Sealing", "Film pull", "Forming", "Film system"].includes(i.group) && !$("ghost").checked) { $("ghost").checked = true; $("ghost").dispatchEvent(new Event("change")); }
    const b = new THREE.Box3().setFromObject(p.node), c = b.getCenter(new THREE.Vector3());
    const r = Math.max(0.25, b.getSize(new THREE.Vector3()).length() * 0.9);
    const dir = camera.position.clone().sub(controls.target).normalize();
    goTo(c.clone().add(dir.multiplyScalar(r * 1.6)), c);
  }
}
$("isolate").addEventListener("click", () => {
  if (!selected) return;
  for (const [id, p] of parts) { p.node.visible = id === selected; $("v_" + id).checked = p.node.visible; }
});
$("showall").addEventListener("click", () => { for (const [id, p] of parts) { p.node.visible = true; $("v_" + id).checked = true; } });

const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
let down = null;
canvas.addEventListener("pointerdown", (e) => { down = [e.clientX, e.clientY]; });
canvas.addEventListener("pointerup", (e) => {
  if (!down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 5) return;   // was a drag
  const r = canvas.getBoundingClientRect();
  ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(ndc, camera);
  const vis = [...parts.values()].filter((p) => p.node.visible).flatMap((p) => p.meshes);
  const hit = ray.intersectObjects(vis, false)[0];
  select(hit ? hit.object.userData.partId : null);
});

// ---------- explode, toggles ----------
function applyExplode() {
  for (const p of parts.values()) {
    const e = p.info.explode;
    p.node.position.set(p.base.x + e[0] * explode, p.base.y + e[1] * explode, p.base.z + e[2] * explode);
  }
}
$("explode").addEventListener("input", (e) => { explode = e.target.value / 100; $("exv").textContent = `${e.target.value} %`; applyExplode(); });
$("ghost").addEventListener("change", (e) => {
  for (const id of ["B14_guard_doors", "B15_electrical_cabinet"]) {
    parts.get(id)?.meshes.forEach((m) => { m.material.transparent = e.target.checked; m.material.opacity = e.target.checked ? 0.18 : 1; m.material.depthWrite = !e.target.checked; });
  }
});
$("spin").addEventListener("change", (e) => { controls.autoRotate = e.target.checked; });
$("floor").addEventListener("change", (e) => { grid.visible = e.target.checked; });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") select(null); });

// ---------- loop ----------
function frame() {
  if (tween) {
    tween.k = Math.min(1, tween.k + 0.06);
    const s = tween.k * tween.k * (3 - 2 * tween.k);
    camera.position.lerpVectors(tween.p0, tween.p1, s);
    controls.target.lerpVectors(tween.t0, tween.t1, s);
    if (tween.k >= 1) tween = null;
  }
  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}
resize();
frame();
