import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.figure_factory as ff
import datetime

from helpers import *
from . import mill
from app import app


regions = {
    'Estate 5': {'lat': -2.481378, 'lon': 116.035222, 'zoom': 12},
    'Estate 7': {'lat': -2.403444, 'lon': 116.182133, 'zoom': 12},
    'Estate 4': {'lat': -2.490556, 'lon': 116.25155, 'zoom': 15},
    'Estate 6': {'lat': -2.474289, 'lon': 116.101633, 'zoom': 15},
    'Estate 2': {'lat': -2.523572, 'lon': 116.158122, 'zoom': 15},
    'Estate 1': {'lat': -2.501944, 'lon': 116.135556, 'zoom': 15},
    'Estate 3': {'lat': -2.524822, 'lon': 116.207278, 'zoom': 14},
    'Estate 8': {'lat': -2.387611, 'lon': 116.109611, 'zoom': 12},
}

dashboard_name = 'Estate Dashboard'
sheet_names = ['estate', 'division']

file_helpers_estate = FileHelpers('./data/mill and estate geo.xlsx', sheet_names[0])
file_helpers_division = FileHelpers('./data/mill and estate geo.xlsx', sheet_names[1])
file_helpers_ripeness = FileHelpers('./data/oer data.xlsx', sheet_name='OER')
raw_estate_dataframe = file_helpers_estate.get_raw_dataframe()
raw_division_dataframe = file_helpers_division.get_raw_dataframe()
raw_ripeness_dataframe = file_helpers_ripeness.get_raw_dataframe()

estate_dataframe_helpers = DataFrameHelpers(raw_estate_dataframe, None)
division_dataframe_helpers = DataFrameHelpers(raw_division_dataframe, None)
ripeness_dataframe_helpers = DataFrameHelpers(raw_ripeness_dataframe, 'Date')

ripeness_dataframe_helpers.add_datetime_attributes(['Year', 'Month', 'Week'])
ripeness_dataframe_helpers.map_month_names()
ripeness_dataframe_helpers.dataframe = ripeness_dataframe_helpers.ordered_categorical_dataframe_column(ripeness_dataframe_helpers.dataframe, 'Month',
                                                    ripeness_dataframe_helpers.month_categories, by=['Month', 'Date'], is_ascending=True)
ripeness_heatmap_helpers = HeatmapHelpers(
                            ripeness_dataframe_helpers.dataframe,
                            ripeness_dataframe_helpers.dataframe.columns
                        )
ripeness_barchart_helpers = BarChartHelpers(
                            ripeness_dataframe_helpers.dataframe,
                            ripeness_dataframe_helpers.dataframe.columns
                        )
available_years_list = estate_dataframe_helpers.get_available_levels('Year')
available_months_list = estate_dataframe_helpers.get_available_levels('Month')
available_years_class = estate_dataframe_helpers.get_selector_options_class(available_years_list, available_years_list, is_ascending=False)
available_months_class = estate_dataframe_helpers.get_selector_options_class(available_months_list, estate_dataframe_helpers.month_categories, is_ascending=True)

layout_helpers = FixedLayoutHelpers(dashboard_name)
firstrow_layout = layout_helpers.generate_firstrow_layout(button_class_list=['button', 'button button-selected', 'button'])
secondrow_layout = layout_helpers.generate_secondrow_layout(available_years_class, available_months_class)

estate_map_helpers = ChoroplethMapHelpers(None)
division_map_helpers = ChoroplethMapHelpers(None)

layout = html.Div([
    html.Div(
        firstrow_layout, className='row', style={'margin-top':20, 'margin-bottom':20}
    ),
    html.Div(
        secondrow_layout, className='row', style={'margin-bottom':20}
    ),
    html.Div([
        dcc.Graph(id='estate-map', style={'margin-bottom':8}, className='six columns',
                    config={'displayModeBar': False}, hoverData={'points': [{'customdata': 'Estate 5'}]}),
        dcc.Graph(id='division-map', style={'margin-bottom':8}, className='six columns',
                    config={'displayModeBar': False}, hoverData={'points': [{'customdata': 'I'}]})

    ], className='row'),
    html.Div([
        dcc.Graph(id='ripeness-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'Ripe (%)'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='ripeness-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
], className='ten columns offset-by-one', style={'margin-bottom':50})


@app.callback(
    Output('estate-map', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('estate-map', 'hoverData')])
def update_estate_map(year, month, hoverData):
    estate_ripeness_dataframe = estate_dataframe_helpers.filter_dataframe(year, optional_filter_selections=[month], optional_filter_cols=['Month'])
    estate_ripeness_mapped_continuous_colors = estate_map_helpers.continuous_color_mapper(estate_ripeness_dataframe, 'Ripeness', 0.0, 1.01, False)
    colors_dict = dict()

    for estate, color in zip(estate_ripeness_dataframe['Estate Name'].tolist(), estate_ripeness_mapped_continuous_colors):
        colors_dict[estate]=color

    estate_map_helpers.colors_dict = colors_dict
    estate_map_helpers.lats = estate_ripeness_dataframe['Latitude']
    estate_map_helpers.lons = estate_ripeness_dataframe['Longitude']

    estate_ripeness_dataframe['Ripeness'] = round(estate_ripeness_dataframe['Ripeness'] * 100, 3)
    estate_ripeness_dataframe['Text'] = 'Estate Name: ' + estate_ripeness_dataframe['Estate Name'] + ',<br>Ripeness: ' + estate_ripeness_dataframe['Ripeness'].astype(str) + '%'

    estate_map_helpers.text = estate_ripeness_dataframe['Text'].tolist()
    estate_map_helpers.name = estate_ripeness_dataframe['Estate Name'].tolist()

    try:
        pointIndex = hoverData['points'][0]['pointIndex']
    except:
        pointIndex = 4

    colors = estate_ripeness_mapped_continuous_colors
    opacity = [0.3 for _ in range(estate_ripeness_dataframe.shape[0])]
    opacity[pointIndex] = 1
    figure = estate_map_helpers.generate_map_figure('Ripeness by Estate', -2.460138, 116.151923, 10.5, False)
    figure['data'][0]['marker'].update({
                                'color': colors,
                                'opacity': opacity,
                                'size': 25
                                })
    return figure


@app.callback(
    Output('division-map', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('estate-map', 'hoverData'),
    Input('division-map', 'hoverData')])
def update_division_map(year, month, hoverData_estate, hoverData_division):
    if hoverData_estate is not None:
        try:
            estate = hoverData_estate['points'][0]['customdata']
        except Exception as e:
            print(e)
            return None
    filter_info = {'Estate Name': estate}
    division_ripeness_dataframe = division_dataframe_helpers.filter_dataframe(year, optional_filter_selections=[month, estate], optional_filter_cols=['Month', 'Estate Name'])
    division_ripeness_mapped_continuous_colors = division_map_helpers.continuous_color_mapper(division_ripeness_dataframe, 'Ripeness', 0.0, 1.01, False)
    colors_dict = dict()
    for division, color in zip(division_ripeness_dataframe['Division Name'].tolist(), division_ripeness_mapped_continuous_colors):
        colors_dict[division]=color

    division_map_helpers.colors_dict = colors_dict
    division_map_helpers.lats = division_ripeness_dataframe['Latitude']
    division_map_helpers.lons = division_ripeness_dataframe['Longitude']
    division_ripeness_dataframe['Ripeness'] = round(division_ripeness_dataframe['Ripeness'] * 100, 3)
    division_ripeness_dataframe['Text'] = 'Division: ' + division_ripeness_dataframe['Division Name'] + ',<br>Estate Name: ' + division_ripeness_dataframe['Estate Name'] + ',<br>Ripeness: ' + division_ripeness_dataframe['Ripeness'].astype(str) + '%'

    division_map_helpers.text = division_ripeness_dataframe['Text'].tolist()
    division_map_helpers.name = division_ripeness_dataframe['Division Name'].tolist()

    try:
        pointIndex = hoverData_division['points'][0]['pointIndex']
        if hoverData_division['points'][0]['customdata'] not in division_map_helpers.name:
            hoverData_division['points'][0]['customdata'] = 'I'
            pointIndex = 0
    except:
        pointIndex = 0

    colors = division_ripeness_mapped_continuous_colors
    opacity = [0.4 for _ in range(division_ripeness_dataframe.shape[0])]
    opacity[pointIndex] = 1

    figure = division_map_helpers.generate_map_figure('Ripeness by Division', regions[estate]['lat'],  regions[estate]['lon'], regions[estate]['zoom'], False)
    figure['data'][0]['marker'].update({
                                'color': colors,
                                'opacity': opacity,
                                'size': 25
                                })
    return figure


@app.callback(
    Output('ripeness-heatmap', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('estate-map', 'hoverData'),
    Input('division-map', 'hoverData')])
def update_ripeness_heatmap(year, month, hoverData_map, hoverData_map_division):
    return ripeness_heatmap_helpers.generate_heatmap(ripeness_dataframe_helpers, year, month,
                    {'Estate': hoverData_map, 'Division': hoverData_map_division},
                    ['Empty Bunch (%)', 'Underipe (%)', 'Unripe (%)', 'Ripe (%)'],
                    [[0.5, 1.2, 2.7, 4], [0.5, 1.2, 2.7, 4], [0.5, 1.2, 2.7, 4], [94, 95, 96, 97]],
                    [True, True, True, False], 'Ripeness Heatmap', metric_is_pct=True)


@app.callback(
    Output('ripeness-daily-barchart', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('estate-map', 'hoverData'),
    Input('division-map', 'hoverData'),
    Input('ripeness-heatmap', 'hoverData')])
def update_ripeness_daily_barchart(year, month, hoverData_map, hoverData_map_division, hoverData_heatmap):
    return ripeness_barchart_helpers.generate_daily_barchart(ripeness_dataframe_helpers, year, month, {'Estate': hoverData_map, 'Division': hoverData_map_division},
                                hoverData_heatmap, {'Empty Bunch (%)': [0.5, 1.2, 2.7, 4], 'Underipe (%)': [0.5, 1.2, 2.7, 4],
                                'Unripe (%)': [0.5, 1.2, 2.7, 4], 'Ripe (%)': [94, 95, 96, 97]},
                                {'Empty Bunch (%)': True, 'Underipe (%)': True, 'Unripe (%)': True, 'Ripe (%)': False},
                                metric_is_pct=True)
