import { useState } from 'react';
import CheckIn from './CheckIn';
import StaffDashboard from './StaffDashboard';

function App() {
  
  const [view, setView] = useState<'student' | 'staff'>('student');

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f4f6f8', paddingBottom: '50px' }}>
      <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', padding: '20px', backgroundColor: '#fff', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: '30px' }}>
        <button 
          onClick={() => setView('student')} 
          style={{ padding: '10px 20px', fontSize: '16px', cursor: 'pointer', border: view === 'student' ? '2px solid #007bff' : '1px solid #ccc', borderRadius: '8px', backgroundColor: view === 'student' ? '#e6f2ff' : '#fff' }}
        >
          🎓 Student Check-In
        </button>
        <button 
          onClick={() => setView('staff')} 
          style={{ padding: '10px 20px', fontSize: '16px', cursor: 'pointer', border: view === 'staff' ? '2px solid #28a745' : '1px solid #ccc', borderRadius: '8px', backgroundColor: view === 'staff' ? '#e6ffe6' : '#fff' }}
        >
          👨‍💻 Staff Dashboard
        </button>
      </div>

      {view === 'student' ? <CheckIn /> : <StaffDashboard />}
    </div>
  );
}

export default App;
