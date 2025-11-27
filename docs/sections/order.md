# Order Section (`sections/order.liquid`)

`sections/order.liquid` renders the individual order detail page, displaying comprehensive order information including line items, pricing, discounts, shipping, taxes, and addresses. The section includes a detailed table with full accessibility support, fulfillment tracking, and responsive padding controls.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `customer.css`, inline `{% style %}` block for responsive padding |
| Icons | `icon-discount.svg` (inline via `inline_asset_content`) |
| Data | Relies on the `order` object (line items, addresses, fulfillment, discounts, taxes) |

- No JavaScript dependencies; the section is purely presentational.
- All text uses translation keys for localization.
- Icons are embedded inline via the `inline_asset_content` filter.

---

## Dynamic Styles

Inline styles generate responsive padding that scales down on mobile:

```liquid
{%- style -%}
  .section-{{ section.id }}-padding {
    padding-top: {{ section.settings.padding_top | times: 0.75 | round: 0 }}px;
    padding-bottom: {{ section.settings.padding_bottom | times: 0.75 | round: 0 }}px;
  }

  @media screen and (min-width: 750px) {
    .section-{{ section.id }}-padding {
      padding-top: {{ section.settings.padding_top }}px;
      padding-bottom: {{ section.settings.padding_bottom }}px;
    }
  }
{%- endstyle -%}
```

- Mobile uses 75% of the configured padding value (rounded to whole pixels).
- Desktop (≥750px) uses the full padding value from settings.
- Padding values range from 0–100px in 4px increments.

---

## Markup Structure

```liquid
<div class="customer order section-{{ section.id }}-padding">
  <div>
    <h1 class="customer__title">{{ 'customer.account.title' | t }}</h1>
    <a href="{{ routes.account_url }}">{{ 'customer.account.return' | t }}</a>
  </div>

  <div>
    <!-- Order header with title, date, cancellation info -->
    <!-- Order details table -->
    <!-- Billing and shipping addresses -->
  </div>
</div>
```

- Header section with account title and return link.
- Order information section with table and address blocks.

### Order Header

```liquid
<div>
  <h2>{{ 'customer.order.title' | t: name: order.name }}</h2>
  {%- assign order_date = order.created_at | time_tag: format: 'date_at_time' -%}
  <p>{{ 'customer.order.date_html' | t: date: order_date }}</p>
  {%- if order.cancelled -%}
    {%- assign cancelled_at = order.cancelled_at | time_tag: format: 'date_at_time' -%}
    <p>{{ 'customer.order.cancelled_html' | t: date: cancelled_at }}</p>
    <p>{{ 'customer.order.cancelled_reason' | t: reason: order.cancel_reason_label }}</p>
  {%- endif -%}
</div>
```

- Displays order name, creation date, and cancellation information (if applicable).
- Date formatting uses `time_tag` filter with `date_at_time` format.
- Cancellation details only show when `order.cancelled` is true.

### Order Details Table

```liquid
<table role="table" class="order-details">
  <caption class="visually-hidden">
    {{ 'customer.order.title' | t: name: order.name }}
  </caption>
  <thead role="rowgroup">
    <tr role="row">
      <th id="ColumnProduct" scope="col" role="columnheader">{{ 'customer.order.product' | t }}</th>
      <th id="ColumnSku" scope="col" role="columnheader">{{ 'customer.order.sku' | t }}</th>
      <th id="ColumnPrice" scope="col" role="columnheader">{{ 'customer.order.price' | t }}</th>
      <th id="ColumnQuantity" scope="col" role="columnheader">{{ 'customer.order.quantity' | t }}</th>
      <th id="ColumnTotal" scope="col" role="columnheader">{{ 'customer.order.total' | t }}</th>
    </tr>
  </thead>
  <tbody role="rowgroup">
    {%- for line_item in order.line_items -%}
      <!-- Line item rows -->
    {%- endfor -%}
  </tbody>
  <tfoot role="rowgroup">
    <!-- Subtotal, discounts, shipping, taxes, duties, refunds, total -->
  </tfoot>
</table>
```

- **Accessibility**: Full ARIA roles, `headers` attributes, and `data-label` for mobile screen readers.
- **Table structure**: Product, SKU, Price, Quantity, and Total columns.
- **Footer**: Contains order totals, discounts, shipping, taxes, and refunds.

### Line Item Details

```liquid
<td id="Row{{ line_item.key }}" headers="ColumnProduct" role="rowheader" scope="row" data-label="{{ 'customer.order.product' | t }}">
  <div>
    {%- if line_item.url != blank -%}
      <a href="{{ line_item.url }}">{{ line_item.title | escape }}</a>
    {%- else -%}
      <p>{{ line_item.title | escape }}</p>
    {%- endif -%}
    
    <!-- Variant, selling plan, and custom properties -->
    <!-- Line-level discounts -->
    <!-- Fulfillment information -->
  </div>
</td>
```

- **Product link**: Links to product page when `line_item.url` is available.
- **Variant display**: Shows variant title when product has multiple variants.
- **Selling plans**: Displays subscription plan name when applicable.
- **Custom properties**: Renders product properties (excluding those starting with `_`).
- **File uploads**: Properties containing `/uploads/` are rendered as download links.
- **Line-level discounts**: Shows discount applications with icons and amounts.
- **Fulfillment tracking**: Displays fulfillment date, tracking URL, company, and tracking number.

### Price Display

```liquid
<td headers="Row{{ line_item.key }} ColumnPrice" role="cell" data-label="{{ 'customer.order.price' | t }}">
  {%- if line_item.original_price != line_item.final_price or line_item.unit_price_measurement -%}
    <dl>
      {%- if line_item.original_price != line_item.final_price -%}
        <dt><span class="visually-hidden">{{ 'products.product.price.regular_price' | t }}</span></dt>
        <dd class="regular-price"><s>{{ line_item.original_price | money }}</s></dd>
        <dt><span class="visually-hidden">{{ 'products.product.price.sale_price' | t }}</span></dt>
        <dd><span>{{ line_item.final_price | money }}</span></dd>
      {%- else -%}
        <dt><span class="visually-hidden">{{ 'products.product.price.regular_price' | t }}</span></dt>
        <dd>{{ line_item.original_price | money }}</dd>
      {%- endif -%}
      {%- if line_item.unit_price_measurement -%}
        <!-- Unit price display -->
      {%- endif -%}
    </dl>
  {%- else -%}
    <span>{{ line_item.final_price | money }}</span>
  {%- endif -%}
</td>
```

- **Price comparison**: Shows original price (strikethrough) and final price when discounted.
- **Unit pricing**: Displays unit price with reference unit when `unit_price_measurement` is available.
- **Accessibility**: Uses `<dl>`, `<dt>`, `<dd>` structure with visually hidden labels for screen readers.

### Order Totals (Table Footer)

```liquid
<tfoot role="rowgroup">
  <tr role="row">
    <td id="RowSubtotal" role="rowheader" scope="row" colspan="4">
      {{ 'customer.order.subtotal' | t }}
    </td>
    <td headers="RowSubtotal" role="cell" data-label="{{ 'customer.order.subtotal' | t }}">
      {{ order.line_items_subtotal_price | money }}
    </td>
  </tr>
  <!-- Cart-level discounts -->
  <!-- Shipping methods -->
  <!-- Tax lines -->
  <!-- Duties (if applicable) -->
  <!-- Refunds (if applicable) -->
  <!-- Total -->
</tfoot>
```

- **Subtotal**: Sum of all line item prices before discounts.
- **Cart-level discounts**: Shows discount applications with icons and amounts.
- **Shipping**: Displays each shipping method with title and price.
- **Taxes**: Shows each tax line with title, rate percentage, and amount.
- **Duties**: Conditionally displays when `order.total_duties` is present.
- **Refunds**: Conditionally displays when `order.total_refunded_amount > 0`.
- **Total**: Final order total using `order.total_net_amount`.

### Addresses

```liquid
<div class="order-addresses">
  <div>
    <h2>{{ 'customer.order.billing_address' | t }}</h2>
    <p>
      <strong>{{ 'customer.order.payment_status' | t }}:</strong>
      {{ order.financial_status_label }}
    </p>
    {{ order.billing_address | format_address }}
  </div>
  <div>
    <h2>{{ 'customer.order.shipping_address' | t }}</h2>
    <p>
      <strong>{{ 'customer.order.fulfillment_status' | t }}:</strong>
      {{ order.fulfillment_status_label }}
    </p>
    {{ order.shipping_address | format_address }}
  </div>
</div>
```

- **Billing address**: Displays payment status and formatted billing address.
- **Shipping address**: Displays fulfillment status and formatted shipping address.
- **Address formatting**: Uses Shopify's `format_address` filter for proper localization.

---

## Behavior

- **Purely presentational**: No JavaScript interactions; all content rendered server-side.
- **Accessibility**: Full ARIA support with proper table semantics, `headers` attributes, and `data-label` for mobile.
- **Conditional rendering**: Various sections (cancellation, discounts, fulfillment, taxes, duties, refunds) only render when applicable.
- **Responsive design**: Table uses `data-label` attributes for mobile-friendly display (typically shown via CSS).

---

## Schema

```json
{
  "name": "t:sections.main-order.name",
  "settings": [
    {
      "type": "header",
      "content": "t:sections.all.padding.section_padding_heading"
    },
    {
      "type": "range",
      "id": "padding_top",
      "min": 0,
      "max": 100,
      "step": 4,
      "unit": "px",
      "label": "t:sections.all.padding.padding_top",
      "default": 36
    },
    {
      "type": "range",
      "id": "padding_bottom",
      "min": 0,
      "max": 100,
      "step": 4,
      "unit": "px",
      "label": "t:sections.all.padding.padding_bottom",
      "default": 36
    }
  ]
}
```

### Section Settings

| Setting ID | Type | Default | Purpose |
|------------|------|---------|---------|
| `padding_top` | range (px) | 36 | Top padding (0–100px, step 4) |
| `padding_bottom` | range (px) | 36 | Bottom padding (0–100px, step 4) |

---

## Implementation Notes

1. **Translation keys**: All user-facing text uses translation filters (`customer.order.*`, `customer.account.*`, `products.product.price.*`, etc.).

2. **Icon dependency**: Ensure `icon-discount.svg` exists in `assets/`; missing icons will break discount displays.

3. **Order object**: This section requires an `order` object context. It's typically used on order detail template pages where Shopify automatically provides the order object.

4. **Table accessibility**: The table structure with `headers` and `data-label` attributes supports both desktop and mobile screen readers. Ensure CSS handles `data-label` display on small screens.

5. **Custom properties filtering**: Line item properties starting with `_` are hidden (common pattern for internal properties). Only properties with non-blank values are displayed.

6. **File upload handling**: Custom properties containing `/uploads/` are treated as file uploads and rendered as download links with the filename extracted from the URL.

7. **Fulfillment tracking**: Tracking information displays when `line_item.fulfillment` exists, including:
   - Fulfillment date
   - Tracking URL (as clickable link)
   - Tracking company name
   - Tracking number (prefixed with `#`)

8. **Price display logic**: Price column uses complex conditional logic:
   - Shows comparison prices when discounted
   - Shows unit pricing when available
   - Uses semantic HTML (`<dl>`, `<dt>`, `<dd>`) for accessibility

9. **Discount display**: Both line-level and cart-level discounts are displayed with discount icons and formatted amounts.

10. **Tax calculation**: Tax rate is displayed as percentage by multiplying `tax_line.rate` by 100.

11. **Address formatting**: Uses Shopify's `format_address` filter which automatically formats addresses according to locale settings.

12. **Responsive breakpoint**: Desktop padding applies at 750px; ensure this aligns with the theme's global breakpoint strategy.

13. **Row IDs**: Table rows use `line_item.key` for unique row identification, ensuring proper `headers` attribute associations.

14. **Colspan usage**: Footer rows use `colspan` attributes to span multiple columns for proper table structure.

15. **Money formatting**: All prices use `money` or `money_with_currency` filters for proper localization and currency display.

