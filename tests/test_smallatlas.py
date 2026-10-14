import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from smallatlas.generator import MOODS, generate_world
from smallatlas.journal import Journal, render_markdown


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class GeneratorTests(unittest.TestCase):
    def test_same_seed_and_mood_produce_same_world(self) -> None:
        self.assertEqual(generate_world(271828, "misterius"), generate_world(271828, "misterius"))

    def test_each_mood_has_a_writing_prompt(self) -> None:
        for mood in MOODS:
            with self.subTest(mood=mood):
                self.assertTrue(generate_world(17, mood).writing_prompt)

    def test_unknown_mood_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Nuansa tidak dikenal"):
            generate_world(1, "riuh")

    def test_world_cards_are_populated(self) -> None:
        world = generate_world(5)
        for value in (world.place, world.law, world.resident, world.event):
            self.assertTrue(value.strip())


class JournalTests(unittest.TestCase):
    def test_save_load_and_markdown_export(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "worlds.json"
            journal = Journal(path)
            world = generate_world(42, "hangat")
            entry = journal.add("Kebun Senja", world.to_dict())

            self.assertEqual(journal.get(entry["id"]), entry)
            self.assertEqual(journal.entries(), [entry])
            self.assertIn("# Kebun Senja", render_markdown(entry))
            self.assertIn(world.place, render_markdown(entry))
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["entries"], [entry])

    def test_empty_title_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "Judul tidak boleh kosong"):
                Journal(Path(directory) / "worlds.json").add("  ", generate_world(2).to_dict())

    def test_corrupt_journal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "worlds.json"
            path.write_text("{not-json", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "bukan JSON yang valid"):
                Journal(path).entries()

    def test_missing_entry_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(KeyError, "tidak ditemukan"):
                Journal(Path(directory) / "worlds.json").get("missing")


class CliIntegrationTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(PROJECT_ROOT)
        return subprocess.run(
            [sys.executable, "-m", "smallatlas", *arguments],
            cwd=PROJECT_ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_save_list_show_and_export_flow(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            journal = str(Path(directory) / "worlds.json")
            saved = self.run_cli(
                "save", "--title", "Mercusuar Hujan", "--seed", "31415",
                "--mood", "puitis", "--journal", journal,
            )
            self.assertEqual(saved.returncode, 0, saved.stderr)
            match = re.search(r"Dunia disimpan: ([a-f0-9]{8})", saved.stdout)
            self.assertIsNotNone(match, saved.stdout)
            identifier = match.group(1)

            listing = self.run_cli("list", "--journal", journal)
            self.assertEqual(listing.returncode, 0, listing.stderr)
            self.assertIn("Mercusuar Hujan", listing.stdout)

            shown = self.run_cli("show", identifier, "--journal", journal)
            self.assertEqual(shown.returncode, 0, shown.stderr)
            self.assertIn("Aturan dunia", shown.stdout)
            self.assertIn("Seed: 31415", shown.stdout)

            output = Path(directory) / "export" / "world.md"
            exported = self.run_cli(
                "export", identifier, "--journal", journal, "--output", str(output)
            )
            self.assertEqual(exported.returncode, 0, exported.stderr)
            self.assertTrue(output.is_file())
            self.assertIn("# Mercusuar Hujan", output.read_text(encoding="utf-8"))

    def test_generate_command_runs_without_journal(self) -> None:
        result = self.run_cli("generate", "--seed", "123", "--mood", "hangat")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Seed: 123 | Nuansa: hangat", result.stdout)
        self.assertIn("Arah menulis", result.stdout)

    def test_invalid_mood_exits_with_usage_error(self) -> None:
        result = self.run_cli("generate", "--mood", "riuh")
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid choice", result.stderr)


if __name__ == "__main__":
    unittest.main()
