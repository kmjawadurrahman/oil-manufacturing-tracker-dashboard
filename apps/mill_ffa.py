import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from helpers import *


dashboard_name = 'Mill FFA Metrics Dashboard'
sheet_names = ['mill', 'FFA', 'FFA Estate']

file_helpers_mill = FileHelpers('./data/mill and estate geo.xlsx', sheet_names[0])
file_helpers_ffa = FileHelpers('./data/mill parameters for demo.xlsx', sheet_names[1])
file_helpers_ffa_estate = FileHelpers('./data/mill parameters for demo.xlsx', sheet_names[2])
raw_mill_dataframe = file_helpers_mill.get_raw_dataframe()
raw_ffa_dataframe = file_helpers_ffa.get_raw_dataframe()
raw_ffa_estate_dataframe = file_helpers_ffa_estate.get_raw_dataframe()
mill_ffa_dataframe_helpers = DataFrameHelpers(raw_mill_dataframe, None)
ffa_dataframe_helpers = DataFrameHelpers(raw_ffa_dataframe, None)
ffa_estate_dataframe_helpers = DataFrameHelpers(raw_ffa_estate_dataframe, None)
mill_ffa_map_helpers = ChoroplethMapHelpers(None)
mill_ffa_dataframe_helpers.dataframe = mill_ffa_dataframe_helpers.ordered_categorical_dataframe_column(mill_ffa_dataframe_helpers.dataframe, 'Month',
                                                    mill_ffa_dataframe_helpers.month_categories, by=['Month'], is_ascending=True)
ffa_dataframe_helpers.dataframe = ffa_dataframe_helpers.ordered_categorical_dataframe_column(ffa_dataframe_helpers.dataframe, 'Month',
                                                    ffa_dataframe_helpers.month_categories, by=['Month', 'Date'], is_ascending=True)
ffa_estate_dataframe_helpers.dataframe = ffa_estate_dataframe_helpers.ordered_categorical_dataframe_column(ffa_estate_dataframe_helpers.dataframe, 'Month',
                                                    ffa_estate_dataframe_helpers.month_categories, by=['Month', 'Date'], is_ascending=True)
available_years_list = mill_ffa_dataframe_helpers.get_available_levels('Year')
available_months_list = mill_ffa_dataframe_helpers.get_available_levels('Month')
available_years_class = mill_ffa_dataframe_helpers.get_selector_options_class(available_years_list, available_years_list, is_ascending=False)
available_months_class = mill_ffa_dataframe_helpers.get_selector_options_class(available_months_list, mill_ffa_dataframe_helpers.month_categories, is_ascending=True)

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
        dcc.Graph(id='mill-map-ffa', style={'margin-bottom':8}, config={'displayModeBar': False},
                    hoverData={'points': [{'customdata': 'Mill 1'}]}),
                    className='row',
    ),
    html.Div([
        dcc.Graph(id='ffa-mill-backlog-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'Mill Backlog'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='ffa-mill-backlog-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
    html.Div([
        dcc.Graph(id='ffa-estate-backlog-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'Estate 7'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='ffa-estate-backlog-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
    html.Div([
        dcc.Graph(id='ffa-old-crop-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'Estate 7'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='ffa-old-crop-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
    html.Div([
        dcc.Graph(id='ffa-kkpa-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'KKPA'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='ffa-kkpa-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
    html.Div([
        dcc.Graph(id='ffa-lf-quality-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'Estate 7'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='ffa-lf-quality-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
    html.Div([
        dcc.Graph(id='ffa-lf-delivery-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'Estate 7'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='ffa-lf-delivery-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
], className='ten columns offset-by-one', style={'margin-bottom':50})


@app.callback(
    Output('mill-map-ffa', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ffa', 'hoverData')])
def update_mill_map_ffa(year, month, hoverData):
    figure = generate_mill_map(mill_ffa_dataframe_helpers, mill_ffa_map_helpers, year, month, hoverData)
    return figure


@app.callback(
    Output('ffa-mill-backlog-heatmap', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ffa', 'hoverData')])
def update_ffa_mill_backlog_heatmap(year, month, hoverData_map):
    ffa_heatmap_helpers = HeatmapHelpers(
                                ffa_dataframe_helpers.dataframe,
                                ffa_dataframe_helpers.dataframe.columns
                            )
    return ffa_heatmap_helpers.generate_heatmap(ffa_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                    ['% LF Delivery', '% LF Rotten', '% Old Crop', 'Backlog', 'Mill Backlog'],
                    [[1, 2, 3, 4], [5, 10, 15, 20], [30, 60, 90, 120], [14, 28, 42, 56], [24, 28, 32, 36]],
                    [True, True, True, True, True], 'Mill Backlog by Week', metric_is_pct=False)


@app.callback(
    Output('ffa-mill-backlog-daily-barchart', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ffa', 'hoverData'),
    Input('ffa-mill-backlog-heatmap', 'hoverData')])
def update_ffa_mill_backlog_daily_barchart(year, month, hoverData_map, hoverData_heatmap):
    ffa_barchart_helpers = BarChartHelpers(
                                ffa_dataframe_helpers.dataframe,
                                ffa_dataframe_helpers.dataframe.columns
                            )
    return ffa_barchart_helpers.generate_daily_barchart(ffa_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                                hoverData_heatmap, {'% LF Delivery': [1, 2, 3, 4], '% LF Rotten': [5, 10, 15, 20], '% Old Crop': [30, 60, 90, 120],
                                'Backlog': [14, 28, 42, 56], 'Mill Backlog':[24, 28, 32, 36]},
                                {'% LF Delivery': True, '% LF Rotten': True , '% Old Crop': True, 'Backlog': True, 'Mill Backlog': True},
                                metric_is_pct=False)


@app.callback(
    Output('ffa-estate-backlog-heatmap', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ffa', 'hoverData')])
def update_ffa_estate_backlog_heatmap(year, month, hoverData_map):
    ffa_estate_heatmap_helpers = HeatmapHelpers(
                                ffa_estate_dataframe_helpers.dataframe,
                                ffa_estate_dataframe_helpers.dataframe.columns
                            )
    return ffa_estate_heatmap_helpers.generate_heatmap(ffa_estate_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                     ['Estate 8', 'Estate 3', 'Estate 1', 'Estate 5', 'Estate 2', 'Estate 6', 'Estate 4', 'Estate 7'],
                    [[20, 40, 60, 80], [20, 40, 60, 80], [20, 40, 60, 80], [20, 40, 60, 80],
                     [20, 40, 60, 80], [20, 40, 60, 80], [20, 40, 60, 80], [20, 40, 60, 80]],
                    [True, True, True, True, True, True, True, True], 'Estate Backlog by Week',
                    filter_info={'Metric': 'Estate Backlog'}, metric_is_pct=False)


@app.callback(
    Output('ffa-estate-backlog-daily-barchart', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ffa', 'hoverData'),
    Input('ffa-estate-backlog-heatmap', 'hoverData')])
def update_ffa_estate_backlog_daily_barchart(year, month, hoverData_map, hoverData_heatmap):
    ffa_estate_barchart_helpers = BarChartHelpers(
                                ffa_estate_dataframe_helpers.dataframe,
                                ffa_estate_dataframe_helpers.dataframe.columns
                            )
    return ffa_estate_barchart_helpers.generate_daily_barchart(ffa_estate_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                                hoverData_heatmap, {'Estate 8': [20, 40, 60, 80], 'Estate 3': [20, 40, 60, 80], 'Estate 1': [20, 40, 60, 80],
                                'Estate 5': [20, 40, 60, 80], 'Estate 2': [20, 40, 60, 80], 'Estate 6': [20, 40, 60, 80],
                                'Estate 4': [20, 40, 60, 80], 'Estate 7': [20, 40, 60, 80]},
                                {'Estate 8': True, 'Estate 3': True, 'Estate 1': True, 'Estate 5': True,
                                'Estate 2': True, 'Estate 6': True, 'Estate 4': True, 'Estate 7': True},
                                metric_is_pct=False, filter_info={'Metric': 'Estate Backlog'}, chart_title_append=' Estate Backlog')


@app.callback(
    Output('ffa-old-crop-heatmap', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ffa', 'hoverData')])
def update_ffa_old_crop_heatmap(year, month, hoverData_map):
    ffa_estate_heatmap_helpers = HeatmapHelpers(
                                ffa_estate_dataframe_helpers.dataframe,
                                ffa_estate_dataframe_helpers.dataframe.columns
                            )
    return ffa_estate_heatmap_helpers.generate_heatmap(ffa_estate_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                     ['Estate 8', 'Estate 3', 'Estate 1', 'Estate 5', 'Estate 2', 'Estate 6', 'Estate 4', 'Estate 7'],
                     [[20, 40, 60, 80], [20, 40, 60, 80], [20, 40, 60, 80], [20, 40, 60, 80],
                      [20, 40, 60, 80], [20, 40, 60, 80], [20, 40, 60, 80], [20, 40, 60, 80]],
                     [True, True, True, True, True, True, True, True], 'Old Crop by Week',
                     filter_info={'Metric': 'Old Crop'}, metric_is_pct=False)


@app.callback(
    Output('ffa-old-crop-daily-barchart', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ffa', 'hoverData'),
    Input('ffa-old-crop-heatmap', 'hoverData')])
def update_ffa_old_crop_daily_barchart(year, month, hoverData_map, hoverData_heatmap):
    ffa_estate_barchart_helpers = BarChartHelpers(
                                ffa_estate_dataframe_helpers.dataframe,
                                ffa_estate_dataframe_helpers.dataframe.columns
                            )
    return ffa_estate_barchart_helpers.generate_daily_barchart(ffa_estate_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                                hoverData_heatmap, {'Estate 8': [20, 40, 60, 80], 'Estate 3': [20, 40, 60, 80], 'Estate 1': [20, 40, 60, 80],
                                'Estate 5': [20, 40, 60, 80], 'Estate 2': [20, 40, 60, 80], 'Estate 6': [20, 40, 60, 80],
                                'Estate 4': [20, 40, 60, 80], 'Estate 7': [20, 40, 60, 80]},
                                {'Estate 8': True, 'Estate 3': True, 'Estate 1': True, 'Estate 5': True,
                                'Estate 2': True, 'Estate 6': True, 'Estate 4': True, 'Estate 7': True},
                                metric_is_pct=False, filter_info={'Metric': 'Old Crop'}, chart_title_append=' Old Crop')


@app.callback(
    Output('ffa-kkpa-heatmap', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ffa', 'hoverData')])
def update_ffa_kkpa_heatmap(year, month, hoverData_map):
    ffa_heatmap_helpers = HeatmapHelpers(
                                ffa_dataframe_helpers.dataframe,
                                ffa_dataframe_helpers.dataframe.columns
                            )
    return ffa_heatmap_helpers.generate_heatmap(ffa_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                    ['KKPA'],
                    [[1, 2, 3, 4]],
                    [True], 'KKPA by Week', metric_is_pct=False)


@app.callback(
    Output('ffa-kkpa-daily-barchart', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ffa', 'hoverData'),
    Input('ffa-kkpa-heatmap', 'hoverData')])
def update_ffa_kkpa_daily_barchart(year, month, hoverData_map, hoverData_heatmap):
    ffa_barchart_helpers = BarChartHelpers(
                                ffa_dataframe_helpers.dataframe,
                                ffa_dataframe_helpers.dataframe.columns
                            )
    return ffa_barchart_helpers.generate_daily_barchart(ffa_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                                hoverData_heatmap,  {'KKPA': [1, 2, 3, 4]},
                                {'KKPA': True},
                                metric_is_pct=False)


@app.callback(
    Output('ffa-lf-quality-heatmap', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ffa', 'hoverData')])
def update_ffa_lf_quality_heatmap(year, month, hoverData_map):
    ffa_estate_heatmap_helpers = HeatmapHelpers(
                                ffa_estate_dataframe_helpers.dataframe,
                                ffa_estate_dataframe_helpers.dataframe.columns
                            )
    return ffa_estate_heatmap_helpers.generate_heatmap(ffa_estate_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                     ['Estate 8', 'Estate 3', 'Estate 1', 'Estate 5', 'Estate 2', 'Estate 6', 'Estate 4', 'Estate 7'],
                    [[10, 15, 20, 25], [10, 15, 20, 25], [10, 15, 20, 25], [10, 15, 20, 25],
                     [10, 15, 20, 25], [10, 15, 20, 25], [10, 15, 20, 25], [10, 15, 20, 25]],
                    [False, False, False, False, False, False, False, False], 'Loose Fruit Quality by Week',
                    filter_info={'Metric': 'Loose Fruit Quality'}, metric_is_pct=False)


@app.callback(
    Output('ffa-lf-quality-daily-barchart', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ffa', 'hoverData'),
    Input('ffa-lf-quality-heatmap', 'hoverData')])
def update_ffa_lf_quality_daily_barchart(year, month, hoverData_map, hoverData_heatmap):
    ffa_estate_barchart_helpers = BarChartHelpers(
                                ffa_estate_dataframe_helpers.dataframe,
                                ffa_estate_dataframe_helpers.dataframe.columns
                            )
    return ffa_estate_barchart_helpers.generate_daily_barchart(ffa_estate_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                                hoverData_heatmap, {'Estate 8': [10, 15, 20, 25], 'Estate 3': [10, 15, 20, 25], 'Estate 1': [10, 15, 20, 25],
                                'Estate 5': [10, 15, 20, 25], 'Estate 2': [10, 15, 20, 25], 'Estate 6': [10, 15, 20, 25],
                                'Estate 4': [10, 15, 20, 25], 'Estate 7': [10, 15, 20, 25]},
                                {'Estate 8': False, 'Estate 3': False, 'Estate 1': False, 'Estate 5': False,
                                'Estate 2': False, 'Estate 6': False, 'Estate 4': False, 'Estate 7': False},
                                metric_is_pct=False, filter_info={'Metric': 'Loose Fruit Quality'}, chart_title_append=' Loose Fruit Quality')


@app.callback(
    Output('ffa-lf-delivery-heatmap', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ffa', 'hoverData')])
def update_ffa_lf_delivery_heatmap(year, month, hoverData_map):
    ffa_estate_heatmap_helpers = HeatmapHelpers(
                                ffa_estate_dataframe_helpers.dataframe,
                                ffa_estate_dataframe_helpers.dataframe.columns
                            )
    return ffa_estate_heatmap_helpers.generate_heatmap(ffa_estate_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                     ['Estate 8', 'Estate 3', 'Estate 1', 'Estate 5', 'Estate 2', 'Estate 6', 'Estate 4', 'Estate 7'],
                    [[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4],
                     [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]],
                    [True, True, True, True, True, True, True, True], 'Loose Fruit Delivery by Week',
                    filter_info={'Metric': 'Loose Fruit Delivery'}, metric_is_pct=False)


@app.callback(
    Output('ffa-lf-delivery-daily-barchart', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ffa', 'hoverData'),
    Input('ffa-lf-delivery-heatmap', 'hoverData')])
def update_ffa_lf_delivery_daily_barchart(year, month, hoverData_map, hoverData_heatmap):
    ffa_estate_barchart_helpers = BarChartHelpers(
                                ffa_estate_dataframe_helpers.dataframe,
                                ffa_estate_dataframe_helpers.dataframe.columns
                            )
    return ffa_estate_barchart_helpers.generate_daily_barchart(ffa_estate_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                                hoverData_heatmap, {'Estate 8': [1, 2, 3, 4], 'Estate 3': [1, 2, 3, 4], 'Estate 1': [1, 2, 3, 4],
                                'Estate 5': [1, 2, 3, 4], 'Estate 2': [1, 2, 3, 4], 'Estate 6': [1, 2, 3, 4],
                                'Estate 4': [1, 2, 3, 4], 'Estate 7': [1, 2, 3, 4]},
                                {'Estate 8': True, 'Estate 3': True, 'Estate 1': True, 'Estate 5': True,
                                'Estate 2': True, 'Estate 6': True, 'Estate 4': True, 'Estate 7': True},
                                metric_is_pct=False, filter_info={'Metric': 'Loose Fruit Delivery'}, chart_title_append=' Loose Fruit Delivery')
