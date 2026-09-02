import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { dashboardService, resumeService } from '../services/api';
import { Upload, FileText, Briefcase, Clock, Trash2, Eye, User as UserIcon, Sparkles, BarChart2 } from 'lucide-react';

export const DashboardPage = () => {
  const { user, logout } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadData = async () => {
    try {
      setLoading(true);
      const [dash, hist] = await Promise.all([
        dashboardService.getDashboard(),
        resumeService.getHistory()
      ]);
      setDashboardData(dash);
      setHistory(hist);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this resume?')) return;
    try {
      await resumeService.deleteResume(id);
      loadData();
    } catch (err) {
      alert(err.message || 'Failed to delete resume');
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ textAlign: 'center', padding: '60px 0' }}>
        <p style={{ color: '#64748b' }}>Loading your candidate dashboard...</p>
      </div>
    );
  }

  const recentResume = dashboardData?.recent_resume;
  const recentJd = dashboardData?.recent_job_description;

  return (
    <div className="container" style={{ maxWidth: '1000px' }}>
      {/* Header Banner */}
      <div className="card" style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: '700', color: '#0f172a', marginBottom: '4px' }}>
            Welcome, {user?.full_name || user?.fullname || user?.email}!
          </h1>
          <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
            Manage your uploaded resumes, job descriptions, and AI-generated ATS Report analytics.
          </p>
        </div>
        <Link to="/upload" className="btn btn-primary">
          <Upload size={16} /> Upload New Resume
        </Link>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Grid Cards for Recent Activity */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        {/* Recent Resume Card */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <FileText color="#2563eb" size={20} />
            <h3 style={{ fontSize: '1.05rem', fontWeight: '600', color: '#0f172a' }}>Recent Resume</h3>
          </div>
          {recentResume ? (
            <div>
              <div style={{ fontWeight: '600', color: '#1e293b', marginBottom: '4px', wordBreak: 'break-all' }}>
                {recentResume.filename}
              </div>
              <div style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '12px' }}>
                Uploaded: {recentResume.upload_date || recentResume.uploaded_at ? new Date(recentResume.upload_date || recentResume.uploaded_at).toLocaleDateString() : 'Recent'}
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <Link to={`/ats-report/${recentResume.id}`} className="btn btn-primary" style={{ fontSize: '0.82rem', padding: '6px 12px' }}>
                  <BarChart2 size={14} /> View ATS Report
                </Link>
                <Link to={`/resume/${recentResume.id}`} className="btn btn-outline" style={{ fontSize: '0.82rem', padding: '6px 12px' }}>
                  Details
                </Link>
              </div>
            </div>
          ) : (
            <p style={{ fontSize: '0.88rem', color: '#94a3b8' }}>No resume uploaded yet.</p>
          )}
        </div>

        {/* Recent Job Description Card */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <Briefcase color="#16a34a" size={20} />
            <h3 style={{ fontSize: '1.05rem', fontWeight: '600', color: '#0f172a' }}>Recent Target Job Description</h3>
          </div>
          {recentJd ? (
            <div>
              <div style={{ fontWeight: '600', color: '#1e293b', marginBottom: '4px' }}>
                {recentJd.title}
              </div>
              <p style={{ fontSize: '0.85rem', color: '#64748b', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                {recentJd.description}
              </p>
              <div style={{ fontSize: '0.82rem', color: '#94a3b8', marginTop: '8px' }}>
                Added: {new Date(recentJd.created_at).toLocaleDateString()}
              </div>
            </div>
          ) : (
            <p style={{ fontSize: '0.88rem', color: '#94a3b8' }}>No job description added yet.</p>
          )}
        </div>

        {/* Profile Summary Card */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <UserIcon color="#0284c7" size={20} />
            <h3 style={{ fontSize: '1.05rem', fontWeight: '600', color: '#0f172a' }}>Profile Summary</h3>
          </div>
          <div style={{ fontSize: '0.9rem', color: '#334155' }}>
            <div><strong>Name:</strong> {user?.full_name || user?.fullname}</div>
            <div style={{ marginTop: '4px' }}><strong>Email:</strong> {user?.email}</div>
            <div style={{ marginTop: '6px', fontSize: '0.82rem', color: '#64748b' }}>
              Total Uploads: <strong>{dashboardData?.total_resumes || 0}</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Resume History Table */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: '600', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Clock size={18} color="#2563eb" /> Resume Upload & Analysis History
          </h3>
          <span className="badge badge-blue">{history.length} Documents</span>
        </div>

        {history.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #e2e8f0', color: '#64748b' }}>
                  <th style={{ padding: '12px' }}>Filename</th>
                  <th style={{ padding: '12px' }}>Target Job Title</th>
                  <th style={{ padding: '12px' }}>ATS Score</th>
                  <th style={{ padding: '12px' }}>Uploaded Date</th>
                  <th style={{ padding: '12px', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {history.map((r) => (
                  <tr key={r.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                    <td style={{ padding: '12px', fontWeight: '500', color: '#1e293b' }}>{r.filename}</td>
                    <td style={{ padding: '12px', color: '#475569' }}>
                      {r.job_descriptions?.length > 0 ? r.job_descriptions[0].title : 'Target Role'}
                    </td>
                    <td style={{ padding: '12px' }}>
                      {r.ats_score ? (
                        <span className="badge badge-green" style={{ fontWeight: '700' }}>
                          {r.ats_score} / 100
                        </span>
                      ) : (
                        <span className="badge badge-blue">Ready</span>
                      )}
                    </td>
                    <td style={{ padding: '12px', color: '#64748b' }}>
                      {r.upload_date || r.uploaded_at ? new Date(r.upload_date || r.uploaded_at).toLocaleDateString() : 'N/A'}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '8px' }}>
                        <Link to={`/ats-report/${r.id}`} className="btn btn-primary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
                          <BarChart2 size={14} /> Report
                        </Link>
                        <Link to={`/resume/${r.id}`} className="btn btn-outline" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
                          <Eye size={14} /> View
                        </Link>
                        <button onClick={() => handleDelete(r.id)} className="btn btn-danger" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '32px 0', color: '#94a3b8' }}>
            No resumes uploaded yet. Click "Upload New Resume" to start.
          </div>
        )}
      </div>
    </div>
  );
};
