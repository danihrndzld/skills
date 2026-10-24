import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build_report  # noqa: E402

FIXTURE = Path(__file__).parent / "fixture"

TEST_FILE = """def test_band_price():  # R-1
    assert True


def test_broken_edge():
    assert False
"""

# Bare <testsuite> root: 3 passed, 1 failed, 1 skipped.
JUNIT = """<?xml version="1.0" encoding="utf-8"?>
<testsuite name="rates" tests="5">
  <testcase classname="tests.test_rates" name="test_band_price" time="0.01"/>
  <testcase classname="tests.test_rates" name="test_light_parcel" time="0.01"/>
  <testcase classname="tests.test_rates" name="test_heavy_parcel" time="0.01"/>
  <testcase classname="tests.test_rates" name="test_broken_edge" time="0.01">
    <failure message="assert 1800 == 900">trace</failure>
  </testcase>
  <testcase classname="tests.test_rates" name="test_future_rule" time="0"><skipped/></testcase>
</testsuite>
"""

ISTANBUL = {
    "total": {"lines": {"total": 40, "covered": 30, "pct": 75}, "branches": {"total": 8, "covered": 6, "pct": 62.5}},
    "src/rates.js": {"lines": {"total": 40, "covered": 30, "pct": 75}, "branches": {"total": 8, "covered": 6, "pct": 62.5}},
}


def make_test(**overrides):
    return {"id": "R-1", "test": "test_band_price", "location": "tests/test_rates.py:1", "covers": "Band price", **overrides}


def make_defect(**overrides):
    return {"id": "D-1", "test": "test_broken_edge", "location": "tests/test_rates.py:5", "severity": "high",
            "expected": "900", "actual": "1800", "analysis": "Off by one band.", **overrides}


def make_report(**overrides):
    report = {
        "title": "Unit test review of rates",
        "meta": {"date": "2026-10-24"},
        "summary": "<p>Summary.</p>",
        "verdict": {"status": "conditional", "text": "Fix D-1."},
        "tests": [make_test()],
        "defects": [make_defect()],
    }
    return {**report, **overrides}


def write_project(tmp_path, report):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_rates.py").write_text(TEST_FILE)
    (tmp_path / "junit.xml").write_text(JUNIT)
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(report))
    return report_path


def build(tmp_path, report, *extra):
    report_path = write_project(tmp_path, report)
    out = tmp_path / "out"
    code = build_report.main([str(report_path), "--junit", str(tmp_path / "junit.xml"),
                              "--root", str(tmp_path), "--out", str(out), *extra])
    return code, out


def test_html_shows_run_counts_taken_from_junit(tmp_path):
    code, out = build(tmp_path, make_report(), "--formats", "html")

    html = (out / "report.html").read_text()
    assert code == 0
    assert '<td class="n nw">5</td><td class="n nw">3</td><td class="n nw">1</td><td class="n nw">0</td><td class="n nw">1</td>' in html


def test_html_marks_the_failing_traced_test_as_failed(tmp_path):
    report = make_report(tests=[make_test(), make_test(id="R-2", test="test_broken_edge", location="tests/test_rates.py:5")])

    code, out = build(tmp_path, report, "--formats", "html")

    assert '<span class="s-fail">failed</span>' in (out / "report.html").read_text()


def test_html_escapes_the_title(tmp_path):
    code, out = build(tmp_path, make_report(title="Rates <script>"), "--formats", "html")

    assert "<h1>Rates &lt;script&gt;</h1>" in (out / "report.html").read_text()


def test_summary_has_no_style_tag(tmp_path):
    code, out = build(tmp_path, make_report(), "--formats", "summary")

    assert "<style" not in (out / "summary.html").read_text()


def test_istanbul_coverage_shows_line_and_branch_percentages(tmp_path):
    (tmp_path / "coverage-summary.json").write_text(json.dumps(ISTANBUL))

    code, out = build(tmp_path, make_report(), "--formats", "html", "--coverage", str(tmp_path / "coverage-summary.json"))

    assert '<td class="n nw">75.0%</td><td class="n nw">62.5%</td>' in (out / "report.html").read_text()


def test_missing_test_file_is_rejected(tmp_path, capsys):
    code, out = build(tmp_path, make_report(tests=[make_test(location="tests/test_gone.py:1")]))

    assert code == 1
    assert "file tests/test_gone.py does not exist" in capsys.readouterr().err


def test_location_on_the_wrong_line_is_rejected(tmp_path, capsys):
    code, out = build(tmp_path, make_report(tests=[make_test(location="tests/test_rates.py:5")]))

    assert code == 1
    assert "do not contain 'test_band_price'" in capsys.readouterr().err


def test_test_missing_from_junit_is_rejected(tmp_path, capsys):
    code, out = build(tmp_path, make_report(tests=[make_test(test="test_not_in_junit")]))

    assert code == 1
    assert "'test_not_in_junit' matches 0 JUnit test cases" in capsys.readouterr().err


def test_junit_failure_missing_from_defects_is_rejected(tmp_path, capsys):
    code, out = build(tmp_path, make_report(defects=[]))

    assert code == 1
    assert "tests.test_rates.test_broken_edge failed but is not listed in defects[]" in capsys.readouterr().err


def test_unknown_verdict_status_is_rejected(tmp_path, capsys):
    code, out = build(tmp_path, make_report(verdict={"status": "ok", "text": "Fine."}))

    assert code == 1
    assert "verdict.status is 'ok'" in capsys.readouterr().err


def test_validate_only_writes_nothing(tmp_path):
    code, out = build(tmp_path, make_report(), "--validate-only")

    assert code == 0
    assert not out.exists()


def test_formats_writes_only_the_requested_outputs(tmp_path):
    code, out = build(tmp_path, make_report(), "--formats", "summary")

    assert sorted(p.name for p in out.iterdir()) == ["junit.xml", "summary.html"]


@pytest.mark.skipif(build_report.find_chrome() is None, reason="no Chrome found")
def test_pdf_is_written_when_chrome_exists(tmp_path):
    code, out = build(tmp_path, make_report(), "--formats", "pdf")

    assert code == 0
    assert (out / "report.pdf").read_bytes().startswith(b"%PDF")


def test_fixture_report_passes_validation():
    code = build_report.main([str(FIXTURE / "report.json"), "--junit", str(FIXTURE / "junit.xml"),
                              "--coverage", str(FIXTURE / "coverage.json"), "--root", str(FIXTURE), "--validate-only"])

    assert code == 0
