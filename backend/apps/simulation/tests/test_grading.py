"""
Tests for the LLM grading system.

OpenAI is never called in these tests; all LLM calls are mocked.
"""
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.simulation.models import Scenario, Run, Decision, DecisionGrade
from apps.simulation.services.grading import (
    build_grading_bundle,
    validate_grade_result,
    run_grading,
    GRADING_SCHEMA,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

VALID_GRADE_RESULT = {
    "rubric_version": "1.0",
    "overall_score": 3.2,
    "universal_score": 3.2,
    "dimension_scores": [
        {"key": "problem_framing", "score": 3, "reason": "Clear problem statement."},
        {"key": "tradeoffs", "score": 3, "reason": "Alternatives considered."},
        {"key": "evidence_assumptions", "score": 3, "reason": "Assumptions stated."},
        {"key": "execution_realism", "score": 3, "reason": "Realistic plan."},
        {"key": "metrics_success", "score": 4, "reason": "Good KPI definition."},
    ],
    "role_scores": [],
    "gates": {
        "has_clear_recommendation": True,
        "mentions_constraints": True,
        "mentions_success_metrics": True,
        "mentions_risks_and_mitigation": False,
        "compares_alternatives": True,
    },
    "strengths": ["Clear recommendation", "Good metric framing"],
    "improvements": ["Add risk mitigation", "Reference baseline data"],
    "red_flags": [],
    "confidence": 0.85,
}


def _make_scenario(name="Test Scenario"):
    return Scenario.objects.create(
        name=name,
        version=1,
        difficulty="beginner",
        context="Test context for grading.",
        config={
            "kpis": ["activation_rate"],
            "max_steps": 3,
            "initial_metrics": {"activation_rate": 50.0},
            "stakeholders": ["Engineering"],
            "prompts": {"0": "What is your first move?"},
        },
    )


def _make_run(user, scenario):
    return Run.objects.create(
        user=user,
        scenario=scenario,
        scenario_version=1,
        status="active",
        seed=42,
        step_number=1,
        state={"metrics": {"activation_rate": 52.0}},
    )


def _make_decision(run):
    return Decision.objects.create(
        run=run,
        step_number=0,
        decision_type="general",
        payload={"choice_id": "investigate", "assumptions": ["Users are confused"], "risks": []},
        rationale="I will investigate the drop by analysing funnel data and running user interviews.",
    )


# ── Unit tests: grading service ───────────────────────────────────────────────

class BuildGradingBundleTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bundleuser", password="pw")
        self.scenario = _make_scenario()
        self.run = _make_run(self.user, self.scenario)
        self.decision = _make_decision(self.run)

    def test_bundle_has_required_keys(self):
        bundle = build_grading_bundle(self.decision.id)
        for key in ("rubric_version", "scenario", "turn", "candidate_response", "run_state"):
            self.assertIn(key, bundle)

    def test_bundle_scenario_context_capped(self):
        self.scenario.context = "x" * 3000
        self.scenario.save()
        bundle = build_grading_bundle(self.decision.id)
        self.assertLessEqual(len(bundle["scenario"]["context"]), 2000)

    def test_bundle_candidate_response_fields(self):
        bundle = build_grading_bundle(self.decision.id)
        cr = bundle["candidate_response"]
        self.assertEqual(cr["rationale"], self.decision.rationale)
        self.assertEqual(cr["choice_id"], "investigate")
        self.assertIsInstance(cr["assumptions"], list)

    def test_bundle_rubric_version(self):
        bundle = build_grading_bundle(self.decision.id)
        self.assertEqual(bundle["rubric_version"], "1.0")


class ValidateGradeResultTest(TestCase):
    def test_valid_result_passes(self):
        # Should not raise
        validate_grade_result(VALID_GRADE_RESULT)

    def test_missing_required_field_raises(self):
        import jsonschema
        bad = dict(VALID_GRADE_RESULT)
        del bad["overall_score"]
        with self.assertRaises(jsonschema.ValidationError):
            validate_grade_result(bad)

    def test_score_out_of_range_raises(self):
        import jsonschema
        bad = json.loads(json.dumps(VALID_GRADE_RESULT))
        bad["overall_score"] = 6  # > 5
        with self.assertRaises(jsonschema.ValidationError):
            validate_grade_result(bad)

    def test_invalid_dimension_key_raises(self):
        import jsonschema
        bad = json.loads(json.dumps(VALID_GRADE_RESULT))
        bad["dimension_scores"][0]["key"] = "not_a_real_dimension"
        with self.assertRaises(jsonschema.ValidationError):
            validate_grade_result(bad)


class RunGradingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="gradeuser", password="pw")
        self.scenario = _make_scenario()
        self.run = _make_run(self.user, self.scenario)
        self.decision = _make_decision(self.run)

    @patch("apps.simulation.services.grading.grade_decision_with_openai")
    def test_run_grading_succeeded(self, mock_openai):
        mock_openai.return_value = VALID_GRADE_RESULT
        grade = run_grading(self.decision.id)
        self.assertEqual(grade.status, "succeeded")
        self.assertEqual(grade.result_json["overall_score"], 3.2)
        self.assertEqual(grade.decision_id, self.decision.id)
        self.assertEqual(grade.run_id, self.run.id)
        self.assertIsNotNone(grade.latency_ms)

    @patch("apps.simulation.services.grading.grade_decision_with_openai")
    def test_run_grading_failed_on_openai_error(self, mock_openai):
        mock_openai.side_effect = RuntimeError("OpenAI is down")
        grade = run_grading(self.decision.id)
        self.assertEqual(grade.status, "failed")
        self.assertIn("OpenAI is down", grade.error)
        self.assertIsNone(grade.result_json)

    @patch("apps.simulation.services.grading.grade_decision_with_openai")
    def test_run_grading_failed_on_schema_violation(self, mock_openai):
        bad_result = dict(VALID_GRADE_RESULT)
        del bad_result["overall_score"]
        mock_openai.return_value = bad_result
        grade = run_grading(self.decision.id)
        self.assertEqual(grade.status, "failed")


# ── API tests: permissions and endpoints ─────────────────────────────────────

class DecisionGradeAPITest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pw")
        self.other = User.objects.create_user(username="other", password="pw")
        self.scenario = _make_scenario()
        self.run = _make_run(self.owner, self.scenario)
        self.decision = _make_decision(self.run)
        self.client = APIClient()

    def _url(self):
        return f"/api/v1/decisions/{self.decision.id}/grade/"

    # GET ── 404 when no grade exists yet
    def test_get_grade_not_found(self):
        self.client.force_authenticate(user=self.owner)
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 404)

    # GET ── returns grade when one exists
    def test_get_grade_returns_latest(self):
        grade = DecisionGrade.objects.create(
            decision=self.decision,
            run=self.run,
            scenario=self.scenario,
            rubric_version="1.0",
            model_name="gpt-4o",
            temperature=0.2,
            status="succeeded",
            result_json=VALID_GRADE_RESULT,
        )
        self.client.force_authenticate(user=self.owner)
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["id"], str(grade.id))
        self.assertEqual(resp.data["status"], "succeeded")

    # GET ── 403 for non-owner
    def test_get_grade_permission_denied_for_non_owner(self):
        self.client.force_authenticate(user=self.other)
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 403)

    # GET ── 401 unauthenticated
    def test_get_grade_unauthenticated(self):
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 403)  # DRF returns 403 for session auth

    # POST ── triggers grading (mocked), returns succeeded grade
    @patch("apps.simulation.api.views.run_grading")
    def test_post_triggers_grading(self, mock_run_grading):
        grade = DecisionGrade.objects.create(
            decision=self.decision,
            run=self.run,
            scenario=self.scenario,
            rubric_version="1.0",
            model_name="gpt-4o",
            temperature=0.2,
            status="succeeded",
            result_json=VALID_GRADE_RESULT,
        )
        mock_run_grading.return_value = grade
        self.client.force_authenticate(user=self.owner)
        resp = self.client.post(self._url())
        self.assertEqual(resp.status_code, 200)
        mock_run_grading.assert_called_once_with(self.decision.id)

    # POST ── 403 for non-owner
    def test_post_grade_permission_denied_for_non_owner(self):
        self.client.force_authenticate(user=self.other)
        resp = self.client.post(self._url())
        self.assertEqual(resp.status_code, 403)

    # POST ── returns 422 when grading fails
    @patch("apps.simulation.api.views.run_grading")
    def test_post_returns_422_on_failed_grade(self, mock_run_grading):
        grade = DecisionGrade.objects.create(
            decision=self.decision,
            run=self.run,
            scenario=self.scenario,
            rubric_version="1.0",
            model_name="gpt-4o",
            temperature=0.2,
            status="failed",
            error="OpenAI timeout",
        )
        mock_run_grading.return_value = grade
        self.client.force_authenticate(user=self.owner)
        resp = self.client.post(self._url())
        self.assertEqual(resp.status_code, 422)
        self.assertEqual(resp.data["status"], "failed")
