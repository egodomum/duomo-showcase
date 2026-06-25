# 최종 브랜드 전수조사 closeout (12브랜드/26제품)

The model holds. Here is the closeout.

---

# DUOMO Detail-Page Tone â Final Cross-Brand Closeout

## 1. Final verdict
The model **holds**. Across now ~12 brands (Flos, Astep, Lasvit, ingo Maurer*, Marset, Santa&Cole, Vibia + the established 9) and both categories (lighting + furniture), every new page is recognizably the same spine: **1000px showcase Â· no funnel/price/urgency/hard-CTA Â· accent = brand color, never gold Â· BrandâDesignerâLifestyle Â· ê²½ì´ì²´ Â· two generations**.

**Fit rate over the 11 new findings: 7 yes / 4 partial / 0 no.**
- **yes (7):** 2097/50 (Flos), Bon Jour Unplugged (Flos), Marset Dipping Light Ã3 instances (the "Astep 2065", "TMM íë¡ì´", and the native Marset node), Lasvit La Scala, Vibia Flamingo.
- **partial (4):** FLOS 2097/18 ("SNOOPY" node), Astep Model 2065 ("Zettel'z" node), Santa&Cole Lamina 166/85. The partials are **not** tone violations â the spine, 1000px, ê²½ì´ì²´, no-funnel rules all pass. They drop to partial only because they **append commerce/spec modules** below the showcase.

No page used gold as a UI accent. No page introduced a funnel, price, urgency, or hard-CTA. **Zero rejects.**

## 2. New accent colors
Note the dominant pattern: **the new brands are achromatic by identity**, so for most, accent = mono is the brand color (rule still satisfied â never gold).

| Brand | Accent | Source |
|---|---|---|
| **Flos** | **Deep navy / midnight blue â #29406C** on spec block (only chromatic new accent); otherwise mono black serif | 2097/50; mono on Bon Jour, 2097/18 |
| **Astep** | Mono (black/white/grey, pill outlines) | Model 2065 |
| **Lasvit** | Mono (near-black serif; amber is product glass, not UI) | La Scala Pendant |
| **ingo Maurer** | *No actual page* â the "Zettel'z" node rendered Astep 2065; **no genuine ingo Maurer sample observed** | â |
| **Marset** | Mono (black lowercase sans wordmark) | Dipping Light Ã3 |
| **Santa&Cole** | Mono (black/grey; brand color is itself achromatic) | Lamina 85/166 |
| **Vibia** | Mono (Vibia brand color is black/monotone by identity) | Flamingo Mini |

## 3. Anything novel
The spine is untouched, but the partials surface **one genuinely new layer not in the 16-product baseline: a structured commerce/spec block stack** appearing below the showcase. It recurs consistently enough to be a real pattern, not noise:
- **Variant selectors** â finish swatch grids (BLACK/BRASS/CHROME/WHITE) and size/êµ¬ì lineup selectors (2097 18/30/50).
- **`OPTION` spec-row blocks** â per-variant COLOR swatch + MATERIALS, catalog-style.
- **CAD dimensioned line-drawings** â engineering schematics (e.g. 2800/510/Ã¸690mm; Ã131/270mm; 22,2cm/Ã¸6cm). This is the most widespread novel element â it appears across Flos, Marset, Lasvit, Santa&Cole, Astep.
- **Full ìíì ë³´ spec table** absorbing KCì¸ì¦ë²í¸ / IP / ìì¼ / ì ì.
- **Purchase-advisory / ì ì© ì êµ¬ block** (FLOS bulb-included notice) and, on the renewal Astep, a **ì¦ì /Benefit pill section + ë°°ì¡ ì ì°¨ section + 6-cell trust grid** (ì ë¬¸ìê³µíÂ·ë¬´ë£ìê³µÂ·1ë A/SÂ·ë¬´ë£ë°°ì¡Â·êµ­ë´ìê³ Â·ì êµ¬ì ê³µ) â wider than the canonical 4-cell trust block.
- **Localization section** â Vibia's "FLAMINGO MINI KOREA CUSTOM" (a named KO-market variant block) is a new section *type*.

Two non-design flags worth carrying forward (data hygiene, not tone): (a) **pervasive node-name â content mismatches** â "SNOOPY"â2097, "Zettel'z"âAstep 2065, "TMM íë¡ì´/Santa&Cole" & "Astep 2065"âMarset Dipping Light, "Lamina 166"âLamina 85; the generator must key off **rendered content, not node label**. (b) Page typo "Pandent/Pandent" on Lasvit.

**Conclusion on novelty:** these are **additive spec/commerce modules layered onto an unchanged tone spine** â directly analogous to how furniture added module/fabric/SH sections. They extend the model; they do not break it. They should be folded in as an **optional "commerce-spec" module set** (variant selector Â· OPTION Â· CAD dimension drawing Â· full spec table Â· trust/ë°°ì¡ block Â· KO-localization), toggled per product complexity (chandeliers/portables with finishes & sizes pull it in; simple SKUs don't).

## 4. One-line conclusion
The DUOMO tone model is **COMPLETE and safe to build the generator on** â spine and rules held at 100% (0 rejects across ~12 brands and both categories); only add an **optional commerce-spec module set** and make the pipeline read rendered content rather than node names.

\* No authentic ingo Maurer page was actually present â its only candidate node rendered Astep. If an ingo Maurer accent is needed for the generator's brand map, it remains **unverified** and should be sampled before launch."
  }
}