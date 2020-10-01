import json

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from helpers import *


dashboard_name = 'Mill Screw Parameters'
sheet_names = ['mill', 'Parameters']

mill_file_helpers_screw = FileHelpers('./data/mill and estate geo.xlsx', sheet_names[0])
file_helpers_screw = FileHelpers('./data/mill parameters for demo.xlsx', sheet_names[1])
raw_screw_dataframe = file_helpers_screw.get_raw_dataframe()
mill_raw_screw_dataframe = mill_file_helpers_screw.get_raw_dataframe()
screw_dataframe_helpers = DataFrameHelpers(raw_screw_dataframe, None)
mill_screw_dataframe_helpers = DataFrameHelpers(mill_raw_screw_dataframe, None)
screw_map_helpers = ChoroplethMapHelpers(None)
screw_dataframe_helpers.dataframe = screw_dataframe_helpers.ordered_categorical_dataframe_column(screw_dataframe_helpers.dataframe, 'Month',
                                                    screw_dataframe_helpers.month_categories, by=['Month', 'Date'], is_ascending=True)
mill_screw_dataframe_helpers.dataframe = mill_screw_dataframe_helpers.ordered_categorical_dataframe_column(mill_screw_dataframe_helpers.dataframe, 'Month',
                                                    mill_screw_dataframe_helpers.month_categories, by=['Month'], is_ascending=True)
available_years_list = mill_screw_dataframe_helpers.get_available_levels('Year')
available_months_list = mill_screw_dataframe_helpers.get_available_levels('Month')
available_years_class = mill_screw_dataframe_helpers.get_selector_options_class(available_years_list, available_years_list, is_ascending=False)
available_months_class = mill_screw_dataframe_helpers.get_selector_options_class(available_months_list,
                                                                mill_screw_dataframe_helpers.month_categories, is_ascending=True)

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
        id='selected-mill-screw', className='row', style={'margin-bottom':20}
    ),
    html.Div(
        dcc.Graph(id='mill-map-screw', style={'margin-bottom':8}, config={'displayModeBar': False},
                    hoverData={'points': [{'customdata': 'Mill 1'}]}),
                    className='row',
    ),
    html.Div([
        dcc.Graph(id='screw-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'Digester Amp'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='screw-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
    html.Div(id='chart-dataframe-screw', style={'display': 'none'})
], className='ten columns offset-by-one', style={'margin-bottom':50})


@app.callback(
    Output('selected-mill-screw', 'children'),
    [Input('mill-screw-clickData', 'children'),
    Input('year-selector', 'value')])
def update_screw_click_data(clickData_json, year):
    selected_screw = pd.read_csv('drillthrough_data.csv')
    return selected_screw['Parameter']


@app.callback(
    Output('mill-map-screw', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-screw', 'hoverData')])
def update_mill_map_screw(year, month, hoverData):
    figure = generate_mill_map(mill_screw_dataframe_helpers, screw_map_helpers, year, month, hoverData)
    return figure


@app.callback(
    Output('chart-dataframe-screw', 'children'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-screw', 'hoverData'),
    Input('selected-mill-screw', 'children')])
def update_chart_dataframe_screw(year, month, hoverData_map, selected_screw):
    interaction_element = get_interaction_element(hoverData_map)
    dataframe = screw_dataframe_helpers.filter_dataframe(year, optional_filter_selections=[month, interaction_element,
                                selected_screw[0]], optional_filter_cols=['Month', 'Mill Name', 'Machine'])
    dataframe = dataframe.pivot(index='Date', columns='Parameter', values='Value').reset_index()
    dataframe = dataframe.reset_index(drop=True).sort_values('Date')
    return dataframe.to_json()


@app.callback(
    Output('screw-heatmap', 'figure'),
    [Input('chart-dataframe-screw', 'children')])
def update_screw_heatmap(chart_dataframe):
    chart_dataframe = pd.read_json(chart_dataframe)
    chart_dataframe_helpers = DataFrameHelpers(chart_dataframe, 'Date')
    chart_dataframe_helpers.add_datetime_attributes(['Year', 'Month', 'Week'])
    chart_dataframe_helpers.map_month_names()
    screw_heatmap_helpers = HeatmapHelpers(
                                chart_dataframe_helpers.dataframe,
                                chart_dataframe_helpers.dataframe.columns
                            )
    weekly_dataframe = screw_heatmap_helpers.generate_weekly_dataframe(chart_dataframe, chart_dataframe_helpers.dataframe)
    figure = screw_heatmap_helpers.generate_heatmap_2(weekly_dataframe,
                    ['Screw Press Tek Hyd', 'Screw Press Amp', 'Screw Press Hour meter', 'Digester Tek steam', 'Digester Suhu', 'Digester Amp'],
                    [[60, 70, 80, 90], [60, 70, 80, 90], [60, 70, 80, 90],
                        [60, 70, 80, 90], [60, 70, 80, 90], [60, 70, 80, 90]],
                    [False, False, False, False, False, False], 'Process Parameter Adherance by Week', metric_is_pct=False)
    figure['layout']['margin'].update(dict(l=180))
    return figure


@app.callback(
    Output('screw-daily-barchart', 'figure'),
    [Input('screw-heatmap', 'hoverData'),
    Input('chart-dataframe-screw', 'children')])
def update_screw_daily_barchart(hoverData_heatmap, chart_dataframe):
    chart_dataframe = pd.read_json(chart_dataframe)
    chart_dataframe_helpers = DataFrameHelpers(chart_dataframe, 'Date')
    chart_dataframe_helpers.add_datetime_attributes(['Year', 'Month', 'Week'])
    chart_dataframe_helpers.map_month_names()
    screw_barchart_helpers = BarChartHelpers(
                                chart_dataframe_helpers.dataframe,
                                chart_dataframe_helpers.dataframe.columns
                            )
    return screw_barchart_helpers.generate_daily_barchart_2(hoverData_heatmap,
                                {'Screw Press Tek Hyd': [60, 70, 80, 90], 'Screw Press Amp': [60, 70, 80, 90],
                                 'Screw Press Hour meter': [60, 70, 80, 90], 'Digester Tek steam': [60, 70, 80, 90],
                                 'Digester Suhu': [60, 70, 80, 90], 'Digester Amp': [60, 70, 80, 90]},
                                {'Screw Press Tek Hyd': False, 'Screw Press Amp': False,
                                 'Screw Press Hour meter': False, 'Digester Tek steam': False,
                                 'Digester Suhu': False, 'Digester Amp': False}, metric_is_pct=False)
