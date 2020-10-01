import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from helpers import *


dashboard_name = 'Mill Oil Loss Metrics Dashboard'
sheet_names = ['mill', 'Oil Loss']

file_helpers_mill = FileHelpers('./data/mill and estate geo.xlsx', sheet_names[0])
file_helpers_ol = FileHelpers('./data/mill parameters for demo.xlsx', sheet_names[1])
raw_mill_dataframe = file_helpers_mill.get_raw_dataframe()
raw_ol_dataframe = file_helpers_ol.get_raw_dataframe()
mill_ol_dataframe_helpers = DataFrameHelpers(raw_mill_dataframe, None)
ol_dataframe_helpers = DataFrameHelpers(raw_ol_dataframe, None)
mill_ol_map_helpers = ChoroplethMapHelpers(None)
mill_ol_dataframe_helpers.dataframe = mill_ol_dataframe_helpers.ordered_categorical_dataframe_column(mill_ol_dataframe_helpers.dataframe, 'Month',
                                                    mill_ol_dataframe_helpers.month_categories, by=['Month'], is_ascending=True)
ol_dataframe_helpers.dataframe = ol_dataframe_helpers.ordered_categorical_dataframe_column(ol_dataframe_helpers.dataframe, 'Month',
                                                    ol_dataframe_helpers.month_categories, by=['Month', 'Date'], is_ascending=True)

available_years_list = mill_ol_dataframe_helpers.get_available_levels('Year')
available_months_list = mill_ol_dataframe_helpers.get_available_levels('Month')
available_years_class = mill_ol_dataframe_helpers.get_selector_options_class(available_years_list, available_years_list, is_ascending=False)
available_months_class = mill_ol_dataframe_helpers.get_selector_options_class(available_months_list, mill_ol_dataframe_helpers.month_categories, is_ascending=True)

layout_helpers = FixedLayoutHelpers(dashboard_name)
firstrow_layout = layout_helpers.generate_firstrow_layout(button_name_list=['Go Back'], href_list = ['/mill'])
secondrow_layout = layout_helpers.generate_secondrow_layout(available_years_class, available_months_class)

layout = html.Div([
    html.Div(
        firstrow_layout, className='row', style={'margin-top':20, 'margin-bottom':20}
    ),
    html.Div(
        secondrow_layout, className='row', style={'margin-bottom':20}
    ),
    html.Div(
        dcc.Graph(id='mill-map-ol', style={'margin-bottom':8}, config={'displayModeBar': False},
                    hoverData={'points': [{'customdata': 'Mill 1'}]}),
                    className='row',
    ),
    html.Div([
        dcc.Graph(id='ol-lines-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'Line 1'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='ol-lines-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
    html.Div([
        dcc.Graph(id='ol-screws-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'Screw Press 1'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='ol-screws-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
    html.Div([
        dcc.Graph(id='ol-eb-loss-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'EB Press 1'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='ol-eb-loss-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
    html.Div([
        dcc.Graph(id='ol-eb-rec-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'EB Press 1 Rec.'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='ol-eb-rec-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
    html.Div([
        dcc.Graph(id='ol-sludge-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'Sludge Separator 1'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='ol-sludge-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
    html.Div([
        dcc.Graph(id='ol-condensate-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'Condensate Loss'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='ol-condensate-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
], className='ten columns offset-by-one', style={'margin-bottom':50})


@app.callback(
    Output('mill-map-ol', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ol', 'hoverData')])
def update_mill_map_ol(year, month, hoverData):
    figure = generate_mill_map(mill_ol_dataframe_helpers, mill_ol_map_helpers, year, month, hoverData)
    return figure


@app.callback(
    Output('ol-lines-heatmap', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ol', 'hoverData')])
def update_ol_lines_heatmap(year, month, hoverData_map):
    ol_heatmap_helpers = HeatmapHelpers(
                                ol_dataframe_helpers.dataframe,
                                ol_dataframe_helpers.dataframe.columns
                            )
    return ol_heatmap_helpers.generate_heatmap(ol_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                    ['Line 2', 'Line 1'], [[0.39, 0.43, 0.47, 0.51], [0.39, 0.43, 0.47, 0.51]],
                    [True, True], 'Cyclone Fiber Loss by Line by Week (% of FFB)', metric_is_pct=False)


@app.callback(
    Output('ol-lines-daily-barchart', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ol', 'hoverData'),
    Input('ol-lines-heatmap', 'hoverData')])
def update_ol_lines_daily_barchart(year, month, hoverData_map, hoverData_heatmap):
    ol_barchart_helpers = BarChartHelpers(
                                ol_dataframe_helpers.dataframe,
                                ol_dataframe_helpers.dataframe.columns
                            )
    return ol_barchart_helpers.generate_daily_barchart(ol_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                                hoverData_heatmap, {'Line 2': [0.39, 0.43, 0.47, 0.51], 'Line 1': [0.39, 0.43, 0.47, 0.51]},
                                {'Line 2': True, 'Line 1': True},
                                metric_is_pct=False)


@app.callback(
    Output('ol-screws-heatmap', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ol', 'hoverData')])
def update_ol_screws_heatmap(year, month, hoverData_map):
    ol_heatmap_helpers = HeatmapHelpers(
                                ol_dataframe_helpers.dataframe,
                                ol_dataframe_helpers.dataframe.columns
                            )
    return ol_heatmap_helpers.generate_heatmap(ol_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                    ['Screw Press 6', 'Screw Press 5', 'Screw Press 4', 'Screw Press 3', 'Screw Press 2', 'Screw Press 1'],
                    [[3.9, 4.3, 4.7, 5.1], [3.9, 4.3, 4.7, 5.1], [3.9, 4.3, 4.7, 5.1],
                        [3.9, 4.3, 4.7, 5.1], [3.9, 4.3, 4.7, 5.1], [3.9, 4.3, 4.7, 5.1]],
                    [True, True, True, True, True, True], 'Cyclone Fiber Loss by Machine by Week (% of Wet Mass)', metric_is_pct=True)


@app.callback(
    Output('ol-screws-daily-barchart', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ol', 'hoverData'),
    Input('ol-screws-heatmap', 'hoverData')])
def update_ol_screws_daily_barchart(year, month, hoverData_map, hoverData_heatmap):
    ol_barchart_helpers = BarChartHelpers(
                                ol_dataframe_helpers.dataframe,
                                ol_dataframe_helpers.dataframe.columns
                            )
    return ol_barchart_helpers.generate_daily_barchart(ol_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                                hoverData_heatmap,  {'Screw Press 6': [3.9, 4.3, 4.7, 5.1], 'Screw Press 5': [3.9, 4.3, 4.7, 5.1],
                                 'Screw Press 4': [3.9, 4.3, 4.7, 5.1], 'Screw Press 3': [3.9, 4.3, 4.7, 5.1],
                                 'Screw Press 2': [3.9, 4.3, 4.7, 5.1], 'Screw Press 1': [3.9, 4.3, 4.7, 5.1]},
                                {'Screw Press 6': True, 'Screw Press 5': True,
                                 'Screw Press 4': True, 'Screw Press 3': True,
                                 'Screw Press 2': True, 'Screw Press 1': True},
                                metric_is_pct=True)


@app.callback(
    Output('ol-eb-loss-heatmap', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ol', 'hoverData')])
def update_ol_eb_loss_heatmap(year, month, hoverData_map):
    ol_heatmap_helpers = HeatmapHelpers(
                                ol_dataframe_helpers.dataframe,
                                ol_dataframe_helpers.dataframe.columns
                            )
    return ol_heatmap_helpers.generate_heatmap(ol_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                    ['EB Press 2', 'EB Press 1'],
                    [[1.64, 1.78, 1.92, 2.06], [1.40, 1.70, 2.00, 2.30]],
                    [True, True], 'Empty Bunch Loss by EB Press by Week (% of WM)', metric_is_pct=False)


@app.callback(
    Output('ol-eb-loss-daily-barchart', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ol', 'hoverData'),
    Input('ol-eb-loss-heatmap', 'hoverData')])
def update_ol_eb_loss_daily_barchart(year, month, hoverData_map, hoverData_heatmap):
    ol_barchart_helpers = BarChartHelpers(
                                ol_dataframe_helpers.dataframe,
                                ol_dataframe_helpers.dataframe.columns
                            )
    return ol_barchart_helpers.generate_daily_barchart(ol_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                                hoverData_heatmap,  {'EB Press 2': [1.64, 1.78, 1.92, 2.06], 'EB Press 1': [1.40, 1.70, 2.00, 2.30]},
                                {'EB Press 2': True, 'EB Press 1': True},
                                metric_is_pct=False)


@app.callback(
    Output('ol-eb-rec-heatmap', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ol', 'hoverData')])
def update_ol_eb_rec_heatmap(year, month, hoverData_map):
    ol_heatmap_helpers = HeatmapHelpers(
                                ol_dataframe_helpers.dataframe,
                                ol_dataframe_helpers.dataframe.columns
                            )
    return ol_heatmap_helpers.generate_heatmap(ol_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                    ['EB Press 2 Rec.', 'EB Press 1 Rec.'],
                    [[4.4, 10.8, 17.2, 23.6], [0.4, 7.8, 15.2, 22.6]],
                    [False, False], 'Recovery by Week', metric_is_pct=False)


@app.callback(
    Output('ol-eb-rec-daily-barchart', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ol', 'hoverData'),
    Input('ol-eb-rec-heatmap', 'hoverData')])
def update_ol_eb_rec_daily_barchart(year, month, hoverData_map, hoverData_heatmap):
    ol_barchart_helpers = BarChartHelpers(
                                ol_dataframe_helpers.dataframe,
                                ol_dataframe_helpers.dataframe.columns
                            )
    return ol_barchart_helpers.generate_daily_barchart(ol_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                                hoverData_heatmap, {'EB Press 2 Rec.': [4.4, 10.8, 17.2, 23.6], 'EB Press 1 Rec.': [0.4, 7.8, 15.2, 22.6]},
                                {'EB Press 2 Rec.': False, 'EB Press 1 Rec.': False},
                                metric_is_pct=False)


@app.callback(
    Output('ol-sludge-heatmap', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ol', 'hoverData')])
def update_ol_sludge_heatmap(year, month, hoverData_map):
    ol_heatmap_helpers = HeatmapHelpers(
                                ol_dataframe_helpers.dataframe,
                                ol_dataframe_helpers.dataframe.columns
                            )
    return ol_heatmap_helpers.generate_heatmap(ol_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                    ['Sludge Separator 3', 'Sludge Separator 2', 'Sludge Separator 1'],
                    [[0.6, 0.7, 0.8, 0.9], [0.6, 0.7, 0.8, 0.9], [0.6, 0.7, 0.8, 0.9]],
                    [True, True, True], 'Raw Effluent Loss by Sludge Separator by Week', metric_is_pct=False)


@app.callback(
    Output('ol-sludge-daily-barchart', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ol', 'hoverData'),
    Input('ol-sludge-heatmap', 'hoverData')])
def update_ol_sludge_daily_barchart(year, month, hoverData_map, hoverData_heatmap):
    ol_barchart_helpers = BarChartHelpers(
                                ol_dataframe_helpers.dataframe,
                                ol_dataframe_helpers.dataframe.columns
                            )
    return ol_barchart_helpers.generate_daily_barchart(ol_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                                hoverData_heatmap, {'Sludge Separator 1': [0.6, 0.7, 0.8, 0.9], 'Sludge Separator 2': [0.6, 0.7, 0.8, 0.9], 'Sludge Separator 3': [0.6, 0.7, 0.8, 0.9]},
                                {'Sludge Separator 1': True, 'Sludge Separator 2': True, 'Sludge Separator 3': True},
                                metric_is_pct=False)


@app.callback(
    Output('ol-condensate-heatmap', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ol', 'hoverData')])
def update_ol_condensate_heatmap(year, month, hoverData_map):
    ol_heatmap_helpers = HeatmapHelpers(
                                ol_dataframe_helpers.dataframe,
                                ol_dataframe_helpers.dataframe.columns
                            )
    return ol_heatmap_helpers.generate_heatmap(ol_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                    ['Condensate Loss'],
                    [[1.4, 1.8, 2.2, 2.6]],
                    [True], 'Condensate Loss by Week', metric_is_pct=False)


@app.callback(
    Output('ol-condensate-daily-barchart', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ol', 'hoverData'),
    Input('ol-condensate-heatmap', 'hoverData')])
def update_ol_condensate_daily_barchart(year, month, hoverData_map, hoverData_heatmap):
    ol_barchart_helpers = BarChartHelpers(
                                ol_dataframe_helpers.dataframe,
                                ol_dataframe_helpers.dataframe.columns
                            )
    return ol_barchart_helpers.generate_daily_barchart(ol_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                                hoverData_heatmap, {'Condensate Loss': [1.4, 1.8, 2.2, 2.6]},
                                {'Condensate Loss': True},
                                metric_is_pct=False)
