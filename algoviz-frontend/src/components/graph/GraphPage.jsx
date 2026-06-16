import React, { useState, useCallback, useRef, useEffect } from 'react'
import { runGraph, createSession } from '../../api/client'
import { useAlgoRun } from '../../hooks/useAlgoRun'
import {
    Btn, AlgoBtn, Slider, StepInfo, StepSlider, LogBox, Legend,
    ControlsBar, CtrlSep, Card, ComplexityCard, ErrorBox, Loader, SharePanel,
} from '../shared/UI'

const ALGOS = [
    { id: 'bfs', label: 'BFS', complexity: { time: 'O(V+E)', space: 'O(V)', stable: 'нет' } },
    { id: 'dfs', label: 'DFS', complexity: { time: 'O(V+E)', space: 'O(V)', stable: 'нет' } },
    { id: 'dijkstra', label: 'Dijkstra', complexity: { time: 'O((V+E) log V)', space: 'O(V)', stable: 'нет' } },
    { id: 'bellman', label: 'Bellman-Ford', complexity: { time: 'O(V·E)', space: 'O(V)', stable: 'нет' } },
]

const NODE_FILL = { start: '#e0705a', current: '#e8a838', queued: '#7c6fcd', visited: '#2ec4a6', default: '#20253a' }
const NODE_STROKE = { start: '#993C1D', current: '#854F0B', queued: '#534AB7', visited: '#0F6E56', default: '#363c57' }
const NODE_TEXT = { start: '#F5C4B3', current: '#FAC775', queued: '#C5BCF8', visited: '#9FE1CB', default: '#7a85a8' }

let _nodeIdCnt = 0

function GraphCanvas({ nodes, edges, step, editMode, edgeWeight, onAddNode, onAddEdge, onRemoveNode, onMoveNode }) {
    const svgRef = useRef()
    const [dragging, setDragging] = useState(null)
    const [edgeFrom, setEdgeFrom] = useState(null)
    const [hovered, setHovered] = useState(null)
    const [local, setLocal] = useState(nodes)

    useEffect(() => setLocal(nodes), [nodes])

    const nodeStates = step?.data?.node_states || {}
    const edgeStates = step?.data?.edge_states || {}

    const toSVG = (e) => {
        const r = svgRef.current.getBoundingClientRect()
        return {
            x: Math.round((e.clientX - r.left) * (560 / r.width)),
            y: Math.round((e.clientY - r.top) * (320 / r.height)),
        }
    }

    const onSVGClick = (e) => {
        if (!editMode || dragging) return
        if (e.target === svgRef.current || e.target.tagName === 'rect') {
            setEdgeFrom(null)
            onAddNode(toSVG(e))
        }
    }
    const onNodeClick = (e, id) => {
        e.stopPropagation()
        if (!editMode) return
        if (edgeFrom === null) { setEdgeFrom(id) }
        else if (edgeFrom !== id) { onAddEdge(edgeFrom, id); setEdgeFrom(null) }
        else { setEdgeFrom(null) }
    }
    const onNodeDbl = (e, id) => {
        e.stopPropagation()
        if (!editMode) return
        setEdgeFrom(null); onRemoveNode(id)
    }
    const onMouseDown = (e, id) => {
        if (!editMode) return
        e.stopPropagation(); setDragging(id)
    }
    const onMouseMove = (e) => {
        if (!dragging) return
        const pt = toSVG(e)
        setLocal(prev => prev.map(n => n.id === dragging ? { ...n, ...pt } : n))
    }
    const onMouseUp = () => {
        if (!dragging) return
        onMoveNode(local); setDragging(null)
    }

    if (!local?.length) return (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text3)', fontSize: '13px' }}>
            {editMode ? '🖱 Клик на холст — добавить вершину' : 'Нажмите «Загрузить»'}
        </div>
    )

    return (
        <svg ref={svgRef} width="100%" height="100%" viewBox="0 0 560 320"
            style={{ cursor: editMode ? (edgeFrom !== null ? 'crosshair' : 'default') : 'default', overflow: 'visible' }}
            onClick={onSVGClick} onMouseMove={onMouseMove} onMouseUp={onMouseUp}
        >
            <rect width={560} height={320} fill="transparent" />

            {edgeFrom !== null && (() => {
                const n = local.find(n => n.id === edgeFrom)
                return n ? <circle cx={n.x} cy={n.y} r={22} fill="none" stroke="var(--amber)" strokeWidth={2} strokeDasharray="4 3" opacity={.7} /> : null
            })()}

            {edges.map((e, i) => {
                const u = local.find(n => n.id === e.u)
                const v = local.find(n => n.id === e.v)
                if (!u || !v) return null
                const key = `${Math.min(e.u, e.v)}-${Math.max(e.u, e.v)}`
                const es = edgeStates[key]
                const stroke = es === 'active' ? '#e8a838' : es === 'visited' ? '#2ec4a6' : '#2f3652'
                return (
                    <g key={i}>
                        <line x1={u.x} y1={u.y} x2={v.x} y2={v.y} stroke={stroke} strokeWidth={es ? 2.5 : 1.5} style={{ transition: 'stroke .2s' }} />
                        <text x={(u.x + v.x) / 2} y={(u.y + v.y) / 2 - 5} textAnchor="middle" fontSize="10" fill="var(--text3)" fontFamily="var(--mono)">{e.w}</text>
                    </g>
                )
            })}

            {local.map(n => {
                const st = nodeStates[String(n.id)] || 'default'
                return (
                    <g key={n.id}
                        onClick={e => onNodeClick(e, n.id)}
                        onDoubleClick={e => onNodeDbl(e, n.id)}
                        onMouseDown={e => onMouseDown(e, n.id)}
                        onMouseEnter={() => setHovered(n.id)}
                        onMouseLeave={() => setHovered(null)}
                        style={{ cursor: editMode ? 'grab' : 'default' }}
                    >
                        <circle cx={n.x} cy={n.y} r={hovered === n.id && editMode ? 20 : 17}
                            fill={NODE_FILL[st]}
                            stroke={edgeFrom === n.id ? 'var(--amber)' : NODE_STROKE[st]}
                            strokeWidth={edgeFrom === n.id ? 2.5 : 2}
                            style={{ transition: 'all .2s' }}
                        />
                        <text x={n.x} y={n.y} textAnchor="middle" dominantBaseline="central"
                            fontSize="12" fontFamily="var(--mono)" fill={NODE_TEXT[st]} fontWeight="500"
                            style={{ pointerEvents: 'none' }}
                        >
                            {n.label}
                        </text>
                    </g>
                )
            })}

            {editMode && (
                <text x={4} y={314} fontSize="10" fill="var(--text3)" fontFamily="var(--mono)">
                    клик=добавить · клик узла=ребро · двойной клик=удалить · тащи=переместить
                </text>
            )}
        </svg>
    )
}

function GraphPage() {
    const [algo, setAlgo] = useState('bfs')
    const [count, setCount] = useState(8)
    const [editMode, setEditMode] = useState(false)
    const [manNodes, setManNodes] = useState([])
    const [manEdges, setManEdges] = useState([])
    const [edgeWeight, setEdgeWeight] = useState(1)
    const [logs, setLogs] = useState([])
    const [shareUrl, setShareUrl] = useState(null)

    const fetchFn = useCallback(() => {
        const body = { algorithm: algo }
        if (editMode && manNodes.length > 0) { body.nodes = manNodes; body.edges = manEdges }
        else body.node_count = count
        return runGraph(body)
    }, [algo, count, editMode, manNodes, manEdges])

    const { state, load, play, pause, step, stepBack, jumpTo, setSpeed, reset } = useAlgoRun(fetchFn)

    const nodes = state.response?.nodes || manNodes
    const edges = state.response?.edges || manEdges
    const complexity = ALGOS.find(a => a.id === algo)?.complexity

    useEffect(() => {
        if (!state.currentStep) return
        const s = state.currentStep
        setLogs(prev => [...prev.slice(-39), { text: `[${s.index + 1}] ${s.message}` }])
    }, [state.currentStep])

    const handleAddNode = (pt) => { const id = _nodeIdCnt++; const label = String.fromCharCode(65 + (manNodes.length % 26)); setManNodes(p => [...p, { id, label, x: pt.x, y: pt.y }]) }
    const handleAddEdge = (u, v) => { if (!manEdges.some(e => (e.u === u && e.v === v) || (e.u === v && e.v === u))) setManEdges(p => [...p, { u, v, w: edgeWeight }]) }
    const handleRemoveNode = (id) => { setManNodes(p => p.filter(n => n.id !== id)); setManEdges(p => p.filter(e => e.u !== id && e.v !== id)) }
    const handleMoveNode = (upd) => setManNodes(upd)
    const handleClear = () => { setManNodes([]); setManEdges([]); _nodeIdCnt = 0; reset(); setLogs([]) }

    const handleLoad = () => { setLogs([]); setShareUrl(null); load() }
    const handleReset = () => { reset(); setLogs([]); setShareUrl(null) }
    const handleShare = async () => {
        try { const res = await createSession({ module: 'graph', algorithm: algo, state: { nodes, edges, stepIndex: state.stepIndex } }); setShareUrl(res.url) } catch { }
    }

    const isPlaying = state.status === 'playing'
    const canPlay = state.status === 'paused' || state.status === 'playing'

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>

            <div style={{ background: 'var(--bg2)', borderBottom: '1px solid var(--border)', padding: '9px 16px', display: 'flex', gap: '6px', flexWrap: 'wrap', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: 'var(--text2)' }}>Алгоритм:</span>
                {ALGOS.map(a => <AlgoBtn key={a.id} active={algo === a.id} onClick={() => { setAlgo(a.id); handleReset() }}>{a.label}</AlgoBtn>)}
                <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '12px', color: 'var(--text2)' }}>Режим:</span>
                    <AlgoBtn active={!editMode} onClick={() => setEditMode(false)}>Случайный</AlgoBtn>
                    <AlgoBtn active={editMode} onClick={() => setEditMode(true)}>✏ Редактор</AlgoBtn>
                </div>
            </div>

            <ControlsBar>
                <Btn variant="primary" onClick={handleLoad} disabled={state.status === 'loading'}>⊕ Запустить</Btn>
                <CtrlSep />
                <Btn onClick={stepBack} disabled={!canPlay || state.stepIndex <= 0} title="Шаг назад">⏮</Btn>
                {!isPlaying ? <Btn onClick={play} disabled={!canPlay || state.status === 'done'}>▶</Btn> : <Btn onClick={pause}>⏸</Btn>}
                <Btn onClick={step} disabled={!canPlay} title="Шаг вперёд">⏭</Btn>
                <Btn onClick={handleReset}>↺</Btn>
                <CtrlSep />
                {!editMode
                    ? <Slider label="Вершин" value={count} min={4} max={12} onChange={v => { setCount(v); handleReset() }} />
                    : <><Slider label="Вес ребра" value={edgeWeight} min={1} max={9} onChange={setEdgeWeight} /><Btn size="sm" variant="danger" onClick={handleClear}>✕ Очистить</Btn></>
                }
                <Slider label="Скорость" value={state.speed} min={1} max={10} onChange={setSpeed} />
                <StepSlider value={state.stepIndex} max={state.total} onChange={jumpTo} />
                <StepInfo current={state.stepIndex} total={state.total} />
            </ControlsBar>

            <div style={{ flex: 1, overflow: 'auto', padding: '16px', display: 'flex', gap: '14px' }}>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '12px', minWidth: 0 }}>
                    {state.status === 'error' && <ErrorBox message={state.error} onRetry={handleLoad} />}
                    {state.status === 'loading' && <Loader text="Генерируем граф…" />}

                    <Card style={{ padding: '16px', minHeight: '300px' }}>
                        <GraphCanvas
                            nodes={nodes} edges={edges} step={state.currentStep}
                            editMode={editMode} edgeWeight={edgeWeight}
                            onAddNode={handleAddNode} onAddEdge={handleAddEdge}
                            onRemoveNode={handleRemoveNode} onMoveNode={handleMoveNode}
                        />
                    </Card>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                        <Legend items={[
                            { color: 'var(--coral)', label: 'старт' },
                            { color: 'var(--amber)', label: 'текущая' },
                            { color: 'var(--purple)', label: 'в очереди' },
                            { color: 'var(--teal)', label: 'посещённая' },
                        ]} />
                        {state.currentStep?.data?.distances && (
                            <div style={{ fontFamily: 'var(--mono)', fontSize: '11px', color: 'var(--text2)', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                                {Object.entries(state.currentStep.data.distances).map(([k, v]) => (
                                    <span key={k}>{nodes[k]?.label}: <span style={{ color: 'var(--purple2)' }}>{v}</span></span>
                                ))}
                            </div>
                        )}
                    </div>

                    <LogBox lines={logs} />
                    <SharePanel onShare={handleShare} sessionUrl={shareUrl} />
                </div>

                <div style={{ width: '160px', flexShrink: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <ComplexityCard complexity={complexity} />
                    {editMode && (
                        <div style={{ background: 'var(--bg3)', border: '1px solid var(--border)', borderRadius: 'var(--r2)', padding: '10px 12px', fontSize: '12px', color: 'var(--text2)', lineHeight: 2, fontFamily: 'var(--mono)' }}>
                            <div style={{ color: 'var(--text)', fontWeight: 500, marginBottom: '4px', fontFamily: 'var(--sans)' }}>Граф</div>
                            <div>вершин: <span style={{ color: 'var(--purple2)' }}>{manNodes.length}</span></div>
                            <div>рёбер:  <span style={{ color: 'var(--teal2)' }}>{manEdges.length}</span></div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
export default GraphPage