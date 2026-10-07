import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("manual", ROOT / "scripts" / "manual.py")
manual = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(manual)


class ManualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.example = json.loads((ROOT / "scheme" / "example.manual.json").read_text(encoding="utf-8"))

    def test_example_validates_and_builds(self):
        expanded = manual.expand_placeholders(copy.deepcopy(self.example), self.example)
        errors, warnings = manual.validate(expanded)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        output = manual.build_html(expanded)
        self.assertIn("Orbit Notes Manual", output)
        self.assertIn("tests/offline-edit.spec.ts", output)
        self.assertIn("What it does", output)

    def test_duplicate_ids_are_errors(self):
        data = copy.deepcopy(self.example)
        data["sections"][0]["entries"][1]["id"] = "local-notebooks"
        errors, _ = manual.validate(data)
        self.assertTrue(any("duplicate ID" in error for error in errors))

    def test_unknown_related_id_is_a_warning(self):
        data = copy.deepcopy(self.example)
        data["sections"][0]["entries"][0]["related"] = ["missing-entry"]
        errors, warnings = manual.validate(data)
        self.assertEqual(errors, [])
        self.assertTrue(any("unknown ID" in warning for warning in warnings))

    def test_todo_is_an_error(self):
        errors, _ = manual.validate(manual.starter("Example"))
        self.assertTrue(any("placeholder text" in error for error in errors))

    def test_overrides_and_placeholders(self):
        data = copy.deepcopy(self.example)
        manual.apply_override(data, "project.version=3.5.0")
        expanded = manual.expand_placeholders(data, copy.deepcopy(data))
        self.assertEqual(expanded["manual"]["badges"][0], "Release 3.5.0")

    def test_build_command_writes_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "manual.html"
            result = manual.run_build(ROOT / "scheme" / "example.manual.json", output, [])
            self.assertEqual(result, 0)
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
