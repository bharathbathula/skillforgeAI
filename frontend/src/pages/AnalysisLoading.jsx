import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { analysisService } from '../services/api';
import { CheckCircle2, Loader2, Sparkles, AlertCircle } from 'lucide-react';

const STEPS = [
  'Resume Uploaded & Validated',
  'Technical Tokenization & Skill Taxonomy Extraction',
  'Deterministic Arithmetic & Experience Ratio Calculation',
  'Individual Responsibility Match & Evidence Search',
  'Google Gemini 1.5 Multi-dimensional Analysis',
  'OpenAI GPT-4o Multi-dimensional Analysis',
  'Anthropic Claude 3.5 Multi-dimensional Analysis',
  'Consensus Ensemble & ATS Report Generation'
];

export const AnalysisLoading = () => {
  const { id } = useParams(); // resumeId
  const navigate = useNavigate();

  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState('');

  useEffect(() => {
    let stepTimer = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < STEPS.length - 1) return prev + 1;
        return prev;
      });
    }, 800);

    const runAnalysis = async () => {
      try {
        await analysisService.startAnalysis(id);
        setTimeout(() => {
          navigate(`/ats-report/${id}`);
        }, 1200);
      } catch (err) {
        setError(err.message || 'Analysis failed. Please try again.');
        clearInterval(stepTimer);
      }
    };

    runAnalysis();

    return () => clearInterval(stepTimer);
  }, [id, navigate]);

  return (
    <div className="container" style={{ maxWidth: '640px', padding: '60px 0' }}>
      <div className="card" style={{ textAlign: 'center', padding: '40px 32px' }}>
        <div style={{
          width: '56px',
          height: '56px',
          borderRadius: '16px',
          background: '#eff6ff',
          color: '#2563eb',
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '20px'
        }}>
          <Sparkles size={28} />
        </div>

        <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#0f172a', marginBottom: '8px' }}>
          Analyzing Your Resume...
        </h2>
        <p style={{ color: '#64748b', fontSize: '0.92rem', marginBottom: '32px' }}>
          SkillForge AI engine is parsing, generating section embeddings, and comparing your background against the target job description.
        </p>

        {error ? (
          <div>
            <div className="alert alert-error" style={{ textAlign: 'left', display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
              <AlertCircle size={20} />
              <div>
                <strong>Analysis Error:</strong> {error}
              </div>
            </div>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button onClick={() => window.location.reload()} className="btn btn-primary">
                Retry Analysis
              </button>
              <button onClick={() => navigate('/dashboard')} className="btn btn-outline">
                Go to Dashboard
              </button>
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'left', background: '#f8fafc', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
            {STEPS.map((stepText, idx) => {
              const isDone = idx < currentStep;
              const isCurrent = idx === currentStep;

              return (
                <div key={idx} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  marginBottom: idx === STEPS.length - 1 ? 0 : '16px',
                  color: isDone ? '#16a34a' : (isCurrent ? '#2563eb' : '#94a3b8'),
                  fontWeight: isCurrent ? '600' : '400',
                  fontSize: '0.9rem'
                }}>
                  {isDone ? (
                    <CheckCircle2 size={20} color="#16a34a" />
                  ) : isCurrent ? (
                    <Loader2 size={20} className="spin" color="#2563eb" style={{ animation: 'spin 1s linear infinite' }} />
                  ) : (
                    <div style={{ width: '20px', height: '20px', borderRadius: '50%', border: '2px solid #cbd5e1' }} />
                  )}
                  <span>{stepText}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
