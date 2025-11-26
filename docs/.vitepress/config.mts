import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "Base Theme Documentation",
  description: "Documentation for the Base Theme",
  base: '/Base/', 
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Sections', link: '/sections/product' },
      { text: 'Snippets', link: '/snippets/component-product-card' }
    ],

    sidebar: [
      {
        text: 'Sections',
        items: [
          { text: '404', link: '/sections/404' },
          { text: 'Account', link: '/sections/account' },
          { text: 'Activate Account', link: '/sections/activate-account' },
          { text: 'Addresses', link: '/sections/addresses' },
          { text: 'Article', link: '/sections/article' },
          { text: 'Blog', link: '/sections/blog' },
          { text: 'Cart', link: '/sections/cart' },
          { text: 'Collection', link: '/sections/collection' },
          { text: 'Collections List', link: '/sections/collections' },
          { text: 'Custom Section', link: '/sections/custom-section' },
          { text: 'Featured Collections', link: '/sections/featured-collections' },
          { text: 'Featured Products', link: '/sections/featured-products' },
          { text: 'Footer', link: '/sections/footer' },
          { text: 'Header', link: '/sections/header' },
          { text: 'Hello World', link: '/sections/hello-world' },
          { text: 'Hero Banner', link: '/sections/hero' },
          { text: 'Login', link: '/sections/login' },
          { text: 'Order', link: '/sections/order' },
          { text: 'Page', link: '/sections/page' },
          { text: 'Password', link: '/sections/password' },
          { text: 'Pickup Availability', link: '/sections/pickup-availability' },
          { text: 'Predictive Results', link: '/sections/predictive-results' },
          { text: 'Product', link: '/sections/product' },
          { text: 'Register', link: '/sections/register' },
          { text: 'Reset Password', link: '/sections/reset-password' },
          { text: 'Search', link: '/sections/search' }
        ]
      },
      {
        text: 'Snippets',
        items: [
          { text: 'Cart Discount', link: '/snippets/cart-discount' },
          { text: 'Article Card', link: '/snippets/component-article-card' },
          { text: 'Cart Drawer', link: '/snippets/component-cart-drawer' },
          { text: 'Cart Notification', link: '/snippets/component-cart-notification' },
          { text: 'Filters Drawer', link: '/snippets/component-filters-drawer' },
          { text: 'Filters Horizontal', link: '/snippets/component-filters-horizontal' },
          { text: 'Filters Price Range', link: '/snippets/component-filters-price-range' },
          { text: 'Filters Sidebar', link: '/snippets/component-filters-sidebar' },
          { text: 'Localization Form', link: '/snippets/component-localization-form' },
          { text: 'Nav Drawer', link: '/snippets/component-nav-drawer' },
          { text: 'Nav Dropdown', link: '/snippets/component-nav-dropdown' },
          { text: 'Nav Megamenu', link: '/snippets/component-nav-megamenu' },
          { text: 'Pagination', link: '/snippets/component-pagination' },
          { text: 'Predictive Search', link: '/snippets/component-predictive-search' },
          { text: 'Product Card', link: '/snippets/component-product-card' },
          { text: 'Product Media Gallery', link: '/snippets/component-product-media-gallery' },
          { text: 'Product Media Modal', link: '/snippets/component-product-media-modal' },
          { text: 'Product Media', link: '/snippets/component-product-media' },
          { text: 'Product Price', link: '/snippets/component-product-price' },
          { text: 'Product Share Button', link: '/snippets/component-product-share-button' },
          { text: 'Social Icons', link: '/snippets/component-social-icons' },
          { text: 'CSS Variables', link: '/snippets/css-variables' },
          { text: 'Meta Tags', link: '/snippets/meta-tags' }
        ]
      },
      {
        text: 'Assets & Components',
        items: [
          { text: 'Card Discount', link: '/assets/card-discount' },
          { text: 'Cart Drawer (Asset)', link: '/assets/component-cart-drawer' },
          { text: 'Cart Notification (Asset)', link: '/assets/component-cart-notification' },
          { text: 'Product Card (Asset)', link: '/assets/component-product-card' },
          { text: 'Collection Section (Asset)', link: '/assets/section-collection' },
          { text: 'Component Filters Price Range (Asset)', link: '/assets/component-filters-price-range' },
          { text: 'Component Infinite Scroll (Asset)', link: '/assets/component-infinite-scroll' },
          { text: 'Component Localization Form (Asset)', link: '/assets/component-localization-form' },
          { text: 'Component Modal Opener (Asset)', link: '/assets/component-modal-opener' },
          { text: 'Component Pickup Availability (Asset)', link: '/assets/component-pickup-availability' },
          { text: 'Component Predictive Search (Asset)', link: '/assets/component-predictive-search' },
          { text: 'Component Product Media Magnify (Asset)', link: '/assets/component-product-media-magnify' },
          { text: 'Component Product Media Modal (Asset)', link: '/assets/component-product-media-modal' },
          { text: 'Component Product Share Button (Asset)', link: '/assets/component-product-share-button' },
          { text: 'Component Quick Add (Asset)', link: '/assets/component-quick-add' },
          { text: 'Component Selling Plans (Asset)', link: '/assets/component-selling-plans' },
          { text: 'Customer (Asset)', link: '/assets/customer' },
          { text: 'Product Recommendations (Asset)', link: '/assets/product-recommendations' },
          { text: 'Section Featured Products (Asset)', link: '/assets/section-featured-products' },
          { text: 'Section Product (Asset)', link: '/assets/section-product' },
          { text: 'Theme (Asset)', link: '/assets/theme' },
        ]
      }
    ],

    socialLinks: [
       { icon: 'github', link: 'https://github.com/EcomExperts-io/Base' }
    ]
  }
})

