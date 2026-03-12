"""
Streamlit UI for interactive Simplex tableau manipulation.
Allows users to define custom tableaus, perform manual pivots, and study the algorithm.
"""

import streamlit as st
import numpy as np
import pandas as pd
from typing import List
from simplex import SimplexTableau, create_standard_tableau, create_tableau_from_parsed
from parser import parse_lp_problem, LPParser


def initialize_session_state():
    """Initialize session state variables."""
    if 'tableau' not in st.session_state:
        st.session_state.tableau = None
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'step_number' not in st.session_state:
        st.session_state.step_number = 0


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

    st.title("Interactive Simplex Tableau Calculator")
    st.markdown("""
    This tool allows you to manually manipulate simplex tableaus, perform pivot operations,
    and optimize **any variable** (including slack variables). Perfect for studying the Simplex algorithm.
    """)

    initialize_session_state()

    # Add tabs for main interface and manual
    tab1, tab2 = st.tabs(["Simplex Calculator", "User Manual"])

    with tab2:
        # Display the manual
        try:
            with open("MANUAL.md", "r") as f:
                manual_content = f.read()
            st.markdown(manual_content)
        except FileNotFoundError:
            st.error("MANUAL.md not found. Please ensure the manual file exists in the application directory.")

    with tab1:
        # Main calculator interface
        main_calculator_interface(objective_type_global=None)


def main_calculator_interface(objective_type_global):

    # Sidebar: Configuration
    with st.sidebar:
        st.header("Configuration")

        mode = st.radio(
            "Tableau Mode",
            [
                "Expression Input (Flexible)",
                "Create New Tableau",
                "Matrix Input (Standard Form)",
                "Final Tableau (Endtableau)"
            ],
            help="Choose input method: expressions, manual tableau, matrices, or final tableau"
        )

        objective_type = st.selectbox(
            "Objective Type",
            ["max", "min"],
            help="Maximize or minimize objective function"
        )

        if mode == "Expression Input (Flexible)":
            st.markdown("---")
            st.subheader("Examples")
            with st.expander("Show syntax examples"):
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

                # Preview parsing
                with st.expander("Preview Parsing"):
                    try:
                        parser = LPParser()
                        obj_coeffs = parser.parse_expression(objective_input)
                        st.write("**Objective coefficients:**", obj_coeffs)

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
                        A, b, c, var_names, basis_vars = parse_lp_problem(
                            objective_input,
                            constraints_input,
                            objective_type
                        )

                        # Create tableau using parsed data
                        st.session_state.tableau = create_tableau_from_parsed(
                            A, b, c, var_names, basis_vars, objective_type
                        )

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
                    use_container_width=True,
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
                    use_container_width=True,
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
                        use_container_width=True,
                        key="vector_b"
                    )

                with col_c:
                    st.subheader("Objective Coefficients c")
                    c_df = st.data_editor(
                        pd.DataFrame(
                            np.ones((1, n_decision_vars)),
                            columns=[f'x{i+1}' for i in range(n_decision_vars)]
                        ),
                        use_container_width=True,
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
                    use_container_width=True,
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
                    use_container_width=True,
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
                        use_container_width=True,
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
                        use_container_width=True,
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
                        use_container_width=True,
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

            # Current basis
            st.subheader("Current Basis")
            for i, var in enumerate(tableau.basis_variables):
                value = tableau.tableau[i, -1]
                st.text(f"{var} = {value:.4f}")

    # Display current tableau
    if st.session_state.tableau is not None:
        st.markdown("---")
        st.header("Current Tableau")

        tableau = st.session_state.tableau
        df = tableau.get_dataframe()

        # Highlight formatting
        def highlight_negative(val):
            """Highlight negative reduced costs."""
            try:
                if float(val) < -1e-6:
                    return 'background-color: #ffcccc'
                elif float(val) > 1e-6:
                    return 'background-color: #ccffcc'
            except:
                pass
            return ''

        # Display with styling
        st.dataframe(
            df.style.format("{:.4f}"),
            use_container_width=True
        )

        # Reduced costs
        st.subheader("Reduced Costs")
        reduced_costs = tableau.get_reduced_costs()

        rc_cols = st.columns(min(4, len(reduced_costs)))
        for i, (var, cost) in enumerate(reduced_costs.items()):
            col_idx = i % len(rc_cols)
            with rc_cols[col_idx]:
                indicator = "[!]" if (objective_type == "max" and cost < -1e-6) or (objective_type == "min" and cost > 1e-6) else "[ ]"
                st.metric(f"{indicator} {var}", f"{cost:.4f}")

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

                    if st.button("Perform Pivot", type="primary"):
                        try:
                            new_tableau = tableau.pivot(leaving_row, entering_col)
                            st.session_state.tableau = new_tableau
                            st.session_state.history.append(new_tableau)
                            st.session_state.step_number += 1
                            st.success(f"Pivoted: {entering_var} enters, {leaving_candidates[selected_idx][1]} leaves")
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

        # Basic solution
        st.markdown("---")
        st.subheader("Current Basic Feasible Solution")

        solution = tableau.get_basic_solution()
        sol_cols = st.columns(min(4, len(solution)))

        for i, (var, value) in enumerate(solution.items()):
            col_idx = i % len(sol_cols)
            with sol_cols[col_idx]:
                is_basic = var in tableau.basis_variables
                indicator = "[B]" if is_basic else "[ ]"
                st.text(f"{indicator} {var} = {value:.4f}")


if __name__ == "__main__":
    main()
