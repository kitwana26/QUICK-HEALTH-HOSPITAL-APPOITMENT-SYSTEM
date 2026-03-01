import React, { useState } from 'react'
import api from './api'

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('patient')
  const [isRegistering, setIsRegistering] = useState(false)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')

  const handleLogin = async (e) => {
    e.preventDefault()
    try {
      console.log('Attempting login to:', api.defaults.baseURL)
      const res = await api.post('/login/', { username, password })
      const { token, role: userRole, name: userName } = res.data
      localStorage.setItem('token', token)
      localStorage.setItem('role', userRole)
      localStorage.setItem('username', username)
      localStorage.setItem('name', userName)
      onLogin({ token, role: userRole, username, name: userName })
    } catch (err) {
      console.error('Login error:', err)
      const errorMessage = err.response?.data?.error || err.message || 'Network error occurred'
      alert('Login failed: ' + errorMessage)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    try {
      const res = await api.post('/register/', { 
        username, password, email, role, name 
      })
      alert('Registered successfully! Please login.')
      setIsRegistering(false)
    } catch (err) {
      alert(err.response?.data?.error || err.message)
    }
  }

  return (
    <div className="login-container">
      <div className="login-box">
        <h1 className="app-title">welcome at Quick health hospital appoitment system</h1>
        
        
        
        <form onSubmit={isRegistering ? handleRegister : handleLogin}>
          {isRegistering && (
            <>
              <input 
                type="text" 
                placeholder="Full Name" 
                value={name} 
                onChange={e => setName(e.target.value)} 
                className="form-input"
                required 
              />
              <input 
                type="email" 
                placeholder="Email" 
                value={email} 
                onChange={e => setEmail(e.target.value)} 
                className="form-input"
              />
            </>
          )}
          
          <input 
            type="text" 
            placeholder="Username" 
            value={username} 
            onChange={e => setUsername(e.target.value)} 
            className="form-input"
            required 
          />
          
          <input 
            type="password" 
            placeholder="Password" 
            value={password} 
            onChange={e => setPassword(e.target.value)} 
            className="form-input"
            required 
          />
          
          {isRegistering && (
            <select 
              value={role} 
              onChange={e => setRole(e.target.value)} 
              className="form-select"
            >
              <option value="patient">Patient</option>
              <option value="doctor">Doctor</option>
            </select>
          )}
          
          <button type="submit" className="btn-primary">
            {isRegistering ? 'Register' : 'Login'}
          </button>
        </form>
        
        <p className="toggle-text">
          {isRegistering ? 'Already have an account?' : "Don't have an account?"}
          <button 
            className="btn-link" 
            onClick={() => setIsRegistering(!isRegistering)}
          >
            {isRegistering ? 'Login' : 'Register'}
          </button>
        </p>
      </div>
    </div>
  )
}
