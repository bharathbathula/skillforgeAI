import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, User as UserIcon, FileText, LayoutDashboard, Sparkles } from 'lucide-react';

export const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav style={{
      background: '#ffffff',
      borderBottom: '1px solid #e2e8f0',
      padding: '12px 0',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      backdropFilter: 'blur(12px)',
      backgroundColor: 'rgba(255,255,255,0.92)'
    }}>
      <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #2563eb, #4f46e5)',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: '800',
            fontSize: '0.85rem',
            boxShadow: '0 2px 8px rgba(37,99,235,0.3)'
          }}>
            SF
          </div>
          <div>
            <span style={{ fontSize: '1.15rem', fontWeight: '800', color: '#0f172a', letterSpacing: '-0.01em' }}>SkillForge AI</span>
            <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'block', lineHeight: 1, marginTop: '1px' }}>Career Mentorship Platform</span>
          </div>
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="btn btn-outline" style={{ padding: '7px 14px', fontSize: '0.85rem' }}>
                <LayoutDashboard size={15} /> Dashboard
              </Link>
              <Link to="/upload" className="btn btn-primary" style={{ padding: '7px 14px', fontSize: '0.85rem' }}>
                <FileText size={15} /> Upload & Analyze
              </Link>
              <div style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '5px 14px', background: '#f8fafc',
                borderRadius: '20px', border: '1px solid #e2e8f0'
              }}>
                <div style={{
                  width: '26px', height: '26px', borderRadius: '50%',
                  background: 'linear-gradient(135deg, #2563eb, #4f46e5)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  <UserIcon size={13} color="#fff" />
                </div>
                <span style={{ fontSize: '0.85rem', fontWeight: '600', color: '#334155' }}>
                  {user?.full_name || user?.fullname || user?.email}
                </span>
                <button onClick={handleLogout} style={{
                  background: 'none', border: 'none', cursor: 'pointer',
                  marginLeft: '4px', color: '#94a3b8', display: 'flex', alignItems: 'center',
                  transition: 'color 0.15s ease'
                }} title="Logout"
                  onMouseEnter={(e) => e.target.style.color = '#dc2626'}
                  onMouseLeave={(e) => e.target.style.color = '#94a3b8'}
                >
                  <LogOut size={15} />
                </button>
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-outline" style={{ padding: '7px 16px', fontSize: '0.88rem' }}>Log In</Link>
              <Link to="/register" className="btn btn-primary" style={{ padding: '7px 16px', fontSize: '0.88rem' }}>
                <Sparkles size={14} /> Get Started
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};
