#!/usr/bin/env python
# coding: utf-8

# # Electric Vehicle Population Data for Washington State
# 
# ### Current registered EVs in the State of Washington according to Washington State Department of Licensing (DOL)
# 

# ## <ins>Introduction: Cleaning and exploring the dataset</ins>

# In[2]:


import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import zscore
import hvplot.pandas 
import holoviews as hv
from bokeh.models import LogTicker, FuncTickFormatter, FixedTicker, CustomJSTickFormatter
import panel as pn 

pn.extension()


# In[3]:


df = pd.read_csv('./csv/Electric_Vehicle_Population_Data.csv')

# print(len(df.columns))
# print(df.info())
# df.head(1)


# ### Checking various columns to see how many unique values there are
# some of these columns Ill probably be able to convert to categories instead of strings/objects for better performance
# Also based on the info method call above, and looking at column types, I might convert other column types where it makes sense
# 
# As an example, some of the float columns would make more sense if they are ints, i.e. postal code

# In[4]:


df['Clean Alternative Fuel Vehicle (CAFV) Eligibility'].unique()


# In[5]:


df['Electric Vehicle Type'].unique()


# In[6]:


df['Make'].unique()


# In[7]:


df['State'].unique()


# In[8]:


df['Clean Alternative Fuel Vehicle (CAFV) Eligibility'].unique()


# Converting columns

# In[9]:


df['State'] = df['State'].astype('category')
df['Electric Vehicle Type'] = df['Electric Vehicle Type'].astype('category')
df['Clean Alternative Fuel Vehicle (CAFV) Eligibility'] = df['Clean Alternative Fuel Vehicle (CAFV) Eligibility'].astype('category')
df['Postal Code'] = df['Postal Code'].astype('Int64')
df['Electric Range'] = df['Electric Range'].astype('Int64')
df['Legislative District'] = df['Legislative District'].astype('Int64')



# Adding extra region column for comparison later

# In[10]:


north_america = ['TESLA', 'JEEP', 'FORD', 'CHEVROLET', 'RIVIAN', 'CHRYSLER', 'CADILLAC', 'LINCOLN', 'DODGE', 'GMC', 'LUCID', 'FISKER', 'MULLEN AUTOMOTIVE INC.', 'BRIGHTDROP', 'RAM', 'AZURE DYNAMICS', 'WHEEGO ELECTRIC CARS']
asia = ['NISSAN', 'KIA', 'HYUNDAI', 'MAZDA', 'TOYOTA', 'SUBARU', 'LEXUS', 'HONDA', 'MITSUBISHI', 'ACURA', 'GENESIS', 'VINFAST']
europe = ['FIAT', 'AUDI', 'PORSCHE', 'BMW', 'POLESTAR', 'VOLVO', 'MINI', 'MERCEDES-BENZ', 'VOLKSWAGEN', 'ALFA ROMEO', 'SMART', 'JAGUAR', 'LAND ROVER', 'LAMBORGHINI', 'TH!NK', 'ROLLS-ROYCE', 'BENTLEY']
def region_check(car_make):
    if car_make in north_america:
        return 'North America'
    elif car_make in asia:
        return 'Asia'
    else:
        return 'Europe'


df['EV Regional Origin'] = df['Make'].apply(region_check)

df.head()


# ## Doing some exploration
# 

# ### Bar Plot of number of EVs for Each Model Year

# In[11]:


print(df['Make'].nunique())
print(df['Model Year'].unique())

filtered_df = df.groupby('Model Year').agg({'VIN (1-10)':'count'})
filtered_df.reset_index(inplace=True)
filtered_df.rename(columns={'VIN (1-10)': 'Number of EVs'}, inplace=True)
filtered_df.head()
hv_bar_plot = filtered_df.hvplot.bar(x='Model Year', 
                                    y='Number of EVs', 
                                    C='Count', 
                                    cmap='BuPu', 
                                    xlabel='Model Year', 
                                    ylabel='Number of Registered EVs (Log Scale)', 
                                    title='Number of Registered EVs in WA Per Model Year',
                                    logy=True).opts(
                                        show_grid=True
                                    )

textbox = hv.Text(
    x=2001, y=120,
    text='*Unit increase in Y = 10× more EVs'
).opts(
    text_align='left',
    text_font_size='10pt',
    bgcolor='white'
)

(hv_bar_plot * textbox)


# ## HeatMap of EVs in Washington State Counties

# In[12]:


df_wa_counties = df[df['State'] == 'WA']

df_top_10_counties_ev_wa = df_wa_counties.groupby('County').agg({'VIN (1-10)':'count'}).nlargest(10, 'VIN (1-10)')
df_top_10_counties_ev_wa.reset_index(inplace=True)


df_wa_counties = df_wa_counties[df_wa_counties['County'].isin(df_top_10_counties_ev_wa['County'])]

heat_map_data = df_wa_counties.pivot_table(index="County", columns="EV Regional Origin", values='VIN (1-10)', aggfunc='count', fill_value=0, sort=False)
# heat_map_data_norm = heat_map_data.apply(lambda x: x**2)
heat_map_data.head(20)



# In[13]:


# # heat_map_data.index.name = 'County'
# # heat_map_data.columns.name = 'Region'

# heat_map_long = heat_map_data.reset_index().melt(
#     id_vars='County',
#     var_name='EV Regional Origin',
#     value_name='Number of EVs Registered'
# )
# print(heat_map_long.head()) 

# custom_formatter = FuncTickFormatter(code="""
#     var log = Math.log10(tick);
#     return tick.toLocaleString() + " (log₁₀=" + log.toFixed(1) + ")";
# """)

# custom_ticks = [1000, 5000, 25000, 70000]

# # Use FixedTicker instead of LogTicker
# fixed_ticker = FixedTicker(ticks=custom_ticks)

# hmap = heat_map_long.hvplot.heatmap(x='EV Regional Origin', 
#                                     y='County', 
#                                     C='Number of EVs Registered', 
#                                     cmap='BuPu', 
#                                     xlabel='EV Car Model Origin', 
#                                     ylabel='Washington State County', 
#                                     title='Top 10 WA Counties: EVs Registered by Car Origin (Log Scale)',
#                                     logz=True,
#                                     colorbar=True).opts(
#                                         colorbar_opts={'title': 'Raw Number of EVs (w/ Log Scale)', 'ticker': fixed_ticker, 'formatter': custom_formatter}
                                        
#                                     )
# hmap


# Violin Plot of Battery Range in each region

# In[14]:


## for this one Ill look at all counties, not just in WA

new_df = df[df['EV Regional Origin'] == 'Europe']
state_df = df[df['State'] != 'WA']
print(new_df['Electric Range'].median())
print(df[df['EV Regional Origin'] == 'North America']['Electric Range'].isna().sum())
print(df['EV Regional Origin'].unique())


## remove any 0s for the electric range
violin__dot_df = df[df['Electric Range'] > 0]

# print(state_df)

# new_df.head(2)


# In[15]:


# plt.figure(figsize=(7, 7))
# sns.violinplot(
#     data=new_df,
#     x='EV Regional Origin',  # or y=... if you prefer horizontal
#     y='Electric Range',
#     palette=['red', 'silver', 'blue'],
#     hue="EV Regional Origin",
#     legend=True
# )
# plt.legend()
# plt.show()

violin = violin__dot_df.hvplot.violin(y='Electric Range', by='EV Regional Origin', ylabel='EV Range (Mi)',
                 cmap=['red', 'silver', 'blue'], legend=False, color='EV Regional Origin',
                 width=600, height=600, padding=0.4).opts(
                     ylim=(-25, 400)
                 )
violin


# Swarm Plot of battery range v model year

# In[16]:


## creating jitter
cats = violin__dot_df['Electric Vehicle Type'].astype('category').cat.categories

violin__dot_df['Electric Vehicle Type Code'] = violin__dot_df['Electric Vehicle Type'].astype('category').cat.codes

violin__dot_df['Jitter'] = violin__dot_df['Electric Vehicle Type Code'] + np.random.normal(0, 0.05, len(violin__dot_df))
# violin__dot_df.head()

scatter = violin__dot_df.hvplot.scatter(x='Jitter', y='Electric Range', by='Electric Vehicle Type',
                                        width=600, height=600, legend=False).opts(
                                          xticks = [(i, cat) for i, cat in enumerate(cats)],
                                          xlabel = 'Electric Vehicle Type',
                                          ylabel = 'Electric Range (mi)',
                                          title='Range Comparison for Battery Electric and Plug-in Hybrid Vehicles'
                                        )
scatter

# scatter of battery type and electric range


# ## Next will work on the widgets that I want for each plot

# first starting with origin region selector for barplot

# In[17]:


select_var_ev_origin = pn.widgets.Select(
    options=[x for x in df['EV Regional Origin'].unique()] + ['All'],                   
    value='All',                   
    description='Choose which Regional HQ Location You would like to focus on'
)

# df.head()


# next lets create a function to produce a barplot depending on the selector

# In[33]:


def create_barplot(ev_origin):
    miny = 0
    maxy = df.groupby('Model Year')['VIN (1-10)'].count().sort_values(ascending=False).iloc[0]
    first_filter = df[df['EV Regional Origin'] == ev_origin] if ev_origin != 'All' else df
    filtered_df = first_filter.groupby('Model Year').agg({'VIN (1-10)':'count'})
    filtered_df.reset_index(inplace=True)
    filtered_df.rename(columns={'VIN (1-10)': 'Number of EVs'}, inplace=True)
    filtered_df.head()
    hv_bar_plot = filtered_df.hvplot.bar(x='Model Year', 
                                        y='Number of EVs', 
                                        C='Count', 
                                        cmap='BuPu', 
                                        xlabel='Model Year', 
                                        ylabel='Number of Registered EVs (Log Scale)', 
                                        title='Number of Registered EVs in WA Per Model Year',
                                        logy=True).opts(
                                            show_grid=True,
                                            xlim=(min(df['Model Year']) - 2, max(df['Model Year']) + 2),
                                            ylim=(2, maxy)
                                        )

    textbox = hv.Text(
        x=2001, y=120,
        text='*Unit increase in Y = 10× more EVs'
    ).opts(
        text_align='left',
        text_font_size='10pt',
        bgcolor='white'
    )

    return (hv_bar_plot * textbox)


# binding together

# In[34]:


interactive_bar_plot = pn.bind(create_barplot, ev_origin=select_var_ev_origin)


# show the dashboard thus far

# In[20]:


# dashboard = pn.Column(
#     pn.Row(select_var_ev_origin),
#     interactive_bar_plot
# )
# dashboard.servable()  # or dashboard.show or view()


# Moving onto Heatmap selector

# In[21]:


year_range_slider = pn.widgets.RangeSlider(
    start=df['Model Year'].min(),
    end=df['Model Year'].max(),
    value=(df['Model Year'].min(), df['Model Year'].max()),
    step=1
)


# function to produce heatmap

# In[22]:


df_wa_counties_2 = df[df['State'] == 'WA']
df_top_10_counties_ev_wa = df_wa_counties_2.groupby('County').agg({'VIN (1-10)':'count'}).nlargest(10, 'VIN (1-10)')
df_top_10_counties_ev_wa = df_top_10_counties_ev_wa.reset_index(inplace=False)

df_wa_counties_new = df_wa_counties_2[df_wa_counties_2['County'].isin(df_top_10_counties_ev_wa['County'])]


# In[23]:


def create_heatmap(year_range):
    filtered_df_wa_counties = df_wa_counties_new[(df_wa_counties_new['Model Year'] >= year_range[0]) & (df_wa_counties_new['Model Year'] <= year_range[1])]
   

    heat_map_data = filtered_df_wa_counties.pivot_table(index="County", columns="EV Regional Origin", values='VIN (1-10)', aggfunc='count', fill_value=0, sort=False)

    heat_map_long = heat_map_data.reset_index().melt(
    id_vars='County',
    var_name='EV Regional Origin',
    value_name='Number of EVs Registered'
    )

    custom_ticks = [1000, 5000, 25000, 70000]

    fixed_ticker = FixedTicker(ticks=custom_ticks)

    custom_formatter_2 = CustomJSTickFormatter(code="""
    var log = Math.log10(tick);
    return tick.toLocaleString() + " (log₁₀=" + log.toFixed(1) + ")";
    """)

    return heat_map_long.hvplot.heatmap(x='EV Regional Origin', 
                                        y='County', 
                                        C='Number of EVs Registered', 
                                        cmap='BuPu', 
                                        xlabel='EV Car Model Origin', 
                                        ylabel='Washington State County', 
                                        title='Top 10 WA Counties: EVs Registered by Car Origin (Log Scale)',
                                        logz=True,
                                        colorbar=True).opts(
                                            colorbar_opts={'title': 'Raw Number of EVs (w/ Log Scale)', 'ticker': fixed_ticker, 'formatter': custom_formatter_2}
                                            
                                        )
    


# In[24]:


interactive_heatmap = pn.bind(create_heatmap, year_range=year_range_slider)


# In[25]:


# dashboard2 = pn.Column(
#     pn.Row(year_range_slider),
#     interactive_heatmap
# )
# dashboard2.servable()  # or dashboard.servable() if using Panel server


# next violin plot

# In[26]:


violin__dot_df = df[df['Electric Range'] > 0]


# In[27]:


def create_violin_plot(year_range):

    filtered_violin_df = violin__dot_df[(violin__dot_df['Model Year'] >= year_range[0]) & (violin__dot_df['Model Year'] <= year_range[1])]

    return filtered_violin_df.hvplot.violin(y='Electric Range', by='EV Regional Origin', ylabel='EV Range (Mi)',
                 cmap=['red', 'silver', 'blue'], legend=False, color='EV Regional Origin',
                 width=600, height=600, padding=0.4).opts(
                     ylim=(-25, 400)
                 )


# In[28]:


interactive_violin = pn.bind(create_violin_plot, year_range=year_range_slider)

# dashboard3 = pn.Column(
#     pn.Row(year_range_slider),
#     interactive_violin
# )
# dashboard3


# finally the jittered dot plot

# In[29]:


## creating jitter
cats = violin__dot_df['Electric Vehicle Type'].astype('category').cat.categories

violin__dot_df['Electric Vehicle Type Code'] = violin__dot_df['Electric Vehicle Type'].astype('category').cat.codes

violin__dot_df['Jitter'] = violin__dot_df['Electric Vehicle Type Code'] + np.random.normal(0, 0.05, len(violin__dot_df))


# In[30]:


miny = -5
maxy = violin__dot_df['Electric Range'].max() + 5

def create_dot_plot(ev_origin):
    first_filter_dot_plot = violin__dot_df[violin__dot_df['EV Regional Origin'] == ev_origin] if ev_origin != 'All' else violin__dot_df

    return first_filter_dot_plot.hvplot.scatter(x='Jitter', y='Electric Range', by='Electric Vehicle Type',
                                            width=600, height=600, legend=False).opts(
                                            xticks = [(i, cat) for i, cat in enumerate(cats)],
                                            xlabel = 'Electric Vehicle Type',
                                            ylabel = 'Electric Range (mi)',
                                            title='Range Comparison for Battery Electric and Plug-in Hybrid Vehicles'
                                            ).opts(
                                                ylim=(miny, maxy)
                                            )


# In[31]:


interactive_dot = pn.bind(create_dot_plot, ev_origin=select_var_ev_origin)

# dashboard4 = pn.Column(
#     pn.Row(select_var_ev_origin),
#     interactive_dot
# )
# dashboard4


# ## Dashboard final

# In[35]:


dashboard_final = pn.Column(
    pn.pane.Markdown("<h1 style='font-size:4em; color: black'>Electric Vehicle Registration data for the State of Washington</h1>"),
    pn.pane.Markdown("<h3 style='font-size:1.5em; color: black'>Use the following dropdown to filter for EV Model Origin in the 2 plots below</h3>"),
    pn.Row(select_var_ev_origin),
    pn.Row(interactive_bar_plot, interactive_dot),
    pn.pane.Markdown("<h3 style='font-size:1.5em; color: black'>Use the following slider to filter for EV Model Years in the 2 plots below</h3>"),
    pn.Row(year_range_slider),
    pn.Row(interactive_heatmap, interactive_violin)
)

dashboard_final.servable()

