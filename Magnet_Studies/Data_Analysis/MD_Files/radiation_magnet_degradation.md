# Radiation-Induced Flux Loss in Permanent Magnets: A Comprehensive Physics Framework for the 12 GeV CEBAF Continuous-Wave Environment

**Grades Under Analysis:** N42EH, N52SH (Nd₂Fe₁₄B); SmCo33H, SmCo35 (Sm₂Co₁₇)

---

## Preface: Scope and Approach

Quantifying radiation-induced flux loss in permanent magnets installed at the 12 GeV Continuous Electron Beam Accelerator Facility (CEBAF) requires coupling the macroscopic thermodynamic state of the magnet -- defined through vector magnetic field superposition -- with the stochastic nuclear transport of the particle cascade initiated by beam-halo losses. Analytical solutions are not tractable in realistic accelerator geometries; the relevant physics must be discretized and sampled via Monte Carlo transport codes, principally Geant4 [1] and FLUKA [2], to compute site-specific energy deposition spectra and Primary Knock-on Atom (PKA) distributions.

This document is organized to follow the complete causal chain from macroscopic operating conditions through cascade physics, nuclear damage mechanisms, microscopic material response, and finally material-specific failure thresholds for the four grades under study. Each section provides both a rigorous physics treatment and a simplified conceptual summary for accessibility.

---

## I. Macroscopic Magnetic States and Vector Field Superposition

### I.1 The Self-Demagnetizing Field

**Simplified concept:** Every permanent magnet generates an internal magnetic field that opposes its own magnetization. This self-opposition is strongest near the magnet's edges and corners. Think of it as the magnet fighting against itself -- the uncompensated magnetic poles at the surfaces create a field pointing in the direction opposite to the magnetization, weakening the magnet's ability to maintain its magnetic state.

**Rigorous treatment:** For an isolated magnetic body with uniform magnetization **M**, the uncompensated magnetic poles at the body's surfaces generate an internal field that actively opposes **M**. This is formalized through the spatial demagnetization tensor **N**(r):

$$\vec{H}_{self}(\vec{r}) = -\mathbf{N}(\vec{r}) \cdot \vec{M}$$

The tensor **N**(r) is position-dependent for all geometries except an infinite ellipsoid. The trace of the demagnetization tensor satisfies the constraint Tr(**N**) = 1 (in SI units) for any closed body [3], reflecting the fact that the total demagnetizing effect is conserved regardless of geometry; changing the aspect ratio redistributes the demagnetizing field among the three principal axes but does not eliminate it.

The self-demagnetizing field is maximized near the physical boundaries of the magnetic volume, intrinsically lowering the local permeance coefficient $P_c$. The permeance coefficient is the slope of the operating load line on the B-H diagram:

$$P_c = \frac{B_m}{\mu_0 H_m}$$

where $B_m$ and $H_m$ are the magnet's operating induction and field, respectively. A low $P_c$ means the local operating point on the B-H curve sits closer to the knee -- the point on the intrinsic demagnetization curve where the curve bends sharply and irreversible flux loss begins. This establishes boundary regions as the sites of greatest thermodynamic vulnerability.

### I.2 The Generalized Operating Point in Halbach Geometries

**Simplified concept:** In a Halbach array -- the arrangement used to build accelerator multipole magnets from wedge-shaped permanent magnet segments -- each magnet wedge is surrounded by neighbors whose magnetizations point in different directions. Some neighbors actively push against a given wedge's magnetization, creating zones of very high internal stress. The wedges where the magnetization is oriented tangentially (azimuthally) experience the worst stress, because their neighbors' fields oppose them most strongly. These are the weak links in the chain -- the first places where radiation damage will cause problems.

**Rigorous treatment:** Accelerator multipoles based on Halbach arrays [4] segment the magnetic circuit into N wedges of differing magnetization orientation. The total internal field **H**_tot within a specific wedge k is the exact linear superposition of the wedge's own self-field and the stray fields contributed by all N-1 adjacent wedges:

$$\vec{H}_{tot}^{(k)}(\vec{r}) = \vec{H}_{self}^{(k)}(\vec{r}) + \sum_{j \neq k} \vec{H}_{stray}^{(j \rightarrow k)}(\vec{r})$$

The scalar quantity that determines local vulnerability is the component of **H**_tot projected anti-parallel to the local magnetization vector **M**_k. Defining the normalized direction $\hat{M}_k = \vec{M}_k / |\vec{M}_k|$, the scalar operating field is:

$$H_{op}(\vec{r}) = \vec{H}_{tot}^{(k)}(\vec{r}) \cdot \hat{M}_k$$

When $H_{op}$ is negative, the total local field opposes the magnetization, and its magnitude $|H_{op}|$ defines the demagnetizing stress at that point. By the geometric constraints of Halbach construction, adjacent wedges are forced into strongly opposing magnetization directions. In wedges where **M** is primarily azimuthal -- the so-called "azimuthal" or "bridge" segments -- $H_{op}(\vec{r})$ is most negative, driving the local operating load line closest to the knee of the normal B-H curve.

This is the site of maximum vulnerability to any perturbation that locally suppresses the intrinsic coercivity, whether thermal or radiation-induced. The critical engineering consequence is that radiation damage does not need to affect the entire magnet volume uniformly to degrade accelerator performance; damage localized to a small number of azimuthal wedge segments can produce outsized effects on the integrated multipole field quality.

### I.3 The Permeance Coefficient and Geometric Shape Factor

**Simplified concept:** The shape of a magnet determines how hard it has to work to maintain its magnetization. A long, thin magnet (like a pencil) is in a naturally stable configuration -- it has a high permeance coefficient and operates far from the danger zone on its demagnetization curve. A short, flat magnet (like a coin) has a low permeance coefficient and operates much closer to the danger zone. In accelerator Halbach arrays, the wedge geometry combined with the opposing fields from neighboring wedges can push certain locations very close to this danger zone.

The permeance coefficient is determined by the magnet's geometric aspect ratio. For a simple cylindrical magnet of length L and diameter D, the approximate relationship is:

$$P_c \approx \frac{L/D}{1 - L/D} \cdot \frac{4}{\pi}$$

More precisely, finite element methods are required for complex geometries, but the key principle is that the L/D ratio (or more generally, the ratio of the dimension parallel to magnetization to the dimension perpendicular) governs the operating point. This dependence has been confirmed experimentally in radiation damage studies: magnets with higher L/D ratios (higher $P_c$) consistently show greater radiation resistance [5, 6, 7].

**Quantitative L/D dependence:** The radiation sensitivity dependence on the geometric shape factor is not merely qualitative. Miyahara et al. [51] irradiated NdFeB samples (Neomax 30H) with 10 MeV neutrons at L/D ratios between 0.5 and 6.1, and found that demagnetization at a given neutron dose varied dramatically with the shape factor. Samples with L/D = 0.5 (disk-like, low $P_c$, operating close to the knee) lost magnetization at much lower fluences than samples with L/D = 6.1 (rod-like, high $P_c$, operating far from the knee). Brown and Cost [39] observed the same pattern with fast neutron irradiation. Simos et al. [22] extended this to mixed irradiation fields at the BNL BLIP facility, confirming that the shape factor is one of the strongest single predictors of radiation sensitivity and further demonstrating that annular magnet geometries (which have a high effective $P_c$ due to their topology) show significantly enhanced demagnetization resistance compared to block geometries of similar material.

The physical interpretation connects directly to the $\Delta T_{crit}$ framework of Section V.3: a higher $P_c$ means a lower $|H_{op}|$ (the operating point is further from the knee), which increases $\Delta T_{crit}$ and thus requires a more energetic thermal spike to trigger domain reversal. The L/D ratio is therefore not an independent variable but a geometric parameterization of the same thermodynamic margin that governs radiation vulnerability.

**Relevance to the LDRD study samples:** The permanent magnet samples used in the CEBAF radiation resiliency study [41,46] are 3.81 cm $\times$ 1.91 cm $\times$ 0.635 cm blocks and paired assemblies. This geometry has a specific $P_c$ that determines its operating point on the demagnetization curve. When comparing LDRD results to the published literature, it is essential to match or correct for the sample geometry, because nominally identical materials at different L/D ratios will show different radiation sensitivity. Similarly, extrapolating from the LDRD sample results to the actual FFA Halbach wedge geometry requires accounting for the very different $P_c$ of the wedge in its assembled magnetic circuit (Section I.2), where the opposing fields from neighboring wedges substantially reduce the effective operating point compared to an isolated sample.

---

## II. The 12 GeV Particle Cascade: Electromagnetic Shower and Photonuclear Neutron Production

### II.1 Cascade Topology: A Critical Distinction

**Simplified concept:** When CEBAF's 12 GeV electron beam loses particles (beam halo losses), those electrons don't directly damage the magnets in any significant way. Instead, the electrons slam into metal structures (beam pipe, collimators), producing a shower of high-energy photons. Some of these photons then knock neutrons out of atomic nuclei. It is these neutrons -- uncharged particles that can penetrate shielding and reach the magnet material -- that are the primary agents of magnet damage. Understanding this chain of events is essential: the damage pathway is electron --> photon --> neutron --> magnet lattice damage.

**Rigorous treatment:** The primary damage vector to permanent magnets at 12 GeV CEBAF is not a hadronic cascade. The dominant pathway is electromagnetic: a primary electron initiates a bremsstrahlung shower in a high-Z material (beam pipe, collimator), producing a spectrum of energetic photons, which in turn excite photonuclear reactions that eject fast neutrons. These neutrons, being uncharged, penetrate electromagnetic shielding and interact directly with the permanent magnet lattice.

This distinction was established experimentally by the extensive studies of Bizen et al. at SPring-8 [5, 8, 9, 10]. Their systematic investigations using 2 to 8 GeV electron beams on Nd₂Fe₁₄B undulator magnets, combined with FLUKA Monte Carlo simulations, demonstrated that low-energy photoneutrons (below approximately 1 MeV) and direct bremsstrahlung photons are not the primary drivers of demagnetization. Rather, the "star density" -- a FLUKA scoring quantity that tallies hadronic interactions including elastic and inelastic neutron scattering above a threshold energy -- showed strong spatial correlation with the observed demagnetization pattern [8].

A hadronic component -- involving pion production, subsequent hadronic cascades, and proton spallation -- is physically real at 12 GeV. The threshold for neutral pion production via $\gamma + p \rightarrow p + \pi^0$ is approximately 145 MeV, and the bremsstrahlung spectrum at 12 GeV extends well beyond this; hadronic processes therefore occur and are not negligible. However, the photonuclear neutron pathway dominates the magnet damage budget, and the two processes must not be conflated. Monte Carlo codes such as Geant4, with appropriate physics lists (e.g., QGSP_BIC_HP or Shielding) activated, model both components simultaneously.

### II.2 Bremsstrahlung Generation and the Bethe-Heitler Cross-Section

**Simplified concept:** When a high-energy electron passes close to a heavy atomic nucleus, the strong electric field of the nucleus deflects the electron, and the electron emits a photon (bremsstrahlung, German for "braking radiation"). The heavier the nucleus (higher atomic number Z), the more efficient this process is -- it scales roughly as Z². This is why lead and tungsten collimators are such prolific radiation sources, and why the choice of material surrounding the beam matters so much for the downstream magnet damage budget.

**Rigorous treatment:** When a 12 GeV primary electron penetrates a high-Z material -- the stainless steel beam pipe or any lead or tungsten collimator -- it decelerates in the screened Coulomb field of the target nuclei and emits a continuous spectrum of bremsstrahlung photons. The differential cross-section for photon emission, $d\sigma_{brem}/dk$, for a photon of energy k emitted by an electron of total energy E, in the complete-screening (high-energy) limit is given by the Bethe-Heitler formula [11]:

$$\frac{d\sigma_{brem}}{dk} = 4\alpha Z^2 r_e^2 \frac{1}{k}\left[\left(1 + \left(\frac{E-k}{E}\right)^2 - \frac{2}{3}\frac{E-k}{E}\right)\ln\frac{183}{Z^{1/3}} + \frac{1}{9}\frac{E-k}{E}\right]$$

where $\alpha \approx 1/137$ is the fine-structure constant, Z is the atomic number of the target nucleus, and $r_e \approx 2.818 \times 10^{-15}$ m is the classical electron radius. The 1/k dependence means the photon spectrum is heavily weighted toward low energies, but the high-energy tail extending up to the full beam energy is what drives the photonuclear processes.

The characteristic length scale for bremsstrahlung energy loss is the radiation length $X_0$, defined as the mean distance over which a high-energy electron loses a fraction (1 - 1/e) of its energy to bremsstrahlung. For materials relevant to CEBAF:

- **Stainless steel (Fe-dominant):** $X_0 \approx 1.76$ cm
- **Lead:** $X_0 \approx 0.56$ cm
- **Tungsten:** $X_0 \approx 0.35$ cm

The radiation length scales approximately as $X_0 \propto A/(Z^2 \ln(183/Z^{1/3}))$, where A is the atomic mass number [12]. This means that high-Z collimator materials convert electron kinetic energy into photon flux much more efficiently per unit length, but also produce more compact and intense electromagnetic showers.

**Landau-Pomeranchuk-Migdal (LPM) suppression.** At 12 GeV in high-density, high-Z materials, the Bethe-Heitler formula overestimates the bremsstrahlung yield at low photon energies. When the longitudinal momentum transfer to the nucleus is less than the inverse of the mean inter-atomic spacing, coherent scattering from multiple atoms destructively interferes with the emission amplitude. This suppression, predicted by Landau and Pomeranchuk [13] and calculated quantum mechanically by Migdal [14], reduces bremsstrahlung production for photon energies below a material-dependent LPM energy. The LPM energy for lead is approximately 2.2 GeV. Geant4 implements LPM suppression and it must be enabled in the physics list for accurate photon spectrum calculation; its omission would overestimate photoneutron yields from lead collimators.

### II.3 Electromagnetic Shower Development

**Simplified concept:** When a high-energy electron enters a dense material, it doesn't just emit one photon and stop. Instead, a cascade multiplication occurs: the electron emits a bremsstrahlung photon; if the photon is energetic enough, it produces an electron-positron pair; each of those particles then emits more photons; those photons create more pairs; and so on. This cascade grows exponentially until the individual particle energies drop below a critical energy where ionization losses dominate over radiation losses. The result is a "shower" of thousands of particles confined to a roughly cone-shaped volume. The transverse spread of this shower, characterized by the Moliere radius, determines how much radiation reaches magnets positioned laterally relative to the beam loss point.

**Rigorous treatment:** The electromagnetic cascade proceeds through alternating generations of bremsstrahlung and pair production. The shower reaches maximum particle multiplicity at a depth approximately given by [12]:

$$t_{max} \approx \ln\left(\frac{E_0}{E_c}\right) - 0.5$$

measured in radiation lengths, where $E_0$ is the primary electron energy and $E_c$ is the critical energy -- the energy at which ionization and radiation losses are equal. For iron, $E_c \approx 21.0$ MeV; for lead, $E_c \approx 7.4$ MeV [12]. At 12 GeV in lead, the shower maximum occurs at approximately $t_{max} \approx \ln(12000/7.4) - 0.5 \approx 6.9$ radiation lengths, corresponding to approximately 3.9 cm of physical depth.

The lateral spread of the shower is characterized by the Moliere radius $R_M$, which is the radius of a cylinder containing approximately 90% of the shower energy:

$$R_M = X_0 \frac{E_s}{E_c}$$

where $E_s = m_e c^2 \sqrt{4\pi/\alpha} \approx 21.2$ MeV is the scale energy [12]. For iron, $R_M \approx 1.78$ cm; for lead, $R_M \approx 1.60$ cm. This lateral containment scale determines the spatial distribution of photoneutron sources and hence the radiation field geometry as seen by nearby permanent magnets.

### II.4 Photonuclear Reactions and Photoneutron Yield

**Simplified concept:** When a high-energy photon from the electromagnetic shower is absorbed by an atomic nucleus, it can shake the nucleus so violently that one or more neutrons are ejected. The dominant mechanism, called the Giant Dipole Resonance (GDR), is a collective oscillation where all the protons in the nucleus slosh back and forth against all the neutrons -- like two interpenetrating fluids vibrating against each other. This resonance peaks at photon energies of about 13-22 MeV depending on the nuclear mass, and it is the single most important source of the neutrons that damage permanent magnets. Crucially, the minimum photon energy needed to eject a neutron depends on how tightly that nucleus holds onto its neutrons -- lead releases neutrons more easily than iron, making lead collimators more prolific neutron sources.

**Rigorous treatment:** High-energy bremsstrahlung photons interacting with target nuclei trigger several photonuclear mechanisms at different energy scales:

**1. Giant Dipole Resonance (GDR), 8-30 MeV:** This is a collective nuclear mode first described by Goldhaber and Teller [15] in which all protons oscillate coherently against all neutrons, behaving as two interpenetrating fluids. The resonance is characterized by a Lorentzian-shaped cross-section peaking at:

- $E_{GDR} \approx 31.2 A^{-1/3} + 20.6 A^{-1/6}$ MeV (an empirical parameterization) [16]
- For heavy nuclei (A > 100): peak at approximately 13-17 MeV
- For medium-mass nuclei (A ~ 50-60): peak at approximately 17-22 MeV

At the GDR peak, the photonuclear cross-section reaches values of approximately 200-600 mb for heavy nuclei, with a width of typically 4-8 MeV [16]. The predominant decay mode is single neutron emission ($\gamma$,n), with ($\gamma$,2n) becoming significant above the two-neutron separation energy. The neutrons emitted from GDR decay have a characteristic "evaporation" energy spectrum, approximately Maxwellian with a nuclear temperature parameter of 1-2 MeV, meaning most GDR-emitted neutrons have energies in the range of 1-5 MeV.

**2. Quasi-deuteron process, 30-140 MeV:** At photon energies above approximately 30 MeV, the photon wavelength becomes comparable to the internucleon spacing, and the photon interacts preferentially with correlated proton-neutron pairs within the nucleus, as described by the Levinger quasi-deuteron model [17]. The cross-section for this process scales as:

$$\sigma_{qd}(E_\gamma) \approx L \frac{NZ}{A} \sigma_d(E_\gamma)$$

where $\sigma_d$ is the free deuteron photodisintegration cross-section, L is the Levinger constant (empirically $L \approx 6.5$), and N, Z, A are the neutron number, proton number, and mass number of the target nucleus [17]. This process produces higher-energy neutrons and protons than the GDR, typically in the range of 10-100 MeV.

**3. Photopion production, above ~145 MeV:** At photon energies above the pion production threshold, $\Delta$(1232) resonance excitation becomes important. This is the onset of the hadronic cascade contribution mentioned in Section II.1.

The volumetric photoneutron production rate $Y_n(\vec{r})$ integrates over all these mechanisms:

$$Y_n(\vec{r}) = \int_{E_{th}}^{E_{max}} \Phi_\gamma(E_\gamma, \vec{r})\, \Sigma_{\gamma,n}(E_\gamma)\, dE_\gamma$$

**The threshold energy $E_{th}$ is not a universal constant.** It equals the neutron separation energy $S_n$ of the target nucleus, which is strongly material-dependent. From the AME2016 atomic mass evaluation [18]:

- **⁵⁶Fe** (dominant isotope in stainless steel beam pipe): $S_n(^{56}\text{Fe}) \approx 11.20$ MeV
- **²⁰⁸Pb** (dominant isotope in lead collimators): $S_n(^{208}\text{Pb}) \approx 7.37$ MeV
- **¹⁸⁴W** (dominant isotope in tungsten collimators): $S_n(^{184}\text{W}) \approx 7.41$ MeV

The consequence is that lead or tungsten collimators are substantially more prolific photoneutron sources per unit photon flux than the stainless beam pipe, because a larger fraction of the bremsstrahlung spectrum exceeds their lower thresholds and because their GDR cross-sections are larger (scaling approximately as NZ/A). Monte Carlo geometry models must therefore accurately represent collimator material composition.

### II.5 Neutron Moderation and the Thermal/Epithermal Neutron Field

**Simplified concept:** The fast neutrons produced by photonuclear reactions don't stay fast. As they scatter off surrounding materials -- concrete shielding, support structures, air, the magnets themselves -- they gradually lose energy through elastic collisions, a process called moderation. After enough collisions, neutrons reach thermal equilibrium with the surrounding material at room temperature, with a characteristic energy of about 0.025 eV. This is important because certain nuclear reactions, particularly the ¹⁰B neutron capture reaction discussed later, have enormous cross-sections at these very low neutron energies. A shielded accelerator environment always has a significant population of moderated (thermal and epithermal) neutrons in addition to the fast neutron field, and both contribute to magnet damage through different mechanisms.

**Rigorous treatment:** In any shielded accelerator environment, the neutron energy spectrum at the magnet location is not monoenergetic but spans from thermal energies (~0.025 eV at room temperature) to the maximum energy set by the photonuclear source term (tens of MeV). The fast neutron spectrum from photonuclear reactions is moderated by elastic scattering in the surrounding material (shielding, structural steel, concrete, the magnet material itself).

The average number of elastic collisions required to moderate a neutron from energy $E_0$ to thermal energy $E_{th}$ is:

$$n = \frac{\ln(E_0/E_{th})}{\xi}$$

where $\xi$ is the average logarithmic energy decrement per collision, given by $\xi = 1 + \frac{(A-1)^2}{2A}\ln\frac{A-1}{A+1}$ for a target of mass number A [19]. For hydrogen (A = 1), $\xi = 1$ (maximum moderation per collision); for iron (A = 56), $\xi \approx 0.035$. This means that approximately 520 elastic collisions with iron are needed to thermalize a 2 MeV neutron, whereas only about 18 collisions with hydrogen suffice.

The practical consequence is that the ratio of thermal-to-fast neutron flux at the magnet location depends sensitively on the local geometry and material composition -- the presence of hydrogenous materials (water pipes, concrete, polyethylene shielding) near the beam loss point dramatically increases the thermal neutron population and therefore the ¹⁰B(n,$\alpha$) reaction rate in NdFeB magnets.

---

## IIA. Synchrotron Radiation in the Recirculating Arcs: The Radiation Environment and an Emerging Observation

Sections II through II.5 describe the electromagnetic cascade initiated when the primary beam (or beam halo) strikes material -- a beam loss event that produces bremsstrahlung, photoneutrons, and associated secondaries. This section treats a fundamentally different radiation source: the synchrotron radiation (SR) emitted by the beam itself as it traverses the bending magnets in the recirculating arcs. In a CW recirculating linac like CEBAF, this SR is continuous, unavoidable, and distributed along every arc dipole. Preliminary results from the ongoing Jefferson Lab LDRD study [41,42] suggest that the arc environment -- where SR is the dominant photon source but where secondaries and beam losses are also present -- may produce more magnet degradation than the linac environment near the cryomodules. The specific damage mechanism responsible for this observation has not yet been identified, and resolving this question is one of the central scientific goals of the study.

### IIA.1 The Synchrotron Radiation Source in CEBAF Arcs

**Simplified concept:** Any charged particle moving in a curved path radiates electromagnetic energy. For multi-GeV electrons bending in a magnetic field, this radiation is an intense, highly collimated fan of X-ray photons. At CEBAF energies, the characteristic photon energy falls in the hard X-ray range (tens to hundreds of keV), and the total radiated power scales as the fourth power of the electron energy. The radiation is emitted tangentially to the electron orbit and sweeps across any component near the beam path, including permanent magnets positioned in or near the arcs.

**Rigorous treatment:** When an electron of energy $E = \gamma m_e c^2$ traverses a dipole of field strength B, it follows a circular arc of radius $\rho = E/(ecB)$ (in practical units, $\rho \text{ [m]} = 3.336\, E \text{ [GeV]} / B \text{ [T]}$). The emitted SR spectrum is a continuous distribution extending from the infrared to well above the critical energy $\varepsilon_c$, defined as the energy that divides the total radiated power into equal halves above and below:

$$\varepsilon_c \text{ [keV]} = 0.665\, E^2 \text{ [GeV}^2\text{]}\, B \text{ [T]}$$

This is the single most important parameter characterizing the SR spectrum's damage potential. The universal spectral shape $S(\varepsilon/\varepsilon_c)$, expressible in terms of modified Bessel functions $K_{5/3}$, peaks near $0.3\,\varepsilon_c$ and has useful flux extending to roughly $4\varepsilon_c$ before falling off exponentially.

For a single pass in CEBAF, the beam energy in the highest arc dipoles ranges from approximately 2.2 GeV (first pass, Arc 1) to 10.9 GeV (fifth pass, Arc 9 or Arc A). The arc dipole fields at the highest energies in the present 12 GeV machine are modest ($B \approx$ 0.4--0.6 T for the highest-energy arcs) because the bending radius scales with E/B and is constrained by the existing tunnel geometry. For the proposed FFA arcs, the permanent magnet fields would be in a similar range, determined by the FFA lattice design. Representative critical energies for the current CEBAF arcs include:

| Arc pass | Approx. E (GeV) | Dipole B (T) | $\varepsilon_c$ (keV) | Spectrum extends to ~$4\varepsilon_c$ (keV) |
|----------|-----------------|--------------|----------------------|---------------------------------------------|
| 1st pass | ~2.2 | ~0.5 | ~1.6 | ~6 |
| 3rd pass | ~6.6 | ~0.5 | ~14 | ~58 |
| 5th pass | ~10.9 | ~0.5 | ~40 | ~158 |

At the highest energies, the SR extends well into the hard X-ray regime, with significant photon flux at energies where photoelectric absorption in Nd (Z = 60) and Sm (Z = 62) is extremely efficient.

The total energy radiated per electron per revolution (traversing a full circular orbit of bending radius $\rho$) is given in practical units by the well-known result:

$$U_0 \text{ [keV]} = 88.46\, \frac{E^4 \text{ [GeV}^4\text{]}}{\rho \text{ [m]}}$$

This formula follows from the Larmor power integrated over the orbit, with the relativistic factor $\gamma^4$ giving rise to the $E^4$ scaling. A single arc dipole of length $L$ subtends a bending angle $\theta = L/\rho$, so the fraction of the full revolution represented by that dipole is $\theta/(2\pi) = L/(2\pi\rho)$. The energy lost by each electron in that single dipole is therefore $\Delta U = U_0 \times L/(2\pi\rho)$.

Multiplying by the number of electrons per second passing through the dipole (equal to $I_b / e$, where $I_b$ is the beam current in amperes), and noting that the power is $P = \Delta U \times I_b$ when $\Delta U$ is expressed in eV, the total SR power emitted from a single dipole of length $L$ and bending radius $\rho$ is:

$$P \text{ [kW]} = \frac{88.46}{2\pi}\, \frac{L \text{ [m]}\, I \text{ [A]}\, E^4 \text{ [GeV}^4\text{]}}{\rho^2 \text{ [m}^2\text{]}} = 14.08\, \frac{L \text{ [m]}\, I \text{ [A]}\, E^4 \text{ [GeV}^4\text{]}}{\rho^2 \text{ [m}^2\text{]}}$$

For CEBAF operating CW at $\sim$50 $\mu$A and 10.9 GeV in a 1 m dipole with $\rho \sim 73$ m ($B \approx 0.5$ T), this gives $P \approx$ 1.9 W per meter of arc dipole -- modest individually, but summed over hundreds of meters of arc and all five passes simultaneously present in the tunnel, the total SR power budget is substantial and continuous.

### IIA.2 Photon Interaction Mechanisms at SR Energies

**Simplified concept:** The X-ray photons from synchrotron radiation interact with the magnet material through three processes: at low energies (below ~100 keV in high-Z materials), the photon is completely absorbed by an inner-shell electron (photoelectric effect); at intermediate energies (~100 keV to a few MeV), the photon scatters off electrons transferring only part of its energy (Compton scattering); and at very high energies (>1.022 MeV), the photon can create an electron-positron pair. For the keV-range X-rays from CEBAF SR, the photoelectric effect overwhelmingly dominates, and it is most efficient in the rare-earth elements (Nd, Sm) because the cross-section scales as roughly $Z^{4\text{--}5}$.

**Rigorous treatment:** The three principal photon interaction mechanisms are:

**Photoelectric absorption:** The incident photon is completely absorbed by a bound electron, ejecting a photoelectron with kinetic energy $T_e = h\nu - E_b$, where $E_b$ is the binding energy of the electron shell. The cross-section scales approximately as $\sigma_{pe} \propto Z^{4\text{--}5}/\varepsilon^{3.5}$ for photon energies well above the K-edge, with sharp discontinuities at the absorption edges. For Nd (Z = 60), the K-edge is at $\sim$43.6 keV; for Sm (Z = 62), it is at $\sim$46.8 keV; for Fe (Z = 26), it is at $\sim$7.1 keV. The SR critical energies at the higher CEBAF passes straddle the Nd and Sm K-edges, producing a dramatic increase in absorption efficiency precisely where the photon flux is highest.

Following photoelectric absorption, the atom de-excites through a fluorescence cascade (characteristic X-rays) or Auger electron emission. In high-Z elements, the fluorescence yield is high ($\sim$90% for the K-shell of Nd/Sm), so the absorbed energy is redistributed through secondary characteristic X-rays and their subsequent re-absorption. The net effect is a distributed, volumetric energy deposition concentrated within the first few hundred micrometers of the magnet surface facing the SR fan.

**Compton scattering:** The photon scatters off a quasi-free electron, transferring a fraction of its energy that depends on the scattering angle. The Klein-Nishina cross-section governs this process, and it becomes the dominant interaction for photon energies between roughly 0.1 and 5 MeV in iron-group and rare-earth materials. For the bulk of the CEBAF SR spectrum ($\varepsilon < 100$ keV), Compton scattering is subdominant to photoelectric absorption.

**Pair production:** The photon converts into an electron-positron pair in the Coulomb field of a nucleus. This requires $\varepsilon > 2m_e c^2 = 1.022$ MeV and is therefore entirely irrelevant for the CEBAF SR spectrum, which is confined to the keV range. It is, however, the dominant process for the MeV-to-GeV bremsstrahlung photons discussed in Section II.

The crucial distinction is that SR damage operates through volumetric dose deposition by keV-range photons, not through the nuclear displacement cascade initiated by fast neutrons. The energy deposited per unit mass (absorbed dose, in Gy) by the SR photon field creates electronic excitations, ionization, and localized heating. While individual keV photon interactions do not produce displacement cascades in the same way as MeV neutrons or heavy charged particles, the cumulative absorbed dose from the continuous SR field can be extremely large. Over months of CW operation, the integrated dose at magnet surfaces a few centimeters from the beam orbit can reach the MGy range, where measurable demagnetization has been observed in synchrotron light source studies [48 (APS), 38 (PETRA III)].

### IIA.3 The CW Dose Profile: SR-Dominated Arc Environment vs. Localized Beam Loss

**Simplified concept:** The radiation environment in the arcs differs fundamentally from the linac environment in its geometry and temporal character. Beam losses from halo scraping or cryomodule field emission are localized events that occur at specific points along the machine. Synchrotron radiation, by contrast, is emitted continuously along every bending magnet in every arc on every pass. In a CW machine like CEBAF, this means the permanent magnets in the FFA arcs would be bathed in a steady, geometry-defined photon field 24 hours a day during operation. Moreover, the SR fan is highly directional (emitted in a narrow cone of half-angle $\sim 1/\gamma$ in the vertical plane, but sweeping the full horizontal extent of the arc), meaning specific portions of a magnet array positioned near the beam plane receive a concentrated, steady dose. It is important to note (and Section IIA.5 discusses in detail) that high absorbed photon dose does not necessarily translate directly into magnet demagnetization -- the relationship between the radiation environment and the actual damage mechanism is an open question.

**Rigorous treatment:** Consider the dose rate at a permanent magnet surface located at a transverse distance $d$ from the beam orbit in the arc midplane. The SR photon flux decreases with distance but remains intense within a few centimeters due to the small vertical opening angle ($\sigma_\psi \approx 0.65/\gamma$ at $\varepsilon_c$, which for 10 GeV electrons gives $\sigma_\psi \approx 30$ $\mu$rad -- the fan expands vertically by only $\sim$0.03 mm per meter of drift). For permanent magnets in a Halbach-style FFA arc, the bore radius places the inner face of the magnet blocks only millimeters to centimeters from the beam orbit, directly in the SR fan from upstream dipoles.

This geometry creates a very different dose profile than beam-loss-induced cascades:

The SR dose is distributed longitudinally along the entire arc. It does not depend on beam loss or tuning errors, it is an inherent feature of normal operation. The dose rate at a given point is deterministic and can be calculated analytically from the SR spectrum, beam current, and geometry.

By contrast, neutron production from cryomodule field emission (Section IIA.4) is localized near specific cavities that happen to be active field emitters. It depends on the cavity gradient distribution, surface contamination, and evolves unpredictably as field emitter sites activate or process away.

Over a multi-year operational lifetime, the cumulative SR dose at the inner face of the FFA permanent magnets could substantially exceed the cumulative neutron dose from even the worst cryomodule field emission sites, particularly because the magnets are in the arcs (the SR source) rather than in the linac (the field emission source). The ongoing LDRD study [41,42] has placed samples at both types of locations to directly compare these dose environments.

### IIA.4 Field Emission from SRF Cryomodules: The Competing Neutron Source

**Simplified concept:** Superconducting cavities in CEBAF's linacs can emit electrons from surface defects when the accelerating gradient is high enough. These "dark current" electrons are accelerated through subsequent cavities, gaining up to tens of MeV, and when they strike material they produce bremsstrahlung and photoneutrons through the same electromagnetic cascade described in Section II. This is a well-known operational problem at CEBAF, causing component activation and radiation damage to nearby equipment.

**Rigorous treatment:** Field emission (FE) in superconducting radio-frequency (SRF) cavities occurs when the local electric field at surface defects or contamination sites exceeds the Fowler-Nordheim threshold, enhanced by the geometric field-enhancement factor $\beta_{enh}$ (typically $\beta_{enh} > 50$ is required for meaningful emission current). The emitted electrons are captured by the RF field and accelerated through subsequent cavities, potentially gaining tens of MeV by the time they exit a multi-cavity cryomodule [43].

Upon striking vacuum chamber walls, beam pipes, or other accelerator components, these FE electrons initiate electromagnetic cascades (Section II) that produce bremsstrahlung photons and, above the photoneutron threshold ($\sim$7--11 MeV depending on material), photoneutrons. The radiation field around an active FE cryomodule can be substantial -- the CEBAF NDX monitoring system [44] routinely detects elevated neutron and gamma dose rates near specific cryomodules, and this radiation has caused measurable damage to vacuum valve seals [43] and activation of beamline components.

Key characteristics of the FE radiation field:

It is highly localized near the offending cryomodule(s). Unlike SR, which is distributed along all arc dipoles, FE radiation is concentrated near the specific cavities with active emission sites.

It is variable in time and intensity. FE onset thresholds change as emitter sites activate, process, or are created by contamination. Gradient redistribution (the subject of active machine learning optimization efforts at CEBAF [43,45]) can mitigate FE from specific cavities but may shift the problem elsewhere.

The neutron spectrum from FE cascades includes the full range from fast ($\sim$MeV) to thermal, with the spectral shape determined by the surrounding materials and moderation geometry. The ¹⁰B(n,$\alpha$) channel (Section III.2) is active for the thermal component.

The critical geographic distinction is that the FFA permanent magnets would be located in the recirculating arcs, spatially separated from the linac cryomodules. The neutron dose that reaches the arcs from FE sources in the linacs is attenuated by distance, shielding walls, and inverse-square spreading. By contrast, the SR dose to the arc magnets is local and intense, produced by the beam bending in those very magnets.

### IIA.5 Preliminary Evidence from the Jefferson Lab LDRD Study and the Mechanistic Open Question

The ongoing FFA@CEBAF permanent magnet resiliency study [41,42,46,47] has placed N42EH, N52SH, SmCo33H, and SmCo35 samples at thirty locations throughout the CEBAF enclosure, spanning the range of radiation environments the magnets would encounter [53]. Twenty sites are in the recirculating arcs, distributed as four stacks of five sample plates each (one per energy pass) in both the East and West arc regions. Ten sites are in and around the linac cryomodules (five in each linac, positioned near NDX neutron detectors at specific girder locations), and two are in the low-dose entrance labyrinths (North and South access points) serving as controls. Each sample plate carries four magnet samples -- one of each grade -- in a custom-machined aluminum holder with defined measurement positions for both Helmholtz coil (magnetic moment) and precision Teslameter (3-axis field) characterization.

The study employs two classes of sample plates [47,53]. "Y-plates" carry individual single-magnet samples (one of each grade per plate), providing isolated measurements of each material's radiation response. "N-plates" (NdFeB) and "S-plates" (SmCo) carry paired assemblies in four configurations designed to probe different operating points on the demagnetization curve, connecting directly to the magnetic circuit analysis of Section I.2. The "Alpha" configuration aligns both magnets parallel (fields reinforcing, simulating a radial Halbach wedge with low $|H_{op}|$ and high $P_c$); the "Beta" configuration places the magnets antiparallel (fields opposing, simulating the most-stressed azimuthal wedge position with high $|H_{op}|$ and low effective $P_c$); the "Gamma" configuration places them at 90 degrees; and the "Delta" configuration uses a single magnet with an inert slug placeholder. This range of configurations tests whether the radiation sensitivity is operating-point-dependent, as predicted by the $\Delta T_{crit}$ framework. Note that the Helmholtz coil measurements of the Beta assemblies are unreliable due to the nonlinear (higher-order multipole) character of the antiparallel field, and must be interpreted with caution [54].

Each sample set is accompanied by dosimetry (optically stimulated luminescence area monitors, optichromic rods, and proximity to NDX live-readback detectors) to measure both neutron and gamma doses. Helmholtz coil and precision Teslameter measurements are performed during scheduled accelerator downtimes to track integrated magnetic flux changes. A systematic study [54] has quantified the temperature-dependent measurement offset between the room-temperature lab environment (~22-24 C) and the warmer tunnel enclosure (~31-32 C during operations). The average Helmholtz coil measurement offset due to the ~7-10 C temperature difference is approximately -0.54%, consistent with the known $B_r$ temperature coefficients of the magnet materials (NdFeB 42EH: -0.10 %/C; NdFeB 52SH: -0.11 %/C; SmCo 33H: -0.04 %/C; SmCo 35: -0.04 %/C). This systematic offset must be corrected in the degradation analysis, as it can account for a significant fraction of the apparent raw flux loss.

At the time of the IPAC'25 and NAPAC'25 proceedings [41,55], error analysis was still ongoing and definitive conclusions had not yet been drawn. Relative to pre-deployment lab baselines (measured at room temperature, ~22-24 C), raw Helmholtz coil readings show apparent percent differences ranging from approximately 0 to -2% [54]. However, a substantial portion of this apparent loss is attributable to the measurement temperature difference: the lab baselines were taken at ~22-24 C, while in-tunnel measurements during beam operations are at ~31-32 C. The $B_r$ temperature coefficients predict that the lab-to-tunnel offset alone would produce an apparent raw decrease of approximately -0.7 to -1.1% for NdFeB and -0.3 to -0.4% for SmCo. After accounting for this temperature offset, the residual radiation-induced degradation is estimated at roughly 0 to -1% for the highest-dose locations, though this estimate is sensitive to the accuracy of the temperature correction. In-tunnel Helmholtz measurements taken after the 2025 CEBAF run ended (January 2026, with the tunnel cooled to ~28-29 C per Teslameter probe readings) show values that have increased relative to the beam-on measurements, consistent with the expected temperature-coefficient behavior of the cooler environment. Extracting a definitive radiation signal from these data requires co-located temperature measurements at each Helmholtz reading, which is an identified priority for future measurement campaigns.

**The arc-vs-linac comparison.** Comparing specific sample plates illustrates the emerging pattern. Plate Y-22, positioned at NL Girder 26 near the end of the North Linac, has accumulated an estimated total dose (neutron + gamma) approaching 20 kGy over the course of the 2025 run. Plate Y-25, positioned in the fourth-pass line of the Southeast Arc, has accumulated a much lower estimated total dose of approximately 0.6 kGy. Despite this ~33-fold difference in total dose, the Y-25 arc samples show a comparable rate of apparent change relative to baseline [54]. On both plates, NdFeB shows larger apparent changes than SmCo, consistent qualitatively with both the material ranking predicted by the $\Delta T_{crit}$ framework (Section VIII) and with the larger $|\alpha(B_r)|$ temperature coefficients of the NdFeB grades. The arc samples appear to change more per unit of recorded dose, suggesting either that the radiation at the arc location is more directly incident on the samples (e.g., the SR fan striking the sample plate), that the effective damage per unit dose is higher in the arc environment, that the dosimetry at the two locations is not directly comparable, or some combination of these factors. Disentangling the temperature and radiation contributions to the observed changes is an active area of analysis.

The dosimetry at the arc sites is dominated by gamma radiation; the neutron levels in the arcs are not particularly elevated. The radiation environment in the arcs is defined by the synchrotron radiation from the bending of the beam through dipoles, with associated secondaries, but the specific mechanism by which this environment produces magnet degradation is not yet identified.

**The photon irradiation paradox.** This observation creates a significant tension with the existing literature. Controlled irradiation experiments at the APS by Alderman et al. [48] exposed NdFeB magnets to bending-magnet X-rays (keV-range SR photons, essentially the same type of radiation present in the CEBAF arcs) up to absorbed doses of 280 MRad (2.8 MGy) and found no measurable demagnetization. The same study irradiated samples with $^{60}$Co gamma rays to 700 MRad (7 MGy) -- again, no detectable flux loss. By contrast, electron irradiation at comparable absorbed doses (2.6 MGy of 17 MeV electrons) produced 9% flux loss in NdFeB [Okuda et al., ref. in 37]. Multiple synchrotron light source studies have confirmed this pattern: pure photon irradiation (whether keV X-rays or MeV gammas) does not significantly demagnetize permanent magnets, even at enormous absorbed doses. It is specifically high-energy particle irradiation -- electrons, neutrons, or protons -- that produces demagnetization, because these particles initiate nuclear interactions (electromagnetic cascades, photonuclear reactions) that generate the secondary particles whose nuclear stopping power drives the thermal spike mechanism (Section V).

Asano et al. [8] provided the clearest evidence for this conclusion by comparing experimental demagnetization data from 2-8 GeV electron irradiation at SPring-8 with FLUKA Monte Carlo simulations. They found that "star density" -- the rate of nuclear (hadronic) interactions per unit volume, including both elastic and inelastic scattering by photoneutrons -- was the quantity that correlated with demagnetization. Neither the absorbed photon dose from bremsstrahlung nor the flux of low-energy ($<$1 MeV) photoneutrons correlated with the observed field loss. This analysis established that the damage agent in electron-irradiated magnets is not the electromagnetic energy deposition itself, but the nuclear interaction products generated within the cascade.

**Candidate mechanisms for the arc observations.** Given this context, several hypotheses remain open to explain the LDRD study's preliminary arc-vs-linac pattern:

*Beam halo losses in the arcs:* The recirculating arcs may experience beam halo scraping at aperture restrictions, corrector magnets, or other beamline elements that is more frequent or more energetic than generally appreciated. Scattered beam electrons striking material near the magnet samples would initiate electromagnetic cascades with associated photonuclear reactions, producing precisely the star density that Asano showed correlates with demagnetization. In this scenario, the SR photon field is not the direct damage agent; rather, the arcs happen to be locations where beam loss-driven cascades are concentrated. The gamma-dominated dosimetry is consistent with this, since the bremsstrahlung gamma field from electron-material interactions would dominate the dose budget while the much rarer but more damaging nuclear interaction products (photoneutrons, star density) would be present at levels too low for the dosimetry to distinguish from the gamma background.

*Synergistic thermal effects:* The continuous SR photon field absorbed by the magnets and surrounding material raises the steady-state temperature at the magnet surfaces. While this absorbed dose alone would not cause demagnetization (per the Alderman results), the temperature increase reduces the coercivity margin $\Delta T_{crit}$ (Section VIII), making the magnets more vulnerable to whatever nuclear interactions do occur from the residual beam loss and scattered particle flux. This synergistic mechanism -- SR-driven bulk heating amplifying the damage from a modest rate of nuclear interactions -- could explain why the arc environment produces more degradation than the linac environment, where the neutron flux is higher but the baseline temperature and continuous photon dose are lower.

*Direct SR-generated secondary electrons:* Hard X-ray SR photons absorbed in beamline components (vacuum chambers, flanges, supports) near the magnet samples eject photoelectrons and Compton electrons with energies up to tens of keV. While these secondary electron energies are far below the photonuclear threshold and cannot themselves initiate nuclear cascades, the question of whether dense, continuous bombardment by keV electrons could produce cumulative damage through a mechanism distinct from the nuclear thermal spike model has not been definitively settled experimentally. The controlled APS X-ray irradiation studies placed the magnets directly in the photon beam, which tests the photon interaction mechanism. But the CEBAF arc environment may expose magnets to a secondary electron field that has different characteristics than direct photon irradiation -- for instance, the angular distribution, fluence rate, and spectrum of secondary electrons scattered from nearby surfaces could produce a different effective damage profile.

*Geographic correlation with other radiation sources:* The arc locations may coincidentally be near other radiation sources not captured in the simple "SR vs. FE" dichotomy -- for example, activated beamline components, residual radiation fields from historical beam losses, or scattered radiation from the experimental halls.

The honest summary is that the LDRD study observes a pattern (more degradation in the gamma-dominated arc environment than near the neutron-producing cryomodules), but the mechanism responsible has not been identified. Resolving this question is one of the central scientific goals of the ongoing study, and the BDSIM simulations [42,47] being developed to model the full radiation environment -- including SR, beam halo losses, and secondary particle production -- will be essential for discriminating between these hypotheses.

The BDSIM simulations include SR generation in the arc dipoles and will be used to validate and extend the measured dose data. Once the simulation-measurement agreement threshold is reached, the models will be extrapolated to the higher energies of the proposed FFA@CEBAF upgrade ($>$20 GeV), where the SR critical energy and total power will be substantially higher than at 12 GeV ($\varepsilon_c \propto E^2$, $P \propto E^4$). Critically, the beam halo loss rates in the arcs are also expected to scale with energy and intensity, meaning both the SR photon field and the potential cascade-driven damage would increase in the upgraded machine.

### IIA.6 Implications for FFA Permanent Magnet Design

Regardless of which specific mechanism is ultimately identified as responsible for the arc degradation observations, the LDRD study's preliminary findings motivate several conservative design measures for the FFA@CEBAF magnets:

**Geometric shielding:** SR absorbers (typically copper or lead strips) positioned between the beam vacuum chamber and the magnet bore could intercept the SR fan before it reaches the permanent magnet material. This is standard practice in synchrotron light source insertion devices and could be adapted for the FFA geometry. Even if direct SR photon absorption is not the primary damage mechanism, absorbers reduce the secondary electron and fluorescence photon field generated by SR interactions with beamline components, and reduce the thermal load on the magnet bore surface.

**Material selection:** The SmCo grades retain their advantages in any plausible damage scenario. In a neutron-dominated mechanism, the absence of boron eliminates the $^{10}$B(n,$\alpha$) channel (Section III.2). In a thermally-mediated mechanism (whether from SR heating, secondary electron bombardment, or cascade-driven thermal spikes), the much higher Curie temperature of SmCo ($T_c \approx$ 920 C vs. 312 C for NdFeB) provides a fundamentally larger $\Delta T_{crit}$ margin. And the pinning-controlled coercivity mechanism (Section V.5) is inherently more resistant to thermally-assisted domain reversal than the nucleation-controlled mechanism of NdFeB. The pre-baking (thermal stabilization) effectiveness demonstrated by Bizen et al. [6] remains important for both material families, as it mitigates the most thermodynamically marginal domains regardless of the specific radiation damage pathway.

**Dose monitoring:** Permanent, integrated dosimetry (optichromic sensors, TLDs, or diamond detectors) should be incorporated into the FFA magnet assemblies from the outset. Critically, the dosimetry should be capable of discriminating between gamma and neutron contributions, and should include both surface-mounted and depth-profiled sensors to distinguish bore-surface dose (which may be SR-dominated) from bulk dose (which may have a different spectral character). The LDRD study's experience with OSL area monitors and optichromic rods provides a baseline for dosimetry design.

**Thermal management:** The synergistic mechanism described in Section IIA.5 -- in which SR-driven bulk heating reduces the coercivity margin and amplifies damage from whatever nuclear interactions are present -- argues for active thermal management of the FFA magnets. Temperature monitoring and, potentially, active cooling of the magnet bore surface would provide both a direct reduction in vulnerability and a diagnostic channel for correlating temperature excursions with flux loss events.

**Lifetime modeling:** The existing star-density correlation model developed by Asano et al. [8] for electron-irradiated undulator magnets may not directly apply to the CEBAF arc environment, where the radiation field is not initiated by direct electron impact on the magnets. The LDRD study's primary scientific contribution will be establishing the empirical dose-response relationship specific to the CEBAF mixed-field environment, including whatever combination of SR photons, secondary electrons, scattered beam particles, and photoneutrons constitutes the actual damage field. This empirical calibration, combined with the BDSIM simulations [42,47] that model the complete radiation environment, will form the basis for lifetime predictions at FFA energies.

**Extrapolation to FFA energies:** At the proposed FFA@CEBAF upgrade energies ($>$20 GeV), both the SR parameters and the beam loss characteristics scale unfavorably. The SR critical energy scales as $\varepsilon_c \propto E^2$ (a factor of $\sim$5 increase over the current 5th pass) and the SR power scales as $P \propto E^4$ (a factor of $\sim$16 increase). If the damage mechanism involves beam halo losses, these are also expected to increase with energy and intensity. The BDSIM simulation framework must therefore model all candidate damage sources to provide reliable extrapolations.

---

## III. Neutron Interactions in the Magnet Lattice: PKA Generation and Nuclear Reactions

### III.1 Elastic Scattering: Energy Transfer to Lattice Nuclei

**Simplified concept:** When a neutron collides with an atom in the magnet's crystal lattice, it transfers some of its kinetic energy to that atom, knocking it out of its crystal site. This displaced atom is called a Primary Knock-on Atom (PKA). The maximum energy that can be transferred in a single head-on collision depends on the mass ratio between the neutron and the target atom. Light atoms (like boron, mass 10-11) receive a much larger fraction of the neutron's energy per collision than heavy atoms (like neodymium, mass 144 or samarium, mass 152). However, the total PKA production rate depends not only on the per-collision energy transfer but also on the number density of each element and its scattering cross-section.

**Rigorous treatment:** Photoneutrons propagate into the permanent magnet material -- Nd₂Fe₁₄B or Sm₂Co₁₇ -- where elastic scattering transfers kinetic energy to lattice nuclei, displacing them from their crystallographic sites to create PKAs. For a neutron of mass $m_n \approx 1$ amu and kinetic energy $E_n$ scattering off a nucleus of atomic mass M (in amu), the maximum kinetic energy transferred occurs in a head-on collision:

$$T_{max} = \frac{4 m_n M}{(m_n + M)^2}\,E_n$$

For isotropic scattering in the center-of-mass frame (a reasonable approximation for neutron energies below about 10 MeV), the average energy transfer is half the maximum:

$$\langle T \rangle = \frac{T_{max}}{2} = \frac{2 m_n M}{(m_n + M)^2}\,E_n$$

The maximum-transfer fractions $T_{max}/E_n$ for the relevant isotopes are:

| Nucleus | A | $T_{max}/E_n$ | Role in Nd₂Fe₁₄B | Role in Sm₂Co₁₇ |
|---------|---|--------------|-------------------|-----------------|
| ¹⁰B    | 10 | 33.1% | Present (1 atom/f.u.) | Absent |
| ¹¹B    | 11 | 30.6% | Present (1 atom/f.u.) | Absent |
| ⁵⁶Fe   | 56 | 6.9%  | Dominant (14 atoms/f.u.) | Absent |
| ⁵⁹Co   | 59 | 6.6%  | Absent | Dominant (variable) |
| ¹⁴⁴Nd  | 144 | 2.7% | Present (2 atoms/f.u.) | Absent |
| ¹⁵²Sm  | 152 | 2.6% | Absent | Present (2 atoms/f.u.) |

**Quantitative assessment of dominant PKA source in Nd₂Fe₁₄B:** The total PKA production rate for each sublattice is proportional to the product of number density and macroscopic scattering cross-section. In the Nd₂Fe₁₄B formula unit (68 atoms total: 2 Nd + 14 Fe + 1 B per f.u., with Z = 4 formula units per unit cell), the atomic fractions are: Fe = 82.4%, Nd = 11.8%, B = 5.9%.

The elastic scattering cross-sections at representative fast neutron energies (1 MeV) from ENDF/B-VIII.0 [20] are approximately: $\sigma_{el}$(⁵⁶Fe) $\approx$ 2.5-3 b, $\sigma_{el}$(¹⁰B) $\approx$ 2 b, $\sigma_{el}$(¹⁴⁴Nd) $\approx$ 5-7 b. The macroscopic scattering rate is proportional to $(n_i / n_{total}) \times \sigma_{el,i}$, giving approximate relative contributions: Fe $\approx$ 0.824 $\times$ 2.7 $\approx$ 2.22, Nd $\approx$ 0.118 $\times$ 6 $\approx$ 0.71, B $\approx$ 0.059 $\times$ 2 $\approx$ 0.12. Iron therefore dominates the total elastic scattering PKA production rate by a factor of roughly 3:1 over neodymium and roughly 18:1 over boron, despite boron's higher per-collision energy transfer. The statement that boron is the primary source of energetic PKAs from elastic scattering alone is not quantitatively correct when integrated over the full lattice composition.

### III.2 The ¹⁰B(n,$\alpha$)⁷Li Reaction: A Distinct and Critical Damage Channel

**Simplified concept:** Natural boron contains about 20% of the isotope boron-10 (¹⁰B), which has a remarkable property: it captures slow (thermal) neutrons with an extraordinarily high probability -- about 3,840 barns, which is roughly 1,000 times larger than most other nuclear cross-sections. When ¹⁰B captures a neutron, it splits apart into a helium-4 nucleus (alpha particle) with about 1.47 MeV of energy and a lithium-7 nucleus with about 0.84 MeV. Both of these heavy, charged particles deposit all their energy within a few micrometers of the reaction site, creating an intense, localized burst of damage far more concentrated than anything produced by elastic neutron scattering.

This reaction is a completely separate damage mechanism from elastic PKA production. It has two important consequences: first, the intense localized energy deposition creates a "thermal spike" that can locally exceed the Curie temperature and trigger domain reversal. Second, the helium produced by this reaction accumulates over time in the crystal lattice, eventually forming gas bubbles at grain boundaries that cause permanent, unrecoverable microstructural damage.

This reaction does not occur in SmCo₁₇ magnets, which contain no boron. This is one of the most important material-selection advantages of SmCo for high-fluence environments.

**Rigorous treatment:** A mechanism entirely distinct from elastic scattering is thermal and epithermal neutron capture on ¹⁰B (natural abundance 19.9% of elemental boron). The reaction:

$${}^{10}\text{B} + n \rightarrow {}^{7}\text{Li}^* + \alpha \quad (Q = 2.310~\text{MeV, 94\% branching ratio})$$
$${}^{10}\text{B} + n \rightarrow {}^{7}\text{Li} + \alpha \quad (Q = 2.792~\text{MeV, 6\% branching ratio})$$

has a thermal neutron capture cross-section of 3,840 barns at 0.0253 eV [20]. The dominant (94%) channel produces an excited ⁷Li* nucleus that promptly emits a 478 keV gamma ray; the alpha particle carries approximately 1.47 MeV and the ⁷Li recoil carries approximately 0.84 MeV [20].

This reaction was identified as a significant contributor to NdFeB magnet demagnetization in the experiments of Klaffky et al. at Argonne National Laboratory [21], who isolated the thermal neutron contribution by irradiating magnets at the NIST reactor facility. Their measurements demonstrated substantial remanence loss attributable to the ¹⁰B(n,$\alpha$) reaction, with MCNPX simulations confirming that the high linear energy transfer (LET) alpha particles from this reaction are primarily responsible for the observed demagnetization.

The ¹⁰B(n,$\alpha$) cross-section follows the 1/v law at low energies:

$$\sigma(E_n) \approx \sigma_{th} \sqrt{\frac{E_{th}}{E_n}} = 3840 \sqrt{\frac{0.0253}{E_n[\text{eV}]}} \text{ barns}$$

This means the cross-section is enormous at thermal energies and remains significant throughout the epithermal range. In the moderated neutron flux present in any shielded accelerator environment -- where fast photoneutrons have been scattered to lower energies by the surrounding material -- this reaction becomes highly probable.

The alpha particle (1.47 MeV, charge +2) and ⁷Li recoil (0.84 MeV, charge +3) are both highly ionizing and deposit their energy within track lengths of approximately 3.4 $\mu$m and 1.6 $\mu$m, respectively, in Nd₂Fe₁₄B (estimated from SRIM stopping power calculations). The linear energy transfer (LET) of these particles is approximately 200-400 keV/$\mu$m, which is orders of magnitude higher than the LET of the fast-neutron elastic PKA pathway. This generates an intense, highly localized energy deposition that is physically distinct from the distributed damage produced by elastic cascade events.

The investigation by Simos et al. at Brookhaven National Laboratory [22] provided further experimental confirmation, demonstrating increased demagnetization when the thermal-to-fast neutron ratio was increased, directly implicating the ¹⁰B capture channel.

**Helium accumulation:** At high cumulative fluences, helium gas produced by this reaction accumulates preferentially at grain boundaries and pre-existing voids, driven by the low solubility of helium in metals. The helium atoms are initially deposited as energetic alpha particles that come to rest in the lattice, creating interstitial helium atoms that are highly mobile even at room temperature. These interstitial helium atoms migrate to sinks -- vacancies, grain boundaries, and defect clusters -- where they nucleate nanoscale bubbles. Over long irradiation periods, these bubbles grow by continued helium trapping and vacancy absorption, eventually producing intergranular pressurization, swelling, and embrittlement that constitute permanent, irrecoverable microstructural damage [23].

### III.3 Other Nuclear Reactions in the Magnet Lattice

In addition to elastic scattering and the ¹⁰B(n,$\alpha$) reaction, several other neutron-induced nuclear reactions occur in the magnet material, particularly at the higher neutron energies present in the CEBAF environment:

**Inelastic scattering (n,n'):** At neutron energies above the first excited state of the target nucleus (typically 0.5-2 MeV for the relevant isotopes), inelastic scattering becomes important. The neutron excites the target nucleus, which de-excites by gamma emission, and the scattered neutron emerges with reduced kinetic energy. The recoiling nucleus receives energy from both the scattering kinematics and the nuclear excitation, contributing to PKA production. Inelastic scattering cross-sections for iron are significant (approximately 1-2 barns) at energies of 1-10 MeV [20].

**Threshold reactions:** At neutron energies above several MeV, (n,p) and (n,$\alpha$) reactions on iron, neodymium, and cobalt nuclei become possible. These produce energetic charged particles that contribute to localized damage. In Sm₂Co₁₇, the ⁵⁹Co(n,$\alpha$) reaction has a threshold of approximately 1 MeV and produces alpha particles that, while less frequent than the ¹⁰B(n,$\alpha$) reaction in NdFeB, still contribute to damage at high fluences.

---

## IV. Primary Radiation Damage: The Displacement Cascade

### IV.1 From PKA to Displacement Cascade

**Simplified concept:** When a lattice atom is struck and knocked out of its crystal site (becoming a PKA), it doesn't just create a single vacancy. The PKA collides with neighboring atoms, which collide with their neighbors, creating a cascade of displaced atoms that spreads through the crystal like a tiny, sub-nanosecond explosion. During this cascade, there is a brief phase where the local region looks almost liquid -- atoms are violently displaced in all directions, the local "temperature" (kinetic energy per atom) far exceeds the melting point, and the crystal order is momentarily destroyed. This is the "thermal spike" or "heat spike" phase. After about 1-10 picoseconds, the cascade region rapidly cools and re-crystallizes, but not perfectly -- some atoms don't return to their correct positions, leaving behind permanent point defects (vacancies and interstitials) that constitute the lasting structural damage.

**Rigorous treatment:** The physics of displacement cascades has been extensively studied through molecular dynamics (MD) simulations, as reviewed comprehensively by Nordlund et al. [24, 25]. A displacement cascade proceeds through three distinct temporal phases:

**Phase 1: Ballistic collisions (0-0.1 ps).** The PKA undergoes a series of binary nuclear collisions with lattice atoms, transferring energy through a branching tree of recoil events. During this phase, the number of displaced atoms approximately follows the predictions of the Norgett-Robinson-Torrens (NRT) model [26]. The spatial extent of the cascade grows rapidly.

**Phase 2: Thermal spike (0.1-1 ps).** As the cascade energy is distributed among an increasing number of atoms, the mean energy per atom drops below the displacement threshold but remains far above thermal equilibrium. The cascade region enters a state analogous to a superheated liquid -- the local atomic kinetic energies correspond to temperatures far exceeding the melting point (for iron, the cascade "temperature" can transiently reach 5,000-10,000 K in the core). During this phase, extensive atomic rearrangement occurs. MD simulations show that the peak number of displaced atoms during the thermal spike is roughly consistent with the NRT prediction, but subsequent recombination during cooling dramatically reduces the surviving defect count [24, 25].

**Phase 3: Quenching and recombination (1-10 ps).** The thermal spike region rapidly cools as energy dissipates into the surrounding lattice through electron-phonon coupling and phonon propagation. As the region re-crystallizes from the periphery inward, the majority of displaced atoms return to lattice sites -- but not necessarily their original sites. The surviving defect count is only approximately one-third of the NRT prediction in metals [25], while the number of atoms that have exchanged positions (atomic mixing) is approximately 30 times larger than the DPA value [25].

This discrepancy between the NRT prediction and actual defect survival was quantified by Nordlund et al. [25], who proposed the "athermal recombination corrected DPA" (arc-DPA) as a more physically realistic measure:

$$N_d^{arc\text{-}dpa} = \begin{cases} 0 & T_{dam} < 2E_d/0.8 \\ c_{arc} \cdot N_d^{NRT} \cdot (T_{dam})^{b_{arc}} & T_{dam} \geq 2E_d/0.8 \end{cases}$$

where $c_{arc}$ and $b_{arc}$ are material-dependent constants determined from MD simulations. For iron, the defect production efficiency $\xi_{arc} \equiv N_d^{arc}/N_d^{NRT} \approx 0.29$ at cascade energies above about 1 keV [25].

### IV.2 The Lindhard Partition Function and Damage Energy

**Simplified concept:** Not all the kinetic energy of a displaced atom goes into creating further displacements. Some of the energy is dissipated through electronic excitation -- the PKA ionizes the atoms it passes by, losing energy to the electron cloud in a process analogous to friction. This electronic energy loss heats the electrons but does not displace atoms from their lattice sites. The Lindhard partition function tells us what fraction of the PKA's initial energy is available for creating atomic displacements (the "damage energy") versus being lost to electronic excitation. For heavy atoms like neodymium at keV energies, most of the energy goes into nuclear collisions; for light atoms like boron at higher energies, a larger fraction is lost to electronic stopping.

**Rigorous treatment:** For a PKA with initial kinetic energy T, the total energy is partitioned between electronic stopping (ionization, creating no permanent lattice damage) and nuclear stopping (lattice displacements). The damage energy $T_{dam}$ -- the fraction contributing to atomic displacements -- is calculated using the Lindhard partition function L(T) [27]:

$$T_{dam} = T \cdot L(T)$$

The Lindhard partition function is given by:

$$L(\epsilon) = \frac{1}{1 + F_L(3.4008\epsilon^{1/6} + 0.40244\epsilon^{3/4} + \epsilon)}$$

where $\epsilon = T / E_L$ is a reduced energy with $E_L = 30.724 Z_1 Z_2 (Z_1^{2/3} + Z_2^{2/3})^{1/2} (A_1 + A_2)/A_2$ eV, and $F_L$ is a constant approximately equal to 0.1337 $Z_1^{1/6} (Z_1/A_1)^{1/2}$ for self-ion recoils [27]. For iron PKAs in Nd₂Fe₁₄B at energies of 1-10 keV (typical of the 12 GeV CEBAF neutron spectrum), approximately 70-85% of the PKA energy goes into nuclear stopping (displacement damage).

### IV.3 The NRT Standard: Displacements Per Atom

Structural damage is then quantified using the Norgett-Robinson-Torrens (NRT) standard [26], which gives the number of displaced atoms $N_d$ produced by a single PKA:

$$N_d^{NRT} = \begin{cases} 0 & T_{dam} < E_d \\ 1 & E_d \leq T_{dam} < 2E_d/0.8 \\ \frac{0.8\,T_{dam}}{2\,E_d} & T_{dam} \geq 2E_d/0.8 \end{cases}$$

where $E_d$ is the threshold displacement energy -- the minimum energy required to permanently displace a lattice atom from its site. $E_d$ is sublattice-dependent and direction-dependent within the crystal. For the materials under study:

**Nd₂Fe₁₄B sublattice displacement energies:**
- Iron sublattice: $E_d \approx 40$ eV (ASTM E693 recommended value for BCC iron [28]; the actual value in the tetragonal Nd₂Fe₁₄B crystal structure may differ and is not well characterized experimentally)
- Neodymium sublattice: $E_d \approx 20-25$ eV (limited experimental data; estimated from systematics of rare-earth displacement thresholds)
- Boron sublattice: $E_d \approx 20-25$ eV (estimated; boron sits in a trigonal prismatic cage within the Nd₂Fe₁₄B structure, and its displacement threshold is not well established independently)

**Sm₂Co₁₇ displacement energies:**
- Cobalt sublattice: $E_d \approx 40$ eV (analogous to iron; limited experimental data specific to the Sm₂Co₁₇ rhombohedral structure)
- Samarium sublattice: $E_d \approx 20-25$ eV (estimated from rare-earth systematics)

The displacement damage is accumulated as a Displacements Per Atom (DPA) dose over the full operational fluence. It is important to recognize that the NRT-DPA is a standardized radiation exposure metric, not an exact count of surviving defects. The actual surviving defect count is approximately one-third the NRT value in metals, as discussed in Section IV.1 [25].

---

## V. The Microscopic Thermal Spike and Radiation-Induced Domain Nucleation

### V.1 The Thermal Spike Model in Permanent Magnets

**Simplified concept:** The key mechanism by which radiation actually reduces a magnet's field strength works through the thermal spike created by a displacement cascade (or by the ¹⁰B capture reaction products). In the nanometer-scale, picosecond-duration hot zone of a thermal spike, the local "temperature" can transiently exceed the Curie temperature of the magnetic material -- the temperature above which the material loses its ferromagnetic order. Within this temporarily non-magnetic nano-volume, the crystal lattice itself remains intact, but the magnetic ordering is momentarily destroyed. When the region cools back down (in a few picoseconds), the magnetic moments must re-establish their orientation. If there is a strong demagnetizing field present at that location -- as there is in the stressed azimuthal wedges of a Halbach array -- the moments preferentially re-align with the local demagnetizing field rather than returning to their original orientation. A reversed magnetic domain has been nucleated. This is a one-way ratchet: each thermal spike that is energetic enough and located in a sufficiently stressed region permanently flips a tiny volume of the magnet, and these individually tiny losses accumulate over the operational lifetime of the accelerator.

**Rigorous treatment:** The thermal spike model for radiation-induced demagnetization was proposed and developed by Bizen et al. [5, 7] based on their extensive experimental studies at SPring-8. The model posits that the PKA (or the alpha/Li recoil from ¹⁰B capture) deposits its nuclear stopping power into the surrounding lattice, creating a transient thermal excursion in a nanometer-scale volume.

Following the nomenclature established by Bizen et al. [7], the thermal spike creates concentric zones around the PKA track:

- **Zone 1 (core):** A region of radius approximately 1-2 nm where the local atomic kinetic energies correspond to temperatures exceeding the melting point. In this zone, if it exists for a given PKA energy, the crystal may momentarily enter a liquid-like state, though for the PKA energies typical of photoneutron recoils (hundreds of eV to tens of keV for iron PKAs), this molten core may not form in every cascade.

- **Zone 2 (above $T_c$):** A surrounding shell where the local temperature transiently exceeds the Curie temperature ($T_c$ = 585 K for Nd₂Fe₁₄B, approximately 1190 K for Sm₂Co₁₇ [3]). Within this zone, ferromagnetic order is lost and the magnetization drops to zero, but the crystal lattice structure is preserved.

- **Zone 3 (reduced $H_{cJ}$):** An outer shell where the temperature is elevated above ambient but below $T_c$. In this zone, the intrinsic coercivity is reduced according to its temperature coefficient but not eliminated. Domain reversal can still occur here if the reduced coercivity falls below the local demagnetizing field.

This model was supported by the molecular dynamics simulations of Samin et al. [29, 30], who used MD to establish the length and time scales of the thermal spike process in NdFeB. Their simulations confirmed that thermal spikes occur on a scale of nanometers in radius and picoseconds in duration, consistent with the Bizen hypothesis. Density functional theory (DFT) calculations by the same group showed that point defects (vacancies and interstitials) in the Nd₂Fe₁₄B lattice alter the local magnetic moment, providing a secondary, persistent mechanism for magnetization reduction beyond the transient thermal spike domain reversal [29].

### V.2 The Temperature-Dependent Coercivity

The intrinsic coercivity decreases with temperature. Over the range relevant to thermal spike analysis (from ambient to $T_c$), the decrease is approximately linear and characterized by the reversible temperature coefficient $\beta$:

$$H_{cJ}(T) = H_{cJ}(T_0)\left[1 + \beta(T - T_0)\right]$$

Because $\beta$ is negative for all rare-earth permanent magnets, any transient temperature increase reduces $H_{cJ}$. The coercivity vanishes at $T_c$ by definition -- above the Curie temperature, the material is paramagnetic and has no coercivity.

### V.3 The Radiation-Induced Domain Nucleation Criterion

Integrating the microscopic thermal physics with the macroscopic vector field analysis of Section I, the criterion for radiation-induced domain reversal at a given lattice site is:

$$H_{cJ}(T_{local}) < |H_{op}(\vec{r})|$$

If the thermal spike transiently reduces the local coercivity $H_{cJ}(T_{local})$ below the magnitude of the opposing operating field $|H_{op}|$ at that lattice site, the magnetic spins in that nano-volume are no longer pinned by magnetocrystalline anisotropy and can rotate freely. As the volume quenches on a picosecond timescale, the spins realign preferentially with the local **H**_tot direction, which in a Halbach azimuthal wedge is anti-parallel to the original magnetization. A reversed magnetic domain has been nucleated and locked into the lattice.

The critical temperature rise needed to trigger this reversal is:

$$\Delta T_{crit} = \frac{H_{cJ}(T_0) - |H_{op}(\vec{r})|}{|\beta| \cdot H_{cJ}(T_0)}$$

A larger $\Delta T_{crit}$ means a more radiation-resistant operating condition: a higher-energy PKA (or a ¹⁰B capture event producing more localized energy deposition) is required to create a thermal spike of sufficient intensity.

### V.4 Role of the Grain Boundary Microstructure in Nd₂Fe₁₄B

**Simplified concept:** Sintered NdFeB magnets are not single crystals -- they are made of many small crystalline grains, each a few micrometers in size, cemented together by a thin (1-5 nm) neodymium-rich intergranular phase. This grain boundary phase has much weaker magnetic properties than the bulk Nd₂Fe₁₄B grains; it is often amorphous or nanocrystalline and has a much lower coercivity. The grain boundaries are the weak points where reversed magnetic domains are most easily nucleated, both thermally and by radiation. This is why the coercivity mechanism of NdFeB magnets is described as "nucleation-controlled" -- once a reversed domain nucleates at a grain boundary, it can expand rapidly through the grain interior.

**Rigorous treatment:** In sintered Nd₂Fe₁₄B, the highest local demagnetizing fields occur at grain boundaries and triple junctions between misoriented grains [31]. The intergranular phase in sintered NdFeB is a Nd-rich amorphous or nanocrystalline layer with a substantially lower coercivity than the Nd₂Fe₁₄B bulk grain. This phase serves as the preferential nucleation site for reversed magnetic domains under both thermal and radiation excitation.

The coercivity of sintered Nd₂Fe₁₄B is nucleation-controlled: the macroscopic coercivity is determined not by the magnetocrystalline anisotropy of the bulk Nd₂Fe₁₄B phase (which would give $\mu_0 H_A \approx 7.3$ T at room temperature [3]) but by the ease with which reversed domains nucleate at defects, primarily at the Nd-rich grain boundary phase. The Brown paradox -- the observation that the measured coercivity of sintered NdFeB is typically only 20-30% of the anisotropy field -- reflects this nucleation limitation [3, 32].

The macroscopic vector field analysis of $H_{op}(\vec{r})$ from Section I thus couples directly to the microstructure: the highest $|H_{op}|$ exists at azimuthal Halbach wedge boundaries, and within those wedges, thermal spikes at grain-boundary sites are the most likely initiation points for flux loss.

### V.5 The Pinning-Controlled Coercivity of Sm₂Co₁₇ and Its Radiation Implications

**Simplified concept:** SmCo₁₇ magnets maintain their coercivity through a fundamentally different mechanism than NdFeB magnets. Instead of nucleation at grain boundaries, SmCo₁₇ uses domain wall pinning: the crystal contains a fine-scale internal microstructure of alternating Sm₂Co₁₇ cells and SmCo₅ cell boundaries, and moving a magnetic domain wall through this microstructure requires overcoming energy barriers at each cell boundary. This "friction" against domain wall motion is what gives SmCo₁₇ its coercivity. Radiation damage must not just nucleate a reversed domain -- it must also unpin the domain walls from their pinning sites. This is inherently more difficult because the pinning sites are distributed throughout the bulk of the material, not concentrated at vulnerable grain boundaries. This is one of the fundamental reasons why Sm₂Co₁₇ magnets show superior radiation resistance compared to NdFeB.

**Rigorous treatment:** The coercivity mechanism of Sm₂Co₁₇-type magnets is fundamentally different from the nucleation-controlled mechanism of sintered Nd₂Fe₁₄B. In precipitation-hardened Sm₂Co₁₇ magnets, the coercivity is controlled by domain wall pinning at the boundaries between the rhombohedral 2:17R cell phase (Sm₂Co₁₇) and the hexagonal 1:5 cell boundary phase (SmCo₅) [33, 34, 35].

The cellular nanostructure of Sm₂Co₁₇-type magnets consists of [33, 34]:

- **2:17R cells:** Diamond-shaped regions of the Sm₂(Co,Fe,Cu,Zr)₁₇ phase, typically 60-120 nm in size, which form the matrix and carry the majority of the magnetization.

- **1:5H cell boundaries:** Thin (5-10 nm) continuous walls of the SmCo₅-type phase enriched in copper, which surround each cell. The difference in domain wall energy between the 2:17R cells and the 1:5H boundaries creates the energy barriers that pin domain walls.

- **Zr-rich platelets:** Thin lamellar precipitates (approximately the Z-phase, of composition Sm₂Zr₃Co₁₅ or similar) that lie parallel to the basal plane and provide additional pinning.

The pinning field -- the applied field required to force a domain wall past a cell boundary -- is determined by the gradient of the domain wall energy across the cell-boundary interface [35]:

$$H_{pin} \propto \frac{\Delta \gamma}{\gamma_0}$$

where $\Delta \gamma$ is the difference in domain wall energy between the 2:17R cell interior and the 1:5H boundary, and $\gamma_0$ is the domain wall energy of the 2:17R phase. This gradient depends on differences in the magnetocrystalline anisotropy constant and exchange stiffness between the two phases, both of which are controlled by the copper and iron partitioning achieved during the complex heat treatment [34].

The radiation resistance advantage of the pinning-controlled mechanism is that:

1. Domain reversal requires not just local nucleation but propagation of domain walls through the pinning field landscape. A thermal spike that nucleates a small reversed region cannot expand unless the spike energy is also sufficient to overcome the pinning barriers at surrounding cell boundaries.

2. The pinning sites are distributed throughout the bulk of each grain on a 60-120 nm length scale, not concentrated at grain boundaries as in NdFeB. The spatial density of critical nucleation sites is therefore fundamentally different.

3. The Curie temperature of Sm₂Co₁₇ ($T_c \approx$ 920 C, or 1193 K [3]) is approximately three times that of Nd₂Fe₁₄B (585 K). The thermal spike must therefore reach much higher temperatures to enter the zone where $H_{cJ}$ is reduced below $|H_{op}|$.

This mechanistic analysis -- that the domain wall pinning mechanism provides superior radiation resistance to the nucleation mechanism -- was advanced by Luna et al. [36] and has been supported by the comparative irradiation studies reviewed in [37].

### V.6 Magnetization Reversal vs. Gradual Demagnetization: The SACLA Discovery

**Simplified concept:** Until 2016, radiation-induced flux loss in permanent magnets was assumed to be a gradual, distributed process: individual thermal spikes randomly flip small domains throughout the magnet volume, and these individually tiny losses accumulate slowly over time. The SACLA X-ray free electron laser facility in Japan discovered something qualitatively different. In one of their undulators, they found that the flux loss was caused by coherent magnetization reversal -- large, millimeter-scale regions of the magnet where the entire magnetization had flipped direction uniformly, rather than being randomly scrambled. This is a much more damaging process: instead of losing a small fraction of one percent from many tiny randomly reversed domains, a single coherent reversal event over a macroscopic region can produce a large, localized flux loss in one step. The distinction matters enormously for predicting whether degradation will be gradual and manageable or sudden and catastrophic.

**Rigorous treatment:** Bizen, Tanaka, and collaborators reported in 2016 [10] that an unexpectedly large flux loss observed in a SACLA undulator was caused not by the expected gradual accumulation of individually reversed nano-domains, but by homogeneous magnetization reversal extending over wide areas of the permanent magnet blocks. By extracting and individually characterizing magnets from the affected undulator, they demonstrated that the flux loss distribution was highly non-uniform -- strongly localized to the upstream end of the undulator (closest to the electron beam injection point) and concentrated in specific magnets rather than distributed uniformly.

The physical mechanism they proposed is an extension of the thermal spike domain nucleation model (Section V.3), but with a critical additional step: once a reversed domain nucleates in a sufficiently stressed region (high $|H_{op}|$, low $\Delta T_{crit}$), the reversed domain can propagate rapidly through a macroscopic volume if the surrounding material is also near its stability threshold. In the nucleation-controlled NdFeB system, where domain walls move freely once nucleated (the coercivity is determined by nucleation, not propagation), a single nucleation event at a grain boundary can trigger an avalanche of reversal through the grain interior and potentially into neighboring grains if the intergranular coupling is sufficient.

This discovery has important implications for the CEBAF environment:

First, the estimated flux-loss rate observed at SACLA was substantially higher than previously reported in the literature for comparable absorbed doses, suggesting that the magnetization reversal mechanism is intrinsically more efficient at converting radiation energy into flux loss than the gradual domain-by-domain process assumed in earlier models.

Second, the strong spatial localization of the damage (concentrated at the upstream end) means that position-averaged dose measurements may severely underestimate the damage at the most-irradiated locations. This is directly relevant to the LDRD study's dosimetry interpretation, where the relationship between the dosimeter location and the actual dose at the magnet surface may not be trivial.

Third, the magnetization reversal mechanism is expected to be less prevalent in the pinning-controlled Sm$_2$Co$_{17}$ system, where domain wall propagation is impeded by the cellular microstructure even after a reversed domain nucleates (Section V.5). This provides an additional physics-based argument for the superior radiation resistance of the SmCo grades beyond the higher $T_c$ and $\Delta T_{crit}$ advantages.

---

## VI. Material Properties of the Four Specific Grades

The four grades under study span two distinct material systems. Their key thermomagnetic parameters, which directly enter the nucleation criterion of Section V.3, are summarized below. All values are from standard manufacturer specifications and published literature; individual lot properties must be verified against the specific supplier's datasheet.

### VI.1 N42EH (Nd₂Fe₁₄B, Extra-High Coercivity Grade)

The "EH" (Extra High) coercivity designation is achieved through partial substitution of dysprosium (Dy) on the neodymium sublattice, forming (Nd,Dy)₂Fe₁₄B. The Dy-Fe exchange interaction is antiferromagnetic: the Dy 4f magnetic moment couples antiparallel to the Fe 3d moment, which increases the magnetocrystalline anisotropy (and hence $H_{cJ}$) but reduces the net magnetic moment (and hence $B_r$) [3].

| Parameter | Value |
|-----------|-------|
| $B_r$ | 1.29-1.32 T |
| $(BH)_{max}$ | 318-334 kJ/m³ (40-42 MGOe) |
| $H_{cJ}$ (min) | 25-30 kOe (1,990-2,388 kA/m); verify against specific supplier datasheet |
| $\alpha(B_r)$ | -0.09 to -0.10%/C (vendor-specific: -0.10%/C per Allstar Magnetics specification [54]) |
| $\beta(H_{cJ})$ | approximately -0.55%/C (Dy substitution reduces magnitude vs. undoped NdFeB) |
| $T_c$ (Nd₂Fe₁₄B) | 585 K (312 C) [3] |
| Max operating temp. | 200 C |

In the Halbach array, N42EH is the NdFeB grade most suitable for high-stress azimuthal wedge positions. Its elevated $H_{cJ}$ increases the margin in the nucleation criterion ($\Delta T_{crit}$ is larger), and the reduced $|\beta|$ from Dy-doping means the local coercivity is less sensitive to thermal spikes.

### VI.2 N52SH (Nd₂Fe₁₄B, Super-High Coercivity Grade)

The N52 designation requires the maximum achievable remanence, which demands near-perfect crystallographic grain alignment and minimal Dy content (since Dy reduces $B_r$). The SH coercivity specification simultaneously demands meaningful Dy doping. N52SH therefore represents a material at the practical limit of simultaneous optimization, and commercial availability at this grade is limited. Its high $B_r$ makes it desirable for maximum flux-on-axis, but the constraints of the SH coercivity designation leave it with lower $H_{cJ}$ than N42EH.

| Parameter | Value |
|-----------|-------|
| $B_r$ | 1.42-1.48 T |
| $(BH)_{max}$ | 398-414 kJ/m³ (50-52 MGOe) |
| $H_{cJ}$ (min) | 20-25 kOe (1,592-1,990 kA/m); verify against specific supplier datasheet |
| $\alpha(B_r)$ | -0.11%/C |
| $\beta(H_{cJ})$ | approximately -0.58%/C |
| $T_c$ (Nd₂Fe₁₄B) | 585 K (312 C) [3] |
| Max operating temp. | 150 C |

In high-stress Halbach wedge positions, the reduced $H_{cJ}$ margin makes N52SH more vulnerable to radiation-induced demagnetization than N42EH despite the higher $B_r$. N52SH is appropriate for low-stress radial wedge positions where the $|H_{op}|$ is smaller.

### VI.3 SmCo33H and SmCo35 (Sm₂Co₁₇ Phase)

At energy products of 33 and 35 MGOe, both grades are firmly in the Sm₂Co₁₇ phase (the 2-17 phase); the SmCo₅ (1-5) phase is limited to approximately 24-26 MGOe maximum. This distinction is essential: the temperature coefficients, Curie temperature, and radiation resistance of Sm₂Co₁₇ and SmCo₅ differ substantially. The SmCo₅ intrinsic coercivity temperature coefficient $\beta(H_{cJ}) \approx -0.40\%$/C is nearly twice as large in magnitude as that of Sm₂Co₁₇; any analysis referencing generic "SmCo" without specifying the phase is incomplete.

| Parameter | SmCo33H | SmCo35 |
|-----------|---------|--------|
| $B_r$ | 1.10-1.15 T | 1.13-1.18 T |
| $(BH)_{max}$ | 255-271 kJ/m³ (32-34 MGOe) | 270-287 kJ/m³ (34-36 MGOe) |
| $\alpha(B_r)$ | -0.03 to -0.04%/C (vendor-specific: -0.04%/C [54]) | -0.03 to -0.04%/C (vendor-specific: -0.04%/C [54]) |
| $\beta(H_{cJ})$ | -0.20 to -0.25%/C | -0.20 to -0.25%/C |
| $T_c$ (Sm₂Co₁₇) | approximately 920 C (1193 K) | approximately 920 C (1193 K) |
| Max operating temp. | 300-350 C | 300 C |

### VI.4 Remanence Temperature Coefficient

For integrated flux-on-axis calculations in accelerator multipoles, the remanence temperature coefficient $\alpha(B_r)$ is as important as the coercivity coefficient. Any spatially or temporally non-uniform temperature distribution across the magnet volume -- whether from beam heating or radiation-induced phonon generation -- will produce a corresponding gradient in $B_r$, directly affecting the multipole field quality. The NdFeB grades (N42EH, N52SH) have $|\alpha(B_r)|$ approximately 2.5 to 3 times larger than the SmCo grades, making them substantially more sensitive to thermal gradients.

The practical significance of these temperature coefficients for the LDRD study has been directly measured [54]. Comparing Helmholtz coil and Teslameter measurements of unexposed control samples at lab temperature (~22-24 C) versus the CEBAF tunnel enclosure temperature (~31-32 C during beam operations) showed that the ~7-10 C temperature difference produces an average measurement offset of -0.54%, with NdFeB single samples showing offsets close to -1% (consistent with $|\alpha(B_r)| \approx 0.10$-0.11 %/C) and SmCo samples showing smaller offsets (consistent with $|\alpha(B_r)| \approx 0.04$ %/C). This systematic offset is fully reversible and must be corrected in the radiation degradation analysis to avoid conflating thermal and radiation-induced effects.

---

## VII. Radiation Damage Regimes, Recovery, and the CW-Specific Environment

### VII.1 Flux Loss Regimes

**Simplified concept:** Radiation-induced flux loss occurs through two fundamentally different mechanisms, and it is critical to distinguish them because their practical consequences are entirely different:

- **Regime 1 ("recoverable" flux loss):** Individual thermal spike events flip tiny magnetic domains. The crystal structure is undamaged -- only the magnetic alignment has changed. This is like flipping one tile in a mosaic: the tile itself is fine, just facing the wrong way. The magnet can be restored to its original state by re-magnetization (applying a strong magnetizing pulse).

- **Regime 2 ("permanent" structural damage):** At very high cumulative radiation doses, the crystal lattice itself is progressively destroyed. Frenkel pair defects accumulate, dislocation loops form, and (in NdFeB) helium bubbles from ¹⁰B capture grow at grain boundaries. The magnetocrystalline anisotropy that provides coercivity is degraded at the atomic level. This damage cannot be recovered by re-magnetization alone; the material's intrinsic magnetic properties have been permanently degraded.

In practice at CEBAF, Regime 1 is the primary operational concern, because it occurs at much lower fluences than Regime 2 and produces measurable flux degradation that directly affects accelerator performance. Regime 2 becomes relevant for magnets operating at the highest fluence locations over multi-year timescales.

**Rigorous treatment:**

**Regime 1 -- Thermally-induced domain reversal** (Section V.3 mechanism). Flux loss is produced by the nucleation of reversed magnetic domains in thermally spiked nano-volumes where $H_{cJ}(T_{local}) < |H_{op}|$. This flux loss is recoverable by re-magnetization: the reversed domains represent a local free-energy minimum reachable by thermal activation, and driving the magnet through a re-magnetizing field cycle restores the original macroscopic state. The process is not thermodynamically reversible in the strict sense -- domain wall motion and nucleation are dissipative, irreversible processes that generate entropy -- but the flux loss is recoverable in practical engineering terms.

The dose range for Regime 1 onset is typically characterized by absorbed doses of 10⁴ to 10⁵ Gy leading to approximately 1% flux loss in NdFeB undulator magnets, as established by operational experience at multiple synchrotron radiation facilities [5, 7, 38]. Equivalently, irradiation studies with high-energy electron beams have shown that exposure to approximately 10¹⁴ to 10¹⁵ electrons (at energies of 2-8 GeV) causes comparable flux loss [5, 8, 9].

**Regime 2 -- Cumulative structural damage.** At high cumulative neutron fluences, the accumulation of NRT displacements (Frenkel pair defects, dislocation loops, stacking fault tetrahedra) and helium gas precipitates from ¹⁰B capture irreversibly destroys the magnetocrystalline anisotropy at and near grain boundaries. This permanently reduces $H_{cJ}(T_0)$ in the defect zones, and the resulting flux loss cannot be recovered by re-magnetization at room temperature. Only elevated-temperature annealing (with subsequent re-magnetization) could partially restore properties, and full recovery is not achievable for severely damaged material.

The fluence threshold for the onset of Regime 2 structural damage in NdFeB depends strongly on the neutron energy spectrum. The frequently cited threshold of approximately 10¹⁵ n/cm² comes primarily from the fast neutron irradiation experiments of Brown and Cost [39] and subsequent studies, but this value refers to fast neutron fluence (typically E_n > 0.1 MeV) and cannot be directly applied to a mixed-spectrum environment without spectral weighting. In the mixed neutron field at CEBAF, where a significant thermal and epithermal population exists, the ¹⁰B(n,$\alpha$) reaction provides an additional structural damage pathway (via helium accumulation) that does not have a direct analogue in fast-neutron-only irradiation studies.

### VII.2 The Effect of Thermal Stabilization (Pre-Baking)

**Simplified concept:** A remarkably effective technique for improving radiation resistance is to thermally stabilize (pre-bake) the magnets before installation. The magnet is heated to a temperature moderately above its planned operating temperature (but far below its Curie point) for an extended period, typically 24 hours. This process intentionally demagnetizes the weakest, most marginally stable magnetic domains -- the ones that were sitting closest to the knife-edge of stability on the demagnetization curve. After baking and cooling, only the more robustly magnetized domains remain. The surviving magnetization is slightly lower than the original, but the magnet is dramatically more resistant to further demagnetization from radiation, because all the easy-to-flip domains have already been flipped.

**Rigorous treatment:** The effect of thermal stabilization (pre-baking) on the radiation resistance of NdFeB magnets was systematically investigated by Bizen et al. [6]. By baking Nd₂Fe₁₄B magnets at temperatures between 142 C and 240 C for 24 hours before irradiation, they demonstrated that all thermally stabilized magnets showed higher resistance to irradiation with 2.0 GeV electrons than unbaked samples. The unbaked samples showed non-linear, drastic demagnetization with increasing electron exposure, while the baked samples exhibited a linear demagnetization curve with a rate substantially lower than the unbaked magnets [6].

The physical mechanism is the removal of marginally stable reversed domain nuclei during the baking process. These are nano-scale regions, typically at grain boundaries, where the operating point is closest to the knee of the demagnetization curve. During baking, the thermally reduced coercivity allows these marginal regions to demagnetize under the self-demagnetizing field. Upon cooling, the remaining magnetization consists entirely of domains with adequate stability margins, effectively "immunizing" the magnet against the lowest-energy thermal spike events.

This is directly relevant to the FFA@CEBAF design: specifying thermal stabilization of all permanent magnets before installation is a first-line defense against radiation-induced flux loss, with negligible cost in remanence (typically 1-3% reduction from pre-baking at appropriate temperatures).

### VII.3 The CW-Specific Operating Hazard at CEBAF

The continuous-wave nature of CEBAF is directly relevant to the demagnetization risk. Unlike pulsed accelerators -- where magnet irradiation occurs in discrete, short bursts with extended quiescent periods between machine pulses -- CEBAF imposes a continuous, uninterrupted photoneutron flux on the magnet lattice during beam operation. There is no inter-pulse interval during which partial relaxation of marginally-nucleated domain walls could occur.

The magnet operates perpetually at elevated $|H_{op}|$ in the most stressed Halbach wedge positions, with no temporal relief from the radiation environment. Thermal management is therefore especially important: any systematic beam-heating-induced temperature rise in the magnet body raises the baseline operating temperature $T_0$, shifts the operating $H_{cJ}(T_0)$ downward, and reduces the thermal spike margin needed to trigger domain reversal.

### VII.4 Transmutation-Induced Compositional Drift

At the cumulative fluences encountered over multi-year CEBAF operational cycles, neutron capture and transmutation measurably alter the stoichiometry of both magnetic phases. In Nd₂Fe₁₄B, the primary transmutation chains include:

- ${}^{148}\text{Nd}(n,\gamma){}^{149}\text{Nd} \xrightarrow{\beta^-} {}^{149}\text{Pm} \xrightarrow{\beta^-} {}^{149}\text{Sm}$: Substituting samarium for neodymium on the rare-earth sublattice.
- ${}^{58}\text{Fe}(n,\gamma){}^{59}\text{Fe} \xrightarrow{\beta^-} {}^{59}\text{Co}$: Substituting cobalt for iron on the Fe sublattice.

These compositional changes alter the exchange interactions governing $T_c$ and $H_{cJ}$, contributing to a long-term drift in baseline $B_r$ that is distinct from both Regime 1 and Regime 2 damage and cannot be attributed to any single radiation event. This is expected to be a second-order effect at the fluences anticipated in the CEBAF environment, but merits monitoring in flux measurements over multi-year timescales.

### VII.5 Radiation-Enhanced Diffusion at Grain Boundaries

A mechanism not addressed in many treatments of radiation effects on permanent magnets is radiation-enhanced diffusion. The continuous production of point defects (vacancies and interstitials) by displacement cascades creates a supersaturation of mobile defects that dramatically accelerates solid-state diffusion compared to the purely thermal diffusion rate. In the Nd₂Fe₁₄B system, the Nd-rich intergranular phase that controls the nucleation-based coercivity mechanism is thermodynamically metastable and maintained kinetically by the low diffusion rates at operating temperatures (typically below 80 C in accelerator environments).

Over extended irradiation periods, radiation-enhanced diffusion could redistribute the Nd-rich grain boundary phase, potentially:

1. Thinning the intergranular layer at some boundaries while thickening it at others, creating spatial inhomogeneity in the nucleation barrier.
2. Promoting crystallization of the amorphous Nd-rich phase, which could either increase or decrease the local coercivity depending on the resulting crystal structure and composition.
3. Facilitating oxygen or hydrogen ingress along grain boundaries if the magnet coating is compromised, accelerating corrosion-driven demagnetization.

This mechanism has not been quantitatively characterized for the fluence levels and neutron spectra relevant to CEBAF and represents an area where long-term monitoring of magnet properties could provide valuable data. The Sm₂Co₁₇ system, with its precipitation-hardened cellular microstructure formed at much higher temperatures (approximately 800-850 C aging), is expected to be more resistant to radiation-enhanced diffusion effects, as the cellular structure is closer to thermodynamic equilibrium.

### VII.6 Dose-Rate and Irradiation Continuity Effects

**Simplified concept:** The rate at which radiation is delivered matters, not just the total dose. Surprisingly, delivering the same total dose in two separate sessions with a long break between them causes less damage than delivering it all at once. This suggests that some partial recovery or relaxation of magnetic domains occurs between irradiation sessions, even without deliberate re-magnetization.

**Rigorous treatment:** Miyahara et al. [51] investigated the effect of irradiation continuity by comparing continuous and discontinuous 10 MeV neutron irradiation of NdFeB magnets. Samples irradiated with 3.7 kGy in a single session showed more demagnetization than samples irradiated with the same total dose of 3.7 kGy delivered in two sessions separated by a nine-month interval. The discontinuously irradiated samples showed approximately 14% less demagnetization than the continuously irradiated ones.

The physical interpretation is not definitively established, but the most likely mechanism involves partial relaxation of marginally reversed domains during the inter-irradiation interval. Domains that were nucleated by thermal spikes but are only weakly stabilized in their reversed orientation (because the local demagnetizing field barely exceeds the reduced coercivity) may partially relax back toward their original orientation through thermally activated processes over the nine-month timescale. This would be most effective for domains sitting in shallow local energy minima -- precisely the marginal domains that thermal stabilization (pre-baking) would also remove.

This finding is directly relevant to the CEBAF environment in two opposing ways. On one hand, CEBAF's CW operation provides continuous irradiation during beam-on periods, which -- per Miyahara's finding -- should produce more damage per unit dose than pulsed irradiation. On the other hand, CEBAF's scheduled maintenance periods (typically several weeks per year) provide inter-irradiation intervals during which partial relaxation could occur. The net effect depends on the relative timescales of domain relaxation and the CEBAF operating schedule, and is not currently quantified.

### VII.7 Manufacturer and Lot Variability

**Simplified concept:** Two magnets with the same nominal composition and grade specification, purchased from different manufacturers, can show significantly different radiation resistance. This is because the radiation sensitivity depends on microstructural details -- grain size distribution, grain boundary phase thickness and composition, defect density, and the precise heat treatment history -- that are not captured by the standard grade designation (which specifies only minimum $B_r$, $H_{cJ}$, and $(BH)_{max}$). The implication is that radiation damage results obtained with magnets from one vendor cannot be assumed to apply quantitatively to nominally identical magnets from a different vendor.

**Rigorous treatment:** Multiple studies have documented significant manufacturer-to-manufacturer variability in radiation resistance for nominally identical magnet grades. Luna et al. [36] found that Sm$_2$Co$_{17}$ magnets from different manufacturers showed substantially different resistance to bremsstrahlung radiation, concluding that manufacturing techniques had a significant influence on radiation hardness. Brown and Cost [39] observed that NdFeB samples from two different manufacturers, irradiated under identical fast neutron conditions, exhibited different demagnetization rates. Simos et al. [22] confirmed this pattern in mixed irradiation fields at the BNL BLIP facility, where magnets of the same grade but different provenance showed measurably different responses.

The microstructural origin of this variability lies in the processing-sensitive features that control the coercivity mechanism. For NdFeB, the critical factors include the grain size (which affects the number of nucleation-prone grain boundaries per unit volume), the thickness and composition of the Nd-rich intergranular phase (which determines the nucleation barrier), and the distribution of soft magnetic impurity phases (particularly $\alpha$-Fe inclusions, which can serve as preferential reversed-domain nucleation sites). For Sm$_2$Co$_{17}$, the cellular microstructure parameters -- cell size, cell boundary continuity, Cu partitioning, and Zr-rich platelet density -- are all processing-dependent and directly affect the pinning field strength.

For the LDRD study, all four grades (N42EH, N52SH, SmCo33H, SmCo35) were procured from specific vendors, and the results should be understood as specific to those particular production lots. The BDSIM simulation framework [42,47] can predict the radiation environment, but the material response coefficients will need to be re-validated if different vendors or lots are used for the actual FFA magnet production.

### VII.8 Cryogenic Temperature Effects on Radiation Resistance

**Simplified concept:** Cooling a magnet to cryogenic temperatures before irradiating it makes it more resistant to radiation damage. This makes physical sense within the thermal spike model: if the magnet starts at a lower baseline temperature, the coercivity is higher (because $H_{cJ}$ increases as temperature decreases), and a thermal spike of a given energy produces a smaller $\Delta T$ relative to the much-higher $\Delta T_{crit}$ threshold. Essentially, the magnet has more thermal "headroom" at low temperatures.

**Rigorous treatment:** Bizen et al. demonstrated that NdFeB magnets irradiated at cryogenic temperatures show significantly less demagnetization than identical magnets irradiated at room temperature for the same electron fluence. This is a direct consequence of the temperature-dependent coercivity: at cryogenic temperatures, $H_{cJ}(T)$ increases (because $\beta$ is negative, so lowering $T$ increases $H_{cJ}$), which increases $\Delta T_{crit}$ per the criterion of Section V.3. The thermal spike must now heat the lattice from a lower starting temperature to the same absolute temperature at which $H_{cJ}$ falls below $|H_{op}|$, requiring more energy per spike.

This result provides important validation of the thermal spike model itself: the observation that reducing the baseline temperature increases radiation resistance is exactly what the model predicts, and rules out alternative mechanisms (such as direct atomic displacement damage to the crystal structure) that would be temperature-independent at these temperature scales.

For the FFA@CEBAF application, cryogenic operation of the permanent magnets is not planned -- the magnets will operate at or near room temperature, possibly with modest cooling. However, the cryogenic data constrains the thermal spike model parameters and supports the conclusion that any measure that reduces the baseline operating temperature of the magnets (improved thermal management, heat sinking, active cooling) will directly improve their radiation resistance. A temperature reduction of even 20-30 C from an uncooled equilibrium could meaningfully increase $\Delta T_{crit}$, particularly for the NdFeB grades where $|\beta|$ is large ($\sim$0.55-0.58 %/C).

---

## VIII. Comparative Vulnerability of the Four Grades

### VIII.1 The $\Delta T_{crit}$ Framework

The radiation vulnerability of the four grades is not uniform and depends on both the material properties and the specific Halbach wedge position. Using the critical temperature rise criterion from Section V.3:

$$\Delta T_{crit} = \frac{H_{cJ}(T_0) - |H_{op}(\vec{r})|}{|\beta| \cdot H_{cJ}(T_0)}$$

A larger $\Delta T_{crit}$ means a more radiation-resistant operating condition.

### VIII.2 Numerical Evaluation at Representative Operating Points

Taking $T_0$ = 40 C (a representative magnet temperature with cooling) and evaluating at two representative operating field levels -- $|H_{op}|$ = 5 kOe (moderate stress, radial wedge) and $|H_{op}|$ = 15 kOe (high stress, azimuthal wedge) -- using the minimum-specification $H_{cJ}$ for each grade:

| Grade | $H_{cJ,min}$ (kOe) | $|\beta|$ (%/C) | $\Delta T_{crit}$ at $|H_{op}|$ = 5 kOe | $\Delta T_{crit}$ at $|H_{op}|$ = 15 kOe |
|-------|---------------------|------------------|------------------------------------------|-------------------------------------------|
| N42EH | 25 | 0.55 | 145 C | 73 C |
| N52SH | 20 | 0.58 | 129 C | 43 C |
| SmCo33H | 25 | 0.22 | 364 C | 182 C |
| SmCo35 | 25 | 0.22 | 364 C | 182 C |

These values use the manufacturer-minimum $H_{cJ}$ specifications. Actual lot values may be higher, which would increase $\Delta T_{crit}$.

### VIII.3 Ranking and Design Implications

1. **SmCo33H and SmCo35 -- most resistant.** The combination of $T_c \approx 920$ C, $|\beta(H_{cJ})| \approx 0.20-0.25\%$/C, the absence of boron (eliminating the ¹⁰B(n,$\alpha$) mechanism entirely), and the domain wall pinning coercivity mechanism makes these grades far more tolerant of the CEBAF neutron environment than either NdFeB grade. SmCo35's marginally higher $B_r$ comes with essentially the same radiation resistance as SmCo33H. The $\Delta T_{crit}$ values are 2.5 times larger than for the NdFeB grades, and this understates the advantage because it does not account for the absence of the ¹⁰B channel or the inherent resistance of the pinning mechanism.

2. **N42EH -- intermediate.** The elevated $H_{cJ}$ from Dy doping increases the numerator of $\Delta T_{crit}$, and the reduced $|\beta|$ from Dy substitution increases the effective threshold. N42EH is the preferred NdFeB grade for high-stress azimuthal wedge positions in the radiation environment.

3. **N52SH -- most vulnerable among the four.** The competing demands of maximum $B_r$ and SH-grade $H_{cJ}$ result in the smallest $\Delta T_{crit}$ margin. At $|H_{op}|$ = 15 kOe, the margin is only 43 C, meaning relatively modest thermal spikes can trigger domain reversal. N52SH is appropriate only for low-stress radial wedge positions with lower $|H_{op}|$. Its use in azimuthal wedge positions at the highest radiation doses should be examined carefully against the Monte Carlo-computed $|H_{op}|$ distribution.

### VIII.4 The Temnykh Demagnetizing Temperature Correlation

**Simplified concept:** Temnykh at Cornell discovered a remarkably useful empirical shortcut for predicting how radiation-resistant a specific magnet sample will be, without needing to know anything about the details of the radiation field or the microscopic damage mechanisms. The key observation is that the radiation dose required to produce a given amount of demagnetization (say, 1% flux loss) correlates exponentially with a single easily measurable quantity: the "demagnetizing temperature" of that specific sample. The demagnetizing temperature is the temperature at which the magnet, in its specific geometry and magnetic circuit, loses a defined fraction of its magnetization due to thermal effects alone. A magnet that can withstand high temperatures before demagnetizing (high demagnetizing temperature) also requires a high radiation dose before demagnetizing, and vice versa. This correlation holds across different magnet grades, geometries, and radiation types, because both thermal demagnetization and radiation-induced demagnetization ultimately operate through the same mechanism: overcoming the coercivity barrier to nucleate reversed domains.

**Rigorous treatment:** Temnykh [52] measured the demagnetization of NdFeB permanent magnets (several grades) induced by 5 GeV electron irradiation at the Cornell Electron Storage Ring (CESR). By systematically varying the magnet geometry (and thus $P_c$) and grade (and thus $H_{cJ}$), Temnykh demonstrated that the radiation dose required to produce a fixed fractional flux loss correlates exponentially with the demagnetizing temperature $T_d$ of each sample:

$$D_{1\%} \propto \exp\left(\alpha \cdot T_d\right)$$

where $D_{1\%}$ is the dose for 1% flux loss and $\alpha$ is an empirical constant. The demagnetizing temperature $T_d$ is defined as the temperature at which the sample, in its specific geometry and external field environment, undergoes a specified fractional loss of magnetization (typically measured by slowly heating the sample while monitoring its field).

The physical basis for this correlation is that $T_d$ integrates exactly the same set of material and geometric parameters that determine radiation sensitivity: $H_{cJ}(T)$, $|\beta|$, $P_c$, and the details of the microstructural nucleation or pinning landscape. A sample with a high $T_d$ has a large effective $\Delta T_{crit}$, meaning both that it requires more thermal energy to demagnetize and that it requires a more energetic thermal spike (from radiation) to nucleate reversed domains.

This correlation provides an extremely practical tool for the LDRD study and FFA design: by measuring $T_d$ for each magnet sample (or for representative samples from a production lot), one can predict relative radiation resistance without performing irradiation experiments. For the LDRD samples, comparing the measured $T_d$ values across grades with the observed flux loss after irradiation provides a direct test of whether the CEBAF arc radiation environment produces demagnetization consistent with the thermal spike mechanism -- if the $T_d$ correlation holds, it confirms a thermally-mediated damage pathway regardless of what the primary radiation species turns out to be.

---

## IX. Empirical Dose-Response Compilation

The following table summarizes the key experimental results from the published literature on radiation-induced demagnetization of permanent magnets. This compilation makes immediately visible several patterns that inform the mechanistic discussion throughout this document: the dependence on radiation type (electrons vs. photons vs. neutrons), the superiority of SmCo over NdFeB, the role of nuclear interactions (star density) vs. absorbed dose, and the photon irradiation paradox discussed in Section IIA.5.

| Material | Radiation type | Energy | Dose / Fluence | Flux loss | Key observation | Ref |
|----------|---------------|--------|----------------|-----------|-----------------|-----|
| NdFeB (sintered) | Electrons | 2 GeV | ~10$^{14}$ e$^-$ | ~1% | Thermal spike model proposed | [5] |
| NdFeB (baked) | Electrons | 2 GeV | ~10$^{14}$ e$^-$ | ~0.3% | Baking reduces damage rate ~3x | [6] |
| NdFeB | Electrons | 4, 6, 8 GeV | Various | Energy-dependent | Damage increases with energy; not proportional | [9] |
| NdFeB (undulator) | Operational (e$^-$ losses) | 2-8 GeV | 10$^4$-10$^5$ Gy absorbed | ~1% | Facility operational data; multiple labs | [5,7,38] |
| NdFeB (SACLA) | Operational (e$^-$ losses) | 8 GeV | Not reported | Large, localized | Coherent magnetization reversal, not gradual | [10] |
| NdFeB | Bending magnet SR (X-rays) | keV range | 280 MRad (2.8 MGy) | $<$0.5% (undetectable) | **No demagnetization from pure SR photons** | [48] |
| NdFeB | $^{60}$Co gamma rays | 1.25 MeV | 700 MRad (7 MGy) | $<$0.5% (undetectable) | **No demagnetization from pure gamma rays** | [48] |
| NdFeB | Electrons | 17 MeV | 2.6 MGy absorbed | ~9% | Electrons at same dose cause large damage | [37] (Okuda) |
| NdFeB | Fast neutrons | ~2 MeV avg | 5$\times$10$^{16}$ n/cm$^2$ | Significant | Manufacturer-dependent; two vendors compared | [39] |
| NdFeB | 10 MeV neutrons | 10 MeV | 1.1-7.4 kGy | 0.6-47% | Strong L/D dependence; dose-rate effect | [51] |
| NdFeB | Thermal neutrons | Thermal | Various | Substantial | $^{10}$B(n,$\alpha$) channel dominant | [21] |
| NdFeB (N38H) | Mixed (BNL BLIP) | Spallation spectrum | Up to ~2 GRad | Severe | Thermal > fast neutron damage in NdFeB; annular geometry more resistant | [22] |
| NdFeB | Mixed (e$^-$, $\gamma$, n) | FLUKA-modeled | Star density correlated | Correlated | **Star density, not absorbed dose, predicts demagnetization** | [8] |
| NdFeB | Electrons | 5 GeV | Various | Various | Exponential correlation with demagnetizing temp $T_d$ | [52] |
| Sm$_2$Co$_{17}$ | Bremsstrahlung | Mixed e$^-$/$\gamma$ | Up to 2 GRad | Small | Most radiation-resistant; manufacturer-dependent | [36] |
| Sm$_2$Co$_{17}$ | Fast neutrons | ~2 MeV avg | 5$\times$10$^{14}$ n/cm$^2$ | Phase unchanged | Domain structure and Mossbauer spectra unchanged | [37] |
| Sm$_2$Co$_{17}$ | Mixed (BNL BLIP) | Spallation spectrum | Up to ~2 GRad | Moderate | Annular shape shows enhanced resistance | [22] |
| SmCo$_5$ | Bremsstrahlung | Mixed e$^-$/$\gamma$ | Up to 2 GRad | Intermediate | Between Sm$_2$Co$_{17}$ and NdFeB | [36] |
| Pr$_2$Fe$_{14}$B | Mixed (BNL BLIP) | Spallation spectrum | Up to ~2 GRad | Less than NdFeB at low fluence; comparable at high fluence | Higher $T_c$ than NdFeB; initially more resistant | [22] |

**Key patterns visible in this compilation:**

The radiation type matters fundamentally. Pure photon irradiation (SR X-rays, $^{60}$Co gammas) produces no measurable demagnetization even at MGy doses (Alderman et al. [48]), while electron irradiation at comparable absorbed doses produces percent-level flux loss (Okuda, Bizen). Asano et al. [8] resolved this by showing that star density (nuclear interaction rate) -- not absorbed electromagnetic dose -- is the quantity that correlates with demagnetization. This establishes that the damage agent is the nuclear interaction products within the electromagnetic cascade, not the electromagnetic energy deposition itself. This finding is central to interpreting the LDRD arc observations (Section IIA.5).

Material ranking is consistent across all radiation types: Sm$_2$Co$_{17}$ $>$ SmCo$_5$ $>$ Pr$_2$Fe$_{14}$B $\geq$ Nd$_2$Fe$_{14}$B, reflecting the hierarchy of Curie temperature, coercivity mechanism (pinning vs. nucleation), and absence of boron.

Geometry (L/D ratio, annular vs. block) is a strong modulator of sensitivity, independent of material, confirming the $P_c$-dependent $\Delta T_{crit}$ framework.

---

## X. Note on Monte Carlo Implementation

The framework above defines the required inputs for a Geant4 or FLUKA radiation damage study. Key parameters requiring explicit specification in the simulation input are:

1. The precise geometry and material composition of collimators, beam pipe, and magnet assemblies, including the Nd₂Fe₁₄B or Sm₂Co₁₇ elemental composition with correct isotopic abundances (particularly the natural ¹⁰B/¹¹B ratio of 19.9%/80.1% in NdFeB).

2. Activation of LPM suppression in the electromagnetic physics list (Geant4: ensure the `G4eBremsstrahlung` process uses the LPM-corrected model, which is default in most physics lists above version 10.0).

3. Accurate photonuclear cross-section libraries (Geant4: `G4PhotoNuclearProcess` with `G4CascadeInterface` for intranuclear cascade modeling; FLUKA: enabled by default through the PHOTONUC card).

4. Thermal neutron transport with the HP (High Precision) neutron package (Geant4: `G4NeutronHPElastic`, `G4NeutronHPCapture`, etc.) to properly sample the ¹⁰B(n,$\alpha$) reaction at epithermal and thermal energies with correct angular and energy distributions.

5. Displacement damage scoring using NIEL/DPA tallies with sublattice-specific $E_d$ values as given in Section IV.3.

6. Geometry sufficient to model neutron moderation in the surrounding environment, including concrete shielding, support structures, and any hydrogenous materials that contribute to the thermal neutron field at the magnet location.

---

## References

[1] Agostinelli, S., et al. (2003). "GEANT4 -- a simulation toolkit." *Nuclear Instruments and Methods in Physics Research Section A*, **506**(3), 250-303. doi:10.1016/S0168-9002(03)01368-8

[2] Ferrari, A., Sala, P.R., Fasso, A., & Ranft, J. (2005). *FLUKA: A Multi-particle Transport Code*. CERN-2005-010, INFN/TC_05/11, SLAC-R-773.

[3] Coey, J.M.D. (2010). *Magnetism and Magnetic Materials*. Cambridge University Press. ISBN 978-0-521-81614-4.

[4] Halbach, K. (1980). "Design of permanent multipole magnets with oriented rare earth cobalt material." *Nuclear Instruments and Methods*, **169**(1), 1-10. doi:10.1016/0029-554X(80)90094-4

[5] Bizen, T., et al. (2001). "Demagnetization of undulator magnets irradiated high energy electrons." *Nuclear Instruments and Methods in Physics Research Section A*, **467-468**, Part 1, 185-189. doi:10.1016/S0168-9002(01)00282-2

[6] Bizen, T., et al. (2003). "Baking effect for NdFeB magnets against demagnetization induced by high-energy electrons." *Nuclear Instruments and Methods in Physics Research Section A*, **515**, 850-852. doi:10.1016/j.nima.2003.07.029

[7] Bizen, T., et al. (2007). "Radiation damage in permanent magnets for ID." *Nuclear Instruments and Methods in Physics Research Section A*, **574**, 401-405. (Proceedings of SRI2006). doi:10.1016/j.nima.2007.02.085

[8] Asano, Y., Bizen, T., & Marechal, X. (2009). "Analyses of the factors for the demagnetization of permanent magnets caused by high-energy electron irradiation." *Journal of Synchrotron Radiation*, **16**, 317-324. doi:10.1107/S0909049509008899

[9] Bizen, T., et al. (2007). "High-energy electron irradiation of NdFeB permanent magnets: Dependence of radiation damage on the electron energy." *Nuclear Instruments and Methods in Physics Research Section A*, **574**(3), 401-405.

[10] Bizen, T., et al. (2016). "Radiation-induced magnetization reversal causing a large flux loss in undulator permanent magnets." *Scientific Reports*, **6**, 37937. doi:10.1038/srep37937

[11] Bethe, H., & Heitler, W. (1934). "On the stopping of fast particles and on the creation of positive electrons." *Proceedings of the Royal Society of London. Series A*, **146**(856), 83-112.

[12] Particle Data Group (Tanabashi, M., et al.) (2018). "Review of Particle Physics." *Physical Review D*, **98**, 030001. Chapter 34: "Passage of particles through matter." (Updated editions available from PDG; radiation length and critical energy values are standard reference data.)

[13] Landau, L.D., & Pomeranchuk, I.Ya. (1953). "Limits of applicability of the theory of bremsstrahlung and pair production at high energies." *Doklady Akademii Nauk SSSR*, **92**, 535 & 735.

[14] Migdal, A.B. (1956). "Bremsstrahlung and pair production in condensed media at high energies." *Physical Review*, **103**(6), 1811-1820.

[15] Goldhaber, M., & Teller, E. (1948). "On Nuclear Dipole Vibrations." *Physical Review*, **74**(9), 1046-1049.

[16] Berman, B.L., & Fultz, S.C. (1975). "Measurements of the giant dipole resonance with monoenergetic photons." *Reviews of Modern Physics*, **47**(3), 713-761.

[17] Levinger, J.S. (1951). "The High Energy Nuclear Photoeffect." *Physical Review*, **84**(1), 43-51.

[18] Wang, M., et al. (2017). "The AME2016 atomic mass evaluation." *Chinese Physics C*, **41**(3), 030003.

[19] Knoll, G.F. (2010). *Radiation Detection and Measurement* (4th ed.). John Wiley & Sons. ISBN 978-0-470-13148-0.

[20] Brown, D.A., et al. (2018). "ENDF/B-VIII.0: The 8th Major Release of the Nuclear Reaction Data Library." *Nuclear Data Sheets*, **148**, 1-142. doi:10.1016/j.nds.2018.02.001

[21] Klaffky, R., Lindstrom, R., Maranville, B., Shull, R., Micklich, B., & Vacca, J. (2006). "Thermal Neutron Demagnetization of NdFeB Magnets." *Proceedings of EPAC 2006*, Edinburgh, Scotland, THPLS130.

[22] Simos, N., et al. (2018). "Demagnetization of Nd₂Fe₁₄B, Pr₂Fe₁₄B, and Sm₂Co₁₇ permanent magnets in mixed irradiation fields." Brookhaven National Laboratory Technical Report. (Available at OSTI.gov: https://www.osti.gov/servlets/purl/1454811)

[23] Zinkle, S.J., & Was, G.S. (2013). "Materials challenges in nuclear energy." *Acta Materialia*, **61**, 735-758.

[24] Nordlund, K., et al. (2018). "Primary radiation damage: A review of current understanding and models." *Journal of Nuclear Materials*, **512**, 450-479. doi:10.1016/j.jnucmat.2018.10.027

[25] Nordlund, K., et al. (2018). "Improving atomic displacement and replacement calculations with physically realistic damage models." *Nature Communications*, **9**, 1084. doi:10.1038/s41467-018-03415-5

[26] Norgett, M.J., Robinson, M.T., & Torrens, I.M. (1975). "A proposed method of calculating displacement dose rates." *Nuclear Engineering and Design*, **33**(1), 50-54.

[27] Lindhard, J., Nielsen, V., Scharff, M., & Thomsen, P.V. (1963). "Integral equations governing radiation effects." *Matematisk-fysiske Meddelelser udgivet af det Kongelige Danske Videnskabernes Selskab*, **33**(10).

[28] ASTM E693-17 (2017). "Standard Practice for Characterizing Neutron Exposures in Iron and Low Alloy Steels in Terms of Displacements Per Atom (DPA)." ASTM International, West Conshohocken, PA.

[29] Samin, A., Kurth, M., & Cao, L.R. (2015). "An analysis of radiation effects on NdFeB permanent magnets." *Nuclear Instruments and Methods in Physics Research Section B*, **342**, 200-205. doi:10.1016/j.nimb.2014.10.006

[30] Samin, A., & Cao, L.R. (2015). "Monte Carlo study of radiation-induced demagnetization using the two-dimensional Ising model." *Nuclear Instruments and Methods in Physics Research Section B*, **360**, 111-117.

[31] Sagawa, M., Fujimura, S., Togawa, N., Yamamoto, H., & Matsuura, Y. (1984). "New material for permanent magnets on a base of Nd and Fe." *Journal of Applied Physics*, **55**(6), 2083-2087.

[32] Kronmuller, H., & Faehnle, M. (2003). *Micromagnetism and the Microstructure of Ferromagnetic Solids*. Cambridge University Press.

[33] Duerrschnabel, M., et al. (2017). "Atomic structure and domain wall pinning in samarium-cobalt-based permanent magnets." *Nature Communications*, **8**, 54. doi:10.1038/s41467-017-00059-9

[34] Hadjipanayis, G.C. (1996). "SmCo permanent magnets." In: *Rare-Earth Iron Permanent Magnets* (J.M.D. Coey, ed.), Oxford University Press, Ch. 12.

[35] Suzudo, T., et al. (2012). "A modeling study of domain wall pinning in Sm₂Co₁₇-based magnets." *Journal of Magnetism and Magnetic Materials*, **324**, 2178-2182. doi:10.1016/j.jmmm.2012.02.013

[36] Luna, H., et al. (1989). "Bremsstrahlung radiation effects in rare earth permanent magnets." *Nuclear Instruments and Methods in Physics Research Section A*, **285**, 349-354.

[37] Samin, A., et al. (2018). "A review of radiation-induced demagnetization of permanent magnets." *Journal of Nuclear Materials*, **509**, 249-262.

[38] Vagin, P., et al. (2014). "Radiation damage of undulators at PETRA III." *Proceedings of IPAC2014*, Dresden, Germany, 2019-2021. JACoW, Geneva.

[39] Brown, R.D., & Cost, J.R. (1989). "Radiation-induced changes in magnetic properties of Nd-Fe-B permanent magnets." *IEEE Transactions on Magnetics*, **25**(5), 3117-3119.

[40] Diaz de la Rubia, T., Averback, R.S., Benedek, R., & King, W.E. (1987). "Role of thermal spikes in energetic collision cascades." *Physical Review Letters*, **59**(17), 1930-1933.

[41] Bodenstein, R.M., et al. (2025). "Current status of permanent magnet radiation resiliency studies at CEBAF." *JACoW*, IPAC2025, THPB093, p. 2664. doi:10.18429/JACoW-IPAC25-THPB093

[42] Gamage, B., Nissen, E., Neththikumara, I., Deitrick, K., & Bodenstein, R. (2025). "Radiation dose simulations for Jefferson Lab's permanent magnet resiliency LDRD study." *Proceedings of NAPAC'25*. (Submitted August 2025.)

[43] Carpenter, A., et al. (2025). "Data-driven gradient optimization for field emission management in a superconducting radio-frequency linac." *Physical Review Accelerators and Beams*, **28**, 044603. doi:10.1103/PhysRevAccelBeams.28.044603

[44] Degtiarenko, P.V. (2019). "Neutron detector and dose rate meter using beryllium-loaded materials." US Patent Number 10281600B2. OSTI: https://www.osti.gov/servlets/purl/1568305

[45] Tennant, C., et al. (2022). "Field emission mitigation in CEBAF SRF cavities using deep learning." *Proceedings of NAPAC'22*, Albuquerque, NM, WEPA25.

[46] Bodenstein, R.M., et al. (2024). "Permanent magnet resiliency in CEBAF's radiation environment: LDRD grant status and plans." *Proceedings of IPAC'24*, Nashville, TN, pp. 3875-3878. doi:10.18429/JACoW-IPAC2024-THPS58

[47] Nissen, E., et al. (2025). "Design and instrumentation for permanent magnet samples exposed to a radiation environment." *Proceedings of NAPAC'25*. (Submitted August 2025.)

[48] Alderman, J., Semones, E., & Job, P.K. (2002). "Measurement of radiation-induced demagnetization of Nd-Fe-B permanent magnets." *Nuclear Instruments and Methods in Physics Research Section A*, **481**, 9-28.

[49] Walker, R.P. (1998). "Synchrotron Radiation." *Proceedings of the CERN Accelerator School*, CERN 98-04, pp. 437-459.

[50] Marhauser, F. (2013). "Field emission and consequences in SRF cavities." *Proceedings of SRF2013*, Paris, France. Also JLab-TN-12-044.

[51] Miyahara, N., Tanaka, T., & Kitamura, H. (2000). "Irradiation of NdFeB permanent magnets using 10 MeV neutrons." *Nuclear Instruments and Methods in Physics Research Section B*, **164-165**, 932-937.

[52] Temnykh, A.B. (2008). "Measurement of NdFeB permanent magnets demagnetization induced by high energy electron radiation." *Nuclear Instruments and Methods in Physics Research Section A*, **587**, 13-19. doi:10.1016/j.nima.2007.12.035

[53] Bodenstein, R.M., Nissen, E., Deitrick, K., & Gamage, R. (2025). "Magnet LDRD Sample Placement." Jefferson Lab Technical Note JLAB-TN-25-021.

[54] Bodenstein, R.M., Deitrick, K., Gamage, R., Neththikumara, I., Nissen, E., & Samari, J. (2025). "Comparing Permanent Magnet Measurements: Lab vs. Tunnel Enclosure." Jefferson Lab Technical Note JLAB-TN-25-069.

[55] Bodenstein, R.M., et al. (2025). "Status of permanent magnet radiation resiliency studies at CEBAF." *Proceedings of NAPAC'25*, Sacramento, CA, USA, pp. 630-633. doi:10.18429/JACoW-NAPAC2025-WEAN02

---

*Document prepared for the 12 GeV CEBAF radiation environment. All grade-specific numerical values should be confirmed against the specific manufacturer's datasheet for the production lot used. The Geant4 physics list selection, geometry implementation, and scoring methodology should follow current Geant4 collaboration recommendations.*
