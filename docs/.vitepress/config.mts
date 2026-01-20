import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "Base Theme Documentation",
  description: "Documentation for the Base Theme",
  base: '/Base/', 
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Sections', link: '/sections/product' },
      { text: 'Snippets', link: '/snippets/component-product-card' },
      { text: 'Assets', link: '/assets/component-product-card' }

    ],

    sidebar: {
      '/sections/': [
        {
          text: 'Sections',
          items: [
            { text: '404', link: '/sections/404' },
            { text: 'Account', link: '/sections/account' },
            { text: 'Activate Account', link: '/sections/activate-account' },
            { text: 'Addresses', link: '/sections/addresses' },
            { text: 'Announcement Bar', link: '/sections/announcement-bar' },
            { text: 'Animated Features', link: '/sections/animated-features' },
            { text: 'Animated Features V2', link: '/sections/animated-features-v2' },
            { text: 'Article', link: '/sections/article' },
            { text: 'Blog', link: '/sections/blog' },
            { text: 'Blogs', link: '/sections/blogs' },
            { text: 'Brand Story', link: '/sections/brand-story' },
            { text: 'Brand Story V2', link: '/sections/brand-story-v2' },
            { text: 'Cart', link: '/sections/cart' },
            { text: 'Collection', link: '/sections/collection' },
            { text: 'Collections', link: '/sections/collections' },
            { text: 'Custom Section', link: '/sections/custom-section' },
            { text: 'Dynamic Grid', link: '/sections/dynamic-grid' },
            { text: 'Featured Collections', link: '/sections/featured-collections' },
            { text: 'Featured Collections V2', link: '/sections/featured-collections-v2' },
            { text: 'Featured Products', link: '/sections/featured-products' },
            { text: 'FAQ', link: '/sections/faq' },
            { text: 'Footer', link: '/sections/footer' },
            { text: 'Header', link: '/sections/header' },
            { text: 'Hello World', link: '/sections/hello-world' },
            { text: 'Hero Banner', link: '/sections/hero' },
            { text: 'Hero V2', link: '/sections/hero-v2' },
            { text: 'Login', link: '/sections/login' },
            { text: 'Logos', link: '/sections/logos' },
            { text: 'Order', link: '/sections/order' },
            { text: 'Page', link: '/sections/page' },
            { text: 'Password', link: '/sections/password' },
            { text: 'Pickup Availability', link: '/sections/pickup-availability' },
            { text: 'Predictive Results', link: '/sections/predictive-results' },
            { text: 'Product', link: '/sections/product' },
            { text: 'Product Details', link: '/sections/product-details' },
            { text: 'Product Highlights', link: '/sections/product-highlights' },
            { text: 'Promo Banner', link: '/sections/promo-banner' },
            { text: 'Register', link: '/sections/register' },
            { text: 'Related Products', link: '/sections/related-products' },
            { text: 'Reset Password', link: '/sections/reset-password' },
            { text: 'Search', link: '/sections/search' },
            { text: 'Selling Points', link: '/sections/selling-points' },
            { text: 'Selling Points V2', link: '/sections/selling-points-v2' },
            { text: 'Shop By Category', link: '/sections/shop-by-category' },
            { text: 'Shop By Category V2', link: '/sections/shop-by-category-v2' },
            { text: 'Shop Categories', link: '/sections/shop-categories' },
            { text: 'Shop The Look', link: '/sections/shop-the-look' }
          ]
        }
      ],
      '/snippets/': [
        {
          text: 'Snippets',
          items: [
            { text: 'Article Card', link: '/snippets/component-article-card' },
            { text: 'Cart Discount', link: '/snippets/component-cart-discount' },
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
        }
      ],
      '/assets/': [
        {
          text: 'Assets',
          items: [
            { text: 'Product Info', link: '/assets/section-product' },
            { text: 'Collection Info', link: '/assets/section-collection' },

            { text: 'Cart Discount', link: '/assets/component-cart-discount' },
            { text: 'Cart Drawer', link: '/assets/component-cart-drawer' },
            { text: 'Cart Notification', link: '/assets/component-cart-notification' },
            { text: 'Product Card', link: '/assets/component-product-card' },
            { text: 'Filters Price Range', link: '/assets/component-filters-price-range' },
            { text: 'Infinite Scroll', link: '/assets/component-infinite-scroll' },
            { text: 'Localization Form', link: '/assets/component-localization-form' },
            { text: 'Modal Opener', link: '/assets/component-modal-opener' },
            { text: 'Pickup Availability', link: '/assets/component-pickup-availability' },
            { text: 'Predictive Search', link: '/assets/component-predictive-search' },
            { text: 'Product Media Magnify', link: '/assets/component-product-media-magnify' },
            { text: 'Product Media Modal', link: '/assets/component-product-media-modal' },
            { text: 'Product Share Button', link: '/assets/component-product-share-button' },
            { text: 'Quick Add', link: '/assets/component-quick-add' },
            { text: 'Selling Plans', link: '/assets/component-selling-plans' },
            { text: 'Customer', link: '/assets/customer' },
            { text: 'Product Recommendations', link: '/assets/product-recommendations' },
            { text: 'Featured Products', link: '/assets/section-featured-products' },
            { text: 'Theme', link: '/assets/theme' },
          ]
        }
      ],
    },

    socialLinks: [
       { icon: 'github', link: 'https://github.com/EcomExperts-io/Base' }
    ]
  }
})

