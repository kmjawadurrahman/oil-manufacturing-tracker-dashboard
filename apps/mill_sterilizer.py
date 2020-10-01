import json

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from helpers import *


dashboard_name = 'Mill Sterilizer Parameters'
sheet_names = ['mill', 'Parameters']

mill_file_helpers_sterilizer = FileHelpers('./data/mill and estate geo.xlsx', sheet_names[0])
file_helpers_sterilizer = FileHelpers('./data/mill parameters for demo.xlsx', sheet_names[1])
raw_sterilizer_dataframe = file_helpers_sterilizer.get_raw_dataframe()
mill_raw_sterilizer_dataframe = mill_file_helpers_sterilizer.get_raw_dataframe()
sterilizer_dataframe_helpers = DataFrameHelpers(raw_sterilizer_dataframe, None)
mill_sterilizer_dataframe_helpers = DataFrameHelpers(mill_raw_sterilizer_dataframe, None)
sterilizer_map_helpers = ChoroplethMapHelpers(None)
sterilizer_dataframe_helpers.dataframe = sterilizer_dataframe_helpers.ordered_categorical_dataframe_column(sterilizer_dataframe_helpers.dataframe, 'Month',
                                                    sterilizer_dataframe_helpers.month_categories, by=['Month', 'Date'], is_ascending=True)
mill_sterilizer_dataframe_helpers.dataframe = mill_sterilizer_dataframe_helpers.ordered_categorical_dataframe_column(mill_sterilizer_dataframe_helpers.dataframe,
                                                'Month', mill_sterilizer_dataframe_helpers.month_categories, by=['Month'], is_ascending=True)

available_years_list = mill_sterilizer_dataframe_helpers.get_available_levels('Year')
available_months_list = mill_sterilizer_dataframe_helpers.get_available_levels('Month')
available_years_class = mill_sterilizer_dataframe_helpers.get_selector_options_class(available_years_list, available_years_list, is_ascending=False)
available_months_class = mill_sterilizer_dataframe_helpers.get_selector_options_class(available_months_list,
                            mill_sterilizer_dataframe_helpers.month_categories, is_ascending=True)

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
        id='selected-mill-sterilizer', className='row', style={'margin-bottom':20}
    ),
    html.Div(
        dcc.Graph(id='mill-map-sterilizer', style={'margin-bottom':8}, config={'displayModeBar': False},
                    hoverData={'points': [{'customdata': 'Mill 1'}]}),
                    className='row',
    ),
    html.Div([
        dcc.Graph(id='sterilizer-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'Pressure Peak 1'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='sterilizer-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
    html.Div(id='chart-dataframe-sterilizer', style={'display': 'none'})
], className='ten columns offset-by-one', style={'margin-bottom':50})


@app.callback(
    Output('selected-mill-sterilizer', 'children'),
    [Input('mill-sterilizer-clickData', 'children'),
    Input('year-selector', 'value')])
def update_sterilizer_click_data(clickData_json, year):
    selected_sterilizer = pd.read_csv('drillthrough_data.csv')
    return selected_sterilizer['Parameter']


@app.callback(
    Output('mill-map-sterilizer', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-sterilizer', 'hoverData')])
def update_mill_map_sterilizer(year, month, hoverData):
    figure = generate_mill_map(mill_sterilizer_dataframe_helpers, sterilizer_map_helpers, year, month, hoverData)
    return figure


@app.callback(
    Output('chart-dataframe-sterilizer', 'children'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('mill-map-sterilizer', 'hoverData'),
    Input('selected-mill-sterilizer', 'children')])
def update_chart_dataframe_sterilizer(year, month, hoverData_map, selected_sterilizer):
    interaction_element = get_interaction_element(hoverData_map)
    dataframe = sterilizer_dataframe_helpers.filter_dataframe(year, optional_filter_selections=[month, interaction_element,
                                selected_sterilizer[0]], optional_filter_cols=['Month', 'Mill Name', 'Machine'])
    dataframe = dataframe.pivot(index='Date', columns='Parameter', values='Value').reset_index()
    dataframe = dataframe.reset_index(drop=True).sort_values('Date')
    return dataframe.to_json()


@app.callback(
    Output('sterilizer-heatmap', 'figure'),
    [Input('chart-dataframe-sterilizer', 'children')])
def update_sterilizer_heatmap(chart_dataframe):
    chart_dataframe = pd.read_json(chart_dataframe)
    chart_dataframe_helpers = DataFrameHelpers(chart_dataframe, 'Date')
    chart_dataframe_helpers.add_datetime_attributes(['Year', 'Month', 'Week'])
    chart_dataframe_helpers.map_month_names()
    sterilizer_heatmap_helpers = HeatmapHelpers(
                                chart_dataframe_helpers.dataframe,
                                chart_dataframe_helpers.dataframe.columns
                            )
    weekly_dataframe = sterilizer_heatmap_helpers.generate_weekly_dataframe(chart_dataframe, chart_dataframe_helpers.dataframe)
    figure = sterilizer_heatmap_helpers.generate_heatmap_2(weekly_dataframe,
                    ['Sterilizer Hour meter', 'Waktu Pindah (Menit)', 'Waktu Operasi (Menit)', 'Pressure Peak 3', 'Pressure Peak 2', 'Pressure Peak 1'],
                    [[1.4, 1.8, 2.2, 2.6], [1.4, 1.8, 2.2, 2.6], [1.4, 1.8, 2.2, 2.6],
                        [1.4, 1.8, 2.2, 2.6], [1.4, 1.8, 2.2, 2.6], [1.4, 1.8, 2.2, 2.6]],
                    [True, True, True, True, True, True], 'Process Parameter Adherance by Week', metric_is_pct=False)
    figure['layout']['margin'].update(dict(l=180))
    return figure


@app.callback(
    Output('sterilizer-daily-barchart', 'figure'),
    [Input('sterilizer-heatmap', 'hoverData'),
    Input('chart-dataframe-sterilizer', 'children')])
def update_sterilizer_daily_barchart(hoverData_heatmap, chart_dataframe):
    chart_dataframe = pd.read_json(chart_dataframe)
    chart_dataframe_helpers = DataFrameHelpers(chart_dataframe, 'Date')
    chart_dataframe_helpers.add_datetime_attributes(['Year', 'Month', 'Week'])
    chart_dataframe_helpers.map_month_names()
    sterilizer_barchart_helpers = BarChartHelpers(
                                chart_dataframe_helpers.dataframe,
                                chart_dataframe_helpers.dataframe.columns
                            )
    return sterilizer_barchart_helpers.generate_daily_barchart_2(hoverData_heatmap,
                                {'Sterilizer Hour meter': [1.4, 1.8, 2.2, 2.6], 'Waktu Pindah (Menit)': [1.4, 1.8, 2.2, 2.6],
                                 'Waktu Operasi (Menit)': [1.4, 1.8, 2.2, 2.6], 'Pressure Peak 3': [1.4, 1.8, 2.2, 2.6],
                                 'Pressure Peak 2': [1.4, 1.8, 2.2, 2.6], 'Pressure Peak 1': [1.4, 1.8, 2.2, 2.6]},
                                {'Sterilizer Hour meter': True, 'Waktu Pindah (Menit)': True,
                                 'Waktu Operasi (Menit)': True, 'Pressure Peak 3': True,
                                 'Pressure Peak 2': True, 'Pressure Peak 1': True}, metric_is_pct=False)
