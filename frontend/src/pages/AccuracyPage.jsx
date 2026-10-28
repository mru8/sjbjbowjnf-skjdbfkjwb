import { useCutoff } from '../CutoffContext.jsx'

export default function AccuracyPage() {
    const { cutoff } = useCutoff()
    return <p>Accuracy page. Cutoff is {cutoff}.</p>
}