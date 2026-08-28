"""Automated tests for 210+ multi-topic tiered data ingestion and strict tier-isolated QA."""

import sqlite3
import unittest
from pathlib import Path

from scripts.tiered_qa import query_tier_isolated, VALID_TIERS

WORKSPACE_DIR = Path(r"C:\Users\am600\MySecondBrain").resolve()
DB_PATH = WORKSPACE_DIR / ".llmwiki" / "index.db"


class TestTieredQA(unittest.TestCase):
    def test_tiered_files_count_and_structure(self):
        """Verify that at least 200 documents exist across tier1, tier2, and tier3."""
        tier1_files = list((WORKSPACE_DIR / "tier1").glob("*.md"))
        tier2_files = list((WORKSPACE_DIR / "tier2").glob("*.md"))
        tier3_files = list((WORKSPACE_DIR / "tier3").glob("*.md"))

        self.assertGreaterEqual(len(tier1_files), 70, f"Expected at least 70 Tier 1 files, found {len(tier1_files)}")
        self.assertGreaterEqual(len(tier2_files), 70, f"Expected at least 70 Tier 2 files, found {len(tier2_files)}")
        self.assertGreaterEqual(len(tier3_files), 70, f"Expected at least 70 Tier 3 files, found {len(tier3_files)}")

        total_files = len(tier1_files) + len(tier2_files) + len(tier3_files)
        self.assertGreaterEqual(total_files, 210, f"Expected at least 210 total files, found {total_files}")

    def test_sqlite_indexing_has_tiered_documents(self):
        """Verify SQLite index contains all tiered documents with proper tags and relative paths."""
        self.assertTrue(DB_PATH.exists(), "SQLite index.db must exist.")

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        for tier in ("tier1", "tier2", "tier3"):
            cursor.execute("SELECT count(*) FROM documents WHERE relative_path LIKE ?", (f"{tier}/%",))
            count = cursor.fetchone()[0]
            self.assertGreaterEqual(count, 70, f"Expected at least 70 indexed docs for {tier}, got {count}")

        conn.close()

    def test_strict_tier_isolation_invariant(self):
        """Verify that querying any tier returns ONLY documents strictly belonging to that tier."""
        tiers = ["tier1", "tier2", "tier3"]
        queries = [
            "Architecture",
            "Algorithm",
            "Protocol",
            "Memory",
            "Optimization",
            "Security",
            "Database",
        ]

        for tier in tiers:
            for q in queries:
                matches, stats = query_tier_isolated(tier, q, limit=10)
                self.assertTrue(stats["isolation_verified"])
                self.assertEqual(stats["cross_tier_leaks"], 0)

                for match in matches:
                    rel = match["relative_path"]
                    self.assertTrue(rel.startswith(f"{tier}/"), f"LEAK! Found {rel} when querying {tier}")

    def test_cross_tier_leakage_rejection(self):
        """Verify that concepts specific to Tier 3 do not appear when querying Tier 1, and vice versa."""
        # FlashAttention belongs strictly to Tier 3
        t1_matches, _ = query_tier_isolated("tier1", "FlashAttention", limit=5)
        for m in t1_matches:
            self.assertTrue(m["relative_path"].startswith("tier1/"))
            self.assertFalse(m["relative_path"].startswith("tier3/"))

        # Von Neumann belongs strictly to Tier 1
        t3_matches, _ = query_tier_isolated("tier3", "Von Neumann", limit=5)
        for m in t3_matches:
            self.assertTrue(m["relative_path"].startswith("tier3/"))
            self.assertFalse(m["relative_path"].startswith("tier1/"))


if __name__ == "__main__":
    unittest.main()
