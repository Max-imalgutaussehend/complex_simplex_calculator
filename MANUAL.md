# Interactive Simplex Tableau Calculator - User Manual

## Overview

This application provides an interactive environment for studying and experimenting with the Simplex algorithm. You can manually define tableaus, perform pivot operations step-by-step, and analyze the behavior of the algorithm.

## Getting Started

### Installation

```bash
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app.py
```

The application will open in your web browser at `http://localhost:8501`

---

## Three Operating Modes

The application offers three modes for creating simplex tableaus:

### Mode 1: Create New Tableau (Free Form)

**Use this when:** You want complete control over every element of the tableau.

**Steps:**
1. Select "Create New Tableau" in the sidebar
2. Set the number of variables (including slack/surplus variables)
3. Set the number of constraints
4. Define variable names (comma-separated, e.g., `x1, x2, s1, s2`)
5. Enter values directly into the tableau grid
   - Each row represents a constraint
   - The last row is the objective function (z-row)
   - The last column is the Right-Hand Side (RHS)
6. Select which variables are currently in the basis (one per constraint)
7. Click "Create Tableau"

**Example:** Creating an arbitrary intermediate tableau from a textbook problem.

---

### Mode 2: Standard Form (Initial - slack in basis)

**Use this when:** Starting from the beginning with a standard LP problem.

**Steps:**
1. Select "Standard Form (Initial - slack in basis)"
2. Set number of decision variables (e.g., 2 for x₁, x₂)
3. Set number of constraints
4. Enter the constraint matrix A
   - Each row is one constraint
   - Each column is one decision variable's coefficient
5. Enter the RHS vector b (right-hand side values)
6. Enter objective coefficients c
7. Click "Create Initial Tableau"

The application automatically:
- Adds slack variables (s₁, s₂, ...)
- Creates the initial tableau
- Sets slack variables as the initial basis

**Example:** Solving a maximization problem from scratch.

**Standard Form:**
```
Maximize:   z = c₁x₁ + c₂x₂ + ... + cₙxₙ
Subject to: a₁₁x₁ + a₁₂x₂ + ... + a₁ₙxₙ ≤ b₁
            a₂₁x₁ + a₂₂x₂ + ... + a₂ₙxₙ ≤ b₂
            ...
            xᵢ ≥ 0
```

---

### Mode 3: Final Tableau (Endtableau - xₙ in basis)

**Use this when:** You want to start from an optimal/final tableau where decision variables are in the basis, allowing you to optimize slack variables.

**Purpose:** This mode is useful for:
- Sensitivity analysis
- Understanding shadow prices (dual values)
- Experimenting with what happens if you pivot slack variables back into the basis
- Post-optimality analysis

**Steps:**
1. Select "Final Tableau (Endtableau - xₙ in basis)"
2. Set number of decision variables
3. Set number of constraints
4. Enter basic variable values (the optimal x values)
5. Enter slack variable coefficients (how slacks appear in each constraint)
6. Enter objective coefficients (shadow prices)
7. Enter reduced costs for slack variables
8. Click "Create Final Tableau"

**What this creates:**
- Decision variables x₁, x₂, ... are in the basis (basic variables)
- Slack variables s₁, s₂, ... are non-basic
- You can now pivot to bring slack variables into the basis
- Useful for studying post-optimal behavior

---

## Understanding the Interface

### Sidebar (Configuration Panel)

**Tableau Mode:** Choose one of three modes
**Objective Type:** Maximize or minimize
**Variable Configuration:** Number of variables and constraints
**Reset Tableau:** Clear everything and start over

### Main Area (Left Column) - Tableau Definition

Input area for defining your tableau based on selected mode.

### Status Panel (Right Column)

**Objective Value (z):** Current value of the objective function

**Optimal Status:**
- "OPTIMAL" - Current solution is optimal
- "Not optimal" - Can improve by pivoting

**Degenerate:** Warning if any basic variable equals zero

**Pivot Steps:** Counter of how many pivots performed

**Current Basis:** List of variables currently in the basis with their values

---

## Reading the Tableau Display

The tableau is displayed as a table with:

**Rows:**
- Basis variable names (one per constraint)
- "z" row (objective function)

**Columns:**
- All variable names
- "RHS" (Right-Hand Side) - values of basic variables

**Values:**
- Constraint coefficients
- Objective row coefficients (reduced costs)
- RHS column (solution values)

---

## Reduced Costs

Displayed below the tableau for each variable.

**Interpretation:**

**For Maximization:**
- Negative reduced cost → Variable can improve objective if entered into basis
- Zero reduced cost → Variable is in basis or won't improve objective
- Positive reduced cost → Variable would worsen objective

**For Minimization:**
- Positive reduced cost → Variable can improve objective if entered into basis
- Zero reduced cost → Variable is in basis or won't improve objective
- Negative reduced cost → Variable would worsen objective

**Color coding:**
- Red indicator: Variable can improve objective
- Green indicator: Variable won't improve objective

---

## Performing Pivot Operations

### Step 1: Select Entering Variable (Pivot Column)

Choose which variable should enter the basis.

**Hints:**
- "Improving" message shows which variables have favorable reduced costs
- You can select ANY variable (not just improving ones)
- Useful for experimentation and learning

### Step 2: Select Leaving Variable (Pivot Row)

Choose which variable should leave the basis.

**Minimum Ratio Test:**
The application shows valid candidates with their ratios:
```
ratio = RHS / pivot_column_coefficient (for positive coefficients only)
```

**Hints:**
- Smallest ratio is typically the best choice (prevents infeasibility)
- Application shows the minimum ratio variable
- "UNBOUNDED" warning if no valid leaving variable exists

### Step 3: Perform Pivot

Shows the pivot element (intersection of pivot row and column).

Click "Perform Pivot" to execute the pivot operation.

**What happens:**
1. Pivot row is divided by pivot element
2. All other rows are updated to make pivot column a unit vector
3. Basis is updated (entering replaces leaving)
4. New tableau is displayed

---

## Pivot Operation Mathematics

Given pivot element at row r, column c:

**Step 1:** Divide pivot row by pivot element
```
new_row[r] = old_row[r] / pivot_element
```

**Step 2:** For each other row i:
```
multiplier = old_row[i][c]
new_row[i] = old_row[i] - multiplier × new_row[r]
```

**Result:** Column c becomes a unit vector with 1 at row r.

---

## History Navigation

After performing pivots, use history buttons to review:

- **First Step:** Return to initial tableau
- **Previous Step:** Go back one pivot
- **Next Step:** Go forward one pivot (if available)

Useful for:
- Reviewing the sequence of pivots
- Understanding how the algorithm progresses
- Teaching and demonstration

---

## Current Basic Feasible Solution

Shows values of all variables:
- Blue circle: Basic variable (in basis, value from RHS)
- White circle: Non-basic variable (value = 0)

---

## Optimality Conditions

**Optimal tableau characteristics:**

**For Maximization:**
- All reduced costs ≥ 0
- Current basis provides maximum objective value

**For Minimization:**
- All reduced costs ≤ 0
- Current basis provides minimum objective value

When optimal, no improving pivots are available.

---

## Special Cases

### Unbounded Problem

**Indication:** "Problem is UNBOUNDED for this entering variable"

**Meaning:**
- All coefficients in entering column are ≤ 0
- No valid leaving variable exists
- Objective can be improved without bound
- Problem has no finite optimal solution

### Degenerate Solution

**Indication:** "Degenerate solution" warning

**Meaning:**
- At least one basic variable has value 0
- May lead to cycling (revisiting same basis)
- Multiple optimal bases may exist

### Alternative Optima

**Indication:** Optimal tableau with some non-basic variables having zero reduced cost

**Meaning:**
- Multiple optimal solutions exist
- Can pivot zero-reduced-cost variable without changing objective value

---

## Example Walkthrough

### Example: Simple Maximization Problem

**Problem:**
```
Maximize: z = 3x₁ + 2x₂
Subject to:
    2x₁ + x₂ ≤ 18
    2x₁ + 3x₂ ≤ 42
    3x₁ + x₂ ≤ 24
    x₁, x₂ ≥ 0
```

**Using Mode 2 (Standard Form):**

1. Set decision variables = 2, constraints = 3
2. Enter A matrix:
   ```
   2  1
   2  3
   3  1
   ```
3. Enter b vector: `[18, 42, 24]`
4. Enter c vector: `[3, 2]`
5. Click "Create Initial Tableau"

**Initial Tableau:**
```
      x1    x2    s1   s2   s3   RHS
s1    2     1     1    0    0    18
s2    2     3     0    1    0    42
s3    3     1     0    0    1    24
z    -3    -2     0    0    0     0
```

**Iteration 1:**
- Entering: x₁ (most negative reduced cost: -3)
- Leaving: s₃ (minimum ratio: 24/3 = 8)
- Pivot on element (3,1)

**Iteration 2:**
- Continue pivoting until all reduced costs ≥ 0

**Final Solution:**
- Read optimal values from RHS column for basic variables
- Non-basic variables = 0
- Optimal z from RHS of objective row

---

## Tips for Using the Application

### Learning the Simplex Algorithm
1. Start with Mode 2 (Standard Form)
2. Perform pivots step-by-step manually
3. Follow minimum ratio test
4. Observe how tableau transforms

### Sensitivity Analysis
1. Reach optimal solution in Mode 2
2. Switch to Mode 3 (Final Tableau) with same values
3. Experiment with pivoting slack variables
4. Observe changes in objective value

### Debugging Simplex Code
1. Use Mode 1 (Create New Tableau)
2. Enter intermediate tableau from your algorithm
3. Verify reduced costs match
4. Check if your pivot selection is correct

### Teaching
1. Use History navigation to demonstrate algorithm steps
2. Show students the minimum ratio test in action
3. Demonstrate unbounded and degenerate cases
4. Explore alternative optima

---

## Troubleshooting

### "Cannot pivot on near-zero element"
- Selected pivot element is too small
- Choose a different leaving variable
- Check for numerical errors in input

### "No valid leaving variable"
- Problem may be unbounded for this entering variable
- Try a different entering variable
- Verify problem formulation

### Unexpected optimal solution
- Check objective type (max vs min)
- Verify input data (A, b, c matrices)
- Check signs of coefficients

### Tableau shows odd values
- Verify initial basis selection
- Ensure RHS values are non-negative
- Check that slack variables are in initial basis (Mode 2)

---

## Advanced Features

### Optimizing Slack Variables

Using Mode 3 (Final Tableau):
1. Start with optimal solution (decision variables in basis)
2. Select a slack variable as entering variable
3. Perform pivot to bring slack into basis
4. Observe how solution changes
5. Useful for post-optimality analysis

### Shadow Prices (Dual Values)

In optimal tableau:
- Reduced costs of slack variables = shadow prices
- Indicates marginal value of relaxing constraints
- Shows sensitivity to RHS changes

---

## Mathematical Background

### Standard Form LP

```
Maximize:     z = cᵀx
Subject to:   Ax ≤ b
              x ≥ 0
```

Add slack variables s:
```
Maximize:     z = cᵀx + 0ᵀs
Subject to:   Ax + s = b
              x, s ≥ 0
```

### Tableau Representation

```
[ B⁻¹N  B⁻¹ ] [ xₙ ]   [ B⁻¹b ]
[ cₙᵀ    0  ] [ xB ] = [  z   ]
```

Where:
- B: basis matrix
- N: non-basis matrix
- xB: basic variables
- xₙ: non-basic variables

---

## Keyboard Shortcuts

None currently - all operations via mouse clicks.

---

## Data Export

Not currently supported. Use screenshots or copy tableau values manually.

---

## Further Reading

- **Linear Programming:** Vanderbei, "Linear Programming: Foundations and Extensions"
- **Simplex Algorithm:** Chvátal, "Linear Programming"
- **Sensitivity Analysis:** Winston, "Operations Research: Applications and Algorithms"

---

## Support

For issues or questions:
- Check this manual
- Review the README.md for technical information
- Examine example problems included in manual

---

## Version

Version 1.0 - Initial Release
