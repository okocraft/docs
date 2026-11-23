"""Behavioral tests for the deterministic comment candidate inventory."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "inventory_comments.py"


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)

    def write(self, name, text):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "--", name], check=True)

    def scan(self, *args):
        p = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(p.stdout)

    def test_multiline_trailing_strings_and_go_raw(self):
        self.write(
            "src/A.java",
            'String url = "https://example.org/a"; // actual\n/* several\n lines */\nString s = "/*not a comment*/";\n/** Docs */\n',
        )
        self.write(
            "src/main.go",
            "package main\nconst s = `// not comment ${x /* also raw text */}`\n//go:build linux\n// real\n",
        )
        self.write(
            "src/ui.ts",
            'const s = `ignored // text ${value /* interpolation */}`;\nconst url = "https://x"; // real\n',
        )
        data = self.scan()
        c = data["candidates"]
        java = [x for x in c if x["path"] == "src/A.java"]
        self.assertEqual(
            [(x["start_line"], x["end_line"], x["kind"]) for x in java],
            [(1, 1, "line"), (2, 3, "block"), (5, 5, "block")],
        )
        self.assertIn("documentation-candidate", java[2]["hints"])
        go = [x for x in c if x["path"] == "src/main.go"]
        self.assertEqual(len(go), 2)
        self.assertIn("tool-directive", go[0]["hints"])
        ts = [x for x in c if x["path"] == "src/ui.ts"]
        self.assertEqual(
            [(x["start_line"], x["kind"]) for x in ts], [(1, "block"), (2, "line")]
        )

    def test_build_and_config_comments_and_exclusions(self):
        self.write("build.gradle.kts", "plugins {\n // plugin note\n}\n")
        self.write("go.mod", "module x\nrequire y v1.2.3 // indirect\n")
        self.write("pom.xml", "<project><!-- explanation\n next line --></project>")
        self.write("gradle/libs.versions.toml", "timeout = 30 # reason\n")
        self.write("Makefile", "build: # inline reason\n\t@echo ok\n")
        self.write("scripts/run.sh", "#!/bin/sh\nvalue=1 # current reason\n")
        self.write("node_modules/dep/a.ts", "// skip")
        self.write("target/generated.java", "// skip")
        self.write("src/new.generated.ts", "// skip")
        data = self.scan()
        seen = {x["path"] for x in data["candidates"]}
        self.assertEqual(
            seen,
            {
                "build.gradle.kts",
                "go.mod",
                "pom.xml",
                "gradle/libs.versions.toml",
                "Makefile",
                "scripts/run.sh",
            },
        )
        self.assertEqual(len(data["excluded_files"]), 3)
        self.assertIn(
            "tool-directive",
            next(x for x in data["candidates"] if x["path"] == "scripts/run.sh")[
                "hints"
            ],
        )
        self.assertEqual(
            [
                x["text"]
                for x in data["candidates"]
                if x["path"] == "gradle/libs.versions.toml"
            ],
            ["# reason"],
        )

    def test_scope_determinism_and_tracked_only(self):
        self.write("src/a.ts", "// tracked\n")
        self.write("build.gradle", "// tracked build\n")
        (self.repo / "src/untracked.ts").write_text("// not tracked\n")
        data = self.scan("--path", "src")
        self.assertEqual(data["scanned_files"], ["src/a.ts"])
        self.assertEqual(len(data["candidates"]), 1)
        self.assertEqual(data, self.scan("--path", "src"))

    def test_path_normalization_and_missing_scope_failures(self):
        self.write("src/a.ts", "// tracked\n")
        self.write("build.gradle", "// tracked build\n")
        self.assertEqual(self.scan("--path", "./src")["scanned_files"], ["src/a.ts"])
        self.assertEqual(
            self.scan("--path", "src/../src")["scanned_files"], ["src/a.ts"]
        )
        self.assertEqual(
            self.scan("--path", ".")["scanned_files"], ["build.gradle", "src/a.ts"]
        )
        self.assertEqual(
            self.scan("--path", "./")["scanned_files"], ["build.gradle", "src/a.ts"]
        )
        for missing in ("./missing", "docs", "../outside", "/absolute"):
            with self.subTest(path=missing):
                proc = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--repo",
                        str(self.repo),
                        "--path",
                        missing,
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertNotEqual(proc.returncode, 0)
                self.assertIn("error:", proc.stderr)

    def test_unterminated_block_candidate_flags_incomplete_scan(self):
        self.write(
            "src/pattern.ts",
            "const pattern = /[/*]/;\n\n// Important: initialization order matters.\ninitialize();\n",
        )
        result_path = self.repo / "inventory.json"
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--repo",
                str(self.repo),
                "--path",
                "./src",
                "--output",
                str(result_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("WARNING: src/pattern.ts:1:", proc.stderr)
        self.assertIn("scan warnings", proc.stdout)
        data = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual(data["scope"], ["src"])
        self.assertEqual(len(data["scan_warnings"]), 1)
        warning = data["scan_warnings"][0]
        self.assertEqual((warning["path"], warning["line"]), ("src/pattern.ts", 1))
        self.assertIn("Manually inspect", warning["reason"])
        self.assertEqual(data["scanned_files"], ["src/pattern.ts"])

    def test_unterminated_real_block_comment_also_warns(self):
        self.write("src/a.java", "class A { /* accidental unclosed comment\n")
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(self.repo)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(len(json.loads(proc.stdout)["scan_warnings"]), 1)


if __name__ == "__main__":
    unittest.main()
