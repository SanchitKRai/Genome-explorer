"""Phase 2 tests: FASTA parsing, validation, POST /api/analyze, N-base handling, and 100kb speed."""
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import create_app


class TestPhase2Analyze(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.client = TestClient(self.app)
        self.sample_dir = Path(__file__).resolve().parent.parent.parent / "sample_data"

    def test_analyze_clean_dna_and_lazy_complements(self) -> None:
        res = self.client.post(
            "/api/analyze",
            json={
                "sequence_id": "test_seq",
                "sequence": "atg gca taa\n",
                "include_complements": False,
            },
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["length"], 9)
        self.assertEqual(data["counts"], {"A": 4, "T": 2, "G": 2, "C": 1, "N": 0})
        self.assertEqual(data["gc_percent"], 33.33)
        self.assertEqual(data["at_percent"], 66.67)
        self.assertGreater(data["molecular_weight_da"], 2700.0)
        self.assertIsNone(data["complement"])
        self.assertIsNone(data["reverse_complement"])

        # Now request lazy complements
        res_comp = self.client.post(
            "/api/analyze",
            json={
                "sequence_id": "test_seq",
                "sequence": "ATGGCATAA",
                "include_complements": True,
            },
        )
        self.assertEqual(res_comp.status_code, 200)
        comp_data = res_comp.json()
        self.assertEqual(comp_data["complement"], "TACCGTATT")
        self.assertEqual(comp_data["reverse_complement"], "TTATGCCAT")

    def test_analyze_ambiguous_n_bases_excludes_n_from_gc_and_mw(self) -> None:
        fasta_text = (self.sample_dir / "ambiguous_n_bases.fasta").read_text(encoding="utf-8")
        res = self.client.post("/api/analyze", json={"sequence": fasta_text})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["id"], "clinical_amplicon_with_N|length=240bp")
        self.assertEqual(data["counts"]["N"], 10)
        self.assertIn("10 N bases excluded", data["molecular_weight_note"])
        self.assertAlmostEqual(data["gc_percent"] + data["at_percent"], 100.0, places=1)

    def test_multi_record_fasta_dropdown_and_selection(self) -> None:
        fasta_text = (self.sample_dir / "multi_record_operon.fasta").read_text(encoding="utf-8")
        res1 = self.client.post("/api/analyze", json={"sequence": fasta_text})
        self.assertEqual(res1.status_code, 200)
        d1 = res1.json()
        self.assertEqual(len(d1["records"]), 2)
        second_id = d1["records"][1]["id"]

        res2 = self.client.post(
            "/api/analyze",
            json={"sequence": fasta_text, "sequence_id": second_id},
        )
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["id"], second_id)

    def test_reject_rna_u_with_clear_message(self) -> None:
        res = self.client.post("/api/analyze", json={"sequence": "ATGGCUAAC"})
        self.assertEqual(res.status_code, 400)
        err = res.json()["error"]
        self.assertEqual(err["code"], "RNA_DETECTED")
        self.assertIn("position 6", err["message"])
        self.assertIn("RNA", err["message"])

    def test_reject_invalid_character_with_exact_position(self) -> None:
        res = self.client.post("/api/analyze", json={"sequence": "ATGGCAT$AA"})
        self.assertEqual(res.status_code, 400)
        err = res.json()["error"]
        self.assertEqual(err["code"], "INVALID_BASE")
        self.assertIn("'$'", err["message"])
        self.assertIn("position 8", err["message"])

    def test_reject_sequence_over_100k_bp(self) -> None:
        huge = "A" * 100_001
        res = self.client.post("/api/analyze", json={"sequence": huge})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["error"]["code"], "SEQUENCE_TOO_LONG")

    def test_100kb_analysis_completes_under_2_seconds(self) -> None:
        seq_100k = ("ATGCGTACGT" * 10_000)  # 100,000 bp
        t0 = time.perf_counter()
        res = self.client.post("/api/analyze", json={"sequence": seq_100k})
        elapsed = time.perf_counter() - t0
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["length"], 100_000)
        self.assertLess(elapsed, 2.0, f"100kb analysis took {elapsed:.2f}s (> 2.0s limit)")


if __name__ == "__main__":
    unittest.main()
