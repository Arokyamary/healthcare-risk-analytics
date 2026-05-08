import React, { useState } from 'react';
import LoginPage from './LoginPage';
import PatientList from './PatientList';

type Page = 'login' | 'patients' | 'detail';

export default function App() {
  const [page, setPage] = useState<Page>(
    localStorage.getItem('token') ? 'patients' : 'login'
  );
  const [selectedPatientId, setSelectedPatientId] = useState<string>('');

  const handleLogin = () => setPage('patients');

  const handleLogout = () => {
    localStorage.removeItem('token');
    setPage('login');
  };

  const handleSelectPatient = (id: string) => {
    setSelectedPatientId(id);
    setPage('detail');
  };

  if (page === 'login') {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f0f4f8' }}>
      <nav style={{
        background: '#1a365d', color: 'white', padding: '12px 24px',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center'
      }}>
        <h1 style={{ margin: 0, fontSize: '20px' }}>
          Healthcare Analytics
        </h1>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <button
            onClick={() => setPage('patients')}
            style={{
              background: page === 'patients' ? '#2b6cb0' : 'transparent',
              color: 'white', border: '1px solid #4a90d9',
              padding: '6px 16px', borderRadius: '4px', cursor: 'pointer'
            }}
          >
            Patients
          </button>
          <button
            onClick={handleLogout}
            style={{
              background: 'transparent', color: 'white',
              border: '1px solid #666', padding: '6px 16px',
              borderRadius: '4px', cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      </nav>

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
        {page === 'patients' && (
          <PatientList onSelect={handleSelectPatient} />
        )}
        {page === 'detail' && (
          <PatientDetail
            patientId={selectedPatientId}
            onBack={() => setPage('patients')}
          />
        )}
      </div>
    </div>
  );
}

function PatientDetail({ patientId, onBack }: { patientId: string, onBack: () => void }) {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { riskAPI } = require('./api');

  const handlePredict = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await riskAPI.predict(patientId);
      setResult(data);
    } catch (e) {
      setError('Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const tierColors: Record<string, string> = {
    LOW: '#27AE60', MEDIUM: '#F39C12',
    HIGH: '#E67E22', CRITICAL: '#E74C3C'
  };

  return (
    <div style={{ background: 'white', borderRadius: '12px', padding: '24px' }}>
      <button onClick={onBack} style={{
        background: 'none', border: 'none', color: '#2b6cb0',
        cursor: 'pointer', fontSize: '16px', marginBottom: '16px'
      }}>
        ← Back to Patients
      </button>
      <h2 style={{ color: '#1a365d' }}>Risk Prediction</h2>
      <p style={{ color: '#666' }}>Patient ID: {patientId}</p>
      <button
        onClick={handlePredict}
        disabled={loading}
        style={{
          background: '#2b6cb0', color: 'white', border: 'none',
          padding: '12px 24px', borderRadius: '6px',
          fontSize: '16px', cursor: 'pointer', marginBottom: '24px'
        }}
      >
        {loading ? 'Predicting...' : 'Run Risk Prediction'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {result && (
        <div style={{
          border: `2px solid ${tierColors[result.risk_tier] || '#999'}`,
          borderRadius: '8px', padding: '24px',
          background: '#f7fafc'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div>
              <p style={{ color: '#666', margin: 0 }}>Risk Score</p>
              <h1 style={{
                color: tierColors[result.risk_tier],
                margin: '4px 0', fontSize: '48px'
              }}>
                {Math.round(result.risk_score * 100)}%
              </h1>
            </div>
            <div style={{
              background: tierColors[result.risk_tier],
              color: 'white', padding: '8px 20px',
              borderRadius: '8px', alignSelf: 'center',
              fontWeight: 'bold', fontSize: '18px'
            }}>
              {result.risk_tier}
            </div>
          </div>
          <div style={{ marginTop: '16px', display: 'flex', gap: '24px' }}>
            <div>
              <p style={{ color: '#666', margin: 0 }}>30-day Readmission</p>
              <p style={{ fontWeight: 'bold', margin: '4px 0' }}>
                {Math.round(result.readmission_30d * 100)}%
              </p>
            </div>
            <div>
              <p style={{ color: '#666', margin: 0 }}>90-day Readmission</p>
              <p style={{ fontWeight: 'bold', margin: '4px 0' }}>
                {Math.round(result.readmission_90d * 100)}%
              </p>
            </div>
            <div>
              <p style={{ color: '#666', margin: 0 }}>Mortality Risk</p>
              <p style={{ fontWeight: 'bold', margin: '4px 0' }}>
                {Math.round(result.mortality_risk * 100)}%
              </p>
            </div>
          </div>
          <p style={{ color: '#666', marginTop: '16px', fontSize: '12px' }}>
            Model: {result.model_version}
          </p>
        </div>
      )}
    </div>
  );
}