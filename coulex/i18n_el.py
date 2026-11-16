"""Greek interface text, keyed by the English original.

Terminology follows Greek physics usage: διέγερση Coulomb, ενεργός διατομή,
(ανηγμένο) στοιχείο πίνακα, βλήμα / στόχος, σύστημα κέντρου μάζας (ΚΜ),
επαναπροσανατολισμός, ισχύς ανάσχεσης, άκαμπτος στροφέας.
"""

EL = {
    'Polarization strength d (MeV⁻¹)': 'Συντελεστής πόλωσης d (MeV⁻¹)',
    'D = d Ecm A/Z² for the excited nucleus. The default 0.005 is a model choice; see Physics for the literature and limitations.':
        'D = d Ecm A/Z² για τον πυρήνα που διεγείρεται. Η προεπιλογή 0,005 είναι επιλογή μοντέλου· δείτε τη Φυσική για τη βιβλιογραφία και τους περιορισμούς.',
    'Unknown polarization convention.': 'Άγνωστη σύμβαση πόλωσης.',
    # ---- general layout -------------------------------------------------------------------------
    'Coulomb Excitation Lab': 'Εργαστήριο Διέγερσης Coulomb',
    'An interactive laboratory for nuclear physics':
        'Ένα διαδραστικό εργαστήριο πυρηνικής φυσικής',
    'Choose a reaction': 'Επιλέξτε αντίδραση',
    'Sidebar step 1: a built-in example, your own reaction file, or your own tables.':
        'Πλαϊνή στήλη, βήμα 1: ενσωματωμένο παράδειγμα, δικό σας αρχείο αντίδρασης ή δικοί σας πίνακες.',
    'Set the beam and angles': 'Ορίστε δέσμη και γωνίες',
    'Sidebar step 2: beam energy in total MeV, the excited nucleus and the CM angle grid.':
        'Πλαϊνή στήλη, βήμα 2: ενέργεια δέσμης σε συνολικά MeV, ο πυρήνας που διεγείρεται και οι γωνίες ΚΜ.',
    'Run the calculation': 'Εκτελέστε τον υπολογισμό',
    'Press “Run calculation” at the bottom of the sidebar.':
        'Πατήστε «Εκτέλεση υπολογισμού» στο κάτω μέρος της πλαϊνής στήλης.',
    'Explore and verify': 'Εξερευνήστε και επαληθεύστε',
    'Results appear in the Calculation tabs. Help and reference → Verification checks them against published theory.':
        'Τα αποτελέσματα εμφανίζονται στις καρτέλες «Υπολογισμός». Η «Βοήθεια και αναφορά → Επαλήθευση» τα ελέγχει έναντι '
        'δημοσιευμένης θεωρίας.',
    'New here? The **Help and reference** tab has the step-by-step guide, the file formats, the physics and the '
    'verification of results.':
        'Πρώτη φορά εδώ; Η καρτέλα **Βοήθεια και αναφορά** περιέχει τον οδηγό βήμα προς βήμα, τις μορφές αρχείων, τη '
        'φυσική και την επαλήθευση των αποτελεσμάτων.',
    'Calculation': 'Υπολογισμός',
    'Help and reference': 'Βοήθεια και αναφορά',
    'Guide': 'Οδηγός',
    'Level scheme': 'Σχήμα σταθμών',
    'Results': 'Αποτελέσματα',
    'During the collision': 'Κατά την κρούση',
    'Detector yields': 'Γεγονότα στον ανιχνευτή',
    'Measurements': 'Μετρήσεις',
    'Verification': 'Επαλήθευση',
    'File formats': 'Μορφές αρχείων',
    'Physics': 'Φυσική',
    'References': 'Βιβλιογραφία',
    'Troubleshooting': 'Αντιμετώπιση προβλημάτων',

    # ---- sidebar: step 1 ---------------------------------------------------------------------------
    '1 · Reaction': '1 · Αντίδραση',
    'Reaction source': 'Πηγή αντίδρασης',
    'Built-in example': 'Ενσωματωμένο παράδειγμα',
    'My own reaction file': 'Δικό μου αρχείο αντίδρασης',
    'My own tables': 'Δικοί μου πίνακες',
    'Ready-made reactions with documented sources': 'Έτοιμες αντιδράσεις με τεκμηριωμένες πηγές',
    'Upload a reaction text file (.txt/.dat)': 'Μεταφόρτωση αρχείου αντίδρασης (.txt/.dat)',
    'Type or upload levels and matrix elements': 'Πληκτρολόγηση ή μεταφόρτωση σταθμών και στοιχείων πίνακα',
    'Example': 'Παράδειγμα',
    'Literature data': 'Δεδομένα βιβλιογραφίας',
    'Teaching model': 'Διδακτικό μοντέλο',
    'View or edit the input text': 'Προβολή ή επεξεργασία του κειμένου εισόδου',
    'Reaction input text': 'Κείμενο εισόδου αντίδρασης',
    'Beam energy is total MeV. Level and transition indices start at 1. Eλ elements use e·b^(λ/2). Text after # is a comment.':
        'Η ενέργεια δέσμης είναι σε συνολικά MeV. Η αρίθμηση σταθμών και μεταβάσεων ξεκινά από το 1. Τα στοιχεία Eλ είναι '
        'σε e·b^(λ/2). Ό,τι ακολουθεί το # είναι σχόλιο.',
    'Download reaction text': 'Λήψη κειμένου αντίδρασης',
    'Upload your reaction file': 'Ανεβάστε το αρχείο αντίδρασης',
    'No file yet. Nothing is calculated until you upload your own input.':
        'Δεν υπάρχει ακόμη αρχείο. Τίποτα δεν υπολογίζεται πριν ανεβάσετε τη δική σας είσοδο.',
    'Upload your reaction file (sidebar, step 1).': 'Ανεβάστε το αρχείο αντίδρασης (πλαϊνή στήλη, βήμα 1).',
    'The file is not UTF-8 text. Save it as plain text (UTF-8) and upload it again.':
        'Το αρχείο δεν είναι κείμενο UTF-8. Αποθηκεύστε το ως απλό κείμενο (UTF-8) και ανεβάστε το ξανά.',
    'Correct the reaction input: see the error message in the sidebar.':
        'Διορθώστε την είσοδο της αντίδρασης: δείτε το μήνυμα σφάλματος στην πλαϊνή στήλη.',
    'Correct the reaction input (see the error in the sidebar).':
        'Διορθώστε την είσοδο της αντίδρασης (δείτε το σφάλμα στην πλαϊνή στήλη).',
    'Correct the reaction input first.': 'Διορθώστε πρώτα την είσοδο της αντίδρασης.',
    'Correct the level or matrix-element table (see the error above the tabs).':
        'Διορθώστε τον πίνακα σταθμών ή στοιχείων πίνακα (δείτε το σφάλμα πάνω από τις καρτέλες).',
    'Enter the nuclei here and the level scheme on the main page.':
        'Δώστε εδώ τους πυρήνες και το σχήμα σταθμών στην κύρια σελίδα.',
    'Reaction title': 'Τίτλος αντίδρασης',
    'e.g. my experiment': 'π.χ. το πείραμά μου',
    'My reaction': 'Η αντίδρασή μου',
    'Projectile Z': 'Z βλήματος',
    'Projectile A': 'A βλήματος',
    'Target Z': 'Z στόχου',
    'Target A': 'A στόχου',
    'Enter {name} (sidebar, step 1).': 'Συμπληρώστε: {name} (πλαϊνή στήλη, βήμα 1).',
    'Your level scheme': 'Το σχήμα σταθμών σας',
    'Fill in both tables (add rows with **+**), load levels from public data, or upload CSV files. They start empty: '
    'nothing from the examples is used here. Measured cross sections or counts belong in the **Measurements** tab, '
    'not in these tables.':
        'Συμπληρώστε και τους δύο πίνακες (προσθέστε γραμμές με **+**), φορτώστε σταθμούς από δημόσια δεδομένα ή ανεβάστε '
        'αρχεία CSV. Ξεκινούν κενοί: τίποτα από τα παραδείγματα δεν χρησιμοποιείται εδώ. Μετρημένες ενεργές διατομές ή '
        'αριθμοί γεγονότων ανήκουν στην καρτέλα **Μετρήσεις**, όχι σε αυτούς τους πίνακες.',
    'Load levels from public data': 'Φόρτωση σταθμών από δημόσια δεδομένα',
    'Downloads adopted energy levels and spins from the IAEA Nuclear Data Services (ENSDF). The request is made only when '
    'you press the button. The result fills the level table, which you can then edit.':
        'Λαμβάνει τις αξιολογημένες ενέργειες σταθμών και τα σπιν από τις Υπηρεσίες Πυρηνικών Δεδομένων του IAEA (ENSDF). Το '
        'αίτημα γίνεται μόνο όταν πατήσετε το κουμπί. Το αποτέλεσμα συμπληρώνει τον πίνακα σταθμών, τον οποίο μπορείτε '
        'στη συνέχεια να επεξεργαστείτε.',
    'Nucleus to load': 'Πυρήνας για φόρτωση',
    'Enter the Z and A of this nucleus first (sidebar, step 1).':
        'Εισαγάγετε πρώτα τα Z και A αυτού του πυρήνα (πλαϊνή στήλη, βήμα 1).',
    'Maximum excitation energy to load (MeV)': 'Μέγιστη ενέργεια διέγερσης για φόρτωση (MeV)',
    'Load levels': 'Φόρτωση σταθμών',
    'Remove loaded levels': 'Αφαίρεση φορτωμένων σταθμών',
    'Could not load levels ({reason}). Enter the levels by hand or upload a CSV file.':
        'Δεν ήταν δυνατή η φόρτωση των σταθμών ({reason}). Εισαγάγετε τους σταθμούς με το χέρι ή ανεβάστε αρχείο CSV.',
    'Loaded {count} levels for {nuclide} ({source}, retrieved {date}).':
        'Φορτώθηκαν {count} στάθμες για τον {nuclide} ({source}, ανάκτηση {date}).',
    'Public data give energies and spins only. Enter the matrix elements (couplings) yourself; the built-in examples '
    'show evaluated B(E2) values as a guide.':
        'Τα δημόσια δεδομένα δίνουν μόνο ενέργειες και σπιν. Εισαγάγετε εσείς τα στοιχεία πίνακα (συζεύξεις)· τα '
        'ενσωματωμένα παραδείγματα δείχνουν αξιολογημένες τιμές B(E2) ως οδηγό.',
    'Not loaded: {count} entries': 'Δεν φορτώθηκαν: {count} καταχωρίσεις',
    'energy uncertain or missing': 'ενέργεια αβέβαιη ή ελλιπής',
    'spin not unique': 'σπιν όχι μοναδικό',
    'Nuclear levels': 'Πυρηνικές στάθμες',
    'Electric matrix elements': 'Ηλεκτρικά στοιχεία πίνακα',
    'Upload a CSV file (optional)': 'Μεταφόρτωση αρχείου CSV (προαιρετικά)',
    'Add at least the ground state to the level table (level 1, energy 0 MeV).':
        'Προσθέστε τουλάχιστον τη θεμελιώδη κατάσταση στον πίνακα σταθμών (στάθμη 1, ενέργεια 0 MeV).',

    # ---- sidebar: steps 2-4 ------------------------------------------------------------------------
    '2 · Beam and angles': '2 · Δέσμη και γωνίες',
    'Beam energy (total MeV)': 'Ενέργεια δέσμης (συνολικά MeV)',
    'Kinetic energy of the whole beam nucleus: MeV/u × mass number.':
        'Κινητική ενέργεια ολόκληρου του πυρήνα της δέσμης: MeV/u × μαζικός αριθμός.',
    '= {value} MeV per nucleon': '= {value} MeV ανά νουκλεόνιο',
    'Enter the beam energy (sidebar, step 2).': 'Δώστε την ενέργεια δέσμης (πλαϊνή στήλη, βήμα 2).',
    'Excited nucleus': 'Πυρήνας που διεγείρεται',
    'Projectile': 'Βλήμα',
    'Target': 'Στόχος',
    'The level scheme belongs to the excited nucleus.': 'Το σχήμα σταθμών ανήκει στον πυρήνα που διεγείρεται.',
    'Use angle range from input file': 'Χρήση του εύρους γωνιών του αρχείου εισόδου',
    'Minimum CM angle (°)': 'Ελάχιστη γωνία ΚΜ (°)',
    'Maximum CM angle (°)': 'Μέγιστη γωνία ΚΜ (°)',
    'Angle step (°)': 'Βήμα γωνίας (°)',
    'Smaller steps give smoother curves and more accurate detector integrals, but take longer.':
        'Μικρότερο βήμα δίνει ομαλότερες καμπύλες και ακριβέστερα ολοκληρώματα ανιχνευτή, αλλά απαιτεί περισσότερο χρόνο.',
    '3 · Target and energy loss': '3 · Στόχος και απώλεια ενέργειας',
    'Target thickness (mg/cm²)': 'Πάχος στόχου (mg/cm²)',
    'Used for yields and count comparisons.': 'Χρησιμοποιείται για αριθμούς γεγονότων και συγκρίσεις μετρήσεων.',
    'Energy loss through a thick target (optional)': 'Απώλεια ενέργειας σε παχύ στόχο (προαιρετικά)',
    'Without a table, a thin target at the selected beam energy is assumed.':
        'Χωρίς πίνακα θεωρείται λεπτός στόχος στην επιλεγμένη ενέργεια δέσμης.',
    'Stopping-power CSV': 'Αρχείο CSV ισχύος ανάσχεσης',
    'Depth quadrature points': 'Σημεία ολοκλήρωσης στο βάθος του στόχου',
    '4 · Physics and numerical options': '4 · Επιλογές φυσικής και αριθμητικών μεθόδων',
    'Include electric dipole polarization': 'Συμπερίληψη ηλεκτρικής διπολικής πόλωσης',
    'Relative tolerance': 'Σχετική ανοχή',
    'Extra orbit range Δω': 'Επιπλέον εύρος τροχιάς Δω',
    'The absolute tolerance is rtol/1000. Test the finite orbit range separately in Help and reference → Verification.':
        'Η απόλυτη ανοχή είναι rtol/1000. Ελέγξτε ξεχωριστά το πεπερασμένο εύρος της τροχιάς στη «Βοήθεια και αναφορά → '
        'Επαλήθευση».',
    'Run calculation': 'Εκτέλεση υπολογισμού',
    'Complete the steps above to enable the calculation.': 'Ολοκληρώστε τα παραπάνω βήματα για να ενεργοποιηθεί ο υπολογισμός.',
    'Correct the error shown above.': 'Διορθώστε το σφάλμα που εμφανίζεται παραπάνω.',
    'Integrating coupled amplitudes…': 'Ολοκλήρωση των συζευγμένων πλατών…',
    'Calculation finished. Open the Results tab.': 'Ο υπολογισμός ολοκληρώθηκε. Ανοίξτε την καρτέλα «Αποτελέσματα».',
    'Your reaction is not complete yet': 'Η αντίδρασή σας δεν είναι ακόμη πλήρης',
    'Settings have changed. Run the calculation to update the results; the plots below show the last completed run.':
        'Οι ρυθμίσεις άλλαξαν. Εκτελέστε ξανά τον υπολογισμό για ενημέρωση· τα διαγράμματα δείχνουν τον τελευταίο '
        'ολοκληρωμένο υπολογισμό.',

    # ---- level scheme tab --------------------------------------------------------------------------
    'Define a reaction in the sidebar to see its level scheme.':
        'Ορίστε μια αντίδραση στην πλαϊνή στήλη για να δείτε το σχήμα σταθμών της.',
    'About this example': 'Σχετικά με το παράδειγμα',
    'Sources: {sources}. Details are in Help and reference → Verification.':
        'Πηγές: {sources}. Λεπτομέρειες στη «Βοήθεια και αναφορά → Επαλήθευση».',
    'Your own reaction': 'Η δική σας αντίδραση',
    'Centre-of-mass energy': 'Ενέργεια κέντρου μάζας',
    'Magnetic substates': 'Μαγνητικές υποστάθμες',
    'Level scheme with transition connections': 'Σχήμα σταθμών με τις μεταβάσεις',
    'Line segments are levels; connecting lines represent nonzero transition matrix elements. Diagonal elements affect '
    'reorientation even though they are not drawn as connections.':
        'Τα οριζόντια τμήματα είναι στάθμες· οι γραμμές σύνδεσης είναι μη μηδενικά στοιχεία πίνακα μετάβασης. Τα διαγώνια '
        'στοιχεία επηρεάζουν τον επαναπροσανατολισμό, αν και δεν σχεδιάζονται ως συνδέσεις.',
    'level': 'στάθμη',
    'spin': 'σπιν',
    'parity': 'ομοτιμία',
    'initial': 'αρχική',
    'final': 'τελική',
    'matrix element [e·b^(λ/2)]': 'στοιχείο πίνακα [e·b^(λ/2)]',
    'Level table': 'Πίνακας σταθμών',
    'Matrix-element table': 'Πίνακας στοιχείων πίνακα',
    'Download the input text': 'Λήψη του κειμένου εισόδου',
    'The text download preserves the text editor. The results JSON additionally records all sidebar settings.':
        'Η λήψη κειμένου διατηρεί το περιεχόμενο του επεξεργαστή. Το αρχείο JSON των αποτελεσμάτων καταγράφει επιπλέον όλες '
        'τις ρυθμίσεις της πλαϊνής στήλης.',
    'Spin J (ℏ)': 'Σπιν J (ℏ)',
    'Excitation energy (MeV)': 'Ενέργεια διέγερσης (MeV)',
    'Levels and electromagnetic connections': 'Στάθμες και ηλεκτρομαγνητικές συζεύξεις',

    # ---- results / dynamics / yields ---------------------------------------------------------------
    '{count} angles': '{count} γωνίες',
    'Levels to plot': 'Στάθμες στο διάγραμμα',
    'Maximum probability drift': 'Μέγιστη απόκλιση διατήρησης πιθανότητας',
    'Beam energy sampled': 'Ενέργειες δέσμης που υπολογίστηκαν',
    'Depth samples': 'Δείγματα βάθους',
    'CM scattering angle (°)': 'Γωνία σκέδασης ΚΜ (°)',
    'Level population probability': 'Πιθανότητα κατάληψης στάθμης',
    'Population probability versus angle': 'Πιθανότητα κατάληψης ως προς τη γωνία',
    'Logarithmic cross-section axis': 'Λογαριθμικός άξονας ενεργού διατομής',
    'Differential cross section versus angle': 'Διαφορική ενεργός διατομή ως προς τη γωνία',
    'Scattered projectile lab angle (°)': 'Γωνία εργαστηρίου του σκεδαζόμενου βλήματος (°)',
    'dσ/dΩlab per branch (barn/sr)': 'dσ/dΩ εργαστηρίου ανά κλάδο (barn/sr)',
    'Lab-frame cross section': 'Ενεργός διατομή στο σύστημα εργαστηρίου',
    'Lab curves include the solid-angle Jacobian and exit-channel speed. For a heavy projectile, two CM branches may reach '
    'the same lab angle; sum their contributions. Detector integration below includes both branches without sampling the '
    'singular turning point.':
        'Οι καμπύλες εργαστηρίου περιλαμβάνουν την Ιακωβιανή στερεάς γωνίας και την ταχύτητα του καναλιού εξόδου. Για βαρύ '
        'βλήμα, δύο κλάδοι ΚΜ μπορεί να αντιστοιχούν στην ίδια γωνία εργαστηρίου· οι συνεισφορές τους αθροίζονται. Η '
        'ολοκλήρωση του ανιχνευτή περιλαμβάνει και τους δύο κλάδους χωρίς δειγματοληψία του ιδιάζοντος σημείου αναστροφής.',
    'Surface separation': 'Απόσταση επιφανειών',
    'Traditional 5 fm guideline': 'Παραδοσιακό όριο 5 fm',
    'Surface separation at closest approach (fm)': 'Απόσταση επιφανειών στην ελάχιστη προσέγγιση (fm)',
    'Surface separation versus angle': 'Απόσταση επιφανειών ως προς τη γωνία',
    'The nuclear-radius estimate is 1.25 A^(1/3) fm. Below the guideline, nuclear interactions may invalidate a pure Coulomb '
    'calculation. For energy-loss runs this plot uses the incident energy, the smallest separation in the target.':
        'Η εκτίμηση της πυρηνικής ακτίνας είναι 1,25 A^(1/3) fm. Κάτω από το όριο, οι πυρηνικές αλληλεπιδράσεις μπορεί να '
        'ακυρώνουν έναν καθαρά ηλεκτρομαγνητικό υπολογισμό. Με απώλεια ενέργειας, το διάγραμμα χρησιμοποιεί την ενέργεια '
        'εισόδου, δηλαδή τη μικρότερη απόσταση μέσα στον στόχο.',
    'Download results CSV': 'Λήψη αποτελεσμάτων (CSV)',
    'Download reproducible calculation JSON': 'Λήψη αναπαραγώγιμου υπολογισμού (JSON)',
    'Numerical results table': 'Πίνακας αριθμητικών αποτελεσμάτων',
    'Numerical results': 'Αριθμητικά αποτελέσματα',
    'Inspect a CM angle (°)': 'Εξέταση γωνίας ΚΜ (°)',
    'This view follows one collision at the selected incident energy. A depth-averaged yield is a separate calculation.':
        'Η προβολή αυτή ακολουθεί μία κρούση στην επιλεγμένη ενέργεια εισόδου. Ο μέσος όρος στο βάθος του στόχου είναι '
        'ξεχωριστός υπολογισμός.',
    'Rutherford trajectory': 'Τροχιά Rutherford',
    'Electric collision functions': 'Ηλεκτρικές συναρτήσεις κρούσης',
    'Follow the amplitudes': 'Παρακολούθηση των πλατών',
    'Resolving the collision history…': 'Υπολογισμός της χρονικής εξέλιξης της κρούσης…',
    'Orbit parameter ω (0 = closest approach)': 'Παράμετρος τροχιάς ω (0 = ελάχιστη απόσταση)',
    'Instantaneous level population': 'Στιγμιαίος πληθυσμός στάθμης',
    'Population during the collision': 'Πληθυσμοί κατά την κρούση',
    'Transient populations need not grow monotonically: the coupled amplitudes interfere and can return population to lower levels.':
        'Οι μεταβατικοί πληθυσμοί δεν αυξάνονται κατ\' ανάγκη μονότονα: τα συζευγμένα πλάτη συμβάλλουν και μπορούν να '
        'επιστρέψουν πληθυσμό σε χαμηλότερες στάθμες.',
    'Inspect magnetic substates': 'Εξέταση μαγνητικών υποσταθμών',
    'Magnetic quantum number m (ℏ)': 'Μαγνητικός κβαντικός αριθμός m (ℏ)',
    'Final substate probability': 'Τελική πιθανότητα υποστάθμης',
    'Final magnetic-substate populations': 'Τελικοί πληθυσμοί μαγνητικών υποσταθμών',
    'Relative Rutherford orbit': 'Σχετική τροχιά Rutherford',
    'Partner nucleus': 'Πυρήνας-εταίρος',
    'Closest approach': 'Ελάχιστη απόσταση',
    'Relative trajectory at θcm = {angle}°': 'Σχετική τροχιά για θcm = {angle}°',
    'imaginary part': 'φανταστικό μέρος',
    'real part': 'πραγματικό μέρος',
    'Collision function Q (dimensionless)': 'Συνάρτηση κρούσης Q (αδιάστατη)',
    'E{lam} driving field': 'Πεδίο διέγερσης E{lam}',
    'Integrate the populated cross section over a **scattered-projectile detector annulus**. The integral uses CM solid '
    'angle and the actual lab acceptance at every target depth.':
        'Ολοκλήρωση της ενεργού διατομής σε **δακτυλιοειδή ανιχνευτή του σκεδαζόμενου βλήματος**. Το ολοκλήρωμα γίνεται '
        'στη στερεά γωνία ΚΜ με την πραγματική αποδοχή εργαστηρίου σε κάθε βάθος του στόχου.',
    'Detector lab minimum (°)': 'Ελάχιστη γωνία ανιχνευτή, εργαστήριο (°)',
    'Detector lab maximum (°)': 'Μέγιστη γωνία ανιχνευτή, εργαστήριο (°)',
    'Azimuth coverage fraction': 'Κλάσμα αζιμουθιακής κάλυψης',
    'Beam particles per second': 'Σωματίδια δέσμης ανά δευτερόλεπτο',
    'Experiment duration (days)': 'Διάρκεια πειράματος (ημέρες)',
    'Particle detection efficiency': 'Απόδοση ανίχνευσης σωματιδίων',
    'Target areal density: {thickness} mg/cm² (from the completed run).':
        'Επιφανειακή πυκνότητα στόχου: {thickness} mg/cm² (από τον ολοκληρωμένο υπολογισμό).',
    'Estimate a direct gamma coincidence for a selected level': 'Εκτίμηση άμεσης σύμπτωσης γάμμα για επιλεγμένη στάθμη',
    'Gamma-emitting level': 'Στάθμη που εκπέμπει γάμμα',
    'Direct gamma branching fraction': 'Λόγος διακλάδωσης άμεσης γάμμα',
    'Absolute gamma efficiency': 'Απόλυτη απόδοση ανίχνευσης γάμμα',
    'Direct branch only; feeding cascades, internal conversion, and gamma angular correlations are not inferred from excitation matrix elements.':
        'Μόνο ο άμεσος κλάδος· η τροφοδοσία από καταρράκτες, η εσωτερική μετατροπή και οι γωνιακές συσχετίσεις γάμμα δεν '
        'προκύπτουν από τα στοιχεία πίνακα διέγερσης.',
    'Integrate detector yields': 'Υπολογισμός γεγονότων στον ανιχνευτή',
    'Check angular convergence by halving the CM angle step and recalculating. A tight ODE tolerance alone does not control detector-integration error.':
        'Ελέγξτε τη γωνιακή σύγκλιση υποδιπλασιάζοντας το βήμα γωνίας ΚΜ και επαναλαμβάνοντας τον υπολογισμό. Μια αυστηρή '
        'ανοχή ΣΔΕ δεν ελέγχει από μόνη της το σφάλμα ολοκλήρωσης του ανιχνευτή.',
    'Press “Run calculation” in the sidebar to fill this view. Results are only shown for the reaction that produced them.':
        'Πατήστε «Εκτέλεση υπολογισμού» στην πλαϊνή στήλη για να συμπληρωθεί η προβολή. Τα αποτελέσματα εμφανίζονται μόνο '
        'για την αντίδραση που τα παρήγαγε.',

    # ---- measurements -------------------------------------------------------------------------------
    'Compare your measurements with the model': 'Σύγκριση των μετρήσεών σας με το μοντέλο',
    'Use **one experimental run per table**: the same reaction, beam energy and target conditions. The comparison uses '
    'the reaction and settings currently selected in the sidebar. Nothing is fitted: the matrix elements stay as entered.':
        'Χρησιμοποιήστε **ένα πειραματικό σύνολο ανά πίνακα**: ίδια αντίδραση, ενέργεια δέσμης και συνθήκες στόχου. Η '
        'σύγκριση χρησιμοποιεί την αντίδραση και τις ρυθμίσεις της πλαϊνής στήλης. Δεν γίνεται προσαρμογή: τα στοιχεία '
        'πίνακα μένουν όπως δόθηκαν.',
    'Define a complete reaction in the sidebar first; measurements are compared with that model.':
        'Ορίστε πρώτα μια πλήρη αντίδραση στην πλαϊνή στήλη· οι μετρήσεις συγκρίνονται με αυτό το μοντέλο.',
    'Current model: {title}': 'Τρέχον μοντέλο: {title}',
    'Measured observable': 'Μετρούμενο μέγεθος',
    'Differential cross sections': 'Διαφορικές ενεργές διατομές',
    'Population probabilities': 'Πιθανότητες κατάληψης',
    'Detected particle counts': 'Αριθμοί ανιχνευμένων σωματιδίων',
    'Direct gamma coincidence counts': 'Αριθμοί άμεσων συμπτώσεων γάμμα',
    'Measurement angle frame': 'Σύστημα αναφοράς γωνιών μέτρησης',
    'CM (centre of mass)': 'ΚΜ (κέντρο μάζας)',
    'Lab (scattered projectile)': 'Εργαστήριο (σκεδαζόμενο βλήμα)',
    'CM': 'ΚΜ',
    'Lab': 'Εργαστήριο',
    'Cross-section units': 'Μονάδες ενεργού διατομής',
    'Each row is a detector angular bin. Lab angles always refer to the scattered projectile. efficiency is the particle '
    'detection fraction for that row, between 0 and 1.':
        'Κάθε γραμμή είναι ένα γωνιακό διάστημα του ανιχνευτή. Οι γωνίες εργαστηρίου αναφέρονται πάντα στο σκεδαζόμενο '
        'βλήμα. Η στήλη efficiency είναι το κλάσμα ανίχνευσης σωματιδίων της γραμμής, μεταξύ 0 και 1.',
    'Each row is a point measurement at angle_deg. Uncertainty is optional, positive and one-sigma, in the same units as '
    'value. For finite-bin data, use a corrected point cross section or compare detector counts.':
        'Κάθε γραμμή είναι σημειακή μέτρηση στη γωνία angle_deg. Η αβεβαιότητα είναι προαιρετική, θετική, μίας τυπικής '
        'απόκλισης και στις ίδιες μονάδες με το value. Για δεδομένα πεπερασμένων διαστημάτων, χρησιμοποιήστε διορθωμένη '
        'σημειακή ενεργό διατομή ή συγκρίνετε αριθμούς γεγονότων.',
    'Import measurements': 'Εισαγωγή μετρήσεων',
    'Upload a file': 'Μεταφόρτωση αρχείου',
    'Paste a table': 'Επικόλληση πίνακα',
    'Upload measurements (CSV or TSV)': 'Μεταφόρτωση μετρήσεων (CSV ή TSV)',
    'Upload your file. Required columns: {columns}. Other column names can be matched after upload.':
        'Ανεβάστε το αρχείο σας. Απαιτούμενες στήλες: {columns}. Διαφορετικά ονόματα στηλών αντιστοιχίζονται μετά τη μεταφόρτωση.',
    'Export the spreadsheet as CSV UTF-8 or paste its cells below.':
        'Εξαγάγετε το λογιστικό φύλλο ως CSV UTF-8 ή επικολλήστε τα κελιά του παρακάτω.',
    'Paste measurements, including the header row': 'Επικολλήστε τις μετρήσεις μαζί με τη γραμμή επικεφαλίδων',
    'Paste spreadsheet cells including the header row. First line: {header}':
        'Επικολλήστε κελιά λογιστικού φύλλου μαζί με τη γραμμή επικεφαλίδων. Πρώτη γραμμή: {header}',
    'Preview of your table (first 20 rows)': 'Προεπισκόπηση του πίνακά σας (πρώτες 20 γραμμές)',
    'Preview of the imported measurement table': 'Προεπισκόπηση του πίνακα μετρήσεων',
    'Match your column names': 'Αντιστοίχιση ονομάτων στηλών',
    'Select which column of your table holds each quantity. Extra columns are ignored.':
        'Επιλέξτε ποια στήλη του πίνακα περιέχει κάθε μέγεθος. Οι επιπλέον στήλες αγνοούνται.',
    '(not supplied)': '(δεν δίνεται)',
    'Exposure and acceptance for these counts': 'Έκθεση και αποδοχή για αυτούς τους αριθμούς γεγονότων',
    'Measurement beam rate (particles/s)': 'Ρυθμός δέσμης της μέτρησης (σωματίδια/s)',
    'Measurement live duration (days)': 'Ενεργός χρόνος μέτρησης (ημέρες)',
    'Measurement azimuth fraction': 'Κλάσμα αζιμουθιακής κάλυψης της μέτρησης',
    'Detector integration CM step (°)': 'Βήμα ολοκλήρωσης ανιχνευτή σε ΚΜ (°)',
    'Target thickness: {thickness} mg/cm², from the sidebar. Live duration should account for acquisition dead time. Use '
    'separate comparisons if the exposure or azimuth coverage changes between detectors.':
        'Πάχος στόχου: {thickness} mg/cm², από την πλαϊνή στήλη. Ο ενεργός χρόνος πρέπει να λαμβάνει υπόψη τον νεκρό χρόνο '
        'καταγραφής. Χρησιμοποιήστε ξεχωριστές συγκρίσεις αν η έκθεση ή η αζιμουθιακή κάλυψη διαφέρει μεταξύ ανιχνευτών.',
    'Direct gamma coincidences multiply populated-level counts by branching_fraction and gamma_efficiency. Both are '
    'absolute fractions supplied per row. Feeding, conversion and angular correlations are not inferred.':
        'Οι άμεσες συμπτώσεις γάμμα πολλαπλασιάζουν τα γεγονότα της στάθμης με branching_fraction και gamma_efficiency. '
        'Και τα δύο είναι απόλυτα κλάσματα ανά γραμμή. Τροφοδοσία, μετατροπή και γωνιακές συσχετίσεις δεν συνάγονται.',
    '{count} observations validated; levels {levels}.': 'Επικυρώθηκαν {count} μετρήσεις· στάθμες {levels}.',
    'Compare measurements': 'Σύγκριση μετρήσεων',
    'Calculating predictions for the measured angles and acceptance…':
        'Υπολογισμός προβλέψεων για τις μετρημένες γωνίες και την αποδοχή…',
    'Measurement or reaction settings changed. Compare again to update these predictions.':
        'Οι μετρήσεις ή οι ρυθμίσεις της αντίδρασης άλλαξαν. Συγκρίνετε ξανά για να ενημερωθούν οι προβλέψεις.',
    'Level {level}: measured': 'Στάθμη {level}: μέτρηση',
    'Level {level}: calculated': 'Στάθμη {level}: υπολογισμός',
    'Level {level}': 'Στάθμη {level}',
    '{frame} detector-bin centre (°)': 'Κέντρο διαστήματος ανιχνευτή, {frame} (°)',
    '{frame} scattering angle (°)': 'Γωνία σκέδασης, {frame} (°)',
    'Measurements and predictions': 'Μετρήσεις και προβλέψεις',
    'Measured values with error bars and calculated predictions': 'Μετρημένες τιμές με σφάλματα και υπολογισμένες προβλέψεις',
    'Measured − calculated ({unit})': 'Μέτρηση − υπολογισμός ({unit})',
    'Residuals': 'Υπόλοιπα',
    'Residuals: measured minus calculated': 'Υπόλοιπα: μέτρηση μείον υπολογισμός',
    'Uses {used} of {total} observations with uncertainties. Assumes independent Gaussian errors; no parameters were '
    'fitted. Correlated normalization/systematic errors and low-count Poisson statistics require a dedicated likelihood analysis.':
        'Χρησιμοποιεί {used} από {total} μετρήσεις με αβεβαιότητες. Θεωρεί ανεξάρτητα γκαουσιανά σφάλματα· δεν έγινε '
        'προσαρμογή παραμέτρων. Συσχετισμένα σφάλματα κανονικοποίησης/συστηματικά και στατιστική Poisson μικρών αριθμών '
        'απαιτούν ειδική ανάλυση πιθανοφάνειας.',
    'No uncertainties supplied: error bars and standardized residuals are unavailable.':
        'Δεν δόθηκαν αβεβαιότητες: δεν υπάρχουν γραμμές σφάλματος ούτε κανονικοποιημένα υπόλοιπα.',
    'Measurement comparison table': 'Πίνακας σύγκρισης μετρήσεων',
    'Download measurement comparison CSV': 'Λήψη σύγκρισης μετρήσεων (CSV)',
    'Download measurement comparison JSON': 'Λήψη σύγκρισης μετρήσεων (JSON)',
    'Check detector-integration convergence: halve the CM step and compare again. For energy loss, also increase the depth quadrature order.':
        'Ελέγξτε τη σύγκλιση της ολοκλήρωσης του ανιχνευτή: υποδιπλασιάστε το βήμα ΚΜ και συγκρίνετε ξανά. Με απώλεια '
        'ενέργειας, αυξήστε επίσης τα σημεία ολοκλήρωσης στο βάθος.',
    'probability': 'πιθανότητα',
    'counts': 'γεγονότα',

    # ---- verification ---------------------------------------------------------------------------------
    'Benchmarks against published theory': 'Έλεγχοι έναντι δημοσιευμένης θεωρίας',
    'Run literature benchmarks': 'Εκτέλεση ελέγχων βιβλιογραφίας',
    'Comparing the solver with published results…': 'Σύγκριση του επιλυτή με δημοσιευμένα αποτελέσματα…',
    'All {count} literature benchmarks passed.': 'Και οι {count} έλεγχοι βιβλιογραφίας πέτυχαν.',
    '{failed} of {count} literature benchmarks failed.': '{failed} από {count} ελέγχους βιβλιογραφίας απέτυχαν.',
    'Benchmark': 'Έλεγχος',
    'Check': 'Δοκιμή',
    'Reference': 'Αναφορά',
    'Published / analytic': 'Δημοσιευμένη / αναλυτική τιμή',
    'This code': 'Αυτός ο κώδικας',
    'Difference': 'Διαφορά',
    'relative': 'σχετική',
    'absolute': 'απόλυτη',
    'Tolerance': 'Ανοχή',
    'Result': 'Αποτέλεσμα',
    'pass': 'επιτυχία',
    'FAIL': 'ΑΠΟΤΥΧΙΑ',
    'Literature benchmark results': 'Αποτελέσματα ελέγχων βιβλιογραφίας',
    'Takes about 5 seconds. Independent of the reaction selected in the sidebar.':
        'Διαρκεί περίπου 5 δευτερόλεπτα. Ανεξάρτητο από την αντίδραση της πλαϊνής στήλης.',
    'What each benchmark tests': 'Τι ελέγχει κάθε δοκιμή',
    'Rutherford scattering': 'Σκέδαση Rutherford',
    'First-order perturbation theory': 'Θεωρία διαταραχών πρώτης τάξης',
    'Sudden limit, two states': 'Στιγμιαίο όριο, δύο καταστάσεις',
    'Sudden limit, rigid rotor': 'Στιγμιαίο όριο, άκαμπτος στροφέας',
    'Elastic dσ/dΩ at θcm = 90° (barn/sr)': 'Ελαστική dσ/dΩ για θcm = 90° (barn/sr)',
    'E{lam} 0+ → {state}, P at θcm = {theta}°': 'E{lam} 0+ → {state}, P για θcm = {theta}°',
    'P(2+) = sin²χ for χ = 1, θcm = 180°, ξ = 0': 'P(2+) = sin²χ για χ = 1, θcm = 180°, ξ = 0',
    'Formula reproduces AW60 Table 4 amplitudes (max |ΔRe|, |ΔIm|)':
        'Ο τύπος αναπαράγει τα πλάτη του Πίνακα 4 των AW60 (μέγ. |ΔRe|, |ΔIm|)',
    'q = {q}: P_I (I = 0…{top}), largest deviation at I = {worst}':
        'q = {q}: P_I (I = 0…{top}), μεγαλύτερη απόκλιση για I = {worst}',
    'Literature data behind the selected input': 'Δεδομένα βιβλιογραφίας της επιλεγμένης εισόδου',
    'You are using your own reaction. Compare your inputs with evaluated data, for example the NNDC/ENSDF level data and '
    'the B(E2) evaluation of Pritychenko et al. (2016).':
        'Χρησιμοποιείτε δική σας αντίδραση. Συγκρίνετε τα δεδομένα σας με αξιολογημένα δεδομένα, για παράδειγμα τα δεδομένα '
        'σταθμών NNDC/ENSDF και την αξιολόγηση B(E2) των Pritychenko κ.ά. (2016).',
    'Quantity': 'Μέγεθος',
    'Literature': 'Βιβλιογραφία',
    'This input': 'Αυτή η είσοδος',
    'Deviation (σ)': 'Απόκλιση (σ)',
    'Status': 'Κατάσταση',
    'Source': 'Πηγή',
    'consistent': 'συμφωνεί',
    'differs from literature': 'διαφέρει από τη βιβλιογραφία',
    'model prediction agrees with experiment': 'η πρόβλεψη του μοντέλου συμφωνεί με το πείραμα',
    'Example input compared with literature values': 'Είσοδος του παραδείγματος σε σύγκριση με τιμές βιβλιογραφίας',
    'Run the calculation with 180° in the angle grid to compare with AW60 Table 5.':
        'Εκτελέστε τον υπολογισμό με τις 180° στο πλέγμα γωνιών για σύγκριση με τον Πίνακα 5 των AW60.',
    'Spin I': 'Σπιν I',
    'AW60 Table 5': 'AW60 Πίνακας 5',
    'This calculation': 'Αυτός ο υπολογισμός',
    'Teaching model compared with Alder and Winther Table 5': 'Διδακτικό μοντέλο σε σύγκριση με τον Πίνακα 5 των Alder και Winther',
    'AW60 parameter q': 'Παράμετρος q των AW60',
    'Numerical convergence checks': 'Έλεγχοι αριθμητικής σύγκλισης',
    'Probability conservation is necessary, but it is not an error estimate. Check the ODE error, the omitted distant part '
    'of the orbit, and angular sampling separately.':
        'Η διατήρηση της πιθανότητας είναι αναγκαία, αλλά δεν αποτελεί εκτίμηση σφάλματος. Ελέγξτε χωριστά το σφάλμα της '
        'ΣΔΕ, το μακρινό τμήμα της τροχιάς που παραλείπεται και τη γωνιακή δειγματοληψία.',
    'Run a calculation first; these checks use its reaction and solver settings.':
        'Εκτελέστε πρώτα έναν υπολογισμό· οι έλεγχοι χρησιμοποιούν την αντίδραση και τις ρυθμίσεις του.',
    'Convergence-check angle (°)': 'Γωνία ελέγχου σύγκλισης (°)',
    'Run independent convergence checks': 'Εκτέλεση ανεξάρτητων ελέγχων σύγκλισης',
    'Comparing tolerances, orbit range, and a second integrator…': 'Σύγκριση ανοχών, εύρους τροχιάς και δεύτερου ολοκληρωτή…',
    'Tighter ODE tolerance': 'Αυστηρότερη ανοχή ΣΔΕ',
    'Orbit extended by Δω=1': 'Τροχιά επεκταμένη κατά Δω=1',
    'Independent RK45 integrator': 'Ανεξάρτητος ολοκληρωτής RK45',
    'Max absolute ΔP': 'Μέγιστη απόλυτη ΔP',
    'Max norm drift': 'Μέγιστη απόκλιση νόρμας',
    'RHS evaluations': 'Υπολογισμοί δεξιού μέλους',
    'Convergence check results': 'Αποτελέσματα ελέγχων σύγκλισης',
    'These are incident-energy checks at one angle. Check additional angles and depth quadrature for precision work. '
    'Absolute agreement does not guarantee relative accuracy for tiny populations.':
        'Πρόκειται για ελέγχους στην ενέργεια εισόδου σε μία γωνία. Για εργασία ακριβείας ελέγξτε και άλλες γωνίες και την '
        'ολοκλήρωση στο βάθος. Η απόλυτη συμφωνία δεν εγγυάται σχετική ακρίβεια για πολύ μικρούς πληθυσμούς.',
    'Comparison with the original C++ code': 'Σύγκριση με τον αρχικό κώδικα C++',
    'The archived comparison report is missing. Restore validation/results from the application distribution.':
        'Η αποθηκευμένη αναφορά σύγκρισης λείπει. Επαναφέρετε τον φάκελο validation/results από τη διανομή της εφαρμογής.',
    'Full report (English)': 'Πλήρης αναφορά (στα αγγλικά)',
    'Original C++ and Python populations versus angle, with residuals':
        'Πληθυσμοί του αρχικού C++ και της Python ως προς τη γωνία, με υπόλοιπα',
    'Download all original comparisons': 'Λήψη όλων των συγκρίσεων με τον αρχικό κώδικα',

    # ---- formats and instructions -----------------------------------------------------------------------
    'Required file format: {title}': 'Απαιτούμενη μορφή αρχείου: {title}',
    'Accepted files: {extensions}. Where: {where}.': 'Αποδεκτά αρχεία: {extensions}. Πού: {where}.',
    'Line-by-line layout of a reaction input file': 'Δομή αρχείου εισόδου αντίδρασης ανά γραμμή',
    'Required and optional columns': 'Απαιτούμενες και προαιρετικές στήλες',
    '{label} — for orientation only; it is never used in your own calculation:':
        '{label} — μόνο για προσανατολισμό· δεν χρησιμοποιείται ποτέ στον δικό σας υπολογισμό:',
    'Annotated blank template': 'Κενό πρότυπο με επεξηγήσεις',
    'Blank template (headers only)': 'Κενό πρότυπο (μόνο επικεφαλίδες)',
    'Column': 'Στήλη',
    'Required': 'Υποχρεωτική',
    'required': 'υποχρεωτική',
    'optional': 'προαιρετική',
    'Unit': 'Μονάδα',
    'Meaning': 'Σημασία',
    'Line': 'Γραμμή',
    'Content': 'Περιεχόμενο',
    'Title': 'Τίτλος',
    'rest': 'υπόλοιπες',
    'Reaction inputs': 'Είσοδοι αντίδρασης',
    'Target energy loss': 'Απώλεια ενέργειας στον στόχο',
    'Measurements for comparison': 'Μετρήσεις για σύγκριση',
    'Which file goes where': 'Ποιο αρχείο πηγαίνει πού',
    'File': 'Αρχείο',
    'Purpose': 'Σκοπός',
    'Where to upload': 'Πού ανεβαίνει',
    'Required columns': 'Απαιτούμενες στήλες',
    'line-based text, see File formats': 'κείμενο ανά γραμμή, δείτε «Μορφές αρχείων»',
    'Upload overview': 'Επισκόπηση μεταφορτώσεων',
    'Every format, with blank templates and example files, is under Help and reference → File formats.':
        'Κάθε μορφή, με κενά πρότυπα και αρχεία-παραδείγματα, βρίσκεται στη «Βοήθεια και αναφορά → Μορφές αρχείων».',
    'same as value': 'ίδια με το value',
    '—': '—',

    # formats.py
    'Save spreadsheets as “CSV UTF-8”. Excel .xlsx workbooks are not read directly.':
        'Αποθηκεύστε τα λογιστικά φύλλα ως «CSV UTF-8». Τα βιβλία εργασίας .xlsx του Excel δεν διαβάζονται απευθείας.',
    'The first row holds the column names exactly as listed (lower case, no units, no spaces).':
        'Η πρώτη γραμμή περιέχει τα ονόματα των στηλών ακριβώς όπως αναγράφονται (πεζά, χωρίς μονάδες, χωρίς κενά).',
    'Separators: comma, semicolon or tab. Decimal commas are accepted only with semicolon or tab separators.':
        'Διαχωριστικά: κόμμα, ερωτηματικό ή στηλοθέτης (tab). Η υποδιαστολή με κόμμα γίνεται δεκτή μόνο με ερωτηματικό '
        'ή στηλοθέτη ως διαχωριστικό.',
    'Numbers only in numeric cells: no units, no thousands separators, no formulas, no percent signs.':
        'Μόνο αριθμοί στα αριθμητικά κελιά: χωρίς μονάδες, διαχωριστικά χιλιάδων, τύπους ή σύμβολα ποσοστού.',
    'Optional columns may be omitted or left blank. Extra columns are ignored.':
        'Οι προαιρετικές στήλες μπορούν να παραλειφθούν ή να μείνουν κενές. Οι επιπλέον στήλες αγνοούνται.',
    'Free text on one line': 'Ελεύθερο κείμενο σε μία γραμμή',
    'Number of nuclear levels (integer)': 'Πλήθος πυρηνικών σταθμών (ακέραιος)',
    'Projectile charge and mass number (integers)': 'Ατομικός και μαζικός αριθμός βλήματος (ακέραιοι)',
    'Target charge and mass number (integers)': 'Ατομικός και μαζικός αριθμός στόχου (ακέραιοι)',
    'Beam energy in total MeV (not MeV/u)': 'Ενέργεια δέσμης σε συνολικά MeV (όχι MeV/u)',
    'CM angle range in degrees; θmax = 0 means a single angle': 'Εύρος γωνιών ΚΜ σε μοίρες· θmax = 0 σημαίνει μία μόνο γωνία',
    'One row per level: index 1…N, spin, energy (MeV), parity +1/−1, K (metadata, use 0). Level 1 is the ground state at 0 MeV.':
        'Μία γραμμή ανά στάθμη: αύξων αριθμός 1…N, σπιν, ενέργεια (MeV), ομοτιμία +1/−1, K (μεταδεδομένο, βάλτε 0). '
        'Η στάθμη 1 είναι η θεμελιώδης κατάσταση στα 0 MeV.',
    'One row per electric matrix element: level numbers i and f, signed reduced matrix element <i‖Eλ‖f> in e·b^(λ/2), '
    'multipolarity λ = 1…4. Use i = f for a diagonal (reorientation) element. Do not add the reversed pair.':
        'Μία γραμμή ανά ηλεκτρικό στοιχείο πίνακα: αριθμοί σταθμών i και f, προσημασμένο ανηγμένο στοιχείο <i‖Eλ‖f> σε '
        'e·b^(λ/2), πολυπολικότητα λ = 1…4. Για διαγώνιο στοιχείο (επαναπροσανατολισμού) i = f. Μην προσθέτετε το '
        'αντίστροφο ζεύγος.',
    'Values on a line are separated by spaces or tabs.': 'Οι τιμές μιας γραμμής χωρίζονται με κενά ή στηλοθέτες.',
    'Text after # or // is a comment and is ignored.': 'Ό,τι ακολουθεί το # ή το // είναι σχόλιο και αγνοείται.',
    'The excited nucleus (projectile or target) is chosen in the sidebar, not in the file.':
        'Ο πυρήνας που διεγείρεται (βλήμα ή στόχος) επιλέγεται στην πλαϊνή στήλη, όχι στο αρχείο.',
    'Reaction text input': 'Αρχείο κειμένου αντίδρασης',
    'Defines the nuclei, beam energy, levels and matrix elements in one text file.':
        'Ορίζει τους πυρήνες, την ενέργεια δέσμης, τις στάθμες και τα στοιχεία πίνακα σε ένα αρχείο κειμένου.',
    'Sidebar → 1 · Reaction → Upload a reaction file': 'Πλαϊνή στήλη → 1 · Αντίδραση → Δικό μου αρχείο αντίδρασης',
    'Example file (22Mg + 104Pd)': 'Αρχείο-παράδειγμα (22Mg + 104Pd)',
    'Nuclear levels table': 'Πίνακας πυρηνικών σταθμών',
    'One row per nuclear level of the excited nucleus.': 'Μία γραμμή ανά πυρηνική στάθμη του πυρήνα που διεγείρεται.',
    'Sidebar → 1 · Reaction → Enter tables, then the level table on the main page':
        'Πλαϊνή στήλη → 1 · Αντίδραση → Δικοί μου πίνακες, και μετά ο πίνακας σταθμών στην κύρια σελίδα',
    'Level number 1, 2, 3 … in order, without gaps': 'Αριθμός στάθμης 1, 2, 3 … με τη σειρά, χωρίς κενά',
    'Spin J: integer or half-integer (0, 2, 1.5 …)': 'Σπιν J: ακέραιο ή ημιακέραιο (0, 2, 1.5 …)',
    'Excitation energy; level 1 must be the ground state at 0': 'Ενέργεια διέγερσης· η στάθμη 1 πρέπει να είναι η θεμελιώδης στο 0',
    'Parity: 1 for +, −1 for −': 'Ομοτιμία: 1 για +, −1 για −',
    'K quantum number, kept as metadata only (default 0)': 'Κβαντικός αριθμός K, μόνο ως μεταδεδομένο (προεπιλογή 0)',
    'All spins must be either integer or half-integer.': 'Όλα τα σπιν πρέπει να είναι είτε ακέραια είτε ημιακέραια.',
    'Every level must lie below the centre-of-mass energy.': 'Κάθε στάθμη πρέπει να βρίσκεται κάτω από την ενέργεια κέντρου μάζας.',
    'Example file (22Mg levels)': 'Αρχείο-παράδειγμα (στάθμες 22Mg)',
    'Electric matrix-elements table': 'Πίνακας ηλεκτρικών στοιχείων πίνακα',
    'One row per electromagnetic coupling between two levels.': 'Μία γραμμή ανά ηλεκτρομαγνητική σύζευξη μεταξύ δύο σταθμών.',
    'Sidebar → 1 · Reaction → Enter tables, then the matrix-element table on the main page':
        'Πλαϊνή στήλη → 1 · Αντίδραση → Δικοί μου πίνακες, και μετά ο πίνακας στοιχείων πίνακα στην κύρια σελίδα',
    'Level number of the first state': 'Αριθμός στάθμης της πρώτης κατάστασης',
    'Level number of the second state (equal to initial for a diagonal element)':
        'Αριθμός στάθμης της δεύτερης κατάστασης (ίσος με το initial για διαγώνιο στοιχείο)',
    'Signed reduced matrix element <initial‖Eλ‖final> (e·b for E2). Not B(Eλ): for a 0+ ground state, value = ±√B(Eλ↑)':
        'Προσημασμένο ανηγμένο στοιχείο πίνακα <initial‖Eλ‖final> (e·b για E2). Όχι B(Eλ): για θεμελιώδη 0+, '
        'value = ±√B(Eλ↑)',
    'Electric multipolarity λ = 1, 2, 3 or 4': 'Ηλεκτρική πολυπολικότητα λ = 1, 2, 3 ή 4',
    'Enter each pair once; the reversed element is generated with the correct phase.':
        'Δώστε κάθε ζεύγος μία φορά· το αντίστροφο στοιχείο δημιουργείται με τη σωστή φάση.',
    'Spin triangle and parity selection rules are checked.': 'Ελέγχονται ο τριγωνικός κανόνας σπιν και οι κανόνες ομοτιμίας.',
    'A table with headers only describes a nucleus without couplings.':
        'Ένας πίνακας μόνο με επικεφαλίδες περιγράφει πυρήνα χωρίς συζεύξεις.',
    'Example file (22Mg couplings)': 'Αρχείο-παράδειγμα (συζεύξεις 22Mg)',
    'Stopping-power table': 'Πίνακας ισχύος ανάσχεσης',
    'Energy loss of the beam in the target, for thick-target averages.':
        'Απώλεια ενέργειας της δέσμης στον στόχο, για μέσους όρους σε παχύ στόχο.',
    'Sidebar → 3 · Target and energy loss': 'Πλαϊνή στήλη → 3 · Στόχος και απώλεια ενέργειας',
    'Beam energy (total MeV), strictly increasing': 'Ενέργεια δέσμης (συνολικά MeV), γνησίως αύξουσα',
    'Stopping power of this ion in this target material': 'Ισχύς ανάσχεσης αυτού του ιόντος σε αυτό το υλικό στόχου',
    'Comma-separated, with exactly these two column names.': 'Διαχωρισμός με κόμμα, με ακριβώς αυτά τα δύο ονόματα στηλών.',
    'At least two rows. The table must cover the incident energy and the exit energy; nothing is extrapolated.':
        'Τουλάχιστον δύο γραμμές. Ο πίνακας πρέπει να καλύπτει την ενέργεια εισόδου και εξόδου· δεν γίνεται παρεκβολή.',
    'Use a validated table (for example from SRIM or ATIMA) for your ion and material.':
        'Χρησιμοποιήστε επικυρωμένο πίνακα (π.χ. από SRIM ή ATIMA) για το ιόν και το υλικό σας.',
    'Synthetic test table (not physical data)': 'Συνθετικός πίνακας δοκιμής (όχι φυσικά δεδομένα)',
    'Measured differential cross sections': 'Μετρημένες διαφορικές ενεργές διατομές',
    'Point measurements dσ/dΩ versus angle.': 'Σημειακές μετρήσεις dσ/dΩ ως προς τη γωνία.',
    'Measurements tab → Differential cross sections': 'Καρτέλα «Μετρήσεις» → Διαφορικές ενεργές διατομές',
    'Scattering angle (CM or lab, as selected); lab angles refer to the scattered projectile':
        'Γωνία σκέδασης (ΚΜ ή εργαστηρίου, όπως επιλεγεί)· οι γωνίες εργαστηρίου αναφέρονται στο σκεδαζόμενο βλήμα',
    'Final level number': 'Αριθμός τελικής στάθμης',
    'Measured dσ/dΩ in the unit selected in the app': 'Μετρημένη dσ/dΩ στη μονάδα που επιλέγεται στην εφαρμογή',
    'One-sigma standard uncertainty; blank = unknown': 'Τυπική αβεβαιότητα μίας σ· κενό = άγνωστη',
    'Example file (synthetic numbers)': 'Αρχείο-παράδειγμα (συνθετικοί αριθμοί)',
    'Measured population probabilities': 'Μετρημένες πιθανότητες κατάληψης',
    'Point measurements of level populations versus CM angle.': 'Σημειακές μετρήσεις πληθυσμών σταθμών ως προς τη γωνία ΚΜ.',
    'Measurements tab → Population probabilities': 'Καρτέλα «Μετρήσεις» → Πιθανότητες κατάληψης',
    'CM scattering angle': 'Γωνία σκέδασης ΚΜ',
    'Probability between 0 and 1': 'Πιθανότητα μεταξύ 0 και 1',
    'Detected particle counts': 'Αριθμοί ανιχνευμένων σωματιδίων',
    'Counts of scattered particles per detector angular bin.': 'Αριθμοί σκεδαζόμενων σωματιδίων ανά γωνιακό διάστημα ανιχνευτή.',
    'Measurements tab → Detected particle counts': 'Καρτέλα «Μετρήσεις» → Αριθμοί ανιχνευμένων σωματιδίων',
    'Lower edge of the angular bin': 'Κάτω όριο του γωνιακού διαστήματος',
    'Upper edge of the angular bin': 'Άνω όριο του γωνιακού διαστήματος',
    'Observed number of counts in the bin': 'Παρατηρούμενος αριθμός γεγονότων στο διάστημα',
    'Particle detection efficiency as a fraction (0.9, not 90)': 'Απόδοση ανίχνευσης σωματιδίων ως κλάσμα (0.9, όχι 90)',
    'Beam rate, live time and azimuth coverage are entered in the app.':
        'Ο ρυθμός δέσμης, ο ενεργός χρόνος και η αζιμουθιακή κάλυψη δίνονται στην εφαρμογή.',
    'Particle–gamma coincidence counts': 'Αριθμοί συμπτώσεων σωματιδίου–γάμμα',
    'Coincidences of a direct gamma ray with the scattered particle.':
        'Συμπτώσεις άμεσης ακτίνας γάμμα με το σκεδαζόμενο σωματίδιο.',
    'Measurements tab → Direct gamma coincidence counts': 'Καρτέλα «Μετρήσεις» → Αριθμοί άμεσων συμπτώσεων γάμμα',
    'Emitting (excited) level number, not 1': 'Αριθμός της στάθμης που εκπέμπει (διεγερμένης), όχι 1',
    'Observed coincidences in the bin': 'Παρατηρούμενες συμπτώσεις στο διάστημα',
    'Direct gamma branch per population': 'Άμεσος κλάδος γάμμα ανά κατάληψη',
    'Absolute gamma detection efficiency': 'Απόλυτη απόδοση ανίχνευσης γάμμα',
    'Feeding cascades, internal conversion and angular correlations are not modelled.':
        'Η τροφοδοσία από καταρράκτες, η εσωτερική μετατροπή και οι γωνιακές συσχετίσεις δεν μοντελοποιούνται.',

    # ---- examples ------------------------------------------------------------------------------------------
    '22Mg radioactive beam (3.0 MeV/u) on 104Pd: 0+, 2+ and 4+ states from evaluated data.':
        'Ραδιενεργός δέσμη 22Mg (3,0 MeV/u) σε 104Pd: καταστάσεις 0+, 2+ και 4+ από αξιολογημένα δεδομένα.',
    'A light nucleus with an uncertain B(E2): the 2+ is excited in one step, the 4+ only weakly in two steps through '
    'a rigid-rotor model element. Q(2+) is not measured and is left out.':
        'Ελαφρύς πυρήνας με αβέβαιο B(E2): η 2+ διεγείρεται σε ένα βήμα, η 4+ μόνο ασθενώς σε δύο βήματα μέσω στοιχείου '
        'πίνακα από το μοντέλο του άκαμπτου στροφέα. Το Q(2+) δεν έχει μετρηθεί και παραλείπεται.',
    'License: GNU General Public License version 3 — free software, without any warranty. A Python adaptation of '
    '[TCLX](https://github.com/jhenderson88/TCLX) and its GPL-3.0 successor [Cygnus](https://github.com/jhenderson88/Cygnus) '
    'by J. Henderson; see LICENSE and README.md.':
        'Άδεια: GNU General Public License, έκδοση 3 — ελεύθερο λογισμικό, χωρίς καμία εγγύηση. Προσαρμογή σε Python του '
        '[TCLX](https://github.com/jhenderson88/TCLX) και του διαδόχου του, [Cygnus](https://github.com/jhenderson88/Cygnus) '
        '(GPL-3.0), του J. Henderson· δείτε τα αρχεία LICENSE και README.md.',
    '58Ni beam (3.79 MeV/u) on 208Pb using evaluated B(E2) and Q(2+).':
        'Δέσμη 58Ni (3,79 MeV/u) σε 208Pb με αξιολογημένες τιμές B(E2) και Q(2+).',
    'Weak coupling: the result is close to first-order perturbation theory, with a small reorientation term.':
        'Ασθενής σύζευξη: το αποτέλεσμα είναι κοντά στη θεωρία διαταραχών πρώτης τάξης, με μικρό όρο επαναπροσανατολισμού.',
    '152Sm beam (3.29 MeV/u) on 58Ni: ground band up to 16+, inverse kinematics.':
        'Δέσμη 152Sm (3,29 MeV/u) σε 58Ni: θεμελιώδης ζώνη έως 16+, αντίστροφη κινηματική.',
    'Multi-step excitation of a rotational band. Measured B(E2) fixes Q0; the rigid-rotor model supplies the other matrix '
    'elements and correctly predicts the measured Q(2+). A heavy beam on a light target gives two lab branches.':
        'Διέγερση πολλαπλών βημάτων περιστροφικής ζώνης. Η μετρημένη B(E2) καθορίζει το Q0· το μοντέλο άκαμπτου στροφέα '
        'δίνει τα υπόλοιπα στοιχεία πίνακα και προβλέπει σωστά τη μετρημένη Q(2+). Βαριά δέσμη σε ελαφρύ στόχο δίνει δύο '
        'κλάδους στο σύστημα εργαστηρίου.',
    '16O beam (4.13 MeV/u) on a 238U target; the target is excited (ground band up to 12+).':
        'Δέσμη 16O (4,13 MeV/u) σε στόχο 238U· διεγείρεται ο στόχος (θεμελιώδης ζώνη έως 12+).',
    'Multiple Coulomb excitation of a strongly deformed nucleus, even with a light beam. Shows target excitation.':
        'Πολλαπλή διέγερση Coulomb ισχυρά παραμορφωμένου πυρήνα, ακόμη και με ελαφριά δέσμη. Δείχνει διέγερση του στόχου.',
    '16O beam (3.75 MeV/u) on a 208Pb target; the octupole 3− and the 2+ state of 208Pb are excited.':
        'Δέσμη 16O (3,75 MeV/u) σε στόχο 208Pb· διεγείρονται η οκταπολική 3− και η 2+ κατάσταση του 208Pb.',
    'Electric octupole (E3) excitation and the adiabatic suppression of high-lying states.':
        'Ηλεκτρική οκταπολική (E3) διέγερση και η αδιαβατική καταστολή υψηλών σταθμών.',
    'Exactly solvable model: a rigid rotor with all levels at 0 MeV, q = 2.':
        'Ακριβώς επιλύσιμο μοντέλο: άκαμπτος στροφέας με όλες τις στάθμες στα 0 MeV, q = 2.',
    'At 180° the populations must reproduce the published Alder–Winther (1960) Table 5.':
        'Στις 180° οι πληθυσμοί πρέπει να αναπαράγουν τον δημοσιευμένο Πίνακα 5 των Alder–Winther (1960).',
}

# Messages raised by the numerical package (English) and their Greek display text.
EL.update({
    'A matrix element refers to a nonexistent level.': 'Ένα στοιχείο πίνακα αναφέρεται σε στάθμη που δεν υπάρχει.',
    'A nonzero electric matrix element violates parity selection.':
        'Ένα μη μηδενικό ηλεκτρικό στοιχείο πίνακα παραβιάζει τον κανόνα επιλογής ομοτιμίας.',
    'A nonzero matrix element violates the angular-momentum triangle rule.':
        'Ένα μη μηδενικό στοιχείο πίνακα παραβιάζει τον τριγωνικό κανόνα της στροφορμής.',
    'A nuclear charge Z cannot exceed its mass number A.': 'Ο ατομικός αριθμός Z δεν μπορεί να υπερβαίνει τον μαζικό αριθμό A.',
    'All levels must have the same integer/half-integer spin character.':
        'Όλες οι στάθμες πρέπει να έχουν σπιν του ίδιου τύπου (όλα ακέραια ή όλα ημιακέραια).',
    'Angle controls must be finite.': 'Οι γωνίες πρέπει να είναι πεπερασμένοι αριθμοί.',
    'Beam energy must be finite and positive (total MeV, not MeV/u).':
        'Η ενέργεια δέσμης πρέπει να είναι πεπερασμένη και θετική (συνολικά MeV, όχι MeV/u).',
    'Beam exits the stopping-table range inside the target; supply a wider table.':
        'Η δέσμη βγαίνει από το εύρος του πίνακα ανάσχεσης μέσα στον στόχο· δώστε ευρύτερο πίνακα.',
    'CSV columns must be energy_mev,stopping_mev_per_mg_cm2.': 'Οι στήλες CSV πρέπει να είναι energy_mev,stopping_mev_per_mg_cm2.',
    'Center-of-mass angle must lie in (0, 180].': 'Η γωνία ΚΜ πρέπει να ανήκει στο (0, 180].',
    'Cross sections must be nonnegative and azimuth coverage must lie in [0, 1].':
        'Οι ενεργές διατομές πρέπει να είναι μη αρνητικές και η αζιμουθιακή κάλυψη στο [0, 1].',
    'Detector integration needs at least two ordered angle samples.':
        'Η ολοκλήρωση του ανιχνευτή χρειάζεται τουλάχιστον δύο διατεταγμένες γωνίες.',
    'Dipole strength must be finite and nonnegative.': 'Η ισχύς διπόλου πρέπει να είναι πεπερασμένη και μη αρνητική.',
    'Duplicate matrix element (including a reversed duplicate).': 'Διπλό στοιχείο πίνακα (ή και αντίστροφο διπλότυπο).',
    'Every level must lie below the available center-of-mass energy.':
        'Κάθε στάθμη πρέπει να βρίσκεται κάτω από τη διαθέσιμη ενέργεια κέντρου μάζας.',
    'Excitation energy must lie below E_cm.': 'Η ενέργεια διέγερσης πρέπει να είναι μικρότερη από την E_cm.',
    'Extra orbit range must be between 0 and 4.': 'Το επιπλέον εύρος τροχιάς πρέπει να είναι μεταξύ 0 και 4.',
    'Incident energy must lie inside the stopping table, above its minimum.':
        'Η ενέργεια εισόδου πρέπει να βρίσκεται μέσα στον πίνακα ανάσχεσης, πάνω από το ελάχιστό του.',
    'Incomplete reaction input; see the File formats tab for the line-by-line layout.':
        'Ελλιπής είσοδος αντίδρασης· δείτε τη δομή ανά γραμμή στην καρτέλα «Μορφές αρχείων».',
    'Level data must be finite.': 'Τα δεδομένα σταθμών πρέπει να είναι πεπερασμένοι αριθμοί.',
    'Level indices must be consecutive, starting at 1.': 'Οι αριθμοί σταθμών πρέπει να είναι διαδοχικοί, ξεκινώντας από το 1.',
    'Matrix elements must be finite.': 'Τα στοιχεία πίνακα πρέπει να είναι πεπερασμένοι αριθμοί.',
    'ODE tolerances are outside the supported range.': 'Οι ανοχές της ΣΔΕ είναι εκτός του επιτρεπτού εύρους.',
    'Only electric E1–E4 transitions are supported; magnetic codes are rejected.':
        'Υποστηρίζονται μόνο ηλεκτρικές μεταβάσεις E1–E4· οι μαγνητικοί κωδικοί απορρίπτονται.',
    'Parity must be +1 or -1.': 'Η ομοτιμία πρέπει να είναι +1 ή -1.',
    'Require 0 < minimum ≤ maximum ≤ 180°, and a positive step.': 'Απαιτείται 0 < ελάχιστη ≤ μέγιστη ≤ 180° και θετικό βήμα.',
    'Require 0 ≤ detector minimum < maximum ≤ 180°.': 'Απαιτείται 0 ≤ ελάχιστη < μέγιστη γωνία ανιχνευτή ≤ 180°.',
    'Rutherford angles must lie in (0, 180].': 'Οι γωνίες Rutherford πρέπει να ανήκουν στο (0, 180].',
    'Spins must be nonnegative integers or half-integers.': 'Τα σπιν πρέπει να είναι μη αρνητικά ακέραια ή ημιακέραια.',
    'Stopping table needs increasing positive energies and positive finite stopping powers.':
        'Ο πίνακας ανάσχεσης χρειάζεται αύξουσες θετικές ενέργειες και θετικές πεπερασμένες ισχύεις ανάσχεσης.',
    'The declared level count does not match the input.': 'Το δηλωμένο πλήθος σταθμών δεν αντιστοιχεί στην είσοδο.',
    'The exit channel must be open.': 'Το κανάλι εξόδου πρέπει να είναι ανοιχτό.',
    'The first level must be the ground state at 0 MeV.': 'Η πρώτη στάθμη πρέπει να είναι η θεμελιώδης κατάσταση στα 0 MeV.',
    'Thickness must be finite and nonnegative.': 'Το πάχος πρέπει να είναι πεπερασμένο και μη αρνητικό.',
    'Use at most 10,001 angles per calculation.': 'Χρησιμοποιήστε το πολύ 10.001 γωνίες ανά υπολογισμό.',
    'Yield inputs must be finite and nonnegative.': 'Οι παράμετροι αριθμού γεγονότων πρέπει να είναι πεπερασμένες και μη αρνητικές.',
    'A detector bin includes 0° CM, where the Rutherford factor diverges. Use a positive lower acceptance angle.':
        'Ένα διάστημα ανιχνευτή περιλαμβάνει τις 0° ΚΜ, όπου ο παράγοντας Rutherford απειρίζεται. Χρησιμοποιήστε θετική '
        'κάτω γωνία αποδοχής.',
    'A direct gamma observation must refer to an excited level, not level 1.':
        'Μια μέτρηση άμεσης γάμμα πρέπει να αναφέρεται σε διεγερμένη στάθμη, όχι στη στάθμη 1.',
    'A measurement lies at a lab turning-point singularity. Use finite detector bins/counts instead of a point cross section.':
        'Μια μέτρηση βρίσκεται σε ιδιάζον σημείο αναστροφής του συστήματος εργαστηρίου. Χρησιμοποιήστε πεπερασμένα '
        'διαστήματα ανιχνευτή αντί για σημειακή ενεργό διατομή.',
    'Add at least a ground-state level.': 'Προσθέστε τουλάχιστον τη θεμελιώδη στάθμη.',
    'Azimuth coverage must lie in (0, 1].': 'Η αζιμουθιακή κάλυψη πρέπει να ανήκει στο (0, 1].',
    'Beam rate and live duration must be positive and finite.': 'Ο ρυθμός δέσμης και ο ενεργός χρόνος πρέπει να είναι θετικοί και πεπερασμένοι.',
    'Choose barn/sr, mb/sr or fm²/sr.': 'Επιλέξτε barn/sr, mb/sr ή fm²/sr.',
    'Detector integration step must lie in (0, 10] degrees.': 'Το βήμα ολοκλήρωσης του ανιχνευτή πρέπει να ανήκει στο (0, 10] μοίρες.',
    'Detector-count comparison requires a positive target thickness.':
        'Η σύγκριση αριθμών γεγονότων απαιτεί θετικό πάχος στόχου.',
    'Each detector row requires 0 ≤ angle_min_deg < angle_max_deg ≤ 180.':
        'Κάθε γραμμή ανιχνευτή απαιτεί 0 ≤ angle_min_deg < angle_max_deg ≤ 180.',
    'Each selected source column can be mapped to only one quantity.':
        'Κάθε στήλη του αρχείου μπορεί να αντιστοιχιστεί μόνο σε ένα μέγεθος.',
    'Every column needs a unique, nonempty header.': 'Κάθε στήλη χρειάζεται μοναδική, μη κενή επικεφαλίδα.',
    'Level numbers must be consecutive and ordered, beginning at 1.':
        'Οι αριθμοί σταθμών πρέπει να είναι διαδοχικοί και ταξινομημένοι, ξεκινώντας από το 1.',
    'Measured values must be nonnegative; background-subtracted negative observations need a separate statistical model.':
        'Οι μετρημένες τιμές πρέπει να είναι μη αρνητικές· αρνητικές τιμές μετά από αφαίρεση υποβάθρου χρειάζονται '
        'ξεχωριστό στατιστικό μοντέλο.',
    'Point angles must lie in (0, 180] degrees.': 'Οι σημειακές γωνίες πρέπει να ανήκουν στο (0, 180] μοίρες.',
    'Population comparisons require CM scattering angles.': 'Οι συγκρίσεις πληθυσμών απαιτούν γωνίες σκέδασης ΚΜ.',
    'Population probabilities must lie in [0, 1].': 'Οι πιθανότητες κατάληψης πρέπει να ανήκουν στο [0, 1].',
    'Select CM or Lab angles.': 'Επιλέξτε γωνίες ΚΜ ή εργαστηρίου.',
    'Target thickness must be finite and nonnegative.': 'Το πάχος στόχου πρέπει να είναι πεπερασμένο και μη αρνητικό.',
    'The exit channel is closed.': 'Το κανάλι εξόδου είναι κλειστό.',
    'The measurement table has no observations.': 'Ο πίνακας μετρήσεων δεν περιέχει μετρήσεις.',
    'The uploaded table is empty.': 'Ο πίνακας που ανέβηκε είναι κενός.',
    'Uncertainty must be a positive one-sigma standard uncertainty, or blank if unknown.':
        'Η αβεβαιότητα πρέπει να είναι θετική τυπική αβεβαιότητα μίας σ, ή κενή αν είναι άγνωστη.',
    'Unknown observable.': 'Άγνωστο μέγεθος.',
})

ERRORS_EL = [
    (r'Invalid reaction input: (.*)', 'Μη έγκυρη είσοδος αντίδρασης: {0}'),
    (r'Invalid CSV: (.*)', 'Μη έγκυρο CSV: {0}'),
    (r'CSV row (\d+): expected (\d+) columns, found (\d+)\.', 'Γραμμή CSV {0}: αναμένονταν {1} στήλες, βρέθηκαν {2}.'),
    (r'Row (\d+), column (\S+): enter a finite number\.', 'Γραμμή {0}, στήλη {1}: δώστε πεπερασμένο αριθμό.'),
    (r'Row (\d+), column (\S+): enter a finite number or leave it blank\.',
     'Γραμμή {0}, στήλη {1}: δώστε πεπερασμένο αριθμό ή αφήστε το κελί κενό.'),
    (r'Row (\d+), column (\S+): expected an integer from (-?\d+) to (-?\d+)\.',
     'Γραμμή {0}, στήλη {1}: αναμενόταν ακέραιος από {2} έως {3}.'),
    (r'Row (\d+), column (\S+): expected an integer from (-?\d+) upwards\.',
     'Γραμμή {0}, στήλη {1}: αναμενόταν ακέραιος από {2} και πάνω.'),
    (r'Missing columns: (.*)\. Download a template or map your headers\.',
     'Λείπουν στήλες: {0}. Κατεβάστε ένα πρότυπο ή αντιστοιχίστε τις επικεφαλίδες σας.'),
    (r'(\S+) must be a fraction between 0 and 1, not a percentage\.',
     'Η στήλη {0} πρέπει να είναι κλάσμα μεταξύ 0 και 1, όχι ποσοστό.'),
    (r'(\S+) must be a positive integer\.', 'Το {0} πρέπει να είναι θετικός ακέραιος.'),
    (r'Detector requires CM angles (\S+)–(\S+)°; extend the calculated grid\.',
     'Ο ανιχνευτής απαιτεί γωνίες ΚΜ {0}–{1}°· επεκτείνετε το πλέγμα γωνιών του υπολογισμού.'),
    (r'ODE solver failed at (\S+)°: (.*)', 'Ο επιλυτής ΣΔΕ απέτυχε στις {0}°: {1}'),
    (r'Probability conservation failed \((\S+)\); tighten tolerances\.',
     'Η διατήρηση της πιθανότητας απέτυχε ({0})· αυστηροποιήστε τις ανοχές.'),
    (r'This import needs (\S+) collision calculations\. Use fewer bins or a larger integration step\.',
     'Η εισαγωγή απαιτεί {0} υπολογισμούς κρούσεων. Χρησιμοποιήστε λιγότερα διαστήματα ή μεγαλύτερο βήμα ολοκλήρωσης.'),
    (r'invalid literal for int\(\) with base 10: (.*)', 'αναμενόταν ακέραιος, βρέθηκε {0}'),
    (r'could not convert string to float: (.*)', 'αναμενόταν αριθμός, βρέθηκε {0}'),
    (r'not enough values to unpack \(expected (\d+), got (\d+)\)',
     'λείπουν τιμές σε μια γραμμή (αναμένονταν {0}, βρέθηκαν {1})'),
    (r'too many values to unpack \(expected (\d+)\)', 'περισσότερες τιμές από όσες αναμένονταν σε μια γραμμή ({0})'),
]
