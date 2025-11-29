# ProductCard Web Component

Imagine a bustling storefront where each product card feels alive: clicking a color swatch instantly refreshes the main image. The **ProductCard** component brings this magic to life, transforming static HTML into an interactive showcase.

## What It Does

`assets/component-product-card.js` exports a custom element named `<product-card>`. It:

- Listens for **swatch clicks** within each card.
- Updates the **main product image** based on the selected variant.
- Toggles a **selected** state on swatches.

All of this happens without a page reload, creating a seamless shopper experience .

---

## API Overview

| Method | Purpose |
| --- | --- |
| **constructor()** | Initializes the HTMLElement by calling `super()`. |
| **connectedCallback** | Attaches click listeners to each `.color-swatch`. |
| **onSwatchClick** | Handles swatch interaction: updates image URL, srcset, and UI. |


---

## Detailed Method Documentation

### constructor()

The story begins here.

When a `<product-card>` is instantiated, its **constructor** calls `super()`, inheriting all standard element behavior.

```js
constructor() {
  super();
}
```

*No additional setup occurs here; the magic starts in* `connectedCallback()` .

---

### connectedCallback()

As soon as the element enters the DOM, **connectedCallback** awakens. It:

1. Finds all elements with `.color-swatch`.
2. Binds the `click` event to each swatch.
3. Ensures `this` inside the handler refers to the card instance.

```js
connectedCallback() {
  this.querySelectorAll('.color-swatch')
      .forEach(s => s.addEventListener('click', this.onSwatchClick.bind(this)));
}
```

This sets the stage for responsive swatch interactions .

---

### onSwatchClick(event)

When a shopper clicks a swatch, **onSwatchClick** takes the lead:

1. **Identify** the clicked swatch (`event.target`).
2. **Locate** the main image using a matching `data-product-image` attribute.
3. **Extract** the variant’s image URL and `srcset`:
4. First from a nested `.data-variant-image` element.
5. Otherwise directly from the swatch element.
6. **Deselect** all swatches, then **select** the clicked one.
7. **Update** the main `<img>`’s `src` and `srcset` if available.

```js
onSwatchClick(event) {
  const swatch = event.target;
  const productImage = this.querySelector(
    `[data-product-image="${this.dataset.productId}"]`
  );

  // Get new URLs
  const swatchImage = swatch.querySelector('.data-variant-image');
  let newImageUrl = swatchImage?.getAttribute('src') || swatch.getAttribute('src');
  let newSrcset   = swatchImage?.getAttribute('srcset') || swatch.getAttribute('srcset');

  // Update swatch UI
  this.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
  swatch.classList.add('selected');

  // Swap the main image
  if (productImage && newImageUrl) {
    productImage.src    = newImageUrl;
    productImage.srcset = newSrcset;
  }
}
```

This elegant flow swaps product visuals in an instant .

---

## Custom Element Definition

To avoid redefinitions, the script checks if `<product-card>` is already registered:

```js
if (!customElements.get('product-card')) {
  customElements.define('product-card', ProductCard);
}
```

This ensures compatibility with other scripts and hot-reloading scenarios .

---

## Integration with Shopify Liquid

On the server, a Liquid snippet injects the `<product-card>` wrapper:

```liquid
<product-card class="product-card" data-product-id="{{ card_product.id }}">
  <!-- Card markup with .color-swatch spans and data-variant-image -->
</product-card>
```

This snippet lives in `snippets/component-product-card.liquid`, linking the JavaScript and HTML glue .

---

## Usage Example

1. **Render** a product card in Liquid:

```liquid
   {% render 'component-product-card',
     card_product: product,
     enable_swatches: true,
     swatch_trigger: 'Color' %}
```

1. **Ensure** your HTML includes:
2. `data-product-id` on `<product-card>`
3. Main `<img>` with `data-product-image="\{\{ product.id \}\}"`
4. `.color-swatch` elements with optional nested `.data-variant-image`

1. **Include** the module:

```html
   <script src="\{\{ 'component-product-card.js' | asset_url \}\}" type="module"></script>
```

With these pieces in place, shoppers can click swatches and see instant image updates—no page reload needed! 🎨

---