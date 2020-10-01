import time
import json
import datetime

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import plotly.figure_factory as ff

from helpers import *
from app import app


dashboard_name = 'Mill Dashboard'
sheet_name = 'mill'

file_helpers_mill = FileHelpers('./data/mill and estate geo.xlsx', sheet_name)
raw_mill_dataframe = file_helpers_mill.get_raw_dataframe()
mill_dataframe_helpers = DataFrameHelpers(raw_mill_dataframe, None)
mill_map_helpers = ChoroplethMapHelpers(None)

file_helpers_parameters_monthly = FileHelpers('./data/mill and estate geo.xlsx', sheet_name='parameters_monthly')
raw_parameters_monthly_dataframe = file_helpers_parameters_monthly.get_raw_dataframe()
parameters_monthly_dataframe_helpers = DataFrameHelpers(raw_parameters_monthly_dataframe, None)

available_years_list = mill_dataframe_helpers.get_available_levels('Year')
available_months_list = mill_dataframe_helpers.get_available_levels('Month')
available_years_class = mill_dataframe_helpers.get_selector_options_class(available_years_list, available_years_list, is_ascending=False)
available_months_class = mill_dataframe_helpers.get_selector_options_class(available_months_list, mill_dataframe_helpers.month_categories, is_ascending=True)

layout_helpers = FixedLayoutHelpers(dashboard_name)
firstrow_layout = layout_helpers.generate_firstrow_layout(button_class_list=['button', 'button', 'button button-selected'])
secondrow_layout = layout_helpers.generate_secondrow_layout(available_years_class, available_months_class)

layout = html.Div([
    html.Div(
        firstrow_layout, className='row', style={'margin-top':20, 'margin-bottom':20}
    ),
    html.Div(
        secondrow_layout, className='row', style={'margin-bottom':20}
    ),
    html.Div(
        dcc.Graph(id='mill-map', style={'margin-bottom':8}, config={'displayModeBar': False},
                    hoverData={'points': [{'customdata': 'Mill 1'}]}),
                    className='row',
    ),
    html.Div([
        dcc.Graph(id='oer-dollars-barchart-monthly', style={'margin-bottom':8}, className='four columns',
            config={'displayModeBar': False}),
        dcc.Graph(id='ffa-dollars-barchart-monthly', style={'margin-bottom':8}, className='four columns',
            config={'displayModeBar': False}),
        dcc.Graph(id='oil-loss-dollars-barchart-monthly', style={'margin-bottom':8}, className='four columns',
            config={'displayModeBar': False}),
    ], className='row'),
    html.H4('Click on KPI charts or Barchart bars below to drillthrough', style={'text-align': 'center'}),
    html.Div([
        dcc.Graph(id='oer-kpi-donut-card', style={'margin-bottom':8}, className='four columns',
            config={'displayModeBar': False}),
        dcc.Graph(id='ffa-kpi-donut-card', style={'margin-bottom':8}, className='four columns', config={'displayModeBar': False}),
        dcc.Graph(id='oil-loss-kpi-donut-card', style={'margin-bottom':8}, className='four columns', config={'displayModeBar': False}),
    ], className='row'),
    html.Div([
        dcc.Graph(id='screw-barchart-monthly', style={'margin-bottom':8}, className='three columns',
            config={'displayModeBar': False}),
        dcc.Graph(id='sterilizer-barchart-monthly', style={'margin-bottom':8}, className='three columns',
            config={'displayModeBar': False}),
        dcc.Graph(id='sludge-barchart-monthly', style={'margin-bottom':8}, className='three columns',
            config={'displayModeBar': False}),
        dcc.Graph(id='ebpress-barchart-monthly', style={'margin-bottom':8}, className='three columns',
            config={'displayModeBar': False}),
    ], className='row'),
], className='ten columns offset-by-one', style={'margin-bottom':50})


def generate_general_barchart(year, month, hoverData_map, dataframe_helpers_object,
                                color_limits_list, metric_col_name, chart_title, x_axis_colname,
                                filter_info={}, metric_is_pct=False, reverse=False, update_opacity_barname=None):
    mill = get_interaction_element(hoverData_map)

    filter_info['Mill Name'] = mill
    if x_axis_colname != 'Month':
        dataframe = dataframe_helpers_object.filter_dataframe(year, optional_filter_selections=[month], optional_filter_cols=['Month'])
    else:
        dataframe = dataframe_helpers_object.filter_dataframe(year)
    barchart_helpers = BarChartHelpers(
                                dataframe,
                                dataframe.columns
                            )
    barchart_helpers.color_limits_list = color_limits_list
    barchart_helpers.filter_info = filter_info
    barchart_helpers.update_chart_dataframe()
    updated_dataframe = barchart_helpers.dataframe
    if metric_is_pct:
        updated_dataframe[metric_col_name] = updated_dataframe[metric_col_name].map(lambda x: round((x * 100), 2))
    else:
        updated_dataframe[metric_col_name] = round(updated_dataframe[metric_col_name], 2)
    if updated_dataframe[metric_col_name].min() >= 0 and updated_dataframe[metric_col_name].max() >= 0:
        upper_offset = updated_dataframe[metric_col_name].max()*0.10
        lower_offset = updated_dataframe[metric_col_name].max()*0.10
    elif updated_dataframe[metric_col_name].max() < 0:
        upper_offset = abs(updated_dataframe[metric_col_name].max())
        lower_offset = abs(updated_dataframe[metric_col_name].max()*0.10)
    else:
        upper_offset = abs(updated_dataframe[metric_col_name].max()*0.10)
        lower_offset = abs(updated_dataframe[metric_col_name].max()*0.10)
    figure = barchart_helpers.generate_barchart(updated_dataframe[x_axis_colname], updated_dataframe[metric_col_name],
                                                chart_title, [updated_dataframe[metric_col_name].min()-lower_offset,
                                                updated_dataframe[metric_col_name].max()+upper_offset])
    mapped_discrete_colors = barchart_helpers.discrete_color_mapper(updated_dataframe, metric_col_name, reverse)
    updated_dataframe.reset_index(drop=True, inplace=True)
    colors = mapped_discrete_colors
    figure['data'][0].update({
                            'marker': {
                                'color': colors,
                                'line':{
                                    'color':'black',
                                    'width':1.5
                                },
                            }
                        })
    if update_opacity_barname is not None:
        bar_index = updated_dataframe[updated_dataframe[x_axis_colname]==update_opacity_barname].index.values[0]
        opacity = [0.4 for _ in range(updated_dataframe.shape[0])]
        opacity[bar_index] = 1
        figure['data'][0].update({
                                'marker': {
                                    'color': colors,
                                    'line':{
                                        'color':'black',
                                        'width':1.5
                                    },
                                    'opacity': opacity
                                }
                            })
    return figure


def generate_kpi_donut_card(year, month, hoverData_map,
                                color_limits_list, metric_col_name, chart_title,
                                metric_is_pct=False, reverse=False):
    chart_helpers = ChartHelpers()
    mill = get_interaction_element(hoverData_map)
    filter_info = {'Mill Name': mill}
    dataframe = mill_dataframe_helpers.filter_dataframe(year, optional_filter_selections=[month], optional_filter_cols=['Month'])
    chart_helpers.color_limits_list = color_limits_list
    chart_helpers.filter_info = filter_info
    chart_helpers.dataframe = dataframe

    card_dataframe = chart_helpers.dataframe[chart_helpers.dataframe['Mill Name'] == mill]
    if metric_is_pct:
        metric = card_dataframe[metric_col_name].map(lambda x: round((x * 100), 3))
    else:
        metric = round(card_dataframe[metric_col_name], 3)
    kpi_data = metric.values
    mapped_discrete_color = chart_helpers.discrete_color_mapper(card_dataframe, metric_col_name, reverse)
    data = {
            "values": 1,
            "labels": [metric_col_name],
            "hoverinfo": "none",
            'textinfo': "none",
            "marker": {
                "colors": mapped_discrete_color,
                "line": {
                    "color":'#000000',
                    "width": 1.5
                },
            },
            "opacity": 1,
            "hole": 0.5,
            "type": "pie",
            "customdata": [metric_col_name]
            }

    layout = {
        "title": chart_title,
        "showlegend": False,
        'height': 350,
        'margin': {
            'l':35,
            'r':35,
            'b':35,
            't':85
        },
        'plot_bgcolor': "#191A1A",
        'paper_bgcolor': "#020202",
        'font': {'color': '#CCCCCC'},
        'titlefont': {'color': '#CCCCCC', 'size':14},
        "annotations": [
            {
            "font": {
                "size": 24,
                "color": '#CCCCCC'
            },
            "showarrow": False,
            "text": str(kpi_data[0]),
            "x": 0.5,
            "y": 0.5
            }
        ]
    }

    fig = dict(data=[data], layout=layout)
    return fig


@app.callback(
    Output('mill-map', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map', 'hoverData')])
def update_mill_map(year, month, hoverData):
    figure = generate_mill_map(mill_dataframe_helpers, mill_map_helpers, year, month, hoverData)
    return figure


@app.callback(
    Output('oer-dollars-barchart-monthly', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map', 'hoverData')])
def update_oer_dollars_monthly_bar_chart(year, month, hoverData_map):

    figure = generate_general_barchart(year, month, hoverData_map, mill_dataframe_helpers,
                                    [-1500, -500, 500, 1500], 'OER', 'Monthly OER Dollar Value (US$)', 'Month',
                                    filter_info={}, metric_is_pct=False, reverse=False, update_opacity_barname=month)
    return figure


@app.callback(
    Output('ffa-dollars-barchart-monthly', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map', 'hoverData')])
def update_ffa_dollars_monthly_bar_chart(year, month, hoverData_map):

    figure = generate_general_barchart(year, month, hoverData_map, mill_dataframe_helpers,
                                    [-1500, -500, 500, 1500], 'FFA', 'Monthly FFA Dollar Value (US$)', 'Month',
                                    filter_info={}, metric_is_pct=False, reverse=False, update_opacity_barname=month)
    return figure


@app.callback(
    Output('oil-loss-dollars-barchart-monthly', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map', 'hoverData')])
def update_oil_loss_dollars_monthly_bar_chart(year, month, hoverData_map):

    figure = generate_general_barchart(year, month, hoverData_map, mill_dataframe_helpers,
                                    [-1500, -500, 500, 1500], 'Oil Loss', 'Monthly Oil Loss Dollar Value (US$)', 'Month',
                                    filter_info={}, metric_is_pct=False, reverse=False, update_opacity_barname=month)
    return figure


@app.callback(
    Output('oer-kpi-donut-card', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map', 'hoverData')])
def update_oer_kpi_dollars_card(year, month, hoverData_map):

    figure = generate_kpi_donut_card(year, month, hoverData_map,
                                    [-1500, -500, 500, 1500], 'OER vs Baseline',
                                    'Monthly OER vs Baseline Dollar Value (US$)',
                                    metric_is_pct=False, reverse=False)
    return figure


@app.callback(
    Output('ffa-kpi-donut-card', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map', 'hoverData')])
def update_ffa_kpi_dollars_card(year, month, hoverData_map):

    figure = generate_kpi_donut_card(year, month, hoverData_map,
                                    [-1500, -500, 500, 1500], 'FFA vs Baseline',
                                    'Monthly FFA vs Baseline Dollar Value (US$)',
                                    metric_is_pct=False, reverse=False)
    return figure


@app.callback(
    Output('oil-loss-kpi-donut-card', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map', 'hoverData')])
def update_oil_loss_kpi_dollars_card(year, month, hoverData_map):

    figure = generate_kpi_donut_card(year, month, hoverData_map,
                                    [-1500, -500, 500, 1500], 'Oil Loss vs Baseline',
                                    'Monthly Oil Loss vs Baseline Dollar Value (US$)',
                                    metric_is_pct=False, reverse=False)
    return figure


@app.callback(
    Output('screw-barchart-monthly', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map', 'hoverData')])
def update_screw_monthly_bar_chart(year, month, hoverData_map):

    figure = generate_general_barchart(year, month, hoverData_map, parameters_monthly_dataframe_helpers,
                                    [3.9, 4.3, 4.7, 5.1], 'Value', 'Monthly Screw Press Loss (%)', 'Machine',
                                    filter_info={'Machine': ['Screw Press 1', 'Screw Press 2', 'Screw Press 3', 'Screw Press 4',
                                                'Screw Press 5', 'Screw Press 6']},
                                    metric_is_pct=True, reverse=True)
    figure['layout']['margin'].update(dict(b=100, r=60))
    figure['layout']['xaxis'].update(dict(tickangle=35))
    return figure


@app.callback(
    Output('sterilizer-barchart-monthly', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map', 'hoverData')])
def update_sterilizer_monthly_bar_chart(year, month, hoverData_map):

    figure = generate_general_barchart(year, month, hoverData_map, parameters_monthly_dataframe_helpers,
                                    [1.4, 1.8, 2.2, 2.6], 'Value', 'Monthly Sterilizer Loss (%)', 'Machine',
                                    filter_info={'Machine': ['Sterilizer 1', 'Sterilizer 2', 'Sterilizer 3', 'Sterilizer 4']},
                                    metric_is_pct=True, reverse=True)
    figure['layout']['margin'].update(dict(b=100, r=60))
    figure['layout']['xaxis'].update(dict(tickangle=35))
    return figure


@app.callback(
    Output('sludge-barchart-monthly', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map', 'hoverData')])
def update_sludge_monthly_bar_chart(year, month, hoverData_map):

    figure = generate_general_barchart(year, month, hoverData_map, parameters_monthly_dataframe_helpers,
                                    [0.6, 0.7, 0.8, 0.9], 'Value', 'Monthly Sludge Separator Loss (%)', 'Machine',
                                    filter_info={'Machine': ['Sludge Separator 1', 'Sludge Separator 2', 'Sludge Separator 3']},
                                    metric_is_pct=False, reverse=True)
    figure['layout']['margin'].update(dict(b=100, r=60))
    figure['layout']['xaxis'].update(dict(tickangle=35))
    return figure


@app.callback(
    Output('ebpress-barchart-monthly', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map', 'hoverData')])
def update_ebpress_monthly_bar_chart(year, month, hoverData_map):

    figure = generate_general_barchart(year, month, hoverData_map, parameters_monthly_dataframe_helpers,
                                    [1.40, 1.70, 2.00, 2.30], 'Value', 'Monthly EB Press Loss (%)', 'Machine',
                                    filter_info={'Machine': ['Empty Bunch Press 1', 'Empty Bunch Press 2']},
                                    metric_is_pct=True, reverse=True)
    figure['layout']['margin'].update(dict(b=100, r=60))
    figure['layout']['xaxis'].update(dict(tickangle=35))
    return figure


@app.callback(
    Output('mill-screw-clickData', 'children'),
    [Input('screw-barchart-monthly', 'clickData')])
def update_screw_click_data(clickData):
    click_data = get_interaction_element(clickData, key='x')
    data = json.dumps({"Machine": click_data}, indent=4)
    df = pd.DataFrame({"Parameter": [click_data], "Machine": ["Screw Press"]})
    df.to_csv('drillthrough_data.csv', index=None)
    return data


@app.callback(
    Output('mill-sludge-clickData', 'children'),
    [Input('sludge-barchart-monthly', 'clickData')])
def update_sludge_click_data(clickData):
    click_data = get_interaction_element(clickData, key='x')
    data = json.dumps({"Machine": click_data}, indent=4)
    df = pd.DataFrame({"Parameter": [click_data], "Machine": ["Sludge Separator"]})
    df.to_csv('drillthrough_data.csv', index=None)
    return data


@app.callback(
    Output('mill-sterilizer-clickData', 'children'),
    [Input('sterilizer-barchart-monthly', 'clickData')])
def update_sterilizer_click_data(clickData):
    click_data = get_interaction_element(clickData, key='x')
    data = json.dumps({"Machine": click_data}, indent=4)
    df = pd.DataFrame({"Parameter": [click_data], "Machine": ["Sterilizer"]})
    df.to_csv('drillthrough_data.csv', index=None)
    return data


@app.callback(
    Output('mill-ebpress-clickData', 'children'),
    [Input('ebpress-barchart-monthly', 'clickData')])
def update_ebpress_click_data(clickData):
    click_data = get_interaction_element(clickData, key='x')
    data = json.dumps({"Machine": click_data}, indent=4)
    df = pd.DataFrame({"Parameter": [click_data], "Machine": ["Empty Bunch Press"]})
    df.to_csv('drillthrough_data.csv', index=None)
    return data


@app.callback(Output('url', 'pathname'),
              [Input('screw-barchart-monthly', 'clickData'),
              Input('sludge-barchart-monthly', 'clickData'),
              Input('sterilizer-barchart-monthly', 'clickData'),
              Input('ebpress-barchart-monthly', 'clickData'),
              Input('oer-kpi-donut-card', 'clickData'),
              Input('ffa-kpi-donut-card', 'clickData'),
              Input('oil-loss-kpi-donut-card', 'clickData')])
def update_pathname_mill_parameters(screw_clickData, sludge_clickData, sterilizer_clickData,
                                    ebpress_clickData, oer_clickData, ffa_clickData, oil_clickData):
    if screw_clickData is not None:
        return '/mill-screw'
    if sludge_clickData is not None:
        return '/mill-sludge'
    if sterilizer_clickData is not None:
        return '/mill-sterilizer'
    if ebpress_clickData is not None:
        return '/mill-ebpress'
    if oer_clickData is not None:
        return '/mill-oer'
    if ffa_clickData is not None:
        return '/mill-ffa'
    if oil_clickData is not None:
        return '/mill-oil-loss'
    return '/mill'
