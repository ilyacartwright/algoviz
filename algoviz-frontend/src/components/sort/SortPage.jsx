import React, { useState, useCallback } from 'react'
import { runSort, createSession } from '../../api/client'
import { useAlgoRun } from '../../hooks/useAlgoRun'
import {
    Btn, AlgoBtn, Slider, StepInfo, StepSlider, LogBox, Legend,
    ControlsBar, CtrlSep, Card, ComplexityCard, ErrorBox, Loader, SharePanel,
} from '../shared/UI'

const ALGOS = [
    { id: 'bubble', label: 'Bubble', complexity: { time: 'O(n²)', space: 'O(1)', stable: 'да' } },
    { id: 'selection', label: 'Selection', complexity: { time: 'O(n²)', space: 'O(1)', stable: 'нет' } },
    { id: 'insertion', label: 'Insertion', complexity: { time: 'O(n²)', space: 'O(1)', stable: 'да' } },
    { id: 'merge', label: 'Merge', complexity: { time: 'O(n log n)', space: 'O(n)', stable: 'да' } },
    { id: 'quick', label: 'Quick', complexity: { time: 'O(n log n)', space: 'O(log n)', stable: 'нет' } },
    { id: 'heap', label: 'Heap', complexity: { time: 'O(n log n)', space: 'O(1)', stable: 'нет' } },
]

function barColor(i, d) {
    const sf = d.sorted_from ?? Infinity
    if (i >= sf) return 'var(--teal)'
    if (d.swapping?.includes(i)) return 'var(--coral)'
    if (d.comparing?.includes(i)) return 'var(--amber)'
    if (d.pivot === i) return 'var(--purple2)'
    if (d.highlight?.includes(i)) return 'var(--blue)'
    return 'var(--purple)'
}

function Bars({ arr, step }) {
    if (!arr?.length) return (
        <div style={{ color: 'var(--text3)', fontSize: '13px', padding: '20px' }}>
            Нажмите «Загрузить»
        </div>
    )
    const max = Math.max(...arr)
    const d = step?.data || {}
    return (
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: '2px', height: '200px', padding: '0 4px' }}>
            {arr.map((v, i) => (
                <div key={i} style={{
                    flex: 1, minWidth: '3px',
                    height: `${Math.max(4, Math.round((v / max) * 190))}px`,
                    background: barColor(i, d),
                    borderRadius: '2px 2px 0 0',
                    transition: 'height .15s ease, background .1s',
                }} />
            ))}
        </div>
    )
}

function SortPage() {
    const [algo, setAlgo] = useState('bubble')
    const [size, setSize] = useState(28)
    const [logs, setLogs] = useState([])
    const [stats, setStats] = useState({ comps: 0, swaps: 0 })
    const [shareUrl, setShareUrl] = useState(null)

    const fetchFn = useCallback(
        () => runSort({ algorithm: algo, size }),
        [algo, size]
    )
    const { state, load, play, pause, step, stepBack, jumpTo, setSpeed, reset } = useAlgoRun(fetchFn)

    const arr = state.currentStep?.data?.array || state.response?.array || []
    const complexity = ALGOS.find(a => a.id === algo)?.complexity

    React.useEffect(() => {
        if (!state.currentStep) return
        const s = state.currentStep
        setLogs(prev => [...prev.slice(-39), { text: `[${s.index + 1}] ${s.message}`, highlight: s.data?.type === 'done' }])
        setStats(prev => ({
            comps: prev.comps + (s.data?.type === 'compare' ? 1 : 0),
            swaps: prev.swaps + (s.data?.type === 'swap' ? 1 : 0),
        }))
    }, [state.currentStep])

    const handleLoad = () => { setLogs([]); setStats({ comps: 0, swaps: 0 }); setShareUrl(null); load() }
    const handleReset = () => { reset(); setLogs([]); setStats({ comps: 0, swaps: 0 }); setShareUrl(null) }
    const handleShare = async () => {
        try {
            const res = await createSession({ module: 'sort', algorithm: algo, state: { array: arr, stepIndex: state.stepIndex } })
            setShareUrl(res.url)
        } catch { }
    }

    const isPlaying = state.status === 'playing'
    const canPlay = state.status === 'paused' || state.status === 'playing'

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>

            {/* Алгоритм */}
            <div style={{ background: 'var(--bg2)', borderBottom: '1px solid var(--border)', padding: '9px 16px', display: 'flex', gap: '6px', flexWrap: 'wrap', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: 'var(--text2)' }}>Алгоритм:</span>
                {ALGOS.map(a => (
                    <AlgoBtn key={a.id} active={algo === a.id} onClick={() => { setAlgo(a.id); handleReset() }}>
                        {a.label}
                    </AlgoBtn>
                ))}
            </div>

            {/* Управление */}
            <ControlsBar>
                <Btn variant="primary" onClick={handleLoad} disabled={state.status === 'loading'}>⊕ Загрузить</Btn>
                <CtrlSep />
                <Btn onClick={stepBack} disabled={!canPlay || state.stepIndex <= 0} title="Шаг назад">⏮</Btn>
                {!isPlaying
                    ? <Btn onClick={play} disabled={!canPlay || state.status === 'done'}>▶</Btn>
                    : <Btn onClick={pause}>⏸</Btn>
                }
                <Btn onClick={step} disabled={!canPlay} title="Шаг вперёд">⏭</Btn>
                <Btn onClick={handleReset}>↺</Btn>
                <CtrlSep />
                <Slider label="Элементов" value={size} min={8} max={60} onChange={v => { setSize(v); handleReset() }} />
                <Slider label="Скорость" value={state.speed} min={1} max={10} onChange={setSpeed} />
                <StepSlider value={state.stepIndex} max={state.total} onChange={jumpTo} />
                <StepInfo current={state.stepIndex} total={state.total} />
            </ControlsBar>

            {/* Холст */}
            <div style={{ flex: 1, overflow: 'auto', padding: '16px', display: 'flex', gap: '14px' }}>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '12px', minWidth: 0 }}>
                    {state.status === 'error' && <ErrorBox message={state.error} onRetry={handleLoad} />}
                    {state.status === 'loading' && <Loader text="Генерируем шаги…" />}

                    <Card style={{ padding: '16px' }}>
                        <Bars arr={arr} step={state.currentStep} />
                    </Card>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                        <Legend items={[
                            { color: 'var(--purple)', label: 'обычный' },
                            { color: 'var(--amber)', label: 'сравнение' },
                            { color: 'var(--coral)', label: 'обмен' },
                            { color: 'var(--purple2)', label: 'пивот' },
                            { color: 'var(--teal)', label: 'отсортирован' },
                        ]} />
                        <span style={{ fontSize: '12px', fontFamily: 'var(--mono)', color: 'var(--text3)' }}>
                            сравнений: <span style={{ color: 'var(--amber2)' }}>{stats.comps}</span>
                            &nbsp;|&nbsp;
                            обменов: <span style={{ color: 'var(--coral2)' }}>{stats.swaps}</span>
                        </span>
                    </div>

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

export default SortPage