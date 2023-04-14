#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import numpy as np

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

get_ipython().system('pip install geopy  ')
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

get_ipython().system('pip install matplotlib')
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.style.use('ggplot')

get_ipython().system('pip install folium')
import folium # plotting library
from folium import plugins
from folium.plugins import MarkerCluster
from folium.plugins import FastMarkerCluster
from folium.plugins import HeatMap

import branca
import branca.colormap as cm

get_ipython().system('pip install geojson')
import geojson

import math


# # 1. Plots Fahrgastzahlen

# ## 1.1 Import

# In[2]:


# working directory anpassen
print(os.getcwd())
user = '/Users/' + os.getlogin()
os.chdir(user + '/Dropbox/Projekt Scripting/01 data')
print(os.getcwd())


# In[3]:


# File importieren
df_fahr=pd.read_csv('./df_fahrgastzahlen_geo.csv')
df_fahr.head(3)


# In[4]:


df_fahr=df_fahr.sort_values('einsteiger', ascending=False)
df_fahr.head(3)


# In[5]:


df_fahr=df_fahr.sort_values('aussteiger', ascending=False)
df_fahr.head(3)


# In[6]:


df_fahr_bewegung=df_fahr.sort_values('traffic_total', ascending=False)
df_fahr_bewegung.head(3)


# In[7]:


df_fahr_bewegung_min=df_fahr.sort_values('traffic_total', ascending=True)
df_fahr_bewegung.head(3)


# ##  1.2 Plots - Linienbelastung und Haltestellen Traffic

# In[8]:


#Endstationen rausfiltern
df_fahr_mind=df_fahr[df_fahr.einsteiger > 0]


# In[9]:


#Anfangsstationen rausfiltern
df_fahr_mind_aus=df_fahr[df_fahr.aussteiger > 0]


# In[10]:


#Linienname as int
df_fahr['linienname'] = df_fahr['linienname'].astype(int)


# ### Linienbelastung

# In[11]:


#Linien mit der geringsten Besetzung
(df_fahr.groupby('linienname').mean().reset_index().sort_values('belastung')
 .head(10).plot(kind='barh', figsize=(12,3), x='linienname', y='belastung'))

plt.title('Linien mit der geringsten Auslastung') 
plt.show()


# In[12]:


#Linien mit der grössten Besetzung
(df_fahr.groupby('linienname').mean().reset_index().sort_values('belastung', ascending=False)
 .head(10).plot(kind='barh', figsize=(12,3), x=('linienname'), y='belastung'))

plt.title('Linien mit der grössten Auslastung')
plt.show()


# ## Haltestellen

# In[13]:


(df_fahr.groupby('haltestellenlangname').mean().reset_index().sort_values('traffic_total')
.head(10).plot(kind='barh', figsize=(12,3), x='haltestellenlangname', y='traffic_total'))

plt.title('Haltestellen mit der geringsten Traffic') 
plt.show()


# In[14]:


(df_fahr.groupby('haltestellenlangname').mean().reset_index().sort_values('traffic_total', ascending=False)
 .head(10).plot(kind='barh', figsize=(12,3), x='haltestellenlangname', y='traffic_total'))

plt.title('Haltestellen mit der grössten Traffic') 
plt.show()


# ## Top 10 Haltestelle Traffic

# In[15]:


# Zürich lon, lat
latitude = 47.36667
longitude = 8.55

df_fahr_topeinsteiger = df_fahr.groupby('haltestellenlangname').mean().reset_index().sort_values('traffic_total', ascending=False).head(10)
max_colormap = df_fahr_topeinsteiger['traffic_total'].max()

#Farben
colormap = cm.LinearColormap(colors=['lightblue','blue'], index=[0, max_colormap],vmin=0,vmax=max_colormap)

def create_circleMarkerMap(df_fahr_topeinsteiger, latitude, longitude):
    map = folium.Map(location=[latitude, longitude], zoom_start=12)
    for loc, colo in zip(zip(df_fahr_topeinsteiger['koord_wgs84_e'], df_fahr_topeinsteiger['koord_wgs84_n']), df_fahr_topeinsteiger['traffic_total']):
            folium.CircleMarker(
                    location=loc,
                    radius=10,
                    color='black',
                    fill=True,
                    fill_opacity=0.8,
                    fill_color=colormap(colo),
                    parse_html = False).add_to(map)  
    map.add_child(colormap)      
    return map


# In[16]:


create_circleMarkerMap(df_fahr_topeinsteiger, latitude, longitude)


# # 2. Maps Fahrgastzahlen

# ## 2.1 Total traffic

# In[17]:


# Zürich lon, lat
latitude = 47.36667
longitude = 8.55

#exclude NaN and groupby
df_fahr_ttg = df_fahr.groupby(["haltestellen_id"], as_index=False)["traffic_total"].sum()

#Daten mergen
df_fahr_tt=df_fahr_ttg.merge(df_fahr,left_on='haltestellen_id',right_on='haltestellen_id', how='right')

#Farben
max_bewegung = df_fahr_tt['traffic_total_x'].max()
colormap = cm.LinearColormap(colors=['lightblue','blue'], index=[0, max_bewegung],vmin=0,vmax=max_bewegung)


# In[18]:


df_fahr_tt.head(50)


# In[19]:


def create_circleMarkerMap(df_fahr_tt, latitude, longitude):
    map = folium.Map(location=[latitude, longitude], zoom_start=12)
    for loc, colo in zip(zip(df_fahr_tt['koord_wgs84_e'], df_fahr_tt['koord_wgs84_n']), df_fahr_tt['traffic_total_x']):
            folium.CircleMarker(
                    location=loc,
                    radius=10,
                    color='black',
                    fill=True,
                    fill_opacity=0.8,
                    fill_color=colormap(colo),
                    parse_html = False).add_to(map)  
    map.add_child(colormap)      
    return map


# In[20]:


create_circleMarkerMap(df_fahr_tt, latitude, longitude)


# ## 2.2 Auslastung pro Haltestelle

# In[21]:


#exclude NaN and groupby
df_fahr_b=df_fahr.dropna(subset=['belastung'])
df_fahr_ttb = df_fahr_b.groupby(["haltestellen_id"], as_index=False)["belastung"].sum()

#Daten mergen
df_fahr_bb=df_fahr_ttb.merge(df_fahr,left_on='haltestellen_id',right_on='haltestellen_id', how='right')
df_fahr_bb=df_fahr_bb.dropna(subset=['belastung_x'])

#Farben
max_belastung = df_fahr_bb['belastung_x'].max()
colormap = cm.LinearColormap(colors=['lightblue','blue'], index=[0, max_belastung],vmin=0,vmax=max_belastung)


# In[22]:


#export df_fahr_bb für detailierte Analyse
df_fahr_bb.to_csv('./df_fahr_bb.csv', index=False)


# In[23]:


def create_circleMarkerMap(df_fahr_bb, latitude, longitude):
    map = folium.Map(location=[latitude, longitude], zoom_start=12)
    for loc, colo in zip(zip(df_fahr_bb['koord_wgs84_e'], df_fahr_bb['koord_wgs84_n']), df_fahr_bb['belastung_x']):
            folium.CircleMarker(
                    location=loc,
                    radius=10,
                    color='black',
                    fill=True,
                    fill_opacity=0.8,
                    fill_color=colormap(colo),
                    parse_html = False).add_to(map)  
    map.add_child(colormap)      
    return map

create_circleMarkerMap(df_fahr_bb, latitude, longitude)


# ## 2.3 Total Traffic pro Quartier

# In[24]:


#Keine Zone rausnehmen (Haltestellen ausserhalb Zürich-Stadt)
kz_filt = df_fahr['Quartier']!='Keine Zone'
df_fahr_kz = df_fahr[kz_filt]


# In[25]:


map_path = './Geodaten/stzh.adm_statzonen_map.geojson'


# In[26]:


def create_kreis_choropleth(df_fahr_kz, map_path, latitude, longitude):
    map = folium.Map(location=[latitude, longitude], zoom_start=12)
    
    folium.Choropleth(
        geo_data=map_path,
        name='traffic_total',
        data=df_fahr_kz,
        columns=['Quartier', 'traffic_total'],
        key_on='feature.properties.stzname',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        legend_name='traffic_total'
    ).add_to(map) 

    folium.LayerControl().add_to(map)

    return map

#traffic_total per Quartier
x = df_fahr_kz[['Quartier','traffic_total']].groupby(['Quartier'])
z = x.sum().reset_index()

create_kreis_choropleth(z, map_path, latitude, longitude)


# ## 2.4 Auslastung pro Quartier

# In[27]:


map_path = './Geodaten/stzh.adm_statzonen_map.geojson'


# In[28]:


def create_kreis_choropleth(df_fahr_kz, map_path, latitude, longitude):
    map = folium.Map(location=[latitude, longitude], zoom_start=12)
    
    folium.Choropleth(
        geo_data=map_path,
        name='belastung',
        data=df_fahr_kz,
        columns=['Quartier', 'belastung'],
        key_on='feature.properties.stzname',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        legend_name='belastung'
    ).add_to(map) 

    folium.LayerControl().add_to(map)

    return map

#traffic_total per Quartier
x = df_fahr_kz[['Quartier','belastung']].groupby(['Quartier'])
z = x.sum().reset_index()

create_kreis_choropleth(z, map_path, latitude, longitude)


# # 3 Bevölkerung gegen Sitzplatzauslastung pro Haltestelle

# In[29]:


# File importieren
df_bev_geo_p=pd.read_csv('./df_bev_geo_p.csv')

#sum of people
df_bev_geo_p['pers_n'].sum()


# In[30]:


#Liste für heatmap

heat_data_a = []
heat_data_a = zip(df_bev_geo_p['koord_wgs84_e'], df_bev_geo_p['koord_wgs84_n'], df_bev_geo_p['pers_n'])

final_heat_list = [list(ele) for ele in heat_data_a]


# In[31]:


#Create heatmap of Bevölkerung
heatmap = folium.Map(location=[latitude, longitude], zoom_start=12) 

#List of coordinates (Latitude and Longitude)
heat_data = final_heat_list

#Farben
max_belastung = df_fahr_bb['belastung_x'].max()
colormap = cm.LinearColormap(colors=['lightblue','blue'], index=[0, max_belastung],vmin=0,vmax=max_belastung)


# Plot the on the map
HeatMap(heat_data,
        min_opacity=0.5,
        #max_zoom=18,
        radius=40,
        blur=50,
        gradient=False,
        overlay=True).add_to(heatmap)

for loc, colo in zip(zip(df_fahr_bb['koord_wgs84_e'], df_fahr_bb['koord_wgs84_n']), df_fahr_bb['belastung_x']):
        folium.CircleMarker(
                #[lat, lng],
                location=loc,
                radius=10,
                color=colormap(colo),
                fill=True,
                fill_opacity=0.8,
                fill_color=colormap(colo),
                parse_html = False).add_to(heatmap)  

features = {}
for row in pd.unique(df_fahr_bb['linienname']):
    features[row] = folium.FeatureGroup(name=row, show=False)
        
#Punkte der Linien auf Karte plotten        
for index, row in df_fahr_bb.iterrows():
    circ = folium.Circle([row['koord_wgs84_e'], row['koord_wgs84_n']],
                   radius=0,
                   color=colormap(row['belastung_x']),
                   tooltip=(row['haltestellenlangname'],'Durchschn. Belastung:',row['belastung_x']),      
                   weight=20)
    circ.add_to(features[row['linienname']])
        
for row in pd.unique(df_fahr_bb['linienname']):
    features[row].add_to(heatmap)

# Display the map
heatmap

