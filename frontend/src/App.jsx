import { Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Toast from './components/common/Toast'
import ErrorBoundary from './components/common/ErrorBoundary'
import './App.css'
import styles from './pages/DashboardPage.module.css'

const LoginPage = lazy(() => import('./pages/LoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const SessionsPage = lazy(() => import('./pages/SessionsPage'))
const OperationsPage = lazy(() => import('./pages/OperationsPage'))
const ReportsPage = lazy(() => import('./pages/ReportsPage'))
const GoalPlannerPage = lazy(() => import('./pages/GoalPlannerPage'))
const GoalsPage = lazy(() => import('./pages/GoalsPage'))
const PrivacyPage = lazy(() => import('./pages/PrivacyPage'))
const SupportPage = lazy(() => import('./pages/SupportPage'))
const DisclaimerPage = lazy(() => import('./pages/DisclaimerPage'))
const Layout = lazy(() => import('./components/layout/Layout'))
const UpgradePage = lazy(() => import('./pages/UpgradePage'))
const AdminLayout = lazy(() => import('./pages/admin/AdminLayout'))
const AdminDashboard = lazy(() => import('./pages/admin/AdminDashboard'))
const AdminUsers = lazy(() => import('./pages/admin/AdminUsers'))
const AdminUserDetail = lazy(() => import('./pages/admin/AdminUserDetail'))

function PrivateRoute({ children }) {
  const { token } = useAuthStore()
  return token ? children : <Navigate to="/login" />
}

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Toast />
        <Suspense fallback={<div className={styles.loading}>Cargando...</div>}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/privacy" element={<PrivacyPage />} />
            <Route path="/support" element={<SupportPage />} />
            <Route path="/disclaimer" element={<DisclaimerPage />} />

            <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
              <Route index element={<DashboardPage />} />
              <Route path="sessions" element={<SessionsPage />} />
              <Route path="operations/:sessionId" element={<OperationsPage />} />
              <Route path="reports" element={<ReportsPage />} />
              <Route path="goal-planner" element={<GoalPlannerPage />} />
              <Route path="goals" element={<GoalsPage />} />
              <Route path="upgrade" element={<UpgradePage />} />
            </Route>

            <Route path="/admin" element={<PrivateRoute><AdminLayout /></PrivateRoute>}>
              <Route index element={<AdminDashboard />} />
              <Route path="users" element={<AdminUsers />} />
              <Route path="users/:userId" element={<AdminUserDetail />} />
            </Route>
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
