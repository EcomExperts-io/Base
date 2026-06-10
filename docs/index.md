---
layout: home

hero:
  name: "Base Theme Documentation"
  text: "Developer guide and reference"
  tagline: "A developer-first Shopify theme prioritizing clean code and maintainability."
  actions:
    - theme: brand
      text: Sections
      link: /sections/product
    - theme: brand
      text: Snippets
      link: /snippets/component-product-card
    - theme: brand
      text: Assets
      link: /assets/component-product-card

features:
  - title: Clean Architecture
    details: Organized, logical file structure with clear separation of concerns.
  - title: Minimal Dependencies
    details: Only essential libraries like Alpine.js — cart functionality is a native engine built on Shopify APIs.
  - title: Modern Development
    details: Built using Shopify CLI 3.0 and Online Store 2.0 features.

---

<br>
<br>
<br>

# Introduction

Base Theme is crafted for developers who appreciate clean, well-structured code and minimal complexity. It serves as a solid foundation that you can build upon, stripping away the bloat commonly found in marketplace themes.

## Developer Benefits

- **Clean Architecture**: Organized file structure with clear separation of concerns.
- **Minimal Dependencies**: Only essential libraries and tools included.
- **Modern Development**: Built using Shopify CLI 3.0 and Online Store 2.0 features.
- **Simplified Customization**: Well-documented sections and blocks.
- **Performance First**: Lightweight base with no unnecessary JavaScript or CSS.
- **Zero Build Tools**: Pure JavaScript and CSS - no complex build processes.

## Third-Party Libraries

We use a carefully selected set of libraries to provide essential functionality while maintaining performance:

- **[Alpine.js](https://alpinejs.dev/)**: Lightweight framework for UI state management and interactivity.
- **[Swiper](https://swiperjs.com/)**: Modern mobile touch slider for product image galleries.

Cart functionality is handled by a native cart engine (`assets/cart.js`) built on Shopify's Cart AJAX API and Section Rendering API. It exposes a `window.Cart` API and broadcasts `cart:change` / `cart:error` events that the cart components react to — no third-party cart library required.
