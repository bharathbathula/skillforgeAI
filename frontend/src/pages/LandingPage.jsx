import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FileCheck, Sparkles, ArrowRight, BarChart2, Brain, Target, Zap, Shield } from 'lucide-react';

export const LandingPage = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div>
      {/* Hero Section */}
      <div style={{
        background: 'linear-gradient(135deg, #1e3a8a 0%, #2563eb 55%, #4f46e5 100%)',
        padding: '80px 24px 100px',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Decorative blobs */}
        <div style={{
          position: 'absolute', top: '-40px', right: '-60px',
          width: '300px', height: '300px', borderRadius: '50%',
          background: 'rgba(255,255,255,0.05)', pointerEvents: 'none'
        }} />
        <div style={{
          position: 'absolute', bottom: '-60px', left: '-40px',
          width: '250px', height: '250px', borderRadius: '50%',
          background: 'rgba(255,255,255,0.04)', pointerEvents: 'none'
        }} />

        <div className="container" style={{ maxWidth: '860px', position: 'relative', zIndex: 1 }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '8px',
            background: 'rgba(255,255,255,0.15)', backdropFilter: 'blur(8px)',
            border: '1px solid rgba(255,255,255,0.25)',
            borderRadius: '20px', padding: '6px 16px',
            fontSize: '0.82rem', fontWeight: '600', color: '#bfdbfe',
            marginBottom: '28px'
          }}>
            <Sparkles size={14} />
            Deterministic ATS Analysis + Pretrained Sentence-Transformer Embeddings
          </div>

          <h1 style={{
            fontSize: '3.2rem', fontWeight: '800', color: '#ffffff',
            lineHeight: '1.15', marginBottom: '20px',
            letterSpacing: '-0.02em'
          }}>
            SkillForge AI
          </h1>

          <p style={{
            fontSize: '1.18rem', color: '#bfdbfe',
            maxWidth: '640px', margin: '0 auto 36px', lineHeight: '1.7'
          }}>
            AI-powered resume analysis platform that generates objective ATS Compatibility Scores,
            maps your skills against job requirements, and provides actionable career development insights.
          </p>

          <div style={{ display: 'flex', justifyContent: 'center', gap: '14px', flexWrap: 'wrap' }}>
            {isAuthenticated ? (
              <Link to="/dashboard" className="btn btn-primary" style={{
                padding: '13px 32px', fontSize: '1rem',
                background: 'rgba(255,255,255,0.95)', color: '#1d4ed8',
                border: '1.5px solid rgba(255,255,255,0.8)',
                boxShadow: '0 4px 20px rgba(0,0,0,0.2)'
              }}>
                Go to Dashboard <ArrowRight size={18} />
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary" style={{
                  padding: '13px 32px', fontSize: '1rem',
                  background: 'rgba(255,255,255,0.95)', color: '#1d4ed8',
                  border: '1.5px solid rgba(255,255,255,0.8)',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.2)'
                }}>
                  Get Started Free <ArrowRight size={18} />
                </Link>
                <Link to="/login" className="btn btn-outline" style={{
                  padding: '13px 32px', fontSize: '1rem',
                  color: '#e0f2fe', borderColor: 'rgba(255,255,255,0.4)',
                  background: 'rgba(255,255,255,0.08)'
                }}>
                  Log In
                </Link>
              </>
            )}
          </div>

          {/* Hero Stats */}
          <div style={{
            display: 'flex', justifyContent: 'center', gap: '40px',
            marginTop: '56px', flexWrap: 'wrap'
          }}>
            {[
              { val: '8', label: 'ATS Parameters Analyzed' },
              { val: '100%', label: 'Deterministic Core Score' },
              { val: '384-dim', label: 'Semantic Embeddings' },
            ].map((stat, i) => (
              <div key={i} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '2rem', fontWeight: '800', color: '#ffffff' }}>{stat.val}</div>
                <div style={{ fontSize: '0.82rem', color: '#93c5fd', fontWeight: '500', marginTop: '2px' }}>{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="container" style={{ maxWidth: '1000px', padding: '72px 24px 80px' }}>
        <div style={{ textAlign: 'center', marginBottom: '52px' }}>
          <h2 style={{ fontSize: '1.9rem', fontWeight: '800', color: '#0f172a', marginBottom: '12px' }}>
            Professional Career Analysis Engine
          </h2>
          <p style={{ fontSize: '1rem', color: '#64748b', maxWidth: '580px', margin: '0 auto', lineHeight: '1.7' }}>
            Built with FastAPI, React, and pretrained sentence-transformer embeddings for objective, reproducible resume scoring.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '22px' }}>
          {[
            {
              icon: BarChart2, color: '#2563eb', bg: '#eff6ff',
              title: 'Deterministic ATS Scoring',
              desc: 'Skills (25%) + Experience (20%) + Responsibilities (20%) + Keywords, Semantic, Education, Projects & Formatting — all objective, zero hallucinations.'
            },
            {
              icon: Brain, color: '#7c3aed', bg: '#f5f3ff',
              title: 'Semantic Embedding Analysis',
              desc: 'Powered by all-MiniLM-L6-v2 pretrained sentence-transformers, producing 384-dimensional vector comparisons between resume and job description sections.'
            },
            {
              icon: Target, color: '#16a34a', bg: '#f0fdf4',
              title: 'Skill Gap Detection',
              desc: 'Multi-tier skill matching distinguishes exact matches, semantic matches, and missing skills across Required, Preferred, and Optional skill categories.'
            },
            {
              icon: Zap, color: '#d97706', bg: '#fffbeb',
              title: 'Actionable Recommendations',
              desc: 'Rule-based or AI-assisted guidance produces concrete project suggestions, learning directions, and resume improvement tips based on your skill gaps.'
            },
            {
              icon: FileCheck, color: '#0284c7', bg: '#f0f9ff',
              title: 'ATS Readability Audit',
              desc: 'Checks contact info, section completeness, content density, and structural formatting criteria to maximize recruiter ATS pass-through rates.'
            },
            {
              icon: Shield, color: '#dc2626', bg: '#fef2f2',
              title: 'Secure & Private',
              desc: 'JWT-authenticated user isolation, PostgreSQL persistence, and zero raw PII sent to external LLMs — only structured gap analysis is used for AI recommendations.'
            },
          ].map((feat, i) => {
            const Icon = feat.icon;
            return (
              <div key={i} className="card fade-in" style={{ animationDelay: `${i * 0.06}s` }}>
                <div style={{
                  width: '44px', height: '44px', borderRadius: '10px',
                  background: feat.bg, color: feat.color,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px'
                }}>
                  <Icon size={22} />
                </div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: '700', marginBottom: '8px', color: '#0f172a' }}>
                  {feat.title}
                </h3>
                <p style={{ fontSize: '0.88rem', color: '#64748b', lineHeight: '1.65' }}>
                  {feat.desc}
                </p>
              </div>
            );
          })}
        </div>

        {/* Bottom CTA */}
        {!isAuthenticated && (
          <div style={{ textAlign: 'center', marginTop: '60px' }}>
            <Link to="/register" className="btn btn-primary" style={{ padding: '14px 36px', fontSize: '1.05rem' }}>
              Analyze Your Resume Now <ArrowRight size={18} />
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};
