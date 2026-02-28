import React, { useState, useEffect } from 'react'
import Login from './Login'
import PatientDashboard from './PatientDashboard'
import DoctorDashboard from './DoctorDashboard'
import AdminDashboard from './AdminDashboard'
import './styles.css'

export default function App() {
  const [user, setUser] = useState(null)

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')
    const username = localStorage.getItem('username')
    const name = localStorage.getItem('name')
    
    if (token && role) {
      setUser({ token, role, username, name })
    }
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('username')
    localStorage.removeItem('name')
    setUser(null)
  }

  if (!user) {
    return <Login onLogin={handleLogin} />
  }

  switch (user.role) {
    case 'admin':
      return <AdminDashboard user={user} onLogout={handleLogout} />
    case 'doctor':
      return <DoctorDashboard user={user} onLogout={handleLogout} />
    case 'patient':
      return <PatientDashboard user={user} onLogout={handleLogout} />
    default:
      return <Login onLogin={handleLogin} />
  }
}
