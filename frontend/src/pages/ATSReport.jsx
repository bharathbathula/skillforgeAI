import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { atsService } from '../services/api';
import { 
  ArrowLeft, RefreshCw, FileCheck, CheckCircle2, AlertCircle, XCircle,
  Briefcase, GraduationCap, Code, Layers, FileText, Sparkles, BookOpen,
  TrendingUp, Award, Check, ChevronDown, ChevronUp, Lightbulb
} from 'lucide-react';

export const ATSReport = () => {
  const { id } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeDetailSection, setActiveDetailSection] = useState('experience');

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
        <RefreshCw size={36} className="spin" style={{ animation: 'spin 1.2s linear infinite', color: '#2563eb', margin: '0 auto 16px' }} />
        <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#0f172a' }}>Loading ATS Analysis Report...</h3>
        <p style={{ fontSize: '0.9rem', color: '#64748b', marginTop: '6px' }}>Retrieving deterministic analytical scores and recommendations.</p>
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
  const projects = details.project_analysis || {};
  const formatting = details.formatting_analysis || {};
  const recs = details.recommendations || {};
  const strengths = details.strengths || [];
  const weaknesses = details.weaknesses || [];
  const jobFit = details.job_fit || 'Evaluated';
  const semanticSim = details.semantic_similarity !== undefined ? details.semantic_similarity : (breakdown.semantic_score || 0);

  // Score color helper
  const getScoreColor = (s) => {
    if (s >= 85) return '#16a34a'; // Emerald
    if (s >= 70) return '#2563eb'; // Blue
    if (s >= 50) return '#d97706'; // Amber
    return '#dc2626'; // Red
  };

  const scoreColor = getScoreColor(score);

  return (
    <div className="container" style={{ maxWidth: '1060px', paddingBottom: '80px' }}>
      {/* Top Bar Actions */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', margin: '24px 0 20px' }}>
        <Link to="/dashboard" className="btn btn-outline" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.88rem' }}>
          <ArrowLeft size={16} /> Back to Dashboard
        </Link>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={fetchReport} className="btn btn-outline" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.88rem' }}>
            <RefreshCw size={14} /> Refresh
          </button>
          <button onClick={() => window.print()} className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.88rem' }}>
            <FileCheck size={14} /> Print / Export
          </button>
        </div>
      </div>

      {/* =========================================================================
          SECTION 1: TOP HERO (ATS Compatibility Score, Role, Semantic Match, Summary)
         ========================================================================= */}
      <div className="card" style={{ marginBottom: '24px', padding: '28px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '28px', alignItems: 'center' }}>
          {/* Main Score Display */}
          <div style={{
            width: '140px',
            height: '140px',
            borderRadius: '16px',
            border: `3px solid ${scoreColor}`,
            background: '#ffffff',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.04)',
            textAlign: 'center'
          }}>
            <span style={{ fontSize: '2.5rem', fontWeight: '800', color: scoreColor, lineHeight: 1 }}>
              {Math.round(score)}
            </span>
            <span style={{ fontSize: '0.75rem', fontWeight: '600', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginTop: '4px' }}>
              out of 100
            </span>
            <span style={{
              fontSize: '0.72rem',
              fontWeight: '700',
              color: scoreColor,
              marginTop: '4px',
              padding: '2px 8px',
              borderRadius: '12px',
              background: `${scoreColor}15`
            }}>
              {jobFit}
            </span>
          </div>

          {/* Role & Summary */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span className="badge badge-blue" style={{ fontSize: '0.8rem', padding: '3px 10px' }}>
                ATS Compatibility Assessment
              </span>
              <span style={{ fontSize: '0.82rem', color: '#64748b' }}>
                Pretrained Sentence-Transformer Embeddings (all-MiniLM-L6-v2)
              </span>
            </div>

            <h1 style={{ fontSize: '1.75rem', fontWeight: '800', color: '#0f172a', marginBottom: '8px' }}>
              Overall Compatibility Score: {Math.round(score)}%
            </h1>

            <p style={{ fontSize: '0.95rem', color: '#475569', lineHeight: 1.5, marginBottom: '14px' }}>
              {experience.explanation || `Candidate profile demonstrates ${jobFit.toLowerCase()} with the target job requirements across skills, experience, and responsibilities.`}
            </p>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '0.88rem', color: '#334155' }}>
              <div style={{ background: '#f8fafc', padding: '6px 12px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                <strong>Semantic Similarity:</strong> <span style={{ color: '#2563eb', fontWeight: '600' }}>{semanticSim}%</span>
              </div>
              <div style={{ background: '#f8fafc', padding: '6px 12px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                <strong>Skills Matched:</strong> <span style={{ color: '#16a34a', fontWeight: '600' }}>{skills.matched_count || skills.matched_skills?.length || 0}</span> / {skills.total_job_skills_count || (skills.matched_skills?.length || 0) + (skills.missing_skills?.length || 0)}
              </div>
              <div style={{ background: '#f8fafc', padding: '6px 12px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                <strong>Experience:</strong> <span style={{ fontWeight: '600' }}>{experience.candidate_relevant_years || 0} yrs</span> (Req: {experience.required_experience_years || 0} yrs)
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* =========================================================================
          SECTION 2: MATCHED SKILLS & MISSING SKILLS CHIPS
         ========================================================================= */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
        {/* Matched Skills */}
        <div className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#166534', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle2 size={18} color="#16a34a" /> Matched Skills ({skills.matched_skills?.length || 0})
            </h3>
            <span style={{ fontSize: '0.78rem', color: '#64748b' }}>Detected in Resume</span>
          </div>
          {skills.matched_skills?.length > 0 ? (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {skills.matched_skills.map((s, idx) => (
                <span key={idx} style={{
                  background: '#f0fdf4',
                  color: '#15803d',
                  border: '1px solid #bbf7d0',
                  borderRadius: '6px',
                  padding: '4px 10px',
                  fontSize: '0.82rem',
                  fontWeight: '600'
                }}>
                  ✓ {s}
                </span>
              ))}
            </div>
          ) : (
            <p style={{ fontSize: '0.88rem', color: '#94a3b8' }}>No direct skill matches detected in resume.</p>
          )}
        </div>

        {/* Missing / Priority Skills */}
        <div className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#991b1b', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <XCircle size={18} color="#dc2626" /> Missing / Priority Skills ({skills.missing_skills?.length || 0})
            </h3>
            <span style={{ fontSize: '0.78rem', color: '#64748b' }}>Required by Job</span>
          </div>
          {skills.missing_skills?.length > 0 ? (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {skills.missing_skills.map((s, idx) => (
                <span key={idx} style={{
                  background: '#fef2f2',
                  color: '#b91c1c',
                  border: '1px solid #fecaca',
                  borderRadius: '6px',
                  padding: '4px 10px',
                  fontSize: '0.82rem',
                  fontWeight: '600'
                }}>
                  + {s}
                </span>
              ))}
            </div>
          ) : (
            <p style={{ fontSize: '0.88rem', color: '#16a34a' }}>All listed job skills are matched in candidate resume!</p>
          )}
        </div>
      </div>

      {/* =========================================================================
          SECTION 3: COMPONENT SCORES BREAKDOWN (AUDITABLE WEIGHTS)
         ========================================================================= */}
      <div className="card" style={{ marginBottom: '24px', padding: '22px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#0f172a' }}>
              Deterministic Component Scores
            </h3>
            <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '2px' }}>
              Formula: Skills (25%) + Experience (20%) + Responsibilities (20%) + Keywords (10%) + Semantic (10%) + Education (5%) + Projects (5%) + Formatting (5%)
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
          {[
            { label: 'Skills Alignment', weight: '25%', score: breakdown.skill_score || 0, icon: Code },
            { label: 'Experience Match', weight: '20%', score: breakdown.experience_score || 0, icon: Briefcase },
            { label: 'Responsibilities', weight: '20%', score: breakdown.responsibility_score || 0, icon: Layers },
            { label: 'Keyword Coverage', weight: '10%', score: breakdown.keyword_score || 0, icon: FileText },
            { label: 'Semantic Similarity', weight: '10%', score: breakdown.semantic_score || semanticSim, icon: TrendingUp },
            { label: 'Education Credential', weight: '5%', score: breakdown.education_score || 0, icon: GraduationCap },
            { label: 'Project Alignment', weight: '5%', score: breakdown.project_score || 0, icon: Sparkles },
            { label: 'ATS Readability', weight: '5%', score: breakdown.formatting_score || 0, icon: FileCheck },
          ].map((item, idx) => {
            const Icon = item.icon;
            const barColor = getScoreColor(item.score);
            return (
              <div key={idx} style={{
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                padding: '12px 14px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', fontWeight: '600', color: '#334155' }}>
                    <Icon size={14} color="#64748b" />
                    <span>{item.label}</span>
                  </div>
                  <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{item.weight}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <div style={{ height: '6px', width: '70%', background: '#e2e8f0', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ width: `${Math.min(100, Math.max(0, item.score))}%`, height: '100%', background: barColor }} />
                  </div>
                  <span style={{ fontSize: '0.88rem', fontWeight: '700', color: barColor }}>
                    {Math.round(item.score)}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* =========================================================================
          SECTION 4: EVIDENCE / DETAILS DRILLDOWN
         ========================================================================= */}
      <div className="card" style={{ marginBottom: '24px', padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', borderBottom: '1px solid #e2e8f0', paddingBottom: '12px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#0f172a' }}>
            Analysis Evidence & Verification Details
          </h3>
          <div style={{ display: 'flex', gap: '6px' }}>
            {[
              { id: 'experience', label: 'Experience' },
              { id: 'responsibilities', label: 'Responsibilities' },
              { id: 'education', label: 'Education' },
              { id: 'projects', label: 'Projects' },
              { id: 'formatting', label: 'Formatting' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveDetailSection(tab.id)}
                className={`btn ${activeDetailSection === tab.id ? 'btn-primary' : 'btn-outline'}`}
                style={{ padding: '4px 12px', fontSize: '0.8rem' }}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content: Experience */}
        {activeDetailSection === 'experience' && (
          <div>
            <div style={{ background: '#f8fafc', padding: '12px 16px', borderRadius: '8px', marginBottom: '16px', border: '1px solid #e2e8f0', fontSize: '0.88rem' }}>
              <strong>Calculation Summary:</strong> {experience.explanation || 'Chronological experience evaluated against JD requirements without overlapping double-count.'}
            </div>
            {experience.role_breakdown?.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {experience.role_breakdown.map((role, idx) => (
                  <div key={idx} style={{ padding: '12px 14px', border: '1px solid #e2e8f0', borderRadius: '8px', background: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: '600', color: '#1e293b', fontSize: '0.9rem' }}>{role.role} — <span style={{ color: '#64748b', fontWeight: '400' }}>{role.company}</span></div>
                      <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '2px' }}>Duration: {role.duration} ({role.duration_years} yrs)</div>
                    </div>
                    <span className={`badge ${role.is_relevant ? 'badge-green' : 'badge-blue'}`} style={{ fontSize: '0.75rem' }}>
                      {role.is_relevant ? 'Domain Relevant' : 'General Experience'}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: '#94a3b8', fontSize: '0.88rem' }}>No individual work experience entries detected in resume.</p>
            )}
          </div>
        )}

        {/* Tab Content: Responsibilities */}
        {activeDetailSection === 'responsibilities' && (
          <div>
            <div style={{ marginBottom: '12px', fontSize: '0.85rem', color: '#64748b' }}>
              Evaluated {responsibilities.total_responsibilities_count || 0} discrete responsibilities extracted from target JD:
            </div>
            {responsibilities.evaluations?.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {responsibilities.evaluations.map((ev, idx) => (
                  <div key={idx} style={{ padding: '12px 14px', border: '1px solid #e2e8f0', borderRadius: '8px', background: '#f8fafc' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontWeight: '600', fontSize: '0.88rem', color: '#1e293b' }}>{ev.responsibility}</span>
                      <span style={{ fontWeight: '700', fontSize: '0.82rem', color: getScoreColor(ev.match_percentage) }}>
                        {ev.match_percentage}% Match
                      </span>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#475569', marginTop: '4px' }}>
                      <strong>Evidence:</strong> {ev.evidence}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: '#94a3b8', fontSize: '0.88rem' }}>No explicit responsibilities evaluated.</p>
            )}
          </div>
        )}

        {/* Tab Content: Education */}
        {activeDetailSection === 'education' && (
          <div style={{ fontSize: '0.9rem', color: '#334155' }}>
            <div style={{ padding: '14px', border: '1px solid #e2e8f0', borderRadius: '8px', background: '#f8fafc' }}>
              <div style={{ marginBottom: '8px' }}>
                <strong>Status:</strong> <span className="badge badge-green" style={{ marginLeft: '8px' }}>{education.match_status || 'Verified'}</span>
              </div>
              <div style={{ marginBottom: '6px' }}><strong>Candidate Credential:</strong> {education.candidate_degree || 'Degree'} from {education.candidate_institution || 'Institution'}</div>
              <div style={{ marginBottom: '6px' }}><strong>Job Requirement:</strong> {education.required_education || 'Bachelor degree or equivalent'}</div>
              <div style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '8px' }}>{education.evidence}</div>
            </div>
          </div>
        )}

        {/* Tab Content: Projects */}
        {activeDetailSection === 'projects' && (
          <div>
            {projects.project_evaluations?.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {projects.project_evaluations.map((p, idx) => (
                  <div key={idx} style={{ padding: '12px 14px', border: '1px solid #e2e8f0', borderRadius: '8px', background: '#f8fafc' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontWeight: '600', fontSize: '0.9rem', color: '#1e293b' }}>{p.name}</span>
                      <span style={{ fontWeight: '700', fontSize: '0.85rem', color: getScoreColor(p.relevance_percentage) }}>
                        {p.relevance_percentage}% Relevance
                      </span>
                    </div>
                    {p.matched_technologies?.length > 0 && (
                      <div style={{ fontSize: '0.8rem', color: '#166534', marginTop: '4px' }}>
                        <strong>Matched Tech:</strong> {p.matched_technologies.join(', ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: '#94a3b8', fontSize: '0.88rem' }}>No individual project entries detected in resume.</p>
            )}
          </div>
        )}

        {/* Tab Content: Formatting */}
        {activeDetailSection === 'formatting' && (
          <div>
            <div style={{ marginBottom: '12px', fontSize: '0.88rem', color: '#475569' }}>
              <strong>ATS Readability Score:</strong> {formatting.formatting_score || 85}% ({formatting.word_count || 0} words)
            </div>
            {formatting.checks?.length > 0 && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '8px' }}>
                {formatting.checks.map((chk, idx) => (
                  <div key={idx} style={{ padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: '6px', background: '#ffffff', fontSize: '0.82rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      {chk.status === 'Passed' ? <CheckCircle2 size={14} color="#16a34a" /> : <AlertCircle size={14} color="#dc2626" />}
                      <strong>{chk.item}</strong>
                    </div>
                    <div style={{ color: '#64748b', marginTop: '2px', fontSize: '0.78rem' }}>{chk.detail}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* =========================================================================
          SECTION 5: STRENGTHS & AREAS TO IMPROVE
         ========================================================================= */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
        <div className="card" style={{ padding: '20px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#166534', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Award size={18} color="#16a34a" /> Key Strengths
          </h3>
          <ul style={{ paddingLeft: '18px', fontSize: '0.88rem', color: '#334155', lineHeight: 1.6 }}>
            {strengths.map((str, idx) => (
              <li key={idx} style={{ marginBottom: '6px' }}>{str}</li>
            ))}
          </ul>
        </div>

        <div className="card" style={{ padding: '20px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#b45309', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <AlertCircle size={18} color="#d97706" /> Areas to Improve
          </h3>
          <ul style={{ paddingLeft: '18px', fontSize: '0.88rem', color: '#334155', lineHeight: 1.6 }}>
            {weaknesses.map((w, idx) => (
              <li key={idx} style={{ marginBottom: '6px' }}>{w}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* =========================================================================
          SECTION 6: DOWNSTREAM RECOMMENDATIONS (ADVISORY LAYER)
         ========================================================================= */}
      <div className="card" style={{ padding: '26px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', borderBottom: '1px solid #e2e8f0', paddingBottom: '12px' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '800', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Lightbulb size={22} color="#2563eb" /> Actionable Recommendations & Guidance
            </h2>
            <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '2px' }}>
              {recs.is_ai_generated ? 'AI-Assisted Guidance generated from structured gap analysis.' : 'Deterministic Rule-Based Guidance derived strictly from missing skill gaps.'}
            </p>
          </div>
          <span className={`badge ${recs.is_ai_generated ? 'badge-blue' : 'badge-green'}`} style={{ fontSize: '0.78rem' }}>
            {recs.is_ai_generated ? 'AI-Assisted (Downstream)' : 'Rule-Based Guidance'}
          </span>
        </div>

        {/* 1. Priority Skills to Develop */}
        {recs.priority_skills?.length > 0 && (
          <div style={{ marginBottom: '22px' }}>
            <h4 style={{ fontSize: '0.92rem', fontWeight: '700', color: '#1e293b', marginBottom: '8px' }}>
              Priority Skills to Develop:
            </h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {recs.priority_skills.map((s, idx) => (
                <span key={idx} style={{
                  background: '#eff6ff',
                  color: '#1d4ed8',
                  border: '1px solid #bfdbfe',
                  borderRadius: '6px',
                  padding: '5px 12px',
                  fontSize: '0.85rem',
                  fontWeight: '600'
                }}>
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* 2. Concrete Project Suggestions */}
        {recs.project_suggestions?.length > 0 && (
          <div style={{ marginBottom: '24px' }}>
            <h4 style={{ fontSize: '0.95rem', fontWeight: '700', color: '#1e293b', marginBottom: '12px' }}>
              Recommended Hands-On Project Implementations:
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
              {recs.project_suggestions.map((proj, idx) => (
                <div key={idx} style={{
                  background: '#ffffff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '10px',
                  padding: '16px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.04)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <h5 style={{ fontSize: '0.95rem', fontWeight: '700', color: '#0f172a' }}>
                      {proj.title}
                    </h5>
                    <span className="badge badge-blue" style={{ fontSize: '0.72rem' }}>
                      {proj.difficulty || 'Intermediate'}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.85rem', color: '#475569', lineHeight: 1.5, marginBottom: '10px' }}>
                    {proj.why_relevant}
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {proj.skills_practiced?.map((sk, sIdx) => (
                      <span key={sIdx} style={{
                        background: '#f1f5f9',
                        color: '#334155',
                        borderRadius: '4px',
                        padding: '2px 6px',
                        fontSize: '0.75rem',
                        fontWeight: '500'
                      }}>
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 3. Learning Direction */}
        {recs.learning_direction?.length > 0 && (
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ fontSize: '0.92rem', fontWeight: '700', color: '#1e293b', marginBottom: '8px' }}>
              Suggested Learning Direction:
            </h4>
            <ul style={{ paddingLeft: '18px', fontSize: '0.88rem', color: '#334155', lineHeight: 1.6 }}>
              {recs.learning_direction.map((item, idx) => (
                <li key={idx} style={{ marginBottom: '4px' }}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {/* 4. Resume Phrasing & Improvements */}
        {recs.resume_improvements?.length > 0 && (
          <div>
            <h4 style={{ fontSize: '0.92rem', fontWeight: '700', color: '#1e293b', marginBottom: '8px' }}>
              Resume Improvement Suggestions:
            </h4>
            <ul style={{ paddingLeft: '18px', fontSize: '0.88rem', color: '#334155', lineHeight: 1.6 }}>
              {recs.resume_improvements.map((item, idx) => (
                <li key={idx} style={{ marginBottom: '4px' }}>{item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
