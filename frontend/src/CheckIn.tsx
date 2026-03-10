import React, { useState } from 'react';

export default function CheckIn() {
  const [checklist, setChecklist] = useState({
    passport: false,
    i20: false,
    w2: false,
    form1042s: false,
  });
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState('');

  const allChecked = Object.values(checklist).every(Boolean);

  const handleCheckbox = (e: React.ChangeEvent<HTMLInputElement>) => {
    setChecklist({ ...checklist, [e.target.name]: e.target.checked });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!email.endsWith('@macalester.edu')) {
      setStatus('Please use your Macalester email.');
      return;
    }

    setStatus('Joining queue...');

    try {
      const response = await fetch('https://isp-tax-session-checkin.onrender.com', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email }),
      });
      const data = await response.json();
      setStatus(`Success! Status: ${data.message}`);
    } catch (error) {
      setStatus('Error: Backend server is not running yet, but frontend works!');
    }
  };

  return (
    <div style={{ maxWidth: '500px', margin: '0 auto', padding: '20px', fontFamily: 'sans-serif', textAlign: 'left' }}>
      <h2>Tax Review Check-in</h2>
      <p>Please confirm you have the following documents ready:</p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '25px', backgroundColor: '#f9f9f9', padding: '15px', borderRadius: '8px', color: '#333' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <input type="checkbox" name="passport" onChange={handleCheckbox} style={{ width: '18px', height: '18px' }}/> 
          Passport & Visa
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <input type="checkbox" name="i20" onChange={handleCheckbox} style={{ width: '18px', height: '18px' }}/> 
          I-20 Form
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <input type="checkbox" name="w2" onChange={handleCheckbox} style={{ width: '18px', height: '18px' }}/> 
          W-2 Form (if employed)
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <input type="checkbox" name="form1042s" onChange={handleCheckbox} style={{ width: '18px', height: '18px' }}/> 
          1042-S Form (if applicable)
        </label>
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        <input 
          type="email" 
          placeholder="Enter your @macalester.edu email" 
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={!allChecked}
          style={{ padding: '12px', fontSize: '16px', borderRadius: '4px', border: '1px solid #ccc' }}
        />
        <button 
          type="submit" 
          disabled={!allChecked || !email}
          style={{ 
            padding: '12px', 
            fontSize: '16px', 
            backgroundColor: allChecked ? '#005b96' : '#cccccc', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: allChecked ? 'pointer' : 'not-allowed' 
          }}
        >
          Join Queue
        </button>
      </form>
      {status && <p style={{ marginTop: '20px', fontWeight: 'bold', color: '#d9534f' }}>{status}</p>}
    </div>
  );
}