import React, { useCallback } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppShell } from "./components/layout/AppShell";
import { useAlgoRun } from "./hooks/useAlgoRun";
import { runSort } from "./api/client";
import './styles/globals.css'

// Временная страница для теста хука
function HookTest() {
    const fetchFn = useCallback(
        () => runSort({ algorithm: 'bubble', size: 10 }),
        []
    )
    const { state, load, play, pause, step, stepBack, reset } = useAlgoRun(fetchFn)

    return (
        <div style={{ padding: '32px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ color: 'var(--purple2)', fontWeight: 500, fontSize: '15px' }}>
                Тест useAlgoRun + API клиент
            </div>

            <div style={{ fontFamily: 'var(--mono)', fontSize: '13px', color: 'var(--text2)', display: 'flex', gap: '24px' }}>
                <span>status: <span style={{ color: 'var(--amber2)' }}>{state.status}</span></span>
                <span>шаг: <span style={{ color: 'var(--purple2)' }}>{state.stepIndex}</span> / {state.total}</span>
                <span>скорость: {state.speed}</span>
            </div>

            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {[
                    { label: '⊕ Загрузить', fn: load, disabled: state.status === 'loading' },
                    { label: '⏮ Назад', fn: stepBack, disabled: state.stepIndex <= 0 },
                    { label: '▶ Играть', fn: play, disabled: state.status !== 'paused' },
                    { label: '⏸ Пауза', fn: pause, disabled: state.status !== 'playing' },
                    { label: '⏭ Шаг', fn: step, disabled: !['paused', 'playing'].includes(state.status) },
                    { label: '↺ Сброс', fn: reset, disabled: false },
                ].map(({ label, fn, disabled }) => (
                    <button
                        key={label}
                        onClick={fn}
                        disabled={disabled}
                        style={{
                            padding: '6px 14px', borderRadius: 'var(--r)',
                            border: '1px solid var(--border2)',
                            background: disabled ? 'none' : 'var(--bg3)',
                            color: disabled ? 'var(--text3)' : 'var(--text)',
                            cursor: disabled ? 'not-allowed' : 'pointer',
                            fontFamily: 'inherit', fontSize: '13px',
                        }}
                    >
                        {label}
                    </button>
                ))}
            </div>

            {state.currentStep && (
                <div style={{
                    background: 'var(--bg3)', border: '1px solid var(--border)',
                    borderRadius: 'var(--r2)', padding: '12px 16px',
                    fontFamily: 'var(--mono)', fontSize: '12px', color: 'var(--text2)',
                }}>
                    <div style={{ color: 'var(--purple2)', marginBottom: '6px' }}>
                        [{state.currentStep.index + 1}] {state.currentStep.message}
                    </div>
                    <div>
                        массив: [{state.currentStep.data.array?.join(', ')}]
                    </div>
                    <div style={{ marginTop: '4px' }}>
                        тип: <span style={{ color: 'var(--amber2)' }}>{state.currentStep.data.type}</span>
                        {state.currentStep.data.comparing && (
                            <span style={{ marginLeft: '12px' }}>
                                comparing: [{state.currentStep.data.comparing.join(', ')}]
                            </span>
                        )}
                    </div>
                </div>
            )}

            {state.error && (
                <div style={{ color: 'var(--coral2)', fontFamily: 'var(--mono)', fontSize: '12px' }}>
                    ⚠ {state.error}
                    <br />
                    <small style={{ color: 'var(--text3)' }}>Убедись что бэкенд запущен: uvicorn app.main:app --reload</small>
                </div>
            )}

            {state.response && (
                <div style={{ color: 'var(--text3)', fontSize: '12px', fontFamily: 'var(--mono)' }}>
                    ✓ Загружено шагов: {state.response.total_steps} |
                    алгоритм: {state.response.algorithm} |
                    массив: [{state.response.array?.join(', ')}]
                </div>
            )}
        </div>
    )
}

function Placeholder({ title }) {
    return (
        <div style={{ padding: '40px', color: 'var(--text2)', fontSize: '14px' }}>
            <div style={{ color: 'var(--purple2)', fontWeight: 500, marginBottom: '8px' }}>{title}</div>
            Пока заглушка
        </div>
    )
}


function App() {
    return (
        <BrowserRouter>
            <AppShell>
                <Routes>
                    <Route path="/*" element={<HookTest />} />
                    {/* <Route path="/" element={<Placeholder title='Главная' />}></Route>
                    <Route path="/sort" element={<Placeholder title='Сортировки' />}></Route>
                    <Route path="/graph" element={<Placeholder title='Графы' />}></Route>
                    <Route path="/tree" element={<Placeholder title='Деревья' />}></Route>
                    <Route path="/dp" element={<Placeholder title='ДП' />}></Route> */}
                </Routes>
            </AppShell>
        </BrowserRouter>
    )
}

export default App