import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api'

export default function Calendar({ user, role }) {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [appointments, setAppointments] = useState({})
  const [selectedDate, setSelectedDate] = useState(null)
  const [dayAppointments, setDayAppointments] = useState([])

  const token = localStorage.getItem('token')
  const config = { headers: { Authorization: `Token ${token}` } }

  useEffect(() => {
    fetchAppointments()
  }, [currentDate])

  const fetchAppointments = async () => {
    try {
      const startOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1)
      const endOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0)
      
      const startDate = startOfMonth.toISOString().split('T')[0]
      const endDate = endOfMonth.toISOString().split('T')[0]

      const res = await axios.get(
        `${API_URL}/appointments/calendar/?start_date=${startDate}&end_date=${endDate}`,
        config
      )
      setAppointments(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const getDaysInMonth = () => {
    const year = currentDate.getFullYear()
    const month = currentDate.getMonth()
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const daysInMonth = lastDay.getDate()
    const startingDay = firstDay.getDay()

    const days = []
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDay; i++) {
      days.push(null)
    }
    
    // Add days of the month
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(i)
    }
    
    return days
  }

  const getAppointmentsForDay = (day) => {
    if (!day) return []
    const dateStr = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    return Object.entries(appointments)
      .filter(([_, appt]) => appt.appointment_date === dateStr)
      .map(([id, appt]) => ({ id, ...appt }))
  }

  const handlePrevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1))
  }

  const handleNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1))
  }

  const handleDayClick = (day) => {
    if (!day) return
    setSelectedDate(day)
    setDayAppointments(getAppointmentsForDay(day))
  }

  const handleUpdateStatus = async (appointmentId, newStatus) => {
    try {
      await axios.put(`${API_URL}/appointments/${appointmentId}/`, { status: newStatus }, config)
      fetchAppointments()
      if (selectedDate) {
        setDayAppointments(getAppointmentsForDay(selectedDate))
      }
    } catch (err) {
      alert(err.response?.data?.error || err.message)
    }
  }

  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

  const days = getDaysInMonth()

  return (
    <div className="calendar-container">
      <div className="calendar-header">
        <button className="calendar-nav-btn" onClick={handlePrevMonth}>◀</button>
        <h3>{monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}</h3>
        <button className="calendar-nav-btn" onClick={handleNextMonth}>▶</button>
      </div>

      <div className="calendar-grid">
        {dayNames.map(day => (
          <div key={day} className="calendar-day-header">{day}</div>
        ))}
        
        {days.map((day, index) => {
          const dayAppts = getAppointmentsForDay(day)
          const hasAppointments = dayAppts.length > 0
          
          return (
            <div 
              key={index} 
              className={`calendar-day ${day ? 'valid-day' : 'empty-day'} ${hasAppointments ? 'has-appointments' : ''} ${selectedDate === day ? 'selected-day' : ''}`}
              onClick={() => handleDayClick(day)}
            >
              {day && (
                <>
                  <span className="day-number">{day}</span>
                  {hasAppointments && (
                    <span className="appointment-count">{dayAppts.length}</span>
                  )}
                </>
              )}
            </div>
          )
        })}
      </div>

      {selectedDate && (
        <div className="day-details">
          <h4>
            Appointments for {monthNames[currentDate.getMonth()]} {selectedDate}, {currentDate.getFullYear()}
          </h4>
          {dayAppointments.length === 0 ? (
            <p className="empty-message">No appointments on this day</p>
          ) : (
            <div className="appointment-list">
              {dayAppointments.map(appt => (
                <div key={appt.id} className="appointment-item">
                  <div className="appointment-info">
                    <p><strong>Patient:</strong> {appt.patient_username}</p>
                    <p><strong>Disease:</strong> {appt.disease}</p>
                    <p><strong>Status:</strong> 
                      <span className={`status-badge status-${appt.status}`}>
                        {appt.status}
                      </span>
                    </p>
                  </div>
                  {role === 'doctor' && (
                    <div className="appointment-actions">
                      {appt.status === 'pending' && (
                        <button 
                          className="btn-success btn-sm"
                          onClick={() => handleUpdateStatus(appt.id, 'approved')}
                        >
                          Approve
                        </button>
                      )}
                      {appt.status === 'pending' && (
                        <button 
                          className="btn-danger btn-sm"
                          onClick={() => handleUpdateStatus(appt.id, 'rejected')}
                        >
                          Reject
                        </button>
                      )}
                      {appt.status === 'approved' && (
                        <button 
                          className="btn-warning btn-sm"
                          onClick={() => handleUpdateStatus(appt.id, 'completed')}
                        >
                          Complete
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
