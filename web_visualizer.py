from parser import parse_regex
from dash import Dash, html, dcc, Input, Output, State, callback_context as ctx, no_update
import graphviz
import dash_cytoscape as cyto
from nfa import global_id_gen

SCALE_X = 100
SCALE_Y = 100

test_nfa = None

# test_regex = "(a|b)"
# test_nfa = parse_regex(test_regex).to_nfa()

def nfa_to_cytoscape_elems(nfa):
    '''
    Convert the NFA into Cytoscape elements
    '''
    
    if nfa:

        # build the graph structure using graphviz DOT engine
        dot_eng = graphviz.Digraph(format='plain')
        dot_eng.attr(rankdir="LR")

        # load the NFA states into dot_eng
        for s in nfa.states:
            dot_eng.node(str(s))

        # load the NFA edges into dot_eng
        for (src, sym), dests in nfa.trans_func.items():
            for dest in dests:
                dot_eng.edge(str(src), str(dest), label=sym)
        
        # render to 'plain' format and extract positions
        # decode in "UTF-8" format as this is the default text output from Graphviz
        plain_output = dot_eng.pipe(format="plain").decode("UTF-8")

        # coordinates for the 'invisible' start state (the invisible state that the 'Start' edge originates from)
        x_start, y_start = 0.0, 0.0

        nodes = []
        edges = [{'data': {'source': 'initial_marker', 'target': str(nfa.start_state), 'label': 'Start'}}]

        # parse the 'plain' output format

        for line in plain_output.splitlines():
            parts = line.split()

            # only need the 'node' and the 'edge' statements, disregard the 'graph' and 'stop' statements
            if parts[0] == 'node':
                '''
                ---------------------
                General format of this statement:

                        node name x y width height label style shape color fillcolor

                ---------------------
                '''

                # get the node's name, x and y coordinates
                # these information are contained in the first 4 indices of parts
                name, x, y = parts[1:4]

                # JSON format for the node, appropriate format for Cytoscape
                # scale the coordinates appropriately
                node_elem = {
                    'data': {
                        'id':name, 
                        'label': "q"+name
                    },
                    'position': {
                        'x': float(x) * SCALE_X,
                        'y': -float(y) * SCALE_Y
                    },
                    'classes': 'state'
                }

                if (name == str(nfa.accept_state)):
                    node_elem['classes'] += " " + "accept"
                
                if (name == str(nfa.start_state)):
                    x_start = float(x)
                    y_start = float(y)

                    node_elem['classes'] += " " + "start"
                

                nodes.append(node_elem)

            if (parts[0] == 'edge'):
                '''
                ---------------------
                General format of this statement:
                        edge tail head n x₁ y₁ .. xₙ yₙ [label xl yl] style color
                ---------------------
                '''

                # cytoscape only need the 'tail' and 'head' parameters to create an edge
                head, tail = parts[1:3]
                
                # get the label for the edge
                label= ''
                for (src, sym), dests in nfa.trans_func.items():
                    if (str(src) == head) and (int(tail) in nfa.trans_func[(src, sym)]):
                        label = sym

                # JSON format for the edge, appropriate format for Cytoscape
                edge_elem = {
                    'data': {
                        'source': head,
                        'target': tail,
                        'label': label
                    },
                    'classes': 'edge'
                }        

                edges.append(edge_elem)

        # append the invisible 'initial_marker' node as the head for the 'Start' edge
        nodes.append({
                        'data': {'id': 'initial_marker'},
                        'position': {
                            'x': (x_start - 0.8) * SCALE_X,
                            'y': -y_start * SCALE_Y
                        },
                    })

        return nodes + edges

    else:
        return []
    
def get_active_states(nfa, ch, prev_states):
    # curr_states = nfa.get_epsilon_closure({nfa.start_state})
    curr_states = nfa.get_epsilon_closure(prev_states)
    
    # compute states reachable by consuming ch
    next_states = set()
    for s in curr_states:
        next_states |= nfa.get_next_state(s, ch)

    new_active_states = nfa.get_epsilon_closure(next_states)
    # print(f"{ch}: {new_active_states}")
    return (ch, new_active_states)

'''
---------------------
Dash App
---------------------
'''

stylesheet = [
    {
        'selector': 'state',
        'style': {
                    'label': 'data(label)',
                    'width': 40, 
                    'height': 40,
                    'text-margin-y': -10,     
                    'font-size': 12,
                    'events': 'no' 
                }
    },
    {'selector': '.accept', 
        'style': {'background-color': 'green'}
    },
    {
        'selector': 'edge',
        'style': {
                    'label': 'data(label)',
                    'width': 3,
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'text-rotation': 'autorotate',
                    'text-margin-x': 0,             
                    'text-margin-y': -10,           
                    'font-size': 12,
                    'color': '#34495e'
                }
    },
    {
        'selector': '#initial_marker',
        'style': {
            'label': '',
            'width': 40,
            'height': 40,
            'opacity': 0,
            'events': 'no' 
        }
    },
]

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Regex to NFA Visualizer", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.Div([
                dcc.Input(id="input-regex", 
                        type = "text", 
                        placeholder = 'Enter regex', 
                        style={
                                "fontFamily": "Courier New, monospace",
                                "fontSize": "20px",
                                "fontWeight": "bold",
                                "color": "#2c3e50",
                                'textAlign': 'center'
                            }),
                html.Button(
                    'Generate NFA', 
                    id='generate-nfa-button', 
                    n_clicks=0,
                    style={'margin': '10px', 'padding': '10px'}
                ), 
            ]),


            html.Div([
                dcc.Input(id="input-string", 
                                type = "text", 
                                placeholder = 'Enter test string', 
                                style={
                                        "fontFamily": "Courier New, monospace",
                                        "fontSize": "20px",
                                        "fontWeight": "bold",
                                        "color": "#2c3e50",
                                        'textAlign': 'center'
                                    }),
                html.Button(
                        'Step', 
                        id='trace-nfa-button', 
                        n_clicks=0,
                        style={'margin': '10px', 'padding': '10px'}
                    ),
            ]),
        ], style={
            'alignItem': 'start'
        }),
        html.Button(
            'Reset View', 
            id='reset-button', 
            n_clicks=0,
            style={'margin': '10px', 'padding': '10px'}
        ),            
    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center'
    }),

    

    html.Div(id='test-string-output',
             style={
                "fontFamily": "Courier New, monospace",
                "fontSize": "32px",
                "fontWeight": "bold",
                "color": "#2c3e50",
                'textAlign': 'center'
            }),

    cyto.Cytoscape(
        id = 'NFA-graph',
        layout={'name': 'preset', 'spacingFactor': 2.0, 'avoidOverlap': True},
        style={'width': '100%', 'height': '400px'},
        elements = nfa_to_cytoscape_elems(test_nfa),
        stylesheet=stylesheet
    ),  
    html.Div(id='acceptance-output',
            style={
            "fontFamily": "Courier New, monospace",
            "fontSize": "32px",
            "fontWeight": "bold",
            "color": "#2c3e50",
            'textAlign': 'center'
        }),
    dcc.Store(id='str-idx'),
    dcc.Store(id='nfa-curr-states'),
    dcc.Store(id='test-string-acceptance'),

])



@app.callback(
    Output('NFA-graph', 'layout'),
    Output('NFA-graph', 'stylesheet'),
    Output('NFA-graph', 'elements'),
    Output(component_id='test-string-output', component_property='children'),
    Output(component_id='acceptance-output', component_property='children'),
    Output('str-idx', 'data'),
    Output('nfa-curr-states', 'data'),
    Output('test-string-acceptance', 'data'),

    Input('reset-button', 'n_clicks'),
    Input('generate-nfa-button', 'n_clicks'),
    Input('trace-nfa-button', 'n_clicks'),

    State(component_id='input-string', component_property='value'),
    State(component_id='input-regex', component_property='value'),
    State('NFA-graph', 'elements'),
    State('str-idx', 'data'),
    State('nfa-curr-states', 'data'),
    State('test-string-acceptance', 'data'),
)
def handle_callback(reset_clicks, 
                    generate_clicks, 
                    trace_clicks, 
                    input_value, 
                    input_regex,
                    current_elements, 
                    str_idx,
                    nfa_curr_states,
                    test_string_acceptance):
    
    global test_nfa


    # 1. Identify Trigger
    trigger_id = ctx.triggered_id
    default_layout = {'name': 'preset'}
    str_idx = str_idx or {'idx': 0}
    input_value = input_value or ''

    nfa_curr_states = nfa_curr_states or {'curr_states': set()}
    test_string_acceptance = test_string_acceptance or False

    # --- A. Reset Button Trigger ---
    if trigger_id == 'reset-button':
        return (
            {
                'name': 'preset', 'fit': True, 'animate': True, 'animationDuration': 500,
                'reset_trigger': reset_clicks, 
            },
            stylesheet,
            current_elements, # Keep the graph elements exactly as they are
            no_update,         # Don't touch the test string output
            f"Accepted?: {test_string_acceptance}",
            str_idx,
            no_update,
            no_update
        )

    # --- B. NFA Generation Trigger ---
    elif trigger_id == 'generate-nfa-button':
        try:

            # Re-calculate and generate new elements
            global_id_gen.reset_id()
            test_nfa = parse_regex(input_regex).to_nfa()
            cyto_nfa_elems = nfa_to_cytoscape_elems(test_nfa)

            nfa_curr_states['curr_states'] = [test_nfa.start_state]

            # Return new elements, default layout, and updated test string value
            return (default_layout, 
                    stylesheet, 
                    cyto_nfa_elems, 
                    f'{input_value}',
                    f"Accepted?: {test_string_acceptance}",
                    str_idx,
                    nfa_curr_states,
                    no_update)
            
        except Exception as e:
            # Handle error during generation
            return (default_layout, 
                    stylesheet, 
                    [], 
                    f"Error: Invalid Regex! {str(e)}", 
                    f"Accepted?: {None}", 
                    no_update,
                    no_update
                    )
    # --- C. Trace Button Trigger ---
    elif trigger_id == 'trace-nfa-button':

        if (len(current_elements) != 0 and 
            input_value):

            if (str_idx['idx'] >= len(input_value)):
                str_idx['idx'] = 0
                nfa_curr_states['curr_states'] = [test_nfa.start_state]

            active_states = get_active_states(test_nfa, input_value[str_idx['idx']], set(nfa_curr_states['curr_states']))
            
            if (len(active_states[1]) > 0):
                if not(test_nfa.accept_state in set(nfa_curr_states['curr_states'])):
                    dynamic_stylesheet = stylesheet + [
                        {'selector': f'node[id="{s}"]', 'style': {'background-color': '#e74c3c'}}
                        for s in (active_states[1] | test_nfa.get_epsilon_closure({test_nfa.start_state}) | set(nfa_curr_states['curr_states']))
                    ]
                else:
                    dynamic_stylesheet = stylesheet + [
                        {'selector': f'node[id="{s}"]', 'style': {'background-color': '#e74c3c'}}
                        for s in (active_states[1] | test_nfa.get_epsilon_closure({test_nfa.start_state}))
                    ]
                    
            else:
                dynamic_stylesheet = stylesheet

            nfa_curr_states['curr_states'] = list(active_states[1])

            string_display_children = []
            test_string_acceptance = test_nfa.match(input_value)
            
            for i, char in enumerate(input_value):
                # Check if the current character index (i) matches the index (str_idx) being simulated
                if i == str_idx['idx']:
                    # Apply specific style to the currently simulated character
                    styled_char = html.Span(
                        char, 
                        style={
                            'textDecoration': 'underline !important', # <-- Add !important
                            'fontWeight': 'bold !important',         # <-- Add !important
                            'fontSize': '1.2em',                     
                            'color': '#c0392b'
                        }
                    )
                else:
                    # Use a standard span for all other characters
                    styled_char = html.Span(char)
                
                string_display_children.append(styled_char)
            
            str_idx['idx'] += 1

            return (no_update, 
                    dynamic_stylesheet, 
                    current_elements, 
                    string_display_children,
                    f"Accepted? {test_string_acceptance}",
                    str_idx,
                    nfa_curr_states,
                    test_string_acceptance)
        else:
            return (no_update, 
                    stylesheet, 
                    current_elements, 
                    f'Please generate the NFA first!',
                    no_update,
                    str_idx,
                    no_update,
                    no_update)

    # --- D. Default/Input String Trigger (input-string or initial load) ---
    else:
        # If any other input (like input-string or input-regex while not generating) 
        # triggers the callback, we must return the current state of the graph.
        return (
            no_update, 
            stylesheet,          
            current_elements, 
            f'{input_value}',
            f"Accepted? {test_string_acceptance}",
            str_idx,
            no_update,
            no_update
        )

if __name__ == "__main__":
    app.run(debug=True) 