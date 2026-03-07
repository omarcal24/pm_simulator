import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@/features/simulation/hooks/useAuth'
import Landing from '@/pages/Landing'
import ScenariosList from '@/pages/ScenariosList'
import ScenarioDetail from '@/pages/ScenarioDetail'
import RunPage from '@/pages/RunPage'
import CaseStudyPage from '@/pages/CaseStudyPage'
import Login from '@/pages/Login'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex min-h-screen items-center justify-center">Loading...</div>
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/scenarios" element={<ScenariosList />} />
      <Route path="/scenarios/:id" element={<ScenarioDetail />} />
      <Route
        path="/runs/:id"
        element={
          <ProtectedRoute>
            <RunPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/case-studies/:id"
        element={
          <ProtectedRoute>
            <CaseStudyPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
