# Reference Verification Log

This directory stores downloaded reference metadata and source files
so that all cited works can be independently verified.

## Policy (established 2026-04-30)
- All bibliographic details (author, title, DOI, journal, pages) must be
  verified against a real source before being written into any document.
- Downloaded metadata or PDFs are stored here for the user to check.
- If a reference cannot be verified, it must be flagged explicitly.

## IPAC26 References — Verified 2026-04-30

| # | Cite Key | Authors | Title | Verified Via |
|---|----------|---------|-------|-------------|
| 1 | Khan:ipac2024-mopr08 | D. Khan et al. | Current status of the FFA@CEBAF energy upgrade | [JACoW](https://proceedings.jacow.org/ipac2024/doi/jacow-ipac2024-mopr08/) |
| 2 | Bizen:2016 | T. Bizen et al. | Radiation-induced magnetization reversal... | [Nature](https://www.nature.com/articles/srep37937), doi:10.1038/srep37937 |
| 3 | Shepherd:Radiation | B. Shepherd | Radiation damage to PM materials: A survey... | [CERN](https://cds.cern.ch/record/2642418), CERN-ACC-2018-0029 |
| 4 | Samin:2018 | A.J. Samin | A review of radiation-induced demagnetization... | [ADS](https://ui.adsabs.harvard.edu/abs/2018JNuM..503...42S), doi:10.1016/j.jnucmat.2018.02.029 |
| 5 | Bodenstein:ipac2024-thps58 | R.M. Bodenstein et al. | PM resiliency in CEBAF's radiation environment... | [OSTI](https://www.osti.gov/biblio/2372851), doi:10.18429/JACoW-IPAC2024-THPS58 |
| 6 | Bodenstein:ipac2025-thpb093 | R.M. Bodenstein et al. | Current status of PM radiation resiliency... | JACoW, doi:10.18429/JACoW-IPAC25-THPB093 |
| 7 | Bodenstein:napac25-wean02 | R.M. Bodenstein et al. | Status of PM radiation resiliency studies... | JACoW/NAPAC'25 |
| 8 | Brooks:IPAC22-THPOTK011 | S.J. Brooks, S.A. Bogacz | Permanent Magnets for CEBAF 24GeV Upgrade | [JACoW](https://proceedings.jacow.org/ipac2022/doi/JACoW-IPAC2022-THPOTK011.html) |
| 9 | Brooks:IPAC23-WEPM128 | S. Brooks | Open-midplane gradient PM with 1.53 T... | JACoW, doi:10.18429/JACoW-IPAC2023-WEPM128 |
| 10 | Helmholtz | Magnetic Instrumentation Inc. | Model HCP Precision Helmholtz Coil Series | Product URL (commercial) |
| 11 | Senis | Senis AG | 3MH6 Teslameter | Product URL (commercial) |
| 12 | Nissen:IPAC24-THPS59 | E. Nissen et al. | Design and instrumentation for PM samples... | JACoW, doi:10.18429/JACoW-IPAC2024-THPS59 |
| 13 | Nissen:NAPAC25-WEP037 | E. Nissen et al. | Final design and first use of in-situ... | JACoW/NAPAC'25 |
| 14 | Alderman:ANL | J. Alderman et al. | Irradiation of Nd-Fe-B PM with APS Bending... | [ANL](https://publications.anl.gov/anlpubs/2000/09/37096.pdf), ANL/APS/LS tech report |
| 15 | NDX | P.V. Degtiarenko | Neutron detector and dose rate meter... | [OSTI](https://www.osti.gov/biblio/1568305), US Patent 10281600B2 |
| 16 | NEVAY:BDSIM | L.J. Nevay et al. | BDSIM: accelerator tracking with particle-matter... | [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0010465520300400), doi:10.1016/j.cpc.2020.107200 |
| 17 | Gamage:IPAC24-THPS57 | B. Gamage et al. | Radiation dose simulations for JLab PM LDRD... | JACoW, doi:10.18429/JACoW-IPAC2024-THPS57 |

## Hallucination Incident — 2026-04-30

**What happened**: The reference originally cited as "Shen:2018" / "T. Shen et al." was
hallucinated. The correct author is A.J. Samin (single author, not "et al.").
The DOI was also wrong: .037 (points to a plutonium trifluoride paper) instead of .029.

**How it was caught**: Co-author flagged that no "Shen" paper exists with that title.

**What was correct**: Title, journal, volume, year, and pages were all correct.
Only the author name and DOI suffix were fabricated.

**Files corrected**: IPAC26.tex, references.bib, main.tex, presentation_plots.py,
thermal_spike_comparison.py, Data_Package copies, memory files.

**Lesson**: Always verify author names and DOIs against a real source (ADS, OSTI,
publisher website) before writing them. Never rely on memory for bibliographic details.

## Billan → Shepherd Correction — 2026-04-30

**What happened**: The tech note's references.bib listed CERN-ACC-2018-0029 as authored by
"Billan, J. and others" with title "Radiation Damage to Permanent Magnet Materials: A Survey."

**Correct attribution**: B. Shepherd (sole author, STFC Daresbury Laboratory). Full title:
"Radiation damage to permanent magnet materials: A survey of experimental results."
Also carries report number CLIC-Note-1079.

**How it was caught**: During IPAC paper audit, the IPAC paper cited this as "B. Shepherd"
while the tech note bib had "Billan, J. and others." CDS record 2642418 confirms Shepherd.

**Files corrected**: references.bib (Billan2018 → Shepherd2018), literature_references.md.

## ICRP 103 Addition — 2026-04-30

**Added**: ICRP Publication 103 (2007), "The 2007 Recommendations of the ICRP."
Ann. ICRP 37(2-4), pp. 1-332. DOI: 10.1016/j.icrp.2007.10.003.
Verified via ICRP website, PubMed (PMID 18082557), and ScienceDirect.
Confirms continuous neutron w_R function with w_R = 2.5 at thermal energies.

## Tech Note Bibliography Cleanup — 2026-05-08

Fixed 6 incomplete/incorrect entries in `Technical_Note/references.bib`.
Three had hallucinated titles (Cost1988, NGotta2024, Brooks2017).

### Corrected entries (metadata completed)

| # | Cite Key | Authors | Title | Journal | DOI | PDF Status |
|---|----------|---------|-------|---------|-----|------------|
| 1 | Alderman | J. Alderman, P.K. Job, R.C. Martin, C.M. Simmons, G.D. Owen, J. Puhl | Measurement of radiation-induced demagnetization of Nd-Fe-B PM | NIMA 481, 9-28 (2002) | 10.1016/S0168-9002(01)01329-8 | PAYWALLED (Elsevier) |
| 2 | Miyahara | N. Miyahara, T. Honma, T. Fujisawa | Irradiation effects of a 10 MeV neutron beam on a Nd-Fe-B PM | NIMB 268, 57-61 (2010) | 10.1016/j.nimb.2009.09.050 | PAYWALLED (Elsevier) |
| 3 | Okuda | S. Okuda, K. Ohashi, N. Kobayashi | Effects of e-beam and gamma-ray irradiation on NdFeB and SmCo PM | NIMB 94, 227-230 (1994) | 10.1016/0168-583X(94)95358-9 | YES (user-uploaded 2026-05-08) |
| 4 | Cost1988 | J.R. Cost, R.D. Brown, A.L. Giorgi, J.T. Stanley | Effects of neutron irradiation on Nd-Fe-B magnetic properties | IEEE Trans. Magn. 24(3), 2016-2019 (1988) | 10.1109/20.3393 | YES (user-uploaded 2026-05-08) |

### Hallucinated entries replaced

| Old Key | Problem | New Key(s) | Real Title(s) | PDF Downloaded? |
|---------|---------|-----------|---------------|-----------------|
| NGotta2024 | Fabricated title "Halbach Array Degradation Patterns and Lattice-Level Impacts"; no such IPAC2024 paper exists | NGotta2025_MEDSI | Development of Radial Magic Finger Design for PMQ | YES |
| | | NGotta2025_NAPAC | Development of combined function dipole-quadrupole PMQs for NSLS-II upgrade | YES |
| Brooks2017 | Fabricated title "Muon Collider Lattice Design..."; no such paper exists | Brooks2017_IPAC | Production of Low Cost, High Field Quality Halbach Magnets | YES |
| | | Brooks2020_PRAB | PM for the return loop of the Cornell-BNL ERL test accelerator | YES |
| | | Brooks2021_IPAC | Modified Halbach Magnets for Emerging Accelerator Applications | YES |

### main.tex citations rewritten

- Line 210: `\cite{NGotta2024,Brooks2017}` -> `\cite{Brooks2021_IPAC,Brooks2017_IPAC}`
- Line 1088: `\cite{NGotta2024}` -> `\cite{Brooks2021_IPAC}`
- Line 2200: `\cite{NGotta2024}` -> `\cite{Brooks2021_IPAC}`
- Line 2313: `\cite{NGotta2024,Brooks2017}` -> `\cite{Brooks2021_IPAC,Brooks2017_IPAC}`
- Lines 2334-2343: Full paragraph rewritten to accurately describe the real papers

### Additional entry added (user-identified)

| # | Cite Key | Authors | Title | Journal | DOI | PDF Status |
|---|----------|---------|-------|---------|-----|------------|
| 10 | Brooks2022_IPAC | S.J. Brooks, S.A. Bogacz | Permanent Magnets for the CEBAF 24 GeV Upgrade | Proc. IPAC'22, pp. 2792-2795 | 10.18429/JACoW-IPAC2022-THPOTK011 | YES (JACoW) |

This is the paper that directly addresses non-uniform demagnetization sensitivity within Halbach wedges for the FFA@CEBAF design (Fig. 5: color-coded map of antiparallel field showing which regions are most vulnerable). Already in IPAC26 bib as `Brooks:IPAC22-THPOTK011`; now added to tech note as `Brooks2022_IPAC`.

### Verification method

- Alderman, Miyahara: DOI resolver landing pages (publisher metadata). PDFs paywalled (Elsevier).
- Okuda: DOI resolver + full PDF (user-uploaded 2026-05-08). Content verified: 9% NdFeB flux loss at 2.6 MGy electron beam, <0.4% SmCo; gamma-ray at 2.8 MGy gives <0.5% for both.
- Cost1988: DOI resolver + full PDF (user-uploaded 2026-05-08). Content verified: collision-cascade reverse-domain nucleation model (foundational thermal spike concept); 10% remanence loss at 10^15 n/cm² (426 K); full recovery on remagnetization + 20% coercivity increase.
- NGotta2025_MEDSI: PDF downloaded from epaper.kek.jp
- NGotta2025_NAPAC: PDF downloaded from prebys.physics.ucdavis.edu
- Brooks2017_IPAC: PDF downloaded from accelconf.web.cern.ch
- Brooks2020_PRAB: PDF downloaded from stephenbrooks.org
- Brooks2021_IPAC: PDF downloaded from accelconf.web.cern.ch

### Additional upload (for later use)

- NDX patent paper: `NDX_Neutron_Dose_Rate_Meters_with_Extended_Capabilities.pdf` (uploaded 2026-05-06). For Task 14 (NDX detector analysis).
