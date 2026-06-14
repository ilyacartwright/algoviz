// import React from "react";
import { NavLink, useLocation } from "react-router-dom";

const NAV = [
    {
        to: '/sort',
        label: 'Сортировки',
        dot: 'var(--purple)',
        desc: 'Bubble, Quick, Merge…'
    },
    {
        to: '/graph',
        label: 'Графы',
        dot: 'var(--teal)',
        desc: 'BFS, DFS, Dijkstra…'
    },
    {
        to: '/tree',
        label: 'Деревья',
        dot: 'var(--coral)',
        desc: 'BST, AVL, Max-Heap'
    },
    {
        to: '/dp',
        label: 'ДП',
        dot: 'var(--amber)',
        desc: 'LCS, Knapsack, Fib…'
    },
]

function SideNav() {
    return (
        <nav style={{
            width: '216px', background: 'var(--bg2)',
            borderRight: '1px solid var(--border)',
            display: 'flex', flexDirection: 'column',
            padding: '16px 10px', gap: '4px', flexShrink: 0,
        }}>
            <div style={{ fontSize: '10px', fontWeight: 500, letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--text3)', padding: '0 8px', marginBottom: '8px' }}>
                Модули
            </div>

            {NAV.map(({ to, label, dot, desc }) => (
                <NavLink key={to} to={to} style={{ textDecoration: 'none' }}>
                    {({ isActive }) => (
                        <div
                            style={{ display: 'flex', alignItems: 'center', gap: '9px', padding: '8px 10px', borderRadius: 'var(--r)', background: isActive ? 'var(--purple-bg)' : 'none', transition: 'background .15s', cursor: 'pointer' }}
                            onMouseEnter={e => !isActive && (e.currentTarget.style.background = 'var(--bg4)')}
                            onMouseLeave={e => !isActive && (e.currentTarget.style.background = 'none')}
                        >
                            <div style={{ width: '7px', height: '7px', borderRadius: '50%', background: dot, flexShrink: 0 }} />
                            <div>
                                <div style={{ fontSize: '13px', color: isActive ? 'var(--purple2)' : 'var(--text)', fontWeight: isActive ? 500 : 400 }}>
                                    {label}
                                </div>
                                <div style={{ fontSize: '11px', color: 'var(--text3)' }}>{desc}</div>
                            </div>
                        </div>
                    )}
                </NavLink>
            ))}

            <div style={{ marginTop: 'auto', padding: '8px 10px', borderTop: '1px solid var(--border)', paddingTop: '16px' }}>
                <div style={{ fontSize: '10px', color: 'var(--text3)', lineHeight: 1.8 }}>
                    <div>FastAPI + WebSocket</div>
                    <div>React 18 + Vite</div>
                    <div style={{ color: 'var(--teal)', display: 'flex', alignItems: 'center', gap: '5px', marginTop: '4px' }}>
                        <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--teal)', animation: 'pulse 2s infinite' }} />
                        API подключён
                    </div>
                </div>
            </div>
        </nav>
    )
}

function Topbar() {
    const loc = useLocation()
    const current = NAV.find(n => loc.pathname.startsWith(n.to))
    return (
        <header style={{ height: '52px', background: 'var(--bg2)', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', padding: '0 20px', gap: '14px', flexShrink: 0 }}>
            <NavLink to="/"><span style={{ fontSize: '15px', fontWeight: 600, color: 'var(--purple2)', letterSpacing: '.02em' }}>Algo<span style={{ color: 'var(--text2)', fontWeight: 400 }}>Viz</span></span></NavLink>
            {current && <><span style={{ color: 'var(--text3)' }}>/</span><span style={{ fontSize: '13px', color: 'var(--text)' }}>{current.label}</span></>}
            <div style={{ marginLeft: 'auto', fontSize: '12px', color: 'var(--text3)' }}>Визуализатор алгоритмов</div>
        </header>
    )
}

export function AppShell({ children }) {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
            <Topbar />
            <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
                <SideNav />
                <main style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                    {children}
                </main>
            </div>
        </div>
    )
}