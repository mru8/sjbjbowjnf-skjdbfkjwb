const API_URL = import.meta.env.VITE_API_URL

export async function getForecast(day, cutoff) {
    const url = `${API_URL}/forecast?day=${day}&cutoff=${encodeURIComponent(cutoff)}`
    const res = await fetch(url)
    if (!res.ok) throw new Error(`API error ${res.status}`)
        return res.json()
}

export async function getAccuracy(start, end, cutoff) {
    const url = `${API_URL}/accuracy?start=${start}&end=${end}&cutoff=${encodeURIComponend(cutoff)}`
    const res = await fetch(url)
    if (!res.ok) throw new Error(`API error ${res.status}`)
    return res.json()
}