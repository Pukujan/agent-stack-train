from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".github/scripts"))

import oio_installer  # noqa: E402
import oio_record  # noqa: E402

SESSION = "agent:codex/0b8e1c2a-7f3d-4e5a-9b6c-1d2e3f4a5b6c"


class RecordTests(unittest.TestCase):
    """The writer stamps the repository it runs in, never a constant (#98)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.top = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.top, check=True)
        self.remote("https://github.com/Example-org/widget.git")
        (self.top / ".oio/ontology").mkdir(parents=True)
        (self.top / ".oio/ontology/project.json").write_text(json.dumps({"version": "1.0.0", "extends": {"version": "1.1.0"}}))
        (self.top / ".oio/schemas/v1").mkdir(parents=True)
        (self.top / ".oio/schemas/v1/issue-log-record.schema.json").write_text(
            (ROOT / "schemas/v1/issue-log-record.schema.json").read_text()
        )

    def tearDown(self):
        self.tmp.cleanup()

    def remote(self, url):
        subprocess.run(["git", "remote", "remove", "origin"], cwd=self.top, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", url], cwd=self.top, check=True)

    def write(self, *extra):
        out, err = io.StringIO(), io.StringIO()
        argv = ["--filer", SESSION, "--consequence", "Release notes skip a commit", "--affected", "release job", *extra]
        with mock.patch.object(oio_record.Path, "cwd", return_value=self.top), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = oio_record.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_the_record_names_this_repository_and_this_agent(self):
        code, out, err = self.write()
        self.assertEqual(code, 0, err)
        record = json.loads(out)
        self.assertEqual(record["project"], {"id": "Example-org/widget", "repository": "Example-org/widget"})
        self.assertEqual(record["filer"]["destination_repository"], "Example-org/widget")
        self.assertEqual(record["filer"]["content_author"], SESSION)
        self.assertEqual(record["filer"]["session_reference"], SESSION)
        self.assertEqual(record["filer"]["origin"], "agent-initiated")
        self.assertIsNone(record["filer"]["directing_human"])
        self.assertEqual(record["ontology"], {"default_version": "1.1.0", "project_version": "1.0.0"})

    def test_an_ssh_remote_gives_the_same_destination(self):
        self.remote("git@github.com:Example-org/widget.git")
        code, out, _ = self.write()
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["filer"]["destination_repository"], "Example-org/widget")

    def test_the_record_matches_the_schema(self):
        from jsonschema import Draft202012Validator

        _, out, _ = self.write("--impact-band", "moderate", "--likelihood", "observed")
        schema = json.loads((ROOT / "schemas/v1/issue-log-record.schema.json").read_text())
        Draft202012Validator(schema).validate(json.loads(out))

    def test_a_person_filing_is_not_a_session(self):
        code, out, _ = self.write("--filer", "Pukujan")
        self.assertEqual(code, 0)
        filer = json.loads(out)["filer"]
        self.assertEqual((filer["origin"], filer["session_reference"]), ("human-direct", None))

    def test_a_directed_log_must_name_who_directed_it(self):
        code, _, err = self.write("--origin", "human-via-agent")
        self.assertEqual(code, 2)
        self.assertIn("--directing-human", err)

    def test_a_made_up_filer_is_refused(self):
        code, _, err = self.write("--filer", "legal graphrag demo")
        self.assertEqual(code, 2)
        self.assertIn("--filer", err)

    def test_no_github_remote_means_no_record(self):
        self.remote("/srv/git/widget.git")
        code, out, err = self.write()
        self.assertEqual((code, out), (2, ""))
        self.assertIn("destination", err)

    def test_without_jsonschema_the_required_fields_are_still_checked(self):
        schema = json.loads((ROOT / "schemas/v1/issue-log-record.schema.json").read_text())
        record = json.loads(self.write()[1])
        self.assertEqual(oio_record.missing_fields(record, schema), [])
        del record["filer"]["destination_repository"]
        self.assertEqual(oio_record.missing_fields(record, schema), ["filer.destination_repository"])

    def test_the_writer_is_installed_into_adopters(self):
        self.assertIn(".github/scripts/oio_record.py", oio_installer.PACKAGE_FILES)


if __name__ == "__main__":
    unittest.main()
