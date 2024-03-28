from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool
from math import radians

def create_bokeh_graph(indicator_values):
    categories = ['pH', 'N', 'P', 'K', 'EC', 'Temp', 'Moist', 'Humid']
    angles = [radians(i * 360 / len(categories)) for i in range(len(categories))]

    source = ColumnDataSource(data=dict(
        category=categories,
        value=indicator_values,
        angle=angles
    ))

    p = figure(width=600, height=600, x_range=(-1.1, 1.1), y_range=(-1.1, 1.1),
               tools="hover,pan,wheel_zoom,reset", toolbar_location=None)

    p.wedge(x=0, y=0, radius=1, start_angle=min(angles), end_angle=max(angles),
            color="lightgray", alpha=0.5)

    p.line(x='angle', y='value', source=source, line_width=2, line_color='blue')
    p.scatter(x='angle', y='value', source=source, size=10, fill_color='blue', line_color='white')

    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.xaxis.major_tick_line_color = None
    p.xaxis.minor_tick_line_color = None
    p.yaxis.major_tick_line_color = None
    p.yaxis.minor_tick_line_color = None
    p.xaxis.major_label_text_font_size = '0pt'
    p.yaxis.major_label_text_font_size = '0pt'

    hover = p.select_one(HoverTool)
    hover.tooltips = [
        ('Category', '@category'),
        ('Value', '@value'),
    ]

    show(p)

# Usage:
indicator_values = [7.5, 150, 75, 120, 1.5, 25, 60, 50]
create_bokeh_graph(indicator_values)