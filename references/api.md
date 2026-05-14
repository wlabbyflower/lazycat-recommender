# Lazycat Public Data Interfaces

These endpoints were verified by Chrome remote debugging against `https://lazycat.cloud/appstore/` and `https://lazycat.cloud/playground/`.

## Appstore

Base sites:

- Store UI: `https://lazycat.cloud/appstore/`
- Store API: `https://appstore.api.lazycat.cloud/api/v3`
- Store metadata CDN: `https://dl.lazycat.cloud/appstore/metarepo`

Useful endpoints:

- Current metadata release:
  `GET https://dl.lazycat.cloud/appstore/metarepo/op/index`
- App total count:
  `GET https://appstore.api.lazycat.cloud/api/v3/user/app/list?category_ids=0&sort=counting.desc&page=0&size=0`
- App categories:
  `GET https://dl.lazycat.cloud/appstore/metarepo/zh/categories.json`
- App search/list:
  `GET https://appstore.api.lazycat.cloud/api/v3/user/app/list?category_ids=0&sort=counting.desc&page=0&size=20&keyword=<keyword>`
- Category app list:
  `GET https://appstore.api.lazycat.cloud/api/v3/user/app/list?category_ids=<id>&sort=counting.desc&page=0&size=24`
- Category detail:
  `GET https://appstore.api.lazycat.cloud/api/v3/user/category/<id>`
- Homepage blocks:
  `GET https://dl.lazycat.cloud/appstore/metarepo/zh/<release>/homepage_block.json`
- Homepage block data:
  `GET https://dl.lazycat.cloud/appstore/metarepo/zh/<release>/homepage_block_recents.json`
  `GET https://dl.lazycat.cloud/appstore/metarepo/zh/<release>/homepage_block_ratings.json`
  `GET https://dl.lazycat.cloud/appstore/metarepo/zh/<release>/homepage_block_4.json`

Important fields:

- App name: `information.name`
- Brief: `information.brief`
- Detail: `information.description`
- Keywords: `information.keywords`
- Package: `package`
- Version: `version.name`
- Download count: `count.downloads`
- Rating: `rating.score`
- Detail URL: `https://lazycat.cloud/appstore/detail/<package>`

## Playground

Base sites:

- Playground UI: `https://lazycat.cloud/playground/`
- Playground API: `https://playground.api.lazycat.cloud/api`

Useful endpoints:

- Guide total count:
  `GET https://playground.api.lazycat.cloud/api/workshop/guideline/list?size=0&note=use_get_total`
- Guide categories:
  `GET https://playground.api.lazycat.cloud/api/workshop/guideline-category/list?size=100`
- Recent guides:
  `GET https://playground.api.lazycat.cloud/api/workshop/guideline/list?size=20&sort=-createdAt&page=0`
- Category guides:
  `GET https://playground.api.lazycat.cloud/api/workshop/guideline/list?size=20&sort=-updatedAt&category_id=<id>&page=0`
- Keyword guide search:
  `GET https://playground.api.lazycat.cloud/api/workshop/guideline/list?size=20&sort=-createdAt&page=0&keyword=<keyword>`

Important fields:

- Guide title: `title`
- Content: `content`
- Category IDs: `categoryIds`
- Category names: `categories`
- Author: `user.nickname` or `user.username`
- Views: `views` or `viewsTotal`
- Detail URL: `https://lazycat.cloud/playground/guideline/<id>`

## Notes

- Both app and guide counts update over time. Always fetch live data before giving counts.
- Unauthenticated `account/userInfo` requests may return `401`; ignore them for recommendation tasks.
- Appstore search accepts `keyword`. Chrome search page behavior may also filter client side, but the API keyword parameter returns useful candidates.
- Prefer API responses over scraping rendered HTML.
