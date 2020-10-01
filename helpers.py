from datetime import datetime, timedelta
import json
import requests
import datetime
from ast import literal_eval

import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.figure_factory as ff


class FixedLayoutHelpers:
    def __init__(self, dashboard_name):
        self.dashboard_name = dashboard_name

    def generate_firstrow_layout(self, button_class_list=[''], button_name_list=['Overall', 'Estates', 'Mills'], href_list = [ '/', '/estate', '/mill']):
        firstrow_layout = list()
        button_name_list = button_name_list
        href_list = href_list
        firstrow_layout.append(html.Img(
            src="https://www.stackreate.com/wp-content/uploads/2020/04/Stackreate-Small-200px.png",
            className='two columns',
                style={
                    'width': 100,
                    'float': 'right',
                    'padding-top': 10,
                    'padding-right': 0
                }
            )
        )
        for button_name, href, button_class in zip(button_name_list, href_list, button_class_list):
            firstrow_layout.append(self.generate_nav_button(button_name, href, button_class))
        return firstrow_layout

    def generate_nav_button(self, button_name, href, button_class):
        nav_button = html.A(html.Button(button_name, className='two columns ' + button_class,
            style={'margin-right':20, 'padding':0, 'white-space': 'normal', 'line-height': 15}),
            href=href)
        return nav_button

    def generate_secondrow_layout(self, available_years_class, available_months_class):
        secondrow_layout = [
            html.H3(
                self.dashboard_name,
                style={
                    'font-family': 'Helvetica',
                    "margin-top": "15",
                    "margin-bottom": "15"
                },
                className='seven columns',
            ),
            html.Div(
            [
                html.P('Year:', style={'fontSize': 16}),
                dcc.Dropdown(
                    id='year-selector',
                    options=available_years_class,
                    multi=False,
                    clearable=False,
                    value=available_years_class[0]['value']
                )
            ],
            className='two columns',
            style={'margin-top': '10',
                    'float': 'right'}
            ),
            html.Div(
                [
                    html.P('Month:', style={'fontSize': 16}),
                    dcc.Dropdown(
                        id='month-selector',
                        options=available_months_class,
                        multi=False,
                        clearable=False,
                        value='September'
                    )
                ],
                className='two columns',
                style={'margin-top': '10',
                        'float': 'right'}
            ),
        ]
        return secondrow_layout


class FileHelpers:
    def __init__(self, relative_path_filename, sheet_name='Sheet1'):
        self.relative_path_filename = relative_path_filename
        self.sheet_name = sheet_name

    def get_raw_dataframe(self):
        raw_dataframe = pd.read_excel(self.relative_path_filename, sheet_name=self.sheet_name)
        return raw_dataframe


class DataFrameHelpers:
    def __init__(self, dataframe, date_colname=None):
        self.dataframe = dataframe
        self.date_colname = date_colname
        self.month_categories = ["January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"]
        self.month_map = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                    7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

    def get_available_levels(self, colname):
        available_levels = self.dataframe[colname].unique()
        return available_levels

    def ordered_categorical_options(self, available_items, categories, is_ascending=True):
        categorical_options = pd.Categorical(available_items, categories=categories, ordered=True)
        categorical_options.sort_values(inplace=True, ascending=is_ascending)
        return categorical_options

    def ordered_categorical_dataframe_column(self, dataframe, colname, categories, by=None, is_ascending=True):
        dataframe[colname] = pd.Categorical(dataframe[colname], categories=categories, ordered=True)
        dataframe.sort_values(by, inplace=True, ascending=is_ascending)
        return dataframe

    def add_datetime_attributes(self, attribute_list):
        if 'Year' in attribute_list and 'Year' not in self.dataframe.columns:
            self.dataframe['Year'] = self.dataframe[self.date_colname].apply(lambda x: x.year)
        if 'Month' in attribute_list and 'Month' not in self.dataframe.columns:
            self.dataframe['Month'] = self.dataframe[self.date_colname].apply(lambda x: x.month)
        if 'Day' in attribute_list and 'Day' not in self.dataframe.columns:
            self.dataframe['Day'] = self.dataframe[self.date_colname].apply(lambda x: x.day)
        if 'Weekday' in attribute_list and 'Weekday' not in self.dataframe.columns:
            self.dataframe['Weekday'] = self.dataframe[self.date_colname].apply(lambda x: x.weekday())
        if 'Yearday' in attribute_list and 'Yearday' not in self.dataframe.columns:
            self.dataframe['Yearday'] = self.dataframe[self.date_colname].apply(lambda x: x.tm_yday)
        if 'Week' in attribute_list and 'Week' not in self.dataframe.columns:
            self.dataframe['Week'] = self.dataframe[self.date_colname].apply(lambda x: x.isocalendar()[1])
        if 'Hour' in attribute_list and 'Hour' not in self.dataframe.columns:
            self.dataframe['Hour'] = self.dataframe[self.date_colname].apply(lambda x: x.hour)
        if 'Minute' in attribute_list and 'Minute' not in self.dataframe.columns:
            self.dataframe['Minute'] = self.dataframe[self.date_colname].apply(lambda x: x.minute)
        if 'Second' in attribute_list and 'Second' not in self.dataframe.columns:
            self.dataframe['Second'] = self.dataframe[self.date_colname].apply(lambda x: x.second)

    def map_month_names(self):
        self.dataframe['Month'] = self.dataframe.Month.map(self.month_map)

    def get_selector_options_class(self, available_items_list, items_categories, is_ascending=True):
        selector_items = self.ordered_categorical_options(available_items_list, items_categories, is_ascending=is_ascending)
        selector_options_class = [{'label': str(item), 'value': item}
                            for item in selector_items]
        return selector_options_class

    def filter_dataframe(self, year, optional_filter_selections=[], optional_filter_cols=[]):
        dff = self.dataframe[self.dataframe['Year'] == year]

        if optional_filter_cols:
            for idx, filter_col in enumerate(optional_filter_cols):
                if filter_col == 'Month' and 'Date' in dff.columns:
                    dff['Week'] = dff['Date'].apply(lambda x: x.isocalendar()[1])
                    dff_month = dff[dff[filter_col] == optional_filter_selections[idx]]
                    weeks_in_month = dff_month['Week'].unique()
                    dff = dff[dff['Week'].isin(weeks_in_month)]
                else:
                    dff = dff[dff[filter_col] == optional_filter_selections[idx]]

        return dff


class ChartHelpers:
    def __init__(self, dataframe=pd.DataFrame(), columns_list=list(), color_limits_list=list(), filter_info=dict()):
        self.performance_colors = ['rgb(215,25,28)',
                                     'rgb(253,174,97)',
                                     'rgb(255,255,191)',
                                     'rgb(166,217,106)',
                                     'rgb(26,150,65)']
        self.dataframe = dataframe
        self.columns_list = columns_list
        self.color_limits_list = color_limits_list
        self.filter_info = filter_info

    def update_chart_dataframe(self):
        if len(self.filter_info) > 0:
            for col_name, level_name in self.filter_info.items():
                if type(level_name) == type(list()):
                    self.dataframe = self.dataframe[self.dataframe[col_name].isin(level_name)]
                else:
                    self.dataframe = self.dataframe[self.dataframe[col_name]==level_name]
        self.dataframe = self.dataframe[self.columns_list]

    def eval_continuous_color_for_val(self, val, plotly_scale_list, colors01, vmin, vmax):
        if vmin>=vmax:
            raise ValueError('vmin should be < vmax')
        v = (val - vmin) / float((vmax - vmin))
        idx = 0
        while(v > plotly_scale_list[idx+1]):
            idx+=1
        left_scale_val = plotly_scale_list[idx]
        right_scale_val = plotly_scale_list[idx+1]
        vv = (v-left_scale_val) / (right_scale_val-left_scale_val)

        val_color01 = colors01[idx] + vv*(colors01[idx+1] - colors01[idx])
        val_color_0255 = list(map(np.uint8, 255*val_color01+0.5))
        return 'rgb'+str(tuple(val_color_0255))

    def continuous_color_mapper(self, dataframe, column_name, colors01_min, colors01_max, reverse=False):
        rate = dataframe[column_name].tolist()
        zmin=min(rate)
        zmax=max(rate)
        if reverse:
            performance_colors = self.performance_colors[::-1]
        else:
            performance_colors = self.performance_colors

        pl_colorscale = [[color01, performance_color] for color01, performance_color \
                            in zip(np.arange(colors01_min, colors01_max, 0.25), performance_colors)]

        pl_scale, pl_colors = map(float, np.array(pl_colorscale)[:,0]), np.array(pl_colorscale)[:,1]
        pl_scale_list = list(pl_scale)
        colors01 = np.array(list(map(literal_eval, [color[3:] for color in pl_colors])))/255.0

        mapped_continuous_colors = [self.eval_continuous_color_for_val(r, pl_scale_list, colors01, zmin, zmax) for r in rate]
        return mapped_continuous_colors

    def discrete_color_mapper(self, dataframe, column_name, reverse=False):
        values_list = dataframe[column_name].tolist()
        mapped_discrete_colors = list()
        if reverse:
            performance_colors = self.performance_colors[::-1]
        else:
            performance_colors = self.performance_colors

        for value in values_list:
            if value is not None:
                if value < self.color_limits_list[0]:
                    mapped_discrete_colors.append(performance_colors[0])
                elif self.color_limits_list[0] <= value < self.color_limits_list[1]:
                    mapped_discrete_colors.append(performance_colors[1])
                elif self.color_limits_list[1] <= value < self.color_limits_list[2]:
                    mapped_discrete_colors.append(performance_colors[2])
                elif self.color_limits_list[2] <= value < self.color_limits_list[3]:
                    mapped_discrete_colors.append(performance_colors[3])
                else:
                    mapped_discrete_colors.append(performance_colors[4])
            else:
                mapped_discrete_colors.append(None)
        return mapped_discrete_colors

    def generate_weekly_dataframe(self, dataframe, dataframe_raw, location_filter_info=None):
        if location_filter_info is not None:
            for location_colname, location_name in location_filter_info.items():
                if location_colname in dataframe.columns and location_colname in dataframe_raw.columns:
                    dataframe_raw = dataframe_raw[dataframe_raw[location_colname] == location_name]
                    dataframe = dataframe[dataframe[location_colname] == location_name]
        weekly_dates_dataframe = dataframe.groupby('Week', as_index=False)['Date'].min()
        first_day_of_month = weekly_dates_dataframe['Date'].min()
        first_week_of_month = weekly_dates_dataframe['Week'].min()
        if first_day_of_month.weekday() != 0:
            weekly_dates_dataframe = weekly_dates_dataframe[weekly_dates_dataframe['Week'] != first_week_of_month]
        weekly_dataframe = dataframe_raw.merge(weekly_dates_dataframe, on=['Date'], suffixes=('_',''))
        if type('Week') == type(" "):
            weekly_dataframe.drop('{}_'.format('Week'), axis=1, inplace=True)
        weekly_dataframe = weekly_dataframe.reset_index(drop=True).sort_values('Date')
        return weekly_dataframe

    def generate_daily_dataframe(self, dataframe, start_date):
        daily_date_dataframe = pd.DataFrame()
        daily_date_dataframe['Date'] = pd.Series(pd.date_range(start=start_date, end=start_date+timedelta(7), closed='left')).reset_index(drop=True)
        daily_dataframe = dataframe.merge(daily_date_dataframe, on='Date', suffixes=('_',''))
        return daily_dataframe


class BarChartHelpers(ChartHelpers):
    def __init__(self, dataframe, columns_list):
        super().__init__(dataframe, columns_list)

    def generate_barchart(self, xdata, ydata, title, yaxis_range_list):
        x = xdata
        y = ydata

        data = {
                    'type':'bar',
                    'x':x,
                    'y':y,
                    'text':y,
                    'textposition':'auto',
                    'textfont':{
                        'color':'black',
                        'size':14
                    },
                    'marker':{
                        'color':['rgb(158,202,225)' for x in range(len(x))],
                        'opacity': 1,
                        },
                    'mode':'markers',
                    'hoverinfo':'x+text',
                    'customdata':x
                }
        layout = dict(
            title=title,
            margin=dict(
                l=50,
                r=35,
                b=35,
                t=85
            ),
            plot_bgcolor="#191A1A",
            paper_bgcolor="#020202",
            font=dict(color='#CCCCCC'),
            titlefont=dict(color='#CCCCCC', size='14'),
            yaxis=dict(
                range=[yaxis_range_list[0], yaxis_range_list[1]]
            ),
            xaxis=dict(
                autorange=True
            ),
        )
        fig = dict(data=[data], layout=layout)
        return fig

    def generate_daily_barchart(self, dataframe_helpers, year, month, hoverData_map_dict, hoverData_heatmap,
                                color_limits_list_dict, reverse_dict, filter_info={}, metric_is_pct=False, chart_title_append = ''):
        location_filter_info=dict()
        if len(filter_info) > 0:
            self.filter_info = filter_info
            self.update_chart_dataframe()
        dataframe = self.dataframe
        for location_colname, hoverData_map in hoverData_map_dict.items():
            location_name = get_interaction_element(hoverData_map)
            if location_colname in dataframe.columns:
                dataframe = dataframe[dataframe[location_colname] == location_name]
        start_date = get_interaction_element(hoverData_heatmap, key='x')
        metric_col_name = get_interaction_element(hoverData_heatmap, key='y')
        self.color_limits_list = color_limits_list_dict[metric_col_name]
        start_date_str = start_date
        start_date = datetime.datetime.strptime(start_date[:-2], '%Y-%m-%d')
        daily_dataframe = self.generate_daily_dataframe(dataframe, start_date)
        reverse = reverse_dict[metric_col_name]
        if metric_is_pct:
            daily_dataframe[metric_col_name] = daily_dataframe[metric_col_name].map(lambda x: round((x * 100), 3))
        else:
            daily_dataframe[metric_col_name] = round(daily_dataframe[metric_col_name], 3)
        if daily_dataframe[metric_col_name].min() >= 0 and daily_dataframe[metric_col_name].max() >= 0:
            upper_offset = daily_dataframe[metric_col_name].max()*0.10
            lower_offset = daily_dataframe[metric_col_name].max()*0.10
        elif daily_dataframe[metric_col_name].max() < 0:
            upper_offset = abs(daily_dataframe[metric_col_name].max())
            lower_offset = abs(daily_dataframe[metric_col_name].max()*0.10)
        else:
            upper_offset = abs(daily_dataframe[metric_col_name].max()*0.10)
            lower_offset = abs(daily_dataframe[metric_col_name].max()*0.10)
        offset = daily_dataframe[metric_col_name].max()*0.10
        chart_title = 'Daily ' + metric_col_name + chart_title_append + ' for week starting ' + start_date_str
        figure = self.generate_barchart(daily_dataframe['Date'], daily_dataframe[metric_col_name], chart_title,
                                                    [daily_dataframe[metric_col_name].min()-lower_offset,
                                                    daily_dataframe[metric_col_name].max()+upper_offset])
        mapped_discrete_colors = self.discrete_color_mapper(daily_dataframe, metric_col_name, reverse)
        colors = mapped_discrete_colors
        figure['data'][0].update({
                                'marker': {
                                    'color': mapped_discrete_colors,
                                    'line':{
                                        'color':'black',
                                        'width':1.5,
                                    }
                                }
                            })
        return figure

    def generate_daily_barchart_2(self, hoverData_heatmap, color_limits_list_dict, reverse_dict,
                                    metric_is_pct=False, chart_title_append = ''):
        start_date = get_interaction_element(hoverData_heatmap, key='x')
        metric_col_name = get_interaction_element(hoverData_heatmap, key='y')
        self.color_limits_list = color_limits_list_dict[metric_col_name]
        start_date_str = start_date
        start_date = datetime.datetime.strptime(start_date[:-2], '%Y-%m-%d')
        daily_dataframe = self.generate_daily_dataframe(self.dataframe, start_date)
        reverse = reverse_dict[metric_col_name]
        if metric_is_pct:
            daily_dataframe[metric_col_name] = daily_dataframe[metric_col_name].map(lambda x: round((x * 100), 3))
        else:
            daily_dataframe[metric_col_name] = round(daily_dataframe[metric_col_name], 3)
        if daily_dataframe[metric_col_name].min() >= 0 and daily_dataframe[metric_col_name].max() >= 0:
            upper_offset = daily_dataframe[metric_col_name].max()*0.10
            lower_offset = daily_dataframe[metric_col_name].max()*0.10
        elif daily_dataframe[metric_col_name].max() < 0:
            upper_offset = abs(daily_dataframe[metric_col_name].max())
            lower_offset = abs(daily_dataframe[metric_col_name].max()*0.10)
        else:
            upper_offset = abs(daily_dataframe[metric_col_name].max()*0.10)
            lower_offset = abs(daily_dataframe[metric_col_name].max()*0.10)
        offset = daily_dataframe[metric_col_name].max()*0.10
        chart_title = 'Daily ' + metric_col_name + chart_title_append + ' for week starting ' + start_date_str
        figure = self.generate_barchart(daily_dataframe['Date'], daily_dataframe[metric_col_name], chart_title,
                                                    [daily_dataframe[metric_col_name].min()-lower_offset,
                                                    daily_dataframe[metric_col_name].max()+upper_offset])
        mapped_discrete_colors = self.discrete_color_mapper(daily_dataframe, metric_col_name, reverse)
        colors = mapped_discrete_colors
        figure['data'][0].update({
                                'marker': {
                                    'color': mapped_discrete_colors,
                                    'line':{
                                        'color':'black',
                                        'width':1.5,
                                    }
                                }
                            })
        return figure


class ChoroplethMapHelpers(ChartHelpers):
    mapbox_token = 'pk.eyJ1IjoiamF3YWR1ciIsImEiOiJjampneHNpcXkzY3FyM3ZtbXJ3b2cxbm9xIn0.ibU3pycC_lqVtRtLCCX_qg'

    def __init__(self, map_data_url):
        super().__init__()
        self.map_data_url = map_data_url
        self.lons = list()
        self.lats = list()
        self.text = ''
        self.sources = list()
        self.colors_dict = dict()
        self.raw_map_data = dict()
        self.name = list()

    def load_map_data(self):
        self.raw_map_data = requests.get(self.map_data_url)
        self.raw_map_data = json.loads(self.raw_map_data.text)

    def filter_and_init_map_data(self, available_property_items, name_mapper_dict, property):
        map_data_list = [row for row in self.raw_map_data['features'] if row['properties'][property] in available_property_items]
        for idx, row in enumerate(map_data_list):
            map_data_list[idx]['properties'][property] = self.map_property_items(row, name_mapper_dict, property)
        map_data_json_dump = json.dumps({"type":"FeatureCollection", "features": map_data_list})
        filtered_map_data = json.loads(map_data_json_dump)

        for k in range(len(filtered_map_data['features'])):
            try:
                country_coords=np.array(filtered_map_data['features'][k]['geometry']['coordinates'][0])
                if len(country_coords.shape) == 3:
                    m, M =country_coords[:,:,0].min(), country_coords[:,:,0].max()
                    self.lons.append(0.5*(m+M))
                    m, M =country_coords[:,:,1].min(), country_coords[:,:,1].max()
                    self.lats.append(0.5*(m+M))
                else:
                    m, M =country_coords[:,0].min(), country_coords[:,0].max()
                    self.lons.append(0.5*(m+M))
                    m, M =country_coords[:,1].min(), country_coords[:,1].max()
                    self.lats.append(0.5*(m+M))
            except Exception as e:
                self.lons.append(np.nan)
                self.lats.append(np.nan)

        for feat in filtered_map_data['features']:
            self.sources.append({"type": "FeatureCollection", 'features': [feat]})
        return filtered_map_data

    def map_property_items(self, map_data_row, name_mapper_dict, property):
        mapped_property_item = name_mapper_dict[map_data_row['properties'][property]]
        return mapped_property_item

    def get_property_items_list(self, available_property_items, name_mapper_dict, property):
        property_items_list = [self.map_property_items(row, name_mapper_dict, property) \
                            for row in self.raw_map_data['features'] if row['properties'][property] in available_property_items]
        return property_items_list

    def generate_hover_text_field(self, filtered_map_data, properties_list):
        text_item_list = list()
        for property in properties_list:
            text_item_list.append([self.raw_map_data['features'][k]['properties'][property] for k in range(len(self.raw_map_data['features']))\
                        if self.raw_map_data['features'][k]['properties'][property] in filtered_map_data['features'][k]['properties'][property]])

        return text_item_list

    def generate_map_figure(self, title, lat, lon, zoom, layers=True):
        data = dict(type='scattermapbox',
            lat = self.lats,
            lon = self.lons,
            mode = 'markers',
            text = self.text,
            customdata = self.name,
            marker = dict(size=10, color='white', opacity = 1, symbol='circle'),
            showlegend = False,
            hoverlabel = dict(bgcolor=[self.colors_dict[name] for name in self.name]),
            hoverinfo = 'text'
        )
        if not layers:
            layers = dict()
        else:
            layers=[dict(sourcetype = 'geojson',
                source = self.sources[k],
                below = "water",
                type = 'fill',
                color = self.colors_dict[self.sources[k]['features'][0]['properties']['name']],
                opacity = 1
            ) for k in range(len(self.text))]
        layout = dict(title=title,
            plot_bgcolor="#191A1A",
            paper_bgcolor="#020202",
            font=dict(color='#CCCCCC'),
            titlefont=dict(color='#CCCCCC', size='14'),
            margin=dict(
                l=35,
                r=35,
                b=35,
                t=85
            ),
            autosize=False,
            hovermode='closest',
            text=self.text,
            mapbox=dict(accesstoken=ChoroplethMapHelpers.mapbox_token,
                style='dark',
                layers=layers,
                bearing=0,
                center=dict(
                    lat = lat,
                    lon = lon),
                pitch=0,
                zoom=zoom
            )
        )
        fig = dict(data=[data], layout=layout)
        return fig


class HeatmapHelpers(ChartHelpers):
    def __init__(self, dataframe, columns_list):
        super().__init__(dataframe, columns_list)

    def heatmap_discrete_color_mapper(self, dataframe, column_name, color_limits_list, reverse):
        values_list = dataframe[column_name].tolist()
        mapped_discrete_colors = list()
        if reverse:
            performance_colors = self.performance_colors[::-1]
        else:
            performance_colors = self.performance_colors

        for value in values_list:
            if value is not None:
                if value < color_limits_list[0]:
                    mapped_discrete_colors.append(performance_colors[0])
                elif color_limits_list[0] <= value < color_limits_list[1]:
                    mapped_discrete_colors.append(performance_colors[1])
                elif color_limits_list[1] <= value < color_limits_list[2]:
                    mapped_discrete_colors.append(performance_colors[2])
                elif color_limits_list[2] <= value < color_limits_list[3]:
                    mapped_discrete_colors.append(performance_colors[3])
                else:
                    mapped_discrete_colors.append(performance_colors[4])
            else:
                mapped_discrete_colors.append(None)
        return mapped_discrete_colors

    def generate_heatmap(self, dataframe_helpers, year, month, hoverData_map_dict, metric_col_names_list, color_limits_lol,
                            reverse_bool_list, chart_title, metric_is_pct=False, filter_info=None):
        location_filter_info = dict()
        for location_colname, hoverData_map in hoverData_map_dict.items():
            location = get_interaction_element(hoverData_map)
            location_filter_info[location_colname] = location
        dataframe = dataframe_helpers.filter_dataframe(year, [month], optional_filter_cols=['Month'])
        weekly_dataframe = self.generate_weekly_dataframe(dataframe, dataframe_helpers.dataframe, location_filter_info=location_filter_info)
        colorscale = [[0.0, 'rgb(215,25,28)'], [0.24999, 'rgb(215,25,28)'], [0.25, 'rgb(253,174,97)'],
                        [0.49999, 'rgb(253,174,97)'], [0.5, 'rgb(255,255,191)'],
                        [0.74999, 'rgb(255,255,191)'], [0.75, 'rgb(166,217,106)'], [0.9999, 'rgb(166,217,106)'], [1.0, 'rgb(26,150,65)']]
        colorscale_dict = {'rgb(215,25,28)': 0.0, 'rgb(253,174,97)': 0.25, 'rgb(255,255,191)': 0.5, 'rgb(166,217,106)': 0.75, 'rgb(26,150,65)': 1.0}
        font_colors = ['black', 'black']
        if 'Metric' in weekly_dataframe.columns:
            weekly_dataframe = weekly_dataframe[['Date', 'Metric'] + metric_col_names_list]
            weekly_dataframe = weekly_dataframe[weekly_dataframe['Metric'] == filter_info['Metric']]
        else:
            weekly_dataframe = weekly_dataframe[['Date'] + metric_col_names_list]
        weekly_dataframe['Date'] = weekly_dataframe['Date'].map(lambda x: x.strftime('%Y-%m-%d') + ' -')
        x = weekly_dataframe['Date'].values.tolist()
        y = metric_col_names_list

        weekly_dataframe = weekly_dataframe[metric_col_names_list]
        if metric_is_pct:
            weekly_dataframe = weekly_dataframe.apply(lambda x: round((x * 100), 3))
        else:
            weekly_dataframe = weekly_dataframe.apply(lambda x: round(x, 3))
        z_orig = (weekly_dataframe.values.T).tolist()
        z_mapped = list()
        for idx, colname in enumerate(metric_col_names_list):
            mapped_discrete_colors = self.heatmap_discrete_color_mapper(weekly_dataframe, colname,
                                            color_limits_lol[idx], reverse_bool_list[idx])
            z_mapped.append([colorscale_dict[color] for color in mapped_discrete_colors])

        annotation_text = z_orig
        text = z_orig
        fig = ff.create_annotated_heatmap(z=z_mapped, x=x, y=y, annotation_text=annotation_text, colorscale=colorscale,
                                            font_colors=font_colors, text=text, hoverinfo='text', zmin = 0.0, zmax = 1.0)

        fig['layout'].update({'margin': {'l': 135, 'r': 35, 'b': 35, 't': 85}, 'title': chart_title,
                                'plot_bgcolor': "#191A1A", 'paper_bgcolor': "#020202", 'font': {'color': '#CCCCCC'},
                                'titlefont': {'color': '#CCCCCC', 'size':14}, 'xaxis': {'tickangle': 10}})
        return fig

    def generate_heatmap_2(self, weekly_dataframe, metric_col_names_list, color_limits_lol,
                            reverse_bool_list, chart_title, metric_is_pct=False):
        colorscale = [[0.0, 'rgb(215,25,28)'], [0.24999, 'rgb(215,25,28)'], [0.25, 'rgb(253,174,97)'],
                        [0.49999, 'rgb(253,174,97)'], [0.5, 'rgb(255,255,191)'],
                        [0.74999, 'rgb(255,255,191)'], [0.75, 'rgb(166,217,106)'], [0.9999, 'rgb(166,217,106)'], [1.0, 'rgb(26,150,65)']]
        colorscale_dict = {'rgb(215,25,28)': 0.0, 'rgb(253,174,97)': 0.25, 'rgb(255,255,191)': 0.5, 'rgb(166,217,106)': 0.75, 'rgb(26,150,65)': 1.0}
        font_colors = ['black', 'black']
        weekly_dataframe = weekly_dataframe[['Date'] + metric_col_names_list]
        weekly_dataframe['Date'] = weekly_dataframe['Date'].map(lambda x: x.strftime('%Y-%m-%d') + ' -')
        x = weekly_dataframe['Date'].values.tolist()
        y = metric_col_names_list

        weekly_dataframe = weekly_dataframe[metric_col_names_list]
        if metric_is_pct:
            weekly_dataframe = weekly_dataframe.apply(lambda x: round((x * 100), 3))
        else:
            weekly_dataframe = weekly_dataframe.apply(lambda x: round(x, 3))
        z_orig = (weekly_dataframe.values.T).tolist()
        z_mapped = list()
        for idx, colname in enumerate(metric_col_names_list):
            mapped_discrete_colors = self.heatmap_discrete_color_mapper(weekly_dataframe, colname,
                                            color_limits_lol[idx], reverse_bool_list[idx])
            z_mapped.append([colorscale_dict[color] for color in mapped_discrete_colors])

        annotation_text = z_orig
        text = z_orig
        fig = ff.create_annotated_heatmap(z=z_mapped, x=x, y=y, annotation_text=annotation_text, colorscale=colorscale,
                                            font_colors=font_colors, text=text, hoverinfo='text', zmin = 0.0, zmax = 1.0)

        fig['layout'].update({'margin': {'l': 135, 'r': 35, 'b': 35, 't': 85}, 'title': chart_title,
                                'plot_bgcolor': "#191A1A", 'paper_bgcolor': "#020202", 'font': {'color': '#CCCCCC'},
                                'titlefont': {'color': '#CCCCCC', 'size':14}, 'xaxis': {'tickangle': 10}})
        return fig


def get_interaction_element(interaction_data, key='customdata'):
    if interaction_data is not None:
        try:
            interaction_element = interaction_data['points'][0][key]
        except Exception as e:
            print(e)
            interaction_element = None
    else:
        interaction_element = None
    return interaction_element


def generate_mill_map(func_dataframe_helpers, func_mill_map_helpers, year, month, hoverData):
    mill_dataframe = func_dataframe_helpers.filter_dataframe(year, optional_filter_selections=[month], optional_filter_cols=['Month'])
    mill_dollar_value_mapped_continuous_colors = func_mill_map_helpers.continuous_color_mapper(mill_dataframe, 'Total Dollar Value', 0.0, 1.01, False)
    colors_dict = dict()

    for mill, color in zip(mill_dataframe['Mill Name'].tolist(), mill_dollar_value_mapped_continuous_colors):
        colors_dict[mill]=color

    func_mill_map_helpers.colors_dict = colors_dict
    func_mill_map_helpers.lats = mill_dataframe['Latitude']
    func_mill_map_helpers.lons = mill_dataframe['Longitude']

    mill_dataframe['Total Dollar Value'] = round(mill_dataframe['Total Dollar Value'], 3)
    mill_dataframe['Text'] = 'Mill Name: ' + mill_dataframe['Mill Name'] + ',<br>Total Dollar Value: US$ '\
                                + mill_dataframe['Total Dollar Value'].astype(str)

    func_mill_map_helpers.text = mill_dataframe['Text'].tolist()
    func_mill_map_helpers.name = mill_dataframe['Mill Name'].tolist()

    try:
        pointIndex = hoverData['points'][0]['pointIndex']
    except:
        pointIndex = 0

    colors = mill_dollar_value_mapped_continuous_colors
    opacity = [0.3 for _ in range(mill_dataframe.shape[0])]
    opacity[pointIndex] = 1
    figure = func_mill_map_helpers.generate_map_figure('Total Dollar Value by Mill', -2.419167, 116.164167, 11, False)
    figure['data'][0]['marker'].update({
                                'color': colors,
                                'opacity': opacity,
                                'size': 35
                                })
    return figure
