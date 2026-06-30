# Thermal Aging Physics Explainer
# Written 2026-05-31 for future JLAB-TN on thermal aging analysis
# Undergraduate-level explanation of the key concepts

## What's Actually Happening Inside a Permanent Magnet

A sintered NdFeB magnet is made of tiny crystalline grains (~5-10 microns). Each grain is a single magnetic domain, meaning all the atomic magnetic moments in that grain point the same direction. When you magnetize the magnet, you align all these grains so their moments point together. That's what makes it a permanent magnet.

But "permanent" isn't really permanent. Each grain's magnetization is sitting in an energy well, like a ball sitting in a bowl. The ball wants to stay at the bottom, but if you shake the bowl hard enough (thermal energy), the ball can hop out and roll into a different orientation. When a grain flips, the magnet gets slightly weaker. This is thermal aging.

## Ea: The Activation Energy

The depth of that energy bowl is the activation energy, Ea. It's measured in electron-volts (eV).

The rate at which grains randomly flip follows the Arrhenius equation (same equation from freshman chemistry for reaction rates):

    flip rate ~ exp(-Ea / kT)

where k is Boltzmann's constant and T is temperature in Kelvin.

- Large Ea (deep bowl) = very hard to flip = very slow aging
- Small Ea (shallow bowl) = easier to flip = faster aging
- Higher T = more thermal energy = more flipping = faster aging

For NdFeB, Ea is typically 0.7 to 1.5 eV. It's actually a distribution (different grains have different barrier depths), but we use a representative value.

### How we use it in the calculation

We have a vendor curve measured at 100C. We need to predict aging at 45C. Arrhenius lets us translate between temperatures:

12 months at 45C is equivalent to how many hours at 100C?

- At Ea = 0.5 eV (unrealistically low): 596 hours at 100C
- At Ea = 1.0 eV (typical): 41 hours at 100C
- At Ea = 1.5 eV (high end): 3 hours at 100C

Higher Ea means the aging rate drops off faster with temperature, so 45C maps to fewer equivalent hours at 100C. We use 1.0 eV as our nominal value, which is middle of the road and conservative (not too favorable to us).

## Hci: The Intrinsic Coercivity

Hci is the magnetic field strength required to demagnetize the magnet. Think of it as "how hard is it to knock the ball out of the bowl." It's measured in kOe (kilo-Oersteds).

- Generic NdFeB (vendor curve grade): Hci ~ 12 kOe
- Our N52SH: Hci = 19 kOe
- Our N42EH: Hci = 30 kOe

Higher Hci = deeper energy wells = much harder to demagnetize (thermally or otherwise). This is exactly why we bought EH and SH grades, on Stephen Brooks' advice.

But Hci also decreases with temperature (the bowls get shallower as it gets hotter). At 100C, the generic grade drops to about 6.2 kOe. Our N42EH at 45C is still at 26.2 kOe. So our magnets have 4x deeper energy wells than the vendor curve grade under its test conditions.

## The Hci Exponent (n): How Protection Scales

Here's where it gets subtle. We know higher Hci means less aging, but how much less? The energy barrier height scales with Hci as:

    E_barrier ~ Hci^n

The exponent n depends on the physics of how domains reverse:

- n = 1 (linear): Simplest assumption. Each doubling of Hci doubles the barrier.
- n = 2 (Stoner-Wohlfarth model): The standard textbook model for coherent rotation of a single-domain particle. Barrier goes as Hci squared.
- n = 3 (nucleation): More realistic for how sintered NdFeB actually reverses. Even stronger protection.

Since the flip rate goes as exp(-E_barrier / kT), and E_barrier ~ Hci^n, the aging correction for our grades vs. the generic grade is:

    correction = (Hci_generic / Hci_ours)^n

For N42EH at 45C vs. generic at 100C:
- n=1: correction = (6.2/26.2)^1 = 0.24 (our magnet ages at 24% the rate)
- n=2: correction = (6.2/26.2)^2 = 0.056 (5.6% the rate)
- n=3: correction = (6.2/26.2)^3 = 0.013 (1.3% the rate)

The real physics is actually exponential through the Boltzmann factor, which would give corrections orders of magnitude smaller than any of these. Using a power law at all is already being generous to the thermal aging hypothesis.

## Why the Sensitivity Table Matters

The n=2 row is our primary estimate (6.4x shortfall). But if someone asks "how do you know it's n=2?", the table shows:

- Even at n=1 (the most favorable assumption for thermal aging, the weakest protection from our high Hci): the shortfall is still 2.1x
- At n=3 (more realistic): 18.5x
- Physical exponential scaling: >> 100x

So the conclusion doesn't depend on knowing the exact exponent. Thermal aging falls short under every reasonable assumption.

## The "Excess Aging" Logic

One more key concept: our measurement compares tunnel plates to lab plates. Both sets of magnets undergo the initial knock-down (the fast early aging from the vendor curve). The only difference is the rate of the slow logarithmic creep at 45C vs. 21C. That difference is the "excess aging," and it's tiny because both temperatures are far below T_0 where aging is negligible.

## Key References

- Arrhenius scaling: standard thermodynamics (any solid-state physics text)
- Stoner-Wohlfarth model (n=2): Stoner & Wohlfarth (1948), Phil. Trans. R. Soc. A 240, 599
- Nucleation-type reversal: Kronmuller & Fahnle (2003), Micromagnetism and the Microstructure of Ferromagnetic Solids
- Hci^2 barrier scaling: Givord et al. (1988), IEEE Trans. Magn. 24(2), 1921-1923
- Haavisto T_0 framework: Haavisto & Paju (2009), IEEE Trans. Magn. 45(12), 5277-5280
- 30-year = 2x(1-hour): Haavisto et al. (2014), Adv. Mater. Sci. Eng. 2014, 760584
- Pre-stabilization: Haavisto et al. (2013), EPJ Web Conf. 40, 06001
- Activation energy distribution: Givord et al. (1987), J. Magn. Magn. Mater. 67, L281
