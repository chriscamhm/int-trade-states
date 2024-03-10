#!/usr/bin/env python
# coding: utf-8

# <h1><center> General objective </center></h1>

# The present work was realized as final project for the **Applied Plotting, Charting & Data Representation in Python**. So, the present code is a compilation well presented of the work that I did. The objective achieved was representing the evolution of the international trade of **Michigan** and its neighbour states **Wisconsin, Ohio, Illinois and Indiana** by an animated and interactive graphic. The data used are exports, imports and balance trade extracted by scrapping web tecnhniques from the USA Census Bureau. 
# The data is monthly and posted online by the Census bureau in the same frequency. Hence, there were multiple files corresponding to monthly data for **exports by origin of movement** and **imports by state destination** both of them not seasonally adjusted. So, in order to learn and avoiding to download many files and joining them I applied scrapping web techniques that I learned from different sources and it was a magnific technique to learn in order to download public databases. 
# The links are the following:
# 
# **Exports:** https://www.census.gov/foreign-trade/statistics/state/origin_movement/index.html
# 
# **Imports:** https://www.census.gov/foreign-trade/statistics/state/destination_state/index.html
# 
# Firstly, I proceed to import the libraries:

# In[3]:


pip install gitpython


# In[2]:


import pandas as pd
import numpy as np
import gitpyhon

import urllib3
import requests
import csv

from bs4 import BeautifulSoup


urllib3.disable_warnings()


# <h1><left> Exports </left></h1>
# 
# I started with the exports databases. As I previously mentioned the data corresponds to montly frequency and the census posted every month. I did not want to download many files and joining them, I heard that you could manage public databases from internet on Python. **Very useful!**
# 
# I start with extracting from the URL where the databases are downloaded, all the code in order to extract fro there the href code corresponding to the databases in a Excel file. That was one of my first problems, because on the page each database is posted with three links to download in excel, text and pdf file respectively but I need it in excel due to I do not know if I could manipulate well from Python with a text file.

# In[2]:


url_page = 'https://www.census.gov/foreign-trade/statistics/state/origin_movement/index.html'
page = requests.get(url_page,verify=False).text 
soup = BeautifulSoup(page, "lxml") 
contenido = soup.find('div', attrs={'id': 'middle-column'}) 
items = contenido.find_all('a')
it= str(items)


# To extract only the links that I am interested in. I imported regex to make a search in the links that extracted only the links corresponding to excel files. The regex is a bit long because I tried with identifiers but it did not work and I passed a lot of time so at the end I used the regex that worked but I think there is much shorter code but I'm not familiriazed with regex. 

# In[3]:


import re
urls = re.findall(r'(<a href=\"\/\w+\-\w+\/\w+\-\w+\/\d*\w+[^>]*\>\(XLS\)\<\/\w+\>)', it)
# the url list contains all the html code included title and href  
links = [] # the link list contains only the <a> href, e.g  <a href="/foreign-trade/Press-Release/2020pr/07/exh2s.xls">(XLS)</a>
for i in urls:
    html = str(i)
    soup = BeautifulSoup(html) #Para leer el html del nuevo string
    
    for a in soup.find_all('a', href=True):
        links.append(a['href'])

#extract the year and month from each link, e.g <a href="/foreign-trade/Press-Release/2020pr/07/exh2s.xls">(XLS)</a>
year =[]
for i in urls:
    year.append(re.findall(r'(\d{4})', i)[0])

month = []
for i in urls:
    month.append(re.findall(r'(?<=\/)(\d{2})(?=\/)', i)[0])


# In[4]:


#transform the list into series and consecuently a database
urls = pd.Series(urls)
links = pd.Series(links)
year = pd.Series(year)
month = pd.Series(month)

extract = pd.concat([urls,links,year,month], axis=1, keys=['urls','links','year','month'])
extract['year'] = extract['year'].fillna('0')

#the initial database with the first link that is of september, 2020
l = 'https://www.census.gov/'
data = pd.read_excel(l+links[0])
data['year'] = [ year.iloc[0] for i in range(len(data)) ] #Add a column of year to the excel
data['month'] = [ month.iloc[0] for i in range(len(data))] #Add a column of month to the excel


# Having an initial database, through a loop I could extract the other links into an excel read file and concatenating with the initial databse. I use the year greater than 2013 because since 2014 the following databases has the same format.

# In[5]:


for link,year,month in zip(extract.links[1:],extract.year[1:],extract.month[1:]):
    if year > '2013':
        datasets = pd.read_excel(l+link)
        datasets['year'] = [year for i in range(len(datasets))]
        datasets['month'] = [month for i in range (len(datasets))]
        data = pd.concat([data,datasets], axis=0)


# All the data is in the database but each file has a format readable to humans but in order to manipulate in programs I have to clean it. Dropping the columns empty or with nan values or columns that I do not need for the objective of this work. I only needed the data of total monthly exports of the five states that I am comparing. I drop the columns, besides the null and empty ones, the columns of manufactured and non manufactured exports, percent of change, and the rows that describes the info of the tables and other information relevant to the users of the tables but not for the aim of this work. Also I cleaned of spaces to the first column that I renamed as State, because later I filtered out by the fives states that I focused on.

# In[6]:


data.drop(data.iloc[:,1:9],axis = 'columns', inplace=True)
data.drop(['Unnamed: 10','Unnamed: 11','Unnamed: 12', 'Unnamed: 13'],axis = 'columns', inplace=True)
data.rename(columns={'Unnamed: 9': 'Total Month Export', 'Unnamed: 0': 'States'}, inplace=True)
data= data.iloc[15:]
data['States'] = data['States'].str.strip() #clean spaces


# In[7]:


#I Filtered out by the states that I am interested in
df= data.loc[(data['States'] == 'Michigan') | (data['States'] == 'Wisconsin')|
             (data['States'] == 'Ohio') | (data['States'] == 'Indiana') | (data['States'] == 'Illinois')]


# <h1><left> Imports </left></h1>
# 
# I repeated the same process but this time with imports.

# In[8]:


url_page_imp = 'https://www.census.gov/foreign-trade/statistics/state/destination_state/index.html'
page_imp = requests.get(url_page_imp,verify=False).text 
soup_imp = BeautifulSoup(page_imp, "lxml") 
contenido_imp = soup_imp.find('div', attrs={'id': 'middle-column'}) 
items_imp = contenido_imp.find_all('a')
it_imp= str(items_imp)

urls_imp = re.findall(r'(<a href=\"\/\w+\-\w+\/\w+\-\w+\/\d*\w+[^>]*\>\(XLS\)\<\/\w+\>)', it_imp)
links_imp = []
for i in urls_imp:
    html_imp = str(i)
    soup_imp = BeautifulSoup(html_imp) #Para leer el html del nuevo string
    
    for a in soup_imp.find_all('a', href=True):
        links_imp.append(a['href'])

year_imp =[]
for i in urls_imp:
    year_imp.append(re.findall(r'(\d{4})', i)[0])
month_imp = []
for i in urls_imp:
    month_imp.append(re.findall(r'(?<=\/)(\d{2})(?=\/)', i)[0])


# In[9]:


urls_imp = pd.Series(urls_imp)
links_imp = pd.Series(links_imp)
year_imp = pd.Series(year_imp)
month_imp = pd.Series(month_imp)

extract_imp = pd.concat([urls_imp,links_imp,year_imp,month_imp], axis=1, keys=['urls','links','year','month'])
extract['year'] = extract['year'].fillna('0')
l = 'https://www.census.gov/'
data_imp = pd.read_excel(l+links_imp[0])
data_imp['year'] = [ year_imp.iloc[0] for i in range(len(data_imp)) ] #Add a column of year to the excel
data_imp['month'] = [ month_imp.iloc[0] for i in range(len(data_imp))] #Add a column of month to the excel


# In[10]:


for link,year,month in zip(extract_imp.links[1:],extract_imp.year[1:],extract_imp.month[1:]):
    if year > '2013':
        datasets = pd.read_excel(l+link)
        datasets['year'] = [year for i in range(len(datasets))]
        datasets['month'] = [month for i in range (len(datasets))]
        data_imp = pd.concat([data_imp,datasets], axis=0)


# In[11]:


#Clean the database dropping the columns that I did not need and also keep the same number of columns fo the exprts database.
data_imp.drop(data_imp.iloc[:,1:7],axis = 'columns', inplace=True)
data_imp.drop(['Unnamed: 8','Unnamed: 9','Unnamed: 10', 'Unnamed: 11'],axis = 'columns', inplace=True)
data_imp.rename(columns={'Unnamed: 7': 'Total Month Import', 'Unnamed: 0': 'States'}, inplace=True)


# In[12]:


data_imp= data_imp.iloc[15:]
data_imp['States'] = data_imp['States'].str.strip()


# In[13]:


df_imp= data_imp.loc[(data_imp['States'] == 'Michigan') | (data_imp['States'] == 'Wisconsin')|
             (data_imp['States'] == 'Ohio') | (data_imp['States'] == 'Indiana') | (data_imp['States'] == 'Illinois')]


# # Merge
# 
# I merged the two resulting databases in order to have one database of international trade of both states and calculate the trade balance which is **Export minus Imports**

# In[44]:


df_trade= df.merge(df_imp, on=['States','year', 'month'])[['States','Total Month Export','Total Month Import','year','month']]
df_trade


# In[45]:


#Join the year and month to create the datetime
df_trade['Date']= df_trade['year'].map(str) + '-'+ df_trade['month'].map(str)
df_trade['Date']= pd.to_datetime(df_trade["Date"])
df_trade.sort_values(['Date'], ascending=True, inplace=True)
df_trade['Trade Balance']=df_trade['Total Month Export']-df_trade['Total Month Import'] #calculate the trade balance


# <h1><center> Graphs </center></h1>
# 
# My objective is compare the evolution of exports, imports and trade balance of the five states. To do so and ir order to learn I made an interactive and animated graphic with three subplots. The following codes make a graphic with three subplots, buttons of play and pause and an interactive slider of time.
# The three subplots are for exports and imports as line graphs and the trade balance as a bar. I did it in that way because I wanted to prove myself and make subplots animated learning in the way how to program a line graph that is not in the predetermined options in Plotly, and a bar graph that is included but I wanted to learn the code behind it so I did it "manually".
# 
# I use **Plotly** a library very useful and easy to use comparing to matplotlib. It was interesting programming with this library because offers many resourful options to make graphics that in matplotlib are difficult to do. However, an animated line graph is not in the predetermined option so I had to do it by myself facing many challenges and consulting in many forums as StackOverflow.

# In[48]:


#import the library from Plotly to manipulate subplots and graph objects
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
#a subplot of two rows and columns but in the second column the graphic occupies two rows. I did it with specs and rowspan
#specific details for design like spaces among the subplots, that the export and import subplot share an axis
fig_2 = make_subplots(rows=2, cols=2, specs=[[{}, {"rowspan": 2}],[{}, None]], 
                      column_widths=[0.7, 0.3], shared_xaxes=True, vertical_spacing=0.075, #70% for the first column
horizontal_spacing=0.05, print_grid=True)


# In[49]:


#Make a database for each state in order to write less code.
Michigan=df_trade[df_trade['States'].isin(['Michigan'])]
Wisconsin=df_trade[df_trade['States'].isin(['Wisconsin'])]
Indiana=df_trade[df_trade['States'].isin(['Indiana'])]
Ohio=df_trade[df_trade['States'].isin(['Ohio'])]
Illinois=df_trade[df_trade['States'].isin(['Illinois'])]


# The following code is very long, I could not think of more efficient code but I think there is. I added to the subplot the traces corresponding to each state.There are 3 subplots and 5 states so the result were 15 traces. 

# In[50]:


#First the traces of the export subplot, giving each state a specific color adn grouping them by the color for the next subplots.

fig_2.add_trace(go.Scatter(x=Michigan['Date'][:1],
                    y=Michigan['Total Month Export'][:1],
                    mode='lines',
                    line=dict(width=1.5, color='blue'),name="Michigan", legendgroup="Michigan"), row=1, col=1)

fig_2.add_trace(go.Scatter(x=Ohio['Date'][:1],
                    y=Ohio['Total Month Export'][:1],
                    mode='lines',
                    line=dict(width=1.5, color='red'),name="Ohio", legendgroup="Ohio"), row=1, col=1)

fig_2.add_trace(go.Scatter(x=Indiana['Date'][:1],
                    y=Indiana['Total Month Export'][:1],
                    mode='lines',
                    line=dict(width=1.5, color='blueviolet'),name="Indiana", legendgroup="Indiana"), row=1, col=1)

fig_2.add_trace(go.Scatter(x=Illinois['Date'][:1],
                    y=Illinois['Total Month Export'][:1],
                    mode='lines',
                    line=dict(width=1.5, color='green'),name="Illinois", legendgroup="Illinois"), row=1, col=1)

fig_2.add_trace(go.Scatter(x=Wisconsin['Date'][:1],
                    y=Wisconsin['Total Month Export'][:1],
                    mode='lines',
                    line=dict(width=1.5, color='black'), name="Wisconsin", legendgroup="Wisconsin"), row=1, col=1)


# In[51]:


#Adding to the import subplot the traces for each state

fig_2.add_trace(go.Scatter(x=Michigan['Date'][:1],
                    y=Michigan['Total Month Import'][:1],
                    mode='lines',
                    line=dict(width=1.5, color='blue'),name="Michigan", legendgroup="Michigan", showlegend=False), row=2, col=1)

fig_2.add_trace(go.Scatter(x=Ohio['Date'][:1],
                    y=Ohio['Total Month Import'][:1],
                    mode='lines',
                    line=dict(width=1.5, color='red'),name="Ohio", legendgroup="Ohio", showlegend=False), row=2, col=1)

fig_2.add_trace(go.Scatter(x=Indiana['Date'][:1],
                    y=Indiana['Total Month Import'][:1],
                    mode='lines',
                    line=dict(width=1.5, color='blueviolet'),name="Indiana", legendgroup="Indiana", showlegend=False), row=2, col=1)

fig_2.add_trace(go.Scatter(x=Illinois['Date'][:1],
                    y=Illinois['Total Month Import'][:1],
                    mode='lines',
                    line=dict(width=1.5, color='green'),name="Illinois", legendgroup="Illinois", showlegend=False), row=2, col=1)

fig_2.add_trace(go.Scatter(x=Wisconsin['Date'][:1],
                    y=Wisconsin['Total Month Import'][:1],
                    mode='lines',
                    line=dict(width=1.5, color='black'), name="Wisconsin", legendgroup="Wisconsin", showlegend=False), row=2, col=1)


# In[52]:


#Adding to the import subplot the traces of the bar graphic for each state


fig_2.add_trace(go.Bar(x=Michigan['States'][0:1],
                    y=Michigan['Trade Balance'][0:1], marker=dict(color='blue'),name="Michigan", legendgroup="Michigan", 
                       showlegend=False, hoverinfo='all',
                textposition='outside',
                texttemplate= '%{x}'), row=1, col=2)

fig_2.add_trace(go.Bar(x=Ohio['States'][0:1],
                    y=Ohio['Trade Balance'][0:1], marker=dict(color='red'),name="Ohio", legendgroup="Ohio", 
                       showlegend=False, hoverinfo='all',
                textposition='outside',
                texttemplate= '%{x}'), row=1, col=2)

fig_2.add_trace(go.Bar(x=Indiana['States'][0:1],
                    y=Indiana['Trade Balance'][0:1], marker=dict(color='blueviolet'),name="Indiana", legendgroup="Indiana", 
                       showlegend=False, hoverinfo='all',
                textposition='outside',
                texttemplate= '%{x}'), row=1, col=2)

fig_2.add_trace(go.Bar(x=Illinois['States'][0:1],
                    y=Illinois['Trade Balance'][0:1], marker=dict(color='green'),name="Illinois", legendgroup="Illinois", 
                       showlegend=False, hoverinfo='all',
                textposition='outside',
                texttemplate= '%{x}'), row=1, col=2)

fig_2.add_trace(go.Bar(x=Wisconsin['States'][0:1],
                    y=Wisconsin['Trade Balance'][0:1], marker=dict(color='black'),name="Wisconsin", legendgroup="Wisconsin", 
                       showlegend=False, hoverinfo='all',
                textposition='outside',
                texttemplate= '%{x}'), row=1, col=2)


# I made changes in the graphic in order to be more esthetic. Therefore, I change the background of the graphics, update the x axis to present date better visually, deleting the labels at the x axis in the bar graphic, putting a title, determine the range of the axis and adjusting the size of the graphics. 

# In[53]:


fig_2.update_layout(width=950, height=540, title = 'International trade for Michigan and surrouding states (M dollars)')
fig_2.update_xaxes(range=[df_trade['Date'].min(), df_trade['Date'].max()])
fig_2.update_yaxes(range=[900, 6600], row=1, col=1) #this line updates both yaxis, and yaxis2 range
fig_2.update_yaxes(range=[1200, 16600], row=2, col=1)
fig_2.update_yaxes(range=[-10700, 270], row=1, col=2)
fig_2.update_xaxes(showticklabels=False, row=1, col=2) #not to show the labels in the bar x axis
fig_2.update_layout(plot_bgcolor="white")

#To make the subtitles and the text that is going to be changing through time
fig_2.add_annotation(x=0.5, y=1, font= dict({
              'size': 12,
              'color': 'rgb(116, 101, 130)'}),
            align= 'center', text= 'Michigan growth rate: 0% exp. 0% imp.', 
                     xanchor='center',xref= 'paper', yanchor='bottom', yref='paper', showarrow=False )
fig_2.add_annotation(x=0.025, y=1, font= dict({'size': 16}),text= 'Exports', 
                     xanchor='center',xref= 'paper', yanchor='bottom', yref='paper', showarrow=False )
fig_2.add_annotation(x=0.8574999999999999, y=1 , font= dict({'size': 16}),text= 'Trade Balance', 
                     xanchor='center',xref= 'paper', yanchor='bottom', yref='paper', showarrow=False)
fig_2.add_annotation(x=0.025, y=0.5, font= dict({'size': 16}),text= 'Imports', 
                     xanchor='center',xref= 'paper', yanchor='bottom', yref='paper', showarrow=False)


# Then, I proceed with making the frames of the animation and also the buttons and the slider. 

# In[54]:


traces=[]
for i in range(0,len(fig_2.data)):
    traces.append(i)

#To make the buttons 
updatemenus= [{"buttons":[{"args": 
                           [None, {"frame": {"duration": 500,"redraw": True}, 
                                "fromcurrent": True, 
                                   "transition": {"duration": 300, "easing": "quadratic-in-out"}}],
                "label": "Play", "method": "animate"},
            {"args": [[None], {"frame": {"duration": 0,"redraw": True}, 
                               "mode": "immediate", "transition": {"duration": 0}}],
                "label": "Pause",
                "method": "animate"}],
               "direction": "left", "pad": {"r": 10, "t": 87}, "showactive": True, 
        "type": "buttons", "x": 0.1, "y": 0}]

#To make the slider, the step list is filled in the frame animation
sliders_dict = {
    "active": 0,
    "yanchor": "top",
    "xanchor": "left",
    "currentvalue": {
        "font": {"size": 20},
        "prefix": "Date:",
        "visible": True,
        "xanchor": "right"
    },
    "transition": {"duration": 300, "easing": "cubic-in-out"},
    "pad": {"b": 10, "t": 50},
    "len": 0.9,
    "x": 0.1,
    "y": 0,
    "steps": []
}


# In[55]:


#To do the frames the code is a loop that add trace by trace a point in each trace. 
list_of_frames = []
for k  in  range(1, len(Michigan)+1):
    exp_growth= ((Michigan.iloc[k-1]['Total Month Export']-Michigan.iloc[k-2]['Total Month Export'])
                 /Michigan.iloc[k-2]['Total Month Export'])
    imp_growth= ((Michigan.iloc[k-1]['Total Month Import']-Michigan.iloc[k-2]['Total Month Import'])
                 /Michigan.iloc[k-2]['Total Month Import'])
    list_of_frames.append(go.Frame(data= [go.Scatter(x=Michigan['Date'][:k],
                           y=Michigan['Total Month Export'][:k]),
                      go.Scatter(x=Ohio['Date'][:k],
                           y=Ohio['Total Month Export'][:k]),
                      go.Scatter(x=Indiana['Date'][:k],
                           y=Indiana['Total Month Export'][:k]),
                      go.Scatter(x=Illinois['Date'][:k],
                           y=Illinois['Total Month Export'][:k]),
                      go.Scatter(x=Wisconsin['Date'][:k],
                           y=Wisconsin['Total Month Export'][:k]),
                      go.Scatter(x=Michigan['Date'][:k],
                           y=Michigan['Total Month Import'][:k]),
                      go.Scatter(x=Indiana['Date'][:k],
                           y=Indiana['Total Month Import'][:k]),
                      go.Scatter(x=Ohio['Date'][:k],
                           y=Ohio['Total Month Import'][:k]),
                      go.Scatter(x=Illinois['Date'][:k],
                           y=Illinois['Total Month Import'][:k]),
                      go.Scatter(x=Wisconsin['Date'][:k],
                           y=Wisconsin['Total Month Import'][:k]),
                      go.Bar(x=Michigan['States'][k-1:k],
                           y=Michigan['Trade Balance'][k-1:k]),
                      go.Bar(x=Indiana['States'][k-1:k],
                           y=Indiana['Trade Balance'][k-1:k]),
                      go.Bar(x=Ohio['States'][k-1:k],
                           y=Ohio['Trade Balance'][k-1:k]),
                      go.Bar(x=Illinois['States'][k-1:k],
                           y=Illinois['Trade Balance'][k-1:k]),
                      go.Bar(x=Wisconsin['States'][k-1:k],
                           y=Wisconsin['Trade Balance'][k-1:k]),],
             layout=go.Layout(
            annotations= [{
            'text': "Michigan growth rate: "+ "{:.1%}".format(exp_growth)+' exp.'+" "+ "{:.1%}".format(imp_growth)+' imp.',
              'font': {
              'size': 12,
              'color': 'rgb(116, 101, 130)'},
            'showarrow': False,
            'align': 'center',
            'x': 0.5,
            'y': 1,}],), traces= traces,name= k))
    
    slider_step = {"args": [
        [k], # this one match the frame name in order to the text in the slider goes simultaneously with the animation
        {"frame": {"duration": 300, "redraw": True},
         "mode": "immediate",
         "transition": {"duration": 300}}
    ],
                   "label": str(Michigan.iloc[k-1]['year']+'-'+Michigan.iloc[k-1]['month']), # This one defines the sliders tick names
                   "method": "animate"} # same as with buttons
    ##Append to sliders_dict
    sliders_dict["steps"].append(slider_step)


# Finally I added the frames, the menus and the slider to the graphic.

# In[56]:


fig_2.update(frames=list(list_of_frames)),
fig_2.update_layout(updatemenus=updatemenus, sliders= [sliders_dict])
fig_2.show()

