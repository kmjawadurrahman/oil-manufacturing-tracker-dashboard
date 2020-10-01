import datetime

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.figure_factory as ff

from helpers import *
from app import app
from . import mill


dashboard_name = 'Overall Summary Dashboard'
sheet_name = 'Tracker OER'
date_colname = 'Date'

file_helpers = FileHelpers('./data/oer data.xlsx', sheet_name)
raw_dashboard_dataframe = file_helpers.get_raw_dataframe()
dataframe_helpers = DataFrameHelpers(raw_dashboard_dataframe, date_colname)
dataframe_helpers.add_datetime_attributes(['Year', 'Month', 'Week'])
dataframe_helpers.map_month_names()
dataframe_helpers.dataframe = dataframe_helpers.ordered_categorical_dataframe_column(dataframe_helpers.dataframe, 'Month',
                                                    dataframe_helpers.month_categories, by=['Month', 'Date'], is_ascending=True)
heatmap_helpers = HeatmapHelpers(
                            dataframe_helpers.dataframe,
                            dataframe_helpers.dataframe.columns
                        )
barchart_helpers = BarChartHelpers(
                            dataframe_helpers.dataframe,
                            dataframe_helpers.dataframe.columns
                        )
available_years_list = dataframe_helpers.get_available_levels('Year')
available_months_list = dataframe_helpers.get_available_levels('Month')
available_years_class = dataframe_helpers.get_selector_options_class(available_years_list, available_years_list, is_ascending=False)
available_months_class = dataframe_helpers.get_selector_options_class(available_months_list, dataframe_helpers.month_categories, is_ascending=True)

layout_helpers = FixedLayoutHelpers(dashboard_name)
firstrow_layout = layout_helpers.generate_firstrow_layout(button_class_list=['button button-selected', 'button', 'button'])
secondrow_layout = layout_helpers.generate_secondrow_layout(available_years_class, available_months_class)

estate_count_file_helpers = FileHelpers('./data/country estates.xlsx')
raw_estate_count_dataframe = estate_count_file_helpers.get_raw_dataframe()
estate_count_dataframe_helpers = DataFrameHelpers(raw_estate_count_dataframe, 'Date')
map_data_url = 'https://gist.githubusercontent.com/kmjawadurrahman/20fcdf21c1ebac7e2e6ae15488101b3b/raw/0299ba6492eff4ec46ebb422e2022e5a6f5aeab8/countries.json'
choropleth_country_map_helpers = ChoroplethMapHelpers(map_data_url)
choropleth_country_map_helpers.load_map_data()
country_map_available_property_items = ['Indonesia', 'Malaysia', 'Papua New Guinea', 'Liberia']
country_map_name_mapper_dict = {'Indonesia': 'Indonesia',
                    'Malaysia': 'Malaysia',
                    'Papua New Guinea': 'Papua New Guinea',
                    'Liberia': 'Liberia'}
country_map_property = 'name'
filtered_map_data = choropleth_country_map_helpers.filter_and_init_map_data(country_map_available_property_items, country_map_name_mapper_dict, country_map_property)
country_name_list = choropleth_country_map_helpers.get_property_items_list(country_map_available_property_items, country_map_name_mapper_dict, country_map_property)

layout = html.Div([
    html.Div(
        firstrow_layout, className='row', style={'margin-top':20, 'margin-bottom':20}
    ),
    html.Div(
        secondrow_layout, className='row', style={'margin-bottom':20}
    ),
    html.Div(
        dcc.Graph(id='choropleth-country-map', config={'displayModeBar': False},
                    style={'margin-bottom':8}, hoverData={'points': [{'customdata': 'Indonesia'}]}),
                    className='row',
    ),
    html.Div([
        dcc.Graph(id='summary-heatmap', style={'margin-bottom':8}, className='six columns',
            hoverData={'points': [{'x': '2019-08-26 -', 'y': 'CPO Product Price'}]}, config={'displayModeBar': False}),
        dcc.Graph(id='metric-daily-barchart', style={'margin-bottom':8}, className='six columns', config={'displayModeBar': False}),
    ], className='row'),
], className='ten columns offset-by-one', style={'margin-bottom':50})


@app.callback(
    Output('choropleth-country-map', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('choropleth-country-map', 'hoverData')])
def update_choropleth_country_map(year, month, hoverData):
    estate_count_dataframe = estate_count_dataframe_helpers.filter_dataframe(year, optional_filter_selections=[month], optional_filter_cols=['Month'])
    country_map_mapped_continuous_colors = choropleth_country_map_helpers.continuous_color_mapper(estate_count_dataframe, 'Number of Estates', 0.0, 1.01, False)
    colors_dict = dict()

    for country, color in zip(country_map_available_property_items, country_map_mapped_continuous_colors):
        colors_dict[country]=color

    choropleth_country_map_helpers.colors_dict = colors_dict
    country_text = list()

    for country_name in country_name_list:
        estate_count_country_rows = estate_count_dataframe[estate_count_dataframe.Country==country_name]
        country_text.append('Country: ' + estate_count_country_rows['Country'].tolist()[0] + '<br>' + 'No. of Estates: ' + str(estate_count_country_rows['Number of Estates'].tolist()[0]))

    choropleth_country_map_helpers.text = country_text
    choropleth_country_map_helpers.name = country_name_list

    try:
        pointIndex = hoverData['points'][0]['pointIndex']
    except:
        pointIndex = 0

    colors = ['rgb(255,255,255)' for x in range(len(choropleth_country_map_helpers.text))]
    colors[pointIndex] = 'rgb(255,0,0)'
    figure = choropleth_country_map_helpers.generate_map_figure('No. of Estates per Country', -0.038794, 70.538079, 2)
    figure['data'][0]['marker'].update({'color': colors})
    return figure


@app.callback(
    Output('summary-heatmap', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('choropleth-country-map', 'hoverData')])
def update_summary_heatmap(year, month, hoverData_map):
    return heatmap_helpers.generate_heatmap(dataframe_helpers, year, month,
                    {'Factory': hoverData_map},
                    ['Palm Oil Yield', 'RTF OER', 'CPO Product Price'],
                    [[10, 11, 12, 13], [19, 20, 21, 22], [2.45, 2.55, 2.65, 2.75]],
                    [False, False, False], 'Summary Heatmap', metric_is_pct=False)


@app.callback(
    Output('metric-daily-barchart', 'figure'),
    [Input('year-selector', 'value'),
    Input('month-selector', 'value'),
    Input('choropleth-country-map', 'hoverData'),
    Input('summary-heatmap', 'hoverData')])
def update_metric_daily_barchart(year, month, hoverData_map, hoverData_heatmap):
    return barchart_helpers.generate_daily_barchart(dataframe_helpers, year, month,
                                {'Factory': hoverData_map}, hoverData_heatmap,
                                {'Palm Oil Yield': [10, 11, 12, 13], 'RTF OER': [19, 20, 21, 22],
                                'CPO Product Price': [2.45, 2.55, 2.65, 2.75]},
                                {'Palm Oil Yield': False, 'RTF OER': False, 'CPO Product Price': False},
                                metric_is_pct=False)
