import React, { useState, useEffect } from 'react'
import api from './api'

export default function AdminDashboard({ user, onLogout }) {
  const [activeTab, setActiveTab] = useState('doctors')
  const [doctors, setDoctors] = useState([])
  const [patients, setPatients] = useState([])
  const [showAddDoctor, setShowAddDoctor] = useState(false)
  const [showAssignPatient, setShowAssignPatient] = useState(false)
  
  // Form states
  const [newDoctor, setNewDoctor] = useState({ username: '', password: '', email: '', name: '' })
  const [assignData, setAssignData] = useState({ patient_username: '', doctor_username: '', disease: '' })

  useEffect(() => {
    fetchDoctors()
    fetchPatients()
  }, [])

  const fetchDoctors = async () => {
    try {
      const res = await api.get('/admin/doctors/')
      setDoctors(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const fetchPatients = async () => {
    try {
      const res = await api.get('/admin/patients/')
      setPatients(Object.entries(res.data).map(([username, data]) => ({ username, ...data })))
    } catch (err) {
      console.error(err)
    }
  }

  const handleAddDoctor = async (e) => {
    e.preventDefault()
    try {
      await api.post('/admin/doctors/', newDoctor)
      alert('Doctor added successfully!')
      setShowAddDoctor(false)
      setNewDoctor({ username: '', password: '', email: '', name: '' })
      fetchDoctors()
    } catch (err) {
      alert(err.response?.data?.error || err.message)
    }
  }

  const handleDeleteDoctor = async (username) => {
    if (!confirm('Are you sure you want to delete this doctor?')) return
    try {
      await api.delete(`/admin/doctors/${username}/`)
      fetchDoctors()
    } catch (err) {
      alert(err.response?.data?.error || err.message)
    }
  }

  const handleAssignPatient = async (e) => {
    e.preventDefault()
    try {
      await api.post('/admin/patients/', assignData)
      alert('Patient assigned to doctor!')
      setShowAssignPatient(false)
      setAssignData({ patient_username: '', doctor_username: '', disease: '' })
      fetchPatients()
    } catch (err) {
      alert(err.response?.data?.error || err.message)
    }
  }

  const handleDeletePatient = async (username) => {
    if (!confirm('Are you sure you want to delete this patient?')) return
    try {
      await api.delete(`/admin/patients/${username}/`)
      fetchPatients()
    } catch (err) {
      alert(err.response?.data?.error || err.message)
    }
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1> Quick Health Appointment System - Admin Panel</h1>
        <div className="header-right">
          <span>Welcome, {user.name || user.username}</span>
          <button className="btn-secondary" onClick={onLogout}>Logout</button>
        </div>
      </header>

      <nav className="dashboard-nav">
        <button 
          className={`nav-btn ${activeTab === 'doctors' ? 'active' : ''}`}
          onClick={() => setActiveTab('doctors')}
        >
          Manage Doctors
        </button>
        <button 
          className={`nav-btn ${activeTab === 'patients' ? 'active' : ''}`}
          onClick={() => setActiveTab('patients')}
        >
           Manage Patients
        </button>
      </nav>

      <main className="dashboard-content">
        {activeTab === 'doctors' && (
          <div className="section">
            <div className="section-header">
              <h2>Doctors Management</h2>
              <button className="btn-primary" onClick={() => setShowAddDoctor(true)}>
                + Add Doctor
              </button>
            </div>

            {showAddDoctor && (
              <div className="modal-overlay">
                <div className="modal">
                  <h3>Add New Doctor</h3>
                  <form onSubmit={handleAddDoctor}>
                    <input 
                      type="text" placeholder="Full Name" 
                      value={newDoctor.name} onChange={e => setNewDoctor({...newDoctor, name: e.target.value})}
                      className="form-input" required 
                    />
                    <input 
                      type="text" placeholder="Username" 
                      value={newDoctor.username} onChange={e => setNewDoctor({...newDoctor, username: e.target.value})}
                      className="form-input" required 
                    />
                    <input 
                      type="password" placeholder="Password" 
                      value={newDoctor.password} onChange={e => setNewDoctor({...newDoctor, password: e.target.value})}
                      className="form-input" required 
                    />
                    <input 
                      type="email" placeholder="Email" 
                      value={newDoctor.email} onChange={e => setNewDoctor({...newDoctor, email: e.target.value})}
                      className="form-input" 
                    />
                    <div className="modal-actions">
                      <button type="submit" className="btn-primary">Add Doctor</button>
                      <button type="button" className="btn-secondary" onClick={() => setShowAddDoctor(false)}>Cancel</button>
                    </div>
                  </form>
                </div>
              </div>
            )}

            <div className="card-grid">
              {doctors.map(doctor => (
                <div key={doctor.username} className="card">
                  <div className="card-icon"></div>
                  <h3>{doctor.name || doctor.username}</h3>
                  <p>Email: {doctor.email || 'N/A'}</p>
                  <p>Username: {doctor.username}</p>
                  <button 
                    className="btn-danger" 
                    onClick={() => handleDeleteDoctor(doctor.username)}
                  >
                    Delete
                  </button>
                </div>
              ))}
              {doctors.length === 0 && <p className="empty-message">No doctors found</p>}
            </div>
          </div>
        )}

        {activeTab === 'patients' && (
          <div className="section">
            <div className="section-header">
              <h2>Patients Management</h2>
              <button className="btn-primary" onClick={() => setShowAssignPatient(true)}>
                + Assign Patient to Doctor
              </button>
            </div>

            {showAssignPatient && (
              <div className="modal-overlay">
                <div className="modal">
                  <h3>Assign Patient to Doctor</h3>
                  <form onSubmit={handleAssignPatient}>
                    <input 
                      type="text" placeholder="Patient Username" 
                      value={assignData.patient_username} onChange={e => setAssignData({...assignData, patient_username: e.target.value})}
                      className="form-input" required 
                    />
                    <select 
                      value={assignData.doctor_username} onChange={e => setAssignData({...assignData, doctor_username: e.target.value})}
                      className="form-select" required
                    >
                      <option value="">Select Doctor</option>
                      {doctors.map(d => (
                        <option key={d.username} value={d.username}>{d.name || d.username}</option>
                      ))}
                    </select>
                    <input 
                      type="text" placeholder="Disease" 
                      value={assignData.disease} onChange={e => setAssignData({...assignData, disease: e.target.value})}
                      className="form-input" 
                    />
                    <div className="modal-actions">
                      <button type="submit" className="btn-primary">Assign</button>
                      <button type="button" className="btn-secondary" onClick={() => setShowAssignPatient(false)}>Cancel</button>
                    </div>
                  </form>
                </div>
              </div>
            )}

            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Full Name</th>
                    <th>Age</th>
                    <th>Gender</th>
                    <th>Disease</th>
                    <th>Doctor</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {patients.map(patient => (
                    <tr key={patient.username}>
                      <td>{patient.username}</td>
                      <td>{patient.full_name || 'N/A'}</td>
                      <td>{patient.age || 'N/A'}</td>
                      <td>{patient.gender || 'N/A'}</td>
                      <td>{patient.disease || 'N/A'}</td>
                      <td>{patient.doctor || 'Not Assigned'}</td>
                      <td>
                        <span className={`status-badge status-${patient.status}`}>
                          {patient.status || 'pending'}
                        </span>
                      </td>
                      <td>
                        <button 
                          className="btn-danger btn-sm"
                          onClick={() => handleDeletePatient(patient.username)}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                  {patients.length === 0 && (
                    <tr><td colSpan="8" className="empty-message">No patients found</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
