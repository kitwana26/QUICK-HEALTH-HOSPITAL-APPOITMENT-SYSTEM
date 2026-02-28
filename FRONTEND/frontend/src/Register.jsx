import React, { useState } from 'react'
import axios from 'axios'

export default function Register(){
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [role, setRole] = useState('patient')

  const submit = async e => {
    e.preventDefault()
    try{
      const res = await axios.post('http://localhost:8000/api/register/', { username, password, email, role })
      alert('Registered — token: ' + res.data.token)
    }catch(err){
      alert(err.response?.data?.error || err.message)
    }
  }

  return (
    <form onSubmit={submit} style={{maxWidth:400}}>
      <input placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} required style={{width:'100%',padding:8,margin:'8px 0'}} />
      <input placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} required style={{width:'100%',padding:8,margin:'8px 0'}} />
      <input placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} style={{width:'100%',padding:8,margin:'8px 0'}} />
      <select value={role} onChange={e=>setRole(e.target.value)} style={{width:'100%',padding:8,margin:'8px 0'}}>
        <option value="patient">Patient</option>
        <option value="doctor">Doctor</option>
      </select>
      <button type="submit" style={{padding:10}}>Register</button>
    </form>
  )
}
