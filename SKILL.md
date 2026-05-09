---
name: lazycat-recommender
description: Analyze a user's Lazycat MicroServer goal, decide whether they need an app, a guide article, or both, then search live Lazycat appstore/playground data and answer with practical reasoning plus official app or guide links. Use for Lazycat software discovery, guide/tutorial lookup, setup paths, remote access, networking, deployment, troubleshooting, or "how can I do X on Lazycat" questions.
---

# Lazycat Recommender

## Workflow

Always use live Lazycat data before answering. Do not answer from memory.

1. Analyze the user's real goal first. Decide whether the user needs:
   - **Guide only**: setup/configuration/how-to/troubleshooting/remote access/networking/usage steps.
   - **App only**: choosing installable software, alternatives, or "what app can do X".
   - **Both**: the user needs an app and also needs setup/use guidance.
2. Search only what is needed. Do not force an app recommendation into a guide-only question.
3. Read the returned titles, names, summaries, and links. Make an independent relevance judgment instead of mechanically trusting the first score.
4. Answer with concise analysis and the needed links. Do not include crawling details, raw JSON, endpoint names, category dumps, live counts, scores, or search keywords unless the user asks for them.

Default automatic search:

```bash
python3 "$CODEX_HOME/skills/lazycat-recommender/scripts/lazycat_recommend.py" "<user need>"
```

If `CODEX_HOME` is unset, use the script path relative to this skill directory:

```bash
python3 scripts/lazycat_recommend.py "<user need>"
```

Force one side only when the user explicitly asks for it or the intent is obvious:

```bash
python3 scripts/lazycat_recommend.py "<user need>" --mode apps
python3 scripts/lazycat_recommend.py "<user need>" --mode guides
```

## Recommendation Rules

- Apps answer "install what"; guides answer "how to set it up, configure it, fix it, or use it".
- For remote access, intranet tunneling, port forwarding, Windows remote desktop, VNC, RDP, Netmap, or "through Lazycat to access another computer", prefer guide articles unless the user explicitly asks what app to install.
- Prefer exact matches in app name/brief/keywords and guide title/content.
- Use the official app name exactly from `apps[].name`. Never invent app names from package names, English query words, or guide text. Do not output `package` as the app name.
- Use the guide title exactly from `guides[].title`.
- If the official app name is English, keep that official English name; otherwise preserve the Chinese name from the store.
- Include only links returned by the live data.
- Do not invent app features or guide content not present in the returned fields.
- If relevance is weak, label the result as "可作为候选" instead of presenting it as certain.
- Omit empty or irrelevant sections. If there is no strong app match, do not show "推荐应用".

## Answer Shape

Answer in Chinese unless the user asks otherwise. Use the sections that fit the intent and omit the rest:

```markdown
需求分析：<1-2 sentences showing you understood the user's actual scenario and why this needs an app, a guide, or both.>

建议方案：<1-2 sentences with the practical route.>

推荐应用：
1. [<official app name from apps[].name>](<app url>)：<why it matches, in one sentence.>

推荐攻略：
1. [<guide title>](<guide url>)：<what this article helps with, in one sentence.>
```

For a guide-only question, the final answer should usually be:

```markdown
需求分析：<analysis>

建议方案：<route>

推荐攻略：
1. [<guide title>](<guide url>)：<why this is the right article.>
```

Limits:

- Usually return 1-2 high-confidence items, not a catalog.
- Do not add a long preface or explain how the search was performed.
- If nothing strong is found, say so plainly and give the closest candidate link only if it is still useful.

## Example Judgment

User: "我要通过懒猫微服的内网穿透远程访问我的另外一台电脑"

Expected behavior: analyze this as a remote-access how-to problem, not an app-shopping problem. Search guides first and recommend an article such as "通过懒猫远程访问windows电脑" if returned by live data. Do not add a "推荐应用" section unless a live app result is clearly necessary.

## Data Source Reference

If the script fails, read `references/api.md` and query the verified endpoints manually with `curl`. If those endpoints no longer match the site, recapture real browser Network traffic with Chrome remote debugging/CDP before changing URLs. If Chrome remote debugging is available at `127.0.0.1:9222`, use that before guessing new endpoints.

Ignore unauthenticated `account/userInfo` 401 responses; they are not needed for public recommendations.
