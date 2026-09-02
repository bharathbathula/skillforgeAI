import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, User as UserIcon, FileText, LayoutDashboard } from 'lucide-react';

export const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav style={{ background: '#ffffff', borderBottom: '1px solid #e2e8f0', padding: '14px 0' }}>
      <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            background: '#2563eb',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: '700'
          }}>
            SF
          </div>
          <div>
            <span style={{ fontSize: '1.2rem', fontWeight: '700', color: '#0f172a' }}>SkillForge AI</span>
            <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', lineHeight: 1 }}>Career Mentorship Platform</span>
          </div>
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="btn btn-outline" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <LayoutDashboard size={16} /> Dashboard
              </Link>
              <Link to="/upload" className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <FileText size={16} /> Upload Resume & JD
              </Link>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 12px', background: '#f8fafc', borderRadius: '20px', border: '1px solid #e2e8f0' }}>
                <UserIcon size={16} color="#2563eb" />
                <span style={{ fontSize: '0.88rem', fontWeight: '600', color: '#334155' }}>{user?.full_name || user?.fullname || user?.email}</span>
                <button onClick={handleLogout} style={{ background: 'none', border: 'none', cursor: 'pointer', marginLeft: '6px', color: '#64748b', display: 'flex', alignItems: 'center' }} title="Logout">
                  <LogOut size={16} />
                </button>
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-outline">Log In</Link>
              <Link to="/register" className="btn btn-primary">Get Started</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};
