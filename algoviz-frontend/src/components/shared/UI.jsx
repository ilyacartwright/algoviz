import React from "react";

const BTN_STYLES = {
    primary: {
        background: 'var(--purple)',
        borderColor: 'var(--purple)',
        color: '#fff'
    },
    ghost: {
        background: 'none',
        borderColor: 'var(--border2)',
        color: 'var(--text)'
    },
    danger: {
        background: 'none',
        borderColor: 'var(--coral)',
        color: 'var(--coral)'
    },
}

export function Btn({ variant = 'ghost', size = 'md', children, ...props }) {
    return (
        <button style={{
            display: 'inline-flex', alignItems: 'center', gap: '6px',
            fontFamily: 'inherit', fontWeight: 500,
            borderRadius: 'var(--r)', border: '1px solid transparent',
            cursor: 'pointer', transition: 'all .15s', whiteSpace: 'nowrap',
            padding: size === 'sm' ? '4px 10px' : '6px 14px',
            fontSize: size === 'sm' ? '12px' : '13px',
            ...BTN_STYLES[variant],
        }} {...props}>{children}</button>
    )
}

export function AlgoBtn({ active, children, ...props }) {
    return (
        <button style={{
            fontSize: '12px', padding: '4px 12px', borderRadius: '20px',
            border: `1px solid ${active ? 'var(--purple)' : 'var(--border2)'}`,
            ackground: active ? 'var(--purple-bg)' : 'none',
            color: active ? 'var(--purple2)' : 'var(--text2)',
            cursor: 'pointer', transition: 'all .15s', fontFamily: 'inherit',
        }} {...props}>{children}</button>
    )
}

export function Slider({ label, value, min = 1, max = 10, step = 1, onChange }) {
    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text2)', whiteSpace: 'nowrap' }}>{label}</span>
            <input
                type="range" min={min} max={max} step={step} value={value}
                onChange={e => onChange(Number(e.target.value))}
                style={{ accentColor: 'var(--purple)', height: '4px', cursor: 'pointer', width: '90px' }}
            />
        </div>
    )
}

export function StepSlider({ value, max, onChange }) {
    if (!max) return null
    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1, minWidth: '100px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text3)', whiteSpace: 'nowrap' }}>таймлайн</span>
            <input
                type="range" min={0} max={max} value={value}
                onChange={e => onChange(Number(e.target.value))}
                style={{ flex: 1, accentColor: 'var(--teal)', height: '3px', cursor: 'pointer' }}
            />
        </div>
    )
}

export function StepInfo({ current, total, label }) {
    return (
        <span style={{ fontSize: '12px', fontFamily: 'var(--mono)', color: 'var(--text2)', marginLeft: 'auto' }}>
            {label && <span style={{ marginRight: '6px', color: 'var(--text3)' }}>{label}</span>}
            <span style={{ color: 'var(--purple2)' }}>{current}</span>
            <span style={{ color: 'var(--text3)' }}> / {total}</span>
        </span>
    )
}

export function LogBox({ lines }) {
    const ref = React.useRef()
    React.useEffect(() => {
        if (ref.current) ref.current.scrollTop = ref.current.scrollHeight
    }, [lines])
    return (
        <div ref={ref} style={{
            background: 'var(--bg2)', border: '1px solid var(--border)',
            borderRadius: 'var(--r2)', padding: '10px 14px',
            maxHeight: '100px', overflowY: 'auto',
            fontFamily: 'var(--mono)', fontSize: '12px', lineHeight: 1.9,
        }}>
            {lines.length === 0
                ? <span style={{ color: 'var(--text3)' }}>Журнал шагов появится здесь…</span>
                : lines.map((l, i) => (
                    <div key={i} style={{ color: l.highlight ? 'var(--purple2)' : 'var(--text2)' }}>
                        {l.text}
                    </div>
                ))
            }
        </div>
    )
}

export function Legend({ items }) {
    return (
        <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap' }}>
            {items.map(({ color, label }) => (
                <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '11px', color: 'var(--text2)' }}>
                    <div style={{ width: '9px', height: '9px', borderRadius: '2px', background: color, flexShrink: 0 }} />
                    {label}
                </div>
            ))}
        </div>
    )
}

export function ComplexityCard({ complexity }) {
    if (!complexity) return null
    return (
        <div style={{
            background: 'var(--bg3)', border: '1px solid var(--border)',
            borderRadius: 'var(--r2)', padding: '10px 14px',
            fontFamily: 'var(--mono)', fontSize: '12px', lineHeight: 2.2,
        }}>
            <div style={{ color: 'var(--text3)', fontSize: '10px', letterSpacing: '.08em', textTransform: 'uppercase', marginBottom: '4px' }}>
                Сложность
            </div>
            <div>Время: <span style={{ color: 'var(--purple2)' }}>{complexity.time}</span></div>
            <div>Память: <span style={{ color: 'var(--teal2)' }}>{complexity.space}</span></div>
            <div>Стабильный: <span style={{ color: 'var(--amber2)' }}>{complexity.stable}</span></div>
        </div>
    )
}

export function Loader({ text = 'Загрузка…' }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text2)', fontSize: '13px', padding: '20px' }}>
      <div style={{
        width: '16px', height: '16px',
        border: '2px solid var(--border2)', borderTopColor: 'var(--purple)',
        borderRadius: '50%', animation: 'spin .7s linear infinite',
      }}/>
      {text}
    </div>
  )
}


export function ErrorBox({ message, onRetry }) {
  return (
    <div style={{
      background: 'var(--coral-bg)', border: '1px solid var(--coral)',
      borderRadius: 'var(--r2)', padding: '12px 16px',
      color: 'var(--coral2)', fontSize: '13px',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    }}>
      <span>⚠ {message}</span>
      {onRetry && <Btn size="sm" variant="danger" onClick={onRetry}>Повторить</Btn>}
    </div>
  )
}


export function ControlsBar({ children }) {
  return (
    <div style={{
      background: 'var(--bg2)', borderBottom: '1px solid var(--border)',
      padding: '9px 16px', display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap',
    }}>
      {children}
    </div>
  )
}

export function CtrlSep() {
  return <div style={{ width: '1px', height: '20px', background: 'var(--border)', flexShrink: 0 }}/>
}

export function Card({ children, style }) {
  return (
    <div style={{
      background: 'var(--bg2)', border: '1px solid var(--border)',
      borderRadius: 'var(--r2)', ...style,
    }}>
      {children}
    </div>
  )
}


export function SharePanel({ onShare, sessionUrl }) {
  const [copied, setCopied] = React.useState(false)
  const copy = () => {
    if (!sessionUrl) return
    navigator.clipboard.writeText(location.origin + sessionUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
      <Btn size="sm" onClick={onShare}>⤴ Поделиться</Btn>
      {sessionUrl && (
        <button onClick={copy} style={{
          fontSize: '11px', fontFamily: 'var(--mono)', padding: '3px 8px',
          borderRadius: 'var(--r)', border: '1px solid var(--teal)',
          background: copied ? 'var(--teal-bg)' : 'none',
          color: 'var(--teal2)', cursor: 'pointer', transition: 'all .2s',
        }}>
          {copied ? '✓ скопировано' : sessionUrl}
        </button>
      )}
    </div>
  )
}