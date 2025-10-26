# 🎯 Regular Expression to NFA Visualizer
A web-based interactive tool that parses regular expressions (via Thompson’s Construction) and visualizes their equivalent NFAs (Nondeterministic Finite Automata) step-by-step.

Built with Dash, Cytoscape.js, and Graphviz, this project bridges theory and visualization for formal language enthusiasts and students.

# 🚀 Features:
- Regex Parser — Parses valid regular expressions and handles | (union), * (Kleene star), and concatenation operators.

- Thompson’s Construction — Generates the corresponding NFA with epsilon ($\epsilon$) transitions.

- Interactive Visualization — Displays the NFA graph using Graphviz (dot layout) and Cytoscape.js.

- Animated Tracing — Step through the NFA’s matching process on input strings dynamically.

- Error Handling — Detects invalid regular expressions and shows informative feedback.

# 🧩 How It Works

**1. Enter a Regex**
   
   Supported symbols:
      - `a`, `b`, `c`, ... (literals)
        
      - `|` (union)
        
      - `*` (Kleene star)
        
      - Concatenation (implicit)

**2. Generate NFA**

  The parser builds an Abstract Syntax Tree (AST).

  Thompson’s Construction recursively creates an NFA from the AST.

**3. Visualize**

   Graphviz’s dot layout positions the nodes for optimal viewing.

   Cytoscape.js renders the graph interactively in the browser.

**4. Simulate Matching**

   The input string is processed symbol-by-symbol. Active states are highlighted/animated to show the traversal.

# 🧰 Installation

1. Clone this repository
```
git clone git@github.com:k13nNg/regex-to-nfa-viz.git
cd regex-to-nfa-viz
```

2. Create a virtual environment (recommended)
```
python3 -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Run the app
```
python web_visualizer.py
```

Then open your browser at: `http://127.0.0.1:8050/`
