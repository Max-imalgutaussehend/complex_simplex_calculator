# Interactive Simplex Tableau Calculator

A Python/Streamlit application for interactive experimentation with the Simplex algorithm. Perfect for students and researchers studying linear programming!

## Features

✨ **Arbitrary Tableau Manipulation**
- Define custom simplex tableaus with any number of variables and constraints
- Start from initial tableaus or any intermediate/final tableau
- Edit variable names (x1, x2, s1, s2, etc.)

🎯 **Interactive Pivot Operations**
- Manually select entering and leaving variables
- Automatic pivot computation with numerical stability
- Step-by-step history navigation

📊 **Comprehensive Analysis**
- Real-time reduced cost computation
- Optimality detection
- Unboundedness detection
- Degeneracy warnings
- Current basis tracking

🔧 **Flexible Optimization**
- Optimize ANY variable (not just decision variables!)
- Maximize or minimize slack variables
- Support for both maximization and minimization problems

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
streamlit run app.py
```

## Quick Start

### Mode 1: Custom Tableau

1. Select "Create New Tableau" in the sidebar
2. Set number of variables and constraints
3. Enter variable names (e.g., x1, x2, s1, s2)
4. Fill in the tableau values
5. Select initial basis variables
6. Click "Create Tableau"

### Mode 2: Standard Form (Auto-slack)

1. Select "Standard Form (Auto-slack)" in the sidebar
2. Enter number of decision variables and constraints
3. Fill in constraint matrix A, RHS vector b, and objective coefficients c
4. Click "Create Standard Form Tableau"
5. Slack variables are added automatically!

## Example: Maximization Problem

Maximize z = 3x₁ + 2x₂

Subject to:
- 2x₁ + x₂ ≤ 18
- 2x₁ + 3x₂ ≤ 42
- 3x₁ + x₂ ≤ 24
- x₁, x₂ ≥ 0

**Using Standard Form Mode:**
1. Set decision variables = 2, constraints = 3
2. Enter A matrix:
   ```
   2  1
   2  3
   3  1
   ```
3. Enter b vector: [18, 42, 24]
4. Enter c vector: [3, 2]

The app will create the initial tableau with slack variables s1, s2, s3.

## Project Structure

```
complex_simplex_calculator/
├── app.py              # Streamlit UI
├── simplex.py          # Core Simplex algorithm
├── requirements.txt    # Dependencies
└── README.md          # Documentation
```

## Key Classes

### `SimplexTableau` (simplex.py)

Main class for tableau representation and manipulation:

- `pivot(row, col)` - Perform pivot operation
- `get_reduced_costs()` - Compute reduced costs
- `is_optimal()` - Check optimality
- `is_unbounded(col)` - Check unboundedness
- `get_basic_solution()` - Extract current solution

## Tips

- **Red metrics** indicate variables that can improve the objective
- **Green metrics** indicate non-improving variables
- Use history navigation to review previous steps
- The minimum ratio test suggests the best leaving variable
- Try optimizing slack variables to explore different bases!

## Technical Details

- Built with Python, NumPy, Pandas, and Streamlit
- Numerical stability via floating-point tolerance (1e-10)
- Clean separation between algorithm logic and UI
- ~400 lines of well-commented code

## License

MIT

## Contributing

Contributions welcome! Feel free to open issues or submit pull requests.
