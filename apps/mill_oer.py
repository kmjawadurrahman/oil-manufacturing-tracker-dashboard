import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from helpers import *


dashboard_name = 'Mill OER Metrics Dashboard'
sheet_names = ['mill', 'OER']

file_helpers_mill = FileHelpers('./data/mill and estate geo.xlsx', sheet_names[0])
file_helpers_oer = FileHelpers('./data/mill parameters for demo.xlsx', sheet_names[1])
raw_mill_dataframe = file_helpers_mill.get_raw_dataframe()
raw_oer_dataframe = file_helpers_oer.get_raw_dataframe()
mill_oer_dataframe_helpers = DataFrameHelpers(raw_mill_dataframe, None)
oer_dataframe_helpers = DataFrameHelpers(raw_oer_dataframe, None)
mill_oer_map_helpers = ChoroplethMapHelpers(None)
mill_oer_dataframe_helpers.dataframe = mill_oer_dataframe_helpers.ordered_categorical_dataframe_column(mill_oer_dataframe_helpers.dataframe, 'Month',
                                                    mill_oer_dataframe_helpers.month_categories, by=['Month'], is_ascending=True)
oer_dataframe_helpers.dataframe = oer_dataframe_helpers.ordered_categorical_dataframe_column(oer_dataframe_helpers.dataframe, 'Month',
                                                    oer_dataframe_helpers.month_categories, by=['Month', 'Date'], is_ascending=True)
oer_heatmap_helpers = HeatmapHelpers(
                            oer_dataframe_helpers.dataframe,
                            oer_dataframe_helpers.dataframe.columns
                        )
oer_barchart_helpers = BarChartHelpers(
                            oer_dataframe_helpers.dataframe,
                            oer_dataframe_helpers.dataframe.columns
                        )
available_years_list = mill_oer_dataframe_helpers.get_available_levels('Year')
available_months_list = mill_oer_dataframe_helpers.get_available_levels('Month')
available_years_class = mill_oer_dataframe_helpers.get_selector_options_class(available_years_list, available_years_list, is_ascending=False)
available_months_class = mill_oer_dataframe_helpers.get_selector_options_class(available_months_list, mill_oer_dataframe_helpers.month_categories, is_ascending=True)

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
        dcc.Graph(id='mill-map-oer', style={'margin-bottom':8}, config={'displayModeBar': False},
                    hoverData={'points': [{'customdata': 'Mill 1'}]}),
                    className='row',
    ),
    html.Div([
        dcc.Graph(id='mill-oer-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'Ripe (%)'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='mill-oer-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
], className='ten columns offset-by-one', style={'margin-bottom':50})


@app.callback(
    Output('mill-map-oer', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-oer', 'hoverData')])
def update_mill_map_oer(year, month, hoverData):
    figure = generate_mill_map(mill_oer_dataframe_helpers, mill_oer_map_helpers, year, month, hoverData)
    return figure


@app.callback(
    Output('mill-oer-heatmap', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-oer', 'hoverData')])
def update_oer_heatmap(year, month, hoverData_map):
    return oer_heatmap_helpers.generate_heatmap(oer_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                    ['Empty Bunch (%)', 'Underipe (%)', 'Unripe (%)', 'Ripe (%)'],
                    [[0.5, 1.2, 2.7, 4], [0.5, 1.2, 2.7, 4], [0.5, 1.2, 2.7, 4], [94, 95, 96, 97]],
                    [True, True, True, False], 'OER Heatmap', metric_is_pct=False)


@app.callback(
    Output('mill-oer-daily-barchart', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-oer', 'hoverData'),
    Input('mill-oer-heatmap', 'hoverData')])
def update_oer_daily_barchart(year, month, hoverData_map, hoverData_heatmap):
    return oer_barchart_helpers.generate_daily_barchart(oer_dataframe_helpers, year, month, {'Mill Name': hoverData_map},
                                hoverData_heatmap, {'Empty Bunch (%)': [0.5, 1.2, 2.7, 4], 'Underipe (%)': [0.5, 1.2, 2.7, 4],
                                'Unripe (%)': [0.5, 1.2, 2.7, 4], 'Ripe (%)': [94, 95, 96, 97]},
                                {'Empty Bunch (%)': True, 'Underipe (%)': True, 'Unripe (%)': True, 'Ripe (%)': False},
                                metric_is_pct=False)
