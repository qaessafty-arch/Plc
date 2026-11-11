import { useEffect, useRef, useState } from 'react'

export async function api(path, { method = 'GET', body, token } = {}) {
  const headers = {}
  if (body) headers['Content-Type'] = 'application/json'
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(`/api${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined })
  if (!res.ok) {
    let detail = res.statusText
    try { const j = await res.json(); detail = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail) } catch { /* not json */ }
    throw new Error(`${res.status}: ${detail}`)
  }
  return res.json()
}

/** Polls a GET endpoint; returns {data, error, reload}. */
export function usePoll(path, ms = 5000) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [tick, setTick] = useState(0)
  useEffect(() => {
    let alive = true
    const load = () => api(path).then(d => { if (alive) { setData(d); setError(null) } }).catch(e => alive && setError(e.message))
    load()
    const id = setInterval(load, ms)
    return () => { alive = false; clearInterval(id) }
  }, [path, ms, tick])
  return { data, error, reload: () => setTick(t => t + 1) }
}

/** Live snapshot over WebSocket with automatic reconnect. */
export function useLive() {
  const [snap, setSnap] = useState(null)
  const [connected, setConnected] = useState(false)
  const timer = useRef(null)
  useEffect(() => {
    let ws, closed = false
    const connect = () => {
      const proto = location.protocol === 'https:' ? 'wss' : 'ws'
      ws = new WebSocket(`${proto}://${location.host}/ws/live`)
      ws.onopen = () => setConnected(true)
      ws.onmessage = ev => { try { setSnap(JSON.parse(ev.data)) } catch { /* ignore malformed frame */ } }
      ws.onclose = () => { setConnected(false); if (!closed) timer.current = setTimeout(connect, 3000) }
    }
    connect()
    return () => { closed = true; clearTimeout(timer.current); ws && ws.close() }
  }, [])
  return { snap, connected }
}
