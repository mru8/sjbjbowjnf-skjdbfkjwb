import { useEffect, useState } from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useCutoff } from '../CutoffContext.jsx'
import { getForecast } from '../api.js'

export default function ForecastPage() {
  const { cutoff } = useCutoff()
  const [day, setDay] = useState('2026-01-15')
  const [showActual, setShowActual] = useState(true)
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let ignore = false
    setLoading(true)
    setError(null)
    getForecast(day, cutoff)
      .then((result) => {
        if (!ignore) setData(result)
      })
      .catch((err) => {
        if (!ignore) setError(err.message)
      })
      .finally(() => {
        if (!ignore) setLoading(false)
      })
    return () => {
      ignore = true
    }
  }, [day, cutoff])

  const chartData = data
    ? data.hours.map((h) => ({
        time: h.startTime.slice(11, 16),
        forecast: h.forecast,
        actual: h.actual,
      }))
    : []

  const editions = data
    ? [...new Set(data.hours.map((h) => h.publishTime.slice(0, 16).replace('T', ' ')))]
    : []

  return (
    <div>
      <div className="controls">
        <label>
          Delivery day{' '}
          <input
            type="date"
            value={day}
            min="2026-01-02"
            max="2026-02-01"
            onChange={(e) => setDay(e.target.value)}
          />
        </label>
        <label>
          <input
            type="checkbox"
            checked={showActual}
            onChange={(e) => setShowActual(e.target.checked)}
          />{' '}
          Show actual
        </label>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'crimson' }}>Could not load: {error}</p>}

      {data && !loading && (
        <div>
          <p>
            Forecast edition used (UTC): {editions.join(', ')}
          </p>
          <div style={{ width: '100%', height: 360 }}>
            <ResponsiveContainer>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" interval={2} />
                <YAxis unit=" MW" width={80} />
                <Tooltip formatter={(v) => (v == null ? 'no data' : `${Math.round(v)} MW`)} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="forecast"
                  name="Forecast"
                  stroke="#0a6"
                  strokeWidth={2}
                  dot={{ r: 2 }}
                />
                {showActual && (
                  <Line
                    type="monotone"
                    dataKey="actual"
                    name="Actual"
                    stroke="#d33"
                    strokeWidth={2}
                    dot={{ r: 2 }}
                    connectNulls={false}
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}