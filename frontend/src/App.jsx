import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import { useCutoff } from './CutoffContext.jsx'
import ForecastPage from './pages/ForecastPage.jsx'
import AccuracyPage from './pages/AccuracyPage.jsx'

export default function App() {
  const { cutoff, setCutoff } = useCutoff()

  return (
    <div className="app">
      <header className="header">
        <h1>Wind forecast: Purchase decisions made in January 2026</h1>
        <label>
          Decision cutoff (D-1, UK time){' '}
          <select value={cutoff} onChange={(e) => setCutoff(e.target.value)}>
            <option value="09:20">09:20 (EPEX hourly)</option>
            <option value="09:50">09:50 (N2EX)</option>
            <option value="15:30">15:30 (EPEX half-hourly)</option>
          </select>
        </label>
      </header>

      <nav className="tabs">
        <NavLink to="/forecast">Forecast</NavLink>
        <NavLink to="/accuracy">Accuracy</NavLink>
      </nav>

      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/forecast" replace />} />
          <Route path="/forecast" element={<ForecastPage/>} />
          <Route path="/accuracy" element={<AccuracyPage/>} />
        </Routes>
      </main>
    </div>
  )
}