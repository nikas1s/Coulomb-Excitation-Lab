# Uploading another experiment

The examples are starting points, not hard-coded reactions. The calculation supports other projectile/target nuclei, open level schemes and real electric E1–E4 matrix elements within the model scope in the README.

There are **two different kinds of input**:

1. **Reaction inputs** specify the nuclei, beam energy, nuclear levels and reduced matrix elements that define a prediction.
2. **Measurements** specify observed cross sections, populations or counts to compare with that prediction. Observations alone do not uniquely supply a nuclear level scheme or its matrix elements. This application compares explicit models; it does not automatically fit them.

Every uploader in the app has a **Required file format** box with the exact columns, units, a header-only **blank template** and a separately labelled **example file**; **Help and reference → File formats** collects them all, and **Help and reference → Guide** explains the workflow. Examples are only used when **Built-in example** is selected: the two “own data” sources start empty, never fall back to example numbers, and results from another source are discarded.

## Reaction text files

In the sidebar, step **1 · Reaction**, choose **My own reaction file**. Download the **Annotated blank template** (or the example file), fill it in, and drop the resulting `.txt` or `.dat` file into **Upload your reaction file**. Nothing is calculated before you upload. The **Level scheme** tab shows the parsed levels and connections. Beam energy is **total MeV**, not MeV/u. Lines beginning with `#` are comments. **Download reaction text** exports a comment-free reaction file.

The file contains: title, number of levels, projectile Z/A, target Z/A, beam energy, angle range, N level rows, then electric matrix-element rows. Download a filled example beside the uploader. The UI defaults to **Use angle range from input file** when a reaction file is uploaded; you can adjust the angle range and beam energy before running. Choose projectile/target excitation explicitly in the UI.

## Spreadsheet entry for nuclear levels and matrix elements

Choose **My own tables** in the sidebar. Enter the title and projectile/target Z and A in step 1 and the beam energy in step 2. The main page presents two **empty** editable tables: add/remove rows, edit cells, or upload CSV files with the headers below. A checklist above the tabs shows what is still missing; **Run calculation** is enabled once the reaction is complete.

**levels.csv** — required: `level,spin,energy_mev,parity`; optional: `k`.

```csv
level,spin,energy_mev,parity,k
1,0,0,1,0
2,2,1.247,1,0
3,4,3.308,1,0
```

- Level numbers are consecutive, starting at 1; level 1 has zero excitation energy.
- Spin may be integer or half-integer. Energies are MeV.
- Parity is `1` or `-1`. `k` is retained metadata, defaulting to zero.

**matrix_elements.csv** — required columns:

```csv
initial,final,value,lambda
1,2,0.4687409432,2
2,2,0.6093632261,2
2,3,0.3529591289,2
3,3,0.4588468676,2
```

- `initial` and `final` refer to the one-based level numbers.
- `value` is the **signed reduced matrix element**, not B(Eλ); units are **e b^(λ/2)**. For E2, this is e b.
- `lambda` is the electric multipolarity 1–4. The reverse matrix element is generated with the appropriate Hermitian phase; do not enter a second reversed duplicate.
- Empty matrix-element data (headers only, or delete all rows) describes an uncoupled nucleus.

These nuclear tables retain their template header names. The measurement importer below additionally offers custom-column mapping.

## Upload experimental measurements

Open **Measurements**. A preceding angle scan is not required: the comparison uses the current validated sidebar model and numerical settings directly.

1. Select the observable, angle frame and units.
2. Open the **Required file format** box, download the blank template (headers only), fill in your observations, and drag the file into the uploader. Alternatively select **Paste a table** and paste spreadsheet cells, including their header row. The example file with synthetic numbers is for orientation only.
3. Inspect the preview. If your columns have different names, use **Match your column names**. Common names such as `theta`, `state`, `counts` and `error` are suggested automatically. Extra columns are ignored.
4. For counts, enter the run's beam rate, live duration and azimuth coverage, and confirm the sidebar target thickness and stopping table.
5. Press **Compare measurements**. Inspect the error-bar plot, residual plot and numerical table; download the comparison as CSV or JSON.

Use **one run per table**: same nuclei, beam energy, target composition/thickness, excitation choice and exposure. Change the sidebar model and import the next run separately. Do not combine different beam energies in one file and assume a per-row energy correction. Unknown spreadsheet columns, including energy columns, are not interpreted automatically.

### Cross sections versus angle

```csv
angle_deg,level,value,uncertainty
30,2,0.11,0.01
90,2,0.12,0.01
150,2,0.06,0.005
```

Select **Differential cross sections**, then select **CM** or **Lab** and **barn/sr**, **mb/sr** or **fm²/sr**. Value and uncertainty use the selected units. Comparison output is converted to barn/sr. Lab angles refer to the **scattered projectile**, including when the excited nucleus is the target.

Each row describes a point differential cross section. The solver calculates the actual measurement angles instead of interpolating a coarse display scan. For inverse kinematics, both CM branches contributing to a lab angle are summed. An inaccessible lab angle has a zero predicted cross section. An exactly singular turning point is rejected; compare finite detector acceptance instead.

Finite angular-bin cross sections need an experimentally appropriate effective-angle/bin correction before treating them as points. Alternatively compare measured counts with detector bounds, which performs an acceptance integral.

### Population probabilities

Use the same four columns, choose **Population probabilities**, and supply values in `[0,1]` at **CM** scattering angles. No Rutherford factor is applied to a probability comparison.

### Detected particle counts per detector bin

```csv
angle_min_deg,angle_max_deg,level,value,uncertainty,efficiency
25,40,2,1200,35,0.9
40,55,2,1000,32,0.9
```

Choose **Detected particle counts**, and specify whether the bin boundaries are lab or CM angles. `value` is the observed count in that angular bin for the specified final nuclear level. `efficiency` is that row's particle-detection efficiency, a fraction from 0 to 1. Do not efficiency-correct the data a second time; if your observations already represent efficiency-corrected counts, set the corresponding efficiency to 1 and propagate the correction's uncertainty appropriately.

Enter beam particles/s, acquisition **live duration in days**, the target's mg/cm² density, and azimuth coverage fraction. The prediction integrates cross section over the bin, then applies exposure and efficiency. A detector that includes the divergent 0° CM Rutherford direction is rejected. A kinematically inaccessible detector interval gives zero counts.

Counts are newly integrated with the selected **Detector integration CM step**; the main display scan's angle grid is not used. Halve the integration step to check angular convergence. If stopping is enabled, the integration accounts for each depth's energy, lab acceptance and Rutherford factor; increase depth order independently to check its convergence.

Use separate comparisons when live exposure or azimuth coverage differs between bins. Efficiencies may differ per row. The angular-bin model assumes constant efficiency inside each bin; subdivide bins when necessary. Target atoms use the supplied target mass number, so the model assumes the target areal density belongs to that isotope; dilution and mixtures require an appropriate effective areal density and stopping data.

### Direct gamma coincidences

```csv
angle_min_deg,angle_max_deg,level,value,uncertainty,efficiency,branching_fraction,gamma_efficiency
25,40,2,120,11,0.9,1,0.1
40,55,2,100,10,0.9,1,0.1
```

Choose **Direct gamma coincidence counts**. These are coincidences with the scattered projectile within the stated angular bin, not unconditioned gamma singles. `level` identifies the populated emitting level. `efficiency` is the particle efficiency; `gamma_efficiency` is the absolute gamma efficiency, and `branching_fraction` is the direct photon branch per population. All three are fractions, not percentages.

The prediction is the populated-level particle count times the supplied branching fraction and gamma efficiency. Use an appropriate photon branching fraction when conversion matters. Feeding cascades, angular correlations and decay-network inference are not included; a dataset requiring those effects needs a fuller decay model before its comparison is physically meaningful.

## File details, uncertainty and safeguards

- Export Excel or LibreOffice sheets as **CSV UTF-8**, or paste copied cells as tab-separated text. `.xlsx` workbooks are not accepted directly.
- Comma, semicolon and tab separators are supported. Decimal points always work; decimal commas work with semicolon/tab separation. Do not use thousands separators, formulas or unit suffixes inside numeric cells.
- Headers must be unique. Malformed/ragged rows, nonfinite numbers, nonexistent level indices, invalid acceptance and out-of-range efficiencies are rejected with an explanation.
- `uncertainty` is an optional **one-sigma standard uncertainty** in the same units as `value`. A blank cell means unknown; it is not silently replaced with zero or sqrt(N). Nonblank uncertainties must be positive.
- The app shows measured-minus-calculated residuals and, where uncertainties are supplied, standardized residuals. The displayed sum of squared standardized residuals assumes independent Gaussian errors; it is not a fitted/reduced chi-square or a Poisson likelihood. It does not include correlated systematic errors, model errors or numerical errors.
- Negative background-subtracted measurements are rejected by this import path; they require an explicitly chosen statistical treatment rather than a silent positivity correction.
- Changes to any measurement, normalization or reaction setting mark the old comparison as stale. The downloaded JSON records the model, settings, units, canonical observations, exposure and results. Missing uncertainty values are JSON `null`.
- Blank templates contain only headers. Every measurement *example file* is **synthetic**; nuclear-table example files use the supplied magnesium example. Example numbers must not be cited as experimental observations.

Template files are in `examples/templates/`, and the same files are downloadable inside the UI. No extra installation is needed for these uploads.
