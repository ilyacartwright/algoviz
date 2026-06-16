import React from 'react'
import { useNavigate } from 'react-router-dom'

const MODULES = [
    {
        to: '/sort', color: 'var(--purple)', bg: 'var(--purple-bg)',
        label: 'Сортировки',
        desc: 'Пошаговая визуализация шести алгоритмов с подсчётом сравнений и обменов.',
        algos: ['Bubble', 'Selection', 'Insertion', 'Merge', 'Quick', 'Heap'],
    },
    {
        to: '/graph', color: 'var(--teal)', bg: 'var(--teal-bg)',
        label: 'Графы',
        desc: 'Обходы и поиск кратчайших путей на взвешенных графах.',
        algos: ['BFS', 'DFS', 'Dijkstra', 'Bellman-Ford'],
    },
    {
        to: '/tree', color: 'var(--coral)', bg: 'var(--coral-bg)',
        label: 'Деревья',
        desc: 'Интерактивные вставка, удаление и поиск в трёх структурах данных.',
        algos: ['BST', 'AVL', 'Max-Heap'],
    },
    {
        to: '/dp', color: 'var(--amber)', bg: 'var(--amber-bg)',
        label: 'Динамическое программирование',
        desc: 'Пошаговое заполнение DP-таблиц с подсветкой оптимального пути.',
        algos: ['LCS', 'Edit Distance', 'Knapsack', 'Fibonacci'],
    },
]

function HomePage() {
    const nav = useNavigate()
    return (
        <div style={{ flex: 1, overflow: 'auto', padding: '40px 32px' }}>
            <div style={{ maxWidth: '780px' }}>
                <div style={{ fontSize: '11px', color: 'var(--text3)', letterSpacing: '.1em', textTransform: 'uppercase', marginBottom: '8px' }}>
                    Интерактивный учебник
                </div>
                <h1 style={{ fontSize: '26px', fontWeight: 600, marginBottom: '10px' }}>
                    Визуализатор алгоритмов
                </h1>
                <p style={{ fontSize: '14px', color: 'var(--text2)', maxWidth: '500px', lineHeight: 1.7, marginBottom: '32px' }}>
                    Пошаговая анимация алгоритмов с пояснениями на каждом шаге.
                    Выберите модуль, задайте параметры и наблюдайте за выполнением.
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '14px' }}>
                    {MODULES.map(m => (
                        <div
                            key={m.to}
                            onClick={() => nav(m.to)}
                            style={{ background: 'var(--bg2)', border: '1px solid var(--border)', borderRadius: 'var(--r3)', padding: '20px', cursor: 'pointer', transition: 'all .2s' }}
                            onMouseEnter={e => { e.currentTarget.style.borderColor = m.color; e.currentTarget.style.background = m.bg }}
                            onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.background = 'var(--bg2)' }}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                                <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: m.color }} />
                                <span style={{ fontWeight: 500 }}>{m.label}</span>
                            </div>
                            <p style={{ fontSize: '13px', color: 'var(--text2)', lineHeight: 1.6, marginBottom: '12px' }}>{m.desc}</p>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                                {m.algos.map(a => (
                                    <span key={a} style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '12px', border: '1px solid var(--border2)', color: 'var(--text3)', fontFamily: 'var(--mono)' }}>
                                        {a}
                                    </span>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default HomePage