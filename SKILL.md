---
name: lazycat-recommender
description: Recommend Lazycat MicroServer apps and playground guides from the live Lazycat appstore and guide platform. Use when the user asks for software recommendations, guide/tutorial recommendations, ways to achieve a goal on Lazycat MicroServer, app counts, guide counts, category discovery, alternatives to an app, or "what Lazycat app/guide can do X"; always use live data because the store and guide platform update frequently.
---

# Lazycat Recommender

## Workflow

Use live Lazycat data before recommending. Do not rely on remembered app or guide lists.

Run:

```bash
python3 "$CODEX_HOME/skills/lazycat-recommender/scripts/lazycat_recommend.py" "<user need>"
```

If `CODEX_HOME` is unset, use:

```bash
python3 "$HOME/.codex/skills/lazycat-recommender/scripts/lazycat_recommend.py" "<user need>"
```

For category-specific searches, pass the category ID from the returned category list:

```bash
python3 "$HOME/.codex/skills/lazycat-recommender/scripts/lazycat_recommend.py" "<user need>" --app-category 24 --guide-category 18
```

## Recommendation Rules

Recommend both apps and guides when useful:

- Apps answer "install what".
- Guides answer "how to set it up or use it".
- If the user's goal is vague, infer likely keywords and mention the assumption.
- If a result has weak evidence, say it is a candidate rather than a confident recommendation.
- Prefer exact matches in name, brief, description, and keywords.
- Prefer higher download count, rating, recent updates, and relevant guide views only after relevance is established.
- Include links to the app detail page or guide detail page.
- Mention whether an app supports PC/mobile when it matters.
- Avoid inventing app features that are not present in the returned fields.

## Answer Shape

For normal recommendations, answer in Chinese unless the user asks otherwise:

1. State the live counts when helpful, for example app total and guide total from the script output.
2. Give 3-6 ranked recommendations.
3. For each item, include:
   - name/title
   - link
   - why it matches the user's need
   - app or guide type
   - any caveat from the data
4. End with a short suggested combination if multiple apps/guides work together.

Keep the response concise. The user wants a practical recommendation, not a catalog dump.

## Data Source Reference

If the script fails, read `references/api.md` and query the verified endpoints manually with `curl`. If those endpoints no longer match the site, recapture real browser Network traffic with Chrome remote debugging/CDP before changing URLs. Do not infer endpoints from bundled frontend filenames alone.

Ignore unauthenticated `account/userInfo` 401 responses; they are not needed for public recommendations.
