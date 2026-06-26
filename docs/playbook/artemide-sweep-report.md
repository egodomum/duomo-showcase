# Artemide 전수조사 리포트 (8제품, 멀티에이전트)

> duomo-figma-tone-sweep 워크플로우 종합 리포트 원문.

I now have full grounding. The existing tool is built around a 13-section conversion funnel at 1200px with a gold Premium preset â which the entire Artemide sweep contradicts. I have everything I need to write the consolidated report with concrete, file-pointing recommendations.

---

# Artemide Tone Matrix â Consolidated Sweep (8 products)

## 1. Consistency verdict

**The DUOMO/Artemide visual tone is highly consistent at the strategic level, but the layout grammar splits into two generations.**

- **100% (8/8)** hold the core DNA: **1000px content width**, **formal Korean ê²½ì´ì²´**, **product-SHOWCASE structure with NO sales funnel** (zero Pain/Problem/Social-Proof/Risk/Comparison/CTA sections), **brand-color accent (never gold)**, **Pretendard-style Korean body**, and **massive whitespace with full-bleed photography alternating with text sections**.
- **~50% (â4/8)** match the *strict* Onfale baseline including **center alignment + pure-white sections + serif product name**: Onfale (old), Eclisse Orange (old), Tolomeo Micro (renewal), Sintesi (partial â keeps center body but breaks white).
- **The deviations are systematic, not random.** Every break clusters in the **renewal/ë¦¬ë´ì¼ generation** and falls into three predictable buckets: (a) left-alignment, (b) sans-serif product names, (c) full-bleed black sections. None is a funnel; none introduces gold; none widens the *content* unit beyond ~1000px.

**Net:** tone is a single coherent system. Treat it as **one baseline + a renewal variant layer**, not eight separate tones.

## 2. Confirmed tokens (reliably true across ALL 8 products)

| Token | Value | Evidence |
|---|---|---|
| **Content width** | **1000px**, single centered column (NOT 1200px, NOT wide-desktop) | All 8. Even Eclisse-renewal's 8739px and Tolomeo-Mega's frames are *artboard padding* â content stays ~1000px |
| **Korean body font** | Pretendard-style geometric sans, regular weight | All 8 |
| **Brand/logo serif** | Noto Serif Display-style high-contrast/Didone for `Artemide`/`Duomo&Co.` wordmarks | All 8 (wordmark serif is universal even where product-name serif is dropped) |
| **Copy register** | Formal ê²½ì´ì²´ (~í©ëë¤/~ìëë¤/~ë©ëë¤), informational-first with light emotional headlines | All 8 |
| **Structure** | Product SHOWCASE â no Pain/Problem/Proof/Risk/Compare/Filter/CTA funnel, no urgency/scarcity/price-strikethrough | All 8, explicitly |
| **Accent rule** | Per-brand color, **NEVER gold** | All 8 (every `differs` note calls this out) |
| **Whitespace** | Generous vertical padding; full-bleed edge-to-edge photography alternating with text blocks | All 8 |
| **Pure black `#000`/`#0A0A0A`** | Available as a section background (designer/brand/mood) | Used in 6/8; the two olds (Onfale, Eclisse Orange) use near-black only for hero photo overlay |

**Body text color** is consistently dark-neutral but the exact hex drifts: `#2C2C2C` (Onfale baseline), `#232725` (Onfale finding), `#1A1A1A`/`#222` (Tolomeo Mega, Shogun). Treat as a **range `#1A1A1Aâ#2C2C2C`**, pick `#1F1F1F` as a safe default.

## 3. Variants found â do the renewal pages go wide/multi-column?

**Critical answer: NO â renewals do NOT use a true wider/desktop layout. The content unit stays ~1000px centered.** The renewal generation differs on *alignment, type, and section color*, not on width.

- **The "wide" frame is a Figma artboard artifact, not a content layout.** Eclisse-renewal sits in an **8739px frame** but renders **two stacked ~1000px columns** (a main showcase column + a separate DUOMO trust/service column) â the extra width is board padding. Tolomeo Mega's 1000Ã8979 and Dedalo's 1000Ã12914 are explicitly "NOT a wide desktop layout." **Do not build a desktop/12-col grid off these.**

**Variant breakdown by product:**

| Product | Era | Breaks from strict baseline |
|---|---|---|
| **Onfale** | old | â (baseline) |
| **Eclisse Orange** | old | Consistent; adds gray "Benefit" free-bulb card + footer policy 2-col (label-left/value-right) |
| **Tolomeo Micro** | renewal | Mostly consistent; **adds top importer-trust block + dark BRAND + dark DESIGNER sections**; bilingual headings (íê¸ serif + EN/IT sans sub, e.g. ìºí¸ë ë² í¸í / Cantilever) |
| **Tolomeo Mega** | renewal | **Left-aligned** (vs center); **product name in HEAVY SANS-SERIF** (not serif); full-bleed black designer section |
| **Sintesi** | renewal | **Pure-white broken** â dark/black editorial dominates; accent = vivid red `#FA1E1E` carried through red-lit full-bleed photography; mixed left/center alignment, giant typographic "A" |
| **Dedalo** | renewal | **Product name spaced SANS-SERIF caps** (serif reserved for Artemide logo only); accent = 6-way product colorway, not one brand color; black spotlight mood sections; it's an umbrella stand reusing the lamp template |
| **Eclisse renewal** | renewal | **Two side-by-side ~1000px columns** (showcase + trust/service); heavy full-bleed black heroes; adds trust/benefit icon grid (2Ã3), promo, Showroom directory |
| **Shogun** | renewal | **Left-aligned (~100px indent)**; this node is **info/brand template ONLY** (ê³µìììì¬ + Brand + Designer) with **no product showcase at all**; sans-serif Bold headlines; black full-bleed designer section |

**Renewal-generation signature (the variant layer):**
1. Left-alignment instead of center (Tolomeo Mega, Shogun; mixed in Sintesi).
2. Sans-serif product name instead of serif (Tolomeo Mega, Dedalo).
3. Full-bleed **black** brand/designer/mood sections breaking pure-white (Tolomeo Micro/Mega, Sintesi, Dedalo, Eclisse-renewal, Shogun).
4. A reusable **front-matter template**: ê³µìììì¬ í¸ë¬ì¤í¸ ë¸ë¡ â Artemide BRAND (giant "A" watermark) â DESIGNER (black bg + B&W portrait), prepended before the product hero (Tolomeo Micro/Mega, Eclisse-renewal, Shogun, Sintesi, Dedalo).

## 4. Section-flow catalogue (union, typical order)

Typical renewal-era top-to-bottom order, with frequency:

| # | Section | Frequency | Seen in |
|---|---|---|---|
| 0 | **ê³µì ììì¬ / Trust-benefits block** (ë¬´ë£ë°°ì¡Â·êµíÂ·A/SÂ·KCì¸ì¦) | Occasional (renewal front-matter) | Tolomeo Micro, Tolomeo Mega, Eclisse-ren, Shogun |
| 1 | **Brand statement** (Artemide wordmark + giant "A" + 1960 heritage) | **Near-universal** | All except bare-old Onfale uses a lighter version; explicit in 7/8 |
| 2 | **Designer block** (portrait + bio; B&W; often black bg) | **Universal** | All 8 (Vistosi, De Lucchi, Magistretti, Gismondi, Botta, Schweinberger) |
| 3 | **Product hero** (name + tagline over full-bleed photo) | Universal* | All except Shogun (template-only node has no product) |
| 4 | **Product intro copy** | Universal* | 7/8 |
| 5 | **Material / feature / mechanism** (with macro photos) | Common | Onfale, Tolomeo Micro, Eclisse-ren, Sintesi |
| 6 | **Lifestyle / mood photography** (full-bleed) | **Universal** | All 8 |
| 7 | **Color options** (swatch grid or single swatch) | Occasional | Onfale (single White), Eclisse Orange (single Orange), Tolomeo Micro (multi), Eclisse-ren (4-row OPTION+MATERIALS) |
| 8 | **Dimension diagram** (line drawing) | Occasional | Onfale, Eclisse Orange, Eclisse-ren only â **absent** in Tolomeo Mega/Micro, Sintesi, Dedalo, Shogun |
| 9 | **Spec table** (íëª/ì ì¡°ì¬/ìì¬/KC/ì ì/ìì¼) | Rare | Eclisse-ren only |
| 10 | **Service column** (Benefit promo, Showroom directory, ë°°ì¡ì ì°¨) | Rare | Eclisse-ren right column; partial gray Benefit card in Eclisse Orange |
| 11 | **Footer policy** (êµíÂ·íë¶Â·A/SÂ·ê³ ê°ì¼í°) | Rare | Eclisse Orange |

**Universal core (always present):** Brand statement, Designer block, Lifestyle photography. **Hero + intro** universal wherever a product is actually shown. **Color/dimension/spec/footer are OPTIONAL** and product-dependent.

## 5. Per-brand accent rule â CONFIRMED

**Accent = brand or product color, NEVER a fixed gold.** Confirmed in all 8 `differs` notes. Observed accent values:

| Product | Accent | Hex |
|---|---|---|
| Onfale | Artemide scarlet (wordmark only) | `#DE0515` |
| Eclisse Orange | Artemide red + product orange | `#E2231A` / `#E8541E` |
| Eclisse renewal | Artemide crimson + product orange | `#D80010` / `#F04820` |
| Sintesi | Vivid red (lamp's own color, drives full-bleed red-lit photography) | `#FA1E1E` |
| Tolomeo Micro | Brand charcoal (no chromatic accent) + multi product finishes | `#1C1C1C` |
| Tolomeo Mega | Monochrome (ink black on white), warmth only from photography | `#000`/`#1A1A1A` |
| Dedalo | Six product colorways stand in for accent (mustard/cobalt/lavender/olive/lt-blue/pink) | n/a (product-driven) |
| Shogun | Achromatic only (black/white/gray + giant "A") | none |

**Rule for the tool:** Artemide's signature chromatic accent is **red** (`#DE0515` â `#D80010`), but the accent must be **a parameter sampled per-brand/per-product**, with a legitimate **achromatic/monochrome fallback** (Tolomeo Mega, Shogun) and a **product-colorway fallback** (Dedalo). **Gold `#D4AF37` must never appear** â it is currently hard-coded in the Premium preset and is wrong for this client.

## 6. Recommendations for the tool

The target files in your brief (`docs/playbook/visual-tone.md`, `design_tokens/duomo-detail.json`) **do not exist yet** â they are net-new. The existing tool at [`landing-page-generator-main`](C:/Users/OWNER/Downloads/landing-page-generator-main) is hard-wired to the *opposite* of this client's tone. Concrete actions:

### 6a. CREATE `design_tokens/duomo-detail.json` (net-new)
There is no `design_tokens/` directory yet â create it. Proposed token set from the full sweep:

```json
{
  "canvas":  { "width_px": 1000, "note": "content unit; ignore oversized Figma artboards (8739px = padding)" },
  "alignment": { "baseline": "center", "renewal": "left" },
  "color": {
    "bg_white": "#FFFFFF",
    "bg_black": "#0A0A0A",
    "text_primary": "#1F1F1F",
    "text_secondary": "#888888",
    "accent": "<<PER_BRAND>>",
    "accent_default_artemide": "#DE0515",
    "accent_fallback_modes": ["brand_red", "achromatic", "product_colorway"],
    "FORBIDDEN": ["#D4AF37 gold"]
  },
  "type": {
    "wordmark_serif": "Noto Serif Display",
    "product_name": { "baseline": "Noto Serif Display", "renewal": "Pretendard Bold (sans) caps, wide tracking" },
    "body": "Pretendard ~40px"
  },
  "structure": "showcase",
  "forbidden_sections": ["pain","problem","story_funnel","social_proof","authority_sales","benefits_bonus","risk_removal","comparison","target_filter","final_cta","price","urgency","scarcity"]
}
```

### 6b. CREATE `docs/playbook/visual-tone.md` (net-new) â or fold into [`references/design-specs.md`](C:/Users/OWNER/Downloads/landing-page-generator-main/references/design-specs.md)
Document: **two generations** (baseline center/white/serif vs renewal left/black/sans), the universal-core section list (Brand â Designer â Lifestyle always present; Hero+Intro when product shown), and the optional spec blocks.

### 6c. **BLOCKING â the 13-section funnel template must be REPLACED, not tweaked.**
[`references/13-section-guide.md`](C:/Users/OWNER/Downloads/landing-page-generator-main/references/13-section-guide.md) and the emotional-journey funnel (`[ì£¼ëª©]â[ê³µê°]â[ì´í´]â...â[íë]`, Pain/Problem/Social-Proof/Risk/Comparison/CTA) are **fundamentally incompatible** with this client. 8/8 products have **zero** funnel sections. Replace the 13-section funnel with the **DUOMO showcase flow**:

> **ê³µìììì¬(í¸ë¬ì¤í¸, optional) â Brand statement â Designer â Product hero â Intro â Material/Feature â Lifestyle(ë°ë³µ) â Color options(optional) â Dimension/Spec(optional) â Footer policy(optional)**

Keep the funnel template as a *separate preset* for non-Artemide clients, but it must not be the default for DUOMO catalog work.

### 6d. Fix the hard-coded conflicts in existing files
- [`references/design-specs.md`](C:/Users/OWNER/Downloads/landing-page-generator-main/references/design-specs.md) line 6â8 & 23: **width is locked to 1200px** â must be **1000px** for DUOMO. The whole section-height table (lines 28â45) is the funnel and must not drive DUOMO pages.
- [`references/design-specs.md`](C:/Users/OWNER/Downloads/landing-page-generator-main/references/design-specs.md) "Premium" preset (line 96â117): **`accent: #D4AF37 (Gold)`** â wrong. DUOMO/Artemide accent is **brand red `#DE0515`** with achromatic fallback. Add a **`duomo`/`artemide` preset** rather than reusing Premium.
- [`agents/04-design-direction.md`](C:/Users/OWNER/Downloads/landing-page-generator-main/agents/04-design-direction.md) line 58â62 (`premium` â gold) and line 100 (`max_width: 1200px`) and the `section_backgrounds` funnel map (lines 190â204): all carry the gold/1200/funnel defaults into the JSON the pipeline consumes. Add an Artemide branch: `max_width: 1000`, `accent: brand color (no gold)`, showcase section map.
- [`references/copy-patterns.md`](C:/Users/OWNER/Downloads/landing-page-generator-main/references/copy-patterns.md): **entirely sales-funnel copy** (urgency, scarcity, price-strikethrough, ê¸´ê¸ì±/í¬ìì±, CTA buttons). None applies â DUOMO copy is ê²½ì´ì²´ brand-storytelling with no price/CTA/urgency. Add a `copy-patterns-showcase.md` (heritage + designer + material storytelling, short emotional headline + 2â3 line informational body) and gate the funnel copy behind the non-Artemide preset.

### 6e. One nuance worth a note in the playbook
The Onfale `differs` field flags that requesting that nodeId at high-res **intermittently rendered an adjacent DEDALO frame**. If the pipeline pulls Figma renders by nodeId, add a **content-verification step** (confirm the product name in the render matches the requested product) before sampling tone â otherwise tokens can be cross-contaminated between products.

**Bottom line:** tone is consistent enough to standardize (1000px / ê²½ì´ì²´ / showcase / brand-color-not-gold are non-negotiable across all 8). The only real fork is the **renewal layer** (left-align + sans product name + black sections). The existing generator's 1200px / gold / 13-section-funnel defaults are the single biggest risk and must be replaced with a DUOMO showcase preset before this tool generates Artemide pages."
  }
}