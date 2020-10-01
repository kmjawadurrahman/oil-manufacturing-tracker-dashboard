import json

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from helpers import *


dashboard_name = 'Mill EB Press Parameters'
sheet_names = ['mill', 'Parameters']

mill_file_helpers_ebpress = FileHelpers('./data/mill and estate geo.xlsx', sheet_names[0])
file_helpers_ebpress = FileHelpers('./data/mill parameters for demo.xlsx', sheet_names[1])
raw_ebpress_dataframe = file_helpers_ebpress.get_raw_dataframe()
mill_raw_ebpress_dataframe = mill_file_helpers_ebpress.get_raw_dataframe()
ebpress_dataframe_helpers = DataFrameHelpers(raw_ebpress_dataframe, None)
mill_ebpress_dataframe_helpers = DataFrameHelpers(mill_raw_ebpress_dataframe, None)
ebpress_map_helpers = ChoroplethMapHelpers(None)
ebpress_dataframe_helpers.dataframe = ebpress_dataframe_helpers.ordered_categorical_dataframe_column(ebpress_dataframe_helpers.dataframe, 'Month',
                                                    ebpress_dataframe_helpers.month_categories, by=['Month', 'Date'], is_ascending=True)
mill_ebpress_dataframe_helpers.dataframe = mill_ebpress_dataframe_helpers.ordered_categorical_dataframe_column(mill_ebpress_dataframe_helpers.dataframe, 'Month',
                                                    mill_ebpress_dataframe_helpers.month_categories, by=['Month'], is_ascending=True)
available_years_list = mill_ebpress_dataframe_helpers.get_available_levels('Year')
available_months_list = mill_ebpress_dataframe_helpers.get_available_levels('Month')
available_years_class = mill_ebpress_dataframe_helpers.get_selector_options_class(available_years_list, available_years_list, is_ascending=False)
available_months_class = mill_ebpress_dataframe_helpers.get_selector_options_class(available_months_list,
                            mill_ebpress_dataframe_helpers.month_categories, is_ascending=True)

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
        id='selected-mill-ebpress', className='row', style={'margin-bottom':20}
    ),
    html.Div(
        dcc.Graph(id='mill-map-ebpress', style={'margin-bottom':8}, config={'displayModeBar': False},
                    hoverData={'points': [{'customdata': 'Mill 1'}]}),
                    className='row',
    ),
    html.Div([
        dcc.Graph(id='ebpress-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'Empty Bunch Hour meter'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='ebpress-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
    html.Div(id='chart-dataframe-ebpress', style={'display': 'none'})
], className='ten columns offset-by-one', style={'margin-bottom':50})


@app.callback(
    Output('selected-mill-ebpress', 'children'),
    [Input('mill-ebpress-clickData', 'children'),
    Input('year-selector', 'value')])
def update_ebpress_click_data(clickData_json, year):
    selected_ebpress = pd.read_csv('drillthrough_data.csv')
    return selected_ebpress['Parameter']


@app.callback(
    Output('mill-map-ebpress', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ebpress', 'hoverData')])
def update_mill_map_ebpress(year, month, hoverData):
    figure = generate_mill_map(mill_ebpress_dataframe_helpers, ebpress_map_helpers, year, month, hoverData)
    return figure


@app.callback(
    Output('chart-dataframe-ebpress', 'children'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-ebpress', 'hoverData'),
    Input('selected-mill-ebpress', 'children')])
def update_chart_dataframe_ebpress(year, month, hoverData_map, selected_ebpress):
    interaction_element = get_interaction_element(hoverData_map)
    dataframe = ebpress_dataframe_helpers.filter_dataframe(year, optional_filter_selections=[month, interaction_element,
                                selected_ebpress[0]], optional_filter_cols=['Month', 'Mill Name', 'Machine'])
    dataframe = dataframe.pivot(index='Date', columns='Parameter', values='Value').reset_index()
    dataframe = dataframe.reset_index(drop=True).sort_values('Date')
    return dataframe.to_json()


@app.callback(
    Output('ebpress-heatmap', 'figure'),
    [Input('chart-dataframe-ebpress', 'children')])
def update_ebpress_heatmap(chart_dataframe):
    chart_dataframe = pd.read_json(chart_dataframe)
    chart_dataframe_helpers = DataFrameHelpers(chart_dataframe, 'Date')
    chart_dataframe_helpers.add_datetime_attributes(['Year', 'Month', 'Week'])
    chart_dataframe_helpers.map_month_names()
    ebpress_heatmap_helpers = HeatmapHelpers(
                                chart_dataframe_helpers.dataframe,
                                chart_dataframe_helpers.dataframe.columns
                            )
    weekly_dataframe = ebpress_heatmap_helpers.generate_weekly_dataframe(chart_dataframe, chart_dataframe_helpers.dataframe)
    figure = ebpress_heatmap_helpers.generate_heatmap_2(weekly_dataframe,
                    ['Empty Bunch Hour meter'],
                    [[1.40, 1.70, 2.00, 2.30]],
                    [True], 'Process Parameter Adherance by Week', metric_is_pct=False)
    figure['layout']['margin'].update(dict(l=200))
    return figure


@app.callback(
    Output('ebpress-daily-barchart', 'figure'),
    [Input('ebpress-heatmap', 'hoverData'),
    Input('chart-dataframe-ebpress', 'children')])
def update_ebpress_daily_barchart(hoverData_heatmap, chart_dataframe):
    chart_dataframe = pd.read_json(chart_dataframe)
    chart_dataframe_helpers = DataFrameHelpers(chart_dataframe, 'Date')
    chart_dataframe_helpers.add_datetime_attributes(['Year', 'Month', 'Week'])
    chart_dataframe_helpers.map_month_names()
    ebpress_barchart_helpers = BarChartHelpers(
                                chart_dataframe_helpers.dataframe,
                                chart_dataframe_helpers.dataframe.columns
                            )
    return ebpress_barchart_helpers.generate_daily_barchart_2(hoverData_heatmap,
                                {'Empty Bunch Hour meter': [1.40, 1.70, 2.00, 2.30]},
                                {'Empty Bunch Hour meter': True}, metric_is_pct=False)
