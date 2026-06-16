import React from "react";
import { BrowserRouter, Routes, Route, Navigate  } from "react-router-dom";
import { AppShell } from "./components/layout/AppShell";
import HomePage from "./components/layout/HomePage";
import SortPage from "./components/sort/SortPage";
import GraphPage from "./components/graph/GraphPage";
import TreePage from "./components/tree/TreePage";
import DPPage from "./components/dp/DPPage";
import './styles/globals.css'



function App() {
    return (
        <BrowserRouter>
            <AppShell>
                <Routes>
                    <Route path="/" element={<HomePage />}></Route>
                    <Route path="/sort" element={<SortPage />}></Route>
                    <Route path="/graph" element={<GraphPage />}></Route>
                    <Route path="/tree" element={<TreePage />}></Route>
                    <Route path="/dp" element={<DPPage />}></Route>
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </AppShell>
        </BrowserRouter>
    )
}

export default App