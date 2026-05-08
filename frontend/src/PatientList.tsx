import React, { useState, useEffect } from 'react';
import { patientAPI } from './api';

interface Patient {
  id: string;
  mrn: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  insurance_type: string;
}

export default function PatientList({ onSelect }: { onSelect: (id: string) => void }) {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchPatients = async (q = '') => {
    setLoading(true);
    try {
      const data = await patientAPI.list(q || undefined);
      setPatients(data.patients);
      setTotal(data.total);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPatients(); }, []);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
    fetchPatients(e.target.value);
  };

  return (
    <div style={{ padding: '24px' }}>
      <h2 style={{ color: '#1a365d', marginBottom: '16px' }}>
        Patients ({total.toLocaleString()})
      </h2>
      <input
        placeholder="Search by name or MRN..."
        value={search}
        onChange={handleSearch}
        style={{
          width: '100%', padding: '10px', marginBottom: '16px',
          border: '1px solid #ddd', borderRadius: '6px',
          fontSize: '14px', boxSizing: 'border-box'
        }}
      />
      {loading ? (
        <p>Loading...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#2b6cb0', color: 'white' }}>
              <th style={{ padding: '10px', textAlign: 'left' }}>MRN</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Name</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>DOB</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Gender</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Insurance</th>
              <th style={{ padding: '10px', textAlign: 'left' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {patients.map((p, i) => (
              <tr key={p.id}
                style={{ background: i % 2 === 0 ? '#f7fafc' : 'white' }}>
                <td style={{ padding: '10px' }}>{p.mrn}</td>
                <td style={{ padding: '10px' }}>{p.first_name} {p.last_name}</td>
                <td style={{ padding: '10px' }}>{p.date_of_birth}</td>
                <td style={{ padding: '10px' }}>{p.gender}</td>
                <td style={{ padding: '10px' }}>{p.insurance_type}</td>
                <td style={{ padding: '10px' }}>
                  <button
                    onClick={() => onSelect(p.id)}
                    style={{
                      background: '#2b6cb0', color: 'white',
                      border: 'none', padding: '6px 12px',
                      borderRadius: '4px', cursor: 'pointer'
                    }}
                  >
                    View Risk
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}