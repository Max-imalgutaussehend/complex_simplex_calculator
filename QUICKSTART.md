# Quick Start Guide

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Running the Application

2. **Start the app:**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## First Example - Expression Input

### Problem
Maximize: z = 3x₁ + 4x₂
Subject to:
- 2x₁ + 3x₂ ≤ 18
- 2x₁ + x₂ ≤ 12

### Steps

1. **Select Mode:** "Expression Input (Flexible)"

2. **Enter Objective:**
```
3*x_1 + 4*x_2
```

3. **Enter Constraints:**
```
2*x_1 + 3*x_2 <= 18,
2*x_1 + x_2 <= 12
```

4. **Click:** "Create Tableau from Expressions"

5. **See Initial Tableau:**
```
     x_1  x_2  s_1  s_2   RHS
s_1  2.0  3.0  1.0  0.0  18.0
s_2  2.0  1.0  0.0  1.0  12.0
z   -3.0 -4.0  0.0  0.0   0.0
```

6. **Perform Pivots:**
   - Select entering variable: `x_2` (has negative reduced cost -4.0)
   - Select leaving variable: `s_1` (minimum ratio)
   - Click "Perform Pivot"

7. **Repeat** until all reduced costs ≥ 0 (OPTIMAL)

---

## Example with Slack Variables

### Problem
Maximize: x₁ + x₂
Subject to: 2x₁ + 3x₂ + 4y₁ ≤ 10

### Input
**Objective:**
```
x_1 + x_2
```

**Constraints:**
```
2*x_1 + 3*x_2 + 4*y_1 <= 10
```

The app recognizes `y_1` as a slack variable and handles it correctly!

---

## Example with Mixed Constraints

### Problem
Maximize: 3x₁ + 2x₂
Subject to:
- x₁ + x₂ ≤ 10
- 2x₁ - x₂ ≥ 3

### Input
**Objective:**
```
3*x_1 + 2*x_2
```

**Constraints:**
```
x_1 + x_2 <= 10,
2*x_1 - x_2 >= 3
```

The app automatically:
- Adds slack `s_1` for first constraint (+1 coefficient)
- Adds surplus `s_2` for second constraint (-1 coefficient)

---

## Tips

### Reading Reduced Costs
- **[!]** = Can improve objective (pivot this variable in)
- **[ ]** = Won't improve objective

### Pivot Selection
1. Choose **entering variable** with [!] indicator
2. Choose **leaving variable** with smallest ratio
3. Click "Perform Pivot"

### History
- Use "Previous Step" / "Next Step" to review algorithm
- Use "First Step" to return to initial tableau

### Optimality
When you see **"OPTIMAL"**, stop! Current solution is optimal.

---

## Keyboard-Free Operation

Everything is done with mouse clicks - no keyboard shortcuts needed!

---

## Troubleshooting

### "Problem is UNBOUNDED"
- No valid leaving variable exists
- Problem has no finite optimal solution
- Try different entering variable to explore

### "Degenerate solution"
- One or more basic variables = 0
- Not an error, just a warning
- Continue pivoting normally

### Parsing Error
- Check syntax: use `*` for multiplication
- Separate constraints with commas
- Use `<=`, `>=`, or `=` operators
- Variable names: letters, numbers, underscores

---

## Next Steps

1. Try the example problems above
2. Read the **User Manual** tab for detailed explanations
3. Experiment with optimizing slack variables (Final Tableau mode)
4. Check TEST_REPORT.md for more examples

---

**Happy Simplex Calculating!**
