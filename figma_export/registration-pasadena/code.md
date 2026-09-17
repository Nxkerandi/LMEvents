# Figma Design Context — Living Manna Registration Page (Pasadena / "Event 2")

**Source:** https://www.figma.com/design/KT1MB0kyS04Sc5HKBxhGaz/Living-Manna-Registration-Page?node-id=40-892&m=dev
**File key:** KT1MB0kyS04Sc5HKBxhGaz
**Node:** 40:892 ("Event 2") — sibling top-level frame to `4:7` ("FInal Frame", the Savannah/Harbert Hills Academy page pulled earlier into `../registration/`). Same overall size, 1440×5144.

This is a **real second event** (Pasadena SDA Church, Oct 21–24, 2026), not a duplicate/placeholder — content below is transcribed verbatim for seeding, same as the Savannah pull.

Treat all code below as REFERENCE ONLY (React/Tailwind) — adapt to this project's actual stack before implementing.

---

## 1. Assets — reuse vs. new

**Reused, byte-identical to the Savannah pull — not re-downloaded:**
- Hero background image (`imgRectangle5`, asset filename `d4714.png`) — same file hash/name as `../registration/hero-bg.png`. Confirmed both by identical filename and by the hero graphic legitimately depicting *both* events on one shared marketing flyer (as already documented in `../registration/code.md` §3a/§7) — this is expected, not a mistake.
- All 4 icons — filenames `d2214.svg` (calendar), `89403.svg` (location), `5853e.svg` (admission), `ecb47.svg` (notice), and confirmed by identical `sizeBytes` (5905 / 1036 / 1429 / 3362 respectively) on a fresh `download_assets` call — byte-identical to `../registration/icon-calendar.svg`, `icon-location.svg`, `icon-admission.svg`, `icon-notice.svg`. Reuse those files; nothing new to save here.

**New in this folder:**
- `frame.png` — full-page 2x export of this frame (2880×10288, same dimensions as the Savannah export since both top-level frames are 1440×5144).

No new icons, logos, or other visual assets appear in this frame beyond what's already in `../registration/`.

---

## 2. Reference code (from get_design_context)

Structurally identical to the Savannah frame (see `../registration/code.md` §2 for the full component breakdown — `Frame3` submit button, `Frame469` Yes/No toggle, `Frame478` session-option button, `Frame468` text input, `CheckBox`/`Group1` checkbox states all reused unchanged). Only the content-bearing text nodes below differ; class/styling strings are identical unless called out in §4.

```jsx
const imgRectangle5 = `${assetPathPrefix}/d4714.png`; // same as Savannah
const imgLayer1 = `${assetPathPrefix}/d2214.svg`;      // same as Savannah
const imgLayer2 = `${assetPathPrefix}/89403.svg`;      // same as Savannah
const imgLayer3 = `${assetPathPrefix}/5853e.svg`;      // same as Savannah
const imgLayer4 = `${assetPathPrefix}/ecb47.svg`;      // same as Savannah

export default function Event2() {
  return (
    <div className="bg-[#f9f7f3] relative size-full" data-node-id="40:892" data-name="Event 2">
      <div className="-translate-x-1/2 absolute h-[700px] left-1/2 top-0 w-[1440px]" data-node-id="40:893">
        <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full" src={imgRectangle5} />
      </div>
      <div className="absolute content-stretch flex flex-col gap-[35px] items-center left-[170px] top-[780px] w-[1100px]" data-node-id="40:894">
        <div className="content-stretch flex flex-col gap-[40px] items-start relative shrink-0 w-full" data-node-id="40:895">

          {/* ABOUT THIS EVENT — identical structure/styling to Savannah; only info-pill text differs */}
          <div className="bg-white border-[#d8a52f] border-[0.5px] border-solid content-stretch flex flex-col gap-[35px] items-start px-[100px] py-[40px] relative rounded-[20px] shrink-0 w-full" data-node-id="40:896">
            <p className="font-['Montserrat:Bold'] font-bold leading-[32px] text-[#0b2242] text-[18px] tracking-[0.36px] w-[416px]" data-node-id="40:899">ABOUT THIS EVENT</p>
            <p className="font-['Montserrat:Regular'] font-normal leading-[32px] text-[#1c1c1c] text-[16px] tracking-[0.32px] w-[799px]" data-node-id="40:900">{`Join us for four days of meetings designed to prepare our hearts and homes for what lies ahead. Together we'll consider what it means to build a home that honors God now, in view of the eternal home He is preparing for us.`}</p>
            <div className="bg-[#fbf5ed] border-[#c98a2b] border-l-5 border-solid content-stretch flex flex-col gap-[30px] items-start pl-[50px] pr-[30px] py-[25px] relative shrink-0 w-[800px]" data-node-id="40:901">
              <p className="font-['Montserrat:Italic'] font-normal italic leading-[32px] text-[#1c1c1c] text-[16px] tracking-[0.32px] w-[715px]" data-node-id="40:903">{`"The well-being of society, the success of the church, and the prosperity of the nation truly depend upon home influences."`}</p>
              <p className="font-['Montserrat:SemiBold'] font-semibold leading-[32px] text-[#0b2242] text-[16px] tracking-[0.32px] w-[416px]" data-node-id="40:905">ELLEN G. WHITE, THE ADVENTIST HOME, p. 15.1</p>
            </div>
            <p className="font-['Montserrat:SemiBold'] font-semibold leading-[32px] text-[#0b2242] text-[18px] tracking-[0.36px] w-[416px]" data-node-id="40:908">SPEAKERS</p>
            <div className="content-stretch flex gap-[35px] items-center relative shrink-0" data-node-id="40:909">
              <div className="bg-[#fbf5ed] border-[#c98a2b] border-[0.5px] border-solid content-stretch flex items-center justify-center px-[40px] py-[15px] relative rounded-[10px] shrink-0" data-node-id="40:910">
                <p className="font-['Montserrat:Medium'] font-medium leading-[normal] text-[#0b2242] text-[16px] whitespace-nowrap" data-node-id="40:911">{`Devaney & Fazlyn Haupt`}</p>
              </div>
              <div className="bg-[#fbf5ed] border-[#c98a2b] border-[0.5px] border-solid content-stretch flex items-center justify-center px-[40px] py-[15px] relative rounded-[10px] shrink-0" data-node-id="40:912">
                <p className="font-['Montserrat:Medium'] font-medium leading-[normal] text-[#0b2242] text-[16px] whitespace-nowrap" data-node-id="40:913">{`Elvin & Marcia Bridges`}</p>
              </div>
            </div>
            <div className="content-stretch flex flex-col gap-[20px] items-start justify-center relative shrink-0" data-node-id="40:914">
              <div className="bg-[rgba(220,226,240,0.1)] border border-[#0b2242] border-solid content-stretch flex gap-[20px] items-center justify-center px-[40px] py-[15px] relative rounded-[40px] shrink-0" data-node-id="40:915">
                <img alt="" className="h-[30px] w-[31.588px]" src={imgLayer1} />
                <p className="font-['Montserrat:SemiBold'] font-semibold leading-[normal] text-[#0b2242] text-[16px] tracking-[0.48px] whitespace-nowrap" data-node-id="40:935">October 21–24, 2026</p>
              </div>
              <div className="bg-[rgba(220,226,240,0.1)] border border-[#0b2242] border-solid content-stretch flex gap-[20px] items-center justify-center px-[40px] py-[15px] relative rounded-[40px] shrink-0" data-node-id="40:936">
                <img alt="" className="h-[30px] w-[21.929px]" src={imgLayer2} />
                <p className="font-['Montserrat:SemiBold'] font-semibold leading-[normal] text-[#0b2242] text-[16px] tracking-[0.48px] whitespace-nowrap" data-node-id="40:940">1280 E. Washington Blvd, Pasadena, CA, 91104</p>
              </div>
              <div className="bg-[rgba(220,226,240,0.1)] border border-[#0b2242] border-solid content-stretch flex gap-[20px] items-center justify-center px-[40px] py-[15px] relative rounded-[40px] shrink-0" data-node-id="40:941">
                <img alt="" className="h-[30px] w-[50px]" src={imgLayer3} />
                <p className="font-['Montserrat:SemiBold'] font-semibold leading-[normal] text-[#0b2242] text-[16px] tracking-[0.48px] whitespace-nowrap" data-node-id="40:945">Free Admission</p>
              </div>
            </div>
          </div>

          {/* SCHEDULE — identical structure; dates only differ */}
          <div className="bg-white border-[#d8a52f] border-[0.5px] border-solid content-stretch flex flex-col gap-[20px] items-start px-[50px] py-[40px] relative rounded-[20px] shrink-0 w-full" data-node-id="40:946">
            <p className="font-['Montserrat:Bold'] font-bold leading-[32px] text-[#c98a2b] text-[18px] tracking-[0.36px] whitespace-nowrap" data-node-id="40:947">SCHEDULE</p>
            <div className="border-[#c98a2b] border-b border-solid content-stretch flex font-['Montserrat:Medium'] font-medium gap-[301px] items-center leading-[32px] pb-[10px] relative shrink-0 text-[#1c1c1c] text-[18px] tracking-[0.36px] w-[1000px] whitespace-nowrap" data-node-id="40:948">
              <p data-node-id="40:949">DATE</p><p data-node-id="40:950">SESSION</p><p data-node-id="40:951">TIME</p>
            </div>
            <div className="border-[#d8a52f] border-b-[0.75px] border-solid content-stretch flex gap-[57px] items-center pb-[10px] relative shrink-0 w-full" data-node-id="40:952">
              <div className="bg-[#0b2242] content-stretch flex items-center justify-center px-[40px] py-[10px] relative rounded-[40px] shrink-0" data-node-id="40:953"><p className="font-['Montserrat:SemiBold'] font-semibold text-[16px] text-white tracking-[0.48px] whitespace-nowrap" data-node-id="40:954">Wed, Oct 21</p></div>
              <p className="font-['Montserrat:Regular'] text-[#1c1c1c] text-[16px] tracking-[0.32px] whitespace-nowrap" data-node-id="40:956">Preparing The Home For Home – Evening Session</p>
              <p className="font-['Montserrat:Regular'] text-[#1c1c1c] text-[16px] tracking-[0.32px] whitespace-nowrap" data-node-id="40:958">6.00 PM - 9.00 PM</p>
            </div>
            <div className="border-[#d8a52f] border-b-[0.75px] border-solid content-stretch flex gap-[57px] items-center pb-[10px] relative shrink-0 w-full" data-node-id="40:959">
              <div className="bg-[#0b2242] ... rounded-[40px] shrink-0 w-[183px]" data-node-id="40:960"><p data-node-id="40:961">Thu, Oct 22</p></div>
              <p data-node-id="40:963">Preparing The Home For Home – Evening Session</p>
              <p data-node-id="40:965">6.00 PM - 9.00 PM</p>
            </div>
            <div className="border-[#d8a52f] border-b-[0.75px] border-solid content-stretch flex gap-[57px] items-center pb-[10px] relative shrink-0 w-full" data-node-id="40:966">
              <div className="bg-[#0b2242] ... rounded-[40px] shrink-0 w-[183px]" data-node-id="40:967"><p data-node-id="40:968">Fri, Oct 23</p></div>
              <p data-node-id="40:970">Preparing The Home For Home – Evening Session</p>
              <p data-node-id="40:972">6.00 PM - 9.00 PM</p>
            </div>
            <div className="content-stretch flex gap-[57px] items-center pb-[10px] relative shrink-0 w-full" data-node-id="40:973">
              <div className="bg-[#0b2242] ... rounded-[40px] shrink-0 w-[183px]" data-node-id="40:974"><p data-node-id="40:975">Sat, Oct 24</p></div>
              <p data-node-id="40:977">Preparing The Home For Home – All-Day Program</p>
              <p data-node-id="40:979">9.00 AM - 6.00 PM</p>
            </div>
          </div>

          {/* Registration-deadline notice bar — identical structure; date differs */}
          <div className="bg-[rgba(255,255,255,0.1)] border border-[#d8a52f] border-solid content-stretch flex gap-[30px] items-start pl-[100px] pr-[30px] py-[25px] relative rounded-[10px] shrink-0 w-full" data-node-id="40:980">
            <img alt="" className="h-[32px] w-[31.998px]" src={imgLayer4} />
            <p className="font-['Montserrat:Italic'] font-normal italic leading-[0] text-[#0b2242] text-[16px] tracking-[0.32px] w-[715px]" data-node-id="40:986">
              <span className="font-['Montserrat:Regular'] leading-[32px]">Please register by</span>
              <span className="font-['Montserrat:SemiBold'] font-semibold leading-[32px]">{` Sunday, October 4, 2026.`}</span>
              <span className="font-['Montserrat:Regular'] leading-[32px]">{` This event is free to attend.`}</span>
            </p>
          </div>

          {/* YOUR INFORMATION — fully identical (no event-specific content in this section) */}
          {/* WHICH SESSIONS WILL YOU ATTEND? — identical structure; dates differ, NO typo this time */}
          <div className="bg-white border-[#d8a52f] border-[0.5px] border-solid content-stretch flex flex-col gap-[35px] items-start justify-center px-[100px] py-[45px] relative rounded-[20px] shrink-0 w-full" data-node-id="40:1007">
            <p className="font-['Montserrat:Bold'] font-bold leading-[32px] text-[#c98a2b] text-[18px] tracking-[0.36px] w-full" data-node-id="40:1008">WHICH SESSIONS WILL YOU ATTEND? *</p>
            <div className="content-stretch cursor-pointer flex flex-col gap-[20px] items-start relative shrink-0 w-full" data-node-id="40:1009">
              <Frame478 text2="Wednesday, October 21" text="Evening Session : 6.00 PM - 9.00 PM" />
              <Frame478 text2="Thursday, October 22" text="Evening Session : 6.00 PM - 9.00 PM" />
              <Frame478 text2="Friday, October 23" text="Evening Session : 6.00 PM - 9.00 PM" />
              {/* ^ correct and complete here — confirms the Savannah frame's "Friday, October 1" is an
                   isolated typo in that frame specifically, not a shared/default component value. */}
              <Frame478 text2="Saturday, October 24" text="All-Day Program : 9.00 AM - 6.00 PM" />
            </div>
          </div>

          {/* CHILDREN & YOUTH — fully identical (no event-specific content in this section) */}

          {/* SABBATH MEAL — identical structure; date differs */}
          <div className="bg-white border-[#d8a52f] border-[0.5px] border-solid content-stretch flex flex-col gap-[30px] items-start justify-center px-[100px] py-[45px] relative rounded-[20px] shrink-0 w-full" data-node-id="40:1022">
            <p className="font-['Montserrat:Bold'] font-bold leading-[32px] text-[#c98a2b] text-[18px] tracking-[0.36px] whitespace-nowrap" data-node-id="40:1023">SABBATH MEAL</p>
            <p className="font-['Montserrat:Regular'] font-normal leading-[32px] text-[#1c1c1c] text-[16px] tracking-[0.32px] whitespace-nowrap" data-node-id="40:1024">Meals will be provided for all visitors on Sabbath, October 24, only.</p>
            {/* Yes/No question block identical to Savannah */}
          </div>

          {/* ADDITIONAL INFORMATION — fully identical (no event-specific content in this section) */}
        </div>

        <Frame3 /> {/* Submit button — identical */}

        {/* Footer line 1 — identical (same contact/email for both events) */}
        <p className="font-['Montserrat:Regular'] font-normal leading-[0] text-[#1c1c1c] text-[16px] text-center tracking-[0.32px] w-[477px]" data-node-id="40:1036">
          <span className="font-['Montserrat:Medium'] font-medium leading-[32px] text-[#0b2242]">Questions about registration?</span>
          <span className="leading-[32px]"><br aria-hidden />Contact Marcia Bridges ·</span>
          <span className="font-['Montserrat:Medium'] font-medium leading-[32px] text-[#0b2242]">{` `}</span>
          <a className="font-['Montserrat:Medium'] font-medium leading-[32px] text-[#0b2242] underline" href="mailto:livingmanna@yahoo.com" target="_blank">livingmanna@yahoo.com</a>
        </p>

        {/* Footer line 2 — DIFFERENT STYLING from Savannah, not just different text. See §4. */}
        <p className="font-['Montserrat:SemiBold'] font-semibold leading-[normal] text-[#0b2242] text-[16px] text-center tracking-[0.48px] w-[542px]" data-node-id="40:1037">
          1280 E. Washington Blvd, Pasadena, CA, 91104
        </p>
      </div>
    </div>
  );
}
```

---

## 3. Verbatim copy content (source of truth for seeding, Pasadena event only)

**About This Event / Schedule / form-question copy:** identical wording to the Savannah event throughout (same "Join us for four days..." body, same Ellen G. White quote, same speaker names, same "CHILDREN & YOUTH" body, same field labels/helper text, same "Short answer" placeholder, same "Submit", same footer line 1). Only the fields below actually differ — see the full non-date-dependent copy already transcribed in `../registration/code.md` §3b if needed.

**Event-specific values for Pasadena:**
- Dates: `October 21–24, 2026`
- Venue address: `1280 E. Washington Blvd, Pasadena, CA, 91104`
- Registration deadline: `Please register by Sunday, October 4, 2026. This event is free to attend.`
- Schedule:
  - `Wed, Oct 21` — `Preparing The Home For Home – Evening Session` — `6.00 PM - 9.00 PM`
  - `Thu, Oct 22` — `Preparing The Home For Home – Evening Session` — `6.00 PM - 9.00 PM`
  - `Fri, Oct 23` — `Preparing The Home For Home – Evening Session` — `6.00 PM - 9.00 PM`
  - `Sat, Oct 24` — `Preparing The Home For Home – All-Day Program` — `9.00 AM - 6.00 PM`
- Which-Sessions options:
  - `Wednesday, October 21` / `Evening Session : 6.00 PM - 9.00 PM`
  - `Thursday, October 22` / `Evening Session : 6.00 PM - 9.00 PM`
  - `Friday, October 23` / `Evening Session : 6.00 PM - 9.00 PM` (correct — no typo, unlike the Savannah frame's "Friday, October 1")
  - `Saturday, October 24` / `All-Day Program : 9.00 AM - 6.00 PM`
- Sabbath Meal body: `Meals will be provided for all visitors on Sabbath, October 24, only.`
- Footer line 2: `1280 E. Washington Blvd, Pasadena, CA, 91104` — **note: address only, no venue/church name prefix** (see §4 — the Savannah page's equivalent line is `Harbert Hills Academy · 45 Rural Lane, Savannah, TN 38372`, i.e. it names the venue; Pasadena's doesn't name "Pasadena SDA Church" anywhere in live text, even though that name appears in the hero image).

Speakers, admission ("Free Admission"), and the quote/attribution are identical to Savannah — both couples speak at both events per the live text (consistent with the shared hero graphic).

---

## 4. Explicit diff vs. the Savannah frame (`4:7`) — styling/structure, not just content

Everything not listed here is pixel-identical between the two frames (same component styling, same spacing tokens, same card padding/radii, same colors/fonts, same icons, same hero image, same checkbox/toggle/button styling) — confirmed by comparing the full reference code line-by-line.

1. **Footer line 2 has genuinely different styling, not just different text.**
   | | Savannah (`18:512`) | Pasadena (`40:1037`) |
   |---|---|---|
   | Font weight | Regular | **SemiBold** |
   | Color | `#1c1c1c` | **`#0b2242`** (navy) |
   | Line height | `32px` | **`normal`** |
   | Letter spacing | `0.32px` | **`0.48px`** |

   This is the one real visual/structural inconsistency between the two pages — everywhere else, footer/body text consistently uses Regular/`#1c1c1c`/32px/0.32px. This single line breaks that pattern on the Pasadena frame. It also explains a knock-on layout difference: the Pasadena content column is 12px shorter overall (`4145.25` vs `4157.25`) purely because this line's box is shorter (`20px` vs `32px` height) under `leading-normal` vs `leading-[32px]`. Worth confirming with the design/content owner whether this was intentional (e.g. meant to echo the info-pill text styling, which also uses SemiBold/0.48px) or a copy-paste slip that should be normalized to match Savannah's plain footer style.

2. **Pasadena's footer address line omits the venue/church name.** Savannah's says "Harbert Hills Academy · [address]"; Pasadena's is just "[address]" with no "Pasadena SDA Church ·" (or similar) prefix, even though the hero image prominently names that church. Likely a content gap rather than a deliberate difference — flagging for the content owner rather than silently adding a name that isn't actually in the source.

3. **The Savannah-only "Friday, October 1" typo does not recur here.** Pasadena's equivalent option correctly reads "Friday, October 23". This confirms that typo is a one-off content mistake specific to the Savannah frame (see `../registration/code.md` §3b), not something baked into a shared component default — so it should be fixed only on the Savannah side, not "matched" here.

4. **Info-pills container width differs (424.93px → 520.93px) and the date-pill / info-pill boxes are a few px wider** — this is pure auto-layout reflow from the longer address string ("1280 E. Washington Blvd, Pasadena, CA, 91104" vs "45 Rural Lane, Savannah, TN 38372") and longer date-pill text ("October 21–24, 2026" vs "October 14–17, 2026"), not a deliberate design change. No action needed beyond letting the layout be fluid/auto-sizing in implementation, same as Savannah.

No other differences were found — section order, card radii (including the "Additional Information" card's odd-one-out `10px` radius, same as Savannah), the "ABOUT THIS EVENT" heading being navy while every other heading is gold, the `#666` session-option border, the `rgba(220,226,240,0.1)`/`rgba(255,255,255,0.1)` tints, and every spacing value in `../registration/code.md` §5–6 all carry over unchanged to this frame.

---

## 5. Notes

- `get_variable_defs` returned `{}` for this node — no Figma Variables bound here either, consistent with the Savannah pull.
- Same hero-image resolution caveat applies here as noted in `../registration/code.md` §8 (the shared hero source photo is lower-resolution than a true 2x export would want) — it's the identical image file, so the same recommendation (request a higher-res source before relying on this for a large hero banner) applies to this page too.
- `frame.png` here is a full, non-cropped 2x export (2880×10288), same as the Savannah `frame.png`.
