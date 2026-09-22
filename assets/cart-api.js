/**
 * Cart transport layer.
 *
 * The only file in the theme that knows a `/cart/*.js` URL. It sends requests,
 * parses responses and normalises errors. It holds no state, touches no DOM,
 * and dispatches no events — that is cart-store.js's job.
 *
 * Every mutation accepts an optional `sections` array (section ids) and
 * `sectionsUrl`. When present they are forwarded so Shopify renders those
 * sections in the same response (Section Rendering API), under
 * `response.sections`.
 *
 * Every add/change/update posts JSON, so:
 *   - add() responds with `{ items: [...] }` — the added lines, not the cart
 *   - change() / update() / clear() respond with the full cart
 *
 * Line items are always addressed by `key` (line_item.key), never by index.
 *
 * Errors thrown are `CartApiError` with `status`, `message`, `description`
 * and `errors` (Shopify's raw error body).
 */

const ROOT = window.Shopify?.routes?.root || '/';

export class CartApiError extends Error {
  /**
   * @param {number} status - HTTP status, 0 for network failures
   * @param {Object} body - parsed error body from Shopify
   */
  constructor(status, body = {}) {
    super(body.message || body.description || 'Cart request failed');
    this.name = 'CartApiError';
    this.status = status;
    this.description = body.description || body.message || '';
    this.errors = body.errors || null;
  }
}

/**
 * @param {string[]} [sections]
 * @param {string} [sectionsUrl]
 * @returns {Object} the Section Rendering params to merge into a body
 */
function sectionParams(sections, sectionsUrl) {
  if (!sections?.length) return {};

  return {
    sections: sections.join(','),
    sections_url: sectionsUrl || window.location.pathname + window.location.search,
  };
}

/**
 * @param {string} path - path under the shop root, e.g. 'cart/add.js'
 * @param {Object} [body] - JSON body; omit for GET
 * @param {AbortSignal} [signal]
 */
async function request(path, body, signal) {
  const options = {
    method: body ? 'POST' : 'GET',
    headers: { Accept: 'application/json' },
    signal,
  };

  if (body) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(body);
  }

  let response;

  try {
    response = await fetch(`${ROOT}${path}`, options);
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new CartApiError(0, { message: error.message });
  }

  const parsed = await response.json().catch(() => ({}));

  if (!response.ok) throw new CartApiError(response.status, parsed);

  return parsed;
}

export const cartApi = {
  /**
   * @param {{ signal?: AbortSignal }} [options]
   * @returns {Promise<Object>} the cart
   */
  get({ signal } = {}) {
    return request('cart.js', undefined, signal);
  },

  /**
   * @param {Object} params
   * @param {Array<{ id: number|string, quantity?: number, properties?: Object, selling_plan?: number|string }>} params.items
   * @param {string[]} [params.sections]
   * @param {string} [params.sectionsUrl]
   * @param {AbortSignal} [params.signal]
   * @returns {Promise<{ items: Object[], sections?: Object }>}
   */
  add({ items, sections, sectionsUrl, signal }) {
    return request('cart/add.js', { items, ...sectionParams(sections, sectionsUrl) }, signal);
  },

  /**
   * @param {Object} params
   * @param {string} params.key - line_item.key
   * @param {number} params.quantity
   * @param {Object} [params.properties] - replaces the line's properties when given
   * @param {number|string|null} [params.sellingPlan] - replaces the line's selling plan when given
   * @param {string[]} [params.sections]
   * @param {string} [params.sectionsUrl]
   * @param {AbortSignal} [params.signal]
   * @returns {Promise<Object>} the cart
   */
  change({ key, quantity, properties, sellingPlan, sections, sectionsUrl, signal }) {
    const body = { id: key, quantity, ...sectionParams(sections, sectionsUrl) };

    if (properties !== undefined) body.properties = properties;
    if (sellingPlan !== undefined) body.selling_plan = sellingPlan;

    return request('cart/change.js', body, signal);
  },

  /**
   * @param {Object} params
   * @param {Object<string, number>} [params.updates] - `{ [key]: quantity }`
   * @param {string} [params.note]
   * @param {Object} [params.attributes]
   * @param {string} [params.discount] - comma-separated codes; empty string clears
   * @param {string[]} [params.sections]
   * @param {string} [params.sectionsUrl]
   * @param {AbortSignal} [params.signal]
   * @returns {Promise<Object>} the cart
   */
  update({ updates, note, attributes, discount, sections, sectionsUrl, signal }) {
    const body = { ...sectionParams(sections, sectionsUrl) };

    if (updates !== undefined) body.updates = updates;
    if (note !== undefined) body.note = note;
    if (attributes !== undefined) body.attributes = attributes;
    if (discount !== undefined) body.discount = discount;

    return request('cart/update.js', body, signal);
  },

  /**
   * @param {{ sections?: string[], sectionsUrl?: string, signal?: AbortSignal }} [params]
   * @returns {Promise<Object>} the emptied cart
   */
  clear({ sections, sectionsUrl, signal } = {}) {
    return request('cart/clear.js', { ...sectionParams(sections, sectionsUrl) }, signal);
  },

  /**
   * Renders sections without mutating the cart.
   * @param {string[]} sections
   * @param {{ url?: string, signal?: AbortSignal }} [options] - `url` is the page to render against
   * @returns {Promise<Object<string, string>>} section id → HTML
   */
  async sections(sections, { url, signal } = {}) {
    if (!sections?.length) return {};

    const target = new URL(url || window.location.href, window.location.origin);
    target.searchParams.set('sections', sections.join(','));

    const response = await fetch(target, { headers: { Accept: 'application/json' }, signal });

    if (!response.ok) throw new CartApiError(response.status, {});

    return response.json();
  },
};
