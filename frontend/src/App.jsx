import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import TicketDetailPage from './pages/TicketDetailPage'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/tickets/:id" element={<TicketDetailPage />} />
      </Routes>
    </div>
  )
}

export default App
