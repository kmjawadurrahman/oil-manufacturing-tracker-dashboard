import json

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from helpers import *


dashboard_name = 'Mill Sludge Separator Parameters'
sheet_names = ['mill', 'Parameters']

mill_file_helpers_sludge = FileHelpers('./data/mill and estate geo.xlsx', sheet_names[0])
file_helpers_sludge = FileHelpers('./data/mill parameters for demo.xlsx', sheet_names[1])
raw_sludge_dataframe = file_helpers_sludge.get_raw_dataframe()
mill_raw_sludge_dataframe = mill_file_helpers_sludge.get_raw_dataframe()
sludge_dataframe_helpers = DataFrameHelpers(raw_sludge_dataframe, None)
mill_sludge_dataframe_helpers = DataFrameHelpers(mill_raw_sludge_dataframe, None)
sludge_map_helpers = ChoroplethMapHelpers(None)
sludge_dataframe_helpers.dataframe = sludge_dataframe_helpers.ordered_categorical_dataframe_column(sludge_dataframe_helpers.dataframe, 'Month',
                                                    sludge_dataframe_helpers.month_categories, by=['Month', 'Date'], is_ascending=True)
mill_sludge_dataframe_helpers.dataframe = mill_sludge_dataframe_helpers.ordered_categorical_dataframe_column(mill_sludge_dataframe_helpers.dataframe, 'Month',
                                                    mill_sludge_dataframe_helpers.month_categories, by=['Month'], is_ascending=True)

available_years_list = mill_sludge_dataframe_helpers.get_available_levels('Year')
available_months_list = mill_sludge_dataframe_helpers.get_available_levels('Month')
available_years_class = mill_sludge_dataframe_helpers.get_selector_options_class(available_years_list, available_years_list, is_ascending=False)
available_months_class = mill_sludge_dataframe_helpers.get_selector_options_class(available_months_list,
                                                        mill_sludge_dataframe_helpers.month_categories, is_ascending=True)

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
    html.H4(
        id='selected-mill-sludge', className='row', style={'margin-bottom':20}
    ),
    html.Div(
        dcc.Graph(id='mill-map-sludge', style={'margin-bottom':8}, config={'displayModeBar': False},
                    hoverData={'points': [{'customdata': 'Mill 1'}]}),
                    className='row',
    ),
    html.Div([
        dcc.Graph(id='sludge-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'Temp CST NO 1'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='sludge-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
    html.Div(id='chart-dataframe-sludge', style={'display': 'none'})
], className='ten columns offset-by-one', style={'margin-bottom':50})


@app.callback(
    Output('selected-mill-sludge', 'children'),
    [Input('mill-sludge-clickData', 'children'),
    Input('year-selector', 'value')])
def update_sludge_click_data(clickData_json, year):
    selected_sludge = pd.read_csv('drillthrough_data.csv')
    return selected_sludge['Parameter']


@app.callback(
    Output('mill-map-sludge', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-sludge', 'hoverData')])
def update_mill_map_sludge(year, month, hoverData):
    figure = generate_mill_map(mill_sludge_dataframe_helpers, sludge_map_helpers, year, month, hoverData)
    return figure


@app.callback(
    Output('chart-dataframe-sludge', 'children'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-sludge', 'hoverData'),
    Input('selected-mill-sludge', 'children')])
def update_chart_dataframe_sludge(year, month, hoverData_map, selected_sludge):
    interaction_element = get_interaction_element(hoverData_map)
    dataframe = sludge_dataframe_helpers.filter_dataframe(year, optional_filter_selections=[month, interaction_element,
                                selected_sludge[0]], optional_filter_cols=['Month', 'Mill Name', 'Machine'])
    dataframe = dataframe.pivot(index='Date', columns='Parameter', values='Value').reset_index()
    dataframe = dataframe.reset_index(drop=True).sort_values('Date')
    return dataframe.to_json()


@app.callback(
    Output('sludge-heatmap', 'figure'),
    [Input('chart-dataframe-sludge', 'children')])
def update_sludge_heatmap(chart_dataframe):
    chart_dataframe = pd.read_json(chart_dataframe)
    chart_dataframe_helpers = DataFrameHelpers(chart_dataframe, 'Date')
    chart_dataframe_helpers.add_datetime_attributes(['Year', 'Month', 'Week'])
    chart_dataframe_helpers.map_month_names()
    sludge_heatmap_helpers = HeatmapHelpers(
                                chart_dataframe_helpers.dataframe,
                                chart_dataframe_helpers.dataframe.columns
                            )
    weekly_dataframe = sludge_heatmap_helpers.generate_weekly_dataframe(chart_dataframe, chart_dataframe_helpers.dataframe)
    figure = sludge_heatmap_helpers.generate_heatmap_2(weekly_dataframe,
                    ['Temp Sludge Tank', 'Temp Hot Water Tank', 'Temp CST NO 2', 'Temp CST NO 1'],
                    [[60, 70, 80, 90], [60, 70, 80, 90], [60, 70, 80, 90],
                        [60, 70, 80, 90]],
                    [False, False, False, False], 'Process Parameter Adherance by Week', metric_is_pct=False)
    figure['layout']['margin'].update(dict(l=180))
    return figure


@app.callback(
    Output('sludge-daily-barchart', 'figure'),
    [Input('sludge-heatmap', 'hoverData'),
    Input('chart-dataframe-sludge', 'children')])
def update_sludge_daily_barchart(hoverData_heatmap, chart_dataframe):
    chart_dataframe = pd.read_json(chart_dataframe)
    chart_dataframe_helpers = DataFrameHelpers(chart_dataframe, 'Date')
    chart_dataframe_helpers.add_datetime_attributes(['Year', 'Month', 'Week'])
    chart_dataframe_helpers.map_month_names()
    sludge_barchart_helpers = BarChartHelpers(
                                chart_dataframe_helpers.dataframe,
                                chart_dataframe_helpers.dataframe.columns
                            )
    return sludge_barchart_helpers.generate_daily_barchart_2(hoverData_heatmap,
                                {'Temp Sludge Tank': [60, 70, 80, 90], 'Temp Hot Water Tank': [60, 70, 80, 90],
                                 'Temp CST NO 2': [60, 70, 80, 90], 'Temp CST NO 1': [60, 70, 80, 90]},
                                {'Temp Sludge Tank': False, 'Temp Hot Water Tank': False,
                                 'Temp CST NO 2': False, 'Temp CST NO 1': False}, metric_is_pct=False)
