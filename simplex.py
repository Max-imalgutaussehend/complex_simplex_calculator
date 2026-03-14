"""
Simplex algorithm core functionality for interactive tableau manipulation.
Supports arbitrary tableaus and allows optimization of any variable including slack variables.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional, Dict


class SimplexTableau:
    """
    Represents a simplex tableau with support for arbitrary configurations.
    Allows manual pivot operations and tracks the current basis.
    """

    def __init__(self,
                 tableau: np.ndarray,
                 variable_names: List[str],
                 basis_variables: List[str],
                 objective_type: str = "max"):
        """
        Initialize a simplex tableau.

        Args:
            tableau: numpy array where last row is objective, last column is RHS
            variable_names: names of all variables (excluding RHS)
            basis_variables: names of current basic variables
            objective_type: "max" or "min"
        """
        self.tableau = tableau.astype(float)
        self.variable_names = variable_names
        self.basis_variables = basis_variables
        self.objective_type = objective_type.lower()
        self.n_constraints = len(tableau) - 1  # excluding objective row
        self.n_variables = len(variable_names)

    def get_dataframe(self) -> pd.DataFrame:
        """Return tableau as a pandas DataFrame for display."""
        row_names = self.basis_variables + ['z']
        col_names = self.variable_names + ['RHS']
        return pd.DataFrame(self.tableau, index=row_names, columns=col_names)

    def get_reduced_costs(self) -> Dict[str, float]:
        """
        Get reduced costs (objective row coefficients) for all variables.
        For maximization: negative means can improve objective
        For minimization: positive means can improve objective
        """
        reduced_costs = {}
        for i, var_name in enumerate(self.variable_names):
            reduced_costs[var_name] = self.tableau[-1, i]
        return reduced_costs

    def get_objective_value(self) -> float:
        """
        Return current objective function value.
        Computes from basic solution: Z = sum(c_i * x_i) for all variables.
        """
        # Get basic solution
        solution = self.get_basic_solution()

        # We need the original objective coefficients
        # For a proper calculation, we need to track original c vector
        # For now, use the RHS of objective row
        return self.tableau[-1, -1]

    def compute_objective_from_solution(self, c_original: np.ndarray) -> float:
        """
        Compute objective value from current solution and original objective coefficients.

        Args:
            c_original: Original objective coefficients for all variables (including slacks)

        Returns:
            Objective value
        """
        solution = self.get_basic_solution()
        obj_value = 0.0

        for i, var_name in enumerate(self.variable_names):
            if i < len(c_original):
                obj_value += c_original[i] * solution[var_name]

        return obj_value

    def is_optimal(self) -> bool:
        """
        Check if current tableau is optimal.
        For max: all reduced costs >= 0
        For min: all reduced costs <= 0
        """
        reduced_costs = self.tableau[-1, :-1]  # exclude RHS

        if self.objective_type == "max":
            return np.all(reduced_costs >= -1e-10)  # small tolerance for floating point
        else:  # min
            return np.all(reduced_costs <= 1e-10)

    def get_entering_variable_candidates(self) -> List[str]:
        """
        Get list of variables that can enter the basis to improve objective.
        For max: variables with negative reduced costs
        For min: variables with positive reduced costs
        """
        candidates = []
        reduced_costs = self.tableau[-1, :-1]

        for i, var_name in enumerate(self.variable_names):
            if self.objective_type == "max":
                if reduced_costs[i] < -1e-10:
                    candidates.append(var_name)
            else:  # min
                if reduced_costs[i] > 1e-10:
                    candidates.append(var_name)

        return candidates

    def get_leaving_variable_candidates(self, entering_col: int) -> List[Tuple[int, str, float]]:
        """
        Get list of variables that can leave the basis for given entering variable.
        Uses minimum ratio test.

        Args:
            entering_col: column index of entering variable

        Returns:
            List of tuples (row_index, variable_name, ratio)
        """
        candidates = []

        for i in range(self.n_constraints):
            pivot_element = self.tableau[i, entering_col]
            rhs = self.tableau[i, -1]

            # Only consider positive pivot elements (minimum ratio test)
            if pivot_element > 1e-10:
                ratio = rhs / pivot_element
                if ratio >= -1e-10:  # allow small negative due to floating point
                    candidates.append((i, self.basis_variables[i], max(0, ratio)))

        return sorted(candidates, key=lambda x: x[2])

    def is_unbounded(self, entering_col: int) -> bool:
        """
        Check if problem is unbounded for given entering variable.
        Unbounded if all coefficients in entering column are <= 0.
        """
        column = self.tableau[:-1, entering_col]  # exclude objective row
        return np.all(column <= 1e-10)

    def pivot(self, pivot_row: int, pivot_col: int) -> 'SimplexTableau':
        """
        Perform pivot operation and return new tableau.

        Args:
            pivot_row: row index for pivot (0 to n_constraints-1)
            pivot_col: column index for pivot (0 to n_variables-1)

        Returns:
            New SimplexTableau after pivot operation
        """
        new_tableau = self.tableau.copy()
        pivot_element = new_tableau[pivot_row, pivot_col]

        if abs(pivot_element) < 1e-10:
            raise ValueError(f"Cannot pivot on near-zero element: {pivot_element}")

        # Step 1: Divide pivot row by pivot element
        new_tableau[pivot_row, :] = new_tableau[pivot_row, :] / pivot_element

        # Step 2: Eliminate pivot column in all other rows (including objective)
        for i in range(len(new_tableau)):
            if i != pivot_row:
                multiplier = new_tableau[i, pivot_col]
                new_tableau[i, :] = new_tableau[i, :] - multiplier * new_tableau[pivot_row, :]

        # Step 3: Update basis
        new_basis = self.basis_variables.copy()
        entering_var = self.variable_names[pivot_col]
        new_basis[pivot_row] = entering_var

        return SimplexTableau(
            tableau=new_tableau,
            variable_names=self.variable_names,
            basis_variables=new_basis,
            objective_type=self.objective_type
        )

    def get_basic_solution(self) -> Dict[str, float]:
        """
        Get current basic feasible solution.
        Non-basic variables are 0, basic variables from RHS.
        """
        solution = {var: 0.0 for var in self.variable_names}

        for i, var_name in enumerate(self.basis_variables):
            solution[var_name] = self.tableau[i, -1]

        return solution

    def is_degenerate(self) -> bool:
        """
        Check if current solution is degenerate.
        Degenerate if any basic variable has value 0.
        """
        for i in range(self.n_constraints):
            if abs(self.tableau[i, -1]) < 1e-10:
                return True
        return False


def solve_simplex_automatic(
    initial_tableau: SimplexTableau,
    max_iterations: int = 100
) -> List[SimplexTableau]:
    """
    Automatically solve simplex problem and return all intermediate tableaus.

    Args:
        initial_tableau: Starting tableau
        max_iterations: Maximum number of iterations to prevent infinite loops

    Returns:
        List of tableaus (including initial), one per iteration
    """
    history = [initial_tableau]
    current = initial_tableau

    for iteration in range(max_iterations):
        # Check if optimal
        if current.is_optimal():
            break

        # Get entering variable (most negative reduced cost for max)
        candidates = current.get_entering_variable_candidates()
        if not candidates:
            break  # Optimal or no improving variables

        # Choose variable with most negative reduced cost (steepest descent)
        entering_var = candidates[0]
        entering_col = current.variable_names.index(entering_var)

        # Get most negative for better improvement
        best_rc = current.get_reduced_costs()[entering_var]
        for var in candidates:
            rc = current.get_reduced_costs()[var]
            if current.objective_type == "max":
                if rc < best_rc:
                    best_rc = rc
                    entering_var = var
                    entering_col = current.variable_names.index(var)
            else:  # min
                if rc > best_rc:
                    best_rc = rc
                    entering_var = var
                    entering_col = current.variable_names.index(var)

        # Check unboundedness
        if current.is_unbounded(entering_col):
            break  # Unbounded

        # Get leaving variable
        leaving_candidates = current.get_leaving_variable_candidates(entering_col)
        if not leaving_candidates:
            break  # No valid leaving variable

        # Choose minimum ratio
        leaving_row = leaving_candidates[0][0]

        # Perform pivot
        try:
            current = current.pivot(leaving_row, entering_col)
            history.append(current)
        except Exception:
            break  # Pivot failed

    return history


def create_standard_tableau(
    A: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
    objective_type: str = "max"
) -> SimplexTableau:
    """
    Create a standard form simplex tableau with slack variables.
    Assumes all constraints are <= for max, >= for min.

    Args:
        A: constraint matrix (m x n)
        b: RHS vector (m)
        c: objective coefficients (n)
        objective_type: "max" or "min"

    Returns:
        SimplexTableau in standard form
    """
    m, n = A.shape

    # Add slack variables
    slack_matrix = np.eye(m)
    A_augmented = np.hstack([A, slack_matrix])

    # Create tableau
    tableau = np.zeros((m + 1, n + m + 1))

    # Constraint rows
    tableau[:m, :n+m] = A_augmented
    tableau[:m, -1] = b

    # Objective row
    if objective_type == "max":
        tableau[-1, :n] = -c  # negative for maximization
    else:
        tableau[-1, :n] = c

    # Variable names
    var_names = [f'x{i+1}' for i in range(n)] + [f's{i+1}' for i in range(m)]

    # Initial basis is slack variables
    basis_vars = [f's{i+1}' for i in range(m)]

    return SimplexTableau(tableau, var_names, basis_vars, objective_type)


def create_tableau_from_parsed(
    A: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
    var_names: List[str],
    basis_vars: List[str],
    objective_type: str = "max",
    objective_constant: float = 0.0
) -> SimplexTableau:
    """
    Create a simplex tableau from already-parsed LP problem.
    Assumes A already includes slack variables and handles Big-M method.

    Args:
        A: constraint matrix with slack variables (m x n)
        b: RHS vector (m)
        c: objective coefficients for all variables (n) - includes Big-M penalties
        var_names: names of all variables
        basis_vars: names of initial basis variables
        objective_type: "max" or "min"
        objective_constant: constant term in objective function

    Returns:
        SimplexTableau ready to solve
    """
    m, n = A.shape

    # Create tableau
    tableau = np.zeros((m + 1, n + 1))

    # Constraint rows
    tableau[:m, :n] = A
    tableau[:m, -1] = b

    # Objective row (initially just -c for max, c for min)
    if objective_type == "max":
        tableau[-1, :n] = -c  # negative for maximization
    else:
        tableau[-1, :n] = c

    # Set objective constant in RHS
    tableau[-1, -1] = objective_constant

    # Big-M Method: If artificial variables are in basis, adjust objective row
    # to eliminate them from the objective function
    artificial_vars = [v for v in basis_vars if v.startswith('a_')]

    if artificial_vars:
        # For each artificial variable in basis, subtract M times its row from objective
        for art_var in artificial_vars:
            if art_var in var_names:
                var_idx = var_names.index(art_var)
                basis_idx = basis_vars.index(art_var)

                # Get the coefficient of this artificial variable in objective
                M_coef = tableau[-1, var_idx]

                # Subtract M_coef times the constraint row from objective row
                # This makes the artificial variable have coefficient 0 in objective
                tableau[-1, :] = tableau[-1, :] - M_coef * tableau[basis_idx, :]

    return SimplexTableau(tableau, var_names, basis_vars, objective_type)


def solve_simplex_automatic(
    initial_tableau: SimplexTableau,
    max_iterations: int = 100
) -> List[SimplexTableau]:
    """
    Automatically solve simplex problem and return all intermediate tableaus.

    Args:
        initial_tableau: Starting tableau
        max_iterations: Maximum number of iterations to prevent infinite loops

    Returns:
        List of tableaus (including initial), one per iteration
    """
    history = [initial_tableau]
    current = initial_tableau

    for iteration in range(max_iterations):
        # Check if optimal
        if current.is_optimal():
            break

        # Get entering variable (most negative reduced cost for max)
        candidates = current.get_entering_variable_candidates()
        if not candidates:
            break  # Optimal or no improving variables

        # Choose variable with most negative reduced cost (steepest descent)
        entering_var = candidates[0]
        entering_col = current.variable_names.index(entering_var)

        # Get most negative for better improvement
        best_rc = current.get_reduced_costs()[entering_var]
        for var in candidates:
            rc = current.get_reduced_costs()[var]
            if current.objective_type == "max":
                if rc < best_rc:
                    best_rc = rc
                    entering_var = var
                    entering_col = current.variable_names.index(var)
            else:  # min
                if rc > best_rc:
                    best_rc = rc
                    entering_var = var
                    entering_col = current.variable_names.index(var)

        # Check unboundedness
        if current.is_unbounded(entering_col):
            break  # Unbounded

        # Get leaving variable
        leaving_candidates = current.get_leaving_variable_candidates(entering_col)
        if not leaving_candidates:
            break  # No valid leaving variable

        # Choose minimum ratio
        leaving_row = leaving_candidates[0][0]

        # Perform pivot
        try:
            current = current.pivot(leaving_row, entering_col)
            history.append(current)
        except Exception:
            break  # Pivot failed

    return history
