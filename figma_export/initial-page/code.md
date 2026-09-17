# Figma Design Context — Living Manna: Initial Page (event chooser)

**Source:** https://www.figma.com/design/KT1MB0kyS04Sc5HKBxhGaz/Living-Manna-Registration-Page?node-id=40-1063&m=dev
**File key:** KT1MB0kyS04Sc5HKBxhGaz
**Node:** 40:1063 ("Initial Page") — 1440×1312. A landing page that sits in front of the two registration forms (`4:7` Savannah / `40:892` Pasadena, both already pulled into `../registration/` and `../registration-pasadena/`), letting the visitor pick which event to register for.

Treat all code below as REFERENCE ONLY (React/Tailwind) — adapt to this project's actual stack before implementing.

---

## 1. Assets

**Reused, byte-identical to the earlier pulls — not re-downloaded:**
- Hero background image (`imgRectangle5`, asset filename `d4714.png`) — same shared marketing-flyer graphic used on both registration pages. See `../registration/hero-bg.png`.

**New in this folder:**
- `frame.png` — full-page 2x export (2880×2624, exact 2x of 1440×1312).

There are **no new icons or other graphics on this page** — confirmed via `download_assets`, which returned zero `svgAssets` and only the two already-known hero-fill `rawImages`. The event-selector box has no icon/chevron/arrow graphic at all (see §4 — this is itself a notable gap, not just "nothing new to report").

---

## 2. Reference code (from get_design_context)

```jsx
const imgRectangle5 = `${assetPathPrefix}/d4714.png`; // same as registration/ and registration-pasadena/

export default function InitialPage() {
  return (
    <a className="bg-[#f9f7f3] block cursor-pointer relative size-full" data-node-id="40:1063" data-name="Initial Page">
      {/* ^ NOTE: the ENTIRE page — hero image AND the selector card below it — is wrapped in a single
           <a> / cursor-pointer element by Figma's codegen. No href is given (Figma resolved some kind
           of prototype "on click" interaction on the frame itself, which this tool can't resolve to a
           real URL). This is almost certainly a Figma-prototyping artifact, not an intentional "click
           anywhere on the page to navigate" design — see §4 for why, and what to actually check before
           implementing navigation. */}

      <div className="-translate-x-1/2 absolute h-[700px] left-1/2 top-0 w-[1440px]" data-node-id="40:1064">
        <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full" src={imgRectangle5} />
      </div>

      <div className="-translate-x-1/2 absolute bg-white border-[#d8a52f] border-[0.5px] border-solid content-stretch flex flex-col gap-[30px] items-start justify-center left-1/2 px-[100px] py-[45px] rounded-[20px] top-[800px] w-[1100px]" data-node-id="40:1234">
        <p className="font-['Montserrat:Bold'] font-bold leading-[32px] text-[#c98a2b] text-[18px] text-left tracking-[0.36px] whitespace-nowrap" data-node-id="40:1235">
          SELECT YOUR EVENT
        </p>
        <p className="font-['Montserrat:Medium'] font-medium leading-[0] text-[#0b2242] text-[16px] text-left tracking-[0.32px] whitespace-nowrap" data-node-id="40:1236">
          <span className="leading-[32px]">{`Which event will you be attending? `}</span>
          <span className="leading-[32px] text-[#c98a2b]">*</span>
        </p>
        <div className="bg-[#fbf5ed] border border-[#d8a52f] border-solid content-stretch flex h-[71px] items-start px-[40px] py-[20px] relative rounded-[10px] shrink-0 w-[950px]" data-node-id="40:1248">
          <p className="font-['Montserrat:Light_Italic'] font-light italic leading-[32px] text-[16px] text-black text-left tracking-[0.32px] whitespace-nowrap" data-node-id="40:1249">
            Choose an event
          </p>
        </div>
        <p className="font-['Montserrat:Regular'] font-normal leading-[32px] text-[#1c1c1c] text-[16px] text-left tracking-[0.32px] whitespace-nowrap" data-node-id="40:1244">
          Select an event above to see its details and registration form.
        </p>
      </div>
    </a>
  );
}
```

---

## 3. Verbatim copy (source of truth)

- Card heading: `SELECT YOUR EVENT`
- Question label: `Which event will you be attending? *`
- Selector placeholder text: `Choose an event`
- Helper text below the selector: `Select an event above to see its details and registration form.`

That's the complete copy on this page — no other body text, no per-option labels are visible anywhere in the static design (see §4 — the two actual event names/dates never appear as literal option strings anywhere in this frame; they're inferred from the hero image and the two registration pages, not confirmed as the dropdown's exact option text).

---

## 4. Selector styling, and the navigation-trigger ambiguity (flagged, not guessed)

### Styling (what IS clear)
| Property | Value |
|---|---|
| Box size | 950px wide × 71px tall |
| Background | `#fbf5ed` (same cream as every text input on the registration pages) |
| Border | `1px solid #d8a52f` (note: full `1px`, not the `0.5px` used on the registration pages' text inputs — a deliberately slightly heavier border here, or possibly just an inconsistency; worth a visual side-by-side check) |
| Corner radius | `10px` |
| Padding | `40px` horizontal, `20px` vertical |
| Placeholder text | `Choose an event` — Montserrat **Light Italic**, 16px, line-height 32px, tracking 0.32px, color `#000000` (pure black — same treatment as the "Short answer" textarea placeholder on the registration pages) |

This matches the visual pattern of every other form-input placeholder in the file (cream fill, gold border, black light-italic placeholder text) — styling itself is unambiguous and consistent with the rest of the design system.

### What's genuinely unclear from this static export (flagged per your ask, not resolved by guessing)

1. **No dropdown affordance is drawn.** There's no chevron/arrow icon, no expanded/open-state variant, and no separate list of options anywhere in the node tree (`get_metadata` shows exactly one child inside the selector box: the placeholder text node — nothing else). It's visually indistinguishable from a plain text input except for the phrasing ("Choose an event" / "Which event will you be attending?"), which strongly implies a `<select>` or a custom dropdown, but the design doesn't show what the open/expanded state or the two option rows actually look like.
2. **The two event names never appear as literal copy anywhere on this page.** Nothing in the live text confirms the exact option strings a real `<select>` should show (e.g. is it "Harbert Hills Academy — October 14–17, 2026" per option, or a shorter "Savannah, TN" / "Pasadena, CA", or something else entirely?). The most reasonable inference — pairing each event's venue name with its dates, matching how they're already labeled in the shared hero image and in each registration page's own info-pills (`../registration/code.md` §3b, `../registration-pasadena/code.md` §3) — would be:
   - `Harbert Hills Academy — October 14–17, 2026 (Savannah, TN)`
   - `Pasadena SDA Church — October 21–24, 2026 (Pasadena, CA)`

   …but that's a reasonable guess for implementation, not something confirmed by the design file. Flag with the content/design owner before finalizing option copy.
3. **What triggers navigation is not shown at all, and is the biggest open question:**
   - There is **no visible "Continue" / "Next" / submit button anywhere in this frame** — the selector and the helper text below it are the only interactive-looking elements.
   - The helper text itself ("Select an event above to see its details and registration form.") reads as though **selecting the dropdown value is the trigger** — i.e., choosing an option immediately navigates to (or reveals) that event's registration form, with no separate confirm step. That's the most natural reading of the copy, and the absence of any button reinforces it.
   - However, the **entire frame is wrapped in a single, unexplained `<a>`/clickable-block element** (see the reference code above) — which doesn't fit a "select from a dropdown" interaction model at all (an anchor around the whole page, including the hero image and the helper text below the selector, isn't how you'd wire up a `<select>`'s `onChange`). This is very likely a **leftover/stray Figma prototype link** (e.g. an "on click, navigate to frame X" hotspot accidentally left on the top-level frame, possibly from copying one of the two registration-page frames as a starting point and never removing/repointing its interaction) rather than a deliberate instruction to make the whole page one clickable link. It does not resolve to a usable href via these tools, and shouldn't be taken as a literal implementation instruction.

   **Recommendation:** implement this as a `<select>` (or equivalent) whose `onChange` navigates immediately to the corresponding registration page — no separate "Continue" button — since that's what the copy and the absence of any button most strongly suggest. But treat this as an inference to confirm with the design/product owner before building it, not a settled spec; specifically confirm (a) immediate-navigate-on-select vs. a button being added later, and (b) the exact option label text for each event.

---

## 5. Layout / spacing

- Hero: 1440×700, same position/size as both registration pages (y=0). Not re-described further — see `../registration/code.md` §7 for why the hero itself is treated as out of scope for detailed analysis.
- Selector card: 1100px wide, centered (`left-1/2` + `-translate-x-1/2`), starts at y=800 (100px below the hero's bottom edge at y=700 — slightly more breathing room than the registration pages' 80px hero-to-content gap).
- Card padding: `100px` horizontal, `45px` vertical; `30px` vertical gap between the heading/question/selector/helper-text stack; corner radius `20px`; border `0.5px solid #d8a52f` — all consistent with the registration pages' card styling.
- Card height: 348px total (hugs its content — heading 32 + gap 30 + question 32 + gap 30 + selector 71 + gap 30 + helper text 32, plus 45px top/bottom padding ≈ matches).

---

## 6. Notes

- `get_variable_defs` returned `{}` — no Figma Variables bound here, consistent with every other node pulled from this file.
- Colors/fonts used on this page (`#c98a2b` gold heading, `#0b2242` navy question text + gold asterisk, `#fbf5ed`/`#d8a52f` input styling, `#1c1c1c` helper text, Montserrat throughout) are all already-documented tokens from `../registration/variables.json` — nothing new to add to the shared palette.
- `frame.png` is a full, non-cropped 2x export (2880×2624).
