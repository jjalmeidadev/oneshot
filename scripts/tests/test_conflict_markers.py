"""Exercita o gate e o hook em indices Git descartaveis, sem tocar no repo."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SH = shutil.which("sh") or "C:/Program Files/Git/bin/sh.exe"


class ConflictMarkersTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.env = os.environ.copy()
        # Hooks podem herdar o indice/repositorio do commit que os chamou.
        for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            self.env.pop(name, None)
        self.git("init", "-b", "ci/test-gate")
        (self.repo / "scripts").mkdir()
        (self.repo / ".githooks").mkdir()
        for relative in ("scripts/check-conflict-markers.sh", ".githooks/pre-commit"):
            shutil.copyfile(ROOT / relative, self.repo / relative)
        self.git("add", ".")

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.repo, env=self.env,
            text=True, capture_output=True, check=True,
        )

    def stage(self, content):
        (self.repo / "arquivo com espacos.txt").write_bytes(content)
        self.git("add", "arquivo com espacos.txt")

    def run_gate_and_hook(self, expected):
        for script in ("scripts/check-conflict-markers.sh", ".githooks/pre-commit"):
            with self.subTest(script=script):
                result = subprocess.run(
                    [SH, script], cwd=self.repo, env=self.env,
                    text=True, capture_output=True,
                )
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                if expected:
                    self.assertIn("marcadores de conflito", result.stderr)

    def test_rejects_each_marker_with_lf_and_crlf(self):
        for marker in (b"<" * 7 + b" HEAD", b"=" * 7, b">" * 7 + b" branch"):
            for newline in (b"\n", b"\r\n"):
                with self.subTest(marker=marker, newline=newline):
                    self.stage(marker + newline)
                    self.run_gate_and_hook(1)

    def test_accepts_pytest_output_and_embedded_examples(self):
        self.stage(b"=" * 16 + b" 10 passed\nExemplo: " + b"<" * 7 + b" HEAD\n")
        self.run_gate_and_hook(0)

    def test_rejects_separator_with_whitespace(self):
        self.stage(b"=" * 7 + b" \t\r\n")
        self.run_gate_and_hook(1)

    def test_reads_staged_content_even_when_worktree_is_resolved(self):
        self.stage(b"<" * 7 + b" HEAD\n")
        (self.repo / "arquivo com espacos.txt").write_text("resolvido\n")
        self.run_gate_and_hook(1)

    def test_ignores_unstaged_and_untracked_markers(self):
        self.stage(b"resolvido\n")
        (self.repo / "arquivo com espacos.txt").write_bytes(b"<" * 7 + b" HEAD\n")
        (self.repo / "nao-rastreado.txt").write_bytes(b">" * 7 + b" branch\n")
        self.run_gate_and_hook(0)

    def test_accepts_deleted_file_and_binary(self):
        self.stage(b"<" * 7 + b" HEAD\n")
        self.git("rm", "--cached", "arquivo com espacos.txt")
        (self.repo / "binario.dat").write_bytes(b"\0\n" + b"=" * 7 + b"\n")
        self.git("add", "binario.dat")
        self.run_gate_and_hook(0)

    def test_fails_when_git_cannot_read_repository(self):
        with tempfile.TemporaryDirectory() as empty:
            result = subprocess.run(
                [SH, str(ROOT / "scripts/check-conflict-markers.sh")],
                cwd=empty, env=self.env, text=True, capture_output=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("nao foi possivel verificar", result.stderr)


if __name__ == "__main__":
    unittest.main()
