# FFA@CEBAF Magnet Radiation Study: Presentation Outline

## Format
- ~30-35 min main talk (accessible to broad physics audience)
- ~25 min discussion / Q&A
- Backup slides for deep technical questions
- Physical samples available for demonstration

---

## Part 1: Motivation and Design (5-7 min)

### Why this study exists
- FFA@CEBAF requires permanent magnets in a mixed radiation environment
- Prior data on radiation damage exists only at doses 100-1000x higher than CEBAF levels
- No measurements existed at real accelerator conditions in the sub-percent regime
- LDRD scope: detect and quantify the effect, if it exists

### Experimental design
- 39 Y-plates: 30 in tunnel, 9 lab controls
- Each plate carries 4 material grades (2 NdFeB, 2 SmCo), randomized slot assignments
- Key idea: NdFeB and SmCo on the same plate, measured in the same session
- Helmholtz coil fluxmeter; temperature-corrected to 20C reference
- 12 months of tunnel deployment (~6 months beam-on)

### The intra-plate differential
- Instrument gain drift is the dominant noise source (~0.1-0.2% per session)
- But gain affects all four slots equally within a session
- Subtracting SmCo from NdFeB on the same plate cancels gain exactly
- This is the methodological core of the study

---

## Part 2: Results (10-12 min)

### The headline result
- NdFeB degraded by -0.208% relative to SmCo (stat. uncertainty 0.028%)
- Signal is robust: survives all physically plausible temperature assumptions (4.9-9.6 sigma across the range)
- Combined significance including systematics: 4.6 sigma

### Lab controls
- Lab Y-plate differential: -0.007% +/- 0.038% (consistent with zero)
- Tunnel minus lab: -0.202% +/- 0.047% (4.3 sigma)
- The lab null confirms the tunnel signal is radiation-associated, not instrumental

### Per-material breakdown
- N42EH (NdFeB): -0.252%
- N52SH (NdFeB): -0.170%
- SmCo33H: +0.037% (consistent with zero)
- SmCo35: -0.044% (consistent with zero)
- SmCo serves as an in-situ radiation-hard reference

### Temperature correction and robustness
- Temperature coefficients differ between NdFeB (-0.10 to -0.11%/C) and SmCo (-0.04%/C)
- Correction is necessary but well-constrained
- Systematic uncertainty: 0.033% on the differential
- Signal persists across the entire plausible temperature range

### Dose correlations
- Gamma dose: no correlation with degradation
- Neutron dose: significant correlation (rho = 0.389, p = 0.034)
- Fast neutrons correlate more strongly than thermal
- Consistent with displacement cascade damage mechanism

---

## Part 3: Physics Interpretation (7-10 min)

### Why N42EH degrades more than N52SH
- N42EH contains 1-2 wt% Dysprosium; N52SH contains none
- Dy has an enormous thermal neutron capture cross-section (994 barns)
- 98% of the rare-earth capture differential comes from Dy alone
- Grain boundary diffusion concentrates Dy at the structurally weakest points
- Actionable finding: Dy-free grades are preferred for radiation environments

### The SmCo paradox
- SmCo has the highest neutron capture rate (Sm: 51.8 cm^-1) yet zero degradation
- Resolution: SmCo has 2.6x higher Curie temperature and 3.6x higher anisotropy field
- Combined thermal spike resistance: ~6.6x
- SmCo absorbs more neutrons but dissipates energy without permanent damage

### Theory comparison
- Thermal spike model predicts 0.001% loss; we measure 0.211% (ratio ~196x)
- Quantitative gap is typical for low-fluence regimes in the literature
- Four candidate explanations discussed in the technical note
- The gap constrains the model; it does not invalidate the measurement

### Dose-position inversion
- In arc stacks, Line 1 (top, lowest total dose) shows the most degradation
- Leading hypothesis: lowest-energy beam pass has tightest aperture, highest local beam loss
- Rod dosimeters measure the broad ambient field, not localized hadronic showers
- Does not undermine the radiation interpretation; reveals dose-field complexity

---

## Part 4: Implications and Next Steps (5-7 min)

### What this means for FFA magnet design
- Radiation damage to NdFeB is real and measurable at CEBAF dose levels
- Dy-free NdFeB grades (e.g., N52SH) are preferred over Dy-containing grades
- SmCo is radiation-hard but has practical drawbacks (brittle, lower remanence, higher cost)
- Neutron fluence, not gamma dose, is the relevant figure of merit
- For Halbach arrays: the distribution of per-sample degradation (not just the mean) determines field quality impact, since local wedge-to-wedge variation drives harmonic distortion

### Systematic uncertainties and what we cannot yet say
- Temperature correction is the dominant systematic (0.033%)
- Gain drift cancels in the differential but limits absolute per-material conclusions
- Lifetime extrapolation requires Campaign 2+ data
- Assembled Halbach field-quality impact requires dedicated modeling

### Campaign 2 status
- 118/120 samples re-measured (April 2026) after ~4 months of lab storage
- C2-C1 differential residual: -0.033 +/- 0.109% (consistent with zero storage effect)
- Magnets returned to tunnel for second exposure period
- Will test cumulative damage hypothesis

### Summary
- Statistically robust detection of sub-percent NdFeB degradation relative to SmCo
- Signal survives all systematic checks: lab controls, temperature sweep, gain cancellation
- Neutrons cause the damage; Dy amplifies sensitivity; SmCo is resistant
- Effect is a quantified engineering risk requiring design qualification for FFA
- Technical note ready for co-author review; Campaign 2 underway

---

## Backup Slides (for Q&A)

1. Temperature scan table (4.9-9.6 sigma across 23-25C)
2. Probe bias derivation and N=2 limitation
3. v1/v2/v3 temperature correction evolution
4. Bonferroni / multiple comparisons discussion
5. H-plate and A-sample results (why they don't reproduce Y-plate signal)
6. Outlier handling (Y-34-4, Y-40-4)
7. Gain drift quantification and session-by-session breakdown
8. Neutron capture budget by element and grade (TS2 plot)
9. Fast vs thermal neutron correlation breakdown
10. Dose-position inversion detail (R7 three-panel plot)
11. Thermal spike model calculation details
12. Literature comparison (prior studies at 100-1000x higher dose)
13. Campaign 2 quality check details
14. Blind analysis mitigation and Campaign 2 recommendations
15. Beam duty cycle: 12 months deployment vs ~6 months beam-on; dosimeters integrate actual dose

## Physical Samples

- Bring Y-plate(s) to pass around during the experimental design discussion
- Demonstrates the four-slot layout and the scale of the magnets
- Makes "same plate, same session" immediately tangible
