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

FILLER_PHRASES = [
    "我想",
    "我要",
    "我需要",
    "帮我",
    "给我",
    "推荐",
    "找一个",
    "有没有",
    "可以",
    "能够",
    "实现",
    "懒猫",
    "微服",
    "应用",
    "软件",
    "攻略",
    "文章",
    "教程",
    "怎么",
    "如何",
    "什么",
    "一个",
    "一下",
    "相关",
    "需求",
    "lazycat",
    "lazy cat",
    "microserver",
    "micro server",
]

INTENT_TERM_GROUPS = [
    ("相册", "照片", "图片", "图像", "手机照片", "photo", "photos", "immich"),
    ("备份", "同步", "迁移", "恢复", "上传", "云端", "保存", "存储", "backup", "sync"),
    ("网盘", "云盘", "文件", "共享", "存储", "alist", "nextcloud"),
    ("下载", "离线下载", "磁力", "bt", "种子", "qbittorrent", "transmission", "aria2"),
    ("影音", "电影", "视频", "媒体库", "播放器", "jellyfin", "emby", "plex"),
    ("音乐", "歌单", "音频", "navidrome", "audiobookshelf"),
    ("阅读", "电子书", "rss", "rsshub", "miniflux", "书库"),
    ("笔记", "文档", "知识库", "wiki", "notion", "outline", "思源"),
    ("密码", "密钥", "凭据", "bitwarden", "vaultwarden", "passkey"),
    ("内网穿透", "远程访问", "反向代理", "frp", "cloudflare", "tailscale", "zerotier", "ddns"),
    ("远程桌面", "远程控制", "电脑", "windows", "rdp", "vnc", "3389", "被控端", "控制端", "netmap"),
    ("网站", "博客", "建站", "主页", "wordpress", "typecho", "halo"),
    ("代码", "git", "仓库", "gitea", "gitlab", "code-server", "vscode"),
    ("数据库", "mysql", "postgres", "redis", "mongodb"),
    ("自动化", "智能家居", "home assistant", "ha", "物联网"),
    ("监控", "告警", "日志", "uptime", "grafana", "prometheus"),
    ("ai", "大模型", "聊天", "机器人", "ollama", "openai", "llm"),
    ("书签", "收藏", "链接", "linkwarden"),
    ("日历", "通讯录", "caldav", "carddav", "baikal"),
]

DOMAIN_PROFILES = [
    {
        "id": "wechat_public_account",
        "label": "微信公众号/公众号内容跟踪",
        "triggers": (
            "公众号",
            "微信公众号",
            "微信公众",
            "weixin official",
            "public account",
            "wxmp",
        ),
        "object_terms": (
            "公众号",
            "微信公众号",
            "微信公众",
            "weixin official accounts",
            "weixin official account",
            "public account",
            "wxmp",
        ),
        "solution_terms": (
            "rss",
            "rsshub",
            "rsspush",
            "werss",
            "wewe rss",
            "juflow",
            "订阅",
            "更新",
            "文章",
            "推送",
            "webhook",
            "api",
            "download",
            "search",
            "下载",
            "搜索",
            "抓取",
        ),
        "keywords": (
            "公众号",
            "微信公众号",
            "WeRSS",
            "WeWe RSS",
            "RSSHub",
            "RSS",
            "订阅",
            "文章更新",
            "公众号文章",
        ),
        "preferred_packages": {
            "community.lazycat.app.we-rss": 120,
            "dev.libr.wewerss": 115,
            "cloud.lazycat.app.rsspush": 95,
            "cloud.lazycat.app.wxmp": 90,
            "com.wbsu2003.weixin-search-mcp": 85,
            "cloud.lazycat.app.juflow": 80,
            "lazycat.app.checkchan": 72,
            "cloud.lazycat.app.rsshub": 70,
            "cloud.lazycat.app.feedhub": 55,
            "cloud.lazycat.app.ai-rss-hub": 50,
            "wcloud.gblw.app.miniflux": 45,
            "cloud.lazycat.app.freshrss": 45,
        },
        "negative_terms": (
            "设备域名",
            "端口映射",
            "端口监控",
            "服务器监控",
            "系统监控",
            "视频监控",
            "prometheus",
            "grafana",
            "hertzbeat",
            "nezha",
        ),
    },
    {
        "id": "smart_screen",
        "label": "懒猫智慧屏/大屏电视",
        "triggers": (
            "智慧屏",
            "懒猫智慧屏",
            "大屏",
            "大屏幕",
            "看电视",
            "电视直播",
            "hdmi",
            "smart tv",
            "smart screen",
            "lzctvcontroller",
        ),
        "object_terms": (
            "智慧屏",
            "懒猫智慧屏",
            "大屏",
            "大屏幕",
            "电视",
            "看电视",
            "hdmi",
            "chromium",
            "遥控器",
            "smart tv",
            "smart screen",
            "lzctvcontroller",
        ),
        "solution_terms": (
            "观影",
            "影音",
            "直播",
            "卫视",
            "cctv",
            "电视台",
            "浏览器",
            "大屏浏览器",
            "遥控",
            "墨水屏",
            "闺蜜机",
            "使用指南",
            "更新",
            "教程",
            "攻略",
        ),
        "keywords": (
            "智慧屏",
            "懒猫智慧屏",
            "懒猫微服怎么大屏看电视",
            "大屏看电视",
            "大屏",
            "看电视",
            "HDMI",
            "电视",
            "懒猫智慧屏使用指南",
            "懒猫智慧屏接墨水屏体验",
        ),
        "preferred_packages": {
            "cloud.lazycat.app.lzctvcontroller": 130,
            "cloud.lazycat.app.video": 55,
            "cloud.lazycat.app.moontvplus": 45,
            "cloud.lazycat.app.libretv": 42,
            "cloud.lazycat.app.jellyfinsingle": 35,
            "cloud.lazycat.app.plex": 35,
        },
        "preferred_guides": {
            569: 150,
            422: 95,
            1124: 80,
            525: 75,
            838: 55,
            511: 45,
        },
        "negative_terms": (
            "飞牛",
            "apple tv",
            "infuse",
            "plex",
            "jellyfin",
            "moontvplus",
            "lightos",
        ),
    },
]

GENERIC_TERMS = {
    "一个",
    "一下",
    "什么",
    "怎么",
    "如何",
    "可以",
    "能够",
    "实现",
    "相关",
    "需求",
    "管理",
    "工具",
    "软件",
    "应用",
    "教程",
    "攻略",
    "文章",
    "懒猫",
    "微服",
    "搭建",
    "部署",
    "使用",
    "配置",
    "推荐",
    "和",
    "lazycat",
    "lazy",
    "cat",
    "microserver",
    "micro",
    "service",
    "server",
    "cloud",
    "app",
    "apps",
}

GUIDE_SIGNAL_TERMS = (
    "怎么",
    "如何",
    "教程",
    "攻略",
    "步骤",
    "配置",
    "设置",
    "搭建",
    "部署",
    "访问",
    "连接",
    "远程",
    "内网穿透",
    "端口",
    "转发",
    "登录",
    "报错",
    "失败",
    "问题",
    "通过",
    "远程桌面",
    "vnc",
    "rdp",
)

APP_SIGNAL_TERMS = (
    "应用",
    "软件",
    "app",
    "安装什么",
    "用什么",
    "推荐",
    "替代",
    "类似",
    "工具",
    "哪个好",
    "找一个",
    "有没有",
)

STRONG_APP_SIGNAL_TERMS = (
    "推荐应用",
    "商店里面的应用",
    "商店里的应用",
    "商店应用",
    "应用商店",
    "懒猫商店",
    "有没有应用",
    "找个应用",
    "找一个应用",
    "推荐一下",
)


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


def score_text(query, fields, weights=None):
    query = (query or "").strip().lower()
    if not query:
        return 0
    terms = meaningful_terms(query)
    score = 0
    weights = weights or [8, 5, 2, 4, 1, 1]
    field_texts = [str(x or "").lower() for x in fields]
    text = "\n".join(field_texts)
    for term in terms:
        if len(term) <= 1:
            continue
        for index, field_text in enumerate(field_texts):
            if term in field_text:
                score += weights[index] if index < len(weights) else 1
    title = field_texts[0] if field_texts else ""
    if query in title:
        score += 10
    if query in text:
        score += 6
    return score


def meaningful_terms(query):
    query = (query or "").strip().lower()
    if not query:
        return []

    terms = []
    compact = compact_need(query)
    lowered = compact.lower()

    for profile in active_domain_profiles(query):
        terms.extend(profile["object_terms"])
        terms.extend(profile["solution_terms"])

    for group in INTENT_TERM_GROUPS:
        if any(term.lower() in query for term in group):
            terms.extend(group)

    for token in re.findall(r"[a-z0-9][a-z0-9.+_-]*", lowered):
        if token not in GENERIC_TERMS and len(token) > 1:
            terms.append(token)

    if not terms:
        for token in re.split(r"[\s,，;；/、|]+", lowered):
            cjk = "".join(ch for ch in token if "\u4e00" <= ch <= "\u9fff")
            if 2 <= len(cjk) <= 10 and cjk not in GENERIC_TERMS:
                terms.append(cjk)
            if len(cjk) >= 3:
                terms.extend(cjk[i : i + 2] for i in range(len(cjk) - 1))

    return [term for term in ordered_unique(terms) if term not in GENERIC_TERMS and len(term) > 1]


def has_any(query, terms):
    lowered = (query or "").lower()
    return any(term.lower() in lowered for term in terms)


def active_domain_profiles(query):
    lowered = (query or "").lower()
    profiles = []
    for profile in DOMAIN_PROFILES:
        if any(term.lower() in lowered for term in profile["triggers"]):
            profiles.append(profile)
    return profiles


def detect_mode(query):
    guide_signal = has_any(query, GUIDE_SIGNAL_TERMS)
    app_signal = has_any(query, APP_SIGNAL_TERMS)
    strong_app_signal = has_any(query, STRONG_APP_SIGNAL_TERMS)
    remote_signal = has_any(query, ("远程访问", "远程桌面", "远程控制", "内网穿透", "vnc", "rdp", "3389"))
    profiles = active_domain_profiles(query)
    explicit_guide_signal = has_any(
        query,
        (
            "攻略",
            "教程",
            "指南",
            "攻略文章",
            "教程文章",
            "步骤",
            "怎么做",
            "怎么用",
            "如何使用",
        ),
    )
    explicit_both_signal = has_any(
        query,
        (
            "应用和攻略",
            "攻略和应用",
            "应用和教程",
            "教程和应用",
            "软件和攻略",
            "攻略还有应用",
            "应用还有攻略",
            "都给",
            "都要",
            "一起推荐",
            "同时推荐",
        ),
    )

    if explicit_both_signal:
        return "both", "这个需求明确同时要应用与攻略，需要两边一起判断。"
    if explicit_guide_signal and not strong_app_signal:
        return "guides", "这是明确要求攻略/教程/文章的问题，只需要攻略结果。"
    if explicit_guide_signal and strong_app_signal:
        return "guides", "虽然提到了应用，但用户明确要攻略/教程，优先只返回攻略文章。"
    if strong_app_signal:
        return "apps", "这是明确要求推荐商店应用的问题，优先需要应用结果。"
    if profiles and has_any(query, ("下载", "批量", "搜索", "检索", "监控", "订阅", "推送", "更新", "生成")) and not has_any(query, ("怎么", "如何", "教程", "攻略", "步骤")):
        return "both", "这是围绕具体对象的自动化/订阅/搜索需求，需要先看可安装应用，必要时补充攻略。"
    if remote_signal and not has_any(query, ("应用", "软件", "app", "安装什么", "推荐应用")):
        return "guides", "这是远程访问/内网穿透类问题，优先需要操作攻略。"
    if guide_signal and not app_signal:
        return "guides", "这是配置、访问或排障类问题，优先需要攻略文章。"
    if app_signal and not guide_signal:
        return "apps", "这是选应用或找软件的问题，优先需要应用结果。"
    if app_signal and guide_signal:
        return "both", "这个需求同时包含选应用和使用配置，需要应用与攻略一起判断。"
    return "both", "这是泛化解决方案需求，需要同时检查应用和攻略。"


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


def ordered_unique(values):
    seen = set()
    result = []
    for value in values:
        value = str(value or "").strip()
        if not value:
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result


def compact_need(query):
    compact = query.strip()
    for phrase in FILLER_PHRASES:
        compact = compact.replace(phrase, " ")
    compact = re.sub(r"\s+", " ", compact).strip(" ，,。.!！?？")
    return compact


def result_text(fields):
    return "\n".join(str(x or "") for x in fields).lower()


def evidence_terms(query, fields, strong_indexes=None):
    indexes = strong_indexes if strong_indexes is not None else range(len(fields))
    text = result_text(fields[index] for index in indexes if index < len(fields))
    return [term for term in meaningful_terms(query) if term.lower() in text]


def profile_match(query, fields, package):
    profiles = active_domain_profiles(query)
    if not profiles:
        return 0, [], []

    text = result_text(fields)
    strong_text = result_text([fields[index] for index in [0, 1, 3, 5] if index < len(fields)])
    score = 0
    hits = []
    negative_hits = []

    for profile in profiles:
        package_score = profile.get("preferred_packages", {}).get(package, 0)
        if package_score:
            score += package_score
            hits.append(f"preferred:{profile['id']}")

        object_hits = [term for term in profile["object_terms"] if term.lower() in text]
        strong_object_hits = [term for term in profile["object_terms"] if term.lower() in strong_text]
        solution_hits = [term for term in profile["solution_terms"] if term.lower() in text]
        strong_solution_hits = [term for term in profile["solution_terms"] if term.lower() in strong_text]
        negative = [term for term in profile.get("negative_terms", ()) if term.lower() in text]

        score += len(object_hits) * 24
        score += len(strong_object_hits) * 28
        score += len(solution_hits) * 8
        score += len(strong_solution_hits) * 12
        score -= len(negative) * 35

        hits.extend(object_hits[:4])
        hits.extend(solution_hits[:4])
        negative_hits.extend(negative[:4])

    lowered_query = (query or "").lower()
    if "下载" in lowered_query or "批量" in lowered_query or "历史文章" in lowered_query:
        if package == "cloud.lazycat.app.wxmp":
            score += 70
        if package in ("community.lazycat.app.we-rss", "dev.libr.wewerss"):
            score += 20
    if "搜索" in lowered_query or "mcp" in lowered_query or "检索" in lowered_query:
        if package == "com.wbsu2003.weixin-search-mcp":
            score += 75
    if "监控" in lowered_query or "更新" in lowered_query or "订阅" in lowered_query or "推送" in lowered_query:
        if package in ("community.lazycat.app.we-rss", "dev.libr.wewerss"):
            score += 60
        if package == "cloud.lazycat.app.rsspush":
            score += 55
        if package == "cloud.lazycat.app.juflow":
            score += 35
        if package == "lazycat.app.checkchan":
            score += 30
        if package == "cloud.lazycat.app.rsshub":
            score += 25

    return score, ordered_unique(hits), ordered_unique(negative_hits)


def guide_profile_match(query, fields, guide_id, products):
    profiles = active_domain_profiles(query)
    if not profiles:
        return 0, [], []

    text = result_text(fields)
    strong_text = result_text([fields[index] for index in [0, 2, 4] if index < len(fields)])
    product_set = {str(product or "") for product in (products or [])}
    lowered_query = (query or "").lower()
    score = 0
    hits = []
    negative_hits = []

    for profile in profiles:
        preferred_guide_score = profile.get("preferred_guides", {}).get(guide_id, 0)
        if preferred_guide_score:
            score += preferred_guide_score
            hits.append(f"preferred-guide:{profile['id']}")

        for package, package_score in profile.get("preferred_packages", {}).items():
            if package in product_set:
                score += min(package_score, 90)
                hits.append(f"linked-app:{package}")

        object_hits = [term for term in profile["object_terms"] if term.lower() in text]
        strong_object_hits = [term for term in profile["object_terms"] if term.lower() in strong_text]
        solution_hits = [term for term in profile["solution_terms"] if term.lower() in text]
        strong_solution_hits = [term for term in profile["solution_terms"] if term.lower() in strong_text]
        negative = [term for term in profile.get("negative_terms", ()) if term.lower() in text]

        score += len(object_hits) * 20
        score += len(strong_object_hits) * 24
        score += len(solution_hits) * 7
        score += len(strong_solution_hits) * 10
        score -= len(negative) * 22

        hits.extend(object_hits[:4])
        hits.extend(solution_hits[:4])
        negative_hits.extend(negative[:4])

        if profile["id"] == "smart_screen":
            if guide_id == 569 and has_any(lowered_query, ("智慧屏", "大屏", "看电视", "电视", "观影", "攻略")):
                score += 90
            if guide_id == 1124 and has_any(lowered_query, ("墨水屏", "电子墨水", "水墨屏")):
                score += 120
            if guide_id == 422 and has_any(lowered_query, ("使用指南", "指南", "怎么用", "入门", "使用")):
                score += 80
            if guide_id in (838, 511, 475, 465) and has_any(lowered_query, ("更新", "新版", "版本")):
                score += 80
            if guide_id == 569 and has_any(lowered_query, ("墨水屏", "电子墨水", "水墨屏")):
                score -= 70

    return score, ordered_unique(hits), ordered_unique(negative_hits)


def query_intent_groups(query):
    lowered = (query or "").lower()
    groups = []
    for group in INTENT_TERM_GROUPS:
        if any(term.lower() in lowered for term in group):
            groups.append(group)
    return groups


def intent_coverage(query, fields):
    text = result_text(fields)
    coverage = []
    for group in query_intent_groups(query):
        matched = [term for term in group if term.lower() in text]
        if matched:
            coverage.append(matched[:3])
    return coverage


def coverage_bonus(query, fields, strong_fields):
    groups = query_intent_groups(query)
    if not groups:
        return 0

    covered = intent_coverage(query, fields)
    strong_covered = intent_coverage(query, strong_fields)
    score = len(covered) * 8 + len(strong_covered) * 10

    if len(groups) > 1 and len(covered) == len(groups):
        score += 12
    elif len(groups) > 1 and len(covered) == 1:
        score -= 8

    return score


def build_search_keywords(query, limit=8):
    query = (query or "").strip()
    keywords = []
    if query:
        keywords.append(query)

    compact = compact_need(query)
    if compact and compact != query:
        keywords.append(compact)

    for profile in active_domain_profiles(query):
        keywords.extend(profile["keywords"])

    lowered = query.lower()
    matched_terms = []
    for group in INTENT_TERM_GROUPS:
        if any(term.lower() in lowered for term in group):
            matched_terms.extend(group[:4])

    latin_terms = re.findall(r"[a-z0-9][a-z0-9.+_-]*", lowered)
    matched_terms.extend(term for term in latin_terms if term not in GENERIC_TERMS)

    keywords.extend(matched_terms)
    if len(matched_terms) >= 2:
        keywords.append(" ".join(matched_terms[:2]))
        keywords.append(" ".join(matched_terms[:3]))

    return ordered_unique(keywords)[:limit] or [""]


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
    strong_fields = [fields[index] for index in [0, 1, 3, 5]]
    base_score = score_text(query, fields) + coverage_bonus(query, fields, strong_fields)
    profile_score, profile_hits, profile_negative_hits = profile_match(query, fields, package)
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
        "strong_evidence_terms": evidence_terms(query, fields, strong_indexes=[0, 1, 3, 5]),
        "evidence_terms": evidence_terms(query, fields),
        "intent_coverage": intent_coverage(query, fields),
        "profile_score": profile_score,
        "profile_hits": profile_hits,
        "profile_negative_hits": profile_negative_hits,
        "matched_keywords": [],
        "score": base_score + profile_score + min(int(count.get("downloads") or 0), 5000) / 10000,
    }


def normalize_guide(item, query):
    title = item.get("title") or ""
    content = item.get("content") or ""
    products = item.get("products") or []
    fields = [
        title,
        content,
        " ".join(item.get("categories") or []),
        item.get("type"),
        " ".join(products),
    ]
    strong_fields = [fields[index] for index in [0, 2, 4]]
    base_score = score_text(query, fields, weights=[10, 2, 5, 1, 8]) + coverage_bonus(query, fields, strong_fields)
    profile_score, profile_hits, profile_negative_hits = guide_profile_match(query, fields, item.get("id"), products)
    return {
        "type": "guide",
        "title": title,
        "id": item.get("id"),
        "url": guide_url(item.get("id")),
        "summary": truncate(content, 520),
        "categories": item.get("categories") or [],
        "products": products,
        "author": safe_get(item, ["user", "nickname"], "") or safe_get(item, ["user", "username"], ""),
        "created_at": item.get("createdAt") or "",
        "updated_at": item.get("updatedAt") or "",
        "views": item.get("views") or item.get("viewsTotal") or 0,
        "thumbs": item.get("thumbCount") or 0,
        "comments": item.get("commentCount") or 0,
        "strong_evidence_terms": evidence_terms(query, fields, strong_indexes=[0, 2, 4]),
        "evidence_terms": evidence_terms(query, fields),
        "intent_coverage": intent_coverage(query, fields),
        "profile_score": profile_score,
        "profile_hits": profile_hits,
        "profile_negative_hits": profile_negative_hits,
        "matched_keywords": [],
        "score": base_score + profile_score + min(int(item.get("views") or 0), 3000) / 10000,
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


def list_apps(category_id=0, sort="counting.desc", size=5000):
    return search_apps("", category_id=category_id, size=size, sort=sort).get("items") or []


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


def collect_apps(query_text, category_id, size, sort):
    collected = {}
    search_keywords = build_search_keywords(query_text)
    profiles = active_domain_profiles(query_text)
    scoring_query = " ".join(search_keywords)
    keyword_boosts = {}

    for keyword_index, keyword in enumerate(search_keywords):
        try:
            items = search_apps(keyword, category_id=category_id, size=max(size * 4, 24), sort=sort).get("items") or []
        except Exception:
            items = []
        for rank, item in enumerate(items):
            package = item.get("package") or safe_get(item, ["version", "package"], "")
            if not package:
                continue
            normalized = normalize_app(item, f"{query_text} {keyword}".strip())
            if profiles:
                if normalized["profile_score"] <= 0 or not normalized["profile_hits"]:
                    continue
            elif not normalized["strong_evidence_terms"]:
                continue
            boost = max(0, 90 - keyword_index * 5 - rank * 3)
            keyword_boosts[package] = max(keyword_boosts.get(package, 0), boost)

    for item in list_apps(category_id=category_id, sort=sort):
        package = item.get("package") or safe_get(item, ["version", "package"], "")
        if not package:
            continue
        normalized = normalize_app(item, scoring_query)
        if profiles:
            if normalized["profile_score"] <= 0 or not normalized["profile_hits"]:
                continue
        elif not normalized["strong_evidence_terms"]:
            continue
        if normalized["strong_evidence_terms"]:
            normalized["score"] += 12
        if package in keyword_boosts:
            normalized["score"] += keyword_boosts[package]
        normalized["matched_keywords"] = search_keywords
        collected[package] = normalized

    return sorted(collected.values(), key=lambda x: x["score"], reverse=True)[:size], search_keywords


def collect_guides(query_text, category_id, size, sort):
    collected = {}
    search_keywords = build_search_keywords(query_text)
    profiles = active_domain_profiles(query_text)
    fetch_size = max(size * 3, size, 12)
    for keyword_index, keyword in enumerate(search_keywords):
        payload = search_guides(keyword, category_id=category_id, size=fetch_size, sort=sort)
        for item in payload.get("items") or []:
            guide_id = item.get("id")
            if not guide_id:
                continue
            normalized = normalize_guide(item, f"{query_text} {keyword}".strip())
            if profiles:
                if normalized["profile_score"] <= 0 and not normalized["strong_evidence_terms"] and len(normalized["evidence_terms"]) < 2:
                    continue
            else:
                if not normalized["strong_evidence_terms"] and len(normalized["evidence_terms"]) < 2:
                    continue
            if normalized["strong_evidence_terms"]:
                normalized["score"] += 10
            normalized["matched_keywords"] = [keyword] if keyword else []
            normalized["score"] += max(0, 3 - keyword_index * 0.25)
            existing = collected.get(guide_id)
            if not existing or normalized["score"] > existing["score"]:
                if existing:
                    normalized["matched_keywords"] = ordered_unique(
                        existing.get("matched_keywords", []) + normalized["matched_keywords"]
                    )
                collected[guide_id] = normalized
            elif existing and keyword:
                existing["matched_keywords"] = ordered_unique(existing.get("matched_keywords", []) + [keyword])
    return sorted(collected.values(), key=lambda x: x["score"], reverse=True)[:size], search_keywords


def main():
    parser = argparse.ArgumentParser(description="Query Lazycat appstore and playground recommendation data.")
    parser.add_argument("query", nargs="*", help="User need / search keywords")
    parser.add_argument("--apps", type=int, default=8, help="Number of app candidates to return")
    parser.add_argument("--guides", type=int, default=8, help="Number of guide candidates to return")
    parser.add_argument("--mode", choices=["auto", "both", "apps", "guides"], default="auto", help="Search apps, guides, both, or auto-detect")
    parser.add_argument("--app-category", type=int, default=0, help="Appstore category id, default 0")
    parser.add_argument("--guide-category", type=int, help="Playground guideline category id")
    parser.add_argument("--include-categories", action="store_true", help="Include category lists for category discovery")
    parser.add_argument("--sort-apps", default="counting.desc", help="App sort, e.g. counting.desc or updated_at.desc")
    parser.add_argument("--sort-guides", default="-createdAt", help="Guide sort, e.g. -createdAt or -updatedAt")
    args = parser.parse_args()

    query_text = " ".join(args.query).strip()
    detected_mode, mode_reason = detect_mode(query_text)
    effective_mode = detected_mode if args.mode == "auto" else args.mode
    search_keywords = build_search_keywords(query_text)

    result = {
        "queried_at_unix": int(time.time()),
        "query": query_text,
        "analysis": {
            "detected_mode": detected_mode,
            "effective_mode": effective_mode,
            "reason": mode_reason,
        },
        "search_keywords": search_keywords,
        "sources": {
            "appstore": "https://lazycat.cloud/appstore/",
            "playground": "https://lazycat.cloud/playground/",
        },
        "counts": {},
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

    if args.include_categories:
        result["categories"] = {}
        try:
            result["categories"]["apps"] = get_app_categories()
        except Exception as exc:
            result["errors"].append(f"app categories fetch failed: {exc}")

        try:
            result["categories"]["guides"] = (get_guide_categories().get("items") or [])
        except Exception as exc:
            result["errors"].append(f"guide categories fetch failed: {exc}")

    if effective_mode in ("both", "apps"):
        try:
            result["apps"], app_keywords = collect_apps(
                query_text,
                category_id=args.app_category,
                size=args.apps,
                sort=args.sort_apps,
            )
            result["search_keywords"] = ordered_unique(result["search_keywords"] + app_keywords)
        except Exception as exc:
            result["errors"].append(f"app search failed: {exc}")

    if effective_mode in ("both", "guides"):
        try:
            result["guides"], guide_keywords = collect_guides(
                query_text,
                category_id=args.guide_category,
                size=args.guides,
                sort=args.sort_guides,
            )
            result["search_keywords"] = ordered_unique(result["search_keywords"] + guide_keywords)
        except Exception as exc:
            result["errors"].append(f"guide search failed: {exc}")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not result["errors"] else 2


if __name__ == "__main__":
    sys.exit(main())
