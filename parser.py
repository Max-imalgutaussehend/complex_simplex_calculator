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

    def parse_expression(self, expr: str) -> Tuple[Dict[str, float], float]:
        """
        Parse a linear expression like "3*x_1 + 4*x_2 - 2*y_1 + 5" into coefficients and constant.

        Returns:
            Tuple of (coefficients dict, constant term)
        """
        coefficients = {}
        constant = 0.0

        # Remove all whitespace
        expr = expr.replace(" ", "")

        # Handle leading signs
        if not expr.startswith(('+', '-')):
            expr = '+' + expr

        # Pattern to match terms like: +3*x_1, -2*x_2, +x_1, -y_1
        # Also matches: +3x_1, -2x_2 (without *)
        pattern = r'([+-]?)(\d*\.?\d*)\*?([a-zA-Z_]\w*)?'

        matches = re.findall(pattern, expr)

        for sign, coef, var in matches:
            if not sign and not coef and not var:
                continue

            # Determine sign
            sign_val = -1 if sign == '-' else 1

            # Determine coefficient
            if coef == '':
                if var:  # Variable without coefficient (like +x_1)
                    coef_val = 1.0
                else:  # Just a sign without number or variable
                    continue
            else:
                coef_val = float(coef)

            if var:
                # Variable term
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
            else:
                # Constant term (number without variable)
                if coef:
                    constant += sign_val * coef_val

        return coefficients, constant

    def parse_constraint(self, constraint: str) -> Tuple[Dict[str, float], str, float]:
        """
        Parse a constraint like "2*x_1 + 3*x_2 <= 4" or "x_1 + x_2 + 5 >= 2".

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

        # Parse left side (variable expression with possible constant)
        left_coeffs, left_constant = self.parse_expression(left.strip())

        # Parse right side (should be a number, but might have variables)
        right = right.strip()

        # Try to parse as number first
        try:
            rhs = float(right)
            rhs_constant = 0.0
            rhs_coeffs = {}
        except ValueError:
            # Right side has variables - move them to left side with negated coefficients
            rhs_coeffs, rhs_constant = self.parse_expression(right)
            rhs = 0.0

            # Move rhs variables to left side
            for var, coef in rhs_coeffs.items():
                if var in left_coeffs:
                    left_coeffs[var] -= coef
                else:
                    left_coeffs[var] = -coef

        # Adjust RHS by moving constants
        # Left side: ax + by + c1 OP rhs + c2
        # Becomes: ax + by OP rhs + c2 - c1
        final_rhs = rhs + rhs_constant - left_constant

        return left_coeffs, operator, final_rhs

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
        objective_type: str = "max",
        endtableau_mode: bool = False
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str], List[str], float]:
        """
        Convert parsed LP to standard form matrices with Big-M method for >= constraints.

        Returns:
            (A, b, c, variable_names, basis_variables, objective_constant)
        """
        # Parse objective (now returns tuple)
        obj_coeffs, obj_constant = self.parse_expression(objective)

        # Parse constraints
        constraints = self.parse_constraints(constraints_str)

        # Get all variables in order
        all_vars = self.get_all_variables()
        n_vars = len(all_vars)
        n_constraints = len(constraints)

        # Build constraint matrix A and RHS vector b
        A = np.zeros((n_constraints, n_vars))
        b = np.zeros(n_constraints)

        # Track which slack/artificial variables we need to add
        # Find the next available slack/artificial counter based on existing variables
        existing_slack_nums = [int(v.split('_')[1]) for v in all_vars if v.startswith('s_') and '_' in v and v.split('_')[1].isdigit()]
        slack_counter = max(existing_slack_nums) + 1 if existing_slack_nums else 1

        existing_artificial_nums = [int(v.split('_')[1]) for v in all_vars if v.startswith('a_') and '_' in v and v.split('_')[1].isdigit()]
        artificial_counter = max(existing_artificial_nums) + 1 if existing_artificial_nums else 1

        added_slacks = []
        added_artificials = []  # For >= and = constraints

        # Big M value
        BIG_M = 1e6

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

            # Check if constraint already has a slack variable (user provided)
            # Look for s_X or y_X variables in this constraint
            has_slack = any(v.startswith(('s_', 'y_')) for v in coeffs.keys())

            # Determine if we need to add slack/artificial variables
            if operator == '<=':
                if not has_slack:
                    # Add slack variable (basis variable)
                    slack_name = f's_{slack_counter}'
                    added_slacks.append((i, slack_name, 1.0, False))  # Not artificial
                    slack_counter += 1
                # else: user already provided slack variable, don't add another
            elif operator == '>=':
                if not has_slack:
                    # Subtract surplus variable, add artificial variable
                    slack_name = f's_{slack_counter}'
                    artificial_name = f'a_{artificial_counter}'
                    added_slacks.append((i, slack_name, -1.0, False))  # Surplus
                    added_artificials.append((i, artificial_name, 1.0))  # Artificial (basis)
                    slack_counter += 1
                    artificial_counter += 1
                else:
                    # User provided slack, but we still need artificial for >= constraint
                    artificial_name = f'a_{artificial_counter}'
                    added_artificials.append((i, artificial_name, 1.0))  # Artificial (basis)
                    artificial_counter += 1
            elif operator == '=':
                # In endtableau mode, '=' constraints don't need artificial variables
                # The variables on the left side are the basis variables
                if not endtableau_mode:
                    # Add artificial variable only
                    artificial_name = f'a_{artificial_counter}'
                    added_artificials.append((i, artificial_name, 1.0))  # Artificial (basis)
                    artificial_counter += 1
                # else: endtableau mode - no artificial needed

        # Add slack variables to matrix
        if added_slacks:
            slack_matrix = np.zeros((n_constraints, len(added_slacks)))
            for idx, (row, slack_name, coef, _) in enumerate(added_slacks):
                slack_matrix[row, idx] = coef

            A = np.hstack([A, slack_matrix])
            all_vars.extend([slack_name for _, slack_name, _, _ in added_slacks])

        # Add artificial variables to matrix
        if added_artificials:
            artificial_matrix = np.zeros((n_constraints, len(added_artificials)))
            for idx, (row, artificial_name, coef) in enumerate(added_artificials):
                artificial_matrix[row, idx] = coef

            A = np.hstack([A, artificial_matrix])
            all_vars.extend([artificial_name for _, artificial_name, _ in added_artificials])

        # Build objective coefficient vector c with Big-M penalty
        c = np.zeros(len(all_vars))
        for i, var in enumerate(all_vars):
            if var in obj_coeffs:
                c[i] = obj_coeffs[var]
            elif var.startswith('a_'):
                # Artificial variables get Big-M penalty
                if objective_type.lower() == "max":
                    c[i] = -BIG_M  # Very negative for maximization
                else:
                    c[i] = BIG_M   # Very positive for minimization

        # Initial basis: slack variables (for <=) and artificial variables (for >= and =)
        basis_vars = []

        # For each constraint, determine which variable should be in basis
        for i, (coeffs, operator, rhs) in enumerate(constraints):
            # Check if constraint already has a slack variable (user provided)
            user_slack_vars = [v for v in coeffs.keys() if v.startswith(('s_', 'y_'))]

            if operator == '<=':
                # For <= constraints, use slack variable as basis
                if user_slack_vars:
                    # User provided slack - use it as basis
                    basis_vars.append(user_slack_vars[0])
                else:
                    # We added a slack - find it
                    for _, slack_name, coef, _ in added_slacks:
                        if coef > 0:  # Positive coefficient (not surplus)
                            if slack_name not in basis_vars:
                                basis_vars.append(slack_name)
                                break
            elif operator == '>=':
                # For >= constraints, use artificial variable as basis
                for _, artificial_name, _ in added_artificials:
                    if artificial_name not in basis_vars:
                        basis_vars.append(artificial_name)
                        break
            elif operator == '=':
                if endtableau_mode:
                    # For endtableau mode, the variable with coefficient 1 on the left is the basis var
                    # Find variable with coefficient close to 1
                    for var, coef in coeffs.items():
                        if abs(coef - 1.0) < 0.01 and var.startswith('x_'):
                            basis_vars.append(var)
                            break
                    # If no x_i found, try any variable
                    if len(basis_vars) <= i:
                        for var in coeffs.keys():
                            if var not in basis_vars:
                                basis_vars.append(var)
                                break
                else:
                    # For = constraints, use artificial variable as basis
                    for _, artificial_name, _ in added_artificials:
                        if artificial_name not in basis_vars:
                            basis_vars.append(artificial_name)
                            break

        # If we still don't have enough basis variables, add more
        if len(basis_vars) < n_constraints:
            # Try to add surplus variables or any slack not yet in basis
            for _, slack_name, coef, _ in added_slacks:
                if slack_name not in basis_vars:
                    basis_vars.append(slack_name)
                    if len(basis_vars) >= n_constraints:
                        break

            # If still not enough, add any slack variable from user input
            if len(basis_vars) < n_constraints:
                for var in all_vars:
                    if var.startswith(('s_', 'y_')) and var not in basis_vars:
                        basis_vars.append(var)
                        if len(basis_vars) >= n_constraints:
                            break

        return A, b, c, all_vars, basis_vars, obj_constant


def parse_lp_problem(
    objective: str,
    constraints: str,
    objective_type: str = "max",
    endtableau_mode: bool = False
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str], List[str], float]:
    """
    Convenience function to parse LP problem.

    Args:
        objective: Objective function like "3*x_1 + 4*x_2"
        constraints: Comma-separated constraints like "2*x_1 + 3*x_2 <= 4, x_1 >= 0"
        objective_type: "max" or "min"
        endtableau_mode: If True, treat '=' constraints without adding artificial variables
                         (for endtableaus where decision variables are in basis)

    Returns:
        (A, b, c, variable_names, initial_basis, objective_constant)
    """
    parser = LPParser()
    A, b, c, var_names, basis_vars, obj_constant = parser.to_standard_form(
        objective, constraints, objective_type, endtableau_mode=endtableau_mode
    )
    return A, b, c, var_names, basis_vars, obj_constant
