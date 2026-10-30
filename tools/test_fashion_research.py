"""Offline research integrity and retrieval tests; no backend/database imports."""
from datetime import date
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from fashion_research import DEEP_FILE, REGISTRY_FILE, ResearchError, load_corpus


def collections():
    sources = [{"source_id": "S1", "title": "Atelier notes", "publisher": "Test Atelier",
                "source_type": "house_collection_notes", "url": "https://example.org/collection",
                "rights_status": "research_reference_only"},
               {"source_id": "S2", "title": "Museum object", "publisher": "Test Museum",
                "source_type": "museum_object", "url": "https://example.org/object",
                "rights_status": "CC0"}]
    records = [{"id": "F1", "kind": "source_supported_observation", "observation": "Defined waist tailoring",
                "source_ids": ["S1"], "concept_area": "silhouette", "concept_key": "waist_definition",
                "critical_counterpoint": "Waistless design is also intentional.", "proposed_engine_implication": "Ask for intent.",
                "review_status": "expert_review_required", "confidence_in_factual_claim": "moderate"},
               {"id": "F2", "kind": "source_supported_observation", "observation": "Waistless silhouette",
                "source_ids": ["S2"], "concept_area": "silhouette", "concept_key": "body_ease",
                "critical_counterpoint": "Defined waist is another valid intention.", "proposed_engine_implication": "Preserve both.",
                "review_status": "expert_review_required", "confidence_in_factual_claim": "moderate"}]
    deep = {"version": "0.2-research-expansion", "research_date": "2026-10-30", "sources": sources,
            "research_records": records,
            "counterexample_tests": [{"id": "T1", "name": "Opposite intentions", "given": "Two briefs",
                                      "expectation": "Allow both silhouettes", "supporting_records": ["F1", "F2"]}],
            "dialectical_comparisons": [{"id": "D1", "tension": "Defined vs loose", "pole_a": "Structure",
                                         "pole_b": "Ease", "sources": ["S1", "S2"], "design_consequence": "Compare intentions",
                                         "status": "research_hypothesis"}],
            "fusion_studies": [{"id": "X1", "fusion": "Tailoring and sportswear", "components": ["tailoring", "sportswear"],
                                "research_question": "Can contrast serve the brief?", "counterargument": "Context matters",
                                "status": "research_hypothesis"}],
            "statistics": {"source_count": 2, "research_observation_count": 2, "evaluation_scenarios": 1,
                           "dialectical_comparisons": 1, "fusion_hypotheses": 1}}
    registry = {"version": "0.1", "as_of": "2026-10-30", "current_directory_candidate_count": 2,
                "raw_source_entry_count": 2,
                "sources": {"S1": {"title": "Directory", "type": "official_industry_member_directory",
                                    "url": "https://example.org/directory", "license": "Reference only"}},
                "candidates": [{"name": name, "aliases": [], "source_ids": ["S1"],
                                "research_status": "directory_candidate_unverified",
                                "entity_type": "brand_or_designer_pending_disambiguation",
                                "design_claims": [], "collection_claims": [], "verification_needed": ["identity", "usage_rights"]}
                               for name in ("Élan Atelier", "Atelier B")]}
    return deep, registry


class FashionResearchTests(unittest.TestCase):
    def setUp(self):
        self.directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.deep, self.registry = collections()
        self.write_inputs()

    def write_inputs(self):
        for filename, data in ((DEEP_FILE, self.deep), (REGISTRY_FILE, self.registry)):
            (self.directory / filename).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8-sig")

    def corpus(self):
        self.write_inputs()
        return load_corpus(self.directory, as_of=date(2026, 10, 30))

    def codes(self):
        return {item["code"] for item in self.corpus().report()["findings"]}

    def test_both_shapes_are_indexed_with_distinct_source_namespaces(self):
        corpus = self.corpus()
        self.assertEqual(corpus.report()["errors"], 0)
        self.assertEqual(corpus.report()["counts"]["entries"], 7)
        self.assertEqual(corpus.report()["counts"]["sources"], 3)
        self.assertEqual(corpus.search("Élan", kind="candidate")["results"][0]["sources"][0]["key"], "registry:S1")
        self.assertEqual(corpus.search("defined waist", kind="observation")["results"][0]["sources"][0]["key"], "deep:S1")

    def test_query_retains_counterpoints_rights_and_uncertainty(self):
        result = self.corpus().search("defined waist", kind="observation", area="silhouette")["results"][0]
        self.assertEqual(result["data"]["critical_counterpoint"], "Waistless design is also intentional.")
        self.assertEqual(result["verification"], "not_independently_verified")
        self.assertEqual(result["training_use"], "not_cleared")
        self.assertEqual(result["sources"][0]["declared_rights"], "research_reference_only")
        self.assertEqual(result["sources"][0].get("publisher"), "Test Atelier")
        self.assertIn("publisher_self_description", result["caveats"])

    def test_search_is_unicode_aware_bounded_and_combines_filters(self):
        corpus = self.corpus()
        self.assertEqual(corpus.search("ELAN", kind="candidate")["matched"], 1)
        self.assertEqual(corpus.search("not present")["matched"], 0)
        result = corpus.search("", kind="candidate", status="directory_candidate_unverified", source="registry:S1", limit=1)
        self.assertEqual(result["matched"], 2)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result, corpus.search("", kind="candidate", status="directory_candidate_unverified", source="registry:S1", limit=1))
        for value in (0, 101):
            with self.assertRaises(ValueError):
                corpus.search(limit=value)
        with self.assertRaises(ValueError):
            corpus.search(source="deep:unknown")

    def test_raw_verified_and_cc0_labels_never_grant_identity_or_training_clearance(self):
        self.registry["candidates"][0]["research_status"] = "identity_verified"
        self.registry["sources"]["S1"]["license"] = "CC0"
        corpus = self.corpus()
        result = corpus.search("elan")["results"][0]
        self.assertEqual(result["declared_status"], "identity_verified")
        self.assertEqual(result["verification"], "not_independently_verified")
        self.assertEqual(result["training_use"], "not_cleared")
        self.assertEqual(corpus.report()["counts"]["verified_brands"], 0)
        self.assertEqual(corpus.report()["counts"]["training_cleared"], 0)

    def test_directory_entries_are_candidates_not_confirmed_entity_types(self):
        self.assertEqual(self.corpus().report()["counts"].get("candidate"), 2)

    def test_duplicate_names_and_aliases_are_flagged_without_merging(self):
        self.registry["candidates"][0]["aliases"] = ["ATELIER-B"]
        corpus = self.corpus()
        self.assertIn("identity_collision", {item["code"] for item in corpus.report()["findings"]})
        self.assertEqual(corpus.search(kind="candidate")["matched"], 2)

    def test_duplicate_urls_are_not_counted_as_independent_sources(self):
        self.deep["sources"][1]["url"] = self.deep["sources"][0]["url"] + "#details"
        self.assertIn("duplicate_source_url", self.codes())

    def test_supplied_publisher_must_be_attributable_text(self):
        self.registry["sources"]["S1"]["publisher"] = 42
        self.assertGreater(self.corpus().report()["errors"], 0)

    def test_missing_source_or_record_references_block_queries(self):
        for section, field, bad in (("research_records", "source_ids", "missing"),
                                    ("dialectical_comparisons", "sources", "missing"),
                                    ("counterexample_tests", "supporting_records", "missing")):
            with self.subTest(section=section):
                self.deep, self.registry = collections()
                self.deep[section][0][field] = [bad]
                corpus = self.corpus()
                self.assertGreater(corpus.report()["errors"], 0)
                with self.assertRaises(ResearchError):
                    corpus.search()
        self.deep, self.registry = collections()
        self.registry["candidates"][0]["source_ids"] = ["missing"]
        self.assertIn("unknown_source", self.codes())

    def test_duplicate_ids_wrong_types_and_misleading_counts_are_errors(self):
        self.deep["research_records"][1]["id"] = "F1"
        self.registry["candidates"][0]["aliases"] = "not-a-list"
        self.registry["current_directory_candidate_count"] = 99
        self.assertTrue({"duplicate_id", "invalid_field", "count_mismatch"}.issubset(self.codes()))

    def test_missing_dates_context_and_unverified_status_remain_quality_warnings(self):
        codes = self.codes()
        self.assertTrue({"source_dates_missing", "context_missing", "review_required", "discovery_only"}.issubset(codes))
        self.deep["research_date"] = "2026-11-01"
        self.assertIn("future_date", self.codes())

    def test_unsafe_and_invalid_source_urls_are_rejected_without_fetching(self):
        for url in ("https://user:password@example.org/", "http://127.0.0.1/x", "https://[::1]/", "file:///tmp/data", "not a URL"):
            with self.subTest(url=url):
                self.deep["sources"][0]["url"] = url
                self.assertIn("invalid_source_url", self.codes())

    def test_strict_json_limits_and_malformed_containers_fail_cleanly(self):
        path = self.directory / DEEP_FILE
        valid = json.dumps(self.deep)
        for suffix in (',"extra":1,"extra":2}', ',"extra":NaN}', ',"extra":1e999}'):
            with self.subTest(suffix=suffix):
                path.write_text(valid[:-1] + suffix, encoding="utf-8")
                with self.assertRaises(ResearchError):
                    load_corpus(self.directory)
        for text in ('{broken', '[]'):
            with self.subTest(text=text):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(ResearchError):
                    load_corpus(self.directory)
        self.write_inputs()
        with patch("fashion_research.MAX_FILE_BYTES", 4):
            with self.assertRaises(ResearchError):
                load_corpus(self.directory)
        self.deep["sources"] = {}
        self.write_inputs()
        with self.assertRaises(ResearchError):
            load_corpus(self.directory)

    def test_scenarios_keep_links_and_are_not_claimed_as_executed_benchmarks(self):
        result = self.corpus().search(kind="scenario")["results"][0]
        self.assertEqual(result["related_records"], ["deep:observation:F1", "deep:observation:F2"])
        self.assertIn("proposed_benchmark_not_executed", result["caveats"])
        self.assertEqual(self.corpus().search(kind="fusion")["results"][0]["verification"], "not_independently_verified")

    def test_offline_execution_preserves_input_bytes_and_needs_no_network(self):
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.directory.iterdir()}
        with patch("socket.socket", side_effect=AssertionError("Network forbidden")):
            corpus = load_corpus(self.directory)
            self.assertEqual(corpus.search("waistless")["matched"], 2)
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.directory.iterdir()}
        self.assertEqual(before, after)

    def test_cli_exit_codes_and_json_output(self):
        command = [sys.executable, "-B", str(Path(__file__).with_name("fashion_research.py")),
                   "--research-dir", str(self.directory)]
        for arguments, want in ((["validate"], 0), (["validate", "--strict"], 1),
                                (["query", "elan", "--kind", "candidate"], 0)):
            result = subprocess.run([*command, *arguments], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, want, result.stderr)
            self.assertIsInstance(json.loads(result.stdout), dict)
        (self.directory / DEEP_FILE).write_text("{broken", encoding="utf-8")
        result = subprocess.run([*command, "validate"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2)
        self.assertIn("error", json.loads(result.stdout))


if __name__ == "__main__":
    unittest.main()
