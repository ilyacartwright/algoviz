import React, { useState, useCallback } from 'react'
import { runTree } from '../../api/client'
import {
    Btn, AlgoBtn, StepInfo, LogBox, Legend,
    ControlsBar, CtrlSep, Card, ComplexityCard, ErrorBox, Loader,
} from '../shared/UI'

const ALGOS = [
    { id: 'bst', label: 'BST', complexity: { time: 'O(log n) avg', space: 'O(n)', stable: 'да' } },
    { id: 'avl', label: 'AVL', complexity: { time: 'O(log n)', space: 'O(n)', stable: 'да' } },
    { id: 'max_heap', label: 'Max-Heap', complexity: { time: 'O(log n)', space: 'O(n)', stable: 'нет' } },
]

const AUTO = [50, 30, 70, 20, 40, 60, 80, 10, 25]

function TreeSVG({ nodes, edges, highlight }) {
    if (!nodes?.length) return (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text3)', fontSize: '13px' }}>
            Вставьте значения или нажмите «Авто»
        </div>
    )
    const H = Math.max(...nodes.map(n => n.y), 200) + 40
    return (
        <svg width="100%" height={H} viewBox={`0 0 560 ${H}`} style={{ overflow: 'visible' }}>
            {edges.map((e, i) => (
                <line key={i} x1={e.fx} y1={e.fy} x2={e.tx} y2={e.ty} stroke="var(--border2)" strokeWidth={1.5} />
            ))}
            {nodes.map((n, i) => {
                const isHL = n.val === highlight
                const isLeaf = n.left === null && n.right === null
                const isRoot = i === 0
                const fill = isHL ? 'var(--amber-bg)' : isRoot ? 'var(--coral-bg)' : isLeaf ? 'var(--teal-bg)' : 'var(--purple-bg)'
                const stroke = isHL ? 'var(--amber)' : isRoot ? 'var(--coral)' : isLeaf ? 'var(--teal)' : 'var(--purple)'
                const tc = isHL ? 'var(--amber2)' : isRoot ? 'var(--coral2)' : isLeaf ? 'var(--teal2)' : 'var(--purple2)'
                return (
                    <g key={i}>
                        <circle cx={n.x} cy={n.y} r={17} fill={fill} stroke={stroke} strokeWidth={2} style={{ transition: 'all .3s' }} />
                        <text x={n.x} y={n.y} textAnchor="middle" dominantBaseline="central" fontSize="11" fontFamily="var(--mono)" fill={tc} fontWeight="500">
                            {n.val}
                        </text>
                    </g>
                )
            })}
        </svg>
    )
}

function TreePage() {
    const [algo, setAlgo] = useState('bst')
    const [values, setValues] = useState([])
    const [input, setInput] = useState('')
    const [tree, setTree] = useState(null)
    const [highlight, setHighlight] = useState(null)
    const [logs, setLogs] = useState([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const complexity = ALGOS.find(a => a.id === algo)?.complexity

    const addLog = (text, hl = false) =>
        setLogs(prev => [...prev.slice(-39), { text, highlight: hl }])

    const rebuild = useCallback(async (vals, hl = null) => {
        if (!vals.length) { setTree(null); setHighlight(null); return }
        setLoading(true); setError(null)
        try {
            const res = await runTree({ tree_type: algo, values: vals })
            const last = res.steps[res.steps.length - 1]
            setTree({ nodes: last.data.nodes, edges: last.data.edges, node_count: last.data.node_count, depth: last.data.depth })
            setHighlight(hl)
        } catch (e) { setError(e.message) }
        finally { setLoading(false) }
    }, [algo])

    const handleInsert = async () => {
        const v = parseInt(input)
        if (isNaN(v) || v < 1 || v > 9999) { addLog('⚠ Введите число 1–9999'); return }
        const next = [...values, v]
        setValues(next); setInput('')
        addLog(`Вставляем: ${v}`, true)
        await rebuild(next, v)
    }

    const handleDelete = async () => {
        const v = parseInt(input)
        if (isNaN(v)) { addLog('⚠ Введите значение'); return }
        if (!values.includes(v)) { addLog(`${v} не найден`); return }
        const next = values.filter(x => x !== v)
        setValues(next); setInput('')
        addLog(`Удаляем: ${v}`, true)
        await rebuild(next)
    }

    const handleSearch = () => {
        const v = parseInt(input)
        if (isNaN(v)) return
        const found = values.includes(v)
        addLog(found ? `✓ Найдено: ${v}` : `✗ ${v} не найден`, found)
        if (found) setHighlight(v)
    }

    const handleAuto = async () => {
        setValues(AUTO); setLogs([])
        addLog(`Авто: ${AUTO.join(', ')}`, true)
        await rebuild(AUTO)
    }

    const handleClear = () => {
        setValues([]); setTree(null); setHighlight(null); setLogs([])
        addLog('Дерево очищено')
    }

    const handleAlgo = (id) => {
        setAlgo(id); setValues([]); setTree(null); setHighlight(null); setLogs([])
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>

            <div style={{ background: 'var(--bg2)', borderBottom: '1px solid var(--border)', padding: '9px 16px', display: 'flex', gap: '6px', flexWrap: 'wrap', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: 'var(--text2)' }}>Структура:</span>
                {ALGOS.map(a => <AlgoBtn key={a.id} active={algo === a.id} onClick={() => handleAlgo(a.id)}>{a.label}</AlgoBtn>)}
            </div>

            <ControlsBar>
                <input
                    value={input} onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleInsert()}
                    placeholder="значение" type="number" min={1} max={9999}
                    style={{ width: '90px', padding: '5px 10px', borderRadius: 'var(--r)', border: '1px solid var(--border2)', background: 'var(--bg3)', color: 'var(--text)', fontSize: '13px', fontFamily: 'inherit' }}
                />
                <Btn variant="primary" onClick={handleInsert}>+ Вставить</Btn>
                <Btn onClick={handleDelete}>− Удалить</Btn>
                <Btn onClick={handleSearch}>⌕ Найти</Btn>
                <CtrlSep />
                <Btn onClick={handleAuto}>⊕ Авто</Btn>
                <Btn onClick={handleClear}>↺ Очистить</Btn>
                <StepInfo current={tree?.node_count ?? 0} total="∞" label="узлов:" />
            </ControlsBar>

            <div style={{ flex: 1, overflow: 'auto', padding: '16px', display: 'flex', gap: '14px' }}>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '12px', minWidth: 0 }}>
                    {error && <ErrorBox message={error} />}
                    {loading && <Loader text="Перестраиваем дерево…" />}

                    <Card style={{ padding: '16px', minHeight: '300px', overflowX: 'auto' }}>
                        <TreeSVG nodes={tree?.nodes} edges={tree?.edges} highlight={highlight} />
                    </Card>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                        <Legend items={[
                            { color: 'var(--coral)', label: 'корень' },
                            { color: 'var(--purple)', label: 'внутренний' },
                            { color: 'var(--teal)', label: 'лист' },
                            { color: 'var(--amber)', label: 'активный' },
                        ]} />
                        {tree && (
                            <span style={{ fontSize: '11px', fontFamily: 'var(--mono)', color: 'var(--text3)' }}>
                                узлов: <span style={{ color: 'var(--purple2)' }}>{tree.node_count}</span>
                                &nbsp;|&nbsp;
                                глубина: <span style={{ color: 'var(--teal2)' }}>{tree.depth}</span>
                            </span>
                        )}
                    </div>

                    <LogBox lines={logs} />
                </div>

                <div style={{ width: '160px', flexShrink: 0 }}>
                    <ComplexityCard complexity={complexity} />
                </div>
            </div>
        </div>
    )
}

export default TreePage