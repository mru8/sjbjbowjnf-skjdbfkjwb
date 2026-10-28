import { useEffect, useState } from "react";
import {
    Bar,
    BarChart,
    CartesianGrid,
    Legend,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts'
import { useCutoff } from '../CutoffContext.jsx'
import { getAccuracy } from "../api.js";

const START = '2026-01-01'
const END = '2026-01-31'

function mw(value) {
    return Math.round(value).toLocaleString('en-GB') + ' MW'
}

export default function AccuracyPage() {
    const { cutoff } = useCutoff()
    const [data, setData] = useState(null)
    const [error, setError] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        let ignore = false
        setLoading(true)
        setError(null)
        getAccuracy(START, END, cutoff)
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
    }, [cutoff])

    if (loading) return <p>Loading...</p>
    if (error) return <p style={{color: "crimson"}}>Could not load: {error}</p>
    if (!data) return null

    const s = data.summary
    const direction = s.bias > 0 ? 'too high' : 'too low'

    return (
        <div>
            <p>
                {s.n_hours} hours, {data.start} to {data.end}, cutoff {data.cutoff} (UK time, D-1).
            </p>

            <div className="cards">
                <div className="card headline">
                    <div className="card-label">P95 absolute error</div>
                    <div className="card-value">{mw(s.p95_abs_error)}</div>
                    <div className="cart-note">
                        In 95% of hours the forecast was within this many MW of the actual.
                    </div>
                </div>
                <div className="card">
                    <div className="card-label">MAE</div>
                    <div className="card-value">{mw(s.mae)}</div>
                    <div className="card-note">Average size of the miss.</div>
                </div>
                <div className="card">
                    <div className="card-label">RMSE</div>
                    <div className="card-value">{mw(s.rmse)}</div>
                    <div className="card-note">Like MAE, but big misses count extra.</div>
                </div>
                <div className="card">
                    <div className="card-label">Bias</div>
                    <div className="card-value">
                        {s.bias > 0 ? '+': ''}
                        {mw(s.bias)}
                    </div>
                    <div className="card-note">
                        On average the forecast was {direction} (forecast minus actual).
                    </div>
                </div>
            </div>

            <h2>Error by hour of the day</h2>
            <div style={{ width: '100%', height: 360}}>
                <ResponsiveContainer>
                    <BarChart data={data.by_hour}>
                        <CartesianGrid strokeDasharray="3 3"/>
                        <XAxis dataKey="hour" interval={1}/>
                        <YAxis unit=" MW" width={80}/>
                        <Tooltip formatter={(v) => mw(v)} labelFormatter={(h) => `Hour ${h}:00`}/>
                        <Legend/>
                        <Bar dataKey="mae" name="MAE" fill="#0a6"/>
                        <Bar dataKey="bias" name="Bias" fill="#d33"/>
                    </BarChart>
                </ResponsiveContainer>
            </div>
            <p className="hint">Hours are UTC, which equals UK time in January.</p>
        </div>
    )
}