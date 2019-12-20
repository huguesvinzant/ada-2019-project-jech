#!/usr/bin/env python
# coding: utf-8

# Imports:
import pandas as pd
import numpy as np
import branca
from matplotlib import rcParams
# figure size in inches
rcParams['figure.figsize'] = 11.7,8.27
import seaborn as sns
import json
import folium
import folium.plugins
from folium.plugins import TimestampedGeoJson
from pathlib import Path
from folium import plugins
from area import area
from folium.plugins import Search

from folium.plugins import HeatMap
from folium.plugins import MiniMap

coords_chicago = [41.8781, -87.6298]

############################################Heatmap##################################################
def heat_map_chicago(data, geo_json_chicago_area):
    '''
    This function enables us to plot the density map of Chicago restaurants using the Heatmap plugin of Folium
    
    Imput:
        data: Pandas Dataframe containing the Latitude and Longitude of the restaurants
        geo_json_chicago_area: GeoJson object containing Chicago boundaries, so we can display the boundaries of the city on the map
    
    Output:
        Folium heatmap representing the density of the restaurants
    '''
    restaurant_density = folium.Map(location=coords_chicago, zoom_start=10) 
    # add the boundaries to the map
    folium.GeoJson(geo_json_chicago_area, style_function=lambda x: {'color': 'grey', 'fillOpacity':0.2}).add_to(restaurant_density)

    # List comprehension to make out list of lists
    heat_data = [[row['Latitude'] ,row['Longitude']] for index, row in data.iterrows()]

    # Plot it on the map
    HeatMap(heat_data, min_opacity=0.1, radius=15, blur=5).add_to(restaurant_density)

    #Minimap
    minimap = MiniMap(toggle_display=True, position='bottomleft')
    restaurant_density.add_child(minimap)

    #Full screen --> Doesn't work on the HTML website
    #plugins.Fullscreen(
    #    position='topright',
    #    title='Expand me',
    #    title_cancel='Exit me',
    #    force_separate_button=True
    #).add_to(restaurant_density)
    return restaurant_density

############################################Time Evolving map########################################
#Function used to had a column color in the dataset, each color corresponding to wether the restaurants pass/pass with condition or failed the inspection
def results_to_color(s):
    '''
    Function creating a column color for our cfi_insp dataset
    
    Imput: 
            s: string containing the results of the inspection
    Output:
            color corresponding to the inspection: red if failed, orange if pass with conditions, green if pass
    '''
    if s=='Fail':
        return 'darkred'
    if s=='Pass':
        return 'orange'
    if s=='Pass w/ Conditions':
        return 'red'

#Note: this code has been inspired by an article written on the website TowardDataScience.

def create_geojson_features(df):
    '''
    This function enables us to create a dict of features, which will be later on used to create the dynamic map
    
    Imput: 
            df: Data set as a Pandas DataFrame
    Output: 
            features: Dictionnary of features
    '''
    features = []
    for _, row in df.iterrows():
        feature = {
            'type': 'Feature',
            'geometry': {
                'type':'Point', 
                'coordinates':[row['Longitude'],row['Latitude']]
            },
            'properties': {
                'time': str(row['Inspection Date'])[0:4] + '/' + str(row['Inspection Date'])[5:7], 
                'popup': '<b>Name: </b>'+ str(row['DBA Name']).lower().capitalize() + '\n'+ '<br><b>Reason of inspection: </b>' + str(row['Inspection Type']),
                'style': {'color' : row['color']},
                'icon': 'circle',
                'iconstyle':{
                    'fillColor': row['color'],
                    'fillOpacity': 1,
                    'stroke': 'False',
                    'radius': 5
                }
            }
        }
        features.append(feature)
    return features

def make_map(features, geo_json_chicago_area, duration=None):
    '''
    This function enables us to create the map, using the features created before.
    
    Imput:
            features: Dictionnary of features
            duration: Time that the point will stay on the map, None by default, meaning that the point will stay 
            forever on the map after having been put (other argument could by 'P1M' for instance, meaning that the 
            point will only stay one period of time)
    Output:
            Folium map containing the restaurants
    '''
    chicago_map = folium.Map(location=coords_chicago, control_scale=True, zoom_start=10)
    
    data = TimestampedGeoJson(
        {'type': 'FeatureCollection',
        'features': features}
        , period='P1M'
        , duration=duration
        , add_last_point=True
        , auto_play=False
        , loop=False
        , max_speed=1
        , loop_button=True
        , date_options='YYYY/MM'
        , time_slider_drag_update=True
    ).add_to(chicago_map)
    
    item_txt = """<br> &nbsp; <i class="fa fa-circle fa-1x" style="color:{col}"></i>  &nbsp;{item} """
    html_itms_1 = item_txt.format(item="Pass", col="orange")
    item_txt = """<br> &nbsp; <i class="fa fa-circle fa-1x" style="color:{col}"></i>  &nbsp;{item} """
    html_itms_2 = item_txt.format(item="Pass w/ conditions", col="red")
    html_itms_3 = item_txt.format(item="Fail", col="darkred")
    
    legend_html = """
         <div style="
         position: fixed; 
         top: 20px; right: 20px; width: 170px; height: 85px; 
         border:2px solid grey; z-index:9999; 

         background-color:white;
         opacity: .85;

         font-size:14px;
         
         ">&nbsp; {title} 
         {itm_txt}
          </div> """.format(title="<b> Inspection results </b>", itm_txt=html_itms_1+html_itms_2+html_itms_3)
    chicago_map.get_root().html.add_child(folium.Element(legend_html))
    folium.GeoJson(geo_json_chicago_area, style_function=lambda x: {'color': 'grey', 'fillOpacity':0.2}).add_to(chicago_map)
    
    return chicago_map

def create_the_map(df, N, duration, geo_json_chicago_area):
    '''
    This function used the previous function to created the features and the map associated with it. Note that, we have
    to take a subsample of our dataset if we used to put a None for the duration, otherwise, the maps becomes too crowded
    and is not readable anymore.
    
    Imput:
            df: Data set as a Pandas DataFrame
            N: Number of samples that we want to take from our dataset
            duration: Time that the point will stay on the map, None by default, meaning that the point will stay 
            forever on the map after having been put (other argument could by 'P1M' for instance, meaning that the 
            point will only stay one period of time)
            geo_json_chicago_area: GeoJson object containing the boundaries of Chicago
    Output:
            Folium map containing the restaurants and their inspection results evolving with time. 
            
    '''
    data = df.sample(N) #Only take a subsample of our dataset to not obtain something too crowded
    features = create_geojson_features(data)
    return make_map(features, geo_json_chicago_area, duration=duration)


###################################################Yelp rating dual map#####################################################
def yelp_to_color(num):
    '''
    This function is used to creat a column containing the color with respect to the Yelp rating
    
    Input:
        num: FLoat number corresponding of the rating (between 1 and 5)
        
    Output:
        String representing the color that will be display using the Folium.Icon attribute
    '''
    if 1<=num and num<2:
        return 'beige'
    if 2<=num and num<3:
        return 'orange'
    if 3<=num and num<4:
        return 'red'
    if 4<=num and num<=5:
        return 'darkred'
    else:
        return 'black'

    
def chicago_dual_map(data, N_top, geo_json_chicago_area):
    '''
    This function is used to plot a dual map of Chicago, with the color of each marker corresponding to the Yelp rating, we marker
    also display other relevant information by clicking on it. Note, on one side of the map, we display the most famous restaurants,
    while on the other we display the less famous ones (using the number of review on Yelp as a proxy for the reputation).
    
    Input:
        data: Pandas Dataframe containing the datas (Latitude, Longitude, Yelp name, Yelp color)
        N_top: Number of restaurants that we want to display
        geo_json_chicago_area: GeoJson object containing the boudaries of Chicago City
        
    Output:
        Folium dual map
    '''

    chicago_dual_map = plugins.DualMap(location=coords_chicago, tiles=None, zoom_start=10)
    folium.GeoJson(geo_json_chicago_area, style_function=lambda x: {'color': 'grey', 'fillOpacity':0.2}).add_to(chicago_dual_map)

    folium.TileLayer('openstreetmap').add_to(chicago_dual_map)

    for i in range(N_top):
        row_1 = data.iloc[i]
        folium.Marker([row_1['Latitude'], row_1['Longitude']], tooltip = row_1['Yelp name'],icon=folium.Icon(color=row_1['Yelp color'], icon='cutlery')).add_to(chicago_dual_map.m1)
        row_2 = data.iloc[data.shape[0]-1-i]
        folium.Marker([row_2['Latitude'], row_2['Longitude']], tooltip = row_2['Yelp name'],icon=folium.Icon(color=row_2['Yelp color'], icon='cutlery')).add_to(chicago_dual_map.m2)


    item_txt = """<i class="fa fa-circle fa-1x" style="color:{col}"></i>  &nbsp;{item} """
    html_itms_1 = item_txt.format(item="Yelp rating < 2", col="#fbf3d4")
    item_txt = """<br> &nbsp; <i class="fa fa-circle fa-1x" style="color:{col}"></i>  &nbsp;{item} """
    html_itms_2 = item_txt.format(item="2 "+"\u2264"+" Yelp rating < 3", col="orange")
    html_itms_3 = item_txt.format(item="3 "+"\u2264"+" Yelp rating < 4", col="red")
    html_itms_4 = item_txt.format(item="4 "+"\u2264"+" Yelp rating", col="darkred")

    legend_html = """
                 <div style="
                 position: fixed; 
                 top: 20px; right: 20px; width: 170px; height: 85px; 
                 border:2px solid grey; z-index:9999; 

                 background-color:white;
                 opacity: .85;

                 font-size:14px;
                 font-weight: bold;
                 ">&nbsp; {itm_txt}
                  </div> """.format(itm_txt=html_itms_1+html_itms_2+html_itms_3+html_itms_4)
    chicago_dual_map.get_root().html.add_child(folium.Element(legend_html))
    return chicago_dual_map

###########################################################Final plot####################################################
def cfi_score_to_color(num, q_25=0, q_50=0, q_75=0):
    '''
    This function is usd to transform the CFI score into colors, we cut them into 4 differents categories using the quantiles
    of the score.
    
    Input:
        num: CFI score as a float between 0 and 10
        q_25: 25% quantile of the CFI score as a float
        q_50: 50% quantile of the CFI score as a float
        q_75: 75% quantile of the CFI score as a float
    
    Output:
        String representing the color that will be display using the Folium.Icon attribute
    '''
    if num<=q_25:
        return 'beige'
    if num<=q_50:
        return 'orange'
    if num <=q_75:
        return 'red'
    return 'darkred'

def final_plot(data, geo_json_chicago_area_crime, list_category, n_areas):
    '''
    This function enables us to generate the final plot of our datastories. This plot is an interactive map, which regroup most of the
    information that has been presented before. Notably, there will be the possibility to choose the food category, to search for a 
    specialy community, to see the crime density in each community. Moreover, it will be possible to choose the Yelp rating. The latter
    will be displayed on the HTML website using a slider to choose the rating that we want.
    
    Input:
        data: Pandas DataFrame containing the datas
        geo_json_chicago_area_crime: GeoJson object containing the areas and the density of crimes in these areas
    
    Output:
        4 Foliums Maps, each one corresponding to some category fo Yelp rating
    '''
    tab = []
    for k in range(2,6):  
        m = folium.Map(location=coords_chicago, zoom_start=10)
        mcg=folium.plugins.MarkerCluster(name=str(k-1) +' <= Yelp rating < ' + str(k), control=False, overlay=True, show=False)
        m.add_child(mcg)
        parent_group = data[data['Yelp rating']>=k-1]

        for j in range(list_category.shape[0]):
            group = parent_group[[list_category[j] in parent_group['Yelp category'].iloc[i] for i in range(parent_group.shape[0])]]
            g = folium.plugins.FeatureGroupSubGroup(
                    mcg, 
                    list_category[j].replace('_',' ').capitalize(), 
                    show=False
                )

            for i in range(group.shape[0]):
                folium.Marker(
                    (group['Latitude'].iloc[i], group['Longitude'].iloc[i]), 
                    tooltip=group['DBA Name'].iloc[i].capitalize(),
                    icon=folium.Icon(color=group['CFI color'].iloc[i], icon='cutlery'), 
                    popup='<b>Yelp rating: </b>'+ str(group['Yelp rating'].iloc[i]) + '<br><b>Food category: </b>' 
                    + list_category[j].replace('_',' ').capitalize()
                ).add_to(g)
            m.add_child(g) 

            #Minimap
            minimap = MiniMap(toggle_display=True, position='bottomleft')
            m.add_child(minimap)

            #Full screem --> Doesn't work on the website
            #plugins.Fullscreen(
            #    position='topright',
            #    title='Expand me',
            #    title_cancel='Exit me',
            #    force_separate_button=True
            #).add_to(m)

        folium.Choropleth(
            geo_data=geo_json_chicago_area_crime,
            name='Community areas (crime density)',
            data=n_areas,
            columns=['code', 'crimes density'],
            key_on='feature.properties.area_num_1',
            fill_color='YlGn',
            fill_opacity=0.7,
            line_opacity=0.5,
            line_color='black',
            legend_name='Density of crimes in 2019 per surface area',
            tooltip=folium.GeoJsonTooltip(
                fields=['community'],
                aliases=['Community:'],
                localize=True)
        ).add_to(m)

        citygeo = folium.GeoJson(
            geo_json_chicago_area_crime,
            show=False,
            name='Community areas names',
            tooltip=folium.GeoJsonTooltip(
                fields=['community'],
                aliases=['Community:'],
                localize=True),
            style_function = lambda x: {
            'fillColor': 'grey',
            'color': 'grey',
            'weight':2,
            'fillOpacity':0.1,
        }
        ).add_to(m)

        citysearch = Search(
            layer=citygeo,
            geom_type='Polygon',
            placeholder='Search for a Community',
            collapsed=True,
            search_label='community'
        ).add_to(m)

        item_txt = """<br> &nbsp; <i class="fa fa-circle fa-1x" style="color:{col}"></i>  &nbsp;{item} """
        html_itms_1 = item_txt.format(item="Poor", col="#fbf3d4")
        item_txt = """<br> &nbsp; <i class="fa fa-circle fa-1x" style="color:{col}"></i>  &nbsp;{item} """
        html_itms_2 = item_txt.format(item="Fair", col="orange")
        html_itms_3 = item_txt.format(item="Good", col="red")
        html_itms_4 = item_txt.format(item="Excellent", col="darkred")

        legend_html = """
                     <div style="
                     position: fixed; 
                     bottom: 20px; right: 20px; width: 170px; height: 105px; 
                     border:2px solid grey; z-index:9999; 

                     background-color:white;
                     opacity: .85;

                     font-size:14px;
                     ">&nbsp; {title} 
                     {itm_txt}
                      </div> """.format(title="<b> Sanitation Standard </b>",itm_txt=html_itms_1+html_itms_2+html_itms_3+html_itms_4)
        m.get_root().html.add_child(folium.Element(legend_html))

        folium.LayerControl(collapsed=True).add_to(m)
        tab.append(m)
    return tab

##################################################Geographical distribution of crimes###########################################
def crime_distribution(geo_json_data, areas, cols):
    '''
    This function is used to display a folium map containing the density of crimes.
    
    Input:
        geo_json_data: GeoJson objects containing the boundaries of the communities
        areas: Pandas DataFrame containing the data for each of the communities
        cols: Columns to use in the Pandas DataFrame
        
    Output:
        Folium map showing the geographical distritbution of crimes
    '''
    m = folium.Map(location=coords_chicago)

    # coloring is using data from a pandas dataframe bound to geojson data through the area code
    folium.Choropleth(
        geo_data=geo_json_data,
        name='choropleth',
        data=areas,
        columns=cols,
        key_on='feature.properties.area_num_1',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Total number of crimes from 2010 to present'
    ).add_to(m)
    folium.LayerControl().add_to(m)
    return m


#################################################Interactive crime map###########################################################
def interactive_crime(n_areas, geo_json_data):
    '''
    This function is used to display a folium map containing the density of crimes. This map is interactive in the sense that it's
    possible to search for a special spatial areas.
    
    Input:
        n_areas: Pandas DataFrame containing the data to display for each communities
        geo_json_data: GeoJson objects containing the boundaries of the communities
        
    Output:
        Interactive Folium map showing the geographical distritbution of crimes
    '''
    crimes_map = folium.Map(location=coords_chicago, zoom_start = 10)

    # coloring is using data from a pandas dataframe bound to geojson data through the area code
    folium.Choropleth(
        geo_data=geo_json_data,
        name='Crime rate in community areas',
        data=n_areas,
        columns=['code', 'crimes density'],
        key_on='feature.properties.area_num_1',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.5,
        line_color='black',
        legend_name='Number of crimes per squarekilometer in 2019',
        tooltip=folium.GeoJsonTooltip(
            fields=['community'],
            aliases=['Community:'],
            localize=True)
    ).add_to(crimes_map)

    citygeo = folium.GeoJson(
        geo_json_data,
        name='Community area names',
        tooltip=folium.GeoJsonTooltip(
            fields=['community'],
            aliases=['Community:'],
            localize=True),
        style_function = lambda x: {
        'fillColor': 'grey',
        'color': 'grey',
        'weight':2,
        'fillOpacity':0.1,
    }
    ).add_to(crimes_map)

    citysearch = Search(
        layer=citygeo,
        geom_type='Polygon',
        placeholder='Search for a Community',
        collapsed=True,
        search_label='community'
    ).add_to(crimes_map)

    minimap = MiniMap(toggle_display=True, position='bottomleft')
    crimes_map.add_child(minimap)
    return crimes_map

################################################Crime density evolving map#############################################################
def create_geojson_crimefeatures(df_areas, df_crimes, colors):
    '''
    This function enables us to create a dict of features, which will be later on used to create the dynamic map
    
    Input: 
            df: Data set as a Pandas DataFrame
    Output: 
            features: Dictionnary of features
    '''
    features = []
    for feat in df_areas:
        code = int(feat['properties']['area_num_1'])
        
        for idx, crime in df_crimes[[code]].iterrows():
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type':'MultiPolygon', 
                    'coordinates': feat['geometry']['coordinates']
                },
                'properties': {
                    'time': str(idx),
                    'style': {'highlight': {},'color' : colors[idx-2010,code-1]},
                }
            }
            features.append(feature)
   
    return features

def make_map_crimes(features, edges, color_scale, duration=None):
    '''
    This function enables us to create the map, using the features created before.
    
    Imput:
            features: Dictionnary of features
            duration: Time that the point will stay on the map, None by default, meaning that the point will stay 
            forever on the map after having been put (other argument could by 'P1M' for instance, meaning that the 
            point will only stay one period of time)
    Output:
            Folium map containing the restaurants
    '''
    chicago_map = folium.Map(location=coords_chicago, control_scale=True, zoom_start=10)
    
    data = TimestampedGeoJson(
        {'type': 'FeatureCollection',
        'features': features}
        , period='P1Y'
        , duration=duration
        , add_last_point=True
        , auto_play=False
        , loop=False
        , max_speed=1
        , min_speed=0.1
        , loop_button=True
        , date_options='YYYY'
        , time_slider_drag_update=True
    ).add_to(chicago_map)
    
    colormap = branca.colormap.LinearColormap(colors=color_scale, vmin=edges[0], vmax=edges[9])
    colormap = colormap.to_step(index=edges)
    colormap.caption = 'Number of crimes per squarekilometer each year'
    colormap.add_to(chicago_map)

    return chicago_map

def create_the_map_crimes(duration, edges, color_scale, geo_json_data, density_grouped, colors):
    '''
    This function used the previous function to created the features and the map associated with it. Note that, we have
    to take a subsample of our dataset if we used to put a None for the duration, otherwise, the maps becomes too crowded
    and is not readable anymore.
    
    Imput:
            df: Data set as a Pandas DataFrame
            N: Number of samples that we want to take from our dataset
            duration: Time that the point will stay on the map, None by default, meaning that the point will stay 
            forever on the map after having been put (other argument could by 'P1M' for instance, meaning that the 
            point will only stay one period of time)
    Output:
            Folium map containing the restaurants   
            
    '''
    df_areas = geo_json_data['features']
    df_crimes = density_grouped
    features = create_geojson_crimefeatures(df_areas, df_crimes, colors)
    return make_map_crimes(features, edges, color_scale, duration)
