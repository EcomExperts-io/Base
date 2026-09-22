/**
 * Cart rules — behaviour that reacts to the cart after every mutation.
 *
 * A rule is `(detail) => mutation[]` registered with Cart.use(). It reads
 * cart state, decides, and returns mutations for the store to queue. Rules
 * never touch the DOM and never fetch. They must be idempotent: given the
 * same cart twice, the second run returns nothing.
 *
 * Config comes from Liquid via <script type="application/json" id="cart-rules-config">
 * (snippets/component-cart-rules.liquid), never hardcoded here.
 *
 * Property vocabulary (underscore = hidden in cart and checkout):
 *   _gwp        gift rule id; the line is a locked free gift
 *   _kit_id     shared id across every line of one kit
 *   _kit_role   'parent' | 'child'
 */

import { Cart } from './cart-store.js';

function readConfig() {
  try {
    const el = document.getElementById('cart-rules-config');
    return el ? JSON.parse(el.textContent) : {};
  } catch {
    return {};
  }
}

const config = readConfig();

/**
 * Gift with purchase.
 *
 * When the cart's total (excluding the gift itself) meets the threshold, add
 * the gift variant with `_gwp`. When it no longer does, remove it. Keep its
 * quantity pinned to 1. The gift is made free by an automatic Buy X Get Y
 * discount in Admin at the same threshold — this rule only manages the line.
 *
 * config.gwp: { id: string, variant_id: number, threshold: number (cents) }
 */
export function giftWithPurchase({ cart }) {
  const gwp = config.gwp;
  if (!gwp?.variant_id || !gwp.threshold) return [];

  const gift = cart.items.find((item) => item.properties?._gwp === gwp.id);
  const giftTotal = gift ? gift.final_line_price : 0;
  const qualifies = cart.total_price - giftTotal >= gwp.threshold;

  if (qualifies && !gift) {
    return [{ type: 'add', items: [{ id: gwp.variant_id, quantity: 1, properties: { _gwp: gwp.id } }] }];
  }

  if (!qualifies && gift) {
    return [{ type: 'change', key: gift.key, quantity: 0 }];
  }

  if (gift && gift.quantity !== 1) {
    return [{ type: 'change', key: gift.key, quantity: 1 }];
  }

  return [];
}

/**
 * Kit integrity.
 *
 * Lines sharing a `_kit_id` are one kit. If the parent is gone, the children
 * go too. If a child is gone, the whole kit is removed — a kit without all its
 * parts is not the thing the customer chose.
 */
export function kitIntegrity({ cart, previousCart }) {
  if (!previousCart) return [];

  const kits = new Map();

  for (const item of cart.items) {
    const kitId = item.properties?._kit_id;
    if (!kitId) continue;
    if (!kits.has(kitId)) kits.set(kitId, []);
    kits.get(kitId).push(item);
  }

  const previousKits = new Set(previousCart.items.map((item) => item.properties?._kit_id).filter(Boolean));
  const removals = [];

  for (const [kitId, lines] of kits) {
    const hasParent = lines.some((line) => line.properties?._kit_role === 'parent');
    const previousSize = previousCart.items.filter((item) => item.properties?._kit_id === kitId).length;
    const broken = !hasParent || (previousKits.has(kitId) && lines.length < previousSize);

    if (!broken) continue;

    for (const line of lines) removals.push({ type: 'change', key: line.key, quantity: 0 });
  }

  return removals;
}

if (config.gwp?.enabled) Cart.use(giftWithPurchase);
Cart.use(kitIntegrity);
