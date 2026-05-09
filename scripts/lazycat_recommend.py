#!/usr/bin/env python3
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request


APPSTORE_API = "https://appstore.api.lazycat.cloud/api/v3"
APPSTORE_CDN = "https://dl.lazycat.cloud/appstore/metarepo"
PLAYGROUND_API = "https://playground.api.lazycat.cloud/api"


def fetch_json(url, timeout=20):
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json,text/plain,*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.6",
            "Origin": "https://lazycat.cloud",
            "Referer": "https://lazycat.cloud/",
            "User-Agent": "lazycat-recommender-skill/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    return json.loads(data.decode("utf-8"))


def fetch_text(url, timeout=20):
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "text/plain,*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.6",
            "Origin": "https://lazycat.cloud",
            "Referer": "https://lazycat.cloud/",
            "User-Agent": "lazycat-recommender-skill/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8").strip()


def q(params):
    return urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})


def safe_get(d, path, default=None):
    cur = d
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def score_text(query, fields):
    query = (query or "").strip().lower()
    if not query:
        return 0
    terms = query_terms(query)
    score = 0
    text = "\n".join(str(x or "") for x in fields).lower()
    title = str(fields[0] or "").lower() if fields else ""
    for term in terms:
        if len(term) <= 1:
            continue
        if term in title:
            score += 8
        if term in text:
            score += 4
    if query in title:
        score += 10
    if query in text:
        score += 6
    return score


def query_terms(query):
    raw = [x for x in re.split(r"[\s,，;；/、|]+", query.lower()) if x]
    terms = set(raw)
    for token in raw:
        cjk = "".join(ch for ch in token if "\u4e00" <= ch <= "\u9fff")
        if len(cjk) >= 2:
            terms.update(cjk[i : i + 2] for i in range(len(cjk) - 1))
        latin = re.findall(r"[a-z0-9][a-z0-9.+_-]*", token)
        terms.update(latin)
    return sorted(terms, key=len, reverse=True)


def app_url(package):
    return f"https://lazycat.cloud/appstore/detail/{urllib.parse.quote(package)}"


def guide_url(guide_id):
    return f"https://lazycat.cloud/playground/guideline/{guide_id}"


def normalize_app(item, query):
    info = item.get("information") or {}
    version = item.get("version") or {}
    count = item.get("count") or {}
    rating = item.get("rating") or {}
    package = item.get("package") or version.get("package") or ""
    name = info.get("name") or package
    fields = [
        name,
        info.get("brief"),
        info.get("description"),
        info.get("keywords"),
        info.get("source"),
        package,
    ]
    return {
        "type": "app",
        "name": name,
        "package": package,
        "url": app_url(package) if package else "",
        "brief": info.get("brief") or "",
        "description": truncate(info.get("description") or "", 420),
        "keywords": info.get("keywords") or "",
        "version": version.get("name") or "",
        "downloads": count.get("downloads", 0),
        "rating": rating.get("score", 0),
        "comments": safe_get(rating, ["statistics", "total"], 0),
        "support_pc": bool(info.get("support_pc")),
        "support_mobile": bool(info.get("support_mobile")),
        "updated_at": item.get("updated_at") or item.get("version_updated_at") or "",
        "score": score_text(query, fields) + min(int(count.get("downloads") or 0), 5000) / 10000,
    }


def normalize_guide(item, query):
    title = item.get("title") or ""
    content = item.get("content") or ""
    fields = [
        title,
        content,
        " ".join(item.get("categories") or []),
        item.get("type"),
    ]
    return {
        "type": "guide",
        "title": title,
        "id": item.get("id"),
        "url": guide_url(item.get("id")),
        "summary": truncate(content, 520),
        "categories": item.get("categories") or [],
        "author": safe_get(item, ["user", "nickname"], "") or safe_get(item, ["user", "username"], ""),
        "created_at": item.get("createdAt") or "",
        "updated_at": item.get("updatedAt") or "",
        "views": item.get("views") or item.get("viewsTotal") or 0,
        "thumbs": item.get("thumbCount") or 0,
        "comments": item.get("commentCount") or 0,
        "score": score_text(query, fields) + min(int(item.get("views") or 0), 3000) / 10000,
    }


def truncate(text, max_len):
    text = " ".join(str(text).split())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "..."


def get_appstore_release():
    return fetch_text(f"{APPSTORE_CDN}/op/index")


def search_apps(keyword, category_id=0, size=20, page=0, sort="counting.desc"):
    params = {
        "category_ids": category_id,
        "sort": sort,
        "page": page,
        "size": size,
        "keyword": keyword or None,
    }
    return fetch_json(f"{APPSTORE_API}/user/app/list?{q(params)}")


def get_app_categories():
    return fetch_json(f"{APPSTORE_CDN}/zh/categories.json")


def get_guide_categories():
    return fetch_json(f"{PLAYGROUND_API}/workshop/guideline-category/list?size=100")


def search_guides(keyword, category_id=None, size=20, page=0, sort="-createdAt"):
    params = {
        "size": size,
        "sort": sort,
        "page": page,
        "keyword": keyword or None,
        "category_id": category_id,
    }
    return fetch_json(f"{PLAYGROUND_API}/workshop/guideline/list?{q(params)}")


def main():
    parser = argparse.ArgumentParser(description="Query Lazycat appstore and playground recommendation data.")
    parser.add_argument("query", nargs="*", help="User need / search keywords")
    parser.add_argument("--apps", type=int, default=8, help="Number of app candidates to return")
    parser.add_argument("--guides", type=int, default=8, help="Number of guide candidates to return")
    parser.add_argument("--app-category", type=int, default=0, help="Appstore category id, default 0")
    parser.add_argument("--guide-category", type=int, help="Playground guideline category id")
    parser.add_argument("--sort-apps", default="counting.desc", help="App sort, e.g. counting.desc or updated_at.desc")
    parser.add_argument("--sort-guides", default="-createdAt", help="Guide sort, e.g. -createdAt or -updatedAt")
    args = parser.parse_args()

    query_text = " ".join(args.query).strip()

    result = {
        "queried_at_unix": int(time.time()),
        "query": query_text,
        "sources": {
            "appstore": "https://lazycat.cloud/appstore/",
            "playground": "https://lazycat.cloud/playground/",
        },
        "counts": {},
        "categories": {},
        "apps": [],
        "guides": [],
        "errors": [],
    }

    try:
        release = get_appstore_release()
        result["appstore_release"] = release
    except Exception as exc:
        result["errors"].append(f"appstore release fetch failed: {exc}")

    try:
        app_total = search_apps("", category_id=0, size=0)
        result["counts"]["apps"] = app_total.get("total")
    except Exception as exc:
        result["errors"].append(f"app count fetch failed: {exc}")

    try:
        guide_total = search_guides("", size=0)
        result["counts"]["guides"] = guide_total.get("total")
    except Exception as exc:
        result["errors"].append(f"guide count fetch failed: {exc}")

    try:
        result["categories"]["apps"] = get_app_categories()
    except Exception as exc:
        result["errors"].append(f"app categories fetch failed: {exc}")

    try:
        result["categories"]["guides"] = (get_guide_categories().get("items") or [])
    except Exception as exc:
        result["errors"].append(f"guide categories fetch failed: {exc}")

    try:
        apps = search_apps(
            query_text,
            category_id=args.app_category,
            size=max(args.apps * 3, args.apps),
            sort=args.sort_apps,
        ).get("items") or []
        normalized = [normalize_app(x, query_text) for x in apps]
        result["apps"] = sorted(normalized, key=lambda x: x["score"], reverse=True)[: args.apps]
    except Exception as exc:
        result["errors"].append(f"app search failed: {exc}")

    try:
        guides = search_guides(
            query_text,
            category_id=args.guide_category,
            size=max(args.guides * 3, args.guides),
            sort=args.sort_guides,
        ).get("items") or []
        normalized = [normalize_guide(x, query_text) for x in guides]
        result["guides"] = sorted(normalized, key=lambda x: x["score"], reverse=True)[: args.guides]
    except Exception as exc:
        result["errors"].append(f"guide search failed: {exc}")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not result["errors"] else 2


if __name__ == "__main__":
    sys.exit(main())
