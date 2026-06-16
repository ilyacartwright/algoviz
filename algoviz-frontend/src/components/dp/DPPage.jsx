import React, { useState, useCallback } from 'react'
import { runDP, createSession } from '../../api/client'
import { useAlgoRun } from '../../hooks/useAlgoRun'
import {
    Btn, AlgoBtn, Slider, StepInfo, StepSlider, LogBox, Legend,
    ControlsBar, CtrlSep, Card, ComplexityCard, ErrorBox, Loader, SharePanel,
} from '../shared/UI'

const ALGOS = [
    { id: 'lcs', label: 'LCS', complexity: { time: 'O(m·n)', space: 'O(m·n)', stable: 'да' } },
    { id: 'edit', label: 'Edit Distance', complexity: { time: 'O(m·n)', space: 'O(m·n)', stable: 'да' } },
    { id: 'knapsack', label: 'Knapsack', complexity: { time: 'O(n·W)', space: 'O(n·W)', stable: 'да' } },
    { id: 'fib', label: 'Fibonacci', complexity: { time: 'O(n)', space: 'O(n)', stable: 'да' } },
]

const inp = { padding: '4px 8px', borderRadius: 'var(--r)', border: '1px solid var(--border2)', background: 'var(--bg3)', color: 'var(--text)', fontFamily: 'var(--mono)', fontSize: '13px' }

function LCSForm({ p, set }) {
    return <>
        <span style={{ fontSize: '12px', color: 'var(--text2)' }}>S1:</span>
        <input style={{ ...inp, width: '110px' }} value={p.string1 || ''} maxLength={12} placeholder="ABCBDAB" onChange={e => set(x => ({ ...x, string1: e.target.value }))} />
        <span style={{ fontSize: '12px', color: 'var(--text2)' }}>S2:</span>
        <input style={{ ...inp, width: '110px' }} value={p.string2 || ''} maxLength={12} placeholder="BDCAB" onChange={e => set(x => ({ ...x, string2: e.target.value }))} />
    </>
}

function EditForm({ p, set }) {
    return <>
        <span style={{ fontSize: '12px', color: 'var(--text2)' }}>Из:</span>
        <input style={{ ...inp, width: '100px' }} value={p.string1 || ''} maxLength={10} placeholder="HORSE" onChange={e => set(x => ({ ...x, string1: e.target.value }))} />
        <span style={{ fontSize: '12px', color: 'var(--text2)' }}>В:</span>
        <input style={{ ...inp, width: '100px' }} value={p.string2 || ''} maxLength={10} placeholder="ROS" onChange={e => set(x => ({ ...x, string2: e.target.value }))} />
    </>
}

function KnapsackForm({ p, set }) {
    const [rw, setRw] = useState((p.weights || [2, 3, 4, 5, 1]).join(','))
    const [rv, setRv] = useState((p.values || [3, 4, 5, 6, 2]).join(','))
    const apply = () => {
        const w = rw.split(',').map(Number).filter(x => x > 0)
        const v = rv.split(',').map(Number).filter(x => x > 0)
        if (w.length && w.length === v.length) set(x => ({ ...x, weights: w, values: v }))
    }
    return <>
        <span style={{ fontSize: '12px', color: 'var(--text2)' }}>Веса:</span>
        <input style={{ ...inp, width: '120px' }} value={rw} onChange={e => setRw(e.target.value)} onBlur={apply} placeholder="2,3,4,5,1" />
        <span style={{ fontSize: '12px', color: 'var(--text2)' }}>Ценности:</span>
        <input style={{ ...inp, width: '120px' }} value={rv} onChange={e => setRv(e.target.value)} onBlur={apply} placeholder="3,4,5,6,2" />
        <span style={{ fontSize: '12px', color: 'var(--text2)' }}>W:</span>
        <input type="number" style={{ ...inp, width: '60px' }} value={p.capacity || 10} min={1} max={30} onChange={e => set(x => ({ ...x, capacity: Number(e.target.value) }))} />
    </>
}

function FibForm({ p, set }) {
    return <>
        <span style={{ fontSize: '12px', color: 'var(--text2)' }}>n =</span>
        <input type="number" style={{ ...inp, width: '70px' }} value={p.n || 12} min={2} max={20} onChange={e => set(x => ({ ...x, n: Number(e.target.value) }))} />
        <span style={{ fontSize: '11px', color: 'var(--text3)' }}>чисел Фибоначчи</span>
    </>
}

const FORMS = { lcs: LCSForm, edit: EditForm, knapsack: KnapsackForm, fib: FibForm }

function DPTable({ step }) {
    if (!step?.data?.dp) return (
        <div style={{ color: 'var(--text3)', fontSize: '13px', padding: '20px' }}>Нажмите «Загрузить»</div>
    )
    const { dp, current, path, row_hdr, col_hdr } = step.data
    const ps = new Set(path || [])
    return (
        <div style={{ overflowX: 'auto' }}>
            <table style={{ borderCollapse: 'collapse', fontFamily: 'var(--mono)', fontSize: '13px' }}>
                <thead>
                    <tr>
                        <th style={{ width: '36px', height: '34px', background: 'var(--bg3)', border: '1px solid var(--border)' }} />
                        {(row_hdr || []).map((h, j) => <th key={j} style={{ width: '36px', height: '34px', background: 'var(--bg3)', color: 'var(--text2)', fontSize: '11px', fontWeight: 400, border: '1px solid var(--border)', padding: '0 4px' }}>{h}</th>)}
                    </tr>
                </thead>
                <tbody>
                    {dp.map((row, i) => (
                        <tr key={i}>
                            <td style={{ width: '36px', height: '34px', background: 'var(--bg3)', color: 'var(--text2)', fontSize: '11px', border: '1px solid var(--border)', textAlign: 'center' }}>
                                {(col_hdr || [])[i] ?? i}
                            </td>
                            {row.map((val, j) => {
                                const isCur = current && current[0] === i && current[1] === j
                                const isPath = ps.has(`${i},${j}`)
                                const isFill = val > 0 || (current && (current[0] > i || (current[0] === i && current[1] > j)))
                                let bg = 'var(--bg3)', color = 'var(--text3)', border = '1px solid var(--border)'
                                if (isCur) { bg = 'var(--amber-bg)'; color = 'var(--amber2)'; border = '1px solid var(--amber)' }
                                else if (isPath) { bg = 'var(--teal-bg)'; color = 'var(--teal2)'; border = '1px solid var(--teal)' }
                                else if (isFill) { bg = 'var(--purple-bg)'; color = 'var(--purple2)'; border = '1px solid var(--border2)' }
                                return <td key={j} style={{ width: '36px', height: '34px', textAlign: 'center', background: bg, color, border, transition: 'all .15s' }}>{val}</td>
                            })}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}

function DPPage() {
    const [algo, setAlgo] = useState('lcs')
    const [params, setParams] = useState({})
    const [logs, setLogs] = useState([])
    const [shareUrl, setShareUrl] = useState(null)

    const fetchFn = useCallback(() => runDP({ algorithm: algo, ...params }), [algo, params])
    const { state, load, play, pause, step, stepBack, jumpTo, setSpeed, reset } = useAlgoRun(fetchFn)

    const complexity = ALGOS.find(a => a.id === algo)?.complexity
    const meta = state.response?.meta
    const Form = FORMS[algo]

    React.useEffect(() => {
        if (!state.currentStep) return
        const s = state.currentStep
        setLogs(prev => [...prev.slice(-39), { text: `[${s.index + 1}] ${s.message}`, highlight: s.index === state.total - 1 }])
    }, [state.currentStep, state.total])

    const handleLoad = () => { setLogs([]); setShareUrl(null); load() }
    const handleReset = () => { reset(); setLogs([]); setShareUrl(null) }
    const handleShare = async () => {
        try { const res = await createSession({ module: 'dp', algorithm: algo, state: { params, stepIndex: state.stepIndex, result: state.response?.result } }); setShareUrl(res.url) } catch { }
    }

    const isPlaying = state.status === 'playing'
    const canPlay = state.status === 'paused' || state.status === 'playing'

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>

            <div style={{ background: 'var(--bg2)', borderBottom: '1px solid var(--border)', padding: '9px 16px', display: 'flex', gap: '6px', flexWrap: 'wrap', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: 'var(--text2)' }}>Задача:</span>
                {ALGOS.map(a => <AlgoBtn key={a.id} active={algo === a.id} onClick={() => { setAlgo(a.id); setParams({}); handleReset() }}>{a.label}</AlgoBtn>)}
            </div>

            <div style={{ background: 'var(--bg2)', borderBottom: '1px solid var(--border)', padding: '8px 16px', display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
                <Form p={params} set={setParams} />
            </div>

            <ControlsBar>
                <Btn variant="primary" onClick={handleLoad} disabled={state.status === 'loading'}>⊕ Загрузить</Btn>
                <CtrlSep />
                <Btn onClick={stepBack} disabled={!canPlay || state.stepIndex <= 0} title="Шаг назад">⏮</Btn>
                {!isPlaying ? <Btn onClick={play} disabled={!canPlay || state.status === 'done'}>▶</Btn> : <Btn onClick={pause}>⏸</Btn>}
                <Btn onClick={step} disabled={!canPlay} title="Шаг вперёд">⏭</Btn>
                <Btn onClick={handleReset}>↺</Btn>
                <CtrlSep />
                <Slider label="Скорость" value={state.speed} min={1} max={10} onChange={setSpeed} />
                <StepSlider value={state.stepIndex} max={state.total} onChange={jumpTo} />
                <StepInfo current={state.stepIndex} total={state.total} />
                {state.response?.result !== undefined && (
                    <span style={{ fontSize: '12px', fontFamily: 'var(--mono)', color: 'var(--teal2)', marginLeft: '6px' }}>
                        Результат: <strong>{state.response.result}</strong>
                    </span>
                )}
            </ControlsBar>

            <div style={{ flex: 1, overflow: 'auto', padding: '16px', display: 'flex', gap: '14px' }}>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '12px', minWidth: 0 }}>
                    {state.status === 'error' && <ErrorBox message={state.error} onRetry={handleLoad} />}
                    {state.status === 'loading' && <Loader text="Генерируем шаги…" />}

                    <Card style={{ padding: '16px' }}>
                        {meta && (
                            <div style={{ display: 'flex', gap: '20px', fontFamily: 'var(--mono)', fontSize: '12px', color: 'var(--text2)', marginBottom: '10px', flexWrap: 'wrap' }}>
                                {meta.string1 && <span>S1: <span style={{ color: 'var(--text)' }}>{meta.string1}</span></span>}
                                {meta.string2 && <span>S2: <span style={{ color: 'var(--text)' }}>{meta.string2}</span></span>}
                                {meta.items && <span>n={meta.items}, W={meta.capacity}</span>}
                                {meta.n && <span>n={meta.n}</span>}
                            </div>
                        )}
                        <DPTable step={state.currentStep} />
                    </Card>

                    <Legend items={[
                        { color: 'var(--bg3)', label: 'пусто' },
                        { color: 'var(--purple-bg)', label: 'заполнено' },
                        { color: 'var(--amber-bg)', label: 'текущая ячейка' },
                        { color: 'var(--teal-bg)', label: 'оптимальный путь' },
                    ]} />

                    <LogBox lines={logs} />
                    <SharePanel onShare={handleShare} sessionUrl={shareUrl} />
                </div>

                <div style={{ width: '160px', flexShrink: 0 }}>
                    <ComplexityCard complexity={complexity} />
                </div>
            </div>
        </div>
    )
}

export default DPPage