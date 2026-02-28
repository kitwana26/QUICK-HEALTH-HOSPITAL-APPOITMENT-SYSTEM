import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('patient');
  const [phone, setPhone] = useState('');i want 
  const [address, setAddress] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8000/api/register/', { username, password, email, role, phone, address });
      localStorage.setItem('token', response.data.token);
      navigate('/dashboard');
    } catch (error) {
      alert(error.response?.data?.error || 'Registration failed');
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '500px', margin: 'auto', fontFamily: 'Arial, sans-serif' }}>
      <h2 style={{ textAlign: 'center', color: '#333' }}>Register</h2>
      <form onSubmit={handleSubmit} style={{ background: '#f9f9f9', padding: '20px', borderRadius: '8px', boxShadow: '0 0 10px rgba(0,0,0,0.1)' }}>
        <input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} required style={{ display:'block', width:'100%', padding:10, margin:'8px 0' }} />
        <input placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} type="password" required style={{ display:'block', width:'100%', padding:10, margin:'8px 0' }} />
        <input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} style={{ display:'block', width:'100%', padding:10, margin:'8px 0' }} />
        <select value={role} onChange={e => setRole(e.target.value)} style={{ display:'block', width:'100%', padding:10, margin:'8px 0' }}>
          <option value="patient">Patient</option>
          <option value="doctor">Doctor</option>
        </select>
        <input placeholder="Phone" value={phone} onChange={e => setPhone(e.target.value)} style={{ display:'block', width:'100%', padding:10, margin:'8px 0' }} />
        <input placeholder="Address / Diseases" value={address} onChange={e => setAddress(e.target.value)} style={{ display:'block', width:'100%', padding:10, margin:'8px 0' }} />
        <button type="submit" style={{ padding: '10px', width: '100%', background: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Register</button>
      </form>
    </div>
  );
}

export default Register;
