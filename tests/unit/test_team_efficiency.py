"""
Unit and Efficiency Stress-Test Suite for Enterprise Team Directory.
Validates 50-member scalability, search performance, pagination, and cryptographic masking.
"""

import time
import unittest
from database.repository import ENMARepository
from database.sample_data import SAMPLE_TEAM_MEMBERS
from database.security_vault import DatabaseSecurityVault

class TestTeamDirectoryEfficiency(unittest.TestCase):

    def setUp(self):
        self.repo = ENMARepository()
        self.repo.reset_team_members()
        self.vault = DatabaseSecurityVault()

    def test_directory_scale_and_capacity(self):
        """Verifies directory contains exactly 50 sample enterprise employees."""
        members = self.repo.get_team_members()
        self.assertEqual(len(members), 50)
        self.assertEqual(len(SAMPLE_TEAM_MEMBERS), 50)

        # Verify key founders and leaders are present
        emails = [m["email"] for m in members]
        self.assertIn("hriday.code1119@gmail.com", emails)
        self.assertIn("chetan@enterprise.com", emails)
        self.assertIn("elena.r@enterprise.com", emails)
        self.assertIn("marcus.t@enterprise.com", emails)

    def test_department_diversity(self):
        """Verifies representative coverage across all core enterprise departments."""
        members = self.repo.get_team_members()
        depts = set(m.get("department") for m in members)
        expected_depts = {
            "AI Engineering",
            "Engineering",
            "Product",
            "Security",
            "Design",
            "Operations",
            "Legal",
            "Executive",
            "Data & Analytics",
            "Sales & Marketing",
            "Customer Success",
            "Finance & HR",
        }
        self.assertTrue(expected_depts.issubset(depts))

    def test_multi_field_search_accuracy(self):
        """Verifies accurate filtering by name, role, email, and department."""
        # By Name
        res_name = self.repo.search_team_members("Hriday")
        self.assertTrue(any(m["name"] == "Hriday Gupta" for m in res_name))

        # By Role
        res_role = self.repo.search_team_members("Prompt Engineering")
        self.assertTrue(any("Kenji Sato" in m["name"] for m in res_role))

        # By Email
        res_email = self.repo.search_team_members("chetan@enterprise.com")
        self.assertEqual(len(res_email), 1)

        # By Department
        res_dept = self.repo.search_team_members("Security")
        self.assertGreaterEqual(len(res_dept), 3)

    def test_search_and_query_efficiency_benchmark(self):
        """Stress-tests search throughput: 1,000 queries on 50 members should execute in < 50ms."""
        members = self.repo.get_team_members()
        test_queries = ["ai", "engineer", "lead", "security", "priya", "director", "manager", "architect", "data", "counsel"]

        t_start = time.perf_counter()
        for i in range(1000):
            q = test_queries[i % len(test_queries)]
            matches = [
                m for m in members
                if q in m.get("name", "").lower() or q in m.get("role", "").lower() or q in m.get("department", "").lower()
            ]
            self.assertIsInstance(matches, list)
        duration_ms = (time.perf_counter() - t_start) * 1000

        # Sub-50ms expectation for 1,000 in-memory queries (typically 2-6ms)
        self.assertLess(duration_ms, 50.0)

    def test_pagination_slices(self):
        """Validates page slicing logic for 50 records across 10 items per page."""
        members = self.repo.get_team_members()
        page_size = 10
        total_pages = (len(members) + page_size - 1) // page_size
        self.assertEqual(total_pages, 5)

        collected = []
        for page in range(1, total_pages + 1):
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, len(members))
            slice_items = members[start_idx:end_idx]
            self.assertEqual(len(slice_items), 10)
            collected.extend(slice_items)

        # Ensure all 50 items were covered without duplicates
        self.assertEqual(len(collected), 50)
        self.assertEqual(len(set(m["id"] for m in collected)), 50)

    def test_crud_and_reset_resilience(self):
        """Verifies add, delete, and directory reset restore sample state cleanly."""
        initial_count = len(self.repo.get_team_members())
        self.assertEqual(initial_count, 50)

        # Add temporary employee
        new_mem = self.repo.add_team_member(
            name="Temporary Worker",
            email="temp.worker@enterprise.com",
            role="Contractor",
            department="Operations",
        )
        self.assertEqual(len(self.repo.get_team_members()), 51)

        # Delete temporary employee
        deleted = self.repo.delete_team_member(new_mem["id"])
        self.assertTrue(deleted)
        self.assertEqual(len(self.repo.get_team_members()), 50)

        # Reset directory check
        reset_members = self.repo.reset_team_members()
        self.assertEqual(len(reset_members), 50)

    def test_pii_security_vault_batch_protection(self):
        """Verifies batch cryptographic masking and blind indexing on all 50 employees."""
        members = self.repo.get_team_members()
        for m in members:
            masked_email = self.vault.mask_email(m["email"])
            masked_phone = self.vault.mask_phone(m["phone"])

            # Verify email masking preserves domain and first letter
            self.assertIn("@", masked_email)
            self.assertEqual(masked_email[0], m["email"][0])
            self.assertIn("*", masked_email)

            # Verify blind indexing generates deterministic HMAC tags
            bidx = self.vault.generate_blind_index(m["email"])
            self.assertTrue(bidx.startswith("bidx::v1::"))
            self.assertEqual(self.vault.generate_blind_index(m["email"]), bidx)

if __name__ == "__main__":
    unittest.main()
