# Spotter.ai UI/UX Investigation

Date: 2026-04-16  
Target: [https://spotter.ai/](https://spotter.ai/)

## Scope and Method

- Investigated the live homepage UI using browser accessibility snapshots and rendered screenshots.
- Focused on visible structure, component patterns, interaction model, messaging hierarchy, and reuse-ready design primitives.
- This report reflects observed behavior on the current production page (desktop viewport).

## Quick Information Architecture (Observed)

Primary entry appears as a single-page marketing experience with section-based storytelling:

1. Top nav/header
2. Hero (value proposition + product visual)
3. Product capability grid (6 capability cards)
4. Results/statistics section
5. Closing CTA section
6. Trust/logo strip
7. Footer (legal + address)

Menu structure (hamburger) includes:

- home
- lens
- tms
- sentinel
- extension
- spotter app
- loan calculators
- insights

## Page-Level UX Pattern

- **Narrative flow:** problem/solution positioning -> capability modules -> proof metrics -> conversion CTA.
- **Conversion points:** repeated CTA pattern (`sign up`, `Unlock the Future of Freight`, `Request a quote`) supports both self-serve and sales-assisted intent.
- **Product discovery:** capability cards reduce cognitive load by separating products into named modules with short explanatory text.
- **Trust reinforcement:** quant metrics and logo marquee provide social proof before final CTA.

## Visual System (Observed Tokens and Style)

### Color Direction

- **Base background:** dark blue/teal gradient with a subtle grid motif in hero.
- **Primary accent:** aqua/teal used for highlight words and interactive emphasis.
- **Text hierarchy:** high-contrast white for primary headlines; muted gray-blue for secondary copy.
- **Support colors in UI art:** orange/red/yellow signals appear in product mockups for status/score meaning.

Approximate visual palette from rendered view:

- Dark blue: `#0F2736` to `#17384A` range
- Accent aqua/teal: `#64D3CC` to `#5BC6C2` range
- Primary text: near-white `#EAF2F5`
- Secondary text: desaturated blue-gray `#7F93A8`

### Typography

- Sans-serif family, geometric/modern feel.
- Heavy headline weights for H1/H2 with large scale.
- Consistent sentence-case supporting text, medium line-height.
- Accent color is used to selectively emphasize key words in major headings.

### Spacing and Layout

- Wide-section spacing with clear vertical breathing room.
- Card/group alignment based on centered container system.
- Rounded corners used across cards, buttons, and nav overlays.
- Grid-based hero backdrop reinforces "operations/precision" brand tone.

## Component Inventory (Reusable Design Components)

### 1) Header/Nav

- Brand logo at top-left.
- Hamburger icon (opens overlay menu).
- Top-right primary action button (`sign up`).
- Overlay menu panel with icon + text list items.

### 2) CTA Buttons

- Rounded pill-like style.
- Filled aqua/teal primary treatment.
- Used in hero and mid/late-page CTA moments.
- Labels suggest mixed intent capture (marketing + lead gen).

### 3) Hero Section

- Large H1 with partial accent coloring.
- Product UI mockup image centered under headline.
- Dark themed visual with technical/operations cues.

### 4) Capability Cards (6 cards)

Each card includes:

- Product name (e.g., Spotter Lens, Spotter CRM, Driver App, Spotter TMS, Sentinel, Load Board Extension)
- Short value proposition subtitle
- One-sentence description

Card style:

- Light card backgrounds (in contrast to dark hero)
- Rounded edges
- Minimal iconography/content blocks
- Uniform dimensions for scanability

### 5) Metrics/Proof Cards

- Numeric headline metric (e.g., `10K+`, `2.8M+`, `$50M+`, `96.7%`)
- Supporting label + micro-context trend text.
- Icon tile at top of each metric card.

### 6) Trust Strip / Logo Marquee

- Horizontally scrolling "trusted by" partner logos.
- Sits before footer to support credibility near conversion end state.

### 7) Footer

- Compact legal links (`Terms of service`, `CCPA`)
- Company address
- Copyright

## Content and Messaging UX

- **Headline tone:** direct and outcome-oriented ("Trucking Automation that works for you").
- **Microcopy style:** concise operational benefits, low jargon density despite AI positioning.
- **Value framing:** "automation + visibility + optimization + safety" repeated across modules.
- **Social proof strategy:** specific numbers rather than testimonials on the observed view.

## Interaction Patterns (Observed)

- Hamburger menu toggles expanded/collapsed state.
- Navigation appears to support section/product jumping.
- CTA buttons are always visible at major engagement points.
- No heavy form interaction was observed on-page in this pass (likely delegated to sign-up/quote flows).

## Accessibility and UX Risks (Initial)

- Link naming in some elements appears non-semantic in accessibility tree (logo links expose style text instead of clear label).
- Large decorative visuals may require stronger alt text strategy to preserve context for non-visual users.
- Contrast for some secondary text on light cards should be verified via automated contrast checks.
- Repeated CTA labels are strong for conversion but may benefit from clearer differentiation by user intent (trial vs contact sales).

## Design Component Typing for Future Work

Use this typed component model as a working baseline:

- `AppShell/Header`
- `HamburgerMenuOverlay`
- `PrimaryCTAButton`
- `SecondaryCTAButton`
- `HeroSection`
- `ProductCapabilityCard`
- `CapabilityGrid`
- `MetricStatCard`
- `StatsGrid`
- `TrustLogoMarquee`
- `FinalCTASection`
- `LegalFooter`

Recommended design-token groups:

- `color.background.*`
- `color.text.*`
- `color.brand.*`
- `spacing.section.*`
- `radius.card|button|overlay`
- `type.display|heading|body|caption`
- `shadow.card|floating`

## Suggested Next-Step Deliverables

For the upcoming task, this investigation is most useful when converted into:

1. A component map (Figma or code) matching the typed model above.
2. A token sheet with exact measured values (colors, spacing, typography scale).
3. A page blueprint with section-by-section reusable blocks.
4. A UX intent matrix mapping each CTA to user journey stage.

## Evidence Captured

Visual references were captured during investigation:

- Hero/top viewport with nav: `spotter-home-top-viewport.png`
- Menu-expanded interaction state: `spotter-home-menu-open.png`
- Full-page and section captures for structure confirmation

