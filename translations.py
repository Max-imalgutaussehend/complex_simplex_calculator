"""
Translation dictionaries for multilingual support.
"""

TRANSLATIONS = {
    "en": {
        # Sidebar
        "configuration": "Configuration",
        "tableau_mode": "Tableau Mode",
        "objective_type": "Objective Type",
        "endtableau_mode": "Endtableau Mode",
        "endtableau_help": "Use this for final tableaus (after Simplex). Equations (=) won't add artificial variables. Decision variables will be in basis.",
        "examples": "Examples",
        "show_examples": "Show syntax examples",

        # Modes
        "mode_expression": "Expression Input (Flexible)",
        "mode_create": "Create New Tableau",
        "mode_matrix": "Matrix Input (Standard Form)",
        "mode_final": "Final Tableau (Endtableau)",

        # Main UI
        "title": "Interactive Simplex Tableau Calculator",
        "subtitle": "This tool allows you to manually manipulate simplex tableaus, perform pivot operations, and optimize **any variable** (including slack variables). Perfect for studying the Simplex algorithm.",

        # Tabs
        "tab_calculator": "Simplex Calculator",
        "tab_manual": "User Manual",

        # Tableau Definition
        "tableau_definition": "Tableau Definition",
        "tableau_loaded": "Tableau loaded",
        "lp_formulation": "LP Formulation (LaTeX)",
        "view_tableau": "View Current Tableau Matrix",
        "tableau_info": "Tableau Info",
        "variables": "Variables",
        "constraints": "Constraints",
        "basis": "Basis",

        # Input fields
        "objective_function": "Objective Function",
        "objective_placeholder": "Objective to optimize",
        "objective_example": "Example: 3*x_1 + 4*x_2 - 2*x_3",
        "constraints_label": "Constraints",
        "constraints_placeholder": "Constraints (comma-separated)",
        "constraints_example": "Example: 2*x_1 + 3*x_2 <= 4, x_1 + x_2 >= 2",

        # Buttons
        "create_tableau": "Create Tableau from Expressions",
        "solve_automatically": "🚀 Solve Automatically",
        "perform_pivot": "Perform Pivot",
        "new_problem": "New Problem",
        "apply": "Apply",

        # Status
        "status": "Status",
        "optimal": "OPTIMAL",
        "not_optimal": "Not optimal",
        "degenerate": "Degenerate solution",
        "unbounded": "Unbounded",
        "pivot_steps": "Pivot Steps",
        "current_basis": "Current Basis",
        "objective_value": "Objective Value (z)",

        # Tableau display
        "current_tableau": "Current Tableau",
        "constraints_section": "Constraints:",
        "objective_section": "Objective Function (Z):",
        "current_solution": "Current Solution:",
        "basic_variables": "Basic Variables:",
        "nonbasic_variables": "Non-basic Variables:",
        "complete_solution": "📊 Complete Solution Vector",

        # Reduced costs
        "reduced_costs": "Reduced Costs (Shadow Prices)",
        "can_improve": "[!]",
        "cannot_improve": "[ ]",

        # Pivot operations
        "pivot_operations": "Pivot Operations",
        "select_entering": "Select Entering Variable",
        "select_leaving": "Select Leaving Variable",
        "show_pivot_details": "Show Pivot Details",
        "entering_variable": "Entering variable",
        "leaving_variable": "Leaving variable",
        "pivot_element": "Pivot element",
        "minimum_ratio_test": "Minimum Ratio Test",
        "no_improving": "Current tableau is optimal. No improving pivots available.",

        # History
        "history": "History",
        "iteration": "Iteration",
        "first_step": "First Step",
        "previous_step": "Previous Step",
        "next_step": "Next Step",
        "current_step": "Current step",

        # Messages
        "success_created": "Tableau created from expressions!",
        "success_solved": "✓ Solved in {0} iterations!",
        "success_pivot": "✓ Pivot successful! Z improved from {0:.4f} to {1:.4f}",
        "error_creating": "Error creating tableau: {0}",
        "info_enter_problem": "Enter objective function and constraints as mathematical expressions",

        # Preview
        "preview_parsing": "Preview Parsing",
        "latex_preview": "📐 LaTeX Preview",
        "objective_coeffs": "Objective coefficients:",
        "objective_constant": "Objective constant:",
        "found_constraints": "Found {0} constraints:",
        "variables_detected": "Variables detected:",
        "parsing_error": "Parsing error: {0}",
        "latex_error": "LaTeX rendering error: {0}",

        # Maximize/Minimize
        "maximize": "Maximiere",
        "minimize": "Minimiere",
        "subject_to": "unter den Nebenbedingungen",
    },

    "de": {
        # Sidebar
        "configuration": "Konfiguration",
        "tableau_mode": "Tableau-Modus",
        "objective_type": "Zielfunktions-Typ",
        "endtableau_mode": "Endtableau-Modus",
        "endtableau_help": "Für Endtableaus (nach Simplex). Gleichungen (=) fügen keine künstlichen Variablen hinzu. Entscheidungsvariablen werden zur Basis.",
        "examples": "Beispiele",
        "show_examples": "Syntax-Beispiele anzeigen",

        # Modes
        "mode_expression": "Ausdrucks-Eingabe (Flexibel)",
        "mode_create": "Neues Tableau erstellen",
        "mode_matrix": "Matrix-Eingabe (Standardform)",
        "mode_final": "End-Tableau (Endtableau)",

        # Main UI
        "title": "Interaktiver Simplex-Tableau-Rechner",
        "subtitle": "Dieses Tool ermöglicht die manuelle Manipulation von Simplex-Tableaus, Pivot-Operationen und die Optimierung **jeder Variable** (einschließlich Schlupfvariablen). Perfekt zum Studieren des Simplex-Algorithmus.",

        # Tabs
        "tab_calculator": "Simplex-Rechner",
        "tab_manual": "Benutzerhandbuch",

        # Tableau Definition
        "tableau_definition": "Tableau-Definition",
        "tableau_loaded": "✓ Tableau geladen",
        "lp_formulation": "📐 LP-Formulierung (LaTeX)",
        "view_tableau": "📊 Aktuelles Tableau-Matrix anzeigen",
        "tableau_info": "Tableau-Info:",
        "variables": "Variablen",
        "constraints": "Nebenbedingungen",
        "basis": "Basis",

        # Input fields
        "objective_function": "Zielfunktion",
        "objective_placeholder": "Zu optimierende Zielfunktion",
        "objective_example": "Beispiel: 3*x_1 + 4*x_2 - 2*x_3",
        "constraints_label": "Nebenbedingungen",
        "constraints_placeholder": "Nebenbedingungen (kommagetrennt)",
        "constraints_example": "Beispiel: 2*x_1 + 3*x_2 <= 4, x_1 + x_2 >= 2",

        # Buttons
        "create_tableau": "Tableau aus Ausdrücken erstellen",
        "solve_automatically": "🚀 Automatisch lösen",
        "perform_pivot": "Pivot durchführen",
        "new_problem": "Neues Problem",
        "apply": "Anwenden",

        # Status
        "status": "Status",
        "optimal": "OPTIMAL",
        "not_optimal": "Nicht optimal",
        "degenerate": "Entartete Lösung",
        "unbounded": "Unbeschränkt",
        "pivot_steps": "Pivot-Schritte",
        "current_basis": "Aktuelle Basis",
        "objective_value": "Zielfunktionswert (z)",

        # Tableau display
        "current_tableau": "Aktuelles Tableau",
        "constraints_section": "Nebenbedingungen:",
        "objective_section": "Zielfunktion (Z):",
        "current_solution": "Aktuelle Lösung:",
        "basic_variables": "Basisvariablen:",
        "nonbasic_variables": "Nichtbasisvariablen:",
        "complete_solution": "📊 Vollständiger Lösungsvektor",

        # Reduced costs
        "reduced_costs": "Reduzierte Kosten (Schattenpreise)",
        "can_improve": "[!]",
        "cannot_improve": "[ ]",

        # Pivot operations
        "pivot_operations": "Pivot-Operationen",
        "select_entering": "Eingangsvariable wählen",
        "select_leaving": "Ausgangsvariable wählen",
        "show_pivot_details": "Pivot-Details anzeigen",
        "entering_variable": "Eingangsvariable",
        "leaving_variable": "Ausgangsvariable",
        "pivot_element": "Pivot-Element",
        "minimum_ratio_test": "Minimum-Ratio-Test",
        "no_improving": "Aktuelles Tableau ist optimal. Keine verbessernden Pivots verfügbar.",

        # History
        "history": "Verlauf",
        "iteration": "Iteration",
        "first_step": "Erster Schritt",
        "previous_step": "Vorheriger Schritt",
        "next_step": "Nächster Schritt",
        "current_step": "Aktueller Schritt",

        # Messages
        "success_created": "✓ Tableau aus Ausdrücken erstellt!",
        "success_solved": "✓ Gelöst in {0} Iterationen!",
        "success_pivot": "✓ Pivot erfolgreich! Z verbessert von {0:.4f} auf {1:.4f}",
        "error_creating": "Fehler beim Erstellen des Tableaus: {0}",
        "info_enter_problem": "Geben Sie Zielfunktion und Nebenbedingungen als mathematische Ausdrücke ein",

        # Preview
        "preview_parsing": "Vorschau Parsing",
        "latex_preview": "📐 LaTeX-Vorschau",
        "objective_coeffs": "Zielfunktionskoeffizienten:",
        "objective_constant": "Zielfunktionskonstante:",
        "found_constraints": "{0} Nebenbedingungen gefunden:",
        "variables_detected": "Erkannte Variablen:",
        "parsing_error": "Parsing-Fehler: {0}",
        "latex_error": "LaTeX-Rendering-Fehler: {0}",

        # Maximize/Minimize
        "maximize": "Maximiere",
        "minimize": "Minimiere",
        "subject_to": "unter den Nebenbedingungen",
    }
}


def get_text(key: str, lang: str = "en") -> str:
    """Get translated text for a given key."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
