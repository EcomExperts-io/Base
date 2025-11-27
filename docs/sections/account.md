# Account Section (`sections/account.liquid`)

`sections/account.liquid` renders the customer account dashboard page, displaying order history in a paginated table and account details including the default address. It provides a logout link and maintains responsive spacing through dynamic padding controls.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `customer.css`, inline `{% style %}` block for responsive padding |
| Icons | `icon-account.svg`, `icon-caret.svg` (inline via `inline_asset_content`) |
| Data | Relies on the `customer` object (orders, addresses, default_address) |

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
{{ 'customer.css' | asset_url | stylesheet_tag }}

<div class="customer account section-{{ section.id }}-padding">
  <div>
    <!-- Header with title and logout -->
  </div>

  <div>
    <!-- Order history table -->
    <!-- Account details -->
  </div>
</div>
```

### Header

```liquid
<div>
  <h1 class="customer__title">{{ 'customer.account.title' | t }}</h1>
  <a href="{{ routes.account_logout_url }}">
    <span class="svg-wrapper">
      {{- 'icon-account.svg' | inline_asset_content -}}
    </span>
    {{ 'customer.log_out' | t }}
  </a>
</div>
```

- Displays the localized account title and a logout link with an inline icon.

### Order History

```liquid
<div>
  <h2>{{ 'customer.orders.title' | t }}</h2>

  {% paginate customer.orders by 20 %}
    {%- if customer.orders.size > 0 -%}
      <table role="table" class="order-history">
        <caption class="visually-hidden">
          {{ 'customer.orders.title' | t }}
        </caption>
        <thead role="rowgroup">
          <tr role="row">
            <th id="ColumnOrder" scope="col" role="columnheader">
              {{ 'customer.orders.order_number' | t }}
            </th>
            <th id="ColumnDate" scope="col" role="columnheader">
              {{ 'customer.orders.date' | t }}
            </th>
            <th id="ColumnPayment" scope="col" role="columnheader">
              {{ 'customer.orders.payment_status' | t }}
            </th>
            <th id="ColumnFulfillment" scope="col" role="columnheader">
              {{ 'customer.orders.fulfillment_status' | t }}
            </th>
            <th id="ColumnTotal" scope="col" role="columnheader">
              {{ 'customer.orders.total' | t }}
            </th>
          </tr>
        </thead>
        <tbody role="rowgroup">
          {%- for order in customer.orders -%}
            <tr role="row">
              <td
                id="RowOrder"
                role="cell"
                headers="ColumnOrder"
                data-label="{{ 'customer.orders.order_number' | t }}"
              >
                <a
                  href="{{ order.customer_url }}"
                  aria-label="{{ 'customer.orders.order_number_link' | t: number: order.name }}"
                >
                  {{ order.name }}
                </a>
              </td>
              <td headers="RowOrder ColumnDate" role="cell" data-label="{{ 'customer.orders.date' | t }}">
                {{ order.created_at | time_tag: format: 'date' }}
              </td>
              <td
                headers="RowOrder ColumnPayment"
                role="cell"
                data-label="{{ 'customer.orders.payment_status' | t }}"
              >
                {{ order.financial_status_label }}
              </td>
              <td
                headers="RowOrder ColumnFulfillment"
                role="cell"
                data-label="{{ 'customer.orders.fulfillment_status' | t }}"
              >
                {{ order.fulfillment_status_label }}
              </td>
              <td headers="RowOrder ColumnTotal" role="cell" data-label="{{ 'customer.orders.total' | t }}">
                {{ order.total_net_amount | money_with_currency }}
              </td>
            </tr>
          {%- endfor -%}
        </tbody>
      </table>
    {%- else -%}
      <p>{{ 'customer.orders.none' | t }}</p>
    {%- endif -%}
    <!-- Pagination -->
  {% endpaginate %}
</div>
```

- **Accessibility**: Full ARIA roles (`role="table"`, `role="row"`, `role="cell"`), `headers` attributes linking cells to column headers, and `data-label` for mobile screen readers.
- **Pagination**: Shows 20 orders per page; pagination controls appear when `paginate.pages > 1`.
- **Empty state**: Displays a localized message when no orders exist.
- **Order links**: Each order number links to `order.customer_url` for detailed order pages.

### Pagination

```liquid
{%- if paginate.pages > 1 -%}
  {%- if paginate.parts.size > 0 -%}
    <nav class="pagination" role="navigation" aria-label="{{ 'general.pagination.label' | t }}">
      <ul role="list">
        {%- if paginate.previous -%}
          <li>
            <a href="{{ paginate.previous.url }}" aria-label="{{ 'general.pagination.previous' | t }}">
              <span class="svg-wrapper">
                {{- 'icon-caret.svg' | inline_asset_content -}}
              </span>
            </a>
          </li>
        {%- endif -%}

        {%- for part in paginate.parts -%}
          <li>
            {%- if part.is_link -%}
              <a href="{{ part.url }}" aria-label="{{ 'general.pagination.page' | t: number: part.title }}">
                {{- part.title -}}
              </a>
            {%- else -%}
              {%- if part.title == paginate.current_page -%}
                <span aria-current="page" aria-label="{{ 'general.pagination.page' | t: number: part.title }}">
                  {{- part.title -}}
                </span>
              {%- else -%}
                <span>{{ part.title }}</span>
              {%- endif -%}
            {%- endif -%}
          </li>
        {%- endfor -%}

        {%- if paginate.next -%}
          <li>
            <a href="{{ paginate.next.url }}" aria-label="{{ 'general.pagination.next' | t }}">
              <span class="svg-wrapper">
                {{- 'icon-caret.svg' | inline_asset_content -}}
              </span>
            </a>
          </li>
        {%- endif -%}
      </ul>
    </nav>
  {%- endif -%}
{%- endif -%}
```

- Previous/next links use caret icons (`icon-caret.svg`).
- Current page is marked with `aria-current="page"`.
- Ellipsis pages (non-clickable) are rendered as plain spans.

### Account Details

```liquid
<div>
  <h2>{{ 'customer.account.details' | t }}</h2>

  {{ customer.default_address | format_address }}

  <a href="{{ routes.account_addresses_url }}">
    {{ 'customer.account.view_addresses' | t }} ({{ customer.addresses_count }})
  </a>
</div>
```

- Uses Shopify's `format_address` filter to render the default address.
- Links to the addresses management page with a count of saved addresses.

---

## Behavior

- **Purely presentational**: No JavaScript interactions; all navigation is handled via standard links.
- **Server-side pagination**: Order pagination uses Liquid's `paginate` tag with 20 items per page.
- **Responsive design**: Table uses `data-label` attributes for mobile-friendly display (typically shown via CSS).
- **Accessibility**: Full ARIA support for screen readers, semantic HTML structure, and keyboard navigation.

---

## Schema

```json
{
  "name": "t:sections.main-account.name",
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

- Merchants can control vertical spacing (0–100px, default 36px).
- No blocks defined; the account layout is fixed.
- All setting labels use translation keys for localization.

---

## Implementation Notes

1. **Translation keys**: All user-facing text must use translation filters (`customer.account.title`, `customer.orders.*`, `general.pagination.*`, etc.).
2. **Icon dependencies**: Ensure `icon-account.svg` and `icon-caret.svg` exist in `assets/`; missing icons will break the UI.
3. **Customer object**: This section requires a logged-in customer; the `customer` object is only available on authenticated account pages.
4. **Table accessibility**: The table structure with `headers` and `data-label` attributes supports both desktop and mobile screen readers. Ensure CSS handles `data-label` display on small screens.
5. **Address formatting**: The `format_address` filter automatically formats the address according to Shopify's locale settings.
6. **Pagination limit**: Orders are paginated at 20 per page; this is hardcoded in the `paginate` tag and cannot be changed via settings.

