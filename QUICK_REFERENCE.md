# Quick Reference Guide

## Starting the Application

```bash
streamlit run app.py
```

## Three Modes Quick Guide

| Mode | Use When | Initial Basis |
|------|----------|---------------|
| Create New Tableau | Complete manual control needed | You select |
| Standard Form (Initial) | Starting from LP problem | Slack variables |
| Final Tableau (Endtableau) | Starting from optimal solution | Decision variables |

## Tableau Structure

```
       x1    x2    s1    s2    RHS
s1   [ a11   a12   1     0  ]  b1    <- Constraint 1
s2   [ a21   a22   0     1  ]  b2    <- Constraint 2
z    [ c1    c2    0     0  ]  z0    <- Objective
```

## Pivot Process

1. **Select Entering Variable** (column)
   - For max: choose variable with most negative reduced cost
   - For min: choose variable with most positive reduced cost
   - [!] indicator shows improving variables

2. **Select Leaving Variable** (row)
   - Compute ratio = RHS / pivot_column_coefficient (for positive coefficients)
   - Choose minimum ratio
   - App shows minimum ratio candidate

3. **Perform Pivot**
   - Click "Perform Pivot" button
   - Tableau updates automatically
   - Basis updates

## Optimality Check

**Maximization:** All reduced costs >= 0
**Minimization:** All reduced costs <= 0

## Notation

- **[B]** = Basic variable (in basis)
- **[ ]** = Non-basic variable (not in basis)
- **[!]** = Improving variable (negative reduced cost for max / positive for min)
- **RHS** = Right-Hand Side (values of basic variables)

## Common Operations

### Navigate History
- **First Step**: Return to initial tableau
- **Previous Step**: Go back one pivot
- **Next Step**: Go forward one pivot

### Reset
Click "Reset Tableau" in sidebar to clear everything

## Tips

1. Always check reduced costs before pivoting
2. Follow minimum ratio test to avoid infeasibility
3. Use history to review algorithm steps
4. [!] indicator highlights variables that can improve objective
5. In final tableau mode, you can optimize slack variables

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "Cannot pivot on near-zero element" | Pivot element too small | Choose different leaving variable |
| "UNBOUNDED" | No valid leaving variable | Problem unbounded for this entering var |
| "Degenerate solution" | Basic variable = 0 | Continue pivoting (may cycle) |

## Keyboard Shortcuts

None - use mouse/trackpad for all operations

## Example: Quick Solve

1. Choose "Standard Form (Initial - slack in basis)"
2. Enter A, b, c matrices
3. Click "Create Initial Tableau"
4. Repeatedly:
   - Choose entering variable with [!] indicator
   - Choose leaving variable (minimum ratio)
   - Click "Perform Pivot"
5. Stop when "OPTIMAL" appears

## File Structure

```
complex_simplex_calculator/
├── app.py              # Main application
├── simplex.py          # Algorithm core
├── MANUAL.md           # Full user manual
├── QUICK_REFERENCE.md  # This file
└── requirements.txt    # Dependencies
```

## Support

For detailed explanations, see MANUAL.md (available in "User Manual" tab)
