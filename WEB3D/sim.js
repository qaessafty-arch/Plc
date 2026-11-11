// On-model process simulation. Motion of jaws, seal bar and film comes from model/cycle.json,
// one cycle of the PLC-logic simulation (SIMULATION/). Product flow (buckets, falling chips,
// bags) is drawn to the same timing. Simulated, not measured.
// All positions are CAD coordinates in mm (X right, Y to the rear, Z up) under the model root.
import * as THREE from "three";

const STEP_NAME = { 20: "Pull film", 30: "Settle", 40: "Close jaws", 50: "Seal and cut", 60: "Open jaws", 70: "Cycle end", 10: "Wait, then dump" };
const GHOST = { E01_z_bucket_elevator: 0.16, W01_multihead_weigher: 0.3, B06_forming_tube: 0.22, B07_forming_collar: 0.3,
                B08_infeed_funnel: 0.22, B14_guard_doors: 0.12, E02_infeed_hopper: 0.4 };

export function createSim({ parts, cyc, ui }) {
  const root = parts.get("B01_main_frame").node.parent;
  const P = cyc.period, R = cyc.rows, JZ = cyc.jaw_z, L = cyc.bag_len, BW = cyc.bag_w;
  const grp = new THREE.Group(); grp.visible = false; root.add(grp);
  const chipMat = new THREE.MeshStandardMaterial({ color: 0xe0a82e, roughness: 0.8 });
  const bagMat = new THREE.MeshStandardMaterial({ color: 0xd9e4ec, roughness: 0.35, metalness: 0.5 });
  const bucketMat = new THREE.MeshStandardMaterial({ color: 0x6f8fb0, roughness: 0.6 });
  const litMat = new THREE.MeshStandardMaterial({ color: 0x3d8bff, emissive: 0x3d8bff, emissiveIntensity: 1.4 });

  // ---- trace sampling
  const row = (t) => { let lo = 0, hi = R.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (R[m][0] <= t) lo = m; else hi = m - 1; } return lo; };
  const val = (t, k) => { const i = row(t), a = R[i], b = R[Math.min(i + 1, R.length - 1)]; const f = b[0] > a[0] ? (t - a[0]) / (b[0] - a[0]) : 0; return a[k] + (b[k] - a[k]) * Math.min(1, Math.max(0, f)); };
  const cutT = R.find((r) => r[4] >= 0.99)[0];
  const closedT = R.find((r) => r[2] >= 0.999)[0];

  // ---- elevator buckets along the Z path
  const PATH = [[-2800, 450], [-1450, 450], [-1450, 3600], [-120, 3600]];      // (x, z)
  const segLen = PATH.slice(1).map((p, i) => Math.hypot(p[0] - PATH[i][0], p[1] - PATH[i][1]));
  const pathLen = segLen.reduce((a, b) => a + b, 0);
  const onPath = (d) => { for (let i = 0; i < segLen.length; i++) { if (d <= segLen[i]) { const f = d / segLen[i]; return [PATH[i][0] + (PATH[i + 1][0] - PATH[i][0]) * f, PATH[i][1] + (PATH[i + 1][1] - PATH[i][1]) * f]; } d -= segLen[i]; } return PATH[PATH.length - 1]; };
  const NB = 16, buckets = [];
  for (let i = 0; i < NB; i++) {
    const b = new THREE.Group();
    b.add(new THREE.Mesh(new THREE.BoxGeometry(170, 330, 110), bucketMat));
    const fill = new THREE.Mesh(new THREE.BoxGeometry(150, 310, 40), chipMat); fill.position.z = 55; b.add(fill);
    grp.add(b); buckets.push(b);
  }

  // ---- chips: one pool, reused
  const chipGeo = new THREE.CylinderGeometry(26, 26, 5, 8);
  const chips = Array.from({ length: 90 }, () => { const m = new THREE.Mesh(chipGeo, chipMat); m.visible = false; grp.add(m); return m; });
  let chipI = 0;
  const flights = [];                                   // {mesh, t0, dur, from, via, to}
  function launch(from, via, to, t0, dur) { const m = chips[chipI++ % chips.length]; m.rotation.set(Math.random() * 3, Math.random() * 3, 0); flights.push({ m, t0, dur, from, via, to }); }

  // ---- weigher heads (markers that light up when selected)
  const WB = cyc.weigher_base_z, heads = [];
  for (let i = 0; i < 10; i++) {
    const a = (i * 36 * Math.PI) / 180, m = new THREE.Mesh(new THREE.BoxGeometry(150, 140, 220), litMat);
    m.position.set(450 * Math.cos(a), 450 * Math.sin(a), WB + 505); m.rotation.z = a; m.visible = false; grp.add(m); heads.push(m);
  }
  let headsOffAt = -1;

  // ---- bags
  const bagGeo = new THREE.SphereGeometry(1, 20, 14);
  const hanging = new THREE.Mesh(bagGeo, bagMat); grp.add(hanging);
  const pile = new THREE.Mesh(new THREE.SphereGeometry(1, 12, 8), chipMat); grp.add(pile);   // charge resting on the jaws
  const free = [];                                       // bags released from the jaws
  const convZ = (x) => 250 + 80 + ((x + 250) / 1800) * 450 + 30;

  let simT = 0, lastCycle = -1, bags = 0, running = false, speed = 0.5, saved = null;

  function ghost(on) {
    if (on) { saved = new Map();
      for (const [id, op] of Object.entries(GHOST)) parts.get(id)?.meshes.forEach((m) => { saved.set(m, [m.material.transparent, m.material.opacity, m.material.depthWrite]); m.material.transparent = true; m.material.opacity = op; m.material.depthWrite = false; });
    } else if (saved) { for (const [m, s] of saved) { m.material.transparent = s[0]; m.material.opacity = s[1]; m.material.depthWrite = s[2]; } saved = null; }
  }

  function dump(tNow) {                                  // weigher discharge: 4 heads, 12 chip packets over string_s
    const pick = [...heads.keys()].sort(() => Math.random() - 0.5).slice(0, 4);
    heads.forEach((h, i) => (h.visible = pick.includes(i))); headsOffAt = tNow + 0.35;
    for (let j = 0; j < 12; j++) {
      const h = heads[pick[j % 4]].position;
      launch([h.x, h.y, WB + 400], [0, 0, 1800], [(Math.random() - 0.5) * 50, (Math.random() - 0.5) * 30, JZ + 30], tNow + (cyc.string_s * j) / 11, cyc.fall_s);
    }
  }

  function pose(t) {                                     // everything that is a pure function of cycle time
    const jaw = val(t, 2), vs = val(t, 3), s = val(t, 5);
    const f = parts.get("B13a_front_jaw"), r = parts.get("B13b_rear_jaw"), v = parts.get("B12_vertical_seal");
    if (f) f.node.position.y = f.base.y + 35 * jaw;
    if (r) r.node.position.y = r.base.y - 35 * jaw;
    if (v) v.node.position.y = v.base.y - 18 * (1 - vs);
    // bag below the jaws: grows during the pull, hangs until the knife cuts
    if (t < cutT && s > 4) { hanging.visible = true; hanging.scale.set(BW / 2 * 0.78, 34, s / 2); hanging.position.set(0, 0, JZ - s / 2); } else hanging.visible = false;
    return { jaw, s };
  }

  function update(dt) {
    if (!running) return;
    simT += dt * speed;
    const c = Math.floor(simT / P), t = simT - c * P;
    const { jaw } = pose(t);
    if (c !== lastCycle) { lastCycle = c; }
    // dump request: dump_t is negative (before the pull) -> late in the previous cycle
    const dAbs = (k) => k * P + cyc.dump_t + P;
    if (update.nextDump === undefined) update.nextDump = 0;
    while (simT >= dAbs(update.nextDump)) { dump(dAbs(update.nextDump)); update.nextDump++; }
    if (headsOffAt > 0 && simT > headsOffAt) { heads.forEach((h) => (h.visible = false)); headsOffAt = -1; }
    // knife: release the hanging bag once per cycle
    if (update.cutDone !== c && t >= cutT && c > 0) { update.cutDone = c; bags++; const m = new THREE.Mesh(bagGeo, bagMat); grp.add(m); free.push({ m, t0: simT }); }
    // charge resting on the closed jaws / carried down in the new bag
    const landA = cyc.dump_t + cyc.fall_s, landB = landA + cyc.string_s;
    let grams = 0; if (c > 0 || t > landA) grams = t < landA ? 1 : Math.min(1, (t - landA) / (landB - landA));
    if (t < closedT) grams = 0;
    pile.visible = grams > 0.02; pile.scale.set(40 * grams + 6, 30, 26 * grams + 4); pile.position.set(0, 0, JZ + 30 + 20 * grams);
    // chips in flight (weigher -> jaws, elevator -> weigher)
    for (let i = flights.length - 1; i >= 0; i--) {
      const fl = flights[i], k = (simT - fl.t0) / fl.dur;
      if (k < 0) { fl.m.visible = false; continue; }
      if (k >= 1) { fl.m.visible = false; flights.splice(i, 1); continue; }
      const q = k * k, a = Math.min(1, q / 0.42), b = Math.max(0, (q - 0.42) / 0.58);
      const p = fl.via ? [fl.from[0] + (fl.via[0] - fl.from[0]) * a + (fl.to[0] - fl.via[0]) * b, fl.from[1] + (fl.via[1] - fl.from[1]) * a + (fl.to[1] - fl.via[1]) * b, fl.from[2] + (fl.via[2] - fl.from[2]) * a + (fl.to[2] - fl.via[2]) * b]
                       : [fl.from[0] + (fl.to[0] - fl.from[0]) * k, fl.from[1] + (fl.to[1] - fl.from[1]) * k, fl.from[2] + (fl.to[2] - fl.from[2]) * q];
      fl.m.visible = true; fl.m.position.set(p[0], p[1], p[2]); fl.m.rotation.x += 0.2;
    }
    // elevator: 0.2 m/s chain; each bucket tips onto the weigher cone at the end of the path
    const adv = simT * 200, pitch = pathLen / NB;
    buckets.forEach((b, i) => { const d = (adv + i * pitch) % pathLen, [x, z] = onPath(d); b.position.set(x, 0, z); b.children[1].visible = d < pathLen - 200;
      const lap = Math.floor((adv + i * pitch) / pathLen); if (b.userData.lap !== undefined && lap !== b.userData.lap) for (let j = 0; j < 3; j++) launch([-60, (Math.random() - 0.5) * 120, 3450], null, [(Math.random() - 0.5) * 160, (Math.random() - 0.5) * 160, WB + 960], simT + j * 0.07, 0.45);
      b.userData.lap = lap; });
    // released bags: drop to the belt, then ride up the take-off conveyor
    for (let i = free.length - 1; i >= 0; i--) {
      const fb = free[i], a = simT - fb.t0, fall = 0.22;
      if (a < fall) { const k = a / fall; fb.m.scale.set(BW / 2 * 0.78, 34, L / 2); fb.m.position.set(0, 0, JZ - L / 2 - (JZ - L / 2 - convZ(0) - 20) * k * k); }
      else { const x = (a - fall) * 420; if (x > 1500) { grp.remove(fb.m); free.splice(i, 1); continue; } fb.m.scale.set(L / 2, BW / 2 * 0.78, 30); fb.m.position.set(x, 0, convZ(x)); fb.m.rotation.y = -Math.atan2(450, 1800); }
    }
    const step = R[row(t)][1];
    ui.step.textContent = `${step} · ${STEP_NAME[step] || ""}`;
    ui.time.textContent = `${t.toFixed(2)} / ${P.toFixed(2)} s`;
    ui.bags.textContent = String(bags);
    ui.rate.textContent = `${(60 / P).toFixed(1)} bags/min`;
    ui.jaw.textContent = jaw > 0.99 ? "closed" : jaw < 0.01 ? "open" : "moving";
  }

  function start() { running = true; grp.visible = true; ghost(true); }
  function pause() { running = false; }
  function reset() {
    running = false; simT = 0; bags = 0; lastCycle = -1; update.nextDump = undefined; update.cutDone = undefined;
    flights.length = 0; chips.forEach((m) => (m.visible = false)); heads.forEach((h) => (h.visible = false));
    free.forEach((f) => grp.remove(f.m)); free.length = 0; buckets.forEach((b) => (b.userData.lap = undefined));
    grp.visible = false; ghost(false); pose(0);
    for (const id of ["B13a_front_jaw", "B13b_rear_jaw", "B12_vertical_seal"]) { const p = parts.get(id); if (p) p.node.position.copy(p.base); }
    ui.step.textContent = "—"; ui.time.textContent = "—"; ui.bags.textContent = "0"; ui.rate.textContent = "—"; ui.jaw.textContent = "—";
  }
  return { start, pause, reset, update, setSpeed: (v) => (speed = v), get running() { return running; }, get active() { return grp.visible; } };
}
