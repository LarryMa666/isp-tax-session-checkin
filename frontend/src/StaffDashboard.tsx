import { useState } from 'react';

export default function StaffDashboard() {
  const [staffId, setStaffId] = useState('');
  const [studentEmail, setStudentEmail] = useState('');
  const [message, setMessage] = useState('');

  // Deal with 1st and 2nd round request
  const handleAction = async (endpoint: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/staff/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          staff_id: parseInt(staffId),
          student_email: studentEmail
        })
      });
      const data = await response.json();
      
      if (response.ok) {
        setMessage(`✅ Success: ${data.message}`);
        setStudentEmail(''); 
      } else {
        setMessage(`❌ Error: ${data.detail}`);
      }
    } catch (error) {
      setMessage('❌ Network Error. Is the backend running?');
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto', padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>👨‍💻 Staff Workspace</h2>
      
      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', fontWeight: 'bold' }}>Your Staff ID:</label>
        <input
          type="number"
          value={staffId}
          onChange={(e) => setStaffId(e.target.value)}
          placeholder="e.g., 1"
          style={{ width: '100%', padding: '8px', marginTop: '5px', borderRadius: '4px', border: '1px solid #ccc' }}
        />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', fontWeight: 'bold' }}>Student Email:</label>
        <input
          type="email"
          value={studentEmail}
          onChange={(e) => setStudentEmail(e.target.value)}
          placeholder="student@macalester.edu"
          style={{ width: '100%', padding: '8px', marginTop: '5px', borderRadius: '4px', border: '1px solid #ccc' }}
        />
      </div>

      <div style={{ display: 'flex', gap: '10px' }}>
        <button
          onClick={() => handleAction('complete_round1')}
          style={{ flex: 1, padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          Complete Round 1
        </button>
        <button
          onClick={() => handleAction('complete_round2')}
          style={{ flex: 1, padding: '10px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          Complete Final
        </button>
      </div>

      {message && (
        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '4px', borderLeft: '4px solid #007bff' }}>
          {message}
        </div>
      )}
    </div>
  );
}