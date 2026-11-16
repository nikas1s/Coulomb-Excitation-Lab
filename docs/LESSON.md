# A 60–90 minute teaching laboratory

## Learning goals

Connect an electromagnetic matrix element to a measured yield; distinguish amplitudes from probabilities; recognize multi-step excitation and reorientation; separate numerical convergence from model validity.

## 1. Read the model (10 minutes)

Run the magnesium example. Explain why the spins 0, 2 and 4 produce 1, 5 and 9 magnetic substates. Identify a direct connection and a two-step path. The input has no diagonal 2→2 (quadrupole) element because Q(2+) of 22Mg is not measured. Why would a diagonal element not represent a decay to another level?

Check the units: 66 MeV is the total beam energy, 3.0 MeV/u. Convert the target areal density from mg/cm² to atoms/cm². Derive the dimensions of the yield formula before using it.

## 2. Follow the collision (15 minutes)

Inspect 30°, 90° and 150° in “During the collision.” Describe how the closest approach changes. Follow the amplitudes and identify the time of strongest excitation. Explain why a level's transient population can decrease later in the same collision.

Discuss why the sum of all populations must remain one within this closed-channel model. Why would an artificial normalization after every time step be a poor accuracy diagnostic?

## 3. Test weak coupling (15 minutes)

Save the original input. Set the diagonal elements and the 2→4 transition to zero. Reduce the 0→2 element by a factor of ten; calculate at 60°. Double this weak element and repeat. Explain why the first-order expectation is roughly four times the excited-state probability. Then restore the original element and identify where the weak-coupling scaling ceases to hold.

Set every transition to zero. Confirm that the nucleus remains in its ground state. The elastic Rutherford cross section is still nonzero: distinguish deflection from internal excitation.

## 4. Observe reorientation and multi-step excitation (15 minutes)

Restore the supplied magnesium input and add a diagonal 2→2 element, `2 2 0.13 2`, which corresponds to Q(2+) ≈ +0.1 e b. Run it, then reverse the element's sign. Compare the angular population and yield curves. Explain why transition strengths alone, without their signs, are insufficient.

Set only the 2→4 element to zero. What happens to the 4+ population? Does the population removed from 4+ necessarily move entirely into 2+? Use conservation and coupled dynamics in your explanation.

## 5. Make a detector prediction (15 minutes)

Use a 25°–55° lab annulus, a beam intensity of 10⁵/s, a two-mg/cm² target, and five days. Record the excited-state yields. Halve the CM angle step and repeat. Report the change as an angular-discretization diagnostic, not as the total experimental uncertainty.

Change the azimuth coverage to 0.5. Verify the expected yield scaling. Explain why a cross section in barn/sr cannot be inserted directly into the particle-count formula.

For a heavy projectile on a light target, examine the two lab branches. Why must both be included in the detector count?

## 6. Defend the calculation (10–20 minutes)

Run the three accuracy checks at a representative angle. Record both the absolute change in each level's probability and the norm drift. Explain why a small norm drift alone does not establish accuracy.

Read the original-code comparison report. Is agreement at the 10⁻⁷ population level an experimental validation? Which features are exercised by the supplied examples, and which have only invariant or analytic tests?

Inspect the surface-separation plot. Identify calculations where a nuclear interaction may matter even though the numerical solver converged. Discuss level-scheme truncation, uncertain matrix elements and stopping-power uncertainty.

## Optional literature exercise (15 minutes)

Select **Teaching: sudden rotor**. All levels are degenerate, so the adiabaticity parameter is ξ = 0, and Alder & Winther (1960) solved the 180° problem exactly. Run the calculation, open **Help and reference → Verification**, and compare your populations with their published Table 5 (P0 = 0.2152, P2 = 0.5597, P4 = 0.1972, …). Why does a degenerate band make the problem exactly solvable at 180°? Then press **Run literature benchmarks** and explain why agreement with first-order perturbation theory requires a *weak* coupling.

Select **152Sm + 58Ni** and open **Help and reference → Verification**: only B(E2; 0+ → 2+) is measured input, yet the rigid-rotor Q(2+) agrees with the measured −1.683(18) e b. What does this say about the shape of 152Sm? Then select **22Mg + 104Pd**: its B(E2) is uncertain by about 40%. Change the 0→2 element within that range and see how much the 2+ cross section changes.

## Optional stopping-power exercise

Upload `examples/synthetic_stopping.csv`. It is deliberately synthetic: a constant 2 MeV/(mg/cm²) should reduce the 66 MeV beam to 62 MeV through 2 mg/cm². Verify this using `StoppingTable.profile`, then compare 4-, 6-, and 8-point depth averages. Do not use this artificial table to infer a physical magnesium stopping power.
