/**
 * Native cart engine (replaces the liquid-ajax-cart library).
 *
 * Owns all Cart AJAX API calls, serializes them through a queue, and asks
 * Shopify to render the cart sections in the same request (Section Rendering
 * API) so cart components can re-render themselves.
 *
 * Public API:    window.Cart — { state, add, change, update, refresh }
 * Success event: document 'cart:change'
 *                detail { action, payload, response, cart, previousCart, sections, source }
 * Failure event: document 'cart:error'
 *                detail { action, payload, error: { status, message, description }, source }
 *
 * Add-to-cart posts FormData, so /cart/add.js responds with the added line
 * item at the top level — component-data-layer.js and
 * component-cart-notification.js rely on that shape.
 *
 * Wiring is event delegation on markup that already exists:
 *   - form[action*="/cart/add"] submits
 *   - a[href*="/cart/change"] clicks (quantity steppers + remove links)
 *   - .cart-quantity input and cart note textarea changes
 */

const ROOT = window.Shopify?.routes?.root || '/';

function readInitialState() {
  try {
    const el = document.getElementById('cart-data');
    return el ? JSON.parse(el.textContent) : null;
  } catch {
    return null;
  }
}

/* Section ids of the cart components currently on the page, read from their
   `.shopify-section` ancestors — nothing hardcoded. */
function sectionIds() {
  const ids = new Set();
  document.querySelectorAll('cart-drawer, cart-page').forEach((el) => {
    const section = el.closest('.shopify-section');
    if (section) ids.add(section.id.replace('shopify-section-', ''));
  });
  return [...ids];
}

function sectionParams(ids) {
  if (!ids.length) return {};
  return {
    sections: ids.join(','),
    sections_url: window.location.pathname + window.location.search,
  };
}

function syncCartCount(cart) {
  if (!cart) return;
  document.querySelectorAll('[data-cart-count]').forEach((el) => {
    el.textContent = cart.item_count;
  });
}

function jsonPost(body) {
  return {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(body),
  };
}

async function requestJson(url, options) {
  const response = await fetch(url, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(body.message || response.statusText);
    error.status = response.status;
    error.description = body.description || body.message || 'Something went wrong. Please try again.';
    throw error;
  }
  return body;
}

/* All mutations run through one promise chain so rapid clicks can't race. */
let queue = Promise.resolve();
let pendingJobs = 0;

function enqueue(task) {
  pendingJobs += 1;
  document.documentElement.classList.add('cart-busy');
  const job = queue.then(task).finally(() => {
    pendingJobs -= 1;
    if (pendingJobs === 0) document.documentElement.classList.remove('cart-busy');
  });
  queue = job.catch(() => {});
  return job;
}

function mutate(action, payload, source, runRequest, { withSections = true } = {}) {
  return enqueue(async () => {
    const previousCart = Cart.state;
    try {
      const response = await runRequest(withSections ? sectionIds() : []);
      const sections = response.sections || null;

      if (action === 'add') {
        // FormData add responses are the line item, not the cart
        Cart.state = await requestJson(`${ROOT}cart.js`);
      } else {
        const cart = { ...response };
        delete cart.sections;
        Cart.state = cart;
      }

      syncCartCount(Cart.state);
      document.dispatchEvent(
        new CustomEvent('cart:change', {
          detail: { action, payload, response, cart: Cart.state, previousCart, sections, source },
        })
      );
      return response;
    } catch (error) {
      document.dispatchEvent(
        new CustomEvent('cart:error', {
          detail: {
            action,
            payload,
            error: { status: error.status || 0, message: error.message, description: error.description || error.message },
            source,
          },
        })
      );
      throw error;
    }
  });
}

const Cart = {
  state: readInitialState(),

  add(formData, source) {
    return mutate('add', formData, source, (ids) => {
      const params = sectionParams(ids);
      Object.keys(params).forEach((key) => formData.append(key, params[key]));
      return requestJson(`${ROOT}cart/add.js`, { method: 'POST', body: formData });
    });
  },

  /** payload: { line, quantity } or { id, quantity } */
  change(payload, source) {
    return mutate('change', payload, source, (ids) =>
      requestJson(`${ROOT}cart/change.js`, jsonPost({ ...payload, ...sectionParams(ids) }))
    );
  },

  /** payload: { note } / { attributes } */
  update(payload, source, options) {
    return mutate(
      'update',
      payload,
      source,
      (ids) => requestJson(`${ROOT}cart/update.js`, jsonPost({ ...payload, ...sectionParams(ids) })),
      options
    );
  },

  /** Re-fetches state + section HTML without mutating — used after external
      cart changes (e.g. the discount form does its own requests). */
  refresh() {
    return enqueue(async () => {
      const previousCart = Cart.state;
      const ids = sectionIds();
      Cart.state = await requestJson(`${ROOT}cart.js`);
      const sections = ids.length ? await requestJson(`${ROOT}?sections=${ids.join(',')}`) : null;

      syncCartCount(Cart.state);
      document.dispatchEvent(
        new CustomEvent('cart:change', {
          detail: { action: 'refresh', payload: null, response: Cart.state, cart: Cart.state, previousCart, sections, source: null },
        })
      );
      return Cart.state;
    });
  },
};

window.Cart = Cart;

syncCartCount(Cart.state);
if (!Cart.state) {
  requestJson(`${ROOT}cart.js`)
    .then((cart) => {
      Cart.state = cart;
      syncCartCount(cart);
    })
    .catch(() => {});
}

/* ----- add-to-cart forms ----- */

document.addEventListener('submit', (event) => {
  const form = event.target;
  if (!(form instanceof HTMLFormElement)) return;
  if (!(form.getAttribute('action') || '').includes('/cart/add')) return;
  event.preventDefault();

  const button = form.querySelector('button[name="add"], [type="submit"]');
  const spinner = button?.querySelector('.loading__spinner');
  const errorEl = form.querySelector('.form-error');
  if (errorEl) errorEl.textContent = '';
  if (button) button.disabled = true;
  spinner?.classList.remove('hidden');

  Cart.add(new FormData(form), form)
    .catch((error) => {
      if (errorEl) errorEl.textContent = error.description;
      // A 422 can still partially add (max available) — re-sync the UI
      Cart.refresh();
    })
    .finally(() => {
      if (button) button.disabled = false;
      spinner?.classList.add('hidden');
    });
});

/* ----- line quantity changes (steppers, remove links, typed input) ----- */

const lineDebounce = new Map();

/* `/cart/change` links can target the line by 1-based index (`line=`) or by
   line item key (`id=`) — accept both. Returns null for anything else so the
   click falls back to native navigation. */
function lineTarget(link) {
  const params = new URL(link.href, window.location.origin).searchParams;
  const line = parseInt(params.get('line'), 10);
  if (line) return { line };
  const id = params.get('id');
  if (id) return { id };
  return null;
}

function changeLine(target, quantity, source) {
  Cart.change({ ...target, quantity }, source).catch((error) => {
    const item = source.closest('.cart-item');
    const errorEl = item?.querySelector('.cart-item__error');
    if (errorEl) errorEl.textContent = error.description;
    const input = item?.querySelector('.cart-quantity input');
    if (input) input.value = input.defaultValue;
  });
}

/* Collapses rapid +/- clicks into one request with the final quantity. */
function queueLineChange(target, quantity, source) {
  const key = target.line || target.id;
  clearTimeout(lineDebounce.get(key));
  lineDebounce.set(
    key,
    setTimeout(() => {
      lineDebounce.delete(key);
      changeLine(target, quantity, source);
    }, 250)
  );
}

document.addEventListener('click', (event) => {
  // The remove row's icon sits beside the link, not inside it — treat a click
  // anywhere in the row as a click on its link.
  const removeRow = event.target.closest('.cart-item__remove');
  const link =
    event.target.closest('a[href*="/cart/change"]') ||
    removeRow?.querySelector('a[href*="/cart/change"]');
  if (!link) return;

  const target = lineTarget(link);
  if (!target) return;
  event.preventDefault();

  const params = new URL(link.href, window.location.origin).searchParams;
  const stepper = link.closest('.cart-quantity');
  if (!stepper) {
    // remove link — href already carries quantity=0
    changeLine(target, parseInt(params.get('quantity'), 10) || 0, link);
    return;
  }

  // Step from the input's current value, not the href, so quick successive
  // clicks accumulate correctly; defaultValue is the server-rendered quantity.
  const input = stepper.querySelector('input');
  const direction = parseInt(params.get('quantity'), 10) >= parseInt(input.defaultValue, 10) ? 1 : -1;
  const quantity = Math.max(0, (parseInt(input.value, 10) || 0) + direction);
  input.value = quantity;
  queueLineChange(target, quantity, link);
});

document.addEventListener('change', (event) => {
  const target = event.target;

  if (target.matches('.cart-quantity input')) {
    const link = target.closest('.cart-quantity')?.querySelector('a[href*="/cart/change"]');
    if (!link) return;
    const lineRef = lineTarget(link);
    if (!lineRef) return;
    const quantity = Math.max(0, parseInt(target.value, 10) || 0);
    target.value = quantity;
    queueLineChange(lineRef, quantity, target);
    return;
  }

  if (target.matches('cart-drawer textarea[name="note"], cart-page textarea[name="note"]')) {
    Cart.update({ note: target.value }, target, { withSections: false }).catch((error) => {
      console.warn('Cart note update failed:', error.message);
    });
  }
});
