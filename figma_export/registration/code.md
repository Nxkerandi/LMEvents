# Figma Design Context — Living Manna Registration Page (full page)

**Source:** https://www.figma.com/design/KT1MB0kyS04Sc5HKBxhGaz/Living-Manna-Registration-Page?node-id=4-7&m=dev
**File key:** KT1MB0kyS04Sc5HKBxhGaz
**Node:** 4:7 ("FInal Frame") — the top-level frame for the whole registration page, 1440×5144.

This file is the **source of truth for real event content** (not a placeholder/demo design like the earlier EAEvents pulls) — copy text below is transcribed verbatim from the design for seeding. One internal inconsistency was found in the source and is flagged inline (session-4 date typo) rather than silently corrected.

Treat all code below as REFERENCE ONLY (React/Tailwind) — adapt to this project's actual stack (Django/HTML/CSS, matching `LMEvents`' own templates/CSS conventions) before implementing.

---

## 1. Page structure overview

```
FInal Frame (1440 × 5144, bg #f9f7f3)
├─ Hero image (Rectangle 5, 1440×700, y=0) — flattened marketing-flyer graphic, see hero-bg.png
├─ Content column (x=170, y=780, w=1100) — 80px gap below hero
│  ├─ Cards stack (gap: 40px between cards)
│  │  ├─ ABOUT THIS EVENT (rounded-20, px-100 py-40)
│  │  ├─ SCHEDULE (rounded-20, px-50 py-40)
│  │  ├─ registration-deadline notice bar (rounded-10, pl-100 pr-30 py-25 — NOT a card, no white bg)
│  │  ├─ YOUR INFORMATION (rounded-20, px-50 py-40)
│  │  ├─ WHICH SESSIONS WILL YOU ATTEND? (rounded-20, px-100 py-45)
│  │  ├─ CHILDREN & YOUTH (rounded-20, px-100 py-45)
│  │  ├─ SABBATH MEAL (rounded-20, px-100 py-45)
│  │  └─ ADDITIONAL INFORMATION (rounded-10 ← different from the rest, px-100 py-45)
│  ├─ [35px gap] Submit button
│  ├─ [35px gap] Footer line 1 (contact)
│  └─ [35px gap] Footer line 2 (venue/address)
```

All cards (except the notice bar) share: `background: #ffffff`, `border: 0.5px solid #d8a52f`.

---

## 2. Reference code (from get_design_context)

```jsx
const assetPathPrefix = "https://www.figma.com/api/mcp/asset/b9112e37-c525-491e-8bdc-f127f5835283";
const imgRectangle5 = `${assetPathPrefix}/d4714.png`; // hero-bg.png in this folder
const imgLayer1 = `${assetPathPrefix}/d2214.svg`;      // icon-calendar.svg
const imgLayer2 = `${assetPathPrefix}/89403.svg`;      // icon-location.svg
const imgLayer3 = `${assetPathPrefix}/5853e.svg`;      // icon-admission.svg
const imgLayer4 = `${assetPathPrefix}/ecb47.svg`;      // icon-notice.svg

function Frame3({ className }) { // Submit button
  return (
    <div className={className || "bg-[#0b2242] content-stretch flex items-center justify-center px-[40px] py-[20px] relative rounded-[10px] w-[600px]"} data-node-id="18:335">
      <p className="[word-break:break-word] font-['Montserrat:Light'] font-light leading-[normal] relative shrink-0 text-[16px] text-white whitespace-nowrap" data-node-id="1:431">
        Submit
      </p>
    </div>
  );
}

function Frame469({ className }) { // "Yes" toggle pill
  return (
    <div className={className || "border border-[#0b2242] border-solid content-stretch flex items-center justify-center px-[20px] py-[15px] relative rounded-[10px] w-[350px]"} data-node-id="18:291" style={{ backgroundImage: "linear-gradient(90deg, rgb(251, 245, 237) 0%, rgb(251, 245, 237) 100%), linear-gradient(90deg, rgb(11, 34, 66) 0%, rgb(11, 34, 66) 100%)" }}>
      <p className="[word-break:break-word] font-['Montserrat:Regular'] font-normal leading-[32px] relative shrink-0 text-[#0b2242] text-[16px] tracking-[0.32px] whitespace-nowrap" data-node-id="4:190">
        Yes
      </p>
    </div>
  );
}

function Group1({ className }) { // "checked" checkbox indicator
  return (
    <div className={className || "relative size-[15px]"} data-node-id="8:221">
      <div className="absolute aspect-[10/10] bg-white border-[#0b2242] border-[0.5px] border-solid left-0 right-0 rounded-[2px] top-0" data-node-id="8:222" />
      <div className="absolute aspect-[10/10] bg-[#0b2242] left-[13.33%] right-[13.33%] rounded-[1px] top-[2px]" data-node-id="8:223" />
    </div>
  );
}

function CheckBox({ className }) { // unchecked checkbox
  return (
    <div className={className || "relative size-[15px]"} data-node-id="8:217" data-name="Check box">
      <div className="absolute bg-white border-[#0b2242] border-[0.5px] border-solid inset-0 rounded-[2px]" data-node-id="8:218" />
    </div>
  );
}

function Frame478({ className, text = "Evening Session : 6.00 PM - 9.00 PM", text2 = "Wednesday, October 14", withCheckBox = true }) { // session option
  return (
    <button className={className || "bg-white border-[#666] border-[0.75px] border-solid content-stretch cursor-pointer flex gap-[25px] items-center px-[20px] relative rounded-[10px] w-[706px]"} data-node-id="8:229">
      {withCheckBox && <CheckBox className="relative shrink-0 size-[15px]" />}
      <div className="[word-break:break-word] content-stretch flex flex-col items-start leading-[32px] px-[20px] py-[10px] relative shrink-0 text-[16px] text-left tracking-[0.32px] w-[646px]" data-node-id="8:225">
        <p className="font-['Montserrat:Medium'] font-medium relative shrink-0 text-[#0b2242] w-[225px]" data-node-id="8:215">{text2}</p>
        <p className="font-['Montserrat:Regular'] font-normal relative shrink-0 text-[#1c1c1c] w-[329px]" data-node-id="8:216">{text}</p>
      </div>
    </button>
  );
}

function Frame468({ className }) { // text input box (empty placeholder state)
  return <button className={className || "bg-[#fbf5ed] block border-[#d8a52f] border-[0.5px] border-solid cursor-pointer h-[65px] relative rounded-[6px] w-[450px]"} data-node-id="4:194" />;
}

export default function FInalFrame() {
  return (
    <div className="bg-[#f9f7f3] relative size-full" data-node-id="4:7" data-name="FInal Frame">
      {/* --- HERO: single flattened image, see hero-bg.png. Not reproduced here (out of scope for text/markup). --- */}
      <div className="-translate-x-1/2 absolute h-[700px] left-1/2 top-0 w-[1440px]" data-node-id="4:8">
        <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full" src={imgRectangle5} />
      </div>

      <div className="absolute content-stretch flex flex-col gap-[35px] items-center left-[170px] top-[780px] w-[1100px]" data-node-id="18:342">
        <div className="content-stretch flex flex-col gap-[40px] items-start relative shrink-0 w-full" data-node-id="18:334">

          {/* ABOUT THIS EVENT */}
          <div className="bg-white border-[#d8a52f] border-[0.5px] border-solid content-stretch flex flex-col gap-[35px] items-start px-[100px] py-[40px] relative rounded-[20px] shrink-0 w-full" data-node-id="4:57">
            <p className="font-['Montserrat:Bold'] font-bold leading-[32px] text-[#0b2242] text-[18px] tracking-[0.36px] w-[416px]" data-node-id="4:55">ABOUT THIS EVENT</p>
            <p className="font-['Montserrat:Regular'] font-normal leading-[32px] text-[#1c1c1c] text-[16px] tracking-[0.32px] w-[799px]" data-node-id="4:53">{`Join us for four days of meetings designed to prepare our hearts and homes for what lies ahead. Together we'll consider what it means to build a home that honors God now, in view of the eternal home He is preparing for us.`}</p>
            <div className="bg-[#fbf5ed] border-[#c98a2b] border-l-5 border-solid content-stretch flex flex-col gap-[30px] items-start pl-[50px] pr-[30px] py-[25px] relative shrink-0 w-[800px]" data-node-id="4:44">
              <p className="font-['Montserrat:Italic'] font-normal italic leading-[32px] text-[#1c1c1c] text-[16px] tracking-[0.32px] w-[715px]" data-node-id="4:48">{`"The well-being of society, the success of the church, and the prosperity of the nation truly depend upon home influences."`}</p>
              <p className="font-['Montserrat:SemiBold'] font-semibold leading-[32px] text-[#0b2242] text-[16px] tracking-[0.32px] w-[416px]" data-node-id="4:46">ELLEN G. WHITE, THE ADVENTIST HOME, p. 15.1</p>
            </div>
            <p className="font-['Montserrat:SemiBold'] font-semibold leading-[32px] text-[#0b2242] text-[18px] tracking-[0.36px] w-[416px]" data-node-id="4:60">SPEAKERS</p>
            <div className="content-stretch flex gap-[35px] items-center relative shrink-0" data-node-id="4:65">
              <div className="bg-[#fbf5ed] border-[#c98a2b] border-[0.5px] border-solid content-stretch flex items-center justify-center px-[40px] py-[15px] relative rounded-[10px] shrink-0" data-node-id="4:61">
                <p className="font-['Montserrat:Medium'] font-medium leading-[normal] text-[#0b2242] text-[16px] whitespace-nowrap" data-node-id="4:62">{`Devaney & Fazlyn Haupt`}</p>
              </div>
              <div className="bg-[#fbf5ed] border-[#c98a2b] border-[0.5px] border-solid content-stretch flex items-center justify-center px-[40px] py-[15px] relative rounded-[10px] shrink-0" data-node-id="4:63">
                <p className="font-['Montserrat:Medium'] font-medium leading-[normal] text-[#0b2242] text-[16px] whitespace-nowrap" data-node-id="4:64">{`Elvin & Marcia Bridges`}</p>
              </div>
            </div>
            <div className="content-stretch flex flex-col gap-[20px] items-start justify-center relative shrink-0" data-node-id="4:93">
              <div className="bg-[rgba(220,226,240,0.1)] border border-[#0b2242] border-solid content-stretch flex gap-[20px] items-center justify-center px-[40px] py-[15px] relative rounded-[40px] shrink-0" data-node-id="4:67">
                <img alt="" className="h-[30px] w-[31.588px]" src={imgLayer1} />
                <p className="font-['Montserrat:SemiBold'] font-semibold leading-[normal] text-[#0b2242] text-[16px] tracking-[0.48px] whitespace-nowrap" data-node-id="4:87">October 14–17, 2026</p>
              </div>
              <div className="bg-[rgba(220,226,240,0.1)] border border-[#0b2242] border-solid content-stretch flex gap-[20px] items-center justify-center px-[40px] py-[15px] relative rounded-[40px] shrink-0" data-node-id="4:88">
                <img alt="" className="h-[30px] w-[21.929px]" src={imgLayer2} />
                <p className="font-['Montserrat:SemiBold'] font-semibold leading-[normal] text-[#0b2242] text-[16px] tracking-[0.48px] whitespace-nowrap" data-node-id="4:92">45 Rural Lane, Savannah, TN 38372</p>
              </div>
              <div className="bg-[rgba(220,226,240,0.1)] border border-[#0b2242] border-solid content-stretch flex gap-[20px] items-center justify-center px-[40px] py-[15px] relative rounded-[40px] shrink-0" data-node-id="4:115">
                <img alt="" className="h-[30px] w-[50px]" src={imgLayer3} />
                <p className="font-['Montserrat:SemiBold'] font-semibold leading-[normal] text-[#0b2242] text-[16px] tracking-[0.48px] whitespace-nowrap" data-node-id="4:119">Free Admission</p>
              </div>
            </div>
          </div>

          {/* SCHEDULE */}
          <div className="bg-white border-[#d8a52f] border-[0.5px] border-solid content-stretch flex flex-col gap-[20px] items-start px-[50px] py-[40px] relative rounded-[20px] shrink-0 w-full" data-node-id="4:157">
            <p className="font-['Montserrat:Bold'] font-bold leading-[32px] text-[#c98a2b] text-[18px] tracking-[0.36px] whitespace-nowrap" data-node-id="4:176">SCHEDULE</p>
            <div className="border-[#c98a2b] border-b border-solid content-stretch flex font-['Montserrat:Medium'] font-medium gap-[301px] items-center leading-[32px] pb-[10px] relative shrink-0 text-[#1c1c1c] text-[18px] tracking-[0.36px] w-[1000px] whitespace-nowrap" data-node-id="4:175">
              <p data-node-id="4:173">DATE</p>
              <p data-node-id="4:172">SESSION</p>
              <p data-node-id="4:174">TIME</p>
            </div>
            {/* 4 rows, each: navy pill date badge (white text) | session title | time */}
            <div className="border-[#d8a52f] border-b-[0.75px] border-solid content-stretch flex gap-[57px] items-center pb-[10px] relative shrink-0 w-full" data-node-id="4:149">
              <div className="bg-[#0b2242] content-stretch flex items-center justify-center px-[40px] py-[10px] relative rounded-[40px] shrink-0" data-node-id="4:124">
                <p className="font-['Montserrat:SemiBold'] font-semibold leading-[normal] text-[16px] text-white tracking-[0.48px] whitespace-nowrap" data-node-id="4:144">Wed, Oct 14</p>
              </div>
              <p className="font-['Montserrat:Regular'] font-normal leading-[32px] text-[#1c1c1c] text-[16px] tracking-[0.32px] whitespace-nowrap" data-node-id="4:145">Preparing The Home For Home – Evening Session</p>
              <p className="font-['Montserrat:Regular'] font-normal leading-[32px] text-[#1c1c1c] text-[16px] tracking-[0.32px] whitespace-nowrap" data-node-id="4:146">6.00 PM - 9.00 PM</p>
            </div>
            <div className="border-[#d8a52f] border-b-[0.75px] border-solid content-stretch flex gap-[57px] items-center pb-[10px] relative shrink-0 w-full" data-node-id="4:158">
              <div className="bg-[#0b2242] ... rounded-[40px] shrink-0 w-[183px]" data-node-id="4:159"><p data-node-id="4:160">Thu, Oct 15</p></div>
              <p data-node-id="4:162">Preparing The Home For Home – Evening Session</p>
              <p data-node-id="4:164">6.00 PM - 9.00 PM</p>
            </div>
            <div className="border-[#d8a52f] border-b-[0.75px] border-solid content-stretch flex gap-[57px] items-center pb-[10px] relative shrink-0 w-full" data-node-id="4:165">
              <div className="bg-[#0b2242] ... rounded-[40px] shrink-0 w-[183px]" data-node-id="4:166"><p data-node-id="4:167">Fri, Oct 16</p></div>
              <p data-node-id="4:169">Preparing The Home For Home – Evening Session</p>
              <p data-node-id="4:171">6.00 PM - 9.00 PM</p>
            </div>
            <div className="content-stretch flex gap-[57px] items-center pb-[10px] relative shrink-0 w-full" data-node-id="4:150">
              <div className="bg-[#0b2242] ... rounded-[40px] shrink-0 w-[183px]" data-node-id="4:151"><p data-node-id="4:152">Sat, Oct 17</p></div>
              <p data-node-id="4:154">Preparing The Home For Home – All-Day Program</p>
              <p data-node-id="4:156">9.00 AM - 6.00 PM</p>
            </div>
          </div>

          {/* Registration-deadline notice bar (not a white card) */}
          <div className="bg-[rgba(255,255,255,0.1)] border border-[#d8a52f] border-solid content-stretch flex gap-[30px] items-start pl-[100px] pr-[30px] py-[25px] relative rounded-[10px] shrink-0 w-full" data-node-id="4:177">
            <img alt="" className="h-[32px] w-[31.998px]" src={imgLayer4} />
            <p className="font-['Montserrat:Italic'] font-normal italic leading-[0] text-[#0b2242] text-[16px] tracking-[0.32px] w-[715px]" data-node-id="4:179">
              <span className="font-['Montserrat:Regular'] leading-[32px]">Please register by</span>
              <span className="font-['Montserrat:SemiBold'] font-semibold leading-[32px]">{` `}</span>
              <span className="font-['Montserrat:SemiBold'] font-semibold leading-[32px]">Sunday, September 27, 2026</span>
              <span className="font-['Montserrat:SemiBold'] font-semibold leading-[32px]">.</span>
              <span className="font-['Montserrat:Regular'] leading-[32px]">{` This event is free to attend.`}</span>
            </p>
          </div>

          {/* YOUR INFORMATION */}
          <div className="bg-white border-[#d8a52f] border-[0.5px] border-solid content-stretch flex flex-col gap-[30px] items-start justify-center px-[50px] py-[40px] relative rounded-[20px] shrink-0 w-full" data-node-id="4:213">
            <p className="font-['Montserrat:Bold'] font-bold leading-[32px] text-[#c98a2b] text-[18px] tracking-[0.36px] whitespace-nowrap" data-node-id="4:214">YOUR INFORMATION</p>
            <div className="content-stretch flex gap-[45px] items-center relative shrink-0 w-[945px]" data-node-id="4:211">
              <div className="content-stretch flex flex-col gap-[20px] items-start relative shrink-0 w-[450px]" data-node-id="4:201">
                <p className="font-['Montserrat:Regular'] font-normal leading-[0] text-[#1c1c1c] text-[16px] tracking-[0.32px] w-full" data-node-id="4:200">
                  <span className="font-['Montserrat:Medium'] font-medium leading-[32px] text-[#0b2242]">First Name</span>
                  <span className="leading-[32px]">{`  `}</span>
                  <span className="font-['Montserrat:SemiBold'] font-semibold leading-[32px] text-[#c98a2b]">*</span>
                </p>
                <Frame468 className="bg-[#fbf5ed] border-[#d8a52f] border-[0.5px] border-solid ... h-[65px] rounded-[6px] w-full" />
              </div>
              <div className="content-stretch flex flex-col gap-[20px] items-start relative shrink-0 w-[450px]" data-node-id="4:202">
                <p data-node-id="4:203"><span className="text-[#0b2242]">{`Last Name `}</span> <span className="text-[#c98a2b]">*</span></p>
                <Frame468 className="... w-full" />
              </div>
            </div>
            <div className="content-stretch flex gap-[45px] items-center relative shrink-0 w-[945px]" data-node-id="4:212">
              <div className="... w-[450px]" data-node-id="4:205">
                <p data-node-id="4:206"><span className="text-[#0b2242]">Phone Number</span> <span className="text-[#c98a2b]">*</span></p>
                <Frame468 className="... w-full" />
              </div>
              <div className="... w-[450px]" data-node-id="4:208">
                <p data-node-id="4:209"><span className="text-[#0b2242]">{`Email Address  `}</span><span className="text-[#c98a2b]">*</span></p>
                <Frame468 className="... w-full" />
              </div>
            </div>
            <div className="content-stretch flex flex-col gap-[20px] items-start relative shrink-0 w-[945px]" data-node-id="18:287">
              <p data-node-id="18:288"><span className="text-[#0b2242]">{`Total People Attending, Including Yourself `}</span> <span className="text-[#c98a2b]">*</span></p>
              <Frame468 className="... w-full" />
              <p className="font-['Montserrat:Italic'] font-normal italic leading-[32px] text-[#0b2242] text-[16px] tracking-[0.32px] w-full" data-node-id="18:290">Count everyone in your group — yourself, your spouse, and any children or youth.</p>
            </div>
          </div>

          {/* WHICH SESSIONS WILL YOU ATTEND? */}
          <div className="bg-white border-[#d8a52f] border-[0.5px] border-solid content-stretch flex flex-col gap-[35px] items-start justify-center px-[100px] py-[45px] relative rounded-[20px] shrink-0 w-full" data-node-id="8:286">
            <p className="font-['Montserrat:Bold'] font-bold leading-[32px] text-[#c98a2b] text-[18px] tracking-[0.36px] w-full" data-node-id="8:285">WHICH SESSIONS WILL YOU ATTEND? *</p>
            <div className="content-stretch cursor-pointer flex flex-col gap-[20px] items-start relative shrink-0 w-full" data-node-id="8:284">
              <Frame478 text2="Wednesday, October 14" text="Evening Session : 6.00 PM - 9.00 PM" />
              <Frame478 text2="Thursday, October 15" text="Evening Session : 6.00 PM - 9.00 PM" />
              <Frame478 text2="Friday, October 1" text="Evening Session : 6.00 PM - 9.00 PM" />
              {/* ^ NOTE: source literally says "Friday, October 1" — almost certainly a typo for "Friday, October 16"
                   (the SCHEDULE table above correctly lists "Fri, Oct 16" for this same session). Flagging, not
                   silently correcting — confirm with the content owner (Marcia Bridges) before seeding. */}
              <Frame478 text2="Saturday, October 17" text="All-Day Program : 9.00 AM - 6.00 PM" />
            </div>
          </div>

          {/* CHILDREN & YOUTH */}
          <div className="bg-white border-[#d8a52f] border-[0.5px] border-solid content-stretch flex flex-col gap-[30px] items-start justify-center px-[100px] py-[45px] relative rounded-[20px] shrink-0 w-full" data-node-id="18:304">
            <p className="font-['Montserrat:Bold'] font-bold leading-[32px] text-[#c98a2b] text-[18px] tracking-[0.36px] whitespace-nowrap" data-node-id="18:305">{`CHILDREN & YOUTH`}</p>
            <p className="font-['Montserrat:Regular'] font-normal leading-[32px] text-[#1c1c1c] text-[16px] tracking-[0.32px] w-[796px]" data-node-id="18:300">Cradle Roll and Youth Sabbath School classes, plus afternoon classes, are available. Outside of class time, we respectfully ask that parents keep their children with them at all times.</p>
            <div className="content-stretch flex flex-col gap-[25px] items-start relative shrink-0 w-[820px]" data-node-id="18:303">
              <p className="font-['Montserrat:SemiBold'] font-semibold leading-[0] text-[#0b2242] text-[16px] tracking-[0.32px] w-full" data-node-id="18:301">
                <span className="leading-[32px]">{`Will children or youth be attending with you? `}</span>
                <span className="leading-[32px] text-[#c98a2b]">*</span>
              </p>
              <div className="content-stretch flex gap-[120px] items-center relative shrink-0 w-full" data-node-id="18:302">
                <Frame469 /> {/* "Yes" */}
                <div className="border border-[#0b2242] border-solid ... w-[350px]" style={{ backgroundImage: "linear-gradient(90deg, rgb(251, 245, 237) 0%, rgb(251, 245, 237) 100%), linear-gradient(90deg, rgb(11, 34, 66) 0%, rgb(11, 34, 66) 100%)" }} data-node-id="18:298">
                  <p className="font-['Montserrat:Regular'] font-normal leading-[32px] text-[#0b2242] text-[16px] tracking-[0.32px] whitespace-nowrap">No</p>
                </div>
              </div>
            </div>
          </div>

          {/* SABBATH MEAL */}
          <div className="bg-white border-[#d8a52f] border-[0.5px] border-solid content-stretch flex flex-col gap-[30px] items-start justify-center px-[100px] py-[45px] relative rounded-[20px] shrink-0 w-full" data-node-id="18:306">
            <p className="font-['Montserrat:Bold'] font-bold leading-[32px] text-[#c98a2b] text-[18px] tracking-[0.36px] whitespace-nowrap" data-node-id="18:307">SABBATH MEAL</p>
            <p className="font-['Montserrat:Regular'] font-normal leading-[32px] text-[#1c1c1c] text-[16px] tracking-[0.32px] whitespace-nowrap" data-node-id="18:308">Meals will be provided for all visitors on Sabbath, October 17, only.</p>
            <div className="content-stretch flex flex-col gap-[25px] items-start relative shrink-0 w-[820px]" data-node-id="18:309">
              <p className="font-['Montserrat:SemiBold'] font-semibold leading-[0] text-[#0b2242] text-[16px] tracking-[0.32px] w-full" data-node-id="18:310">
                <span className="leading-[32px]">{`Will you be joining us for the Sabbath meal? `}</span>
                <span className="leading-[32px] text-[#c98a2b]">*</span>
              </p>
              <div className="content-stretch flex gap-[120px] items-center relative shrink-0 w-full" data-node-id="18:311">
                <Frame469 /> {/* "Yes" */}
                <div /* "No", same styling as above */ data-node-id="18:313" />
              </div>
            </div>
          </div>

          {/* ADDITIONAL INFORMATION — note rounded-[10px], not [20px] like the other cards */}
          <div className="bg-white border-[#d8a52f] border-[0.5px] border-solid content-stretch flex flex-col gap-[20px] items-start justify-center px-[100px] py-[45px] relative rounded-[10px] shrink-0 w-full" data-node-id="18:326">
            <p className="font-['Montserrat:Bold'] font-bold leading-[32px] text-[#c98a2b] text-[18px] tracking-[0.36px] whitespace-nowrap" data-node-id="18:330">ADDITIONAL INFORMATION</p>
            <p className="font-['Montserrat:SemiBold'] font-semibold leading-[32px] text-[#0b2242] text-[16px] tracking-[0.32px] whitespace-nowrap" data-node-id="18:327">What city do you currently live in? (Optional)</p>
            <div className="bg-[#fbf5ed] border border-[#d8a52f] border-solid content-stretch flex h-[93px] items-start px-[40px] py-[30px] relative rounded-[10px] shrink-0 w-[853px]" data-node-id="18:333">
              <p className="font-['Montserrat:Light_Italic'] font-light italic leading-[32px] text-[16px] text-black tracking-[0.32px] whitespace-nowrap" data-node-id="18:332">Short answer</p>
            </div>
          </div>

        </div>

        {/* Submit button */}
        <Frame3 />

        {/* Footer line 1 */}
        <p className="font-['Montserrat:Regular'] font-normal leading-[0] text-[#1c1c1c] text-[16px] text-center tracking-[0.32px] w-[477px]" data-node-id="18:343">
          <span className="font-['Montserrat:Medium'] font-medium leading-[32px] text-[#0b2242]">Questions about registration?</span>
          <span className="leading-[32px]"><br aria-hidden />Contact Marcia Bridges ·</span>
          <span className="font-['Montserrat:Medium'] font-medium leading-[32px] text-[#0b2242]">{` `}</span>
          <a className="font-['Montserrat:Medium'] font-medium leading-[32px] text-[#0b2242] underline" href="mailto:livingmanna@yahoo.com" target="_blank">livingmanna@yahoo.com</a>
        </p>

        {/* Footer line 2 */}
        <p className="font-['Montserrat:Regular'] font-normal leading-[32px] text-[#1c1c1c] text-[16px] text-center tracking-[0.32px] w-[542px]" data-node-id="18:512">
          Harbert Hills Academy · 45 Rural Lane, Savannah, TN 38372
        </p>
      </div>
    </div>
  );
}
```

---

## 3. Verbatim copy content (source of truth for seeding)

### 3a. Hero image (baked into `hero-bg.png` as pixels — NOT live/editable text; transcribed here only because its content is real event info worth having on record for `<title>`/meta/alt-text purposes)

> **⚠️ Important:** this hero graphic is a shared marketing flyer that promotes **two separate events**. Only the left-hand one (Harbert Hills Academy, Oct 14–17) is what this registration page/form is actually for — confirmed by the live-text schedule, address, and footer all matching that event only. The Pasadena SDA Church listing is a different event at a different venue/date/speaker-pairing and should **not** be pulled into this event's seed data — it's just along for the ride on the shared graphic.

- Big title: "PREPARING THE HOME FOR **HOME**" ("HOME" on its own line, large gold text; "PREPARING THE" navy)
- Left speaker: "Brother DEVANEY HAUPT" — "Messengers of Present Truth Ministries"
- Right speaker: "Elder ELVIN BRIDGES" — "Living Manna Ministries"
- Center emblem: "LIVING MANNA MINISTRIES" circular logo + globe icon, caption "Messengers of Present Truth Ministries"
- Left location badge: "Harbert Hills Academy" / "October 14–17, 2026" / "Savannah, Tennessee" — **this event**
- Right location badge: "Pasadena SDA Church" / "October 21–24, 2026" / "Pasadena, California" — **a different event, out of scope**
- Bottom bar: "livingmannaministries.org  |  livingmanna@yahoo.com"

### 3b. Live page copy (verbatim, in page order)

**About This Event**
- Heading: `ABOUT THIS EVENT`
- Body: `Join us for four days of meetings designed to prepare our hearts and homes for what lies ahead. Together we'll consider what it means to build a home that honors God now, in view of the eternal home He is preparing for us.`
- Quote: `"The well-being of society, the success of the church, and the prosperity of the nation truly depend upon home influences."`
- Attribution: `ELLEN G. WHITE, THE ADVENTIST HOME, p. 15.1`
- Subheading: `SPEAKERS`
- Speaker pill 1: `Devaney & Fazlyn Haupt`
- Speaker pill 2: `Elvin & Marcia Bridges`
- Info pill 1 (calendar icon): `October 14–17, 2026` (en dash)
- Info pill 2 (location icon): `45 Rural Lane, Savannah, TN 38372`
- Info pill 3 (ticket icon): `Free Admission`

**Schedule**
- Heading: `SCHEDULE`
- Column headers: `DATE`, `SESSION`, `TIME`
- Row 1: `Wed, Oct 14` — `Preparing The Home For Home – Evening Session` — `6.00 PM - 9.00 PM` (en dash before "Evening")
- Row 2: `Thu, Oct 15` — `Preparing The Home For Home – Evening Session` — `6.00 PM - 9.00 PM`
- Row 3: `Fri, Oct 16` — `Preparing The Home For Home – Evening Session` — `6.00 PM - 9.00 PM`
- Row 4: `Sat, Oct 17` — `Preparing The Home For Home – All-Day Program` — `9.00 AM - 6.00 PM`

**Registration notice** (own bordered bar, not a card)
- `Please register by Sunday, September 27, 2026. This event is free to attend.` ("Sunday, September 27, 2026." rendered SemiBold/emphasized, rest Regular)

**Your Information** (form section)
- Heading: `YOUR INFORMATION`
- Field: `First Name *`
- Field: `Last Name *`
- Field: `Phone Number *`
- Field: `Email Address *`
- Field: `Total People Attending, Including Yourself *`
  - Helper text: `Count everyone in your group — yourself, your spouse, and any children or youth.` (em dash)

**Which Sessions Will You Attend?** (form section)
- Heading: `WHICH SESSIONS WILL YOU ATTEND? *` (asterisk is part of the same gold heading text here, unlike the field labels above where only the `*` itself is gold)
- Option 1: `Wednesday, October 14` / `Evening Session : 6.00 PM - 9.00 PM`
- Option 2: `Thursday, October 15` / `Evening Session : 6.00 PM - 9.00 PM`
- Option 3: `Friday, October 1` / `Evening Session : 6.00 PM - 9.00 PM` — **⚠️ likely typo in source** (schedule table says "Fri, Oct 16"; this option label is missing the trailing "6"). Transcribed verbatim; flag for confirmation before seeding rather than auto-correcting.
- Option 4: `Saturday, October 17` / `All-Day Program : 9.00 AM - 6.00 PM`

**Children & Youth** (form section)
- Heading: `CHILDREN & YOUTH`
- Body: `Cradle Roll and Youth Sabbath School classes, plus afternoon classes, are available. Outside of class time, we respectfully ask that parents keep their children with them at all times.`
- Question: `Will children or youth be attending with you? *`
- Options: `Yes` / `No`

**Sabbath Meal** (form section)
- Heading: `SABBATH MEAL`
- Body: `Meals will be provided for all visitors on Sabbath, October 17, only.`
- Question: `Will you be joining us for the Sabbath meal? *`
- Options: `Yes` / `No`

**Additional Information** (form section)
- Heading: `ADDITIONAL INFORMATION`
- Question: `What city do you currently live in? (Optional)`
- Placeholder: `Short answer`

**Submit button**
- `Submit`

**Footer**
- Line 1: `Questions about registration?` (line break) `Contact Marcia Bridges · ` + link text `livingmanna@yahoo.com` (mailto:livingmanna@yahoo.com)
- Line 2: `Harbert Hills Academy · 45 Rural Lane, Savannah, TN 38372`

---

## 4. Typography

**Single font family throughout: Montserrat.** Unlike the earlier EAEvents design (Poppins body + "Eleven Eleven" display font), **this design does not use a separate display/heading typeface** — headings are distinguished purely by weight/size/color (Bold/SemiBold, 18px, navy-or-gold) rather than a different font family. Worth confirming this is intentional with the design owner if a more distinct heading treatment was expected, but as pulled, it's Montserrat end-to-end.

Weights used: Light, Light Italic, Regular, Italic, Medium, SemiBold, Bold.

| Role | Weight | Size | Line height | Letter spacing | Color |
|---|---|---|---|---|---|
| Card heading, "ABOUT THIS EVENT" only | Bold | 18px | 32px | 0.36px | `#0b2242` (navy — the odd one out, see note below) |
| Card heading, all other sections | Bold | 18px | 32px | 0.36px | `#c98a2b` (gold) |
| Body paragraph | Regular | 16px | 32px | 0.32px | `#1c1c1c` |
| Italic quote | Italic | 16px | 32px | 0.32px | `#1c1c1c` |
| Quote attribution | SemiBold | 16px | 32px | 0.32px | `#0b2242` |
| Speaker pill text | Medium | 16px | normal | none | `#0b2242` |
| Info pill text (date/location/admission) | SemiBold | 16px | normal | 0.48px | `#0b2242` |
| Schedule table header | Medium | 18px | 32px | 0.36px | `#1c1c1c` |
| Schedule date pill (white on navy) | SemiBold | 16px | normal | 0.48px | `#ffffff` |
| Schedule session/time cell | Regular | 16px | 32px | 0.32px | `#1c1c1c` |
| Notice bar text | Regular / SemiBold (mixed inline) | 16px | 32px | 0.32px | `#0b2242`, italic |
| Field label | Medium | 16px | 32px | 0.32px | `#0b2242` |
| Field label asterisk | SemiBold | 16px | 32px | 0.32px | `#c98a2b` |
| Field helper/italic text | Italic | 16px | 32px | 0.32px | `#0b2242` |
| Session-option date line | Medium | 16px | (block) | 0.32px (inherited) | `#0b2242` |
| Session-option description line | Regular | 16px | (block) | 0.32px (inherited) | `#1c1c1c` |
| Toggle pill (Yes/No) text | Regular | 16px | 32px | 0.32px | `#0b2242` |
| Textarea placeholder ("Short answer") | Light Italic | 16px | 32px | 0.32px | `#000000` (pure black — the only place true black is used instead of `#1c1c1c` or `#0b2242`) |
| Submit button text | Light | 16px | normal | none | `#ffffff` |
| Footer line 1 (plain parts) | Regular | 16px | 32px | 0.32px | `#1c1c1c` |
| Footer line 1 (emphasized parts + link) | Medium | 16px | 32px | 0.32px | `#0b2242` |
| Footer line 2 | Regular | 16px | 32px | 0.32px | `#1c1c1c` |

**Note on heading color inconsistency:** every section heading is gold (`#c98a2b`) *except* "ABOUT THIS EVENT", which is navy (`#0b2242`). This is exactly as authored in the file (verified directly in the returned code, not a transcription slip) — flagging it since it's easy to "normalize away" by mistake when implementing, but it's a deliberate-looking distinction (first/intro section vs. all the rest) that should probably be preserved rather than treated as an error, unlike the schedule-date typo above which does look like an actual mistake.

---

## 5. Color palette (hex)

| Token (suggested name) | Hex / value | Usage |
|---|---|---|
| `--navy` | `#0b2242` | Primary text/heading/border/button color (note: close to but distinct from EAEvents' `#0a2342`) |
| `--gold` | `#c98a2b` | Section headings (except "About"), quote left-border, notice-bar accents |
| `--gold-border` | `#d8a52f` | Card borders, input borders, speaker-pill borders (a second, slightly lighter/warmer gold — distinct token from `--gold` above; don't collapse the two) |
| `--text` | `#1c1c1c` | Body copy (near-black, not navy) |
| `--bg` | `#f9f7f3` | Page background |
| `--input-bg` | `#fbf5ed` | Input/textarea/speaker-pill fill (cream) |
| `--white` | `#ffffff` | Card backgrounds, schedule date-pill text, submit-button text |
| `--black` | `#000000` | Textarea placeholder text only |
| `--session-border` | `#666666` | Session-option button border |
| — | `rgba(220,226,240,0.1)` | Info-pill background (very faint blue-grey tint) |
| — | `rgba(255,255,255,0.1)` | Registration-notice-bar background (faint white tint) |

---

## 6. Spacing / layout summary

- Page: 1440px wide, `#f9f7f3` background.
- Hero: 700px tall, full width, y=0 (see §7 — out of scope to re-describe beyond size).
- Content column: 1100px wide, centered (170px side margins), starts 80px below the hero (y=780).
- Cards stack: vertical `gap: 40px` between each of the 8 sections.
- Below the cards stack: `gap: 35px` between [cards stack] → [Submit button] → [footer line 1] → [footer line 2].
- Card padding: mostly `100px`/`50px` horizontal × `40px`–`45px` vertical (varies slightly per card — see the reference code above for each card's exact `px-`/`py-` values; not fully uniform).
- Card corner radius: `20px` for every card except "Additional Information", which is `10px`.
- Notice bar corner radius: `10px`.
- Text input height: `65px`, radius `6px`.
- Textarea height: `93px`, radius `10px`.
- Session-option button: `706px` wide, radius `10px`.
- Yes/No toggle pills: `350px` wide each, `120px` gap between them, radius `10px`.
- Submit button: `600px` wide, radius `10px`, centered.

---

## 7. Hero image — out of scope, noted only for placement

Per instructions, the hero background image itself is not re-described in detail here beyond what's needed to place the content column: it's a single flattened 1440×700 graphic (see `hero-bg.png`), and the content column begins 80px below it. See §3a above for a transcription of its baked-in text (kept only because it's real content, e.g. useful for `<title>`/alt-text) — but the visual design/treatment of the hero itself was intentionally not analyzed further here.

---

## 8. Notes

- `get_variable_defs` returned `{}` — no Figma Variables (design tokens) are bound anywhere in this frame.
- Assets: see the file listing in the final response for what was exported/downloaded and why (flattened PNG vs. real SVG file) for each.
- `frame.png` (full-page 2x export) is 2880×10288 — an exact 2x of the 1440×5144 frame (unlike some previous single-text-node pulls, a full frame export isn't ink-cropped).
- **Resolution risk on the hero image:** the underlying uploaded source photo for the hero (`hero-bg-source-raw-highres.jpg`) is only 1964×801px. At the design's native 1440×700 box this comfortably covers at 1x (no upscaling), but the requested 2x export (2880×1400) needs the source's height scaled up ~1.75× (801→1400) beyond its native resolution to fill the box — i.e. `hero-bg.png`, despite being a "2x export," is itself a mild upscale of a sub-2x-resolution source and may look soft when displayed large, similar to the blur issue found and fixed on the EAEvents hero banner previously. Recommend requesting a higher-resolution source flyer graphic from the design/content owner before relying on this for a large hero banner, rather than assuming `hero-bg.png` is genuinely crisp at 2x.
