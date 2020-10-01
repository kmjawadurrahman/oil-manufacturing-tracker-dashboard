from os import sys, path

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import overall, estate, mill, mill_oer, mill_ffa, mill_screw, mill_sludge, mill_ebpress, mill_oil_loss, mill_sterilizer


server = app.server

sys.path.append(path.dirname(path.abspath(__file__)))

app.layout = html.Div([
        dcc.Location(id='url', refresh=True),
        html.Div(id='mill-screw-clickData', style={'display': 'none'}),
        html.Div(id='mill-sludge-clickData', style={'display': 'none'}),
        html.Div(id='mill-sterilizer-clickData', style={'display': 'none'}),
        html.Div(id='mill-ebpress-clickData', style={'display': 'none'}),
        html.Div(id='page-content')
    ])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return overall.layout
    elif pathname == '/estate':
        return estate.layout
    elif pathname == '/mill':
        return mill.layout
    elif pathname == '/mill-screw':
        return mill_screw.layout
    elif pathname == '/mill-sludge':
        return mill_sludge.layout
    elif pathname == '/mill-sterilizer':
        return mill_sterilizer.layout
    elif pathname == '/mill-ebpress':
        return mill_ebpress.layout
    elif pathname == '/mill-oer':
        return mill_oer.layout
    elif pathname == '/mill-ffa':
        return mill_ffa.layout
    elif pathname == '/mill-oil-loss':
        return mill_oil_loss.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=False)
