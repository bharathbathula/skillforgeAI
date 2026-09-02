import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FileCheck, Database, Lock, Sparkles, ArrowRight } from 'lucide-react';

export const LandingPage = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="container" style={{ maxWidth: '960px' }}>
      {/* Hero */}
      <div style={{ textAlign: 'center', margin: '40px 0 60px' }}>
        <span className="badge badge-blue" style={{ marginBottom: '16px', fontSize: '0.85rem' }}>
          <Sparkles size={14} /> Phase 1: Core Storage & Authentication Engine
        </span>
        <h1 style={{ fontSize: '2.75rem', fontWeight: '800', color: '#0f172a', lineHeight: '1.2', marginBottom: '20px' }}>
          SkillForge AI
        </h1>
        <p style={{ fontSize: '1.15rem', color: '#475569', maxWidth: '680px', margin: '0 auto 32px', lineHeight: '1.6' }}>
          An AI-powered career mentorship and resume analysis platform designed to help students bridge skill gaps, align resumes with industry expectations, and track employability.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px' }}>
          {isAuthenticated ? (
            <Link to="/dashboard" className="btn btn-primary" style={{ padding: '12px 28px', fontSize: '1rem' }}>
              Go to Dashboard <ArrowRight size={18} />
            </Link>
          ) : (
            <>
              <Link to="/register" className="btn btn-primary" style={{ padding: '12px 28px', fontSize: '1rem' }}>
                Get Started <ArrowRight size={18} />
              </Link>
              <Link to="/login" className="btn btn-outline" style={{ padding: '12px 28px', fontSize: '1rem' }}>
                Log In
              </Link>
            </>
          )}
        </div>
      </div>

      {/* Feature Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '24px', margin: '40px 0' }}>
        <div className="card">
          <div style={{ width: '40px', height: '40px', borderRadius: '8px', background: '#eff6ff', color: '#2563eb', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
            <FileCheck size={24} />
          </div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '8px' }}>Resume & JD Storage</h3>
          <p style={{ fontSize: '0.9rem', color: '#64748b' }}>
            Upload resume PDFs and target job descriptions to maintain structured applicant profile histories.
          </p>
        </div>

        <div className="card">
          <div style={{ width: '40px', height: '40px', borderRadius: '8px', background: '#f0fdf4', color: '#16a34a', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
            <Database size={24} />
          </div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '8px' }}>PostgreSQL Integration</h3>
          <p style={{ fontSize: '0.9rem', color: '#64748b' }}>
            Engineered with SQLAlchemy ORM and Alembic migrations, pre-architected for future vector embedding migrations.
          </p>
        </div>

        <div className="card">
          <div style={{ width: '40px', height: '40px', borderRadius: '8px', background: '#fef3c7', color: '#d97706', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
            <Lock size={24} />
          </div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '8px' }}>Secure JWT Authentication</h3>
          <p style={{ fontSize: '0.9rem', color: '#64748b' }}>
            Protected user sessions ensuring student data privacy and isolated user dashboard management.
          </p>
        </div>
      </div>
    </div>
  );
};
