import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { resumeService, jobDescService } from '../services/api';
import { UploadCloud, FileText, AlignLeft, CheckCircle, Sparkles } from 'lucide-react';

export const UploadPage = () => {
  const [resumeFile, setResumeFile] = useState(null);
  const [jdTitle, setJdTitle] = useState('');
  const [jdText, setJdText] = useState('');
  const [uploadMode, setUploadMode] = useState('text'); // 'text' | 'file'

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const ext = file.name.split('.').pop().toLowerCase();
      if (!['pdf', 'docx', 'doc'].includes(ext)) {
        setError('Resume must be a PDF or DOCX file (.pdf, .docx)');
        return;
      }
      setResumeFile(file);
      setError('');
    }
  };

  const handleJdFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setJdText(event.target.result);
      };
      reader.readAsText(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (!resumeFile) {
      setError('Please select a PDF or DOCX resume file');
      return;
    }

    if (!jdTitle.trim()) {
      setError('Please enter a job description title');
      return;
    }

    if (!jdText.trim()) {
      setError('Please provide the target job description text');
      return;
    }

    setLoading(true);

    try {
      // 1. Upload Resume File
      const formData = new FormData();
      formData.append('file', resumeFile);
      const uploadedResume = await resumeService.upload(formData);

      // 2. Create attached Job Description
      await jobDescService.create({
        resume_id: uploadedResume.id,
        title: jdTitle,
        description: jdText
      });

      setSuccess(true);
      
      // 3. Navigate to Analysis Pipeline loading screen
      setTimeout(() => {
        navigate(`/analysis-loading/${uploadedResume.id}`);
      }, 800);

    } catch (err) {
      setError(err.message || 'Failed to upload resume and job description');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{ maxWidth: '720px' }}>
      <div className="card">
        <div style={{ marginBottom: '24px' }}>
          <h2 style={{ fontSize: '1.4rem', fontWeight: '700', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <UploadCloud color="#2563eb" size={24} /> Upload Resume & Target Job Description
          </h2>
          <p style={{ color: '#64748b', fontSize: '0.9rem', marginTop: '4px' }}>
            SkillForge AI will parse your resume, analyze the target job description, generate embeddings, and produce a full ATS Score & detailed report.
          </p>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {success && (
          <div className="alert alert-success" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle size={18} /> Uploaded successfully! Redirecting to AI Analysis Pipeline...
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Section 1: Resume Upload */}
          <div style={{ marginBottom: '24px', paddingBottom: '20px', borderBottom: '1px solid #e2e8f0' }}>
            <label className="form-label" style={{ fontSize: '1rem', fontWeight: '600', color: '#1e293b' }}>
              1. Select Resume (PDF or DOCX) *
            </label>
            <div style={{
              border: '2px dashed #cbd5e1',
              borderRadius: '8px',
              padding: '24px',
              textAlign: 'center',
              background: '#f8fafc',
              marginTop: '8px',
              cursor: 'pointer'
            }} onClick={() => document.getElementById('resume-file-input').click()}>
              <FileText color="#2563eb" size={32} style={{ marginBottom: '8px' }} />
              <p style={{ fontWeight: '500', color: '#334155' }}>
                {resumeFile ? resumeFile.name : 'Click to browse PDF or DOCX resume file'}
              </p>
              <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>PDF and DOCX files supported</span>
              <input
                id="resume-file-input"
                type="file"
                accept=".pdf,.docx,.doc"
                style={{ display: 'none' }}
                onChange={handleFileChange}
              />
            </div>
          </div>

          {/* Section 2: Job Description */}
          <div style={{ marginBottom: '24px' }}>
            <label className="form-label" style={{ fontSize: '1rem', fontWeight: '600', color: '#1e293b', marginBottom: '12px', display: 'block' }}>
              2. Target Job Description *
            </label>

            <div className="form-group">
              <label className="form-label">Job Title / Role Name *</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Software Engineer / Python Backend Developer"
                value={jdTitle}
                onChange={(e) => setJdTitle(e.target.value)}
                required
              />
            </div>

            {/* Mode selector */}
            <div style={{ display: 'flex', gap: '16px', marginBottom: '12px' }}>
              <button
                type="button"
                className={`btn ${uploadMode === 'text' ? 'btn-primary' : 'btn-outline'}`}
                style={{ padding: '6px 14px', fontSize: '0.85rem' }}
                onClick={() => setUploadMode('text')}
              >
                Paste Text
              </button>
              <button
                type="button"
                className={`btn ${uploadMode === 'file' ? 'btn-primary' : 'btn-outline'}`}
                style={{ padding: '6px 14px', fontSize: '0.85rem' }}
                onClick={() => setUploadMode('file')}
              >
                Upload File (.txt / .text)
              </button>
            </div>

            {uploadMode === 'text' ? (
              <div className="form-group">
                <label className="form-label">Job Description Text *</label>
                <textarea
                  className="form-textarea"
                  placeholder="Paste requirements, responsibilities, required skills, and qualifications here..."
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  rows={6}
                  required
                ></textarea>
              </div>
            ) : (
              <div className="form-group">
                <label className="form-label">Job Description File (.txt / text file)</label>
                <input
                  type="file"
                  accept=".txt,.md,.text"
                  className="form-input"
                  onChange={handleJdFileChange}
                />
                {jdText && (
                  <div style={{ marginTop: '8px', fontSize: '0.85rem', color: '#475569', background: '#f1f5f9', padding: '8px', borderRadius: '6px', maxHeight: '100px', overflowY: 'auto' }}>
                    Preview: {jdText.substring(0, 150)}...
                  </div>
                )}
              </div>
            )}
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '12px', fontSize: '1rem' }} disabled={loading}>
            {loading ? 'Uploading & Preparing...' : 'Analyze Resume & Generate ATS Score'}
          </button>
        </form>
      </div>
    </div>
  );
};
