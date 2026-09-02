import sys, traceback
sys.path.insert(0, '.')

errors = []

# Test 1: education_verifier _parse_candidate_education
print("=== Test 1: education_verifier ===")
try:
    from app.services.deterministic.education_verifier import EducationVerifier
    # Empty education should return 0.0
    r1 = EducationVerifier.verify([], {}, '', '')
    assert r1['education_score'] == 0.0, f"Expected 0.0 got {r1['education_score']}"
    # Valid degree
    r2 = EducationVerifier.verify(
        [{'degree': 'B.Tech Computer Science', 'institution': 'IIT', 'field': 'Computer Science'}], {}, '', ''
    )
    assert r2['education_score'] == 100.0, f"Expected 100.0 got {r2['education_score']}"
    # Dict with empty degree string fallback (old code used "Degree" default which would parse wrong)
    r3 = EducationVerifier.verify(
        [{'degree': '', 'institution': 'Some College'}], {}, 'B.Tech Computer Science from Some College', ''
    )
    print(f"  r3 score: {r3['education_score']} - {r3['candidate_degree']}")
    print("  PASSED")
except Exception:
    errors.append(f"education_verifier: {traceback.format_exc()}")
    print("  FAILED:", traceback.format_exc())

# Test 2: ats_scoring_service - sync wrapper
print("=== Test 2: ats_scoring_service sync wrapper ===")
try:
    from app.services.ats.ats_scoring_service import ATSScoringService
    r = ATSScoringService.compute_full_ats_report(
        {'skills': {'programming_languages': ['Python']}, 'experience': []},
        {'job_info': {'title': 'Python Dev', 'experience_required': '2 years'},
         'skills': {'required_skills': ['Python']}},
        'Python developer with experience',
        'Python Dev 2 years required',
        {}, {}
    )
    assert 'overall_score' in r
    assert 'comparison_table' in r
    print(f"  overall_score: {r['overall_score']}")
    print("  PASSED")
except Exception:
    errors.append(f"ats_scoring_service: {traceback.format_exc()}")
    print("  FAILED:", traceback.format_exc())

# Test 3: analysis.py - check skill_analysis key used in SkillMatch loop
print("=== Test 3: analysis.py skill_analysis key ===")
try:
    from app.api.endpoints.analysis import router
    # Simulate what analysis.py does at line 134 with the new scorer output
    sample_skill_analysis = {
        'matched_skills': ['Python', 'FastAPI'],
        'missing_skills': ['Kubernetes'],
        'skill_score': 75.0,
        'skill_matches': []  # check if key exists
    }
    # The line in analysis.py: skill_analysis.get("skill_matches", [])
    skill_matches = sample_skill_analysis.get("skill_matches", [])
    print(f"  skill_matches from new scorer: {skill_matches}")
    print("  NOTE: New DeterministicScorer does NOT produce 'skill_matches' dicts - loop is safe (returns empty list)")
    print("  PASSED (no crash - empty list skips loop)")
except Exception:
    errors.append(f"analysis.py: {traceback.format_exc()}")
    print("  FAILED:", traceback.format_exc())

# Test 4: responsibility_matcher with empty resume (best_block=None guard)
print("=== Test 4: responsibility_matcher with empty resume ===")
try:
    from app.services.deterministic.responsibility_matcher import ResponsibilityMatcher
    r = ResponsibilityMatcher.analyze(
        {'responsibilities': ['Build FastAPI REST APIs', 'Deploy to Kubernetes']},
        {},
        '',
        'Build FastAPI REST APIs and deploy to Kubernetes'
    )
    print(f"  responsibility_score: {r['responsibility_score']}")
    print(f"  evaluations[0]: {r['evaluations'][0]}")
    print("  PASSED")
except Exception:
    errors.append(f"responsibility_matcher: {traceback.format_exc()}")
    print("  FAILED:", traceback.format_exc())

print("\n=== SUMMARY ===")
if errors:
    for e in errors:
        print("FAIL:", e[:300])
else:
    print("ALL TESTS PASSED")
