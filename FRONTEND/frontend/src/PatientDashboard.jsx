import React, { useState, useEffect } from 'react'
import axios from 'axios'
import Calendar from './Calendar'
import MedicalRecords from './MedicalRecords'

const API_URL = 'http://localhost:8000/api'

export default function PatientDashboard({ user, onLogout }) {
  const [activeTab, setActiveTab] = useState('profile')
  const [profile, setProfile] = useState({
    full_name: '',
    age: '',
    marital_status: '',
    gender: '',
    address: '',
    phone: '',
    email: '',
    disease: ''
  })
  const [appointment, setAppointment] = useState({
    doctor_username: '',
    disease: '',
    appointment_date: '',
    appointment_time: ''
  })
  const [doctors, setDoctors] = useState([])
  const [message, setMessage] = useState('')
  const [showCalendar, setShowCalendar] = useState(false)
  const [calendarKey, setCalendarKey] = useState(0)

  const token = localStorage.getItem('token')
  const username = localStorage.getItem('username')
  const config = { headers: { Authorization: `Token ${token}` } }

  useEffect(() => {
    fetchProfile()
    fetchDoctors()
  }, [])

  const fetchProfile = async () => {
    try {
      const res = await axios.get(`${API_URL}/patient/profile/`, config)
      if (res.data && Object.keys(res.data).length > 0) {
        setProfile(res.data)
        if (res.data.disease) {
          setAppointment(prev => ({ ...prev, disease: res.data.disease }))
        }
      }
    } catch (err) {
      console.error(err)
    }
  }

  const fetchDoctors = async () => {
    try {
      const res = await axios.get(`${API_URL}/admin/doctors/`, config)
      setDoctors(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const handleSaveProfile = async (e) => {
    e.preventDefault()
    try {
      await axios.post(`${API_URL}/patient/profile/`, profile, config)
      setMessage('Profile saved successfully!')
      setTimeout(() => setMessage(''), 3000)
    } catch (err) {
      alert(err.response?.data?.error || err.message)
    }
  }

  const handleMakeAppointment = async (e) => {
    e.preventDefault()
    try {
      await axios.post(`${API_URL}/patient/appointment/`, appointment, config)
      setMessage('Appointment requested successfully!')
      setTimeout(() => setMessage(''), 3000)
      // Clear form after successful booking
      setAppointment({
        doctor_username: '',
        disease: '',
        appointment_date: '',
        appointment_time: ''
      })
      // Switch to calendar view to see the appointment
      setActiveTab('calendar')
    } catch (err) {
      alert(err.response?.data?.error || err.message)
    }
  }

  // Get minimum date (today) to prevent booking past dates
  const getMinDate = () => {
    const today = new Date()
    return today.toISOString().split('T')[0]
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1> Quick Health Appointment System - Patient Portal</h1>
        <div className="header-right">
          <span>Welcome, {user.name || user.username}</span>
          <button className="btn-secondary" onClick={onLogout}>Logout</button>
        </div>
      </header>

      <nav className="dashboard-nav">
        <button 
          className={`nav-btn ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          📋 My Profile
        </button>
        <button 
          className={`nav-btn ${activeTab === 'appointment' ? 'active' : ''}`}
          onClick={() => setActiveTab('appointment')}
        >
          📅 Book Appointment
        </button>
        <button 
          className={`nav-btn ${activeTab === 'calendar' ? 'active' : ''}`}
          onClick={() => setActiveTab('calendar')}
        >
          📆 My Schedule
        </button>
        <button 
          className={`nav-btn ${activeTab === 'records' ? 'active' : ''}`}
          onClick={() => setActiveTab('records')}
        >
          📋 Medical Records
        </button>
      </nav>

      <main className="dashboard-content">
        {activeTab === 'profile' && (
          <div className="section">
            <h2>Patient Information</h2>
            {message && <div className="success-message">{message}</div>}
            
            <form onSubmit={handleSaveProfile} className="profile-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Full Name</label>
                  <input 
                    type="text" 
                    value={profile.full_name} 
                    onChange={e => setProfile({...profile, full_name: e.target.value})}
                    className="form-input"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Age</label>
                  <input 
                    type="number" 
                    value={profile.age} 
                    onChange={e => setProfile({...profile, age: e.target.value})}
                    className="form-input"
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Marital Status</label>
                  <select 
                    value={profile.marital_status} 
                    onChange={e => setProfile({...profile, marital_status: e.target.value})}
                    className="form-select"
                    required
                  >
                    <option value="">Select Status</option>
                    <option value="single">Single</option>
                    <option value="married">Married</option>
                    <option value="divorced">Divorced</option>
                    <option value="widowed">Widowed</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Gender</label>
                  <select 
                    value={profile.gender} 
                    onChange={e => setProfile({...profile, gender: e.target.value})}
                    className="form-select"
                    required
                  >
                    <option value="">Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Address</label>
                <input 
                  type="text" 
                  value={profile.address} 
                  onChange={e => setProfile({...profile, address: e.target.value})}
                  className="form-input"
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Phone Number</label>
                  <input 
                    type="tel" 
                    value={profile.phone} 
                    onChange={e => setProfile({...profile, phone: e.target.value})}
                    className="form-input"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input 
                    type="email" 
                    value={profile.email} 
                    onChange={e => setProfile({...profile, email: e.target.value})}
                    className="form-input"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Disease/Symptoms</label>
                <textarea 
                  value={profile.disease} 
                  onChange={e => setProfile({...profile, disease: e.target.value})}
                  className="form-input"
                  rows="3"
                  placeholder="Describe your symptoms or disease"
                />
              </div>

              <button type="submit" className="btn-primary">Save Profile</button>
            </form>
          </div>
        )}

        {activeTab === 'appointment' && (
          <div className="section">
            <h2>Book Appointment</h2>
            {message && <div className="success-message">{message}</div>}
            
            <div className="appointment-info">
              <p><strong>Status:</strong> {profile.status || 'pending'}</p>
              <p><strong>Assigned Doctor:</strong> {profile.doctor || 'Not assigned yet'}</p>
            </div>

            {!profile.doctor ? (
              <div className="info-message">
                <p>You have not been assigned a doctor yet. Please contact the admin to get assigned to a doctor.</p>
              </div>
            ) : (
              <form onSubmit={handleMakeAppointment} className="appointment-form">
                <div className="form-group">
                  <label>Your Assigned Doctor</label>
                  <input
                    type="text"
                    value={`Dr. ${profile.doctor}`}
                    className="form-input"
                    disabled
                  />
                </div>

                <div className="form-group">
                  <label>Disease/Symptoms</label>
                  <textarea 
                    value={appointment.disease} 
                    onChange={e => setAppointment({...appointment, disease: e.target.value})}
                    className="form-input"
                    rows="3"
                    placeholder="Describe your symptoms"
                    required
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Preferred Date</label>
                    <input
                      type="date"
                      value={appointment.appointment_date}
                      onChange={e => setAppointment({...appointment, appointment_date: e.target.value})}
                      className="form-input"
                      min={getMinDate()}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Preferred Time</label>
                    <input
                      type="time"
                      value={appointment.appointment_time}
                      onChange={e => setAppointment({...appointment, appointment_time: e.target.value})}
                      className="form-input"
                    />
                  </div>
                </div>

                <button type="submit" className="btn-primary">Request Appointment</button>
              </form>
            )}
          </div>
        )}

        {activeTab === 'calendar' && (
          <Calendar user={user} role="patient" />
        )}

        {activeTab === 'records' && (
          <MedicalRecords user={user} role="patient" />
        )}
      </main>
    </div>
  )
}
