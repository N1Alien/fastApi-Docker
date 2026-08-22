// Plik: src/components/SidebarFiles.jsx
import React, { useState } from 'react';
import { API_BASE_URL } from '../config';
import { Upload, FileText, CheckCircle2, AlertTriangle, Cpu, HelpCircle } from 'lucide-react';

export default function SidebarFiles() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('IDLE');
  const [errorMsg, setErrorMsg] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setStatus('IDLE');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setStatus('UPLOADING');
    setErrorMsg('');

    const token = localStorage.getItem('token');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/upload-pdf`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'ICEWALL BLOCK: Data transmission failed.');
      }

      setStatus('SUCCESS');
      setUploadedFiles(prev => [...prev, { name: file.name, chunks: data.indexed_chunks }]);
      setFile(null);
    } catch (err) {
      setStatus('ERROR');
      setErrorMsg(err.message);
    }
  };

  return (
    <div style={{
      width: '340px',
      backgroundColor: '#0e0e13',
      borderRight: '2px solid #ff0055',
      padding: '24px',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      fontFamily: 'monospace',
      color: '#cbd5e1',
      boxSizing: 'border-box'
    }}>
      {/* SECTION HEADER */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid #ff0055', paddingBottom: '12px', marginBottom: '24px' }}>
        <Cpu style={{ color: '#ff0055' }} />
        <h3 style={{ fontSize: '14px', fontWeight: '900', tracking: '0.1em', color: '#00f0ff', margin: 0, textTransform: 'uppercase' }}>NETRUN DATA INGESTION</h3>
      </div>

      {/* DRAG & DROP / FILE CHOOSE BOX */}
      <div style={{
        border: '2px dashed #00f0ff',
        backgroundColor: '#14141c',
        padding: '24px',
        textAlign: 'center',
        position: 'relative',
        marginBottom: '20px',
        cursor: 'pointer'
      }}>
        <input type="file" accept=".pdf" onChange={handleFileChange} style={{ position: 'absolute', inset: 0, opacity: 0, cursor: 'pointer', width: '100%', height: '100%' }} />
        <Upload style={{ color: '#00f0ff', width: '36px', height: '36px', margin: '0 auto 12px auto' }} />
        <p style={{ fontSize: '11px', fontWeight: 'bold', color: '#94a3b8', margin: 0, uppercase: 'true' }}>CHOOSE_DATASHARD.PDF</p>
        {file && <p style={{ fontSize: '12px', color: '#ffee00', marginTop: '12px', fontWeight: 'bold', wordBreak: 'break-all', padding: '0 4px' }}>{file.name}</p>}
      </div>

      {/* HIGHLY INTERACTIVE EXECUTE BUTTON */}
      {file && status !== 'UPLOADING' && (
        <button 
          onClick={handleUpload} 
          style={{
            width: '100%',
            height: '56px',
            backgroundColor: '#ffee00',
            color: '#000000',
            fontWeight: '900',
            fontSize: '13px',
            fontFamily: 'monospace',
            textTransform: 'uppercase',
            letterSpacing: '2px',
            border: 'none',
            boxShadow: '0 0 15px rgba(255,238,0,0.4)',
            cursor: 'pointer',
            transition: 'all 100ms',
            marginBottom: '20px'
          }}
          onMouseOver={(e) => e.target.style.backgroundColor = '#ddcc00'}
          onMouseOut={(e) => e.target.style.backgroundColor = '#ffee00'}
        >
          EXECUTE INJECTION ⚡
        </button>
      )}

      {/* STATUS INDICATORS */}
      {status === 'UPLOADING' && (
        <div style={{ backgroundColor: '#1a1300', border: '1px solid #ffee00', padding: '12px', fontSize: '12px', color: '#ffee00', fontWeight: 'bold', marginBottom: '20px' }}>
          ⚡ PACKET TRANSMISSION IN PROGRESS... ENCODING VECTORS
        </div>
      )}

      {status === 'SUCCESS' && (
        <div style={{ backgroundColor: '#001a1a', border: '1px solid #00f0ff', padding: '12px', fontSize: '12px', color: '#00f0ff', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px', boxShadow: '0 0 10px rgba(0,240,255,0.15)' }}>
          <CheckCircle2 style={{ width: '16px', height: '16px', flexShrink: 0 }} />
          <span>SHARD VECTORIZED SUCCESSFULLY.</span>
        </div>
      )}

      {status === 'ERROR' && (
        <div style={{ backgroundColor: '#1a000a', border: '1px solid #ff0055', padding: '12px', fontSize: '12px', color: '#ff0055', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
          <AlertTriangle style={{ width: '16px', height: '16px', flexShrink: 0 }} />
          <span style={{ wordBreak: 'break-all' }}>{errorMsg}</span>
        </div>
      )}

      {/* PERSISTENT MEMORY BANK SHARDS */}
      <div style={{ flex: 1, overflowY: 'auto', marginBottom: '20px' }}>
        <p style={{ fontSize: '10px', color: '#ff0055', fontWeight: '900', letterSpacing: '2px', textTransform: 'uppercase', marginBottom: '12px' }}>PARTITION_INDEX:</p>
        {uploadedFiles.length === 0 ? (
          <p style={{ fontSize: '12px', color: '#475569', fontStyle: 'italic', margin: 0 }}>No dynamic shards active in this sector.</p>
        ) : (
          uploadedFiles.map((f, i) => (
            <div key={i} style={{ backgroundColor: '#14141c', border: '1px solid #1e293b', padding: '10px', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <FileText style={{ color: '#00f0ff', flexShrink: 0 }} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{ fontSize: '12px', fontWeight: 'bold', color: '#e2e8f0', margin: 0, textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>{f.name}</p>
                <p style={{ fontSize: '10px', color: '#ffee00', fontWeight: 'bold', margin: '2px 0 0 0' }}>CHUNKS: {f.chunks}</p>
              </div>
            </div>
          ))
        )}
      </div>

      {/* CYBERPUNK FIRST-TIME USER INSTRUCTIONS */}
      <div style={{
        borderTop: '2px solid #00f0ff',
        paddingTop: '16px',
        backgroundColor: '#0a0a0f',
        padding: '12px',
        border: '1px solid #1e293b'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#ffee00', fontSize: '11px', fontWeight: '900', marginBottom: '8px' }}>
          <HelpCircle style={{ width: '14px', height: '14px' }} />
          <span>RUN_MANUAL // FIRST_TIME_NETRUNNER</span>
        </div>
        <ol style={{ fontSize: '11px', color: '#94a3b8', lineHeight: '1.6', margin: 0, paddingLeft: '16px', fontWeight: 'bold' }}>
          <li style={{ marginBottom: '6px' }}><span style={{ color: '#00f0ff' }}>STEP_01:</span> Drop a raw corporate corporate PDF file into the upload sector above.</li>
          <li style={{ marginBottom: '6px' }}><span style={{ color: '#00f0ff' }}>STEP_02:</span> Click "EXECUTE INJECTION" to push vectorized matrices into pgvector storage.</li>
          <li style={{ marginBottom: '6px' }}><span style={{ color: '#00f0ff' }}>STEP_03:</span> Move to the mainframe console. Enter data queries to execute semantic RAG analysis.</li>
          <li><span style={{ color: '#ffee00' }}>TIP:</span> Use keyword "internet" or "today" to deploy real-time search sub-routines.</li>
        </ol>
      </div>

    </div>
  );
}
