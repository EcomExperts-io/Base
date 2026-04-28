class BundleRoot extends HTMLElement {
  constructor() {
    super()
    this.state = { items: {} }
  }

  connectedCallback() {
    // config
    const configEl = document.getElementById('bundle-config')
    this.config = JSON.parse(configEl.textContent)

    this.bucket = this.querySelector('bundle-bucket')
    this.bucket.root = this

    this.addEventListener('bundle:update', this.handleUpdate.bind(this))

    this.initAccordion()
    this.querySelectorAll('.bundle-block').forEach((block) => {
      const heading = block.querySelector('.bundle-heading')
      if (heading) {
        heading.setAttribute('aria-expanded', String(block.classList.contains('active')))
      }
    })
    this.updateBlockSelectedCounts()
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
    const { productId, title, price, quantity, blockId , image } = e.detail

    if (quantity <= 0) {
      delete this.state.items[productId]
    } else {
      this.state.items[productId] = {
        productId,
        title,
        price: parseFloat(price),
        quantity,
        blockId,
        image
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
    this.title = this.dataset.title
    this.price = this.dataset.price
    this.blockId = this.dataset.blockId
    this.image = this.dataset.image

    this.qtyEl = this.querySelector('.qty-value')
    this.plus = this.querySelector('.plus')
    this.minus = this.querySelector('.minus')

    this.quantity = 0

    this.plus.addEventListener('click', () => this.changeQty(1))
    this.minus.addEventListener('click', () => this.changeQty(-1))
  }

  changeQty(delta) {
    let qty = this.quantity + delta
    if (qty < 0) qty = 0
      
    this.dispatchEvent(new CustomEvent('bundle:update', {
      bubbles: true,
      detail: {
        productId: this.productId,
        title: this.title,
        price: this.price,
        quantity: qty,
        blockId: this.blockId,
        image: this.image
      }
    }))
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
    let total = 0
    console.log("Mm",{items:this.items})
    Object.values(this.items).forEach(item => {
      if (!grouped[item.blockId]) grouped[item.blockId] = []
      grouped[item.blockId].push(item)
    })

    let html = ''

    for (const blockId in grouped) {
      const title = this.root.config[blockId]?.title || 'Group'

      html += `<div class="bucket-block"> <h3>${title}</h3>`

      grouped[blockId].forEach(item => {
        total += item.price * item.quantity
        html += `
          <div class="bucket-item">
            <img src="${item.image}" alt="${item.title}">
            <p>${item.title}</p>
            <div class="qty-container">
              <button data-id="${item.productId}" class="minus">-</button>
              <span>${item.quantity}</span>
              <button data-id="${item.productId}" class="plus">+</button>
            </div>
            <p>${item.price}</p>
          </div>
        `
      })
      html += `</div>`
    }

    html += `<hr><strong>Total: $${total.toFixed(2)}</strong>`

    this.querySelector('.bucket-items').innerHTML = html

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

    this.dispatchEvent(new CustomEvent('bundle:update', {
      bubbles: true,
      detail: {
        productId: item.productId,
        title: item.title,
        price: item.price,
        quantity: qty,
        blockId: item.blockId,
        image: item.image
      }
    }))
  }
}

customElements.define('bundle-bucket', BundleBucket)