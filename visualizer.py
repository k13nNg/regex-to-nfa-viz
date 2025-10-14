from graphviz import Digraph
import parser

regex = "(a|bc)*"

nfa = parser.parse_regex(regex).to_nfa()


def visualize_nfa_graphviz(nfa, filename="nfa.gv"):
    """
    Visualize an NFA (Thompson's construction style) using Graphviz.
    Generates a clean left-to-right layout.
    """
    dot = Digraph(comment="NFA", format="png")
    dot.attr(rankdir="LR", bgcolor="white")

    # Node styles
    for state in nfa.states:
        if state == nfa.start_state:
            dot.node(str(state), shape="circle", style="filled", fillcolor="#98FB98", label=f"Start\n{state}")
        elif state == nfa.accept_state:
            dot.node(str(state), shape="doublecircle", style="filled", fillcolor="#FFB6C1", label=f"Accept\n{state}")
        else:
            dot.node(str(state), shape="circle", label=str(state))

    # Add transitions
    for (src, symbol), dests in nfa._trans_func.items():
        for dest in dests:
            label = "ε" if symbol == "@" else symbol
            style = "dashed" if symbol == "@" else "solid"
            dot.edge(str(src), str(dest), label=label, style=style)

    dot.render(filename, view=True)
    print(f"✅ NFA visualization generated: {filename}.png")


visualize_nfa_graphviz(nfa)