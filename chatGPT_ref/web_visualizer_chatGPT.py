import dash
from dash import html, dcc
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
import graphviz
import parser

# regex = "(a|b)*(bc|ab)(dasf|bfaskd)*"
regex = "(a|b)*"

your_nfa = parser.parse_regex(regex).to_nfa()


SCALE_X = 100
SCALE_Y = 100


def nfa_to_cytoscape_with_dot(nfa):
    """
    Convert NFA to Cytoscape elements using Graphviz 'dot' layout.
    """
    # Build Graphviz dot source
    dot = graphviz.Digraph(format='plain')
    dot.attr(rankdir='LR')
    for state in nfa.states:
        dot.node(str(state))
    for (src, sym), dests in nfa.trans_func.items():
        for dest in dests:
            dot.edge(str(src), str(dest), label=sym)

    # Render to 'plain' format to extract positions
    plain_output = dot.pipe(format='plain').decode('utf-8')
    nodes = []
    edges = []

    # Parse the 'plain' format
    for line in plain_output.splitlines():
        parts = line.split()
        if parts[0] == 'node':
            _, name, x, y, _, _ = parts[:6]
            nodes.append({
                'data': {'id': name, 'label': name},
                'position': {'x': float(x)*SCALE_X, 'y': -float(y)*SCALE_Y},  # scale & invert y
                'classes': 'start' if name == str(nfa.start_state)
                           else 'accept' if name == str(nfa.accept_state) else ''
            })
        elif parts[0] == 'edge':
            _, src, dst, npts, *rest = parts
            # Use the label from nfa.trans_func if available
            label = ''
            for (s, sym), dests in nfa.trans_func.items():
                if str(s) == src and int(dst) in dests:
                    label = sym
                    break
            edges.append({
                'data': {'source': src, 'target': dst, 'label': label},
                'classes': 'epsilon' if label == '@' else ''
            })

    return nodes, edges

# ------------------------
# Dash app
# ------------------------

app = dash.Dash(__name__)

# Replace `your_nfa` with your NFA object
nodes, edges = nfa_to_cytoscape_with_dot(your_nfa)

stylesheet = [
    {'selector': 'node', 'style': {'label': 'data(label)', 'width': 40, 'height': 40, 'background-color': '#888'}},
    {'selector': '.start', 'style': {'background-color': 'green'}},
    {'selector': '.accept', 'style': {'background-color': 'yellow', 'shape': 'doublecircle'}},
    {'selector': 'edge', 'style': {'label': 'data(label)',
                                   'curve-style': 'bezier',
                                   'target-arrow-shape': 'triangle',
                                   'text-rotation': 'autorotate',
                                   'text-margin-x': 0,             
                                   'text-margin-y': -12,           
                                   'font-size': 16,
                                   'color': '#34495e',
                                   'curve-style': 'bezier'}},
    {'selector': '.epsilon', 'style': {'line-style': 'dashed'}}
]

app.layout = html.Div([
    html.H2("Interactive Thompson NFA Visualizer"),
    html.P(f"Regex: {regex}", style={
    "fontFamily": "Courier New, monospace",
    "fontSize": "20px",
    "fontWeight": "bold",
    "color": "#2c3e50"
    }),
    cyto.Cytoscape(
        id='nfa-graph',
        elements=nodes + edges,
        style={'width': '100%', 'height': '600px'},
        layout={'name': 'preset', 'spacingFactor': 2.0, 'avoidOverlap': True},  # use fixed positions
        stylesheet=stylesheet
    ),
    html.Br(),
    dcc.Input(id='input-string', type='text', placeholder='Enter test string'),
    # html.Button('Test', id='test-btn'),
    html.Div(id='result')
])

# ------------------------
# Callback to test string
# ------------------------
@app.callback(
    Output('result', 'children'),
    # Input('test-btn', 'n_clicks'),
    Input('input-string', 'value')
)
def test_string(test_str):

    if not test_str:
        return ""
    accepted = your_nfa.match(test_str)
    return f"String '{test_str}' accepted? {accepted}"

# ------------------------
if __name__ == '__main__':
    app.run(debug=True)
