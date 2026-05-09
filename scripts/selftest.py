#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "lazycat_recommend.py"


def run_case(query):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), query, "--apps", "5", "--guides", "5"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode not in (0, 2):
        raise AssertionError(f"script failed for {query!r}: {proc.stderr}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"invalid JSON for {query!r}: {exc}") from exc


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def test_remote_windows_guide_only():
    data = run_case("我要通过懒猫微服的内网穿透远程访问我的另外一台电脑")
    titles = [item["title"] for item in data["guides"]]
    assert_true(data["analysis"]["effective_mode"] == "guides", "remote-access query must be guide-only")
    assert_true(data["apps"] == [], "remote-access query must not include app recommendations")
    assert_true(titles, "remote-access query must return guide results")
    assert_true(titles[0] == "通过懒猫远程访问windows电脑", f"unexpected top guide: {titles[:3]}")


def test_vnc_does_not_pollute_apps():
    data = run_case("Lazycat VNC server")
    assert_true(data["analysis"]["effective_mode"] == "guides", "VNC query must be guide-first")
    assert_true(data["apps"] == [], "VNC query must not return generic app matches")
    assert_true(any("远程" in item["title"] or "VNC" in item["summary"] for item in data["guides"]), "VNC query must return remote-access guide evidence")


def test_app_name_uses_store_name():
    data = run_case("我想找一个相册管理应用")
    names = [item["name"] for item in data["apps"]]
    assert_true(data["analysis"]["effective_mode"] == "apps", "app-shopping query must be app-only")
    assert_true(names and names[0] == "懒猫相册", f"unexpected top app name: {names[:3]}")
    assert_true("cloud.lazycat" not in names[0].lower(), "app display name must not be package name")


def main():
    tests = [
        test_remote_windows_guide_only,
        test_vnc_does_not_pollute_apps,
        test_app_name_uses_store_name,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
