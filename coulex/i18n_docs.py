"""Long instruction pages in English and Greek (Markdown)."""

DOCS = {
    'instructions_intro': {
        'en': '''### What this app does
It calculates **Coulomb excitation**: how the electric field of one nucleus, passing another on a Rutherford
orbit, excites nuclear levels. It solves the full coupled equations for every magnetic substate, so multi-step
excitation, de-excitation and reorientation are included. From the level populations it derives cross sections,
detector counts, and comparisons with your measurements.

There are **two ways to work**, and they are kept strictly apart: built-in examples are used only when you choose
“Built-in example”. Your own calculations start empty and never contain example numbers or example results.''',
        'el': '''### Τι κάνει η εφαρμογή
Υπολογίζει τη **διέγερση Coulomb**: πώς το ηλεκτρικό πεδίο ενός πυρήνα, που κινείται σε τροχιά Rutherford κοντά
σε έναν άλλο, διεγείρει πυρηνικές στάθμες. Επιλύει πλήρως τις συζευγμένες εξισώσεις για κάθε μαγνητική υποστάθμη,
επομένως περιλαμβάνονται η διέγερση πολλαπλών βημάτων, η αποδιέγερση και ο επαναπροσανατολισμός. Από τις
πιθανότητες κατάληψης υπολογίζει ενεργές διατομές, αριθμούς γεγονότων στον ανιχνευτή και συγκρίσεις με τις
μετρήσεις σας.

Υπάρχουν **δύο τρόποι εργασίας**, αυστηρά διαχωρισμένοι: τα ενσωματωμένα παραδείγματα χρησιμοποιούνται μόνο όταν
επιλέγετε «Ενσωματωμένο παράδειγμα». Οι δικοί σας υπολογισμοί ξεκινούν κενοί και δεν περιέχουν ποτέ αριθμούς ή
αποτελέσματα από παραδείγματα.''',
    },
    'instructions_example': {
        'en': '''#### A · Explore a built-in example
1. In the sidebar, step **1 · Reaction**, keep **Built-in example** and pick a reaction. The badge tells you whether it
   uses *literature data* or is a *teaching model*.
2. Step **2 · Beam and angles** is filled from the example; change the beam energy or angles if you like.
3. Press **Run calculation**. Open **Results**, **During the collision** and **Detector yields**.
4. Open **Help and reference → Verification** to see the literature values behind the example and to run the
   benchmarks against published theory.''',
        'el': '''#### Α · Εξερεύνηση ενσωματωμένου παραδείγματος
1. Στην πλαϊνή στήλη, βήμα **1 · Αντίδραση**, αφήστε **Ενσωματωμένο παράδειγμα** και διαλέξτε αντίδραση. Η ετικέτα
   δείχνει αν χρησιμοποιεί *δεδομένα βιβλιογραφίας* ή αν είναι *διδακτικό μοντέλο*.
2. Το βήμα **2 · Δέσμη και γωνίες** συμπληρώνεται από το παράδειγμα· μπορείτε να αλλάξετε την ενέργεια ή τις γωνίες.
3. Πατήστε **Εκτέλεση υπολογισμού**. Ανοίξτε τις καρτέλες **Αποτελέσματα**, **Κατά την κρούση** και
   **Γεγονότα στον ανιχνευτή**.
4. Ανοίξτε **Βοήθεια και αναφορά → Επαλήθευση** για τις τιμές της βιβλιογραφίας του παραδείγματος και για τους
   ελέγχους έναντι δημοσιευμένης θεωρίας.''',
    },
    'instructions_own': {
        'en': '''#### B · Calculate your own reaction
1. In step **1 · Reaction** choose **My own reaction file** (one text file) or **My own tables** (levels and matrix
   elements, typed in or uploaded as CSV). Each uploader has a **Required file format** box with the exact columns,
   a blank template and an example file.
2. In step **2** enter the beam energy in **total MeV** (MeV/u × A), choose the **excited nucleus** and the CM angles.
3. Optional: step **3** for the target thickness and a stopping-power table; step **4** for numerical options.
4. The **Run calculation** button becomes active only when the reaction is complete; a checklist above the tabs
   tells you what is still missing.
5. To compare with data, open **Measurements** and upload a measurement table in one of the four formats.''',
        'el': '''#### Β · Υπολογισμός της δικής σας αντίδρασης
1. Στο βήμα **1 · Αντίδραση** επιλέξτε **Δικό μου αρχείο αντίδρασης** (ένα αρχείο κειμένου) ή **Δικοί μου πίνακες**
   (στάθμες και στοιχεία πίνακα, πληκτρολογημένα ή ως αρχεία CSV). Κάθε πεδίο μεταφόρτωσης έχει πλαίσιο
   **Απαιτούμενη μορφή αρχείου** με τις ακριβείς στήλες, κενό πρότυπο και αρχείο-παράδειγμα.
2. Στο βήμα **2** δώστε την ενέργεια δέσμης σε **συνολικά MeV** (MeV/u × A), επιλέξτε τον **πυρήνα που διεγείρεται**
   και τις γωνίες στο σύστημα κέντρου μάζας.
3. Προαιρετικά: βήμα **3** για το πάχος στόχου και πίνακα ισχύος ανάσχεσης· βήμα **4** για αριθμητικές επιλογές.
4. Το κουμπί **Εκτέλεση υπολογισμού** ενεργοποιείται μόνο όταν η αντίδραση είναι πλήρης· μια λίστα πάνω από τις
   καρτέλες δείχνει τι λείπει.
5. Για σύγκριση με πειραματικά δεδομένα, ανοίξτε την καρτέλα **Μετρήσεις** και ανεβάστε πίνακα μετρήσεων σε μία από
   τις τέσσερις μορφές.''',
    },
    'instructions_tabs': {
        'en': '''### Where everything is
The screen has two parts. **Calculation** (opens first) is where you work; **Help and reference** is opened only
when you need it, and opening it does not reset anything in Calculation.

| Calculation | Content |
|---|---|
| **Level scheme** | Levels, spins and couplings of the current reaction; for an example, a short description of its sources |
| **Results** | Level populations and cross sections versus angle (CM and lab), closest-approach check, downloads |
| **During the collision** | Rutherford orbit, driving fields, populations along the orbit, magnetic substates |
| **Detector yields** | Counts expected in a scattered-particle detector, optionally with a gamma ray |
| **Measurements** | Upload your data and compare it with the model (no fitting) |

| Help and reference | Content |
|---|---|
| **Guide** | This page |
| **File formats** | Every accepted file, with columns, units, blank templates and examples |
| **Verification** | Benchmarks against published theory, literature data of the examples, convergence checks of your run, original-code comparison |
| **Physics** | Equations, model scope and references |''',
        'el': '''### Πού βρίσκεται το καθετί
Η οθόνη έχει δύο μέρη. Ο **Υπολογισμός** (ανοίγει πρώτος) είναι ο χώρος εργασίας· η **Βοήθεια και αναφορά** ανοίγει
μόνο όταν τη χρειάζεστε, και το άνοιγμά της δεν μηδενίζει τίποτα στον Υπολογισμό.

| Υπολογισμός | Περιεχόμενο |
|---|---|
| **Σχήμα σταθμών** | Στάθμες, σπιν και συζεύξεις της τρέχουσας αντίδρασης· για παράδειγμα, σύντομη περιγραφή των πηγών του |
| **Αποτελέσματα** | Πιθανότητες κατάληψης και ενεργές διατομές ως προς τη γωνία (ΚΜ και εργαστήριο), έλεγχος ελάχιστης απόστασης, λήψεις |
| **Κατά την κρούση** | Τροχιά Rutherford, πεδία διέγερσης, πληθυσμοί κατά μήκος της τροχιάς, μαγνητικές υποστάθμες |
| **Γεγονότα στον ανιχνευτή** | Αναμενόμενα γεγονότα σε ανιχνευτή σκεδαζόμενων σωματιδίων, προαιρετικά με ακτίνα γάμμα |
| **Μετρήσεις** | Ανεβάστε τα δεδομένα σας και συγκρίνετέ τα με το μοντέλο (χωρίς προσαρμογή) |

| Βοήθεια και αναφορά | Περιεχόμενο |
|---|---|
| **Οδηγός** | Αυτή η σελίδα |
| **Μορφές αρχείων** | Κάθε αποδεκτό αρχείο, με στήλες, μονάδες, κενά πρότυπα και παραδείγματα |
| **Επαλήθευση** | Έλεγχοι έναντι δημοσιευμένης θεωρίας, δεδομένα βιβλιογραφίας των παραδειγμάτων, έλεγχοι σύγκλισης του υπολογισμού σας, σύγκριση με τον αρχικό κώδικα |
| **Φυσική** | Εξισώσεις, πεδίο ισχύος του μοντέλου και βιβλιογραφία |''',
    },
    'instructions_units': {
        'en': '''### Units at a glance
- Beam energy: **total MeV** of the beam nucleus (not MeV/u). Level energies: **MeV**.
- Angles: **degrees**; CM unless a field says *lab*. Lab angles always refer to the scattered projectile.
- Reduced matrix elements **<i‖Eλ‖f>** in **e·b^(λ/2)** (e·b for E2), with sign. For a 0+ ground state,
  |<0‖Eλ‖λ>| = √B(Eλ↑).
- Cross sections: **barn/sr** (measurements may also be mb/sr or fm²/sr). Target thickness: **mg/cm²**.
- Efficiencies and fractions: numbers between **0 and 1**, never percentages.''',
        'el': '''### Μονάδες με μια ματιά
- Ενέργεια δέσμης: **συνολικά MeV** του πυρήνα της δέσμης (όχι MeV/u). Ενέργειες σταθμών: **MeV**.
- Γωνίες: **μοίρες**· στο σύστημα κέντρου μάζας (ΚΜ), εκτός αν το πεδίο γράφει *εργαστήριο*. Οι γωνίες εργαστηρίου
  αναφέρονται πάντα στο σκεδαζόμενο βλήμα.
- Ανηγμένα στοιχεία πίνακα **<i‖Eλ‖f>** σε **e·b^(λ/2)** (e·b για E2), με πρόσημο. Για θεμελιώδη κατάσταση 0+,
  |<0‖Eλ‖λ>| = √B(Eλ↑).
- Ενεργές διατομές: **barn/sr** (οι μετρήσεις μπορούν να είναι και σε mb/sr ή fm²/sr). Πάχος στόχου: **mg/cm²**.
- Αποδόσεις και κλάσματα: αριθμοί μεταξύ **0 και 1**, ποτέ ποσοστά.''',
    },
    'instructions_faq': {
        'en': '''- **The Run button is grey.** The checklist above the tabs lists what is missing (for example the beam energy or
  the ground-state row).
- **“Every level must lie below the available centre-of-mass energy.”** The beam energy is probably in MeV/u;
  enter total MeV.
- **“violates parity selection” / “triangle rule”.** Check spins, parities and λ of that matrix element.
- **Results disappeared.** Results belong to one reaction source. Switching between an example and your own data,
  or uploading another file, starts afresh so that results are never mixed.
- **My spreadsheet is not accepted.** Save it as CSV UTF-8, use the column names exactly as in the template, and keep
  units out of the cells.
- **The surface-separation curve falls below 5 fm.** Nuclear forces may then matter; a pure Coulomb calculation may
  not apply even if it converged.
- **How do I start the app next time?** Double-click `start_mac.command` (macOS) or `start_windows.bat` (Windows) in
  the application folder, or run `./start_linux.sh` (Linux) or `python3 run.py` there in a terminal. Keep that terminal window open while you work; Ctrl+C stops
  the app. The first start installs the packages and needs internet; later starts work offline.''',
        'el': '''- **Το κουμπί εκτέλεσης είναι γκρι.** Η λίστα πάνω από τις καρτέλες δείχνει τι λείπει (π.χ. η ενέργεια δέσμης
  ή η γραμμή της θεμελιώδους κατάστασης).
- **«Κάθε στάθμη πρέπει να βρίσκεται κάτω από τη διαθέσιμη ενέργεια κέντρου μάζας.»** Πιθανότατα δώσατε MeV/u·
  δώστε συνολικά MeV.
- **«παραβιάζει τον κανόνα επιλογής ομοτιμίας» / «τριγωνικό κανόνα».** Ελέγξτε σπιν, ομοτιμίες και λ του στοιχείου.
- **Τα αποτελέσματα εξαφανίστηκαν.** Τα αποτελέσματα ανήκουν σε μία πηγή αντίδρασης. Η εναλλαγή μεταξύ παραδείγματος
  και δικών σας δεδομένων, ή η μεταφόρτωση άλλου αρχείου, ξεκινά από την αρχή ώστε να μην αναμειγνύονται ποτέ.
- **Το λογιστικό μου φύλλο δεν γίνεται δεκτό.** Αποθηκεύστε το ως CSV UTF-8, χρησιμοποιήστε τα ονόματα στηλών ακριβώς
  όπως στο πρότυπο και μην γράφετε μονάδες μέσα στα κελιά.
- **Η καμπύλη απόστασης επιφανειών πέφτει κάτω από 5 fm.** Τότε μπορεί να συνεισφέρουν πυρηνικές δυνάμεις· ένας
  καθαρά ηλεκτρομαγνητικός υπολογισμός ίσως να μην ισχύει, ακόμη κι αν συγκλίνει.
- **Πώς ξεκινώ την εφαρμογή την επόμενη φορά;** Κάντε διπλό κλικ στο `start_mac.command` (macOS) ή στο
  `start_windows.bat` (Windows) στον φάκελο της εφαρμογής, ή εκτελέστε εκεί σε τερματικό `./start_linux.sh` (Linux) ή
  `python3 run.py`. Αφήστε ανοιχτό εκείνο το
  παράθυρο τερματικού όσο εργάζεστε· το Ctrl+C σταματά την εφαρμογή. Η πρώτη εκκίνηση εγκαθιστά τα πακέτα και χρειάζεται
  σύνδεση στο διαδίκτυο· οι επόμενες λειτουργούν χωρίς σύνδεση.''',
    },
    'formats_intro': {
        'en': '''Every file the app accepts is described here: purpose, where to upload it, the exact columns and units, a
**blank template** (headers or placeholders only) and an **example file** for orientation. Example files are
never used in your own calculation. Rules for all spreadsheet (CSV) files:''',
        'el': '''Εδώ περιγράφεται κάθε αρχείο που δέχεται η εφαρμογή: σκοπός, πού ανεβαίνει, οι ακριβείς στήλες και μονάδες, ένα
**κενό πρότυπο** (μόνο επικεφαλίδες ή θέσεις προς συμπλήρωση) και ένα **αρχείο-παράδειγμα** για προσανατολισμό. Τα
αρχεία-παραδείγματα δεν χρησιμοποιούνται ποτέ στον δικό σας υπολογισμό. Κανόνες για όλα τα αρχεία λογιστικών φύλλων (CSV):''',
    },
    'verification_intro': {
        'en': '''How do we know the numbers are right? This tab provides four kinds of checks: (1) the solver is compared
with **published theory and tables** from the scientific literature; (2) the inputs of the examples are compared with
**evaluated nuclear data**; (3) **numerical convergence** is tested for your own calculation; (4) the results are
compared with **archived numerical outputs from TCLX**.''',
        'el': '''Πώς ξέρουμε ότι οι αριθμοί είναι σωστοί; Η καρτέλα παρέχει τέσσερις κατηγορίες ελέγχων: (1) ο επιλυτής
συγκρίνεται με **δημοσιευμένη θεωρία και πίνακες** της επιστημονικής βιβλιογραφίας· (2) τα δεδομένα εισόδου των
παραδειγμάτων συγκρίνονται με **αξιολογημένα πυρηνικά δεδομένα**· (3) ελέγχεται η **αριθμητική σύγκλιση** του δικού σας
υπολογισμού· (4) τα αποτελέσματα συγκρίνονται με **αποθηκευμένα αριθμητικά αποτελέσματα του TCLX**.''',
    },
    'benchmarks_intro': {
        'en': '''Each benchmark sets up a reaction whose answer is known from the literature and runs the **same solver** used
for your calculations. The reference values are computed independently (CODATA 2018 constants, B(Eλ) values,
Alder–Winther orbital integrals) or copied from published tables. Small differences of order 10⁻⁵ come from the
rounded physical constants and from rounding in the printed tables.''',
        'el': '''Κάθε έλεγχος στήνει μια αντίδραση της οποίας η απάντηση είναι γνωστή από τη βιβλιογραφία και τρέχει τον
**ίδιο επιλυτή** που χρησιμοποιείται στους υπολογισμούς σας. Οι τιμές αναφοράς υπολογίζονται ανεξάρτητα (σταθερές
CODATA 2018, τιμές B(Eλ), τροχιακά ολοκληρώματα Alder–Winther) ή αντιγράφονται από δημοσιευμένους πίνακες. Μικρές
διαφορές της τάξης του 10⁻⁵ οφείλονται στις στρογγυλοποιημένες φυσικές σταθερές και στη στρογγυλοποίηση των πινάκων.''',
    },
    'benchmarks_detail': {
        'en': '''- **Rutherford scattering** [R1911, CODATA18]: the elastic cross section with the CODATA value of e².
- **First-order perturbation theory** [AW56, AW75]: for very weak couplings the excitation probability must equal
  P = (Ze/ħv)² a^(−2λ) B(Eλ) · 16π²/(2λ+1)³ · Σμ |Yλμ(π/2,0)|² |Iλμ(θ,ξ)|². The orbital integrals Iλμ are evaluated
  independently of the solver's collision functions, for E1, E2, E3 and E4, several angles and ξ > 0. This tests the
  coupling constants, the Wigner–Eckart convention B(Eλ) = |<i‖Eλ‖f>|²/(2Ii+1), the orbit and the adiabatic phase.
- **Sudden limit, two states** [AW60 §4]: with degenerate levels (ξ = 0) at 180°, the two-state problem is exactly
  solvable, P(2+) = sin²χ with the Alder–Winther strength parameter χ. Here χ = 1, far beyond perturbation theory.
- **Sudden limit, rigid rotor** [AW60 Tables 4 and 5]: for a K = 0 rotational band at 180° and ξ = 0, Alder and
  Winther (1960) give the exact amplitudes and tabulate the probabilities P0…P12 for several values of q. The solver
  must reproduce the printed table, which tests multi-step excitation and reorientation through all diagonal and
  off-diagonal couplings.''',
        'el': '''- **Σκέδαση Rutherford** [R1911, CODATA18]: η ελαστική ενεργός διατομή με την τιμή CODATA του e².
- **Θεωρία διαταραχών πρώτης τάξης** [AW56, AW75]: για πολύ ασθενείς συζεύξεις η πιθανότητα διέγερσης πρέπει να ισούται
  με P = (Ze/ħv)² a^(−2λ) B(Eλ) · 16π²/(2λ+1)³ · Σμ |Yλμ(π/2,0)|² |Iλμ(θ,ξ)|². Τα τροχιακά ολοκληρώματα Iλμ υπολογίζονται
  ανεξάρτητα από τις συναρτήσεις κρούσης του επιλυτή, για E1, E2, E3 και E4, σε διάφορες γωνίες και ξ > 0. Ελέγχονται
  οι σταθερές σύζευξης, η σύμβαση Wigner–Eckart B(Eλ) = |<i‖Eλ‖f>|²/(2Ii+1), η τροχιά και η αδιαβατική φάση.
- **Στιγμιαίο όριο, δύο καταστάσεις** [AW60 §4]: με εκφυλισμένες στάθμες (ξ = 0) στις 180°, το πρόβλημα δύο καταστάσεων
  λύνεται ακριβώς, P(2+) = sin²χ με την παράμετρο ισχύος χ των Alder–Winther. Εδώ χ = 1, πολύ πέρα από τη θεωρία διαταραχών.
- **Στιγμιαίο όριο, άκαμπτος στροφέας** [AW60 Πίνακες 4 και 5]: για περιστροφική ζώνη K = 0 στις 180° και ξ = 0, οι
  Alder και Winther (1960) δίνουν τα ακριβή πλάτη και πινακοποιούν τις πιθανότητες P0…P12 για διάφορες τιμές του q. Ο
  επιλυτής πρέπει να αναπαράγει τον τυπωμένο πίνακα· έτσι ελέγχεται η διέγερση πολλαπλών βημάτων και ο
  επαναπροσανατολισμός μέσω όλων των διαγώνιων και μη διαγώνιων συζεύξεων.''',
    },
    'original_summary': {
        'en': '''The comparison with [TCLX](https://github.com/jhenderson88/TCLX) uses two inputs and matched polarization settings
(`reference`). The app uses the literature mass convention (`standard`), so its polarized results differ.
The report below records the tested angles and errors. Its reference values were generated using a minimal ROOT adapter. Only the numerical results are retained; source and build tools are no longer included.
TCLX has no licence, so its two input files are not distributed either: to rerun the comparison, download them as
described in `validation/tclx_inputs/README.md`.''',
        'el': '''Η σύγκριση με το [TCLX](https://github.com/jhenderson88/TCLX) χρησιμοποιεί δύο σύνολα δεδομένων και ίδιες ρυθμίσεις
πόλωσης (`reference`). Η εφαρμογή χρησιμοποιεί τη σύμβαση μάζας της βιβλιογραφίας (`standard`), επομένως τα αποτελέσματα με πόλωση διαφέρουν.
Η παρακάτω αναφορά καταγράφει τις γωνίες και τα σφάλματα. Οι τιμές αναφοράς παρήχθησαν με ελάχιστο προσαρμογέα ROOT. Διατηρούνται μόνο τα αριθμητικά αποτελέσματα· ο πηγαίος κώδικας και τα εργαλεία μεταγλώττισης έχουν αφαιρεθεί.
Το TCLX δεν έχει άδεια χρήσης, επομένως ούτε τα δύο αρχεία εισόδου του διανέμονται: για να επαναλάβετε τη σύγκριση,
κατεβάστε τα όπως περιγράφεται στο `validation/tclx_inputs/README.md`.''',
    },
    'physics_steps': {
        'en': r'''### From a level scheme to a detector count
1. **Describe the nucleus.** Each level has an energy, spin and parity. A reduced electric matrix element specifies a coupling, including its sign.
2. **Resolve magnetic substates.** A level of spin $J$ contains $2J+1$ substates. Wigner 3j symbols impose angular-momentum selection rules.
3. **Follow a Rutherford orbit.** The CM angle determines $\epsilon=1/\sin(\theta/2)$. The orbit parameter $\omega=0$ marks closest approach.
4. **Integrate complex amplitudes.** All connected states evolve together; this includes repeated excitation, de-excitation and reorientation.
5. **Sum probabilities.** Sum $|a|^2$ over final substates and average over equally populated initial ground-state substates.
6. **Calculate an observable.** Multiply by the level-dependent Rutherford factor, integrate detector solid angle, and multiply by target atoms and incident particles.''',
        'el': r'''### Από το σχήμα σταθμών στον αριθμό γεγονότων
1. **Περιγραφή του πυρήνα.** Κάθε στάθμη έχει ενέργεια, σπιν και ομοτιμία. Ένα ανηγμένο ηλεκτρικό στοιχείο πίνακα ορίζει μια σύζευξη, μαζί με το πρόσημό της.
2. **Μαγνητικές υποστάθμες.** Μια στάθμη με σπιν $J$ έχει $2J+1$ υποστάθμες. Τα σύμβολα 3j του Wigner επιβάλλουν τους κανόνες επιλογής στροφορμής.
3. **Τροχιά Rutherford.** Η γωνία ΚΜ καθορίζει το $\epsilon=1/\sin(\theta/2)$. Η παράμετρος τροχιάς $\omega=0$ αντιστοιχεί στην ελάχιστη απόσταση.
4. **Ολοκλήρωση μιγαδικών πλατών.** Όλες οι συνδεδεμένες καταστάσεις εξελίσσονται μαζί· έτσι περιλαμβάνονται επαναλαμβανόμενη διέγερση, αποδιέγερση και επαναπροσανατολισμός.
5. **Άθροιση πιθανοτήτων.** Αθροίζεται το $|a|^2$ στις τελικές υποστάθμες και λαμβάνεται μέσος όρος στις ισοπίθανες αρχικές υποστάθμες της θεμελιώδους κατάστασης.
6. **Παρατηρήσιμο μέγεθος.** Πολλαπλασιάζεται με τον παράγοντα Rutherford κάθε στάθμης, ολοκληρώνεται στη στερεά γωνία του ανιχνευτή και πολλαπλασιάζεται με τα άτομα του στόχου και τα σωματίδια της δέσμης.''',
    },
    'physics_scope': {
        'en': '''**Numerics:** SciPy DOP853 with explicit tolerances; exact SymPy Wigner symbols converted to double precision;
sparse coupling operators. No Numerical Recipes implementation is used. The physical constants have finite precision; independent benchmark references use CODATA 2018 values.

**Polarization:** D = d Ecm A/Z² uses the excited nucleus. The coefficient d defaults to 0.005 MeV⁻¹ and can be changed or disabled. It is a model assumption, not a measured universal constant. See [Orce (2016), Eq. (4) and footnote 1](https://arxiv.org/abs/1510.04087) for the mass convention and discussion of alternative strengths.

**Model scope:** semiclassical electromagnetic E1–E4 excitation of one nucleus at a time. No magnetic transitions,
nuclear-force coupling, mutual excitation or relativistic trajectory. The Research tab adds explicit gamma networks,
pure-electric rest-frame angular response, shape invariants and parameter fitting; see docs/RESEARCH.md for assumptions. The input K column is
retained as metadata. Numerical convergence does not establish the physical validity of the model.

**Try in class:** set off-diagonal E2 elements to zero; reverse a diagonal quadrupole element; double a weak
transition element and test approximate fourfold excitation; compare 30°, 90° and 150°; halve the angle step before
trusting a detector yield; run the teaching rotor at 180° and compare with Alder & Winther's Table 5.''',
        'el': '''**Αριθμητικές μέθοδοι:** SciPy DOP853 με ρητές ανοχές· ακριβή σύμβολα Wigner της SymPy μετατρεπόμενα σε διπλή
ακρίβεια· αραιοί τελεστές σύζευξης. Δεν χρησιμοποιείται κώδικας Numerical Recipes. Οι φυσικές σταθερές έχουν πεπερασμένη ακρίβεια· οι ανεξάρτητες τιμές αναφοράς χρησιμοποιούν CODATA 2018.

**Πόλωση:** D = d Ecm A/Z² με A και Z του πυρήνα που διεγείρεται. Ο συντελεστής d έχει προεπιλογή 0,005 MeV⁻¹ και μπορεί να αλλάξει ή να απενεργοποιηθεί. Είναι υπόθεση μοντέλου, όχι μετρημένη καθολική σταθερά. Δείτε [Orce (2016), εξ. (4) και υποσημείωση 1](https://arxiv.org/abs/1510.04087) για τη σύμβαση μάζας και εναλλακτικούς συντελεστές.

**Πεδίο ισχύος:** ημικλασική ηλεκτρομαγνητική διέγερση E1–E4 ενός πυρήνα κάθε φορά. Δεν περιλαμβάνονται μαγνητικές
μεταβάσεις, σύζευξη μέσω πυρηνικών δυνάμεων, ταυτόχρονη διέγερση και των δύο πυρήνων ή σχετικιστική τροχιά. Η καρτέλα Έρευνα προσθέτει ρητά δίκτυα γάμμα, αμιγώς ηλεκτρική γωνιακή απόκριση στο σύστημα ηρεμίας, αναλλοίωτες σχήματος και προσαρμογή παραμέτρων· δείτε docs/RESEARCH.md για τις παραδοχές. Η στήλη K διατηρείται ως μεταδεδομένο. Η αριθμητική σύγκλιση δεν αποδεικνύει τη
φυσική εγκυρότητα του μοντέλου.

**Δοκιμάστε στην τάξη:** μηδενίστε τα μη διαγώνια στοιχεία E2· αντιστρέψτε το πρόσημο ενός διαγώνιου τετραπολικού
στοιχείου· διπλασιάστε ένα ασθενές στοιχείο μετάβασης και ελέγξτε την περίπου τετραπλάσια διέγερση· συγκρίνετε
30°, 90° και 150°· υποδιπλασιάστε το γωνιακό βήμα πριν εμπιστευτείτε αριθμό γεγονότων· τρέξτε τον διδακτικό στροφέα
στις 180° και συγκρίνετε με τον Πίνακα 5 των Alder & Winther.''',
    },
}
