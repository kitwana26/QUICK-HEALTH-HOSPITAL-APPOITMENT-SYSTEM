import React, { useState, useEffect } from 'react'
import api from './api'
import Calendar from './Calendar'
import MedicalRecords from './MedicalRecords'

export default function DoctorDashboard({ user, onLogout }) {
  const [activeTab, setActiveTab] = useState('patients')
  const [patients, setPatients] = useState([])
  const [appointments, setAppointments] = useState([])
  const [selectedPatient, setSelectedPatient] = useState(null)
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchPatients()
    fetchAppointments()
  }, [])

  const fetchPatients = async () => {
    try {
      const res = await api.get('/doctor/patients/')
      setPatients(Object.entries(res.data).map(([username, data]) => ({ username, ...data })))
    } catch (err) {
      console.error(err)
    }
  }

  const fetchAppointments = async () => {
    try {
      const res = await api.get('/appointments/')
      setAppointments(Object.entries(res.data).map(([id, data]) => ({ id: parseInt(id), ...data })))
    } catch (err) {
      console.error(err)
    }
  }

  const handleSignPatient = async (patientUsername) => {
    try {
      await api.post(`/doctor/patients/${patientUsername}/sign`, {})
      setMessage('Patient signed successfully!')
      setTimeout(() => setMessage(''), 3000)
      fetchPatients()
    } catch (err) {
      alert(err.response?.data?.error || err.message)
    }
  }

  const handleDischargePatient = async (patientUsername) => {
    if (!confirm('Are you sure you want to discharge this patient?')) return
    try {
      await api.post(`/doctor/patients/${patientUsername}/discharge`, {})
      setMessage('Patient discharged successfully!')
      setTimeout(() => setMessage(''), 3000)
      fetchPatients()
    } catch (err) {
      alert(err.response?.data?.error || err.message)
    }
  }

  const handleDeletePatient = async (patientUsername) => {
    if (!confirm('Are you sure you want to delete this patient record?')) return
    try {
      await api.delete(`/doctor/patients/${patientUsername}/`)
      setMessage('Patient deleted successfully!')
      setTimeout(() => setMessage(''), 3000)
      fetchPatients()
    } catch (err) {
      alert(err.response?.data?.error || err.message)
    }
  }

  const handleApproveAppointment = async (appointmentId) => {
    try {
      await api.put(`/appointments/${appointmentId}/`, { status: 'approved' })
      setMessage('Appointment approved successfully!')
      setTimeout(() => setMessage(''), 3000)
      fetchAppointments()
    } catch (err) {
      alert(err.response?.data?.error || err.message)
    }
  }

  const handleRejectAppointment = async (appointmentId) => {
    try {
      await api.put(`/appointments/${appointmentId}/`, { status: 'rejected' })
      setMessage('Appointment rejected!')
      setTimeout(() => setMessage(''), 3000)
      fetchAppointments()
    } catch (err) {
      alert(err.response?.data?.error || err.message)
    }
  }

  const handleCompleteAppointment = async (appointmentId) => {
    try {
      await api.put(`/appointments/${appointmentId}/`, { status: 'completed' })
      setMessage('Appointment completed!')
      setTimeout(() => setMessage(''), 3000)
      fetchAppointments()
    } catch (err) {
      alert(err.response?.data?.error || err.message)
    }
  }

  const getStatusBadge = (status) => {
    const statusClass = {
      'pending': 'status-pending',
      'under_treatment': 'status-treatment',
      'discharged': 'status-discharged'
    }
    return statusClass[status] || 'status-pending'
  }

  const getAppointmentStatusBadge = (status) => {
    const statusClass = {
      'pending': 'status-pending',
      'approved': 'status-approved',
      'rejected': 'status-rejected',
      'completed': 'status-completed',
      'cancelled': 'status-discharged'
    }
    return statusClass[status] || 'status-pending'
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Not set'
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1> Quick Health hospital Appointment System - Doctor Portal</h1>
        <div className="header-right">
          <span>Welcome, Dr. {user.name || user.username}</span>
          <button className="btn-secondary" onClick={onLogout}>Logout</button>
        </div>
      </header>

      <nav className="dashboard-nav">
        <button 
          className={`nav-btn ${activeTab === 'patients' ? 'active' : ''}`}
          onClick={() => setActiveTab('patients')}
        >
          👥 My Patients
        </button>
        <button 
          className={`nav-btn ${activeTab === 'appointments' ? 'active' : ''}`}
          onClick={() => setActiveTab('appointments')}
        >
          📅 Appointments
        </button>
        <button 
          className={`nav-btn ${activeTab === 'calendar' ? 'active' : ''}`}
          onClick={() => setActiveTab('calendar')}
        >
          📆 Calendar
        </button>
        <button 
          className={`nav-btn ${activeTab === 'records' ? 'active' : ''}`}
          onClick={() => setActiveTab('records')}
        >
          📋 Medical Records
        </button>
      </nav>

      <main className="dashboard-content">
        {activeTab === 'patients' && (
          <div className="section">
            <h2>My Patients</h2>
            {message && <div className="success-message">{message}</div>}
            
            <div className="stats-row">
              <div className="stat-card">
                <span className="stat-number">{patients.length}</span>
                <span className="stat-label">Total Patients</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">
                  {patients.filter(p => p.status === 'pending').length}
                </span>
                <span className="stat-label">Pending</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">
                  {patients.filter(p => p.status === 'under_treatment').length}
                </span>
                <span className="stat-label">Under Treatment</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">
                  {patients.filter(p => p.status === 'discharged').length}
                </span>
                <span className="stat-label">Discharged</span>
              </div>
            </div>

            {patients.length === 0 ? (
              <div className="empty-state">
                <p>No patients assigned to you yet.</p>
                <p>Contact admin to assign patients.</p>
              </div>
            ) : (
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Username</th>
                      <th>Full Name</th>
                      <th>Age</th>
                      <th>Gender</th>
                      <th>Phone</th>
                      <th>Disease</th>
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
                        <td>{patient.phone || 'N/A'}</td>
                        <td>{patient.disease || 'N/A'}</td>
                        <td>
                          <span className={`status-badge ${getStatusBadge(patient.status)}`}>
                            {patient.status === 'under_treatment' ? 'Under Treatment' : 
                             patient.status === 'discharged' ? 'Discharged' : 'Pending'}
                          </span>
                        </td>
                        <td className="actions-cell">
                          {patient.status !== 'under_treatment' && patient.status !== 'discharged' && (
                            <button 
                              className="btn-success btn-sm"
                              onClick={() => handleSignPatient(patient.username)}
                            >
                              ✓ Sign
                            </button>
                          )}
                          {patient.status === 'under_treatment' && (
                            <button 
                              className="btn-warning btn-sm"
                              onClick={() => handleDischargePatient(patient.username)}
                            >
                              Discharge
                            </button>
                          )}
                          <button 
                            className="btn-danger btn-sm"
                            onClick={() => handleDeletePatient(patient.username)}
                          >
                            🗑️
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'appointments' && (
          <div className="section">
            <h2>Appointments</h2>
            {message && <div className="success-message">{message}</div>}
            
            <div className="stats-row">
              <div className="stat-card">
                <span className="stat-number">{appointments.length}</span>
                <span className="stat-label">Total Appointments</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">
                  {appointments.filter(a => a.status === 'pending').length}
                </span>
                <span className="stat-label">Pending</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">
                  {appointments.filter(a => a.status === 'approved').length}
                </span>
                <span className="stat-label">Approved</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">
                  {appointments.filter(a => a.status === 'completed').length}
                </span>
                <span className="stat-label">Completed</span>
              </div>
            </div>

            {appointments.length === 0 ? (
              <div className="empty-state">
                <p>No appointments found.</p>
              </div>
            ) : (
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Patient</th>
                      <th>Doctor</th>
                      <th>Disease</th>
                      <th>Date</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {appointments.map(appointment => (
                      <tr key={appointment.id}>
                        <td>{appointment.patient_username}</td>
                        <td>{appointment.doctor_username || 'Not assigned'}</td>
                        <td>{appointment.disease || 'N/A'}</td>
                        <td>{formatDate(appointment.appointment_date)}</td>
                        <td>
                          <span className={`status-badge ${getAppointmentStatusBadge(appointment.status)}`}>
                            {appointment.status.charAt(0).toUpperCase() + appointment.status.slice(1)}
                          </span>
                        </td>
                        <td className="actions-cell">
                          {appointment.status === 'pending' && (
                            <>
                              <button 
                                className="btn-success btn-sm"
                                onClick={() => handleApproveAppointment(appointment.id)}
                              >
                                ✓ Approve
                              </button>
                              <button 
                                className="btn-danger btn-sm"
                                onClick={() => handleRejectAppointment(appointment.id)}
                              >
                                ✗ Reject
                              </button>
                            </>
                          )}
                          {appointment.status === 'approved' && (
                            <button 
                              className="btn-warning btn-sm"
                              onClick={() => handleCompleteAppointment(appointment.id)}
                            >
                              ✓ Complete
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'calendar' && (
          <Calendar user={user} role="doctor" />
        )}

        {activeTab === 'records' && (
          <MedicalRecords user={user} role="doctor" />
        )}
      </main>
    </div>
  )
}
