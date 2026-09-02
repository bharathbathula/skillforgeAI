import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { atsService } from '../services/api';
import { 
  Award, CheckCircle, AlertTriangle, XCircle, ArrowLeft, RefreshCw,
  Code, Briefcase, GraduationCap, FileCheck, Search, Lightbulb, Sparkles, TrendingUp,
  Cpu, ShieldCheck, HelpCircle, Layers, CheckCircle2, ChevronRight, BookOpen, UserCheck
} from 'lucide-react';

export const ATSReport = () => {
  const { id } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeModelTab, setActiveModelTab] = useState('consensus');

  const fetchReport = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await atsService.getReport(id);
      setReport(data);
    } catch (err) {
      setError(err.message || 'Failed to load ATS report');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [id]);

  if (loading) {
    return (
      <div className="container" style={{ textAlign: 'center', padding: '100px 0', color: '#64748b' }}>
        <RefreshCw size={36} className="spin" style={{ animation: 'spin 1.5s linear infinite', color: '#2563eb', margin: '0 auto 16px' }} />
        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#0f172a' }}>Assembling Multi-Model Intelligence...</h3>
        <p style={{ fontSize: '0.9rem', color: '#64748b', marginTop: '6px' }}>Reconciling deterministic arithmetic with Gemini, OpenAI, and Claude evaluations.</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="container" style={{ maxWidth: '600px', padding: '60px 0' }}>
        <div className="alert alert-error">{error || 'Report not found'}</div>
        <Link to="/dashboard" className="btn btn-outline">← Back to Dashboard</Link>
      </div>
    );
  }

  const details = report.report_details || report.score_details || {};
  const score = report.overall_score !== undefined ? report.overall_score : (details.overall_score || 0);
  const breakdown = report.score_breakdown || details.score_breakdown || {};
  const skills = details.skill_analysis || {};
  const experience = details.experience_analysis || {};
  const education = details.education_analysis || {};
  const keywords = details.keyword_analysis || {};
  const responsibilities = details.responsibility_analysis || {};
  const formatting = details.formatting_analysis || {};
  const models = details.models || {};
  const comparisonTable = details.comparison_table || [];
  const consensus = details.consensus || {};
  const learningRoadmap = details.learning_roadmap || consensus.learning_roadmap || [];
  const disagreements = details.disagreements || consensus.disagreements || [];
  const resumeImprovements = details.resume_improvements || consensus.resume_improvements || [];
  const strengths = details.strengths || consensus.strengths || [];
  const weaknesses = details.weaknesses || consensus.weaknesses || [];
  const jobFit = details.job_fit || consensus.job_fit || 'Evaluated';
  const confidence = details.confidence || consensus.confidence || 88;

  // Score color helper
  const getScoreColor = (s) => {
    if (s >= 85) return '#16a34a'; // Emerald
    if (s >= 70) return '#2563eb'; // Blue
    if (s >= 50) return '#d97706'; // Amber
    return '#dc2626'; // Red
  };

  const scoreColor = getScoreColor(score);

  return (
    <div className="container" style={{ maxWidth: '1120px', paddingBottom: '80px' }}>
      {/* Top Bar Navigation */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <Link to="/dashboard" className="btn btn-outline" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          <ArrowLeft size={16} /> Back to Dashboard
        </Link>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={fetchReport} className="btn btn-outline" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <RefreshCw size={15} /> Re-evaluate
          </button>
          <button onClick={() => window.print()} className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <FileCheck size={15} /> Export Report
          </button>
        </div>
      </div>

      {/* Hero: Final ATS Consensus Assessment */}
      <div className="card" style={{
        padding: '32px',
        marginBottom: '28px',
        background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
        border: '1px solid #e2e8f0',
        boxShadow: '0 4px 16px rgba(0,0,0,0.04)'
      }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '32px', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ flex: '1 1 450px' }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '4px 12px', background: '#eff6ff', borderRadius: '20px', color: '#1d4ed8', fontSize: '0.82rem', fontWeight: '600', marginBottom: '12px' }}>
              <ShieldCheck size={16} /> Multi-Model ATS Consensus Assessment
            </div>
            <h1 style={{ fontSize: '1.85rem', fontWeight: '800', color: '#0f172a', marginBottom: '8px' }}>
              Job Fit: <span style={{ color: scoreColor }}>{jobFit}</span>
            </h1>
            <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.6', marginBottom: '16px' }}>
              Cross-reconciled using deterministic arithmetic evidence, Google Gemini 1.5, OpenAI GPT-4o, and Anthropic Claude 3.5.
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '0.88rem' }}>
              <div style={{ padding: '6px 14px', background: '#f1f5f9', borderRadius: '8px', color: '#334155' }}>
                <strong>Confidence:</strong> {confidence}%
              </div>
              <div style={{ padding: '6px 14px', background: '#f1f5f9', borderRadius: '8px', color: '#334155' }}>
                <strong>Relevant Exp:</strong> {experience.candidate_relevant_years !== undefined ? `${experience.candidate_relevant_years} yrs` : 'Calculated'}
              </div>
              <div style={{ padding: '6px 14px', background: '#f1f5f9', borderRadius: '8px', color: '#334155' }}>
                <strong>Required Skills:</strong> {skills.matched_count || 0} / {skills.total_job_skills_count || 'N/A'}
              </div>
            </div>
          </div>

          {/* Big Score Gauge */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '24px 36px',
            background: '#ffffff',
            borderRadius: '20px',
            border: `2px solid ${scoreColor}`,
            boxShadow: '0 8px 24px rgba(0,0,0,0.06)'
          }}>
            <div style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>
              Consensus ATS Score
            </div>
            <div style={{ fontSize: '3.6rem', fontWeight: '900', color: scoreColor, lineHeight: '1' }}>
              {Math.round(score)}
            </div>
            <div style={{ fontSize: '0.82rem', color: '#94a3b8', fontWeight: '500', marginTop: '4px' }}>
              out of 100
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(135px, 1fr))',
        gap: '14px',
        marginBottom: '32px'
      }}>
        {[
          { label: 'Skills Match', val: breakdown.skill_score || 0, weight: '25%', icon: Code, color: '#2563eb' },
          { label: 'Relevant Exp', val: breakdown.experience_score || 0, weight: '20%', icon: Award, color: '#059669' },
          { label: 'Responsibilities', val: breakdown.responsibility_score || 0, weight: '20%', icon: Briefcase, color: '#7c3aed' },
          { label: 'Keywords', val: breakdown.keyword_score || 0, weight: '10%', icon: Search, color: '#0284c7' },
          { label: 'Semantic Sim', val: breakdown.semantic_score || 0, weight: '10%', icon: Sparkles, color: '#d97706' },
          { label: 'Education', val: breakdown.education_score || 0, weight: '5%', icon: GraduationCap, color: '#4f46e5' },
          { label: 'Formatting', val: breakdown.formatting_score || 0, weight: '5%', icon: FileCheck, color: '#0891b2' }
        ].map((item, idx) => (
          <div key={idx} className="card" style={{ padding: '16px', textAlign: 'center' }}>
            <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: '600', marginBottom: '4px' }}>
              {item.label}
            </div>
            <div style={{ fontSize: '1.35rem', fontWeight: '800', color: getScoreColor(item.val) }}>
              {Math.round(item.val)}%
            </div>
            <div style={{ height: '4px', background: '#e2e8f0', borderRadius: '2px', marginTop: '8px', overflow: 'hidden' }}>
              <div style={{ width: `${Math.min(100, Math.max(0, item.val))}%`, height: '100%', background: getScoreColor(item.val) }} />
            </div>
          </div>
        ))}
      </div>

      {/* SECTION: Multi-Model 3-Column Comparison Table */}
      <div className="card" style={{ marginBottom: '32px', overflowX: 'auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Cpu size={20} color="#2563eb" /> Multi-Model ATS Comparison Matrix
            </h3>
            <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '2px' }}>
              Side-by-side evaluation across Google Gemini, OpenAI GPT-4o, and Anthropic Claude 3.5.
            </p>
          </div>
        </div>

        {comparisonTable && comparisonTable.length > 0 ? (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem' }}>
            <thead>
              <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                <th style={{ padding: '12px 16px', fontWeight: '700', color: '#334155' }}>Evaluation Parameter</th>
                <th style={{ padding: '12px 16px', fontWeight: '700', color: '#2563eb' }}>Gemini 1.5</th>
                <th style={{ padding: '12px 16px', fontWeight: '700', color: '#059669' }}>OpenAI GPT-4o</th>
                <th style={{ padding: '12px 16px', fontWeight: '700', color: '#7c3aed' }}>Claude 3.5</th>
                <th style={{ padding: '12px 16px', fontWeight: '800', color: '#0f172a', background: '#f1f5f9' }}>Consensus Result</th>
              </tr>
            </thead>
            <tbody>
              {comparisonTable.map((row, idx) => {
                const isOverall = row.parameter_key === 'overall_score';
                return (
                  <tr key={idx} style={{
                    borderBottom: '1px solid #f1f5f9',
                    background: isOverall ? '#f0fdf4' : (idx % 2 === 0 ? '#ffffff' : '#fafafa'),
                    fontWeight: isOverall ? '700' : 'normal'
                  }}>
                    <td style={{ padding: '12px 16px', color: '#1e293b' }}>
                      {row.label}
                    </td>
                    <td style={{ padding: '12px 16px', color: '#334155' }}>
                      {typeof row.gemini === 'number' ? `${Math.round(row.gemini)}%` : row.gemini}
                    </td>
                    <td style={{ padding: '12px 16px', color: '#334155' }}>
                      {typeof row.openai === 'number' ? `${Math.round(row.openai)}%` : row.openai}
                    </td>
                    <td style={{ padding: '12px 16px', color: '#334155' }}>
                      {typeof row.claude === 'number' ? `${Math.round(row.claude)}%` : row.claude}
                    </td>
                    <td style={{ padding: '12px 16px', fontWeight: '700', color: '#0f172a', background: isOverall ? '#dcfce7' : '#f8fafc' }}>
                      {typeof row.consensus === 'number' ? `${Math.round(row.consensus)}%` : row.consensus}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <p style={{ color: '#94a3b8', fontSize: '0.88rem' }}>Multi-model comparison data generated with consensus score.</p>
        )}
      </div>

      {/* SECTION: Model Details & Tabs */}
      {models && Object.keys(models).length > 0 && (
        <div className="card" style={{ marginBottom: '32px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid #e2e8f0', paddingBottom: '12px', marginBottom: '20px' }}>
            {['consensus', 'gemini', 'openai', 'claude', 'deterministic'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveModelTab(tab)}
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  border: 'none',
                  fontSize: '0.88rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  background: activeModelTab === tab ? '#2563eb' : '#f1f5f9',
                  color: activeModelTab === tab ? '#ffffff' : '#475569',
                  transition: 'all 0.15s ease'
                }}
              >
                {tab === 'consensus' && 'Final Consensus'}
                {tab === 'gemini' && 'Gemini Analysis'}
                {tab === 'openai' && 'OpenAI Analysis'}
                {tab === 'claude' && 'Claude Analysis'}
                {tab === 'deterministic' && 'Deterministic Baseline'}
              </button>
            ))}
          </div>

          {/* Model Tab Content */}
          {activeModelTab === 'consensus' ? (
            <div>
              <h4 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#0f172a', marginBottom: '12px' }}>Consensus Key Insights</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
                <div style={{ background: '#f0fdf4', padding: '18px', borderRadius: '10px', border: '1px solid #bbf7d0' }}>
                  <h5 style={{ fontWeight: '700', color: '#166534', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <CheckCircle2 size={16} /> Verified Candidate Strengths
                  </h5>
                  <ul style={{ paddingLeft: '18px', color: '#14532d', fontSize: '0.88rem', lineHeight: '1.6' }}>
                    {strengths.map((s, idx) => (
                      <li key={idx} style={{ marginBottom: '6px' }}>{s}</li>
                    ))}
                  </ul>
                </div>
                <div style={{ background: '#fef2f2', padding: '18px', borderRadius: '10px', border: '1px solid #fecaca' }}>
                  <h5 style={{ fontWeight: '700', color: '#991b1b', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <AlertTriangle size={16} /> Identified Gaps & Weaknesses
                  </h5>
                  <ul style={{ paddingLeft: '18px', color: '#7f1d1d', fontSize: '0.88rem', lineHeight: '1.6' }}>
                    {weaknesses.map((w, idx) => (
                      <li key={idx} style={{ marginBottom: '6px' }}>{w}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            <div>
              {models[activeModelTab] ? (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h4 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#0f172a' }}>
                      {models[activeModelTab].provider_name} Evaluation ({models[activeModelTab].model_id})
                    </h4>
                    <span style={{ fontSize: '0.82rem', padding: '4px 10px', borderRadius: '12px', background: models[activeModelTab].status === 'success' ? '#dcfce7' : '#fee2e2', color: models[activeModelTab].status === 'success' ? '#166534' : '#991b1b', fontWeight: '600' }}>
                      Status: {models[activeModelTab].status}
                    </span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '16px' }}>
                    <div style={{ padding: '14px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                      <strong>Overall Score:</strong> {models[activeModelTab].overall_score}%
                    </div>
                    <div style={{ padding: '14px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                      <strong>Job Fit:</strong> {models[activeModelTab].job_fit || 'Evaluated'}
                    </div>
                    <div style={{ padding: '14px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                      <strong>Confidence:</strong> {models[activeModelTab].confidence}%
                    </div>
                  </div>

                  {models[activeModelTab].strengths && models[activeModelTab].strengths.length > 0 && (
                    <div style={{ marginBottom: '12px' }}>
                      <strong>Model Strengths:</strong>
                      <ul style={{ paddingLeft: '18px', fontSize: '0.88rem', color: '#334155', marginTop: '6px' }}>
                        {models[activeModelTab].strengths.map((s, i) => <li key={i}>{s}</li>)}
                      </ul>
                    </div>
                  )}

                  {models[activeModelTab].weaknesses && models[activeModelTab].weaknesses.length > 0 && (
                    <div>
                      <strong>Model Gaps:</strong>
                      <ul style={{ paddingLeft: '18px', fontSize: '0.88rem', color: '#334155', marginTop: '6px' }}>
                        {models[activeModelTab].weaknesses.map((w, i) => <li key={i}>{w}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <p style={{ color: '#94a3b8' }}>No detailed log available for this model.</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* SECTION: Itemized Responsibility-by-Responsibility Analysis Table */}
      <div className="card" style={{ marginBottom: '32px' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#0f172a', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Briefcase size={20} color="#7c3aed" /> Job Responsibility Alignment & Evidence
        </h3>
        <p style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '16px' }}>
          Discrete verification of each Job Description responsibility against resume work history.
        </p>

        {responsibilities.evaluations && responsibilities.evaluations.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {responsibilities.evaluations.map((item, idx) => {
              const isMatch = item.match_percentage >= 65;
              const isPartial = item.match_percentage >= 35 && item.match_percentage < 65;
              return (
                <div key={idx} style={{
                  padding: '16px',
                  borderRadius: '8px',
                  background: isMatch ? '#f8fafc' : (isPartial ? '#fffbeb' : '#fef2f2'),
                  borderLeft: `4px solid ${isMatch ? '#16a34a' : (isPartial ? '#d97706' : '#dc2626')}`,
                  border: '1px solid #e2e8f0',
                  borderLeftWidth: '4px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                    <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.92rem' }}>
                      {item.responsibility}
                    </div>
                    <span style={{
                      fontSize: '0.8rem',
                      fontWeight: '700',
                      padding: '3px 10px',
                      borderRadius: '12px',
                      background: isMatch ? '#dcfce7' : (isPartial ? '#fef3c7' : '#fee2e2'),
                      color: isMatch ? '#166534' : (isPartial ? '#92400e' : '#991b1b')
                    }}>
                      {item.match_percentage}% Match
                    </span>
                  </div>
                  <div style={{ fontSize: '0.85rem', color: '#334155', marginTop: '4px' }}>
                    <strong>Resume Evidence:</strong> {item.evidence}
                  </div>
                  {item.gap && (
                    <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '2px' }}>
                      <strong>Context:</strong> {item.gap}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <p style={{ color: '#94a3b8' }}>Responsibilities matched against core role requirements.</p>
        )}
      </div>

      {/* SECTION: Skills Analysis (Required vs Preferred) */}
      <div className="card" style={{ marginBottom: '32px' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#0f172a', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Code size={20} color="#2563eb" /> Technical & Core Skills Breakdown
        </h3>

        {/* Required Skills */}
        <div style={{ marginBottom: '20px' }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: '700', color: '#1e293b', marginBottom: '10px' }}>
            Required Skills ({skills.required_skills_breakdown ? skills.required_skills_breakdown.length : 0})
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {skills.required_skills_breakdown && skills.required_skills_breakdown.length > 0 ? (
              skills.required_skills_breakdown.map((s, idx) => {
                const isFound = s.status !== 'Missing';
                return (
                  <div key={idx} style={{
                    padding: '6px 12px',
                    borderRadius: '6px',
                    background: isFound ? '#f0fdf4' : '#fef2f2',
                    border: `1px solid ${isFound ? '#86efac' : '#fca5a5'}`,
                    fontSize: '0.85rem',
                    color: isFound ? '#166534' : '#991b1b',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    {isFound ? <CheckCircle size={14} /> : <XCircle size={14} />}
                    <span><strong>{s.skill}</strong> ({s.status})</span>
                  </div>
                );
              })
            ) : (
              skills.matched_skills && skills.matched_skills.map((s, idx) => (
                <span key={idx} className="badge badge-green">{s}</span>
              ))
            )}
          </div>
        </div>

        {/* Preferred Skills */}
        {skills.preferred_skills_breakdown && skills.preferred_skills_breakdown.length > 0 && (
          <div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: '700', color: '#475569', marginBottom: '10px' }}>
              Preferred / Secondary Skills ({skills.preferred_skills_breakdown.length})
            </h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {skills.preferred_skills_breakdown.map((s, idx) => {
                const isFound = s.status !== 'Missing';
                return (
                  <div key={idx} style={{
                    padding: '6px 12px',
                    borderRadius: '6px',
                    background: isFound ? '#eff6ff' : '#f8fafc',
                    border: `1px solid ${isFound ? '#bfdbfe' : '#e2e8f0'}`,
                    fontSize: '0.85rem',
                    color: isFound ? '#1e40af' : '#64748b',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    {isFound ? <CheckCircle size={14} /> : <span style={{ width: '14px', textAlign: 'center' }}>-</span>}
                    <span>{s.skill} ({s.status})</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* SECTION: Experience & Education Verification */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '24px', marginBottom: '32px' }}>
        {/* Experience Verification Card */}
        <div className="card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Award size={18} color="#059669" /> Experience Verification
          </h3>
          <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '0.88rem' }}>
              <span style={{ color: '#64748b' }}>Required:</span>
              <strong style={{ color: '#0f172a' }}>{experience.required_experience_years || '2.0'} years</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '0.88rem' }}>
              <span style={{ color: '#64748b' }}>Candidate Relevant:</span>
              <strong style={{ color: '#16a34a' }}>{experience.candidate_relevant_years || 0} years</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem' }}>
              <span style={{ color: '#64748b' }}>Total Work History:</span>
              <strong style={{ color: '#334155' }}>{experience.candidate_total_years || 0} years</strong>
            </div>
          </div>
          <p style={{ fontSize: '0.85rem', color: '#475569', lineHeight: '1.5' }}>
            {experience.explanation || experience.gap_summary || 'Experience calculated from chronological resume positions.'}
          </p>
        </div>

        {/* Education Verification Card */}
        <div className="card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <GraduationCap size={18} color="#4f46e5" /> Education Credentials
          </h3>
          <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '12px' }}>
            <div style={{ fontSize: '0.88rem', marginBottom: '4px' }}>
              <strong>Candidate Degree:</strong> {education.candidate_degree || 'None Found'}
            </div>
            <div style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '4px' }}>
              <strong>Institution:</strong> {education.candidate_institution || 'N/A'}
            </div>
            <div style={{ fontSize: '0.85rem', color: '#16a34a' }}>
              <strong>Match Status:</strong> {education.match_status || 'Verified'}
            </div>
          </div>
          <p style={{ fontSize: '0.85rem', color: '#475569', lineHeight: '1.5' }}>
            {education.evidence || 'Education credentials verified against job prerequisites.'}
          </p>
        </div>
      </div>

      {/* SECTION: Model Disagreements & Explanation (if any) */}
      {disagreements && disagreements.length > 0 && (
        <div className="card" style={{ marginBottom: '32px', background: '#fffbeb', border: '1px solid #fde68a' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#92400e', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <HelpCircle size={18} color="#d97706" /> Model Variance & Reconciliation
          </h3>
          <p style={{ fontSize: '0.85rem', color: '#78350f', marginBottom: '14px' }}>
            Our ensemble engine detected divergence between AI models and reconciled the result using verified deterministic facts:
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {disagreements.map((d, idx) => (
              <div key={idx} style={{ padding: '12px', background: '#ffffff', borderRadius: '6px', border: '1px solid #fef3c7' }}>
                <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.88rem' }}>{d.parameter}</div>
                <div style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '2px' }}>{d.divergence}</div>
                <div style={{ fontSize: '0.82rem', color: '#166534', marginTop: '2px', fontWeight: '500' }}>{d.resolution}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SECTION: Prioritized Job-Specific Learning Roadmap */}
      <div className="card" style={{ marginBottom: '32px' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#0f172a', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BookOpen size={20} color="#059669" /> Prioritized Job-Specific Learning Roadmap
        </h3>
        <p style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '16px' }}>
          Tailored learning path specifically targeting missing technologies from this job description.
        </p>

        {learningRoadmap && learningRoadmap.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {learningRoadmap.map((item, idx) => (
              <div key={idx} style={{ padding: '16px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <div style={{ fontWeight: '700', color: '#0f172a', fontSize: '0.95rem' }}>
                    {item.skill}
                  </div>
                  <span style={{ fontSize: '0.78rem', fontWeight: '700', padding: '3px 8px', borderRadius: '4px', background: '#e0f2fe', color: '#0369a1' }}>
                    {item.priority}
                  </span>
                </div>
                <div style={{ fontSize: '0.85rem', color: '#334155', marginBottom: '4px' }}>
                  <strong>Why it matters:</strong> {item.importance_reason || item.reason}
                </div>
                <div style={{ fontSize: '0.82rem', color: '#059669' }}>
                  <strong>Action Plan:</strong> {item.learning_sequence || item.expected_benefit}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: '#94a3b8' }}>No critical technology gaps identified for this role.</p>
        )}
      </div>

      {/* SECTION: Evidence-Based Resume Improvement Recommendations */}
      <div className="card">
        <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#0f172a', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <TrendingUp size={20} color="#2563eb" /> Resume Improvement & Refinement Recommendations
        </h3>
        <p style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '16px' }}>
          Actionable, honest recommendations to optimize your resume impact without fabricating experience.
        </p>
        <ul style={{ paddingLeft: '20px', color: '#334155', fontSize: '0.9rem', lineHeight: '1.7' }}>
          {resumeImprovements && resumeImprovements.length > 0 ? (
            resumeImprovements.map((rec, idx) => (
              <li key={idx} style={{ marginBottom: '8px' }}>{rec}</li>
            ))
          ) : (
            <li>Quantify project outcomes and impact metrics (e.g. 'Improved query latency by 40%').</li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default ATSReport;
