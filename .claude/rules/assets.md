---
description: Static files (css, js, and images) for theme templates
paths:
  - "assets/**"
---

# Assets

The assets directory contains any assets that need to be referenced within a `.liquid` file, usually using the [asset_url](https://shopify.dev/docs/api/liquid/filters/asset_url) Liquid filter.

Assets is a flat directory, it may not contain subdirectories.

Any images that are required in the code, including icons, may be stored within assets. Icons can be used in `.liquid` files via the [inline_asset_content](https://shopify.dev/docs/api/liquid/filters/inline_asset_content) Liquid filter.
