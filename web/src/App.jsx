import { Link, Route, Routes } from 'react-router-dom'
import Dashboard from './components/Dashboard.jsx'
import VendorPage from './components/VendorPage.jsx'
import Footer from './components/Footer.jsx'

export default function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <div className="flex-1">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/vendors/:id" element={<VendorPage />} />
          <Route path="*" element={<div className="mx-auto max-w-7xl p-4">Not found. <Link className="underline" to="/">Home</Link></div>} />
        </Routes>
      </div>
      <Footer />
    </div>
  )
}
