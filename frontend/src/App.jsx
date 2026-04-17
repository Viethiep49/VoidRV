import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import AnalyzePage from './pages/AnalyzePage'
import RestaurantPage from './pages/RestaurantPage'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/analyze" element={<AnalyzePage />} />
        <Route path="/restaurant/:slug" element={<RestaurantPage />} />
      </Routes>
    </div>
  )
}
