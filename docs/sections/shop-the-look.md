# Shop The Look Section (`sections/shop-the-look.liquid`)

`sections/shop-the-look.liquid` renders an interactive slider showcasing styled looks with clickable hotspots on images and corresponding product cards. Each slide contains a lifestyle image with customizable hotspots and up to 4 product recommendations. The section uses Swiper for smooth carousel functionality and supports both desktop navigation buttons and mobile pagination.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `swiper7.4.1.min.css`, `section-shop-the-look.css` |
| JS   | `swiper7.4.1.min.js` (deferred), `section-shop-the-look.js` (module) |
| Custom Element | `<shop-the-look>` defined in `section-shop-the-look.js` |
| Snippets | `component-product-card.liquid` |
| Blocks | `slide` (contains image, products, and hotspot settings) |
| Data | Relies on `section.blocks` for slides and hotspots, `section.settings` for display options |

- Swiper library handles slider functionality with navigation and pagination.
- Custom element manages slider initialization and navigation state.
- Product cards rendered using the existing `component-product-card.liquid` snippet.
- Hotspots are positioned using percentage-based coordinates for responsive behavior.

---

## Block Structure

### Slide Block
Each slide contains all settings in one block:
- **Image**: Main lifestyle/lookbook image
- **Products**: Up to 4 product selections
- **Hotspots**: Up to 4 hotspots with individual enable toggles
  - Each hotspot has:
    - Enable checkbox
    - Horizontal Position (0-100%)
    - Vertical Position (0-100%)

---

## Dynamic Styles

The section uses inline styles for dynamic values:

```liquid
<shop-the-look
  data-section-id="{{ section.id }}"
  class="color-{{ section.settings.color_scheme }}"
  style="padding-top: {{ padding_top }}px; padding-bottom: {{ padding_bottom }}px;"
>
```

- `padding-top` / `padding-bottom`: Section spacing (0–100px, default 36px).
- `color_scheme`: Applies theme color scheme classes.

---

## Features

### 1. Swiper Slider
- Single slide view with smooth transitions
- Navigation arrows (prev/next buttons) positioned on the right
- Progress bar showing current slide position
- Progress bar fills based on slide count (e.g., 1/3 = 33%, 2/3 = 66%)
- Auto-height disabled for consistent layout
- Loop disabled (linear progression)

### 2. Interactive Hotspots
- Click to reveal tooltip with custom text content
- Positioned absolutely on images using percentage coordinates
- Only one tooltip open at a time (auto-closes others)
- Click outside hotspot to dismiss
- Smooth fade and slide animations
- Desktop: Hover effect with scale transform
- Mobile: Touch-friendly tap interaction
- Accessible with keyboard focus states and ARIA labels
- Tooltips appear below hotspot with arrow pointer
- Auto-sized based on content (max-width: 280px desktop, 240px mobile)

### 3. Product Grid
- Responsive grid layout:
  - Mobile: 1 column
  - Tablet+: 2 columns
- Uses existing product card component
- Supports vendor display toggle
- Configurable image aspect ratio

### 4. Responsive Layout
- Mobile: Stacked image and products
- Desktop: Side-by-side (50/50 split)
- Image maintains 4:5 aspect ratio (3:4 on mobile)

---

## Settings

### Section Settings
- **Heading**: Main section title
- **View All URL**: Optional link to collection/page
- **Color Scheme**: Theme color scheme selection
- **Show Vendor**: Toggle product vendor display
- **Image Ratio**: Product card image aspect ratio (adapt/portrait/square)
- **Padding**: Top and bottom spacing

### Block Settings (Slide)
- **Image**: Lifestyle/lookbook image
- **Product 1-4**: Product selections for the look
- **Hotspot 1-4**: Each hotspot includes:
  - Enable checkbox to show/hide
  - Tooltip Text: Custom content to display (textarea)
  - Horizontal Position: 0-100% from left
  - Vertical Position: 0-100% from top

---

## JavaScript Functionality

The `section-shop-the-look.js` custom element:

1. **Initialization**
   - Checks for Swiper library availability
   - Prevents duplicate initialization
   - Sets up navigation and pagination

2. **Hotspot Interaction**
   - Click event handling for tooltip toggle
   - Auto-closes other tooltips when one is opened
   - Click outside to close all tooltips
   - Adds/removes `is-active` class for state management
   - Updates `aria-expanded` attribute for accessibility

3. **Progress Bar Management**
   - Calculates progress percentage based on current slide
   - Updates progress bar width on slide change
   - Formula: `(currentIndex + 1) / totalSlides * 100`
   - Smooth transition animation

4. **Navigation State Management**
   - Disables prev button on first slide
   - Disables next button on last slide
   - Updates on slide change
   - Closes all tooltips when changing slides

5. **Cleanup**
   - Properly destroys Swiper instance on disconnect
   - Removes event listeners
   - Prevents memory leaks

---

## Usage Example

### Basic Setup
1. Add section to theme
2. Add a "Slide" block
3. Upload lifestyle image
4. Select 2-4 products
5. Enable desired hotspots (1-4)
6. Position each hotspot using the horizontal and vertical sliders
7. Repeat for additional slides

---

## Styling Notes

### CSS Variables Used
- `--color-background`: Background colors
- `--color-foreground`: Text and border colors
- Theme color scheme variables via `color-{{ color_scheme }}` class

### Key CSS Features
- CSS Grid for responsive layouts
- Flexbox for product card grids
- CSS animations for hotspot pulse effect
- Container queries ready (aspect-ratio, object-fit)
- Mobile-first responsive design

---

## Accessibility

- Semantic HTML structure
- ARIA labels on interactive elements
- Keyboard navigation support
- Focus visible states on hotspots
- Screen reader friendly navigation buttons

---

## Static Text

The section uses static text (no translation keys required):

- **View All link**: "VIEW ALL"
- **Hotspot aria-label**: "View product details"
- **Navigation buttons**: "Previous slide", "Next slide"
- **Tooltip content**: Custom text from block settings

---

## Performance Considerations

- Images use lazy loading (except first slide)
- Responsive image srcsets for optimal delivery
- Swiper watchOverflow prevents unnecessary navigation
- CSS animations use transform for GPU acceleration
- JavaScript only loads when section is present

---

## Browser Support

- Modern browsers (last 2 versions)
- Swiper 7.4.1 compatibility
- CSS Grid and Flexbox support required
- Custom Elements API required

---

## Future Enhancements

Potential improvements:
- Video support in addition to images
- Product quick view on hotspot click
- Auto-play slider option
- Thumbnail navigation
- Zoom on hotspot hover
- Analytics tracking for hotspot interactions

