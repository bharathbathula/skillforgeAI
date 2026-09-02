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
      <footer style={{ borderTop: '1px solid #e2e8f0', padding: '20px 0', background: '#ffffff', textAlign: 'center', color: '#64748b', fontSize: '0.88rem' }}>
        <div className="container">
          SkillForge AI © {new Date().getFullYear()} — Career Mentorship & Resume Analysis Platform (Academic Mini Project)
        </div>
      </footer>
    </div>
  );
};
