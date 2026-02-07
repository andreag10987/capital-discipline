import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import SessionsPage from './pages/SessionsPage'
import OperationsPage from './pages/OperationsPage'
import ReportsPage from './pages/ReportsPage'
import GoalPlannerPage from './pages/GoalPlannerPage'
import GoalsPage from './pages/GoalsPage'
import PrivacyPage from './pages/PrivacyPage'
import SupportPage from './pages/SupportPage'
import DisclaimerPage from './pages/DisclaimerPage'
import Layout from './components/layout/Layout'
import Toast from './components/common/Toast'
import ErrorBoundary from './components/common/ErrorBoundary'
import './App.css'
import UpgradePage from './pages/UpgradePage'
import AdminLayout from './pages/admin/AdminLayout';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminUsers from './pages/admin/AdminUsers';
import AdminUserDetail from './pages/admin/AdminUserDetail';

function PrivateRoute({ children }) {
  const { token } = useAuthStore()
  return token ? children : <Navigate to="/login" />
}

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Toast />
       <Routes>
  {/* Rutas públicas */}
  <Route path="/login" element={<LoginPage />} />
  <Route path="/register" element={<RegisterPage />} />
  <Route path="/privacy" element={<PrivacyPage />} />
  <Route path="/support" element={<SupportPage />} />
  <Route path="/disclaimer" element={<DisclaimerPage />} />

  {/* Rutas privadas - Dashboard principal */}
  <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
    <Route index element={<DashboardPage />} />
    <Route path="sessions" element={<SessionsPage />} />
    <Route path="operations/:sessionId" element={<OperationsPage />} />
    <Route path="reports" element={<ReportsPage />} />
    <Route path="goal-planner" element={<GoalPlannerPage />} />
    <Route path="goals" element={<GoalsPage />} />
    <Route path="upgrade" element={<UpgradePage />} />
  </Route>


{/* Rutas de Admin - También protegidas */}
<Route path="/admin" element={<PrivateRoute><AdminLayout /></PrivateRoute>}>
  <Route index element={<AdminDashboard />} />
  <Route path="users" element={<AdminUsers />} />
  <Route path="users/:userId" element={<AdminUserDetail />} />
</Route>

</Routes>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App