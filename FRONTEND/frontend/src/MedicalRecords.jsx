import React, { useState, useEffect } from 'react'
import api from './api'

export default function MedicalRecords({ user, role }) {
  const [records, setRecords] = useState({})
  const [patients, setPatients] = useState({})
  const [showForm, setShowForm] = useState(false)
  const [selectedPatient, setSelectedPatient] = useState('')
  const [newRecord, setNewRecord] = useState({
    diagnosis: '',
    treatment: '',
    medications: '',
    notes: ''
  })
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchRecords()
    if (role === 'doctor') {
      fetchPatients()
    }
  }, [])

  const fetchRecords = async () => {
    try {
      const res = await api.get('/medical-records/')
      setRecords(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const fetchPatients = async () => {
    try {
      const res = await api.get('/doctor/patients/')
      setPatients(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const handleCreateRecord = async (e) => {
    e.preventDefault()
    try {
      await api.post('/medical-records/', {
        patient_username: selectedPatient,
        ...newRecord
      })
      setMessage('Medical record created successfully!')
      setShowForm(false)
      setNewRecord({ diagnosis: '', treatment: '', medications: '', notes: '' })
      setSelectedPatient('')
      fetchRecords()
      setTimeout(() => setMessage(''), 3000)
    } catch (err) {
      alert(err.response?.data?.error || err.message)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  const getPatientName = (patientUsername) => {
    const patient = patients[patientUsername]
    if (patient) {
      return patient.full_name || patientUsername
    }
    return patientUsername
  }

  const recordList = Object.entries(records)

  return (
    <div className="records-container">
      <div className="records-header">
        <h3>📋 Medical Records</h3>
        {role === 'doctor' && (
          <button 
            className="btn-primary" 
            style={{ width: 'auto', marginTop: 0 }}
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? 'Cancel' : '+ Add Record'}
          </button>
        )}
      </div>

      {message && <div className="success-message">{message}</div>}

      {showForm && role === 'doctor' && (
        <form onSubmit={handleCreateRecord} className="record-form">
          <h4>Create New Medical Record</h4>
          
          <div className="form-group-full">
            <label>Select Patient</label>
            <select 
              value={selectedPatient} 
              onChange={e => setSelectedPatient(e.target.value)}
              className="form-select"
              required
            >
              <option value="">Select a Patient</option>
              {Object.entries(patients).map(([username, patient]) => (
                <option key={username} value={username}>
                  {patient.full_name || username}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group-full">
            <label>Diagnosis</label>
            <textarea 
              value={newRecord.diagnosis}
              onChange={e => setNewRecord({...newRecord, diagnosis: e.target.value})}
              rows="3"
              placeholder="Enter diagnosis"
              required
            />
          </div>

          <div className="form-group-full">
            <label>Treatment</label>
            <textarea 
              value={newRecord.treatment}
              onChange={e => setNewRecord({...newRecord, treatment: e.target.value})}
              rows="3"
              placeholder="Enter treatment plan"
              required
            />
          </div>

          <div className="form-group-full">
            <label>Medications</label>
            <textarea 
              value={newRecord.medications}
              onChange={e => setNewRecord({...newRecord, medications: e.target.value})}
              rows="2"
              placeholder="Enter medications"
            />
          </div>

          <div className="form-group-full">
            <label>Additional Notes</label>
            <textarea 
              value={newRecord.notes}
              onChange={e => setNewRecord({...newRecord, notes: e.target.value})}
              rows="2"
              placeholder="Enter any additional notes"
            />
          </div>

          <button type="submit" className="btn-primary" style={{ width: 'auto', marginTop: '10px' }}>
            Save Record
          </button>
        </form>
      )}

      {recordList.length === 0 ? (
        <div className="no-records">
          <p>No medical records found.</p>
        </div>
      ) : (
        <div className="records-list">
          {recordList.map(([recordId, record]) => (
            <div key={recordId} className="record-card">
              <h4>
                {role === 'doctor' ? `Patient: ${getPatientName(record.patient_username)}` : 'Medical Record'}
              </h4>
              <div className="record-details">
                <p><strong>Diagnosis:</strong> {record.diagnosis || 'N/A'}</p>
                <p><strong>Treatment:</strong> {record.treatment || 'N/A'}</p>
                <p><strong>Medications:</strong> {record.medications || 'N/A'}</p>
                {record.notes && <p><strong>Notes:</strong> {record.notes}</p>}
              </div>
              <div className="record-meta">
                <p>Created: {formatDate(record.created_at)}</p>
                {record.updated_at && <p>Updated: {formatDate(record.updated_at)}</p>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
