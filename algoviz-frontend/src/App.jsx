import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppShell } from "./components/layout/AppShell";
import './styles/globals.css'

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
                    <Route path="/" element={<Placeholder title='Главная' />}></Route>
                    <Route path="/sort" element={<Placeholder title='Сортировки' />}></Route>
                    <Route path="/graph" element={<Placeholder title='Графы' />}></Route>
                    <Route path="/tree" element={<Placeholder title='Деревья' />}></Route>
                    <Route path="/dp" element={<Placeholder title='ДП' />}></Route>
                </Routes>
            </AppShell>
        </BrowserRouter>
    )
}

export default App