#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import plotly.express as px
import geopandas as gp 
from pathlib import Path


# In[2]:


gsd = r'codepo_gb.gpkg'


# In[3]:


data_al = r'Postcode_level_standard_electricity_2015_A_to_L.csv'
data_lz = r'Postcode_level_standard_electricity_2015_L_to_Z.csv'


# In[4]:


df_al = pd.read_csv(data_al,delimiter=",", encoding="UTF-8")
df_lz = pd.read_csv(data_lz,delimiter=",", encoding="UTF-8")


# In[5]:


df_al.head()


# In[6]:


df_lz.head()


# In[7]:


df_al.shape


# In[8]:


df_lz.shape


# Appending the postcoode from L-Z to A-L, there should not be any duplicates

# In[9]:


df = df_al.append(df_lz, ignore_index=True)


# In[10]:


df.shape


# Reading the geospatial data 

# In[11]:


gdf = gp.read_file(gsd)


# In[12]:


gdf.head()


# I need only a postcode and geometry olumns to use with  with my data frames.

# In[13]:


gdf_postGeo = gdf[["Postcode","geometry"]] 


# In[14]:


df.info()


# In[15]:


gdf_postGeo.info()


# In[16]:


df.rename(columns = {"POSTCODE" : "Postcode"}, inplace=True)


# In[17]:


joined = df.set_index("Postcode").join(gdf_postGeo.set_index("Postcode"))


# In[18]:


joined.info()


# There is too many missing values, better to drop them to thin out the data frame 

# In[33]:


joined.dropna(inplace=True)


# In[34]:


joined.head(1)


# In[35]:


joined.iloc[0]


# The geopgrahical data is in the grid refereence system,I should extracy the easting and northing coordinataes from "geometry" column into two seperated columns 

# In[44]:


joined["easting"] = 0
joined["northing"] = 0


# In[46]:


easings = joined.apply(lambda row: (row["geometry"].x), axis=1)
norhtings = joined.apply(lambda row: (row["geometry"].y), axis=1)


# In[47]:


joined["easting"] = easings
joined["northing"] = norhtings


# In[48]:


joined.head()


# There is need for converting eastings and northings into latitude and longitude.

# In[50]:


from pyproj import Proj, transform


# In[63]:


v84 = Proj(proj="latlong",towgs84="0,0,0",ellps="WGS84")
v36 = Proj(proj="latlong", k=0.9996012717, ellps="airy",
        towgs84="446.448,-125.157,542.060,0.1502,0.2470,0.8421,-20.4894")
vgrid = Proj(init="world:bng")

def vectorized_convert(df):
    vlon36, vlat36 = vgrid(df["easting"].values, 
                           df["northing"].values, 
                           inverse=True)

    converted = transform(v36, v84, vlon36, vlat36)

    df['longitude'] = converted[0]
    df['latitude'] = converted[1]

    return df


# In[64]:


vectorized_convert(joined)


# In[67]:


joined = joined.drop(columns=["Number of meters","Consumption (kWh)","geometry","northing","easting"])


# In[68]:


joined


# In[69]:


new_cols = {
    "Mean consumption (kWh)" : "mean_kWh",
    "Median consumption (kWh)" : "median_kWh"
}

joined.rename(columns=new_cols, inplace=True)


# In[70]:


joined


# In[75]:


joined = joined.reset_index()


# In[77]:


fig = px.scatter_mapbox(joined, lat = "latitude", lon="longitude", color = "median_kWh", zoom=5,
                        mapbox_style="open-street-map", hover_name='Postcode', hover_data=["median_kWh"])
fig.show()


# To many data to plot it elegantly, lets focus on hig consumption, ten top 1%

# In[79]:


joined["median_kWh"].median()


# In[80]:


joined["median_kWh"].quantile(0.99)


# In[81]:


top_usage = joined[joined["median_kWh"] > joined["median_kWh"].quantile(0.99)]


# In[82]:


top_usage.describe()


# In[83]:


top_usage.info()


# In[84]:


fig = px.scatter_mapbox(top_usage, lat = "latitude", lon="longitude", color = "median_kWh", zoom=5,
                        mapbox_style="open-street-map", hover_name='Postcode', hover_data=["median_kWh"])
fig.show()


# In[ ]:




