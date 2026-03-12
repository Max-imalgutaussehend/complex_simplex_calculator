"""
Expression parser for linear programming constraints and objectives.
Supports flexible input like: 3*x_1 + 4*x_2, 2*x_1 + 3*x_2 <= 4
"""

import re
import numpy as np
from typing import Dict, List, Tuple, Set


class LPParser:
    """Parser for linear programming expressions."""

    def __init__(self):
        self.variables: Set[str] = set()
        self.decision_vars: Set[str] = set()
        self.slack_vars: Set[str] = set()

    def parse_expression(self, expr: str) -> Dict[str, float]:
        """
        Parse a linear expression like "3*x_1 + 4*x_2 - 2*y_1" into coefficients.

        Returns:
            Dictionary mapping variable names to coefficients
        """
        coefficients = {}

        # Remove all whitespace
        expr = expr.replace(" ", "")

        # Handle leading signs
        if not expr.startswith(('+', '-')):
            expr = '+' + expr

        # Pattern to match terms like: +3*x_1, -2*x_2, +x_1, -y_1
        # Also matches: +3x_1, -2x_2 (without *)
        pattern = r'([+-]?)(\d*\.?\d*)\*?([a-zA-Z_]\w*)'

        matches = re.findall(pattern, expr)

        for sign, coef, var in matches:
            if not var:
                continue

            # Determine sign
            sign_val = -1 if sign == '-' else 1

            # Determine coefficient
            if coef == '':
                coef_val = 1.0
            else:
                coef_val = float(coef)

            final_coef = sign_val * coef_val

            # Add to coefficients
            if var in coefficients:
                coefficients[var] += final_coef
            else:
                coefficients[var] = final_coef

            # Track variable
            self.variables.add(var)

            # Classify variable (x_ prefix = decision, y_ or s_ = slack)
            if var.startswith('x_') or var.startswith('x'):
                self.decision_vars.add(var)
            elif var.startswith('y_') or var.startswith('s_') or var.startswith('y') or var.startswith('s'):
                self.slack_vars.add(var)
            else:
                self.decision_vars.add(var)  # Default to decision variable

        return coefficients

    def parse_constraint(self, constraint: str) -> Tuple[Dict[str, float], str, float]:
        """
        Parse a constraint like "2*x_1 + 3*x_2 <= 4" or "x_1 + x_2 >= 2".

        Returns:
            (coefficients_dict, operator, rhs_value)
        """
        # Find operator
        if '<=' in constraint:
            operator = '<='
            left, right = constraint.split('<=')
        elif '>=' in constraint:
            operator = '>='
            left, right = constraint.split('>=')
        elif '=' in constraint and '!=' not in constraint:
            operator = '='
            left, right = constraint.split('=')
        else:
            raise ValueError(f"No valid operator found in constraint: {constraint}")

        # Parse left side (variable expression)
        left_coeffs = self.parse_expression(left.strip())

        # Parse right side (should be a number, but might have variables)
        right = right.strip()

        # Try to parse as number first
        try:
            rhs = float(right)
            rhs_coeffs = {}
        except ValueError:
            # Right side has variables - move them to left side with negated coefficients
            rhs_coeffs = self.parse_expression(right)
            rhs = 0.0

            # Move rhs variables to left side
            for var, coef in rhs_coeffs.items():
                if var in left_coeffs:
                    left_coeffs[var] -= coef
                else:
                    left_coeffs[var] = -coef

        return left_coeffs, operator, rhs

    def parse_constraints(self, constraints_str: str) -> List[Tuple[Dict[str, float], str, float]]:
        """
        Parse comma-separated constraints.

        Example: "2*x_1 + 3*x_2 <= 4, x_1 + x_2 >= 2"

        Returns:
            List of (coefficients, operator, rhs) tuples
        """
        constraints = []

        # Split by comma
        constraint_list = constraints_str.split(',')

        for constraint_str in constraint_list:
            constraint_str = constraint_str.strip()
            if not constraint_str:
                continue

            constraint = self.parse_constraint(constraint_str)
            constraints.append(constraint)

        return constraints

    def get_all_variables(self, sort: bool = True) -> List[str]:
        """
        Get all variables (decision + slack) in consistent order.

        Args:
            sort: Whether to sort variables naturally
        """
        all_vars = list(self.variables)

        if sort:
            # Natural sort: x_1, x_2, ..., x_10, ..., y_1, y_2, ...
            def natural_key(var):
                # Extract prefix and number
                match = re.match(r'([a-zA-Z_]+)(\d+)', var)
                if match:
                    prefix, num = match.groups()
                    return (0 if prefix.startswith('x') else 1, prefix, int(num))
                return (2, var, 0)

            all_vars.sort(key=natural_key)

        return all_vars

    def to_standard_form(
        self,
        objective: str,
        constraints_str: str,
        objective_type: str = "max"
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str], List[str]]:
        """
        Convert parsed LP to standard form matrices.

        Returns:
            (A, b, c, variable_names, basis_variables)
        """
        # Parse objective
        obj_coeffs = self.parse_expression(objective)

        # Parse constraints
        constraints = self.parse_constraints(constraints_str)

        # Get all variables in order
        all_vars = self.get_all_variables()
        n_vars = len(all_vars)
        n_constraints = len(constraints)

        # Build constraint matrix A and RHS vector b
        A = np.zeros((n_constraints, n_vars))
        b = np.zeros(n_constraints)

        # Track which slack variables we need to add
        slack_counter = 1
        added_slacks = []

        for i, (coeffs, operator, rhs) in enumerate(constraints):
            # Fill in coefficients for existing variables
            for j, var in enumerate(all_vars):
                if var in coeffs:
                    A[i, j] = coeffs[var]

            # Handle RHS (might be negative)
            if rhs < 0:
                # Multiply constraint by -1 to make RHS positive
                A[i, :] *= -1
                rhs *= -1
                # Flip operator
                if operator == '<=':
                    operator = '>='
                elif operator == '>=':
                    operator = '<='

            b[i] = rhs

            # Determine if we need to add a slack variable
            if operator == '<=':
                # Add slack variable
                slack_name = f's_{slack_counter}'
                added_slacks.append((i, slack_name, 1.0))  # +1 coefficient
                slack_counter += 1
            elif operator == '>=':
                # Subtract slack variable (or add surplus)
                slack_name = f's_{slack_counter}'
                added_slacks.append((i, slack_name, -1.0))  # -1 coefficient
                slack_counter += 1
            # operator == '=' needs no slack

        # Add slack variables to matrix
        if added_slacks:
            slack_matrix = np.zeros((n_constraints, len(added_slacks)))
            for idx, (row, slack_name, coef) in enumerate(added_slacks):
                slack_matrix[row, idx] = coef

            A = np.hstack([A, slack_matrix])
            all_vars.extend([slack_name for _, slack_name, _ in added_slacks])

        # Build objective coefficient vector c
        c = np.zeros(len(all_vars))
        for i, var in enumerate(all_vars):
            if var in obj_coeffs:
                c[i] = obj_coeffs[var]

        # For minimization, negate objective
        if objective_type.lower() == "min":
            c = -c

        # Initial basis is the slack variables we added
        basis_vars = [slack_name for _, slack_name, _ in added_slacks]

        # If we don't have enough basis variables, we need artificial variables
        # (This is a more advanced case - for now, assume we have enough slacks)
        if len(basis_vars) < n_constraints:
            # Add artificial variables (simplified - would need two-phase simplex)
            for i in range(len(basis_vars), n_constraints):
                artificial_name = f'a_{i+1}'
                all_vars.append(artificial_name)
                basis_vars.append(artificial_name)

                # Add column to A
                col = np.zeros((n_constraints, 1))
                col[i, 0] = 1.0
                A = np.hstack([A, col])

                # Add to objective (big M method - simplified)
                c = np.append(c, 0)

        return A, b, c, all_vars, basis_vars


def parse_lp_problem(
    objective: str,
    constraints: str,
    objective_type: str = "max"
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str], List[str]]:
    """
    Convenience function to parse LP problem.

    Args:
        objective: Objective function like "3*x_1 + 4*x_2"
        constraints: Comma-separated constraints like "2*x_1 + 3*x_2 <= 4, x_1 >= 0"
        objective_type: "max" or "min"

    Returns:
        (A, b, c, variable_names, initial_basis)
    """
    parser = LPParser()
    return parser.to_standard_form(objective, constraints, objective_type)
