/**
 * Cart store.
 *
 * Owns cart state, serialises every mutation through one queue, asks Shopify
 * to render the cart sections in the same request, runs registered rules
 * after each successful mutation, and tells the page what changed.
 *
 * Layers:
 *   cart-api.js    → transport (this file is its only caller)
 *   cart-store.js  → state, queue, events, rules runner        ← you are here
 *   cart-rules.js  → the rules themselves (gift with purchase, kit integrity)
 *   component-*    → presentation; subscribe and swap HTML, never fetch
 *
 * Public API:  window.Cart
 *   state                       latest cart JSON
 *   pending                     number of jobs in flight
 *   add(items, options)         items: [{ id, quantity, properties, selling_plan }]
 *   change(key, quantity, options)
 *   update(payload, options)    payload: { note, attributes, discount, updates }
 *   clear(options)
 *   refresh()                   re-fetch state + sections without mutating
 *   subscribe(fn)               fn(detail); returns unsubscribe
 *   use(rule)                   rule(detail) → mutation[]; see runRules()
 *
 * Events on document (kept for third-party code and the data layer):
 *   'cart:change'  detail { action, payload, response, cart, previousCart, sections, source }
 *   'cart:error'   detail { action, payload, error: { status, message, description }, source }
 *
 * Section discovery:
 *   Any element carrying `data-cart-section` is re-rendered on every
 *   mutation. Its section id is read from the closest `.shopify-section`.
 *   If a section with id CART_JSON_SECTION is present on the page it is
 *   rendered too, and its JSON becomes the new state — so an add costs one
 *   request. Without it, the store falls back to a GET /cart.js after adds.
 */

import { cartApi } from './cart-api.js';

const CART_JSON_SECTION = 'cart-json';
const MAX_RULE_DEPTH = 2;
const BUSY_CLASS = 'cart-busy';

/* ------------------------------------------------------------------ state */

function readInitialState() {
  try {
    const el = document.getElementById('cart-data');
    return el ? JSON.parse(el.textContent) : null;
  } catch {
    return null;
  }
}

/**
 * Pulls cart JSON out of the rendered cart-json section, if it came back.
 * @param {Object|null} sections
 * @returns {Object|null}
 */
function stateFromSections(sections) {
  const html = sections?.[CART_JSON_SECTION];
  if (!html) return null;

  try {
    const doc = new DOMParser().parseFromString(html, 'text/html');
    const script = doc.querySelector('script[type="application/json"]');
    return script ? JSON.parse(script.textContent) : null;
  } catch {
    return null;
  }
}

/* --------------------------------------------------------------- sections */

function sectionIds() {
  const ids = new Set();

  for (const el of document.querySelectorAll('[data-cart-section]')) {
    const section = el.closest('.shopify-section');
    if (section) ids.add(section.id.replace('shopify-section-', ''));
  }

  if (document.getElementById(`shopify-section-${CART_JSON_SECTION}`)) ids.add(CART_JSON_SECTION);

  return [...ids];
}

/**
 * Strips the cart-json section from what consumers see — it is state, not UI.
 * @param {Object|null} sections
 */
function uiSections(sections) {
  if (!sections) return null;

  const { [CART_JSON_SECTION]: _ignored, ...rest } = sections;
  return Object.keys(rest).length ? rest : null;
}

/* ------------------------------------------------------------ count badge */

/**
 * Publishes the item count. <cart-count> (component-cart-count.js) and any
 * other subscriber render it — the store never writes to the header.
 * @param {number} count
 * @param {boolean} [optimistic] - true before the server has confirmed
 */
function renderCount(count, optimistic = false) {
  document.dispatchEvent(new CustomEvent('cart:count', { detail: { count, optimistic } }));
}

/* ------------------------------------------------------------------ queue */

let queue = Promise.resolve();
const listeners = new Set();
const rules = new Set();

function setPending(delta) {
  Cart.pending += delta;
  document.documentElement.classList.toggle(BUSY_CLASS, Cart.pending > 0);
}

function enqueue(task) {
  setPending(1);
  const job = queue.then(task).finally(() => setPending(-1));
  queue = job.catch(() => {});
  return job;
}

function emit(detail) {
  for (const fn of listeners) {
    try {
      fn(detail);
    } catch (error) {
      console.error('cart subscriber failed', error);
    }
  }

  document.dispatchEvent(new CustomEvent('cart:change', { detail }));
}

function emitError(action, payload, error, source) {
  document.dispatchEvent(
    new CustomEvent('cart:error', {
      detail: {
        action,
        payload,
        error: {
          status: error.status || 0,
          message: error.message,
          description: error.description || error.message,
        },
        source,
      },
    })
  );
}

/* ------------------------------------------------------------------ rules */

/**
 * A rule receives the same detail subscribers get and returns zero or more
 * mutations to apply:
 *   { type: 'add',    items }
 *   { type: 'change', key, quantity, properties? }
 *   { type: 'update', updates?, note?, attributes?, discount? }
 *
 * Rule-issued mutations carry `source: 'rule'` and a depth counter. Rules run
 * again on their results up to MAX_RULE_DEPTH, so a gift added by one rule is
 * still seen by a kit rule, but two rules fighting each other stop instead of
 * looping. Rules must be idempotent: given the same cart, return no mutations.
 */
async function runRules(detail, depth) {
  if (depth >= MAX_RULE_DEPTH || !rules.size) return;

  const mutations = [];

  for (const rule of rules) {
    try {
      const result = await rule(detail);
      if (Array.isArray(result)) mutations.push(...result);
    } catch (error) {
      console.error('cart rule failed', error);
    }
  }

  if (!mutations.length) return;

  if (depth === MAX_RULE_DEPTH - 1) {
    console.warn('cart rules still requesting changes at max depth; stopping', mutations);
    return;
  }

  const options = { source: 'rule', depth: depth + 1 };

  for (const mutation of mutations) {
    const { type, ...params } = mutation;

    if (type === 'add') await Cart.add(params.items, options).catch(() => {});
    if (type === 'change') await Cart.change(params.key, params.quantity, { ...options, properties: params.properties }).catch(() => {});
    if (type === 'update') await Cart.update(params, options).catch(() => {});
  }
}

/* --------------------------------------------------------------- mutation */

/**
 * @param {string} action
 * @param {*} payload - what the caller asked for, echoed in the event
 * @param {Object} options - { source, depth }
 * @param {(sections: string[]) => Promise<Object>} send
 */
function mutate(action, payload, options, send) {
  const { source = null, depth = 0 } = options;

  return enqueue(async () => {
    const previousCart = Cart.state;

    try {
      const response = await send(sectionIds());
      const sections = response.sections || null;

      let cart = stateFromSections(sections);

      if (!cart) {
        // change/update/clear return the cart; add returns { items } and
        // needs a follow-up when the cart-json section isn't on the page.
        if (action === 'add') {
          cart = await cartApi.get();
        } else {
          const { sections: _ignored, ...rest } = response;
          cart = rest;
        }
      }

      Cart.state = cart;
      renderCount(cart.item_count);

      const detail = { action, payload, response, cart, previousCart, sections: uiSections(sections), source };
      emit(detail);
      await runRules(detail, depth);

      return response;
    } catch (error) {
      renderCount(previousCart?.item_count ?? 0);
      emitError(action, payload, error, source);
      throw error;
    }
  });
}

/* ------------------------------------------------------------------- API */

const Cart = {
  state: readInitialState(),
  pending: 0,

  /**
   * @param {Array<{ id: number|string, quantity?: number, properties?: Object, selling_plan?: number|string }>} items
   * @param {{ source?: *, depth?: number }} [options]
   */
  add(items, options = {}) {
    const list = Array.isArray(items) ? items : [items];

    // Optimistic badge — reconciled or reverted when the response lands.
    const optimistic = (Cart.state?.item_count ?? 0) + list.reduce((sum, item) => sum + (Number(item.quantity) || 1), 0);
    renderCount(optimistic, true);

    return mutate('add', list, options, (sections) => cartApi.add({ items: list, sections }));
  },

  /**
   * @param {string} key - line_item.key
   * @param {number} quantity
   * @param {{ properties?: Object, sellingPlan?: number|string|null, source?: *, depth?: number }} [options]
   */
  change(key, quantity, options = {}) {
    const { properties, sellingPlan } = options;
    const payload = { key, quantity };

    return mutate('change', payload, options, (sections) =>
      cartApi.change({ key, quantity, properties, sellingPlan, sections })
    );
  },

  /**
   * @param {{ updates?: Object, note?: string, attributes?: Object, discount?: string }} payload
   * @param {{ source?: *, depth?: number, withSections?: boolean }} [options]
   */
  update(payload, options = {}) {
    const { withSections = true } = options;

    return mutate('update', payload, options, (sections) =>
      cartApi.update({ ...payload, sections: withSections ? sections : [] })
    );
  },

  /** @param {{ source?: *, depth?: number }} [options] */
  clear(options = {}) {
    return mutate('clear', null, options, (sections) => cartApi.clear({ sections }));
  },

  /** Re-fetches state and section HTML without mutating. Rules do not run. */
  refresh() {
    return enqueue(async () => {
      const previousCart = Cart.state;
      const ids = sectionIds();

      const [cart, sections] = await Promise.all([cartApi.get(), ids.length ? cartApi.sections(ids) : null]);

      Cart.state = cart;
      renderCount(cart.item_count);
      emit({ action: 'refresh', payload: null, response: cart, cart, previousCart, sections: uiSections(sections), source: null });

      return cart;
    });
  },

  /**
   * @param {(detail: Object) => void} fn
   * @returns {() => void} unsubscribe
   */
  subscribe(fn) {
    listeners.add(fn);
    return () => listeners.delete(fn);
  },

  /**
   * @param {(detail: Object) => (Object[]|Promise<Object[]>)} rule
   * @returns {() => void} remove the rule
   */
  use(rule) {
    rules.add(rule);
    return () => rules.delete(rule);
  },
};

window.Cart = Cart;

/* ------------------------------------------------------------------- boot */

if (Cart.state) {
  renderCount(Cart.state.item_count);
} else {
  cartApi
    .get()
    .then((cart) => {
      Cart.state = cart;
      renderCount(cart.item_count);
    })
    .catch(() => {});
}

export { Cart };
