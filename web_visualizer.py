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
    
def get_active_states(nfa, ch):
    curr_states = nfa.get_epsilon_closure({nfa.start_state})

    for s in curr_states:
        next_states |= nfa.get_next_state(s, ch)

    curr_states = nfa.get_epsilon_closure(next_states)

    return (ch, list(curr_states))




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
    html.H1("Regex to NFA Tracer", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.H2("Regex:"),
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
        ], style={
            'display': 'flex',
            'alignItems': 'center',  
            'marginBottom': '20px',
            'gap':'10px',
            'width': '550px'

        }),
    ], style = {
        'margin': '0 auto',
        'marginBottom': '20px',
        'width': '100%'
    }),
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
                'Trace NFA', 
                id='trace-nfa-button', 
                n_clicks=0,
                style={'margin': '10px', 'padding': '10px'}
            ),
    ]),
    html.Button(
            'Reset View', 
            id='reset-button', 
            n_clicks=0,
            style={'margin': '10px', 'padding': '10px'}
    ),            

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
        style={'width': '100%', 'height': '600px'},
        elements = nfa_to_cytoscape_elems(test_nfa),
        stylesheet=stylesheet
    ),
   
    
])

# @app.callback(
#     Output('NFA-graph', 'layout'),
#     Output('NFA-graph', 'elements'),
#     Output(component_id='test-string-output', component_property='children'),
#     Input('reset-button', 'n_clicks'),
#     Input('generate-nfa-button', 'n_clicks'),
#     Input('trace-nfa-button', 'n_clicks'),
#     Input(component_id='input-string', component_property='value'),
#     Input(component_id='input-regex', component_property='value'),
#     State('NFA-graph', 'elements')
# )

# def handle_callback(reset_clicks, generate_clicks, trace_clicks, input_value, input_regex, current_elements):
#     """Resets the Cytoscape view to fit all elements."""

#     cyto_nfa_elems = []
#     try:
#         # test if the regex is valid first 
#         parse_regex(input_regex)

#         if ('generate-nfa-button' == ctx.triggered_id):
#             global_id_gen.reset_id()
#             test_nfa = parse_regex(input_regex).to_nfa()
#             cyto_nfa_elems = nfa_to_cytoscape_elems(test_nfa)

#         # Check if the button has been clicked at least once
#         if reset_clicks > 0:
#             # Return the layout dictionary with 'fit': True
#             return {
#                 'name': 'preset',
#                 'fit': True,
#                 'animate': True,
#                 'animationDuration': 500,
#                 'reset_trigger': reset_clicks
#             }, current_elements, f'{input_value}'
        
#     except Exception:
#         test_nfa = None
    
#     return {'name': 'preset'},\
#             cyto_nfa_elems,\
#             f'{input_value}'

@app.callback(
    Output('NFA-graph', 'layout'),
    Output('NFA-graph', 'elements'),
    Output(component_id='test-string-output', component_property='children'),
    Input('reset-button', 'n_clicks'),
    Input('generate-nfa-button', 'n_clicks'),
    Input('trace-nfa-button', 'n_clicks'),
    Input(component_id='input-string', component_property='value'),
    Input(component_id='input-regex', component_property='value'),
    State('NFA-graph', 'elements')
)
def handle_callback(reset_clicks, generate_clicks, trace_clicks, input_value, input_regex, current_elements):
    
    # 1. Identify Trigger
    trigger_id = ctx.triggered_id
    default_layout = {'name': 'preset'}
    
    # --- A. Reset Button Trigger ---
    if trigger_id == 'reset-button' and reset_clicks > 0:
        return (
            {
                'name': 'preset', 'fit': True, 'animate': True, 'animationDuration': 500,
                'reset_trigger': reset_clicks, 
            },
            current_elements, # Keep the graph elements exactly as they are
            no_update         # Don't touch the test string output
        )

    # --- B. NFA Generation Trigger ---
    elif trigger_id == 'generate-nfa-button':
        try:
            # Re-calculate and generate new elements
            global_id_gen.reset_id()
            test_nfa = parse_regex(input_regex).to_nfa()
            cyto_nfa_elems = nfa_to_cytoscape_elems(test_nfa)
            
            # Return new elements, default layout, and updated test string value
            return default_layout, cyto_nfa_elems, f'{input_value}'
            
        except Exception as e:
            # Handle error during generation
            # print(f"Regex Error: {e}")
            return default_layout, [], f"Error: Invalid Regex!"

    # --- C. Trace Button Trigger (If implemented) ---
    elif trigger_id == 'trace-nfa-button':
        # Assuming tracing updates the elements (e.g., highlights nodes)
        # You'll need logic here to process current_elements and input_value

        new_layout = {

        }

        # Example: update elements for tracing logic
        # traced_elements = trace_nfa_elements(current_elements, input_value)
        # return no_update, traced_elements, f'Tracing: {input_value}'
        
        # For now, just pass through elements while updating the string display:
        return no_update, current_elements, f'{input_value}'

    # --- D. Default/Input String Trigger (input-string or initial load) ---
    else:
        # If any other input (like input-string or input-regex while not generating) 
        # triggers the callback, we must return the current state of the graph.
        return (
            no_update,           
            current_elements,    
            f'{input_value}'
        )

if __name__ == "__main__":
    app.run(debug=True) 