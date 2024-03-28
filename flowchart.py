from graphviz import Digraph, Source
from random import choice

def create_flowchart():
    # Define a list of colors for the nodes
    colors = ['#006400', '#FFD700', '#87CEFA', '#D95319', '#EDB120']

    flowchart = Digraph(
        comment='Soil Health Diagnostic System',
        format='png',
        node_attr={'shape': 'rectangle', 'fontname': 'Helvetica', 'fontsize': '8', 'fontcolor': '#333333', 'style': 'filled'},
        edge_attr={'arrowhead': 'normal', 'arrowtail': 'none'},
        graph_attr={'bgcolor': 'white', 'fontcolor': '#333333', 'fontname': 'Helvetica', 'fontsize': '10', 'layout': 'dot', 'ratio': 'compress'}
    )

    # Nodes on the left-hand side
    with flowchart.subgraph(name='cluster_left', node_attr={'color': choice(colors), 'fontcolor': '#333333', 'rankdir': 'TB'}) as left_subgraph:
        left_subgraph.attr(label='Start', fontname='Helvetica', fontsize='10', style='filled')
        left_subgraph.node('start', 'Start', color=choice(colors))
        left_subgraph.node('input', 'Input Farmer Info\nand Soil Health Indicators', color=choice(colors))
        left_subgraph.node('validate', 'Validate Input', color=choice(colors))

    # Nodes on the right-hand side
    with flowchart.subgraph(name='cluster_right', node_attr={'color': choice(colors), 'fontcolor': '#333333', 'rankdir': 'TB'}) as right_subgraph:
        right_subgraph.attr(label='End', fontname='Helvetica', fontsize='10', style='filled')
        right_subgraph.node('assess', 'Assess Soil Health', color=choice(colors))
        right_subgraph.node('output', 'Output Soil Health\nScore and Recommendations', color=choice(colors))
        right_subgraph.node('save', 'Save Results\nto Database', color=choice(colors))
        right_subgraph.node('generate_report', 'Generate PDF\nReport', color=choice(colors))
        right_subgraph.node('end', 'End', color=choice(colors))

    # Create a subgraph for FAHP weight calculation
    with flowchart.subgraph(name='cluster_fahp', node_attr={'color': choice(colors), 'fontcolor': '#333333'}) as fahp_subgraph:
        fahp_subgraph.attr(label='FAHP Weight Calculation', fontname='Helvetica', fontsize='10', style='filled')
        fahp_subgraph.node('fahp_start', 'Start', color=choice(colors))
        fahp_subgraph.node('fahp_input', 'Input Fuzzy\nComparison Matrix', color=choice(colors))
        fahp_subgraph.node('geometric_mean', 'Calculate Fuzzy\nGeometric Means', color=choice(colors))
        fahp_subgraph.node('fuzzy_weights', 'Calculate Fuzzy\nWeights', color=choice(colors))
        fahp_subgraph.node('defuzzify', 'Defuzzify Fuzzy\nWeights', color=choice(colors))
        fahp_subgraph.node('normalize', 'Normalize Weights', color=choice(colors))
        fahp_subgraph.node('consistency_check', 'Check Consistency\nRatio', color=choice(colors))
        fahp_subgraph.node('consistent', 'Consistent?', color=choice(colors), fontcolor='black')
        fahp_subgraph.node('fahp_output', 'Output FAHP\nWeights', color=choice(colors))
        fahp_subgraph.node('fahp_end', 'End', color=choice(colors))
        fahp_subgraph.node('reenter', 'Re-enter Fuzzy\nComparison Matrix', color=choice(colors))

        fahp_subgraph.edges([('fahp_start', 'fahp_input'), ('fahp_input', 'geometric_mean'),
                              ('geometric_mean', 'fuzzy_weights'), ('fuzzy_weights', 'defuzzify'),
                              ('defuzzify', 'normalize'), ('normalize', 'consistency_check'),
                              ('consistency_check', 'consistent')])
        fahp_subgraph.edge('consistent', 'fahp_output', label='Yes', fontcolor='green')
        fahp_subgraph.edge('consistent', 'reenter', label='No', fontcolor='red')
        fahp_subgraph.edges([('reenter', 'fahp_input'), ('fahp_output', 'fahp_end')])

    flowchart.edges([('start', 'input'), ('input', 'validate'), ('validate', 'fahp_start'),
                     ('fahp_end', 'assess'), ('assess', 'output'), ('output', 'save'),
                     ('save', 'generate_report'), ('generate_report', 'end')])

    flowchart.render('soil_health_diagnostic_system', view=True)

    # Display the flowchart in a window
    Source.from_file('soil_health_diagnostic_system.gv.png')._repr_png_()

if __name__ == "__main__":
    create_flowchart()