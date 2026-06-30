# Management Presentation Plan: FFA@CEBAF Magnet Radiation Study

Date: June 2, 2026 | Duration: 1 hour total | Audience: Physics Division leadership + senior staff

---

## Audience Profile

| Name | Likely focus | Notes |
|------|-------------|-------|
| David Dean | Overall assessment, decision-maker | Wants honest, rigorous assessment. Frustrated by prior misrepresentation of FFA work. Transparency and restraint will resonate. |
| Eric Brown | — | — |
| Mike Spata | Accelerator operations | Supportive. Beam loss / dose-position story will resonate. |
| Alex Bogacz | FFA design | Will challenge aggressively. Expect attacks on temperature, significance, operational relevance. Prepare but do not engage personally. Stay measured; let the data speak. |
| Joe Grames | Instrumentation | Will appreciate Helmholtz method + gain cancellation |
| Douglas Higinbotham | Rigorous statistics | Supportive. His rigor works in our favor since the work is solid. A nod from him carries weight. |
| Matt Shepherd | Nuclear/particle physics | — |
| Axel Schmidt | Nuclear physics | — |
| Allison Lung | Senior leadership | Big picture, implications |
| Eric Voutier | Nuclear physics | — |
| John Arrington | Precision measurements | Will appreciate differential technique + systematics |
| Jianwei Qiu | Theory | May engage with mechanism discussion (Dy, capture) |
| Nobuo Sato | Theory / data science | Statistical methodology, correlations |

**Key insight**: This is NOT a generally hostile room. Most attendees are neutral-to-supportive senior physicists. The primary challenge will come from one person who will probe aggressively. The best strategy is scrupulous fairness about what the data do and don't show. Restraint and transparency are the strongest assets; they contrast sharply with any prior misrepresentation in the room. Do not oversell; do not engage personally; explain calmly and move on. The room will draw its own conclusions.

## Format

- **Main talk**: ~30-35 min, accessible, building the claim ladder
- **Q&A / discussion**: ~25-30 min, expect deep technical probing
- **Backup slides**: 10+ slides for technical deep-dives (prepared answers)
- **Show and tell**: Bring Y-plate samples and/or H-plate assemblies to pass around

## Presentation Structure (Claim Ladder)

Each slide builds toward the headline result. Goal: even a skeptic walks away convinced the signal is real.

### Block 1: Setup (5 min, 3 slides)

**Slide 1: Why this matters**
- FFA@CEBAF needs permanent magnets; radiation damages them
- No one has measured this at CEBAF conditions (low dose, real accelerator)
- One sentence on the LDRD scope

**Slide 2: Experimental design**
- 39 plates, 4 material slots each (N42EH, N52SH, SmCo33H, SmCo35)
- NdFeB vs SmCo on same plate = internal standard (gain cancels)
- 30 tunnel + 9 lab controls
- Photo of plate in tunnel

**Slide 3: Measurement protocol**
- Helmholtz coil (precision), Teslameter (in-situ)
- Pre-deployment baseline -> 12 months deployment (~6 months beam-on) -> post-deployment
- Temperature correction (why it matters: 1C -> 0.1% shift vs 0.2% signal)

### Block 2: The Result (10 min, 5 slides)

**Slide 4: The money plot** [use P1 or v3 bar chart]
- NdFeB-SmCo differential: -0.208% +/- 0.028% (7.6 sigma stat, 4.6 sigma combined)
- Visual: clear negative NdFeB, SmCo near zero
- TONE NOTE: Do NOT lead with "7.6 sigma" or invoke "discovery standard." Frame as: "The signal is robust: it survives every reasonable systematic assumption we tested." Let the plot speak. Sigma values are backup if asked.
- Do NOT say "world's largest study" or "first in-situ confirmation" verbally. These are defensible in print but sound like advocacy in a room. If someone asks about prior work, then compare to Simos (N=3).

**Slide 5: Lab controls**
- Lab differential: -0.007% +/- 0.038% (0.2 sigma) = null
- This demonstrates the measurement system introduces no material-dependent bias
- Tunnel-Lab: -0.202% +/- 0.047% (4.3 sigma) = radiation is the cause
- EMPHASIS: This slide may be more persuasive than the sigma values. Dwell on it.

**Slide 6: Temperature robustness** [use temp scan table or plot]
- Signal is 4.9 sigma even at the worst-case temperature assumption
- v3 is data-driven (probe bias measurement), not cherry-picked
- NOT the most extreme result in the scan

**Slide 7: Neutron vs Gamma** [use R1 side-by-side]
- Gamma: no correlation (rho = 0.125, p = 0.51)
- Neutron: significant (rho = 0.389, p = 0.034)
- Consistent with literature: neutrons damage magnets, gammas don't (at these levels)

**Slide 8: Systematic uncertainty budget** [use P5 or uncertainty table]
- Gain drift: +/-0.124% -- but cancels in differential
- Temperature: +/-0.033%
- Total systematic: +/-0.036% -> combined 4.6 sigma
- "We've identified every systematic we know about and the signal survives"

### Block 3: The Physics (10 min, 4 slides)

**Slide 9: Why N42EH > N52SH (the Dy discovery)**
- N42EH has 1-2 wt% Dy; N52SH has zero
- Dy thermal neutron capture cross section is enormous (994 barns)
- 98% of rare-earth capture differential comes from Dy alone
- Grain boundary diffusion concentrates Dy at the weakest points

**Slide 10: SmCo paradox** [use TS2 capture budget plot]
- SmCo Sm capture: 51.8 cm^-1 (huge!) yet zero degradation
- Resolution: 6.6x higher thermal spike resistance (higher Tc, higher Ha)
- SmCo absorbs more neutrons but shrugs them off

**Slide 11: Dose-position inversion** [use R7 plot]
- More degradation at low-dose positions (top of arc stack)
- Leading hypothesis: beam loss structure (line 1 = lowest rigidity)
- Rod dosimeters measure ambient field, not local beam loss secondaries
- Doesn't undermine radiation interpretation; reveals dose field complexity
- NOTE: Do NOT volunteer simulations (BDSIM) unless asked. If asked, frame as "a future goal that would quantitatively test the hypothesis" -- not in progress, not promised on a timeline.

**Slide 12: Theory gap**
- Thermal spike model predicts 0.001% loss
- We measure 0.211% -- ratio ~196x
- Four explanations in the paper (multiple cascades, Dy amplification, sub-threshold effects, fluence underestimate)
- This gap is typical in the literature; not unique to our study

### Block 4: Implications and Next Steps (5 min, 3 slides)

**Slide 13: What this means for FFA**
- Radiation damage is real at CEBAF levels
- NdFeB without Dy (like N52SH) is preferred over Dy-containing grades
- SmCo is radiation-hard but has practical drawbacks (brittle, weak, expensive)
- Neutron fluence is the figure of merit, not gamma dose
- Non-uniform Halbach degradation will affect field quality
- FRAMING: "We identified and quantified a real effect that now needs engineering qualification." Do NOT say "FFA magnets are unsafe" or anything that sounds like a veto. Frame as quantified engineering risk requiring mitigation and design qualification.
- HALBACH ARGUMENT: The ensemble mean (-0.208%) establishes that the effect exists. But for Halbach arrays, the distribution width and tail behavior (some samples at 0.5-0.8%) determine field quality impact. Local wedge-to-wedge variation drives harmonic distortion and tune perturbations more than uniform bulk loss. Be disciplined: don't defend every extreme point as signal; distinguish robust ensemble effect from distribution width from extreme tail.
- If challenged "0.2% is nothing": "The measured effect is small over one year, but it is measurable, material-dependent, radiation-correlated, and cannot be assumed negligible without lifetime and field-quality analysis."

**Slide 14: Campaign 2 preview**
- 118/120 samples re-measured (April 2026)
- C2-C1 differential residual: -0.033 +/- 0.109% (consistent with zero storage effect)
- Magnets returned to tunnel for second exposure
- Will test cumulative damage hypothesis

**Slide 15: Summary and thank you**
- 39 plates, 156+ magnets, 12 months deployed in a real accelerator
- Statistically robust NdFeB degradation relative to SmCo, surviving all systematic checks
- Neutrons (not gammas) cause damage
- Dy amplifies radiation sensitivity
- SmCo is radiation-hard despite high capture rate
- Campaign 2 underway; paper ready for co-author review
- TONE: End with "identified a real effect, quantified it, now need engineering follow-through." Not triumphant; measured and responsible.

---

## Backup Slides: Top 10 Adversarial Q&A

### Q1: Dose-position inversion ("if degradation anti-correlates with dose, how can radiation be the cause?")
**Answer**: The rod dosimeters measure ambient dose, not local beam loss secondaries. CEBAF beam loss is highly non-uniform. Line 1 (top) has lowest rigidity = highest beam loss probability. We also have the lab control null (0.2 sigma), the SmCo null within tunnel plates, and the NdFeB-selective material dependence. All point to radiation, just a more complex dose field than the rods capture.
**Backup data**: R7 three-panel plot, 4 hypotheses from Section 6.7

### Q2: Temperature p-hacking ("you tried three temperature corrections and picked the best one")
**Answer**: Temp scan table shows signal at 4.9 sigma MINIMUM across the entire plausible range (23-25C). v3 corresponds to the probe bias measurement, not the highest significance (that would be 25C = 9.6 sigma). The choice was data-driven, not result-driven.
**Backup data**: Temp scan table, probe bias section

### Q3: Multiple comparisons ("with 21 correlations tested, Bonferroni kills your p=0.034")
**Answer**: The neutron-differential correlation was a directed hypothesis (neutrons damage magnets; from Samin 2018). We did not perform a blind search. The 4 supporting lines (material selectivity, lab null, fast>thermal, literature match) are independent. Even with Bonferroni, the total neutron-NdFeB (p=0.011) is borderline, and the intra-plate differential (7.6 sigma) does not depend on correlations at all.
**Backup data**: Section 6.6 directed hypothesis defense

### Q4: 200x theory gap ("your measurement is 200x larger than theory predicts")
**Answer**: The thermal spike model is notoriously imprecise for low-fluence regimes. Four explanations: (1) multiple cascades from secondaries, (2) Dy grain boundary amplification, (3) sub-threshold thermal spike accumulation, (4) local fluence underestimate from rod dosimeter sampling. Literature routinely shows 10-100x discrepancies. The 196x ratio constrains the model, it doesn't invalidate our measurement.
**Backup data**: TS1 plot, Section 7.4-7.5

### Q5: H/A null results ("why do your other sample types show nothing?")
**Answer**: H/A measurements are NOT gain-immune (measured across sessions, not on same plate). They carry the full +/-0.124% gain systematic. At 0.2% signal level, gain noise overwhelms the signal. This is a measurement limitation, not a physics contradiction. The Y-plate differential was specifically designed to avoid this.
**Backup data**: Section 6.4, uncertainty budget table

### Q6: N=2 temperature basis ("your entire temperature correction rests on 2 data points")
**Answer**: Yes, only 2 Y-H cross-checks per probe. But: (1) they agree within 0.1C (internal consistency), (2) the time-of-day explanation is physically plausible, (3) even if the probe bias were 0C (v2), the signal is still 4.9 sigma. Independent lab temperature logging is recommended for Campaign 2.
**Backup data**: Section 5.2, temp scan table

### Q7: Flat time evolution ("if damage is cumulative, why is the curve flat?")
**Answer**: The magnets were REMOVED from the tunnel after the first exposure period. Post-deployment measurements are in the lab (zero radiation). A flat curve is EXPECTED. Lab controls also show flat evolution, confirming no instrument drift. In-situ teslameter monitoring is available but carries its own systematics (Section 6.3).
**Backup data**: P2 time-series plot, Section 6.2

### Q8: SmCo capture paradox ("SmCo has 51.8 cm^-1 capture rate but zero damage. Isn't that contradictory?")
**Answer**: This is actually a STRENGTH of the study. SmCo's Curie temperature is 820C vs 315C for NdFeB (2.6x higher). Its anisotropy field Ha is 3.6x higher. Combined resistance: 6.6x. SmCo absorbs more neutrons but dissipates the energy without domain reversal. This is exactly what the thermal spike model predicts: damage depends on Tc/Ha ratio, not just absorption rate.
**Backup data**: TS2 capture budget plot, Section 7.3

### Q9: No blind analysis ("you knew the tunnel vs lab assignment while analyzing")
**Answer**: Five structural safeguards mitigate analyst bias: (1) randomized slot assignments, (2) pre-registered analysis plan (Helmholtz % change), (3) automated pipeline (no manual adjustment), (4) multiple measurement systems (Helmholtz + Teslameter), (5) lab controls providing independent validation. Full blind analysis is recommended for Campaign 2 (Section 7.8).
**Backup data**: Section 7.8

### Q10: FFA practical impact ("so what? Is 0.2% actually a problem?")
**Answer**: For a single 12-month deployment period (~6 months beam-on), 0.2% is small. But (1) FFA magnets would operate for 20+ years, (2) damage is likely cumulative, (3) non-uniform Halbach degradation affects field quality more than bulk loss, (4) beam loss hotspots could see 10-100x higher local fluence than our ambient measurement. The purpose of this study is to detect and characterize the effect; engineering margin calculations require Campaign 2+ data and neutron transport simulations.
**Halbach sub-argument**: "The ensemble mean answers whether radiation damage exists at all. The distribution width and tail behavior determine whether a real Halbach lattice can maintain field quality tolerances." Even discounting extreme points, the distribution width itself drives harmonic distortion through wedge-to-wedge variation.
**If challenged "then why emphasize the mean?"**: Because the mean establishes statistical reality of the effect; the tails determine engineering severity. These are complementary, not contradictory.
**Backup data**: Section 8.3 implications

### Q11: Beam duty cycle ("if beam was only on for 6 months, why do you say 12 months?")
**Answer**: The 12-month figure is the deployment period. Beam was on for approximately 6 months of that period, with a scheduled shutdown from September 2025 through January 2026. This does not affect any quantitative results because the rod dosimeters integrate actual delivered dose, and all correlations use measured dose values, not time. The dose numbers are what they are regardless of duty cycle. We now state "12 months deployment (~6 months beam-on)" in the presentation and technical note to make this distinction explicit.
**Backup data**: Section 3.4 Study Timeline, operations schedule

---

## Overall Presentation Strategy (from external reviews)

### Tone
- Frame as: "We identified and quantified a real effect that now needs engineering qualification"
- NOT: "We proved permanent magnets are unsafe" (triggers institutional immune response)
- Restraint makes senior people trust the warning more

### Sigma strategy
- Do NOT lead with 7.6σ or invoke "discovery standard" verbally
- Instead: "The signal is robust across all physically plausible temperature assumptions"
- Combined 4.6σ (including systematics) is the scientifically honest number
- If pressed on exact significance, give both: "7.6σ statistical, 4.6σ with systematics"

### Separation discipline
- What was directly measured (differential, material dependence, spatial variation)
- What correlations exist (neutron dose, line position)
- What mechanisms are hypothesized (Dy grain boundary, thermal spike, beam loss structure)
- Keep these cleanly separated in verbal presentation

### Anticipated attack lines (scripted answers)
1. "Result dominated by uncertain temperature" → Signal persists 4.9-9.6σ across full range; controls null; differential suppresses gain
2. "You changed correction until you got the answer you wanted" → Evolution fully documented; v3 driven by data, not significance; signal exists across all versions
3. "H/A don't reproduce the Y result" → Correct, because not gain-immune and location-confounded; this is explicitly acknowledged; supplementary not primary
4. "0.2% is operationally irrelevant" → Measurable, material-dependent, radiation-correlated; cannot be assumed negligible without lifetime and field-quality analysis

---

## Key Presentation Plots (from existing inventory)

| Slide | Plot source | File |
|-------|------------|------|
| 4 | Money plot / material comparison | P1_material_comparison.png |
| 5 | Lab controls | P4_lab_controls.png |
| 6 | Temp scan | (table from main.tex, or make new plot) |
| 7 | R1 side-by-side | rod_correlation_R1_side_by_side.png |
| 8 | Uncertainty budget | P5_uncertainty_budget.png |
| 9 | TS2 capture budget | neutron_capture_TS2.png |
| 10 | SmCo paradox | neutron_capture_TS2.png (same) |
| 11 | Dose-position inversion | rod_correlation_R7_line_position_inversion.png |
| 12 | Theory comparison | thermal_spike_TS1.png |
| 13 | Literature comparison | P15_literature_comparison.png |
| 14 | C2 comparison | C2-3_campaign_comparison.png |

### Plots that may need creating:
- "Hero" slide: single dramatic visual of the 7.6 sigma result
- Simplified experimental design schematic (photo + diagram)
- Temp scan visualization (currently only a table)
