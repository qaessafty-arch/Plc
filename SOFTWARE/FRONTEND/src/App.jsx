import React, { useState } from 'react'
import { api, useLive, usePoll } from './api.js'

const STATES = ['STOPPED', 'STARTING', 'READY', 'RUNNING', 'STOPPING', 'FAULT', 'E-STOP']
const MODES = ['OFF', 'MANUAL', 'SETUP', 'AUTO', 'MAINTENANCE']
const stateClass = s => (s === 3 ? 'ok' : s >= 5 ? 'bad' : 'warn')
const fmt = ts => (ts ? new Date(ts).toLocaleString() : '-')

function Spark({ points, height = 60 }) {
  if (!points || points.length < 2) return <p className="muted">Not enough data yet.</p>
  const w = 600, min = Math.min(...points), max = Math.max(...points), span = max - min || 1
  const d = points.map((p, i) => `${i ? 'L' : 'M'}${((i / (points.length - 1)) * w).toFixed(1)},${(height - 4 - ((p - min) / span) * (height - 8)).toFixed(1)}`).join(' ')
  return (
    <svg viewBox={`0 0 ${w} ${height}`} preserveAspectRatio="none" className="spark" role="img" aria-label={`trend from ${min.toFixed(1)} to ${max.toFixed(1)}`}>
      <path d={d} fill="none" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  )
}

function Dashboard({ snap, connected }) {
  const { data: sum } = usePoll('/production/summary?hours=8', 10000)
  const { data: ts } = usePoll('/production/timeseries?hours=1', 15000)
  if (!snap) return <p className="muted">{connected ? 'Waiting for first data…' : 'No connection to the monitoring server.'}</p>
  if (snap.online === false) return <p className="banner bad">PLC offline - the monitoring server cannot read the controller.</p>
  return (
    <>
      <div className="grid">
        <div className={`card state ${stateClass(snap.state)}`}>
          <h3>Machine state</h3>
          <strong>{STATES[snap.state] ?? snap.state}</strong>
          <span>Mode {MODES[snap.mode] ?? snap.mode}</span>
        </div>
        <div className="card"><h3>Speed</h3><strong>{snap.speed_bpm.toFixed(1)}</strong><span>bags / min</span></div>
        <div className="card"><h3>Bags (total counter)</h3><strong>{snap.bags_total.toLocaleString()}</strong><span>{snap.recipe || 'no recipe name'}</span></div>
        <div className="card"><h3>Last 8 h</h3><strong>{sum?.bags?.toLocaleString() ?? '-'}</strong>
          <span>availability {sum?.availability_pct ?? '-'} % · {sum?.stops ?? '-'} stops</span></div>
      </div>
      <div className="grid">
        {snap.temps.map((t, i) => (
          <div className="card" key={i}>
            <h3>{['Front jaw', 'Rear jaw', 'Vertical bar'][i]} temperature</h3>
            <strong>{t.toFixed(1)} °C</strong><span>setpoint {snap.temp_setpoints[i]} °C</span>
          </div>
        ))}
      </div>
      <div className="card wide"><h3>Speed, last hour</h3><Spark points={ts?.map(p => p.speed_bpm)} /></div>
      {snap.active_alarms.length > 0 && <p className="banner bad">Active alarms: {snap.active_alarms.join(', ')} - see the Alarms tab.</p>}
    </>
  )
}

function Alarms() {
  const { data, error } = usePoll('/alarms?limit=200', 5000)
  const { data: pareto } = usePoll('/alarms/pareto?hours=24', 30000)
  if (error) return <p className="banner bad">{error}</p>
  return (
    <>
      <div className="card wide"><h3>Downtime by alarm, last 24 h</h3>
        {pareto?.length ? (
          <table><thead><tr><th>Id</th><th>Alarm</th><th>Class</th><th>Count</th><th>Minutes</th></tr></thead>
            <tbody>{pareto.map(p => <tr key={p.alarm_id}><td>{p.alarm_id}</td><td>{p.text}</td><td>{p.class}</td><td>{p.count}</td><td>{p.minutes}</td></tr>)}</tbody></table>
        ) : <p className="muted">No alarms in the last 24 hours.</p>}
      </div>
      <div className="card wide"><h3>Alarm history</h3>
        {data?.length ? (
          <table><thead><tr><th>Raised</th><th>Cleared</th><th>Id</th><th>Class</th><th>Text</th></tr></thead>
            <tbody>{data.map(a => (
              <tr key={a.id} className={a.cleared_at ? '' : 'active'}><td>{fmt(a.raised_at)}</td><td>{a.cleared_at ? fmt(a.cleared_at) : 'ACTIVE'}</td>
                <td>{a.alarm_id}</td><td>{a.alarm_class}</td><td>{a.text}</td></tr>))}</tbody></table>
        ) : <p className="muted">No alarm has been recorded.</p>}
      </div>
    </>
  )
}

function Batches({ token }) {
  const { data, error, reload } = usePoll('/batches', 10000)
  const [form, setForm] = useState({ batch_no: '', product: '', target_weight_g: 40, planned_bags: 0, film_lot: '', operator: '' })
  const [msg, setMsg] = useState(null)
  const [report, setReport] = useState(null)
  const [busy, setBusy] = useState(false)
  const act = async fn => { setBusy(true); setMsg(null); try { await fn(); reload() } catch (e) { setMsg(e.message) } finally { setBusy(false) } }
  const set = k => e => setForm({ ...form, [k]: e.target.type === 'number' ? Number(e.target.value) : e.target.value })
  return (
    <>
      <form className="card wide" onSubmit={e => { e.preventDefault(); act(() => api('/batches', { method: 'POST', body: form, token })) }}>
        <h3>Open a batch</h3>
        <div className="row">
          <label>Batch no.<input required value={form.batch_no} onChange={set('batch_no')} pattern="[A-Za-z0-9._\-/]+" /></label>
          <label>Product<input required value={form.product} onChange={set('product')} /></label>
          <label>Target g<input required type="number" min="1" step="0.1" value={form.target_weight_g} onChange={set('target_weight_g')} /></label>
          <label>Planned bags<input type="number" min="0" value={form.planned_bags} onChange={set('planned_bags')} /></label>
          <label>Film lot<input value={form.film_lot} onChange={set('film_lot')} /></label>
          <label>Operator<input value={form.operator} onChange={set('operator')} /></label>
          <button disabled={busy || !token} title={token ? '' : 'Enter the access token first'}>Open batch</button>
        </div>
        {!token && <p className="muted">Enter the access token (top right) to create or close batches.</p>}
        {msg && <p className="banner bad">{msg}</p>}
      </form>
      <div className="card wide"><h3>Batch records</h3>
        {error && <p className="banner bad">{error}</p>}
        {data?.length ? (
          <table><thead><tr><th>Batch</th><th>Product</th><th>Target g</th><th>Started</th><th>Closed</th><th>Bags</th><th /></tr></thead>
            <tbody>{data.map(b => (
              <tr key={b.id}><td>{b.batch_no}</td><td>{b.product}</td><td>{b.target_weight_g}</td><td>{fmt(b.started_at)}</td><td>{b.closed_at ? fmt(b.closed_at) : 'OPEN'}</td>
                <td>{b.bags_at_close != null ? b.bags_at_close - b.bags_at_start : '…'}</td>
                <td><button type="button" onClick={() => api(`/batches/${b.id}/report`).then(setReport).catch(e => setMsg(e.message))}>Report</button>{' '}
                  {!b.closed_at && <button type="button" disabled={busy || !token} onClick={() => act(() => api(`/batches/${b.id}/close`, { method: 'POST', token }))}>Close</button>}</td></tr>))}</tbody></table>
        ) : <p className="muted">No batch yet. Open one above to start a batch record.</p>}
      </div>
      {report && (
        <div className="card wide"><h3>Batch report {report.batch.batch_no}</h3>
          <p>{report.bags_produced.toLocaleString()} bags · nominal {report.nominal_output_kg} kg · {report.alarms.length} alarm events</p>
          <p className="muted">{report.note}</p>
          <button type="button" onClick={() => setReport(null)}>Hide</button>
        </div>)}
    </>
  )
}

function Maintenance({ token }) {
  const { data, error, reload } = usePoll('/maintenance/due', 30000)
  const [who, setWho] = useState('')
  const [msg, setMsg] = useState(null)
  const done = id => api('/maintenance/records', { method: 'POST', token, body: { task_id: id, done_by: who, kind: 'preventive' } }).then(reload).catch(e => setMsg(e.message))
  if (error) return <p className="banner bad">{error}</p>
  return (
    <div className="card wide"><h3>Preventive maintenance</h3>
      <label>Technician <input value={who} onChange={e => setWho(e.target.value)} placeholder="name" /></label>
      {msg && <p className="banner bad">{msg}</p>}
      <table><thead><tr><th>Task</th><th>Interval</th><th>Last done</th><th>Since</th><th>Status</th><th /></tr></thead>
        <tbody>{data?.map(t => (
          <tr key={t.task_id} className={t.due ? 'active' : ''}><td>{t.name}<br /><small className="muted">{t.instructions}</small></td>
            <td>{[t.interval_cycles && `${t.interval_cycles.toLocaleString()} bags`, t.interval_days && `${t.interval_days} d`].filter(Boolean).join(' / ')}</td>
            <td>{fmt(t.last_done)}</td><td>{t.cycles_since.toLocaleString()} bags{t.days_since != null ? ` · ${t.days_since} d` : ''}</td>
            <td>{t.due ? 'DUE' : 'ok'}</td>
            <td><button type="button" disabled={!token || !who} onClick={() => done(t.task_id)}>Record done</button></td></tr>))}</tbody></table>
    </div>
  )
}

export default function App() {
  const [tab, setTab] = useState('Dashboard')
  const [token, setToken] = useState(() => sessionStorage.getItem('spm_token') || '')
  const { snap, connected } = useLive()
  const saveToken = v => { setToken(v); sessionStorage.setItem('spm_token', v) }
  return (
    <div className="app">
      <header>
        <h1>SPM-420 <small>production monitor</small></h1>
        <nav>{['Dashboard', 'Alarms', 'Batches', 'Maintenance'].map(t => (
          <button key={t} className={t === tab ? 'on' : ''} onClick={() => setTab(t)}>{t}</button>))}</nav>
        <span className={`dot ${connected ? 'ok' : 'bad'}`} title={connected ? 'live' : 'disconnected'} />
        <input className="token" type="password" value={token} onChange={e => saveToken(e.target.value)} placeholder="access token" aria-label="access token" />
      </header>
      <p className="notice">Monitoring only. This application cannot start, stop or change the machine; use the machine HMI.</p>
      <main>
        {tab === 'Dashboard' && <Dashboard snap={snap} connected={connected} />}
        {tab === 'Alarms' && <Alarms />}
        {tab === 'Batches' && <Batches token={token} />}
        {tab === 'Maintenance' && <Maintenance token={token} />}
      </main>
    </div>
  )
}
