import { createContext, useContext, useState } from "react";

const CutoffContext = createContext(null)

export function CutoffProvider({ children }) {
    const [cutoff, setCutoff] = useState('09:50')
    return (
        <CutoffContext.Provider value={{ cutoff, setCutoff }}>
            {children}
        </CutoffContext.Provider>
    )
}

export function useCutoff() {
    return useContext(CutoffContext)
}