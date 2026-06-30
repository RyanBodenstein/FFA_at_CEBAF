# Back-of-the-Envelope Degradation Estimates (INFORMAL, NOT FOR PUBLICATION)

Date: 2026-05-15
Status: Curiosity calculation only. Not verified, not peer-reviewed, not for any report or talk.

---

## Campaign 1 Context

- ~12 months deployed, ~6 months beam-on (Mar-Sep 2025)
- 2.12 GeV/pass, up to 5.5 passes (max ~11.7 GeV)
- Hall D dominant (~300 nA at 12 GeV); Halls A/B/C lower currents
- Y-plates positioned ~1-2 feet from beamline on girders and arc pipe supports

## Doses at Arc Locations (where FFA magnets would go)

- Gamma: 10 - 1,700 Gy (5 orders of magnitude range across all locations)
- Neutron: 8 - 30 rem (arcs); linac NDX plates saw 40,000 - 156,000 rem
- Dose rates in arcs: ~0.002 - 0.4 Gy/hr gamma over ~4,400 beam-on hours

## Observed Degradation by Arc Line (NdFeB-SmCo differential)

| Arc Line | Pass | Mean Gamma (Gy) | Mean Degradation (%) |
|----------|------|-----------------|---------------------|
| Line 1 (top) | 1st, lowest energy | 30 | -0.431 |
| Line 2 | 2nd | 320 | -0.258 |
| Line 3 | 3rd | 650 | -0.176 |
| Line 4 | 4th | 1,120 | -0.133 |
| Line 5 (bottom) | 5th, highest energy | 670 | -0.142 |

Worst individual plate: Y-39 (NE Arc, Line 1) at -0.744%.

Key observation: degradation is INVERTED relative to ambient gamma dose. Line 1
gets the least gamma but the most damage. Likely explanation: lowest-rigidity pass
has tightest aperture, most localized beam loss, and the rod dosimeters measure
ambient field rather than the local hadronic showers doing the damage.

## Rough Linear Extrapolation (assuming ~6 months beam/year)

| Location | Rate (%/yr) | Time to 1% | Time to 5% |
|----------|-------------|-----------|-----------|
| Arc Line 1 mean | ~0.43 | ~2.3 yr | ~12 yr |
| Arc overall mean | ~0.23 | ~4.3 yr | ~22 yr |
| Arc Line 4 mean | ~0.13 | ~7.7 yr | ~38 yr |
| Y-39 (worst plate) | ~0.74 | ~1.4 yr | ~6.8 yr |
| Y-11 (best arc plate) | ~0.02 | ~50 yr | ~250 yr |

## Material Dependence

- N42EH (has 1-2% Dy): ~0.25%/campaign, reaches 1% in ~4 yr
- N52SH (Dy-free): ~0.17%/campaign, reaches 1% in ~6 yr (roughly 50% slower)
- SmCo: zero measurable degradation despite highest neutron capture rate

Dy-free NdFeB buys you ~50% more lifetime. SmCo is effectively indefinite
but costs remanence (11.2-12.0 vs 14.2-14.5 kGs) and is brittle.

## Halbach Field Quality (the real concern)

Uniform degradation is compensable. Wedge-to-wedge variation is not.
Our 20 arc plates show a spread of -0.019% to -0.744% (range: 0.73 pp).
RMS scatter: ~0.17% after one campaign. If this grows linearly:
- After 5 yr: ~1% RMS wedge variation
- After 10 yr: ~2% RMS wedge variation
1% RMS starts eating into dynamic aperture budgets for high-performance rings.

## Critical Point: Our Measurements Are a Lower Bound

Our Y-plates were ~1-2 feet from the beamline. FFA Halbach magnets would be
wrapped around the beam pipe (bore surface at the beam aperture). This matters:

1. Radiation falls off steeply with distance; dose at bore surface could be
   10-100x higher than at our standoff positions.
2. The FFA upgrade targets ~22 GeV (roughly double C1's 11.7 GeV max).
   Higher energy secondaries produce more displacement damage.
3. Our dose-position inversion suggests localized beam loss at aperture
   restrictions dominates over ambient dose. Halbach magnets ARE the aperture
   restriction; they catch the showers directly.

This means the real FFA degradation rate could be an order of magnitude worse
than our measurements suggest. The timeline shifts from "a few years before
problems" to "potentially problematic within the first year of operations"
at beam loss hotspots.

## Bottom Line

- At our standoff distances: manageable for a few years, especially with Dy-free grades
- At real Halbach bore distances and FFA energies: likely much worse, possibly
  first-year-of-operations concern at hotspots
- The study establishes that the effect is real and measurable even in our
  relatively benign geometry; the upgraded machine geometry only makes it worse
- Key unknowns: whether damage saturates or stays linear (Campaign 2 will test),
  actual dose multiplier for bore vs. standoff, FFA beam loss distribution

## Major Caveats

- Linear extrapolation from one campaign is the crudest possible model
- Actual beam delivery data (not planning schedules) needed for real dose rates
- No neutron transport simulation to estimate bore-surface doses
- Campaign 2 needed to test cumulative/linear/saturation behavior
- FFA beam loss patterns would differ from current CEBAF operations
