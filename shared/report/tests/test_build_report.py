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


def test_invalid_junit_xml_exits_1_with_a_message(tmp_path, capsys):
    report_path = write_project(tmp_path, make_report())
    (tmp_path / "junit.xml").write_text("<testsuite>")

    code = build_report.main([str(report_path), "--junit", str(tmp_path / "junit.xml"), "--root", str(tmp_path)])

    assert code == 1
    assert "Could not read the inputs" in capsys.readouterr().err


def test_missing_report_file_exits_1_with_a_message(tmp_path, capsys):
    code = build_report.main([str(tmp_path / "gone.json")])

    assert code == 1
    assert "Could not read the inputs" in capsys.readouterr().err


def test_invalid_report_json_exits_1_with_a_message(tmp_path, capsys):
    (tmp_path / "report.json").write_text("{")

    code = build_report.main([str(tmp_path / "report.json")])

    assert code == 1
    assert "Could not read the inputs" in capsys.readouterr().err


def test_null_tests_and_sections_are_treated_as_empty(tmp_path):
    code, out = build(tmp_path, make_report(tests=None, sections=None), "--formats", "html")

    assert code == 0


def test_null_defects_with_a_failing_test_is_a_validation_error(tmp_path, capsys):
    code, out = build(tmp_path, make_report(defects=None))

    assert code == 1
    assert "test_broken_edge failed but is not listed in defects[]" in capsys.readouterr().err


def test_istanbul_unknown_percentage_shows_n_a(tmp_path):
    unknown = {"lines": {"total": 0, "covered": 0, "pct": "Unknown"}, "branches": {"total": 0, "covered": 0, "pct": "Unknown"}}
    (tmp_path / "coverage-summary.json").write_text(json.dumps({"total": unknown, "src/empty.js": unknown}))

    code, out = build(tmp_path, make_report(), "--formats", "html", "--coverage", str(tmp_path / "coverage-summary.json"))

    assert code == 0
    assert '<td class="n nw">n/a</td><td class="n nw">n/a</td>' in (out / "report.html").read_text()


def test_nested_suites_do_not_double_count_duration(tmp_path):
    report_path = write_project(tmp_path, make_report(tests=[], defects=[]))
    (tmp_path / "junit.xml").write_text("""<testsuites>
  <testsuite name="outer" time="3.0">
    <testcase classname="outer" name="test_outer" time="1.0"/>
    <testsuite name="inner" time="2.0"><testcase classname="inner" name="test_inner" time="2.0"/></testsuite>
  </testsuite>
</testsuites>""")

    cases, suites = build_report.parse_junit([tmp_path / "junit.xml"])

    assert sum(s["time"] for s in suites) == 3.0


def test_usage_error_exits_1(tmp_path):
    with pytest.raises(SystemExit) as exit_info:
        build_report.main(["--no-such-flag"])

    assert exit_info.value.code == 1


def test_empty_formats_list_exits_1(tmp_path):
    report_path = write_project(tmp_path, make_report())

    with pytest.raises(SystemExit) as exit_info:
        build_report.main([str(report_path), "--formats", ","])

    assert exit_info.value.code == 1


def test_copying_inputs_never_overwrites_another_input(tmp_path):
    report_path = write_project(tmp_path, make_report())
    out = tmp_path / "out"
    out.mkdir()
    (out / "junit-1.xml").write_text('<testsuite name="second"><testcase classname="b" name="test_other"/></testsuite>')

    code = build_report.main([str(report_path), "--junit", str(tmp_path / "junit.xml"), "--junit", str(out / "junit-1.xml"),
                              "--root", str(tmp_path), "--out", str(out), "--formats", "summary"])

    assert code == 0
    assert 'name="rates"' in (out / "junit-1.xml").read_text()
    assert 'name="second"' in (out / "junit-2.xml").read_text()


def test_junit_files_from_an_earlier_run_are_removed(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "junit-1.xml").write_text(JUNIT)
    (out / "junit-2.xml").write_text(JUNIT)

    code, out = build(tmp_path, make_report(), "--formats", "summary")

    assert sorted(p.name for p in out.iterdir()) == ["junit.xml", "summary.html"]


def test_traceability_without_junit_says_no_junit(tmp_path):
    report_path = write_project(tmp_path, make_report())
    out = tmp_path / "out"

    code = build_report.main([str(report_path), "--root", str(tmp_path), "--out", str(out), "--formats", "html"])

    assert code == 0
    assert '<span class="s-muted">no JUnit</span>' in (out / "report.html").read_text()


def test_ci_lists_an_undocumented_failure_and_forces_the_verdict_to_fail(tmp_path):
    code, out = build(tmp_path, make_report(defects=[]), "--ci", "--formats", "html,summary")

    html = (out / "report.html").read_text()
    summary = (out / "summary.html").read_text()
    assert code == 0
    assert "<h2>Undocumented results</h2>" in html
    assert '<b class="s-fail">fail</b>The verdict is fail because this run has 1 failing' in html
    assert ">fail</b> The verdict is fail because this run has 1 failing" in summary


def test_ci_lists_a_traced_test_missing_from_junit_without_failing_the_verdict(tmp_path):
    code, out = build(tmp_path, make_report(tests=[make_test(test="test_band_price_old")]), "--ci", "--formats", "html")

    html = (out / "report.html").read_text()
    assert code == 0
    assert "not in JUnit" in html
    assert '<b class="s-warn">conditional</b>' in html


def test_ci_still_rejects_a_bad_location(tmp_path, capsys):
    code, out = build(tmp_path, make_report(tests=[make_test(location="tests/test_gone.py:1")]), "--ci")

    assert code == 1
    assert "file tests/test_gone.py does not exist" in capsys.readouterr().err


def test_an_input_with_a_stale_name_is_not_deleted(tmp_path):
    report_path = write_project(tmp_path, make_report())
    out = tmp_path / "out"
    out.mkdir()
    (out / "junit-2.xml").write_text(JUNIT)

    code = build_report.main([str(report_path), "--junit", str(out / "junit-2.xml"),
                              "--root", str(tmp_path), "--out", str(out), "--formats", "summary"])

    assert code == 0
    assert sorted(p.name for p in out.iterdir()) == ["junit-2.xml", "junit.xml", "summary.html"]
