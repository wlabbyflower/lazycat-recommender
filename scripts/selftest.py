#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "lazycat_recommend.py"


def run_case(query):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), query, "--apps", "8", "--guides", "8"],
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


def names(data):
    return [item["name"] for item in data["apps"]]


def titles(data):
    return [item["title"] for item in data["guides"]]


def packages(data):
    return [item["package"] for item in data["apps"]]


def guide_ids(data):
    return [item["id"] for item in data["guides"]]


CASES = [
    {
        "name": "公众号更新监控推荐应用",
        "query": "我想要监控一下公众号，某个公众号，你帮我推荐一下懒猫商店里面的应用",
        "mode": "apps",
        "must_packages": ["community.lazycat.app.we-rss"],
        "forbid_packages": ["in.zhaoj.lazycatonlinedevice", "lazycat.app.hertzbeat", "white.lazycat.app.nezha-v1"],
    },
    {
        "name": "公众号 RSS 订阅",
        "query": "我想订阅微信公众号更新并生成 RSS",
        "mode": "both",
        "must_any_package": ["community.lazycat.app.we-rss", "dev.libr.wewerss", "cloud.lazycat.app.rsshub"],
    },
    {
        "name": "公众号历史文章下载",
        "query": "我想批量下载某个微信公众号的历史文章",
        "mode": "both",
        "must_packages": ["cloud.lazycat.app.wxmp"],
    },
    {
        "name": "公众号文章搜索 MCP",
        "query": "我需要搜索微信公众号文章并接入 MCP",
        "mode": "both",
        "must_packages": ["com.wbsu2003.weixin-search-mcp"],
    },
    {
        "name": "公众号排版不是监控",
        "query": "我想写公众号文章并做 Markdown 排版",
        "mode": "both",
        "must_any_name_contains": ["公众号", "Markdown", "WeMD"],
    },
    {
        "name": "远程访问 Windows 电脑",
        "query": "我要通过懒猫微服的内网穿透远程访问我的另外一台电脑",
        "mode": "guides",
        "must_first_title": "通过懒猫远程访问windows电脑",
        "apps_empty": True,
    },
    {
        "name": "VNC 远程控制",
        "query": "Lazycat VNC server",
        "mode": "guides",
        "apps_empty": True,
        "must_title_contains": "远程",
    },
    {
        "name": "智慧屏攻略只返回攻略",
        "query": "还有吗？我想要智慧屏的攻略呀",
        "mode": "guides",
        "apps_empty": True,
        "must_first_guide_id": 569,
        "must_first_title": "懒猫微服怎么大屏看电视",
        "must_guide_product": "cloud.lazycat.app.lzctvcontroller",
    },
    {
        "name": "智慧屏应用首选官方应用",
        "query": "我想找懒猫智慧屏应用",
        "mode": "apps",
        "must_first_package": "cloud.lazycat.app.lzctvcontroller",
        "must_first_name": "懒猫智慧屏",
    },
    {
        "name": "相册管理应用",
        "query": "我想找一个相册管理应用",
        "mode": "apps",
        "must_first_name": "懒猫相册",
    },
    {
        "name": "照片备份方案",
        "query": "我想搭一个照片备份和相册管理",
        "mode": "both",
        "must_packages": ["cloud.lazycat.app.photo"],
        "must_title_contains": "相册",
    },
    {
        "name": "影视库应用",
        "query": "我想看电影和管理影视库，推荐懒猫商店应用",
        "mode": "apps",
        "must_any_name_contains": ["视频", "Plex", "Jellyfin", "Emby"],
    },
    {
        "name": "远程访问服务攻略",
        "query": "我需要远程访问家里的服务",
        "mode": "guides",
        "apps_empty": True,
        "must_title_contains": "远程",
    },
    {
        "name": "密码管理应用",
        "query": "我想在懒猫上管理密码，推荐应用",
        "mode": "apps",
        "must_any_name_contains": ["Bitwarden", "Vaultwarden", "密码"],
    },
    {
        "name": "RSS 阅读器应用",
        "query": "我想搭 RSS 阅读器，推荐懒猫应用",
        "mode": "apps",
        "must_any_name_contains": ["RSS", "FreshRSS", "Miniflux", "Tiny Tiny RSS"],
    },
    {
        "name": "BT 下载应用",
        "query": "我想离线下载 BT 种子，推荐应用",
        "mode": "apps",
        "must_any_name_contains": ["qBittorrent", "Transmission", "Deluge"],
    },
    {
        "name": "网盘文件管理应用",
        "query": "我想要网盘和文件管理，推荐应用",
        "mode": "apps",
        "must_any_name_contains": ["懒猫网盘", "Nextcloud", "Alist", "AList"],
    },
    {
        "name": "笔记知识库应用",
        "query": "我想搭建个人笔记和知识库，推荐应用",
        "mode": "apps",
        "must_any_name_contains": ["思源", "Outline", "Wiki", "笔记"],
    },
    {
        "name": "AI 助手应用",
        "query": "我想部署 AI 助手或者聊天机器人，推荐应用",
        "mode": "apps",
        "must_any_name_contains": ["小龙猫", "OpenClaw", "LangBot", "AI"],
    },
    {
        "name": "博客建站应用",
        "query": "我想搭个人博客网站，推荐应用",
        "mode": "apps",
        "must_any_name_contains": ["WordPress", "Halo", "博客", "Blog"],
    },
    {
        "name": "数据库管理应用",
        "query": "我想管理 MySQL 或 PostgreSQL 数据库，推荐应用",
        "mode": "apps",
        "must_any_name_contains": ["NocoDB", "数据库", "PostgreSQL", "MySQL"],
    },
    {
        "name": "端口监控不要推荐公众号",
        "query": "我想监控服务器端口和服务在线状态，推荐应用",
        "mode": "apps",
        "must_any_name_contains": ["监控", "Uptime", "Watch", "HertzBeat", "Nezha"],
        "forbid_packages": ["community.lazycat.app.we-rss", "dev.libr.wewerss"],
    },
]


def assert_case(case):
    data = run_case(case["query"])
    actual_mode = data["analysis"]["effective_mode"]
    assert_true(actual_mode == case["mode"], f"{case['name']}: mode {actual_mode!r} != {case['mode']!r}")

    app_names = names(data)
    app_packages = packages(data)
    guide_titles = titles(data)

    if case.get("apps_empty"):
        assert_true(data["apps"] == [], f"{case['name']}: expected no app results, got {app_names[:3]}")

    if "must_first_title" in case:
        assert_true(guide_titles and guide_titles[0] == case["must_first_title"], f"{case['name']}: unexpected first guide {guide_titles[:3]}")

    if "must_first_guide_id" in case:
        ids = guide_ids(data)
        assert_true(ids and ids[0] == case["must_first_guide_id"], f"{case['name']}: unexpected first guide id {ids[:3]}")

    if "must_title_contains" in case:
        needle = case["must_title_contains"]
        assert_true(any(needle in title for title in guide_titles), f"{case['name']}: no guide title contains {needle!r}: {guide_titles[:5]}")

    if "must_first_name" in case:
        assert_true(app_names and app_names[0] == case["must_first_name"], f"{case['name']}: unexpected first app {app_names[:3]}")

    if "must_first_package" in case:
        assert_true(app_packages and app_packages[0] == case["must_first_package"], f"{case['name']}: unexpected first package {app_packages[:3]}")

    if "must_guide_product" in case:
        expected_product = case["must_guide_product"]
        linked_products = [
            product
            for guide in data["guides"]
            for product in guide.get("products", [])
        ]
        assert_true(expected_product in linked_products, f"{case['name']}: missing linked product {expected_product}; got {linked_products[:8]}")

    for package in case.get("must_packages", []):
        assert_true(package in app_packages, f"{case['name']}: missing package {package}; got {app_packages[:8]}")

    for package in case.get("forbid_packages", []):
        assert_true(package not in app_packages[:5], f"{case['name']}: forbidden package {package} appeared in top results")

    if "must_any_package" in case:
        expected = set(case["must_any_package"])
        assert_true(bool(expected.intersection(app_packages)), f"{case['name']}: none of {sorted(expected)} in {app_packages[:8]}")

    if "must_any_name_contains" in case:
        needles = case["must_any_name_contains"]
        joined = "\n".join(app_names[:8])
        assert_true(any(needle.lower() in joined.lower() for needle in needles), f"{case['name']}: none of {needles} in {app_names[:8]}")


def main():
    for index, case in enumerate(CASES, 1):
        assert_case(case)
        print(f"PASS {index:02d} {case['name']}")
    print(f"PASS all {len(CASES)} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
