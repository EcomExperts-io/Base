# Base Theme × AI Workflow — Vision & Principles
 
**Purpose of this doc:** the durable "why" behind this whole initiative.
This should rarely change. Project-specific status, technical rules, and
open questions live in the companion documents linked at the bottom —
keep those out of here.
 
**Facilitating:** Naish Abbas
**Final sign-off on architecture decisions:** Moemen Hegazy (Head of Engineering)
**Also looped in:** Mohannad Belidy
 
---
 
## 1. The Bigger Goal
 
Streamline the pipeline so that any Figma file can become Base Theme–standard
code with minimal human touch-up:
 
> Designer creates Figma → Figma follows AI-friendly design practices →
> AI accesses Figma through Figma MCP → AI accesses Shopify through Shopify MCP →
> AI accesses our Base Theme principles/reference architecture →
> AI builds the page → AI validates the implementation against the Figma design →
> Developer reviews, handles edge cases, and makes final refinements.
 
The end goal is that we can take a Figma file and say:
 
> **"Build this using our Base Theme standards."**
 
And the AI should already understand both **what the design is** and
**how we expect that design to be implemented** — without a developer
having to re-explain the architecture every time.
 
---
 
## 2. Two Connected Problems
 
1. **Design → AI** — how do we get designers to structure Figma files
   (naming, auto layout, components, tokens) so Figma MCP extracts an
   accurate, unambiguous design?
2. **AI → Production code** — how do we give AI (Claude Code, Cursor,
   Codex, or any future tool) the Base Theme's architecture principles
   so it builds *in the Base Theme style*, not just something that looks
   visually correct?
---
 
## 3. Explicitly Not the Goal
 
- Rewriting Moemen's architecture to taste.
- Turning every build task into a Base Theme redesign.
- Locking this knowledge into Cursor Rules specifically — the workflow
  needs to work across Claude Code, Cursor, Codex, and whatever comes
  next.
If we spot a genuine architecture improvement while doing this work:
document it, bank it, don't implement it as a side effect of an
unrelated build task.
 
---
 
## 4. Where Base Theme Comes From
 
Base Theme is Moemen's simplified take on Shopify's Dawn theme. He spent
significant time debugging and understanding why Dawn was structured the
way it was, then simplified/refactored parts of it into the architecture
we use today. That reasoning — not just the current file layout — is
what we're trying to capture and generalize. Base Theme's current
implementation is **not necessarily final or perfect**; the priority is
teaching AI to build consistently within these principles, not treating
the current code as gospel.
 
---
 
## 5. Working Method
 
- **Figma MCP + Shopify MCP + a strong coding model** (Sonnet/Opus —
  not the cheapest available model).
- **One-shot, single-prompt builds** work well for simpler, cleanly
  structured pages (works well when the Figma file uses good naming,
  auto layout, consistent components).
- **Complex pages** (Collection, PDP, Homepage) need more: visual
  accuracy from Figma isn't enough — the code also needs to follow Base
  Theme's architecture. These pages get a dedicated recon + audit step
  against the actual Base Theme reference architecture.
- **Order of attack:** Collection → PDP → other complex pages/sections
  (Header/Mega Menu, Cart engine) later. Don't jump ahead.
---
 
## 6. Related Documents
 
- **Base Theme Architecture Reference — Collection & PDP** — the
  technical rulebook extracted from Base Theme itself (durable, reusable
  across any future client build).
- **Base Theme Decisions Log** — cross-project architecture questions
  and Moemen's rulings, resolved and open.
- **Bites Vitamins — Project Status** — page-by-page tracker for the
  current client project.
- **Bites Vitamins — Collection Page Audit** — compliance check of the
  already-built Collection page against the architecture reference.