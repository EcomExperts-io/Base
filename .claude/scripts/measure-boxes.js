// Run in the page through the browser tools' JavaScript action. Two helpers:
//
//   MEASURE({ "hero/heading": ".hero__title", "hero/cta": ".hero__cta" })
//     -> { "hero/heading": { x, y, w, h, font_size, line_height, color, background, font_family }, ... }
//        Coordinates are page pixels (scroll-independent), rounded to 0.5px, so they
//        line up with a full-page render and with frame-relative Figma metadata once
//        the section's own top is subtracted.
//
//   MASKS()
//     -> [ "x,y,w,h", ... ] for every element carrying data-verify-mask — pass each
//        one to compare.py as --mask. These are the regions that hold live store data
//        and can never match a mock.
//
// Paste the whole file, then call the helper you need and return its value.

(() => {
  const round = (n) => Math.round(n * 2) / 2;
  const box = (el) => {
    const r = el.getBoundingClientRect();
    return { x: round(r.left + window.scrollX), y: round(r.top + window.scrollY), w: round(r.width), h: round(r.height) };
  };
  const px = (v) => (v && v.endsWith("px") ? round(parseFloat(v)) : v);
  const hex = (rgb) => {
    const m = rgb && rgb.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
    if (!m) return rgb;
    if (m[4] !== undefined && parseFloat(m[4]) === 0) return "transparent";
    return "#" + [m[1], m[2], m[3]].map((n) => parseInt(n, 10).toString(16).padStart(2, "0")).join("");
  };

  window.MEASURE = (selectors) => {
    const out = {};
    for (const [name, sel] of Object.entries(selectors)) {
      const el = document.querySelector(sel);
      if (!el) { out[name] = null; continue; }
      const cs = getComputedStyle(el);
      out[name] = Object.assign(box(el), {
        font_size: px(cs.fontSize),
        line_height: px(cs.lineHeight),
        font_family: cs.fontFamily.split(",")[0].replace(/["']/g, "").trim(),
        color: hex(cs.color),
        background: hex(cs.backgroundColor),
        radius: px(cs.borderTopLeftRadius),
        gap: px(cs.gap === "normal" ? "" : cs.gap),
        display: cs.display,
      });
    }
    return out;
  };

  window.MASKS = () =>
    Array.from(document.querySelectorAll("[data-verify-mask]")).map((el) => {
      const b = box(el);
      return `${b.x},${b.y},${b.w},${b.h}`;
    });

  return "MEASURE and MASKS are defined";
})();
