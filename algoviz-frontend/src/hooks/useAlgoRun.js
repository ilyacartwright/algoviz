import { useState, useRef, useCallback } from 'react'

export function useAlgoRun(fetchFn) {
    const stepsRef = useRef([])
    const timerRef = useRef(null)

    const [state, setState] = useState({
        status: 'idle',
        stepIndex: 0,
        currentStep: null,
        total: 0,
        speed: 5,
        error: null,
        response: null,
    })

    const _clear = () => {
        if (timerRef.current) {
            clearInterval(timerRef.current)
            timerRef.current = null
        }
    }

    const speedToMs = (s) => Math.round(1500 - (s - 1) * (1450 / 9))

    const _tick = useCallback(() => {
        setState(prev => {
            const idx = prev.stepIndex
            if (idx >= stepsRef.current.length) {
                _clear()
                return { ...prev, status: 'done' }
            }
            return {
                ...prev,
                currentStep: stepsRef.current[idx],
                stepIndex: idx + 1,
            }
        })
    }, [])

    const _startTimer = useCallback((speed) => {
        _clear()
        timerRef.current = setInterval(_tick, speedToMs(speed))
    }, [_tick])

    const load = useCallback(async () => {
        _clear()
        setState(s => ({
            ...s,
            status: 'loading', stepIndex: 0, currentStep: null, error: null,
        }))
        try {
            const res = await fetchFn()
            stepsRef.current = res.steps
            setState(s => ({
                ...s,
                status: 'paused', total: res.total_steps, response: res,
            }))
        } catch (e) {
            setState(s => ({ ...s, status: 'error', error: e.message }))
        }
    }, [fetchFn])

    const play = useCallback(() => {
        setState(s => {
            if (s.stepIndex >= stepsRef.current.length) return s
            _startTimer(s.speed)
            return { ...s, status: 'playing' }
        })
    }, [_startTimer])

    const pause = useCallback(() => {
        _clear()
        setState(s => ({ ...s, status: 'paused' }))
    }, [])

    const step = useCallback(() => {
        setState(prev => {
            const idx = prev.stepIndex
            if (idx >= stepsRef.current.length) return { ...prev, status: 'done' }
            return {
                ...prev,
                currentStep: stepsRef.current[idx],
                stepIndex: idx + 1,
                status: idx + 1 >= stepsRef.current.length ? 'done' : 'paused',
            }
        })
    }, [])

    const stepBack = useCallback(() => {
        setState(prev => {
            const idx = prev.stepIndex - 1
            if (idx <= 0) return { ...prev, stepIndex: 0, currentStep: null, status: 'paused' }
            return {
                ...prev,
                stepIndex: idx,
                currentStep: stepsRef.current[idx - 1],
                status: 'paused',
            }
        })
    }, [])

    const jumpTo = useCallback((idx) => {
        const clamped = Math.max(0, Math.min(idx, stepsRef.current.length))
        _clear()
        setState(prev => ({
            ...prev,
            stepIndex: clamped,
            currentStep: clamped > 0 ? stepsRef.current[clamped - 1] : null,
            status: clamped >= stepsRef.current.length ? 'done' : 'paused',
        }))
    }, [])

    const setSpeed = useCallback((v) => {
        setState(s => {
            if (s.status === 'playing') _startTimer(v)
            return { ...s, speed: v }
        })
    }, [_startTimer])

    const reset = useCallback(() => {
        _clear()
        stepsRef.current = []
        setState({
            status: 'idle', stepIndex: 0, currentStep: null,
            total: 0, speed: 5, error: null, response: null,
        })
    }, [])

    return { state, load, play, pause, step, stepBack, jumpTo, setSpeed, reset }
}