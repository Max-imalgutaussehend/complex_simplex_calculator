"""
Streamlit UI for interactive Simplex tableau manipulation.
Allows users to define custom tableaus, perform manual pivots, and study the algorithm.
"""

import streamlit as st
import numpy as np
import pandas as pd
from typing import List
from simplex import SimplexTableau, create_standard_tableau, create_tableau_from_parsed, solve_simplex_automatic
from parser import parse_lp_problem, LPParser
from translations import get_text
from tableau_renderer import render_tableau_with_inequalities


def initialize_session_state():
    """Initialize session state variables."""
    if 'tableau' not in st.session_state:
        st.session_state.tableau = None
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'step_number' not in st.session_state:
        st.session_state.step_number = 0
    if 'pivot_info' not in st.session_state:
        st.session_state.pivot_info = None
    if 'objective_input' not in st.session_state:
        st.session_state.objective_input = None
    if 'constraints_input' not in st.session_state:
        st.session_state.constraints_input = None
    if 'objective_type_saved' not in st.session_state:
        st.session_state.objective_type_saved = None
    if 'language' not in st.session_state:
        st.session_state.language = "de"  # Default to German


def convert_to_latex(objective: str, constraints_str: str, objective_type: str = "max") -> str:
    """
    Convert LP problem to LaTeX format.

    Args:
        objective: Objective function string like "3*x_1 + 4*x_2"
        constraints_str: Constraints string like "2*x_1 + 3*x_2 <= 4, x_1 >= 0"
        objective_type: "max" or "min"

    Returns:
        LaTeX string for rendering
    """
    # Convert objective
    obj_latex = objective.replace("*", " \\cdot ")
    obj_latex = obj_latex.replace("x_", "x_{").replace("y_", "y_{").replace("s_", "s_{")
    # Close subscripts
    import re
    obj_latex = re.sub(r'x_\{(\d+)', r'x_{\1}', obj_latex)
    obj_latex = re.sub(r'y_\{(\d+)', r'y_{\1}', obj_latex)
    obj_latex = re.sub(r's_\{(\d+)', r's_{\1}', obj_latex)

    # Maximize/Minimize text
    opt_text = "\\text{Maximiere}" if objective_type == "max" else "\\text{Minimiere}"

    # Convert constraints
    constraints = [c.strip() for c in constraints_str.split(',') if c.strip()]
    constraint_latex_list = []

    for constraint in constraints:
        # Replace operators
        c_latex = constraint.replace("*", " \\cdot ")
        c_latex = c_latex.replace("<=", "\\leq")
        c_latex = c_latex.replace(">=", "\\geq")
        c_latex = c_latex.replace("=", "=")

        # Replace variables
        c_latex = c_latex.replace("x_", "x_{").replace("y_", "y_{").replace("s_", "s_{")
        c_latex = re.sub(r'x_\{(\d+)', r'x_{\1}', c_latex)
        c_latex = re.sub(r'y_\{(\d+)', r'y_{\1}', c_latex)
        c_latex = re.sub(r's_\{(\d+)', r's_{\1}', c_latex)

        constraint_latex_list.append(c_latex)

    # Build LaTeX string
    latex_str = f"{opt_text} \\quad {obj_latex}, \\text{{ unter den Nebenbedingungen}}"
    latex_str += "\\begin{cases}\n"
    for c_latex in constraint_latex_list:
        latex_str += f"  {c_latex} \\\\\n"
    latex_str += "\\end{cases}"

    return latex_str


def display_tableau_formatted(tableau: SimplexTableau, pivot_row=None, pivot_col=None, lang="de"):
    """
    Display tableau in a formatted way similar to emathhelp.net.
    Shows constraints and objective separately with better formatting.
    Now includes beautiful LaTeX system representation.
    """
    st.markdown("### " + get_text("current_tableau", lang))

    # Beautiful LaTeX representation with >= / <=
    with st.expander("📐 " + ("Gleichungssystem-Darstellung" if lang == "de" else "System Representation"), expanded=True):
        render_tableau_with_inequalities(tableau, lang)

    # Get tableau data
    df = tableau.get_dataframe()

    # Split into constraints and objective
    constraint_rows = df.iloc[:-1]
    objective_row = df.iloc[-1:]

    # Create styled dataframe
    def highlight_pivot(row):
        """Create highlighting style for pivot element."""
        styles = ['' for _ in row.index]
        if pivot_row is not None and pivot_col is not None:
            # Check if this is the pivot row
            if row.name == tableau.basis_variables[pivot_row]:
                var_name = tableau.variable_names[pivot_col]
                if var_name in row.index:
                    idx = row.index.get_loc(var_name)
                    styles[idx] = 'background-color: #ffeb3b; font-weight: bold; border: 2px solid #ff9800;'
        return styles

    # Display constraints
    st.markdown("#### " + get_text("constraints_section", lang))
    st.dataframe(
        constraint_rows.style.format("{:.4f}").apply(highlight_pivot, axis=1),
        width='stretch'
    )

    # Display objective function
    st.markdown("#### " + get_text("objective_section", lang))
    st.dataframe(
        objective_row.style.format("{:.4f}").background_gradient(cmap='RdYlGn', axis=1),
        width='stretch'
    )

    # Display current solution
    st.markdown("---")
    st.markdown("#### Current Solution:")

    solution = tableau.get_basic_solution()
    obj_value = tableau.get_objective_value()

    # Create columns for solution display
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("**Basic Variables:**")
        for var in tableau.basis_variables:
            value = solution[var]
            st.markdown(f"- **{var}** = {value:.4f}")

    with col2:
        st.markdown("**Non-basic Variables:**")
        nonbasic = [v for v in tableau.variable_names if v not in tableau.basis_variables]
        for var in nonbasic[:5]:  # Show first 5
            st.markdown(f"- **{var}** = 0.0000")
        if len(nonbasic) > 5:
            st.markdown(f"- ... ({len(nonbasic) - 5} more)")

    # Objective value prominently displayed
    st.markdown("---")
    st.markdown(f"### 🎯 **Z = {obj_value:.4f}**")

    # Show complete solution vector in expandable section
    with st.expander("📊 Complete Solution Vector", expanded=False):
        # Create DataFrame for complete solution
        sol_data = []
        for var in tableau.variable_names:
            val = solution[var]
            is_basic = "✓" if var in tableau.basis_variables else ""
            sol_data.append({
                "Variable": var,
                "Value": f"{val:.6f}",
                "Basic": is_basic
            })

        sol_df = pd.DataFrame(sol_data)
        st.dataframe(sol_df, width='stretch', hide_index=True)

        # Summary
        st.markdown("**Summary:**")
        st.markdown(f"- Decision variables: {len([v for v in tableau.variable_names if v.startswith('x')])}")
        st.markdown(f"- Slack variables: {len([v for v in tableau.variable_names if v.startswith('s')])}")
        st.markdown(f"- Basic variables: {len(tableau.basis_variables)}")
        st.markdown(f"- Non-basic (zero): {len(tableau.variable_names) - len(tableau.basis_variables)}")


def display_pivot_details(tableau: SimplexTableau, entering_var: str, leaving_var: str,
                         entering_col: int, leaving_row: int):
    """Display detailed pivot operation information."""
    st.markdown("---")
    st.markdown("### 📋 Pivot Operation Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Entering Variable:**")
        st.markdown(f"### ➡️ {entering_var}")
        rc = tableau.get_reduced_costs()[entering_var]
        st.markdown(f"Reduced cost: **{rc:.4f}**")

    with col2:
        st.markdown("**Leaving Variable:**")
        st.markdown(f"### ⬅️ {leaving_var}")
        value = tableau.tableau[leaving_row, -1]
        st.markdown(f"Current value: **{value:.4f}**")

    with col3:
        st.markdown("**Pivot Element:**")
        pivot_element = tableau.tableau[leaving_row, entering_col]
        st.markdown(f"### 🎯 {pivot_element:.4f}")
        st.markdown(f"Position: Row {leaving_row+1}, Col {entering_col+1}")

    # Show minimum ratio test
    st.markdown("---")
    st.markdown("#### 📊 Minimum Ratio Test")
    st.markdown("Choose the row with the **smallest non-negative ratio** to leave the basis.")

    candidates = tableau.get_leaving_variable_candidates(entering_col)

    ratio_data = []
    for row, var, ratio in candidates:
        rhs = tableau.tableau[row, -1]
        coef = tableau.tableau[row, entering_col]
        ratio_data.append({
            "✓": "✓✓✓" if var == leaving_var else "",
            "Basis Variable": var,
            "RHS": f"{rhs:.4f}",
            f"{entering_var} Coefficient": f"{coef:.4f}",
            "Ratio (RHS/Coef)": f"{ratio:.4f}",
        })

    ratio_df = pd.DataFrame(ratio_data)
    st.dataframe(ratio_df, width='stretch', hide_index=True)

    # Show the pivot operation formula
    st.markdown("---")
    st.markdown("#### 📐 Pivot Operation Steps")
    st.markdown(f"""
    1. **Divide pivot row** by pivot element ({pivot_element:.4f})
    2. **Eliminate** {entering_var} from all other rows
    3. **Update basis**: Replace {leaving_var} with {entering_var}
    """)


def display_iteration_summary(step_number: int, entering_var: str, leaving_var: str,
                             old_obj: float, new_obj: float):
    """Display summary of iteration."""
    st.markdown("---")
    st.markdown(f"### 🔄 Iteration {step_number} Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Entering", entering_var, delta="IN", delta_color="normal")

    with col2:
        st.metric("Leaving", leaving_var, delta="OUT", delta_color="inverse")

    with col3:
        obj_change = new_obj - old_obj
        st.metric("Z Value", f"{new_obj:.4f}", delta=f"{obj_change:+.4f}")


def create_empty_tableau(n_vars: int, n_constraints: int, var_names: List[str]) -> pd.DataFrame:
    """Create an empty tableau DataFrame for user input."""
    # Constraint rows + objective row
    row_names = [f'Row {i+1}' for i in range(n_constraints)] + ['z']
    col_names = var_names + ['RHS']

    # Initialize with zeros
    data = np.zeros((n_constraints + 1, n_vars + 1))

    return pd.DataFrame(data, index=row_names, columns=col_names)


def create_final_tableau(
    A: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
    objective_type: str = "max"
) -> SimplexTableau:
    """
    Create a final tableau where decision variables are in the basis.
    This allows manipulation of slack variables.

    Args:
        A: constraint matrix (m x n) - should be the inverse basis matrix times original A
        b: RHS vector (m) - values of basic variables
        c: objective coefficients (n)
        objective_type: "max" or "min"

    Returns:
        SimplexTableau with decision variables in basis
    """
    m, n = A.shape

    # Add slack variables
    slack_matrix = np.eye(m)
    A_augmented = np.hstack([A, slack_matrix])

    # Create tableau - identity for decision vars, negative of A for slack vars
    # This represents the tableau after decision variables entered the basis
    tableau = np.zeros((m + 1, n + m + 1))

    # For a final tableau, we want decision variables to have identity columns
    # and slack variables to have transformed coefficients
    tableau[:m, :n] = np.eye(m, n)  # Identity for first m decision variables
    tableau[:m, n:n+m] = A[:, :m] if m <= n else np.eye(m)[:, :m]  # Slack variable coefficients
    tableau[:m, -1] = b  # RHS

    # Objective row - compute reduced costs for slack variables
    # For a final tableau, decision variable reduced costs should be 0
    tableau[-1, :n] = 0  # Decision variables have zero reduced costs (optimal)

    # Slack variables will have non-zero reduced costs (can be manipulated)
    if objective_type == "max":
        tableau[-1, n:n+m] = -c[:m] if m <= len(c) else np.zeros(m)
    else:
        tableau[-1, n:n+m] = c[:m] if m <= len(c) else np.zeros(m)

    # Objective value
    tableau[-1, -1] = np.dot(c[:min(m, len(c))], b[:min(m, len(c))])

    # Variable names
    var_names = [f'x{i+1}' for i in range(n)] + [f's{i+1}' for i in range(m)]

    # Basis is first m decision variables
    basis_vars = [f'x{i+1}' for i in range(m)]

    return SimplexTableau(tableau, var_names, basis_vars, objective_type)


def main():
    st.set_page_config(
        page_title="Interactive Simplex Calculator",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    initialize_session_state()

    # Language selector at the very top
    lang = st.session_state.language

    st.title(get_text("title", lang))
    st.markdown(get_text("subtitle", lang))

    # Add tabs for main interface and manual
    tab1, tab2 = st.tabs([get_text("tab_calculator", lang), get_text("tab_manual", lang)])

    with tab2:
        # Display the manual
        try:
            with open("MANUAL.md", "r") as f:
                manual_content = f.read()
            st.markdown(manual_content)
        except FileNotFoundError:
            st.error("MANUAL.md not found. Please ensure the manual file exists in the application directory.")

    with tab1:
        # Sidebar: Configuration
        with st.sidebar:
            # Language selector at the top
            st.session_state.language = st.selectbox(
                "🌐 Language / Sprache",
                ["de", "en"],
                format_func=lambda x: "🇩🇪 Deutsch" if x == "de" else "🇬🇧 English",
                index=0 if st.session_state.language == "de" else 1
            )
            lang = st.session_state.language

            st.markdown("---")
            st.header(get_text("configuration", lang))

            mode = st.radio(
                get_text("tableau_mode", lang),
                [
                    "Expression Input (Flexible)",
                    "Create New Tableau",
                    "Matrix Input (Standard Form)",
                    "Final Tableau (Endtableau)"
                ],
                format_func=lambda x: {
                    "Expression Input (Flexible)": get_text("mode_expression", lang),
                    "Create New Tableau": get_text("mode_create", lang),
                    "Matrix Input (Standard Form)": get_text("mode_matrix", lang),
                    "Final Tableau (Endtableau)": get_text("mode_final", lang)
                }.get(x, x),
                help=get_text("tableau_mode", lang)
            )

            objective_type = st.selectbox(
                get_text("objective_type", lang),
                ["max", "min"],
                help=get_text("objective_type", lang)
            )

            # Endtableau mode checkbox (for Expression Input only)
            if mode == "Expression Input (Flexible)":
                endtableau_mode = st.checkbox(
                    get_text("endtableau_mode", lang),
                    value=False,
                    help=get_text("endtableau_help", lang)
                )
            else:
                endtableau_mode = False

            if mode == "Expression Input (Flexible)":
                st.markdown("---")
                st.subheader(get_text("examples", lang))
                with st.expander(get_text("show_examples", lang)):
                    st.code("""
Objective:
  3*x_1 + 4*x_2
  2*x_1 - 3*x_2 + 5*x_3

Constraints (comma-separated):
  2*x_1 + 3*x_2 <= 4
  x_1 + x_2 >= 2
  x_1 - x_2 = 1

With slack variables:
  2*x_1 + 3*x_2 + 4*y_1 <= 10
  x_1 + s_1 >= 5

Negative RHS (automatically handled):
  x_1 + x_2 <= -3  (converted to: -x_1 - x_2 >= 3)
                    """)

            elif mode == "Create New Tableau":
                n_vars = st.number_input(
                    "Number of Variables",
                    min_value=1,
                    max_value=20,
                    value=4,
                    help="Total variables including slack/surplus"
                )

                n_constraints = st.number_input(
                    "Number of Constraints",
                    min_value=1,
                    max_value=20,
                    value=2,
                    help="Number of constraint rows (excluding objective)"
                )

                # Variable names
                st.subheader("Variable Names")
                default_names = [f'x{i+1}' for i in range(n_vars)]
                var_names_input = st.text_input(
                    "Variable Names (comma-separated)",
                    value=", ".join(default_names),
                    help="e.g., x1, x2, s1, s2"
                )
                var_names = [name.strip() for name in var_names_input.split(',')]

                if len(var_names) != n_vars:
                    st.warning(f"⚠️ Please provide exactly {n_vars} variable names")
                    var_names = default_names

            elif mode == "Matrix Input (Standard Form)":
                n_decision_vars = st.number_input(
                    "Number of Decision Variables",
                    min_value=1,
                    max_value=20,
                    value=2,
                    help="Original decision variables (slack added automatically)"
                )

                n_constraints = st.number_input(
                    "Number of Constraints",
                    min_value=1,
                    max_value=20,
                    value=2,
                    help="Number of constraints"
                )

            else:  # Final Tableau (Endtableau)
                n_decision_vars = st.number_input(
                    "Number of Decision Variables",
                    min_value=1,
                    max_value=20,
                    value=2,
                    help="Original decision variables (will be in basis)"
                )

                n_constraints = st.number_input(
                    "Number of Constraints",
                    min_value=1,
                    max_value=20,
                    value=2,
                    help="Number of constraints"
                )

            st.markdown("---")

            if st.button("Reset Tableau"):
                st.session_state.tableau = None
                st.session_state.history = []
                st.session_state.step_number = 0
                st.rerun()

        # Main area
        col1, col2 = st.columns([2, 1])

        with col1:
            st.header("Tableau Definition")

            # Show current tableau if it exists
            if st.session_state.tableau is not None:
                st.success("✓ Tableau loaded")

                # Show original LP formulation in LaTeX if available
                if (st.session_state.objective_input is not None and
                    st.session_state.constraints_input is not None and
                    st.session_state.objective_type_saved is not None):

                    with st.expander("📐 LP Formulation (LaTeX)", expanded=True):
                        try:
                            latex_str = convert_to_latex(
                                st.session_state.objective_input,
                                st.session_state.constraints_input,
                                st.session_state.objective_type_saved
                            )
                            st.latex(latex_str)
                        except Exception as e:
                            st.error(f"LaTeX rendering error: {str(e)}")

                with st.expander("📊 View Current Tableau Matrix", expanded=False):
                    tableau = st.session_state.tableau
                    df = tableau.get_dataframe()
                    st.dataframe(df.style.format("{:.4f}"), width='stretch')

                    st.markdown("**Tableau Info:**")
                    st.markdown(f"- Variables: {len(tableau.variable_names)}")
                    st.markdown(f"- Constraints: {tableau.n_constraints}")
                    st.markdown(f"- Basis: {', '.join(tableau.basis_variables[:5])}{'...' if len(tableau.basis_variables) > 5 else ''}")

        if mode == "Expression Input (Flexible)":
            # Expression-based input
            if st.session_state.tableau is None:
                st.info("Enter objective function and constraints as mathematical expressions")

                # Objective function input
                st.subheader("Objective Function")
                objective_input = st.text_area(
                    "Objective to optimize",
                    value="3*x_1 + 4*x_2",
                    help="Example: 3*x_1 + 4*x_2 - 2*x_3",
                    height=80
                )

                # Constraints input
                st.subheader("Constraints")
                constraints_input = st.text_area(
                    "Constraints (comma-separated)",
                    value="2*x_1 + 3*x_2 <= 18,\n2*x_1 + x_2 <= 12,\nx_1 + 2*x_2 <= 10",
                    help="Example: 2*x_1 + 3*x_2 <= 4, x_1 + x_2 >= 2",
                    height=150
                )

                # LaTeX Preview
                with st.expander("📐 LaTeX Preview", expanded=True):
                    try:
                        latex_str = convert_to_latex(objective_input, constraints_input, objective_type)
                        st.latex(latex_str)
                    except Exception as e:
                        st.error(f"LaTeX rendering error: {str(e)}")

                # Preview parsing
                with st.expander("Preview Parsing"):
                    try:
                        parser = LPParser()
                        obj_coeffs, obj_constant = parser.parse_expression(objective_input)
                        st.write("**Objective coefficients:**", obj_coeffs)
                        if obj_constant != 0:
                            st.write("**Objective constant:**", obj_constant)

                        constraints = parser.parse_constraints(constraints_input)
                        st.write(f"**Found {len(constraints)} constraints:**")
                        for i, (coeffs, op, rhs) in enumerate(constraints):
                            st.write(f"Constraint {i+1}: {coeffs} {op} {rhs}")

                        all_vars = parser.get_all_variables()
                        st.write("**Variables detected:**", ", ".join(all_vars))
                    except Exception as e:
                        st.error(f"Parsing error: {str(e)}")

                if st.button("Create Tableau from Expressions", type="primary"):
                    try:
                        # Parse LP problem
                        A, b, c, var_names, basis_vars, obj_constant = parse_lp_problem(
                            objective_input,
                            constraints_input,
                            objective_type,
                            endtableau_mode=endtableau_mode
                        )

                        # Create tableau using parsed data
                        st.session_state.tableau = create_tableau_from_parsed(
                            A, b, c, var_names, basis_vars, objective_type, obj_constant
                        )

                        # Save inputs for later display
                        st.session_state.objective_input = objective_input
                        st.session_state.constraints_input = constraints_input
                        st.session_state.objective_type_saved = objective_type

                        st.session_state.history = [st.session_state.tableau]
                        st.session_state.step_number = 0
                        st.success("Tableau created from expressions!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating tableau: {str(e)}")

        elif mode == "Create New Tableau":
            # Create custom tableau
            if st.session_state.tableau is None:
                st.info("Enter your tableau values below. Last row is the objective function (z).")

                # Create editable dataframe
                empty_df = create_empty_tableau(n_vars, n_constraints, var_names)

                edited_df = st.data_editor(
                    empty_df,
                    width='stretch',
                    num_rows="fixed",
                    key="tableau_input"
                )

                # Basis selection
                st.subheader("Initial Basis Variables")
                st.info(f"Select {n_constraints} basic variables (one per constraint row)")

                basis_cols = st.columns(min(4, n_constraints))
                basis_vars = []

                for i in range(n_constraints):
                    col_idx = i % len(basis_cols)
                    with basis_cols[col_idx]:
                        basis_var = st.selectbox(
                            f"Row {i+1} basis",
                            options=var_names,
                            index=min(i, len(var_names)-1),
                            key=f"basis_{i}"
                        )
                        basis_vars.append(basis_var)

                if st.button("Create Tableau", type="primary"):
                    # Convert edited dataframe to tableau
                    tableau_array = edited_df.values

                    st.session_state.tableau = SimplexTableau(
                        tableau=tableau_array,
                        variable_names=var_names,
                        basis_variables=basis_vars,
                        objective_type=objective_type
                    )
                    st.session_state.history = [st.session_state.tableau]
                    st.session_state.step_number = 0
                    st.success("Tableau created!")
                    st.rerun()

        elif mode == "Matrix Input (Standard Form)":
            if st.session_state.tableau is None:
                st.info("Enter constraint matrix A, RHS vector b, and objective coefficients c")

                # Input for standard form
                st.subheader("Constraint Matrix A")
                A_df = st.data_editor(
                    pd.DataFrame(
                        np.zeros((n_constraints, n_decision_vars)),
                        columns=[f'x{i+1}' for i in range(n_decision_vars)]
                    ),
                    width='stretch',
                    key="matrix_A"
                )

                col_b, col_c = st.columns(2)

                with col_b:
                    st.subheader("RHS Vector b")
                    b_df = st.data_editor(
                        pd.DataFrame(
                            np.ones((n_constraints, 1)),
                            columns=['b']
                        ),
                        width='stretch',
                        key="vector_b"
                    )

                with col_c:
                    st.subheader("Objective Coefficients c")
                    c_df = st.data_editor(
                        pd.DataFrame(
                            np.ones((1, n_decision_vars)),
                            columns=[f'x{i+1}' for i in range(n_decision_vars)]
                        ),
                        width='stretch',
                        key="vector_c"
                    )

                if st.button("Create Initial Tableau (Slack in Basis)", type="primary"):
                    A = A_df.values
                    b = b_df.values.flatten()
                    c = c_df.values.flatten()

                    st.session_state.tableau = create_standard_tableau(
                        A, b, c, objective_type
                    )
                    st.session_state.history = [st.session_state.tableau]
                    st.session_state.step_number = 0
                    st.success("Initial tableau created with slack variables in basis!")
                    st.rerun()

        else:  # Final Tableau (Endtableau)
            if st.session_state.tableau is None:
                st.info("Create a final tableau with decision variables (x_n) in the basis. You can then optimize slack variables!")

                # Input for final tableau
                st.subheader("Basic Variable Values (b)")
                st.markdown("Enter the values of the basic decision variables (RHS)")
                b_df = st.data_editor(
                    pd.DataFrame(
                        np.array([[10.0], [5.0]])[:n_constraints],
                        columns=['Value'],
                        index=[f'x{i+1}' for i in range(n_constraints)]
                    ),
                    width='stretch',
                    key="final_b"
                )

                st.subheader("Slack Variable Coefficients")
                st.markdown("Enter the coefficients of slack variables in each constraint")
                slack_df = st.data_editor(
                    pd.DataFrame(
                        np.eye(n_constraints),
                        columns=[f's{i+1}' for i in range(n_constraints)],
                        index=[f'x{i+1}' for i in range(n_constraints)]
                    ),
                    width='stretch',
                    key="slack_coef"
                )

                col_obj, col_rc = st.columns(2)

                with col_obj:
                    st.subheader("Objective Coefficients (c)")
                    st.markdown("Shadow prices / dual values")
                    c_df = st.data_editor(
                        pd.DataFrame(
                            np.array([[3.0], [2.0]])[:n_constraints],
                            columns=['Coefficient'],
                            index=[f'x{i+1}' for i in range(n_constraints)]
                        ),
                        width='stretch',
                        key="final_c"
                    )

                with col_rc:
                    st.subheader("Slack Reduced Costs")
                    st.markdown("Reduced costs for slack variables")
                    rc_df = st.data_editor(
                        pd.DataFrame(
                            np.array([[1.0], [0.5]])[:n_constraints],
                            columns=['Reduced Cost'],
                            index=[f's{i+1}' for i in range(n_constraints)]
                        ),
                        width='stretch',
                        key="slack_rc"
                    )

                # Additional decision variables beyond basis
                if n_decision_vars > n_constraints:
                    st.subheader(f"Non-basic Decision Variables x{n_constraints+1} to x{n_decision_vars}")
                    st.markdown("Coefficients for non-basic decision variables")
                    nonbasic_df = st.data_editor(
                        pd.DataFrame(
                            np.zeros((n_constraints, n_decision_vars - n_constraints)),
                            columns=[f'x{i+1}' for i in range(n_constraints, n_decision_vars)],
                            index=[f'x{i+1}' for i in range(n_constraints)]
                        ),
                        width='stretch',
                        key="nonbasic_x"
                    )

                if st.button("Create Final Tableau (x_n in Basis)", type="primary"):
                    b = b_df.values.flatten()
                    c = c_df.values.flatten()
                    slack_coef = slack_df.values
                    slack_rc = rc_df.values.flatten()

                    # Build the final tableau manually
                    total_vars = n_decision_vars + n_constraints
                    tableau = np.zeros((n_constraints + 1, total_vars + 1))

                    # Identity for basic decision variables (first n_constraints columns)
                    tableau[:n_constraints, :n_constraints] = np.eye(n_constraints)

                    # Non-basic decision variables (if any)
                    if n_decision_vars > n_constraints:
                        tableau[:n_constraints, n_constraints:n_decision_vars] = nonbasic_df.values

                    # Slack variable coefficients
                    tableau[:n_constraints, n_decision_vars:n_decision_vars+n_constraints] = slack_coef

                    # RHS
                    tableau[:n_constraints, -1] = b

                    # Objective row - zeros for basic variables
                    tableau[-1, :n_constraints] = 0

                    # Non-basic decision variable reduced costs
                    if n_decision_vars > n_constraints:
                        tableau[-1, n_constraints:n_decision_vars] = 0  # Can be customized

                    # Slack variable reduced costs
                    tableau[-1, n_decision_vars:n_decision_vars+n_constraints] = slack_rc

                    # Objective value
                    tableau[-1, -1] = np.dot(c, b)

                    # Variable names
                    var_names = [f'x{i+1}' for i in range(n_decision_vars)] + [f's{i+1}' for i in range(n_constraints)]

                    # Basis variables (first n_constraints decision variables)
                    basis_vars = [f'x{i+1}' for i in range(n_constraints)]

                    st.session_state.tableau = SimplexTableau(
                        tableau=tableau,
                        variable_names=var_names,
                        basis_variables=basis_vars,
                        objective_type=objective_type
                    )
                    st.session_state.history = [st.session_state.tableau]
                    st.session_state.step_number = 0
                    st.success("Final tableau created with decision variables in basis! Now you can optimize slack variables!")
                    st.rerun()

    with col2:
        if st.session_state.tableau is not None:
            st.header("Status")

            tableau = st.session_state.tableau

            # Objective value
            obj_value = tableau.get_objective_value()
            st.metric(
                "Objective Value (z)",
                f"{obj_value:.4f}"
            )

            # Optimality
            is_optimal = tableau.is_optimal()
            if is_optimal:
                st.success("OPTIMAL")
            else:
                st.info("Not optimal")

            # Degeneracy
            if tableau.is_degenerate():
                st.warning("Degenerate solution")

            # Step counter
            st.metric("Pivot Steps", st.session_state.step_number)

            st.markdown("---")

            # Auto-solve button
            if not is_optimal:
                if st.button("🚀 Solve Automatically", type="primary", use_container_width=True):
                    try:
                        all_tableaus = solve_simplex_automatic(tableau)
                        st.session_state.history = all_tableaus
                        st.session_state.tableau = all_tableaus[-1]
                        st.session_state.step_number = len(all_tableaus) - 1
                        st.success(f"✓ Solved in {len(all_tableaus)-1} iterations!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Auto-solve failed: {str(e)}")

            st.markdown("---")

            # Current basis
            st.subheader("Current Basis")
            for i, var in enumerate(tableau.basis_variables):
                value = tableau.tableau[i, -1]
                st.text(f"{var} = {value:.4f}")

    # Display current tableau
    if st.session_state.tableau is not None:
        st.markdown("---")

        tableau = st.session_state.tableau

        # Check if we have pivot info to highlight
        pivot_row = None
        pivot_col = None
        if st.session_state.pivot_info:
            pivot_row = st.session_state.pivot_info.get('row')
            pivot_col = st.session_state.pivot_info.get('col')

        # Use new formatted display
        display_tableau_formatted(tableau, pivot_row, pivot_col, lang)

        # Show last pivot info if available
        if st.session_state.pivot_info and st.session_state.step_number > 0:
            with st.expander(f"📜 Last Pivot (Iteration {st.session_state.step_number})", expanded=False):
                info = st.session_state.pivot_info
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Entered Basis", info['entering'], delta="IN")

                with col2:
                    st.metric("Left Basis", info['leaving'], delta="OUT")

                with col3:
                    if 'old_obj' in info:
                        old_obj = info['old_obj']
                        new_obj = tableau.get_objective_value()
                        change = new_obj - old_obj
                        st.metric("Z Change", f"{change:+.4f}", delta=f"{new_obj:.4f}")

        # Reduced costs section
        st.markdown("---")
        st.subheader("Reduced Costs (Shadow Prices)")
        reduced_costs = tableau.get_reduced_costs()

        rc_cols = st.columns(min(5, len(reduced_costs)))
        for i, (var, cost) in enumerate(reduced_costs.items()):
            col_idx = i % len(rc_cols)
            with rc_cols[col_idx]:
                indicator = "[!]" if (objective_type == "max" and cost < -1e-6) or (objective_type == "min" and cost > 1e-6) else "[ ]"
                delta_color = "inverse" if abs(cost) > 1e-6 else "off"
                st.metric(f"{indicator} {var}", f"{cost:.4f}", delta=None, delta_color=delta_color)

        # Pivot controls
        st.markdown("---")
        st.header("Pivot Operations")

        if is_optimal:
            st.success("Current tableau is optimal. No improving pivots available.")
        else:
            pivot_col1, pivot_col2, pivot_col3 = st.columns([2, 2, 1])

            with pivot_col1:
                st.subheader("1. Select Entering Variable")

                # Show candidates
                candidates = tableau.get_entering_variable_candidates()
                if candidates:
                    st.info(f"Improving: {', '.join(candidates)}")

                # Allow selection of any variable
                entering_var = st.selectbox(
                    "Entering variable (pivot column)",
                    options=tableau.variable_names,
                    help="Choose any variable to enter the basis"
                )
                entering_col = tableau.variable_names.index(entering_var)

            with pivot_col2:
                st.subheader("2. Select Leaving Variable")

                # Check unboundedness
                if tableau.is_unbounded(entering_col):
                    st.error("Problem is UNBOUNDED for this entering variable!")
                    leaving_candidates = []
                else:
                    leaving_candidates = tableau.get_leaving_variable_candidates(entering_col)

                    if leaving_candidates:
                        st.info(f"Minimum ratio: {leaving_candidates[0][1]} ({leaving_candidates[0][2]:.4f})")

                        # Display all candidates with ratios
                        leaving_options = [
                            f"{var} (ratio: {ratio:.4f})"
                            for _, var, ratio in leaving_candidates
                        ]

                        leaving_choice = st.selectbox(
                            "Leaving variable (pivot row)",
                            options=leaving_options,
                            help="Variable to leave the basis (minimum ratio test)"
                        )

                        # Extract row index
                        selected_idx = leaving_options.index(leaving_choice)
                        leaving_row = leaving_candidates[selected_idx][0]
                    else:
                        st.warning("No valid leaving variable (all coefficients <= 0)")
                        leaving_row = None

            with pivot_col3:
                st.subheader("3. Pivot")

                if leaving_candidates and leaving_row is not None:
                    pivot_element = tableau.tableau[leaving_row, entering_col]
                    st.metric("Pivot Element", f"{pivot_element:.4f}")

                    # Show pivot details before performing
                    leaving_var = leaving_candidates[selected_idx][1]

                    with st.expander("Show Pivot Details", expanded=False):
                        display_pivot_details(tableau, entering_var, leaving_var, entering_col, leaving_row)

                    if st.button("Perform Pivot", type="primary"):
                        try:
                            # Save old objective value
                            old_obj = tableau.get_objective_value()

                            # Save pivot info for highlighting
                            st.session_state.pivot_info = {
                                'row': leaving_row,
                                'col': entering_col,
                                'entering': entering_var,
                                'leaving': leaving_var,
                                'old_obj': old_obj
                            }

                            new_tableau = tableau.pivot(leaving_row, entering_col)
                            st.session_state.tableau = new_tableau
                            st.session_state.history.append(new_tableau)
                            st.session_state.step_number += 1

                            # Show iteration summary
                            new_obj = new_tableau.get_objective_value()
                            st.success(f"✓ Pivot complete: {entering_var} → IN, {leaving_var} → OUT")
                            st.info(f"Objective improved from {old_obj:.4f} to {new_obj:.4f} (Δ = {new_obj - old_obj:+.4f})")

                            st.rerun()
                        except Exception as e:
                            st.error(f"Pivot failed: {str(e)}")

        # History navigation
        if len(st.session_state.history) > 1:
            st.markdown("---")
            st.subheader("History")

            hist_col1, hist_col2, hist_col3 = st.columns(3)

            with hist_col1:
                if st.button("First Step"):
                    st.session_state.tableau = st.session_state.history[0]
                    st.session_state.step_number = 0
                    st.rerun()

            with hist_col2:
                if st.session_state.step_number > 0:
                    if st.button("Previous Step"):
                        st.session_state.step_number -= 1
                        st.session_state.tableau = st.session_state.history[st.session_state.step_number]
                        st.rerun()

            with hist_col3:
                if st.session_state.step_number < len(st.session_state.history) - 1:
                    if st.button("Next Step"):
                        st.session_state.step_number += 1
                        st.session_state.tableau = st.session_state.history[st.session_state.step_number]
                        st.rerun()


if __name__ == "__main__":
    main()
