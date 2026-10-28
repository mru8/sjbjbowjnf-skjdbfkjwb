import { StrictMode } from "react"
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import { CutoffProvider } from './CutoffContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <CutoffProvider>
        <App />
      </CutoffProvider>
    </BrowserRouter>
  </StrictMode>
)