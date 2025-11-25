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
          { text: 'Cart', link: '/sections/cart' },
          { text: 'Collection', link: '/sections/collection' },
          { text: 'Collections List', link: '/sections/collections' },
          { text: 'Product', link: '/sections/product' }
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
          { text: 'Collection Section (Asset)', link: '/assets/section-collection' },
          { text: 'Price Range (Asset)', link: '/assets/component-filters-price-range' }
        ]
      }
    ],

    socialLinks: [
       { icon: 'github', link: 'https://github.com/EcomExperts-io/Base' }
    ]
  }
})

