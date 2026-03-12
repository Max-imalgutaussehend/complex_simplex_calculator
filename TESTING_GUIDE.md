# Test Instructions - New UI

## Quick Test

1. **Start the app:**
```bash
streamlit run app.py
```

2. **Select Mode:** "Expression Input (Flexible)"

3. **Enter Problem:**
```
Objective: 3*x_1 + 4*x_2

Constraints:
2*x_1 + 3*x_2 <= 18,
2*x_1 + x_2 <= 12
```

4. **Click:** "Create Tableau from Expressions"

## What You'll See

### ✅ Separate Sections

**Constraints:**
- Clean table showing only the constraint rows
- s_1 and s_2 as row labels

**Objective Function (Z):**
- Separate Z-row with gradient coloring
- Reduced costs clearly visible

**Current Solution:**
- Two columns: Basic vs Non-basic variables
- Clear indication of which variables are in basis
- Prominent Z value display

### ✅ Reduced Costs

Displayed below with indicators:
- `[!]` = Can improve (negative for max, positive for min)
- `[ ]` = Cannot improve or is in basis

### ✅ Pivot Controls

1. **Select Entering Variable**
   - Dropdown shows all variables
   - "Improving:" hint shows good candidates

2. **Select Leaving Variable**
   - Dropdown shows candidates with ratios
   - "Minimum ratio:" hint shows best choice

3. **Show Pivot Details** (expandable)
   - Entering variable with reduced cost
   - Leaving variable with current value
   - Pivot element with position
   - **Minimum Ratio Test table** with all candidates
   - Pivot operation steps explanation

4. **Perform Pivot**
   - Click button
   - See success message with Z improvement
   - Tableau updates automatically

### ✅ After Pivot

- **Last Pivot section** (expandable)
  - Shows what entered/left
  - Shows Z value change

- **Updated tableau** with new basis

- **History navigation**
  - Go back to review steps
  - Go forward if you went back

## Test Sequence

### Iteration 1
1. Select **x_2** as entering (reduced cost: -4.0000)
2. Select **s_1** as leaving (ratio: 6.0000)
3. Expand "Show Pivot Details" to see full analysis
4. Click "Perform Pivot"
5. Observe:
   - Z changes from 0.0000 to 24.0000
   - Basis changes to [x_2, s_2]
   - Last Pivot shows: x_2 IN, s_1 OUT

### Iteration 2
1. Select **x_1** as entering (reduced cost: -0.3333)
2. Select **s_2** as leaving (ratio: 4.5000)
3. Click "Perform Pivot"
4. Observe:
   - Z changes from 24.0000 to 25.5000
   - Basis changes to [x_2, x_1]
   - **Status: OPTIMAL** ✓

## Features to Test

### ✓ Expression Input
- Try: `2*x_1 - 3*x_2 + 5*x_3`
- Try: `x_1 + x_2` (simple)
- Try with slack: `x_1 + y_1`

### ✓ Constraints
- `<=` constraints: `x_1 + x_2 <= 10`
- `>=` constraints: `x_1 + x_2 >= 5`
- Mixed: `x_1 <= 10, x_2 >= 3`
- With slacks: `x_1 + y_1 <= 10`

### ✓ UI Elements
- Constraint section formatting
- Z-row gradient coloring
- Solution display (basic/non-basic split)
- Z value prominence
- Pivot details expandable
- Last pivot info expandable
- History navigation

### ✓ Educational Features
- Minimum ratio test table
- Pivot element highlighting (yellow with orange border)
- Step-by-step explanations
- Iteration summaries
- Z value tracking

## Expected Behavior

### ✅ Initial Display
- Constraints section shows only constraint rows
- Z-row shown separately with coloring
- Solution split into basic/non-basic columns
- Z value prominent at bottom
- All reduced costs displayed with indicators

### ✅ During Pivot Selection
- Entering variable dropdown works
- Leaving variable dropdown shows ratios
- "Show Pivot Details" expands correctly
- Minimum ratio test table displays
- Pivot element value shown

### ✅ After Pivot
- Success message with improvement
- Last pivot section appears
- Tableau updates with new basis
- Z value changes
- History grows

### ✅ History Navigation
- "First Step" goes to initial
- "Previous Step" goes back
- "Next Step" goes forward (if available)
- Last pivot info preserved

## Common Issues

### Issue: TypeError
**Fixed!** The highlight_pivot function signature was corrected.

### Issue: No improving variables
This is correct if the tableau is optimal. All reduced costs should be >= 0 (for max) or <= 0 (for min).

### Issue: Unbounded
Some entering variables may have no valid leaving variable. This means the problem is unbounded in that direction. Try a different entering variable.

## Success Criteria

✅ App starts without errors
✅ Tableau displays in separate sections
✅ Solution shows basic/non-basic split
✅ Z value prominently displayed
✅ Pivot details expandable works
✅ Minimum ratio test table shows
✅ Pivot executes successfully
✅ Last pivot info appears
✅ History navigation works
✅ All sections format correctly

---

**Status: READY FOR TESTING**

Run: `streamlit run app.py`
