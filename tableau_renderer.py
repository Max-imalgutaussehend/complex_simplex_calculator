"""
Utilities for rendering tableaus in beautiful mathematical notation.
"""

import streamlit as st
import numpy as np
from simplex import SimplexTableau
from typing import List, Tuple


def tableau_to_latex_system(tableau: SimplexTableau, lang: str = "de") -> str:
    """
    Convert a simplex tableau to a LaTeX system of equations/inequalities.

    Shows the tableau as:
    x_1 = RHS - a*s_1 - b*s_2 - ...  (for basic variables)

    Args:
        tableau: SimplexTableau to render
        lang: Language ("en" or "de")

    Returns:
        LaTeX string
    """
    lines = []

    # Get basis and non-basis variables
    basis_vars = tableau.basis_variables
    all_vars = tableau.variable_names
    nonbasis_vars = [v for v in all_vars if v not in basis_vars]

    # For each constraint row (basic variable)
    for i, basis_var in enumerate(basis_vars):
        # Left side: basis variable
        left = format_var_latex(basis_var)

        # Right side: RHS and non-basis terms
        rhs_value = tableau.tableau[i, -1]
        terms = [f"{rhs_value:.4g}"]

        # Add non-basis variable terms
        for j, var in enumerate(all_vars):
            if var not in basis_vars:
                coef = tableau.tableau[i, j]
                if abs(coef) > 1e-10:  # Not zero
                    if coef > 0:
                        terms.append(f"- {coef:.4g} \\cdot {format_var_latex(var)}")
                    else:
                        terms.append(f"+ {-coef:.4g} \\cdot {format_var_latex(var)}")

        # Build equation
        right = " ".join(terms)
        lines.append(f"  {left} &= {right} \\\\")

    # Objective function
    obj_label = "Z" if lang == "en" else "Z"
    obj_terms = [f"{tableau.tableau[-1, -1]:.4g}"]

    for j, var in enumerate(all_vars):
        if var not in basis_vars:
            coef = -tableau.tableau[-1, j]  # Negate because in tableau it's stored negated
            if abs(coef) > 1e-10:
                if coef > 0:
                    obj_terms.append(f"+ {coef:.4g} \\cdot {format_var_latex(var)}")
                else:
                    obj_terms.append(f"- {-coef:.4g} \\cdot {format_var_latex(var)}")

    obj_line = " ".join(obj_terms)
    lines.append(f"  {obj_label} &= {obj_line}")

    # Build system
    latex = "\\begin{align}\n" + "\n".join(lines) + "\n\\end{align}"

    return latex


def format_var_latex(var: str) -> str:
    """Format variable name for LaTeX."""
    if "_" in var:
        parts = var.split("_")
        if len(parts) == 2 and parts[1].isdigit():
            return f"{parts[0]}_{{{parts[1]}}}"
    return var


def render_tableau_as_system(tableau: SimplexTableau, lang: str = "de", title: str = None):
    """
    Render tableau as a beautiful system of equations in LaTeX.

    Args:
        tableau: SimplexTableau to render
        lang: Language ("en" or "de")
        title: Optional title for the system
    """
    if title:
        st.markdown(f"### {title}")

    try:
        latex_system = tableau_to_latex_system(tableau, lang)
        st.latex(latex_system)
    except Exception as e:
        st.error(f"LaTeX rendering error: {str(e)}")
        # Fallback to dataframe
        st.dataframe(tableau.get_dataframe().style.format("{:.4f}"), width='stretch')


def render_tableau_with_inequalities(tableau: SimplexTableau, lang: str = "de"):
    """
    Render tableau with >= 0 constraints for all variables.

    Shows:
    x_i = RHS - a*s_1 - ... >= 0
    s_j >= 0
    Z = ...

    Args:
        tableau: SimplexTableau to render
        lang: Language ("en" or "de")
    """
    lines = []

    # Get basis and non-basis variables
    basis_vars = tableau.basis_variables
    all_vars = tableau.variable_names
    nonbasis_vars = [v for v in all_vars if v not in basis_vars]

    # For each constraint row (basic variable)
    for i, basis_var in enumerate(basis_vars):
        # Left side: basis variable
        left = format_var_latex(basis_var)

        # Right side: RHS and non-basis terms
        rhs_value = tableau.tableau[i, -1]
        terms = []

        # RHS
        if abs(rhs_value) > 1e-10:
            terms.append(f"{rhs_value:.4g}")

        # Add non-basis variable terms
        for j, var in enumerate(all_vars):
            if var not in basis_vars:
                coef = tableau.tableau[i, j]
                if abs(coef) > 1e-10:  # Not zero
                    if coef > 0:
                        terms.append(f"- {coef:.4g} {format_var_latex(var)}")
                    else:
                        terms.append(f"+ {-coef:.4g} {format_var_latex(var)}")

        # Build equation with >= 0
        if terms:
            right = " ".join(terms)
            lines.append(f"  {left} = {right} &\\geq 0 \\\\")
        else:
            lines.append(f"  {left} = 0 &\\geq 0 \\\\")

    # Non-basis variables >= 0
    for var in nonbasis_vars:
        lines.append(f"  {format_var_latex(var)} &\\geq 0 \\\\")

    # Objective function
    obj_label = "Z"
    obj_terms = []

    # RHS
    obj_rhs = tableau.tableau[-1, -1]
    if abs(obj_rhs) > 1e-10:
        obj_terms.append(f"{obj_rhs:.4g}")

    for j, var in enumerate(all_vars):
        if var not in basis_vars:
            coef = -tableau.tableau[-1, j]  # Negate because stored negated
            if abs(coef) > 1e-10:
                if coef > 0:
                    obj_terms.append(f"+ {coef:.4g} {format_var_latex(var)}")
                else:
                    obj_terms.append(f"- {-coef:.4g} {format_var_latex(var)}")

    if obj_terms:
        obj_line = " ".join(obj_terms)
        lines.append(f"  {obj_label} &= {obj_line}")
    else:
        lines.append(f"  {obj_label} &= {obj_rhs:.4g}")

    # Build system
    latex = "\\begin{align}\n" + "\n".join(lines) + "\n\\end{align}"

    try:
        st.latex(latex)
    except Exception as e:
        st.error(f"LaTeX rendering error: {str(e)}")
