---
name: lazycat-recommender
description: Understand a user's goal and recommend Lazycat MicroServer apps and playground guide articles from live Lazycat data. Use when the user asks what app, software, guide, tutorial, article, or setup path can satisfy a need on Lazycat MicroServer; always search the live appstore and/or playground before answering, and return only practical suggestions with app links and guide links.
---

# Lazycat Recommender

## Workflow

Always use live Lazycat data before recommending. Do not answer from memory.

1. Read the user's need and reduce it to 2-5 concrete search terms: target job, app category, protocol/tool name, data type, or setup action.
2. Search apps and guides unless the user explicitly asks for only one of them.
3. Rank results by direct relevance first. Popularity, ratings, views, and freshness are tie-breakers only.
4. Answer with concise advice, app links, and guide article links. Do not include crawling details, raw JSON, endpoint names, category dumps, or live counts unless the user asks for them.

From an installed Codex skill, run:

Run:

```bash
python3 "$CODEX_HOME/skills/lazycat-recommender/scripts/lazycat_recommend.py" "<user need>"
```

If `CODEX_HOME` is unset, use the script path relative to this skill directory:

```bash
python3 scripts/lazycat_recommend.py "<user need>"
```

To search only one side:

```bash
python3 scripts/lazycat_recommend.py "<user need>" --mode apps
python3 scripts/lazycat_recommend.py "<user need>" --mode guides
```

## Recommendation Rules

- Apps answer "install what"; guides answer "how to set it up or use it".
- Prefer exact matches in app name, brief, description, keywords, guide title, and guide content.
- If the user's wording is broad, infer the practical intent and search with those terms. Mention the inferred intent only if it affects the recommendation.
- Include only links returned by the live data.
- Do not invent app features or guide content not present in the returned fields.
- If relevance is weak, label the result as "可作为候选" instead of presenting it as certain.
- Mention PC/mobile support only when it affects the user's need.

## Answer Shape

Answer in Chinese unless the user asks otherwise. Keep this shape and omit empty sections:

```markdown
建议：<1-2 sentences explaining the best route for the user's need.>

推荐应用：
1. [<app name>](<app url>)：<why it matches, in one sentence.>
2. [<app name>](<app url>)：<why it matches, in one sentence.>

攻略文章：
1. [<guide title>](<guide url>)：<what this article helps with, in one sentence.>
2. [<guide title>](<guide url>)：<what this article helps with, in one sentence.>
```

Limits:

- Usually return 1-3 apps and 1-3 guide articles.
- Do not show app totals, guide totals, API URLs, search keywords, scores, or categories in the final answer.
- Do not add a long preface or explain how the search was performed.
- If nothing strong is found, say which part was not found and give the closest candidate links if any.

## Data Source Reference

If the script fails, read `references/api.md` and query the verified endpoints manually with `curl`. If those endpoints no longer match the site, recapture real browser Network traffic with Chrome remote debugging/CDP before changing URLs. If Chrome remote debugging is available at `127.0.0.1:9222`, use that before guessing new endpoints.

Ignore unauthenticated `account/userInfo` 401 responses; they are not needed for public recommendations.
