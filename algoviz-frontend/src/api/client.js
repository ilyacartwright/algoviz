const BASE = '/api'

async function post(path, body) {
    const r = await fetch(BASE + path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    })
    if (!r.ok) {
        const err = await r.json().catch(() => ({}))
        throw new Error(err.detail || `HTTP ${r.status}`)
    }
    return r.json()
}

async function get(path) {
    const r = await fetch(BASE + path)
    if (!r.ok) throw new Error(`HTTP ${r.status}`)
    return r.json()
}

export const fetchAlgorithms = () => get('/algorithms/')
export const runSort = (body) => post('/run/sort', body)
export const runGraph = (body) => post('/run/graph', body)
export const runTree = (body) => post('/run/tree', body)
export const runDP = (body) => post('/run/dp', body)
export const createSession = (body) => post('/share/', body)
export const getSession = (id) => get(`/share/${id}`)

export function createAlgoSocket(onInit, onStep, onDone, onError) {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${location.host}/ws/stream`)

    ws.onmessage = (e) => {
        const msg = JSON.parse(e.data)
        if (msg.type === 'init') onInit?.(msg)
        else if (msg.type === 'step') onStep?.(msg)
        else if (msg.type === 'done') onDone?.(msg)
        else if (msg.type === 'error') onError?.(new Error(msg.message))
    }

    ws.onerror = () => onError?.(new Error('WebSocket connection failed'))

    return {
        send: (payload) => ws.readyState === 1 && ws.send(JSON.stringify(payload)),
        close: () => ws.close(),
        get ready() { return ws.readyState === 1 },
    }
}