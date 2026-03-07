"""Unit tests for the pure simulation engine."""
from django.test import TestCase
from apps.simulation.engine import step_engine
from apps.simulation.engine.step import EngineInput


class EngineTestCase(TestCase):
    """Tests for the step engine."""

    def test_step_engine_produces_metrics(self):
        """Engine produces metrics for each KPI."""
        config = {
            "kpis": ["activation_rate", "retention_30d"],
            "max_steps": 5,
        }
        input_data = EngineInput(
            state={"step_number": 0, "metrics": {}},
            decision={"decision_type": "prioritization", "rationale": "Test"},
            config=config,
            step_number=0,
            seed=42,
        )
        output = step_engine(input_data)
        self.assertIn("activation_rate", output.metrics)
        self.assertIn("retention_30d", output.metrics)
        self.assertGreaterEqual(output.metrics["activation_rate"], 0)
        self.assertLessEqual(output.metrics["activation_rate"], 100)

    def test_step_engine_deterministic(self):
        """Same inputs produce same outputs."""
        config = {"kpis": ["kpi1"], "max_steps": 3}
        input_data = EngineInput(
            state={"step_number": 0},
            decision={"rationale": "Same"},
            config=config,
            step_number=1,
            seed=100,
        )
        out1 = step_engine(input_data)
        out2 = step_engine(input_data)
        self.assertEqual(out1.metrics, out2.metrics)

    def test_step_engine_completes_at_max_steps(self):
        """Engine sets is_complete when reaching max_steps."""
        config = {"kpis": ["k"], "max_steps": 2}
        input_data = EngineInput(
            state={"step_number": 1},
            decision={"rationale": "Final"},
            config=config,
            step_number=1,
            seed=1,
        )
        output = step_engine(input_data)
        self.assertTrue(output.is_complete)
