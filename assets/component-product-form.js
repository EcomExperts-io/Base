/**
 * <product-form> — wraps one `{% form 'product' %}` and submits it through
 * Cart.add instead of a page load. Builds the `items[]` payload from the
 * form's fields, so a bundle builder or kit can extend it and add several
 * items in one request.
 *
 * Hooks in the wrapped markup (all optional):
 *   button[name="add"]      disabled while pending
 *   .loading__spinner       `.hidden` toggled while pending
 *   .form-error             receives the error description
 * @extends HTMLElement
 */
export class ProductForm extends HTMLElement {
  constructor() {
    super();
    this.onSubmit = this.onSubmit.bind(this);
  }

  connectedCallback() {
    this.form = this.querySelector('form[action*="/cart/add"]');
    this.form?.addEventListener('submit', this.onSubmit);
  }

  disconnectedCallback() {
    this.form?.removeEventListener('submit', this.onSubmit);
  }

  get button() {
    return this.form?.querySelector('button[name="add"], [type="submit"]');
  }

  /**
   * Translates the form's fields into Cart API items. Override in a subclass
   * to add more lines (kits) or shared properties (`_kit_id`).
   * @returns {Array<{ id: string, quantity: number, properties?: Object, selling_plan?: string }>}
   */
  buildItems() {
    const data = new FormData(this.form);
    const item = { id: data.get('id'), quantity: Number(data.get('quantity')) || 1 };
    const sellingPlan = data.get('selling_plan');
    if (sellingPlan) item.selling_plan = sellingPlan;

    const properties = {};

    for (const [name, value] of data.entries()) {
      const match = name.match(/^properties\[(.+)\]$/);
      if (match && value !== '') properties[match[1]] = value;
    }

    if (Object.keys(properties).length) item.properties = properties;

    return [item];
  }

  setPending(pending) {
    if (this.button) this.button.disabled = pending;
    this.form.querySelector('.loading__spinner')?.classList.toggle('hidden', !pending);
    this.toggleAttribute('aria-busy', pending);
  }

  showError(message) {
    const el = this.form.querySelector('.form-error');
    if (el) el.textContent = message;
  }

  async onSubmit(event) {
    event.preventDefault();
    if (!this.form.reportValidity()) return;

    this.showError('');
    this.setPending(true);

    try {
      await window.Cart.add(this.buildItems(), { source: this });
    } catch (error) {
      this.showError(error.description || error.message);
      // A 422 can still partially add (max available) — bring the UI back in sync.
      if (error.status === 422) window.Cart.refresh();
    } finally {
      this.setPending(false);
    }
  }
}

if (!customElements.get('product-form')) {
  customElements.define('product-form', ProductForm);
}
