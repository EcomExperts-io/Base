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
          { text: 'Cart Drawer', link: '/snippets/component-cart-drawer' },
          { text: 'Cart Notification', link: '/snippets/component-cart-notification' },
          { text: 'Product Card', link: '/snippets/component-product-card' }
        ]
      },
      {
        text: 'Assets & Components',
        items: [
          { text: 'Card Discount', link: '/assets/card-discount' },
          { text: 'Cart Drawer (Asset)', link: '/assets/component-cart-drawer' },
          { text: 'Cart Notification (Asset)', link: '/assets/component-cart-notification' },
          { text: 'Product Card (Asset)', link: '/assets/component-product-card' },
          { text: 'Collection Section (Asset)', link: '/assets/section-collection' }
        ]
      }
    ],

    socialLinks: [
       { icon: 'github', link: 'https://github.com/EcomExperts-io/Base' }
    ]
  }
})

