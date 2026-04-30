function escapeHtml(value) {
  if (value == null) return ''
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

/** Parse money_without_currency style value; returns null if invalid. */
function parsePriceNumber(raw) {
  if (raw == null || String(raw).trim() === '') return null
  const n = parseFloat(String(raw))
  return Number.isFinite(n) ? n : null
}

/** Shopify variant prices are in minor units (cents for USD). */
function moneyFromShopifyCents(cents) {
  const c = Number(cents)
  if (!Number.isFinite(c)) return null
  return c / 100
}

/** Unit compare-at for a bucket line when it is above current price. */
function escapeCssAttr(value) {
  const s = String(value)
  if (typeof CSS !== 'undefined' && typeof CSS.escape === 'function') {
    return CSS.escape(s)
  }
  return s.replace(/\\/g, '\\\\').replace(/"/g, '\\"')
}

function compareUnitForLine(item) {
  if (
    item.compareAtCents != null &&
    item.priceCents != null &&
    Number.isFinite(item.compareAtCents) &&
    Number.isFinite(item.priceCents) &&
    item.compareAtCents > item.priceCents
  ) {
    return item.compareAtCents / 100
  }
  const cup = item.compareAtPrice
  if (cup == null || !Number.isFinite(cup)) return null
  if (cup <= item.price) return null
  return cup
}

const BUNDLE_STORAGE_VERSION = 1

class BundleRoot extends HTMLElement {
  constructor() {
    super()
    this.state = { items: {} }
    this._saveFeedbackTimer = null
  }

  connectedCallback() {
    // config
    const configEl = document.getElementById('bundle-config')
    this.config = JSON.parse(configEl.textContent)

    this.bucket = this.querySelector('bundle-bucket')
    this.bucket.root = this

    this.addEventListener('bundle:update', this.handleUpdate.bind(this))
    this.initSaveForLater()

    this.initAccordion()
    this.querySelectorAll('.bundle-block').forEach((block) => {
      const heading = block.querySelector('.bundle-heading')
      if (heading) {
        heading.setAttribute('aria-expanded', String(block.classList.contains('active')))
      }
    })
    this.updateBlockSelectedCounts()
    this.updateFooterActionButtonsState()

    setTimeout(() => this.restorePersistedState(), 0)
  }

  /**
   * Checkout requires at least one bucket line. “Save for later” stays enabled so an empty
   * bundle can be saved and stale localStorage is cleared on refresh.
   */
  updateFooterActionButtonsState() {
    const footer = this.bucket?.querySelector?.('.bucket-footer')
    if (!footer) return

    const hasItems = Object.values(this.state.items).some(
      (item) => item && item.quantity > 0,
    )

    const checkout = footer.querySelector(
      '.bucket-footer-button:not(.bucket-footer-button-secondary)',
    )

    if (checkout) checkout.disabled = !hasItems
  }

  getStorageKey() {
    const sid = this.getAttribute('section-id') || 'default'
    return `bundle-builder:${sid}`
  }

  initSaveForLater() {
    this.addEventListener('click', (e) => {
      if (!e.target.closest('[data-bundle-save-for-later]')) return
      e.preventDefault()
      this.persistStateToLocalStorage()
    })
  }

  persistStateToLocalStorage() {
    const items = Object.values(this.state.items).filter((i) => i.quantity > 0)
    const payload = { v: BUNDLE_STORAGE_VERSION, items }
    try {
      localStorage.setItem(this.getStorageKey(), JSON.stringify(payload))
      this.showBundleSaveFeedback(true, items.length === 0)
    } catch {
      this.showBundleSaveFeedback(false)
    }
  }

  /**
   * Shows save confirmation (or error) under the footer buttons for 5 seconds.
   * @param {boolean} success
   * @param {boolean} [savedEmpty] — true when bucket had no items (clears saved bundle on next visit)
   */
  showBundleSaveFeedback(success, savedEmpty = false) {
    const el = this.bucket?.querySelector?.('[data-bundle-save-feedback]')
    if (!el) return

    if (this._saveFeedbackTimer != null) {
      clearTimeout(this._saveFeedbackTimer)
      this._saveFeedbackTimer = null
    }

    el.textContent = success
      ? savedEmpty
        ? 'Your saved bundle has been cleared. We will not restore items on your next visit.'
        : 'Your selected system has been saved.'
      : 'Could not save your system. Please try again.'
    el.classList.toggle('is-error', !success)
    el.removeAttribute('hidden')

    this._saveFeedbackTimer = setTimeout(() => {
      el.setAttribute('hidden', '')
      el.textContent = ''
      el.classList.remove('is-error')
      this._saveFeedbackTimer = null
    }, 5000)
  }

  restorePersistedState() {
    let raw
    try {
      raw = localStorage.getItem(this.getStorageKey())
    } catch {
      return
    }
    if (!raw) return

    let data
    try {
      data = JSON.parse(raw)
    } catch {
      return
    }
    if (!data || data.v !== BUNDLE_STORAGE_VERSION || !Array.isArray(data.items)) return

    const first = data.items.find((i) => Number(i.quantity) > 0)
    if (first && first.blockId != null) {
      this.setActiveBlock(String(first.blockId))
    }

    for (const line of data.items) {
      const qty = Number(line.quantity) || 0
      if (qty <= 0) continue

      const pid = String(line.productId)
      const bid = String(line.blockId)
      const el = this.querySelector(
        `bundle-item[data-product-id="${escapeCssAttr(pid)}"][data-block-id="${escapeCssAttr(bid)}"]`,
      )
      if (!el || typeof el.restoreFromSnapshot !== 'function') continue
      el.restoreFromSnapshot(line)
    }
  }

  initAccordion() {
    this.activeBlock = this.querySelector('.bundle-block.active')?.dataset.blockId
  
    this.addEventListener('click', (e) => {
      this.activeBlock = this.querySelector('.bundle-block.active')?.dataset.blockId
      const heading = e.target.closest('.bundle-heading')
      if (!heading) return

      const block = heading.closest('.bundle-block')
      const blockId = block.dataset.blockId

      this.setActiveBlock(this.activeBlock === blockId ? null : blockId)
    })

    this.addEventListener('keydown', (e) => {
      if (e.key !== 'Enter' && e.key !== ' ') return
      const heading = e.target.closest('.bundle-heading')
      if (!heading || !this.contains(heading)) return
      e.preventDefault()
      this.activeBlock = this.querySelector('.bundle-block.active')?.dataset.blockId
      const block = heading.closest('.bundle-block')
      const blockId = block.dataset.blockId
      this.setActiveBlock(this.activeBlock === blockId ? null : blockId)
    })
  }
  setActiveBlock(blockId) {
    this.querySelectorAll('.bundle-block').forEach(block => {
      const isActive = block.dataset.blockId === blockId
      block.classList.toggle('active', isActive)
      const heading = block.querySelector('.bundle-heading')
      if (heading) {
        heading.setAttribute('aria-expanded', String(isActive))
      }
    })
  }
  handleUpdate(e) {
    const {
      productId,
      title,
      price,
      quantity,
      blockId,
      image,
      compareAtDisplay,
      compareAtPrice,
      compareAtCents,
      priceCents,
      priceDisplay,
      variantId,
    } = e.detail

    if (quantity <= 0) {
      delete this.state.items[productId]
    } else {
      const cmp =
        compareAtDisplay != null &&
        String(compareAtDisplay).trim() !== '' &&
        String(compareAtDisplay).toLowerCase() !== 'null'
          ? String(compareAtDisplay).trim()
          : null

      let cmpNum = parsePriceNumber(compareAtPrice)
      if (cmpNum == null && compareAtCents != null) {
        cmpNum = moneyFromShopifyCents(compareAtCents)
      }

      const pc =
        priceCents != null && Number.isFinite(Number(priceCents))
          ? Number(priceCents)
          : null
      let unitPrice =
        pc != null ? moneyFromShopifyCents(pc) : null
      if (!Number.isFinite(unitPrice)) {
        if (typeof price === 'number') unitPrice = price
        else if (typeof price === 'string') {
          unitPrice = parseFloat(String(price).replace(/,/g, '').trim())
        }
      }
      if (!Number.isFinite(unitPrice)) unitPrice = 0

      let variantIdNum = null
      if (variantId != null && String(variantId).trim() !== '') {
        const vn = Number(variantId)
        if (Number.isFinite(vn)) variantIdNum = vn
      }

      this.state.items[productId] = {
        productId,
        title,
        price: unitPrice,
        quantity,
        blockId,
        image,
        compareAtDisplay: cmp,
        compareAtPrice: cmpNum,
        compareAtCents:
          compareAtCents != null && Number.isFinite(Number(compareAtCents))
            ? Number(compareAtCents)
            : null,
        priceCents:
          priceCents != null && Number.isFinite(Number(priceCents))
            ? Number(priceCents)
            : null,
        priceDisplay:
          priceDisplay != null && String(priceDisplay).trim() !== ''
            ? String(priceDisplay).trim()
            : null,
        variantId: variantIdNum,
      }
    }

    this.syncUI(blockId,productId)
  }

  syncUI(blockId,productId) {
    const item = this.state.items[productId]

    // update left
    const el = this.querySelector(`[data-product-id="${productId}"][data-block-id="${blockId}"]`)
    if (el) {
      let quantity = item ? item.quantity : 0;
      el.updateQuantity(quantity);
      if(quantity > 0){
        el.classList.add('added')
      }else{
        el.classList.remove('added')
      }
    }

    // update bucket
    this.bucket.update(this.state.items)
    this.updateBlockSelectedCounts()
    this.updateFooterActionButtonsState()
  }

  /**
   * Total units per step (sum of quantities for items in that block).
   */
  updateBlockSelectedCounts() {
    const totals = {}
    Object.values(this.state.items).forEach((item) => {
      if (!item.blockId || item.quantity <= 0) return
      const id = String(item.blockId)
      totals[id] = (totals[id] || 0) + item.quantity
    })
    this.querySelectorAll('.bundle-heading__count').forEach((el) => {
      const blockId = el.dataset.blockId
      const n = totals[blockId] || 0
      const label = n === 1 ? '1 selected' : `${n} selected`
      el.textContent = label
      el.classList.toggle('is-empty', n === 0)
    })
  }
}

customElements.define('bundle-root', BundleRoot)

class BundleItem extends HTMLElement {
  connectedCallback() {
    this.productId = this.dataset.productId
    this.blockId = this.dataset.blockId

    this.qtyEl =
      this.querySelector('.qty-value-number') ||
      this.querySelector('.qty-value')
    this.plus = this.querySelector('.plus')
    this.minus = this.querySelector('.minus')
    this.priceCompareEl = this.querySelector('.bndlr-price-compare')
    this.priceCurrentEl = this.querySelector('.bndlr-price-current')
    this.badgeSave = this.querySelector('.bndlr-badge--save')
    this.badgeFree = this.querySelector('.bndlr-badge--free')
    this.mainImg = this.querySelector('.bndlr-card-image')
    this.optionsRoot = this.querySelector('.bndlr-options')

    const variantsScript = this.querySelector('script[data-bundle-item-variants]')
    try {
      this.variants = variantsScript ? JSON.parse(variantsScript.textContent) : []
    } catch {
      this.variants = []
    }

    this.optionPositions = [...this.querySelectorAll('.bndlr-option-group')]
      .map((g) => parseInt(g.dataset.optionPosition, 10))
      .filter((n) => !Number.isNaN(n))
      .sort((a, b) => a - b)

    this.selection = {}
    this.querySelectorAll('.bndlr-option-btn.is-selected').forEach((btn) => {
      const pos = parseInt(btn.dataset.optionPosition, 10)
      this.selection[pos] = btn.getAttribute('data-option-value')
    })

    this.quantity = 0

    if (this.variants.length && this.optionPositions.length) {
      const initial =
        this.findVariantForSelection(this.selection, false) || this.variants[0]
      if (initial) {
        this.optionPositions.forEach((p) => {
          this.selection[p] = initial[`option${p}`]
        })
        this.syncOptionButtonsFromSelection()
        this.applyVariant(initial)
      }
    } else {
      this.title = this.dataset.title
      this.price = this.dataset.price
      this.image = this.dataset.image
      const dvid = this.dataset.defaultVariantId
      this.currentVariantId =
        dvid != null && String(dvid).trim() !== ''
          ? Number(dvid)
          : null

      const ca = this.dataset.bucketCompareAt?.trim()
      this._bucketCompareAt =
        ca && ca.toLowerCase() !== 'null' ? ca : null
      this._bucketPriceDisplay =
        this.dataset.bucketPriceDisplay?.trim() || ''

      const pCents = Number(this.dataset.priceCents)
      const cCentsRaw = this.dataset.bucketCompareAtCents
      const cCents =
        cCentsRaw != null && String(cCentsRaw).trim() !== ''
          ? Number(cCentsRaw)
          : NaN

      this._bucketPriceCents = Number.isFinite(pCents) ? pCents : null
      this._bucketCompareAtCents =
        Number.isFinite(cCents) &&
        Number.isFinite(pCents) &&
        cCents > pCents
          ? cCents
          : null

      if (this._bucketCompareAtCents != null && this._bucketPriceCents != null) {
        this._bucketCompareAtPrice = this._bucketCompareAtCents / 100
      } else {
        const cup = parsePriceNumber(this.dataset.bucketCompareAtPrice)
        const p = parsePriceNumber(this.dataset.price)
        this._bucketCompareAtPrice =
          cup != null && p != null && cup > p ? cup : null
      }
    }

    this.optionsRoot?.addEventListener('click', (e) => {
      const btn = e.target.closest('.bndlr-option-btn')
      if (!btn || !this.optionsRoot.contains(btn)) return
      const pos = parseInt(btn.dataset.optionPosition, 10)
      const value = btn.getAttribute('data-option-value')
      if (value === null || this.selection[pos] === value) return
      this.selectOption(pos, value)
    })

    this.plus.addEventListener('click', () => this.changeQty(1))
    this.minus.addEventListener('click', () => this.changeQty(-1))
  }

  findVariantForSelection(sel, availableOnly) {
    return this.variants.find((v) => {
      if (availableOnly && !v.available) return false
      for (const p of this.optionPositions) {
        if (v[`option${p}`] !== sel[p]) return false
      }
      return true
    })
  }

  findFirstAvailableWithOptionValue(position, value) {
    return this.variants.find((v) => v.available && v[`option${position}`] === value)
  }

  findFirstWithOptionValue(position, value) {
    return this.variants.find((v) => v[`option${position}`] === value)
  }

  selectOption(position, value) {
    const temp = { ...this.selection, [position]: value }
    const variant =
      this.findVariantForSelection(temp, true) ||
      this.findFirstAvailableWithOptionValue(position, value) ||
      this.findVariantForSelection(temp, false) ||
      this.findFirstWithOptionValue(position, value)

    if (!variant) return

    this.optionPositions.forEach((p) => {
      this.selection[p] = variant[`option${p}`]
    })
    this.syncOptionButtonsFromSelection()
    this.applyVariant(variant)
    this.dispatchBundleUpdateIfInBucket()
  }

  syncOptionButtonsFromSelection() {
    this.querySelectorAll('.bndlr-option-group').forEach((group) => {
      const pos = parseInt(group.dataset.optionPosition, 10)
      const selectedValue = this.selection[pos]
      group.querySelectorAll('.bndlr-option-btn').forEach((btn) => {
        const val = btn.getAttribute('data-option-value')
        btn.classList.toggle('is-selected', val === selectedValue)
      })
    })
  }

  applyVariant(variant) {
    if (!variant) return
    this.currentVariantId =
      variant.id != null && String(variant.id).trim() !== ''
        ? Number(variant.id)
        : null
    this.price = String(variant.price)
    this.image = variant.image
    this.title = `${this.dataset.title} — ${variant.title}`

    this.updatePricingAndBadges(variant)

    if (this.mainImg && variant.cardImage) {
      this.mainImg.src = variant.cardImage
    }
  }

  /**
   * Compare-at (struck) + current price (red on sale), save % pill, FREE pill.
   */
  updatePricingAndBadges(v) {
    // Trust Liquid `isFree` only — parseFloat("0,99") is 0 in JS and wrongly showed FREE for comma decimals.
    const isFree = v.isFree === true

    const compareRaw = v.compareAtDisplay
    const compare =
      compareRaw != null &&
      compareRaw !== '' &&
      String(compareRaw).toLowerCase() !== 'null'
        ? compareRaw
        : null

    const showCompare = Boolean(!isFree && compare)

    if (this.priceCompareEl) {
      if (showCompare) {
        this.priceCompareEl.textContent = compare
        this.priceCompareEl.removeAttribute('hidden')
      } else {
        this.priceCompareEl.textContent = ''
        this.priceCompareEl.setAttribute('hidden', '')
      }
    }

    if (this.priceCurrentEl) {
      if (isFree) {
        this.priceCurrentEl.textContent = 'FREE'
        this.priceCurrentEl.classList.add('bndlr-price-current--free')
        this.priceCurrentEl.classList.remove('bndlr-price-current--sale')
      } else {
        this.priceCurrentEl.textContent = v.priceDisplay || ''
        this.priceCurrentEl.classList.remove('bndlr-price-current--free')
        if (compare) {
          this.priceCurrentEl.classList.add('bndlr-price-current--sale')
        } else {
          this.priceCurrentEl.classList.remove('bndlr-price-current--sale')
        }
      }
    }

    if (this.badgeFree) {
      if (isFree) {
        this.badgeFree.removeAttribute('hidden')
      } else {
        this.badgeFree.setAttribute('hidden', '')
      }
    }

    if (this.badgeSave) {
      const saveNum = Number(v.savePercent)
      const showSave =
        !isFree &&
        compare &&
        v.savePercent != null &&
        Number.isFinite(saveNum) &&
        saveNum > 0
      if (showSave) {
        this.badgeSave.textContent = `Save ${v.savePercent}%`
        this.badgeSave.removeAttribute('hidden')
      } else {
        this.badgeSave.setAttribute('hidden', '')
      }
    }

    this._bucketCompareAt = !isFree && compare ? compare : null
    this._bucketPriceDisplay = isFree ? 'FREE' : (v.priceDisplay || '')

    const pCents = Number(v.priceCents)
    const cCents = v.compareAtCents != null ? Number(v.compareAtCents) : NaN
    const centsOk =
      !isFree &&
      compare &&
      Number.isFinite(pCents) &&
      Number.isFinite(cCents) &&
      cCents > pCents

    this._bucketPriceCents = Number.isFinite(pCents) ? pCents : null
    this._bucketCompareAtCents = centsOk ? cCents : null

    let bucketCompare = centsOk ? cCents / 100 : null
    if (bucketCompare == null && !isFree && compare) {
      const cmpNum = parsePriceNumber(v.compareAtPrice)
      const unitP = parsePriceNumber(v.price)
      if (cmpNum != null && unitP != null && cmpNum > unitP) {
        bucketCompare = cmpNum
      }
    }
    this._bucketCompareAtPrice = bucketCompare

    // Host `data-*` must follow the selected variant (Liquid only outputs the initial variant).
    this.dataset.price = String(v.price)
    if (Number.isFinite(pCents)) {
      this.dataset.priceCents = String(Math.round(pCents))
    } else {
      this.dataset.priceCents = ''
    }

    if (isFree) {
      this.dataset.bucketPriceDisplay = 'FREE'
      this.dataset.bucketCompareAt = ''
      this.dataset.bucketCompareAtPrice = ''
      this.dataset.bucketCompareAtCents = ''
    } else {
      this.dataset.bucketPriceDisplay = v.priceDisplay || ''
      this.dataset.bucketCompareAt = compare ? compare : ''
      const capStr =
        v.compareAtPrice != null && String(v.compareAtPrice).trim() !== ''
          ? String(v.compareAtPrice).trim()
          : bucketCompare != null && Number.isFinite(bucketCompare)
            ? bucketCompare.toFixed(2)
            : ''
      this.dataset.bucketCompareAtPrice = capStr
      this.dataset.bucketCompareAtCents = centsOk
        ? String(Math.round(cCents))
        : ''
    }

    if (this.image) {
      this.dataset.image = this.image
    }
  }

  getBundleUpdateDetail(quantity) {
    return {
      productId: this.productId,
      title: this.title,
      price: this.price,
      quantity,
      blockId: this.blockId,
      image: this.image,
      compareAtDisplay: this._bucketCompareAt ?? null,
      compareAtPrice: this._bucketCompareAtPrice ?? null,
      compareAtCents: this._bucketCompareAtCents ?? null,
      priceCents: this._bucketPriceCents ?? null,
      priceDisplay: this._bucketPriceDisplay || null,
      variantId: this.currentVariantId ?? null,
    }
  }

  dispatchBundleUpdateIfInBucket() {
    if (this.quantity <= 0) return
    this.dispatchEvent(
      new CustomEvent('bundle:update', {
        bubbles: true,
        detail: this.getBundleUpdateDetail(this.quantity),
      }),
    )
  }

  changeQty(delta) {
    let qty = this.quantity + delta
    if (qty < 0) qty = 0

    this.dispatchEvent(
      new CustomEvent('bundle:update', {
        bubbles: true,
        detail: this.getBundleUpdateDetail(qty),
      }),
    )
  }

  /**
   * Rehydrate qty, variant/options UI, and pricing from a persisted line (localStorage).
   */
  restoreFromSnapshot(line) {
    const qty = Number(line.quantity) || 0
    const vid =
      line.variantId != null && String(line.variantId).trim() !== ''
        ? Number(line.variantId)
        : null

    const applySnapshotPricing = () => {
      if (vid != null && Number.isFinite(vid)) {
        this.currentVariantId = vid
      }
      if (line.title != null && String(line.title).trim() !== '') {
        this.title = String(line.title)
      }
      if (line.image != null && String(line.image).trim() !== '') {
        this.image = String(line.image)
      }
      if (line.price != null) {
        this.price = String(line.price)
        this.dataset.price = this.price
      }
      if (line.priceCents != null && Number.isFinite(Number(line.priceCents))) {
        this._bucketPriceCents = Number(line.priceCents)
        this.dataset.priceCents = String(line.priceCents)
      }
      if (line.compareAtCents != null && Number.isFinite(Number(line.compareAtCents))) {
        this._bucketCompareAtCents = Number(line.compareAtCents)
        this.dataset.bucketCompareAtCents = String(line.compareAtCents)
      } else {
        this._bucketCompareAtCents = null
        this.dataset.bucketCompareAtCents = ''
      }
      if (line.compareAtDisplay != null && String(line.compareAtDisplay).trim() !== '') {
        this._bucketCompareAt = String(line.compareAtDisplay).trim()
        this.dataset.bucketCompareAt = this._bucketCompareAt
      } else {
        this._bucketCompareAt = null
        this.dataset.bucketCompareAt = ''
      }
      if (line.compareAtPrice != null && Number.isFinite(Number(line.compareAtPrice))) {
        this._bucketCompareAtPrice = Number(line.compareAtPrice)
        this.dataset.bucketCompareAtPrice = String(line.compareAtPrice)
      } else if (
        this._bucketCompareAtCents != null &&
        this._bucketPriceCents != null &&
        this._bucketCompareAtCents > this._bucketPriceCents
      ) {
        this._bucketCompareAtPrice = this._bucketCompareAtCents / 100
        this.dataset.bucketCompareAtPrice = this._bucketCompareAtPrice.toFixed(2)
      }
      if (line.priceDisplay != null && String(line.priceDisplay).trim() !== '') {
        this._bucketPriceDisplay = String(line.priceDisplay).trim()
        this.dataset.bucketPriceDisplay = this._bucketPriceDisplay
      }
      if (this.mainImg && this.image) {
        this.mainImg.src = this.image
      }
    }

    if (this.variants.length && this.optionPositions.length && vid != null) {
      const v = this.variants.find((x) => String(x.id) === String(vid))
      if (v) {
        this.optionPositions.forEach((p) => {
          this.selection[p] = v[`option${p}`]
        })
        this.syncOptionButtonsFromSelection()
        this.applyVariant(v)
      } else {
        applySnapshotPricing()
      }
    } else {
      applySnapshotPricing()
    }

    this.updateQuantity(qty)
    this.dispatchEvent(
      new CustomEvent('bundle:update', {
        bubbles: true,
        detail: this.getBundleUpdateDetail(qty),
      }),
    )
  }

  updateQuantity(qty) {
    this.quantity = qty
    this.qtyEl.textContent = qty
  }
}

customElements.define('bundle-item', BundleItem)


class BundleBucket extends HTMLElement {
  update(items) {
    this.items = items
    this.render()
  }

  render() {
    const grouped = {}
    let totalPayable = 0
    let totalCompare = 0

    Object.values(this.items).forEach((item) => {
      if (!grouped[item.blockId]) grouped[item.blockId] = []
      grouped[item.blockId].push(item)
    })

    let html = ''

    for (const blockId in grouped) {
      const title = this.root.config[blockId]?.title || 'Group'

      html += `<div class="bucket-block"> <h3>${title}</h3>`
      grouped[blockId].forEach((item) => {
        const qty = item.quantity
        totalPayable += item.price * qty
        const u = compareUnitForLine(item)
        totalCompare += (u ?? item.price) * qty
        const cmpRaw = item.compareAtDisplay
        const showCompare =
          item.price !== 0 &&
          cmpRaw != null &&
          String(cmpRaw).trim() !== '' &&
          String(cmpRaw).toLowerCase() !== 'null'
        const currentLabel =
          item.price === 0
            ? 'FREE'
            : item.priceDisplay && String(item.priceDisplay).trim() !== ''
              ? String(item.priceDisplay).trim()
              : item.price.toFixed(2)
        const currentClass =
          item.price === 0
            ? 'bucket-item__current bucket-item__current--free'
            : showCompare
              ? 'bucket-item__current bucket-item__current--sale'
              : 'bucket-item__current'
        html += `
          <div class="bucket-item">
            <img src="${item.image}" alt="${escapeHtml(item.title)}">
            <p>${escapeHtml(item.title)}</p>
            <div class="qty-container">
              <button data-id="${item.productId}" class="minus">-</button>
              <span>${item.quantity}</span>
              <button data-id="${item.productId}" class="plus">+</button>
            </div>
            <div class="bucket-item__pricing">
              ${
                showCompare
                  ? `<span class="bucket-item__compare">${escapeHtml(cmpRaw)}</span>`
                  : ''
              }
              <span class="${currentClass}">${escapeHtml(currentLabel)}</span>
            </div>
          </div>
        `
      })
      html += `</div>`
    }

    const showCompareTotal = totalCompare - totalPayable > 0.005
    const totalHtml = showCompareTotal
      ? `<hr><div class="bucket-total" aria-live="polite">
          <p class="bucket-total__label">Total</p>
          <div class="bucket-total__row">
            <p class="bucket-total__compare">$${totalCompare.toFixed(2)}</p>
            <p class="bucket-total__payable bucket-total__payable--sale">$${totalPayable.toFixed(2)}</p>
          </div>
        </div>`
      : `<hr><div class="bucket-total" aria-live="polite">
          <p class="bucket-total__label">Total</p>
          <p class="bucket-total__payable">$${totalPayable.toFixed(2)}</p>
        </div>`

    html += totalHtml

    this.querySelector('.bucket-items').innerHTML = html

    const savingsBanner = this.querySelector('[data-bucket-savings-banner]')
    if (savingsBanner) {
      if (showCompareTotal) {
        const saved = totalCompare - totalPayable
        savingsBanner.textContent = `Congrats! you are saving $${saved.toFixed(2)} on your security bundle`
        savingsBanner.removeAttribute('hidden')
      } else {
        savingsBanner.textContent = ''
        savingsBanner.setAttribute('hidden', '')
      }
    }

  }

  connectedCallback() {
    this.items = {}
  
    this.addEventListener('click', (e) => {
      const btn = e.target.closest('button')
      if (!btn) return
  
      const productId = btn.dataset.id
      if (!productId) return
  
      if (btn.classList.contains('plus')) {
        this.changeQty(productId, 1)
      }
  
      if (btn.classList.contains('minus')) {
        this.changeQty(productId, -1)
      }
    })
  }

  changeQty(productId, delta) {
    const item = this.items[productId]
    if (!item) return

    let qty = item.quantity + delta
    if (qty < 0) qty = 0

    this.dispatchEvent(
      new CustomEvent('bundle:update', {
        bubbles: true,
        detail: {
          productId: item.productId,
          title: item.title,
          price: item.price,
          quantity: qty,
          blockId: item.blockId,
          image: item.image,
          compareAtDisplay: item.compareAtDisplay ?? null,
          compareAtPrice: item.compareAtPrice ?? null,
          compareAtCents: item.compareAtCents ?? null,
          priceCents: item.priceCents ?? null,
          priceDisplay: item.priceDisplay ?? null,
          variantId: item.variantId ?? null,
        },
      }),
    )
  }
}

customElements.define('bundle-bucket', BundleBucket)