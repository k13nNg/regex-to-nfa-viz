import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto
import graphviz
import parser
import json

# Your regex and NFA
regex = "(a|b)*"
your_nfa = parser.parse_regex(regex).to_nfa()

SCALE_X = 100
SCALE_Y = 100

def nfa_to_cytoscape_with_dot(nfa):
    """Convert NFA to Cytoscape elements using Graphviz layout."""
    dot = graphviz.Digraph(format='plain')
    dot.attr(rankdir='LR')
    for state in nfa.states:
        dot.node(str(state))
    for (src, sym), dests in nfa.trans_func.items():
        for dest in dests:
            dot.edge(str(src), str(dest), label=sym)

    plain_output = dot.pipe(format='plain').decode('utf-8')
    nodes, edges = [], []

    for line in plain_output.splitlines():
        parts = line.split()
        if parts[0] == 'node':
            _, name, x, y, _, _ = parts[:6]
            nodes.append({
                'data': {'id': name, 'label': name},
                'position': {'x': float(x)*SCALE_X, 'y': -float(y)*SCALE_Y},
                'classes': (
                    'start' if name == str(nfa.start_state)
                    else 'accept' if name == str(nfa.accept_state)
                    else ''
                )
            })
        elif parts[0] == 'edge':
            _, src, dst, *_ = parts
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


def simulate_nfa_steps(nfa, test_str):
    """Yield states at each step for visualization."""
    start = nfa.start_state
    curr_states = nfa.get_epsilon_closure({start})
    steps = [{'char': None, 'states': list(curr_states)}]

    for ch in test_str:
        next_states = set()
        for s in curr_states:
            next_states |= nfa.get_next_state(s, ch)
        curr_states = nfa.get_epsilon_closure(next_states)
        steps.append({'char': ch, 'states': list(curr_states)})
    return steps


# Build graph elements
nodes, edges = nfa_to_cytoscape_with_dot(your_nfa)

stylesheet = [
    {'selector': 'node', 'style': {'label': 'data(label)', 'width': 40, 'height': 40,
                                   'background-color': '#888'}},
    {'selector': '.start', 'style': {'background-color': '#2ecc71'}},
    {'selector': '.accept', 'style': {'background-color': '#f1c40f', 'shape': 'doublecircle'}},
    {'selector': '.active', 'style': {'background-color': '#3498db'}},
    {'selector': 'edge', 'style': {'label': 'data(label)', 'curve-style': 'bezier',
                                   'target-arrow-shape': 'triangle',
                                   'text-rotation': 'autorotate',
                                   'text-margin-y': -10, 'font-size': 16}},
    {'selector': '.epsilon', 'style': {'line-style': 'dashed'}}
]


# Dash app setup
app = dash.Dash(__name__)
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
        layout={'name': 'preset'},
        stylesheet=stylesheet
    ),
    html.Br(),
    dcc.Input(id='input-string', type='text', placeholder='Enter test string'),
    html.Button('Run Animation', id='run-btn'),
    html.Div(id='result'),
    dcc.Interval(id='interval', interval=1000, n_intervals=0, disabled=True),
    dcc.Store(id='simulation-data'),
    dcc.Store(id='step-index', data=0)
])

@app.callback(
    Output('nfa-graph', 'stylesheet'),
    Output('simulation-data', 'data'),
    Output('step-index', 'data'),
    Output('interval', 'disabled'),
    Output('result', 'children'),
    Input('interval', 'n_intervals'),
    Input('run-btn', 'n_clicks'),
    State('input-string', 'value'),
    State('simulation-data', 'data'),
    State('step-index', 'data')
)
def combined_callback(n_intervals, n_clicks, test_str, sim_data, step_idx):
    # Start new simulation
    triggered = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered == 'run-btn' and test_str:
        steps = simulate_nfa_steps(your_nfa, test_str)
        return stylesheet, json.dumps(steps), 0, False, "Running..."

    # Continue animation
    if not sim_data:
        return stylesheet, sim_data, step_idx, True, ""
    steps = json.loads(sim_data)

    if step_idx >= len(steps):
        return stylesheet, sim_data, step_idx, True, "Simulation finished."

    step = steps[step_idx]
    active_states = {s for s in step['states']}

    # highlight active states
    # dynamic_styles = stylesheet + [
    #     {'selector': f'node[id="{s}"]', 'style': {'background-color': '#e74c3c'}}
    #     for s in active_states
    # ] 

    dynamic_styles = [
    {'selector': 'node', 'style': {'label': 'data(label)', 'width': 40, 'height': 40,
                                   'background-color': '#888'}},
    {'selector': '.start', 'style': {'background-color': '#2ecc71'}},
    {'selector': '.accept', 'style': {'background-color': '#f1c40f', 'shape': 'doublecircle'}},
    {'selector': 'edge', 'style': {'label': 'data(label)', 'curve-style': 'bezier',
                                   'target-arrow-shape': 'triangle',
                                   'text-rotation': 'autorotate',
                                   'text-margin-y': -10, 'font-size': 16}},
    {'selector': '.epsilon', 'style': {'line-style': 'dashed'}}
] + [
    {'selector': f'node[id="{s}"]', 'style': {'background-color': '#e74c3c'}}
    for s in active_states
]

    next_idx = step_idx + 1
    result = ""

    print(f"{step['char']}: {active_states}")

    if next_idx >= len(steps):
        accepted = your_nfa.accept_state in active_states
        result = f"Finished tracing! Accepted? {accepted}"

    return dynamic_styles, sim_data, next_idx, next_idx >= len(steps), result


if __name__ == '__main__':
    app.run(debug=True)
