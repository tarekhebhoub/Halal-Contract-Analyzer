"""Smoke tests for the analyzer engine (no LLM, deterministic)."""
from django.test import TestCase, override_settings

from apps.analyzer.engine import analyze_clause
from apps.analyzer.scoring import aggregate_score


@override_settings(LLM_ENABLED=False, OPENAI_API_KEY="")
class EngineTests(TestCase):
    def test_riba_high_risk(self):
        clause = "The borrower shall pay interest at an annual percentage rate (APR) of 8% on outstanding balances, with compound interest accruing monthly."
        result = analyze_clause(clause)
        self.assertEqual(result.category, "riba")
        self.assertEqual(result.risk_level, "high")
        self.assertTrue(result.evidences)

    def test_gambling_high_risk(self):
        clause = "Profits from spread-betting and binary options on commodity prices shall be shared 50/50."
        result = analyze_clause(clause)
        self.assertEqual(result.category, "maysir")
        self.assertEqual(result.risk_level, "high")

    def test_innocuous_clause(self):
        clause = "This Agreement shall be governed by and construed in accordance with the laws of the State."
        result = analyze_clause(clause)
        self.assertEqual(result.risk_level, "none")
        self.assertEqual(result.evidences, [])

    def test_aggregate_score(self):
        class C:
            def __init__(self, r):
                self.risk_level = r

        self.assertEqual(aggregate_score([]), 0)
        score = aggregate_score([C("high"), C("medium"), C("none"), C("low")])
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)
