# Experimental validation target

Primary source and attribution are in `manifest.json`. `yields.csv` transcribes the 120Sn subset of Table I, including the weak feeding line. It preserves reported peak-intensity errors and the absence of efficiency correction. It is not a raw-Poisson or efficiency-corrected dataset.

Before reproducing the extraction, obtain the seven missing input groups listed in the manifest. The gamma response must include calibrated efficiency and angular/acceptance corrections; target normalization must be matched. An arbitrary count scale or unit efficiency would not constitute validation. The current qualification command reports this case as incomplete and does not fit it.

`acceptance.png` illustrates the nominal projectile/recoil angular mapping and kinetic energies. Its 1 MeV threshold is explicitly illustrative, not an experimental calibration. The predictor now supports the corresponding event union, but the experiment-specific trigger, thresholds, masks and efficiencies still require validation.
