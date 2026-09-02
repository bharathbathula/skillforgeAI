import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { resumeService, jobDescService } from '../services/api';
import { FileText, Briefcase, ArrowLeft, Trash2, Calendar } from 'lucide-react';

export const ResumeDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchResume = async () => {
      try {
        const data = await resumeService.getResume(id);
        setResume(data);
      } catch (err) {
        setError(err.message || 'Failed to load resume details');
      } finally {
        setLoading(false);
      }
    };
    fetchResume();
  }, [id]);

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this resume and its job description?')) return;
    try {
      await resumeService.deleteResume(id);
      navigate('/dashboard');
    } catch (err) {
      alert(err.message || 'Failed to delete resume');
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ textAlign: 'center', padding: '60px 0' }}>
        <p style={{ color: '#64748b' }}>Loading resume details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container" style={{ maxWidth: '600px' }}>
        <div className="alert alert-error">{error}</div>
        <Link to="/dashboard" className="btn btn-outline">← Back to Dashboard</Link>
      </div>
    );
  }

  const jobDesc = resume?.job_descriptions?.[0] || null;

  return (
    <div className="container" style={{ maxWidth: '800px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <Link to="/dashboard" className="btn btn-outline" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          <ArrowLeft size={16} /> Back to Dashboard
        </Link>
        <button onClick={handleDelete} className="btn btn-danger" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          <Trash2 size={16} /> Delete
        </button>
      </div>

      {/* Resume Card */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '16px' }}>
          <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: '#eff6ff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <FileText size={24} color="#2563eb" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#0f172a' }}>{resume.filename}</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: '#64748b' }}>
              <Calendar size={14} />
              Uploaded: {resume.upload_date || resume.uploaded_at ? new Date(resume.upload_date || resume.uploaded_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : 'Recent'}
            </div>
          </div>
        </div>
        <div style={{ padding: '12px 16px', background: '#f8fafc', borderRadius: '8px', fontSize: '0.88rem', color: '#475569' }}>
          <strong>Stored at:</strong> <code style={{ background: '#e2e8f0', padding: '2px 6px', borderRadius: '4px', fontSize: '0.82rem' }}>{resume.file_path || resume.filepath}</code>
        </div>
      </div>

      {/* Job Description Card */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <div style={{ width: '44px', height: '44px', borderRadius: '10px', background: '#f0fdf4', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Briefcase size={24} color="#16a34a" />
          </div>
          <h3 style={{ fontSize: '1.15rem', fontWeight: '600', color: '#0f172a' }}>
            Attached Job Description
          </h3>
        </div>

        {jobDesc ? (
          <div>
            <div style={{ marginBottom: '12px' }}>
              <span className="badge badge-blue" style={{ marginBottom: '8px' }}>{jobDesc.title}</span>
              <div style={{ fontSize: '0.82rem', color: '#94a3b8', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Calendar size={12} />
                Added: {new Date(jobDesc.created_at).toLocaleDateString()}
              </div>
            </div>
            <div style={{
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '16px',
              fontSize: '0.9rem',
              lineHeight: '1.7',
              color: '#334155',
              whiteSpace: 'pre-wrap',
              maxHeight: '400px',
              overflowY: 'auto'
            }}>
              {jobDesc.description}
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '24px 0', color: '#94a3b8', fontSize: '0.9rem' }}>
            No job description attached to this resume.
            <br />
            <Link to="/upload" style={{ marginTop: '8px', display: 'inline-block' }}>Upload another resume with a job description →</Link>
          </div>
        )}
      </div>
    </div>
  );
};
