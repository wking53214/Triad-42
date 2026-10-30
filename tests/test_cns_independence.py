"""Triad+42 is independent of CNS, and these tests hold whether or not CNS is installed.

Most run in a fresh interpreter. Where ``cns`` is blocked outright
(``sys.modules['cns'] = None`` makes any import of it fail), the result does not
depend on what the test environment happens to contain. They never skip.
"""
import ast
import os
import pkgutil
import subprocess
import sys
import textwrap
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "triad42"
CONNECTOR = "triad42.cns_connector"
MODULES = sorted(f"triad42.{m.name}" for m in pkgutil.iter_modules([str(PACKAGE)]))
BLOCK = "import sys; sys.modules['cns'] = None; sys.modules['cns.gate'] = None\n"
ENV = {"PYTHONPATH": str(ROOT), "PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONDONTWRITEBYTECODE": "1"}
HINT = 'pip install -e ".[cns]"'
SESSION = """
    from triad42 import Label, LabeledItem, Session, Severity, SurfacingStatus
    session = Session()
    rp = session.start_pass(LabeledItem("The plan as written.", Label.ASSUMPTION))
    shown = rp.add_finding("Step 3 has no rollback.", Severity.HIGH, scope="plan")
    session.harvest(rp, surfaced_ids={shown.finding_id})
    output = [c for c in session.candidates.all() if c.status is SurfacingStatus.SURFACED][0]
"""


def run(code: str, *, block: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-c", (BLOCK if block else "") + textwrap.dedent(code)],
                          capture_output=True, text=True, env=ENV, timeout=120)


def ok(done: subprocess.CompletedProcess) -> None:
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip().endswith("ok"), done.stdout


def test_the_module_list_is_the_whole_package():
    assert CONNECTOR in MODULES and "triad42.review" in MODULES and len(MODULES) > 10


def test_importing_the_package_and_every_other_module_does_not_load_cns_even_when_it_is_installed():
    others = [m for m in MODULES if m != CONNECTOR]
    ok(run(f"""
        import importlib, sys
        import triad42
        for name in {others!r}:
            importlib.import_module(name)
        loaded = [m for m in sys.modules if m == "cns" or m.startswith("cns.") or m.startswith("cns_composition")]
        assert not loaded, loaded
        print('ok')
    """, block=False))


def test_importing_the_connector_does_not_load_cns_either():
    ok(run(f"""
        import sys
        import {CONNECTOR}
        loaded = [m for m in sys.modules if m == "cns" or m.startswith("cns.") or m.startswith("cns_composition")]
        assert not loaded, loaded
        print('ok')
    """, block=False))


def test_every_module_imports_with_cns_blocked():
    ok(run(f"""
        import importlib
        for name in {MODULES!r}:
            importlib.import_module(name)
        print('ok')
    """))


def test_the_connector_says_what_is_missing_when_cns_is_blocked():
    ok(run(SESSION + f"""
    from triad42.cns_connector import CnsNotInstalled, binds, cns_available, output_content, output_digest
    assert cns_available() is False
    assert output_content(output)["source"] == "triad42"   # plain data, no cns needed
    for call in (lambda: output_digest(output), lambda: binds(object(), output)):
        try:
            call()
        except CnsNotInstalled as e:
            assert {HINT!r} in str(e), str(e)
            assert isinstance(e, ImportError)
        else:
            raise SystemExit("ran without cns")
    print('ok')
    """))


def test_no_module_of_the_package_imports_cns_by_statement():
    offenders = {}
    for path in PACKAGE.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                [node.module] if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module else []
            bad = [n for n in names if n == "cns" or n.startswith(("cns.", "cns_composition"))]
            if bad:
                offenders.setdefault(str(path.relative_to(PACKAGE)), []).extend(bad)
    assert offenders == {}


def test_the_package_declares_no_runtime_dependency_and_pins_the_cns_extra():
    meta = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert meta["dependencies"] == []
    assert meta["optional-dependencies"]["cns"] == ["cns @ git+https://github.com/wking53214/CNS.git@v2.2.0"]
