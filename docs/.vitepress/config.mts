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
          { text: 'Header', link: '/sections/header' },
          { text: 'Account', link: '/sections/account' },
          { text: 'Hero Banner', link: '/sections/hero' },
          { text: 'Product', link: '/sections/product' },
          { text: 'Featured Products', link: '/sections/featured-products' },
          { text: 'Collection', link: '/sections/collection' },
          { text: 'Featured Collections', link: '/sections/featured-collections' },
          { text: 'Collections List', link: '/sections/collections' },
          { text: 'Custom Section', link: '/sections/custom-section' },
          { text: 'Article', link: '/sections/article' },
          { text: 'Blog', link: '/sections/blog' },
          { text: 'Cart', link: '/sections/cart' },
          { text: '404', link: '/sections/404' },
          { text: 'Footer', link: '/sections/footer' },
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

