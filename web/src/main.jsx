import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import Honeybadger from '@honeybadger-io/js'
import './index.css'
import { registerIntercepts } from 'apis/axios'
import queryClient from 'utils/queryClient'
import App from './App.jsx'

if (import.meta.env.VITE_HONEYBADGER_API_KEY) {
  Honeybadger.configure({
    apiKey: import.meta.env.VITE_HONEYBADGER_API_KEY,
    environment: import.meta.env.MODE,
    // Every browser error is tagged so Honeybadger's GitHub integration can label the issue.
    tags: ['frontend', 'bug'],
  })
  // Console handle for smoke tests: Honeybadger.notify(new Error('frontend smoke test'))
  window.Honeybadger = Honeybadger
}

registerIntercepts()

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
)
