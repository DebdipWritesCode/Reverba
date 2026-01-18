import { Route, Routes } from 'react-router-dom'
import Login from '@/pages/Auth/Login'
import Signup from '@/pages/Auth/Signup'
import ProtectedRoute from './ProtectedRoute'
import DashboardLayout from '@/layouts/DashboardLayout'
import AddWords from '@/pages/AddWords'
import TodaysTasks from '@/pages/TodaysTasks'
import ChatHistory from '@/pages/ChatHistory'
import MyProfile from '@/pages/MyProfile'

// Placeholder dashboard component
const Dashboard = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
        <p className="text-muted-foreground">Welcome to your vocabulary app!</p>
      </div>
    </div>
  )
}



// Placeholder landing page
const Landing = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Reverba</h1>
        <p className="text-muted-foreground mb-8">Learn and master new words</p>
        <div className="space-x-4">
          <a href="/login" className="text-primary hover:underline">Login</a>
          <a href="/signup" className="text-primary hover:underline">Sign Up</a>
        </div>
      </div>
    </div>
  )
}

// 404 page
const NotFound = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">404</h1>
        <p className="text-muted-foreground mb-8">Page not found</p>
        <a href="/" className="text-primary hover:underline">Go home</a>
      </div>
    </div>
  )
}

const Router = () => {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/today-tasks" element={<TodaysTasks />} />
        <Route path="/add-words" element={<AddWords />} />
        <Route path="/chat-history" element={<ChatHistory />} />
        <Route path="/my-profile" element={<MyProfile />} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default Router
