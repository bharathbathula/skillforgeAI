import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from '../components/Navbar';

export const MainLayout = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <main style={{ flex: 1, padding: '32px 0' }}>
        <Outlet />
      </main>
      <footer style={{
        borderTop: '1px solid #e2e8f0',
        padding: '24px 0',
        background: '#ffffff',
        textAlign: 'center'
      }}>
        <div className="container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '0.88rem', fontWeight: '600', color: '#334155' }}>
            SkillForge AI
          </span>
          <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
            Career Mentorship & Resume Analysis Platform — Academic Mini Project © {new Date().getFullYear()}
          </span>
        </div>
      </footer>
    </div>
  );
};
