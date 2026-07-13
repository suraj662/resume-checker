import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  'https://xetdalbqalshjicasfuu.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhldGRhbGJxYWxzaGppY2FzZnV1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI5Nzk2NTIsImV4cCI6MjA5ODU1NTY1Mn0.zSeWk6e0k7Gud-mqSy44dc2NR4RfFoMQjV2gSBvGM6E'
);

function App() {
  const [file, setFile] = useState(null);
  const [jobDesc, setJobDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  
  // 🔥 NEW: User State
  const [user, setUser] = useState(null);

  // 🔥 NEW: Check if user is logged in on page load
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const onDrop = (acceptedFiles) => {
    setFile(acceptedFiles[0]);
    setError('');
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] },
    maxFiles: 1
  });

  // 🔥 NEW: Google Login Handler
  const handleGoogleLogin = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin }
    });
    if (error) alert('Google Login error: ' + error.message);
  };

  // 🔥 NEW: Logout Handler
  const handleLogout = async () => {
    await supabase.auth.signOut();
  };

  const handleAnalyze = async () => {
    if (!file || !jobDesc.trim()) {
      setError('Please upload a resume and enter a job description.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      // 🔥 1. Get the CURRENT session token from Supabase
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token;

      if (!token) {
        setError('You must be signed in to analyze a resume.');
        setLoading(false);
        return;
      }

      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = async () => {
        const base64String = reader.result.split(',')[1];

        // 🔥 2. Send the token in the Authorization header
        const response = await axios.post(
          'http://localhost:8000/api/scan/analyze', 
          {
            file_base64: base64String,
            filename: file.name,
            job_desc: jobDesc
          },
          {
            headers: {
              'Authorization': `Bearer ${token}`  // <-- THIS FIXES THE 403
            }
          }
        );

        if (response.status === 200) {
          setResult(response.data);
        } else {
          setError('Unexpected response from server.');
        }
        setLoading(false);
      };
    } catch (err) {
      console.error("Full error:", err);
      setError('Analysis failed. Please check the backend is running.');
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* 🔥 NEW: Top bar with Title and Login Button */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ margin: 0 }}>📄 AI Resume Checker</h1>
        <div>
          {user ? (
            <button 
              onClick={handleLogout} 
              style={{ 
                padding: '8px 16px', 
                background: '#e74c3c', 
                color: 'white', 
                border: 'none', 
                borderRadius: '8px', 
                cursor: 'pointer', 
                fontWeight: 'bold' 
              }}
            >
              Sign Out ({user.email})
            </button>
          ) : (
            <button 
              onClick={handleGoogleLogin} 
              style={{ 
                padding: '8px 16px', 
                background: '#4285F4', 
                color: 'white', 
                border: 'none', 
                borderRadius: '8px', 
                cursor: 'pointer', 
                fontWeight: 'bold',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <span style={{ fontSize: '1.2rem' }}>G</span> Sign In with Google
            </button>
          )}
        </div>
      </div>

      <p className="subtitle">Upload your resume and get an ATS score instantly</p>

      <div {...getRootProps()} className="upload-zone">
        <input {...getInputProps()} />
        <div style={{ fontSize: '3rem' }}>📁</div>
        {file ? <p><strong>{file.name}</strong></p> : <p>Drag & drop your resume here</p>}
      </div>

      <textarea placeholder="Paste the job description here..." value={jobDesc} onChange={(e) => setJobDesc(e.target.value)} />
      
      {error && <div style={{ color: '#e74c3c', margin: '10px 0' }}>{error}</div>}
      
      <button className="analyze-btn" onClick={handleAnalyze} disabled={loading}>
        {loading ? 'Analyzing...' : '🚀 Analyze Resume'}
      </button>

      {result && (
        <div className="results-container">
          <div className="score-box"><div className="score-number">{result.match_score}%</div><p>ATS Match Score</p></div>
          <div className="keywords-grid">
            <div className="keyword-box"><h3 className="missing">⚠️ Missing</h3><ul>{result.missing_keywords.map((k,i) => <li key={i}>{k}</li>)}</ul></div>
            <div className="keyword-box"><h3 className="matched">✅ Strong</h3><ul>{result.strong_matches.map((k,i) => <li key={i}>{k}</li>)}</ul></div>
          </div>
          <div className="issues-box"><h3>📝 Formatting</h3><ul>{result.formatting_issues.map((k,i) => <li key={i}>{k}</li>)}</ul></div>
          <div className="suggestions-box"><h3>💡 Suggestions</h3><p>{result.suggestions}</p></div>
        </div>
      )}
    </div>
  );
}

export default App;