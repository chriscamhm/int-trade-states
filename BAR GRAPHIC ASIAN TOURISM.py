#!/usr/bin/env python
# coding: utf-8

# <h1><center> Asian tourism in Colombia: Quarterly Top 8 from 2015 to 2019 </center></h1>
# 
# <h1><left> General Objective </left></h1>

# The following code shows the process from data collection to the final graph. The objective of this part of the project is to look at the evolution of **Asian tourism in Colombia**. For this purpose, an animated bar graph was used that changes over time and shows the 8 countries with the most entries to Colombia quarter by quarter from 2015 to the end of 2019. The data from 2015 to 2017 were extracted from the Migración Colombia website. which are monthly so they were grouped together to see it quarterly. While for 2018 and 2019 they were downloaded from the Tableau dashboards provided by Migración Colombia. The links are the following:
# 
# **Migration data from 2015 to 2017:** https://www.migracioncolombia.gov.co/planeacion/estadisticas/historico-estadisticas
# 
# **Data for 2018:** https://public.tableau.com/profile/migraci.n.colombia#!/vizhome/TablasdeSalidas2018/Inicio
# 
# **Data for 2019:** https://public.tableau.com/profile/migraci.n.colombia#!/vizhome/FlujosMigratorios-2019/Inicio
# 
# **Flag images database:** https://query.data.world/s/ikdif4hs6ic7uyqrszeotioo5sjj3x

# In[1]:


import pandas as pd
import numpy as np
import re

import urllib3
import requests
import csv

from bs4 import BeautifulSoup


urllib3.disable_warnings()


# <h1><left> Migration data from 2015 to 2017 </left></h1>
# 
# I started with the data from 2015 to 2017 published in Migración Colombia. This data is monthly and to avoid downloading the files one by one, use web scrapping techniques. For each year it was a different link, therefore, through a loop in the link, the year changed and from that link I extracted the monthly bases one by one.
# Using regex, it identified only the links corresponding to the downloads of the monthly files. In the end, having the urls that interested me, I extracted the year and the corresponding month from these to finally put together everything extracted in a base for the 3 years.

# In[2]:


links = []
date =[]
urls= []
for i in (2015,2016,2017):
    url_page = 'https://www.migracioncolombia.gov.co/planeacion/estadisticas/historico-estadisticas/boletin-migratorio-{}'.format(i)
    page = requests.get(url_page,verify=False).text 
    soup = BeautifulSoup(page, "lxml") 
    contenido = soup.find('div', attrs={'id': 'k2Container'}) 
    items = contenido.find_all('a')
    it= str(items)
    urls2 = re.findall(r'(<a href="[^"]*" title="[^"]*">)', it)
    urls.extend(urls2)
    for k in urls2:
        html = str(k)
        soup = BeautifulSoup(html) #Para leer el html del nuevo string
    
        for a in soup.find_all('a', href=True):
            links.append(a['href'])
        date.append(re.findall(r'(\w+\s\d{4})', k)[0]) #Extrae el mes y el año de cada enlace
    
    


# In[3]:


urls = pd.Series(urls)
links = pd.Series(links)
año = pd.Series(date).str.split(' ', expand=True).get(1)
mes = pd.Series(date).str.split(' ', expand=True).get(0)

extract = pd.concat([urls,links,año,mes], axis=1, keys=['urls','links','año','mes'])
extract['año'] = extract['año'].fillna('0')


# In[4]:


'https://www.migracioncolombia.gov.co'+links[0]


# In[5]:


import urllib.parse
l = 'https://www.migracioncolombia.gov.co'
data = pd.read_excel(l+urllib.parse.quote(links[0]),sheet_name="CUADRO 3") #cuadro 3 es el nombre de la hoja con los datos
data.drop(data.columns[0], axis=1, inplace=True)
data = data.iloc[3:]
data['Año'] = [ año.iloc[0] for i in range(len(data)) ]
data['Mes'] = [ mes.iloc[0] for i in range(len(data))]
data


# Having an initial base for 2015, I made a loop to extract the other bases and then concatenate it with the one for 2015, creating a total base for the 3 years.

# In[6]:


for link,año,mes in zip(extract.links[1:],extract.año[1:],extract.mes[1:]):
        datasets = pd.read_excel(l+urllib.parse.quote(link),sheet_name="CUADRO 3")
        datasets.drop(datasets.columns[0], axis=1, inplace=True)
        datasets = datasets.iloc[3:]
        datasets['Año'] = [año for i in range(len(datasets))]
        datasets['Mes'] = [mes for i in range (len(datasets))]
        data = pd.concat([data,datasets], axis=0)
data.info()


# <h1><left> Data from 2018 to 2019 </left></h1>
# 
# For 2018 and 2019, the page stopped publishing monthly databases to focus on its dashboards in Tableau. I didn't know and couldn't extract the information from those control panels, so I had to download both databases.

# In[7]:


bd= pd.read_csv('Mapa_Nacionalidad_E_Datos_completos_data.csv', sep=";")
bd


# In[8]:


bd.info()


# In[9]:


#I filter by Asia and group the records to add them by month, this for 2018
bd2= bd.loc[(bd['Entrada Salida (copia)']=='Entradas')& (bd['Region Nacionalidad']=='Asia')]
bd3= bd2.groupby(['País Nacionalidad','Año','Meses1']).aggregate({'Femenino':np.sum, 
                                                            'Masculino': np.sum, 'Cantidad de filas (agregadas)':np.sum,}).reset_index()


# In[10]:


#I repeat the process for 2019 and concatenate with 2018.
bd19= pd.read_csv('Meses_E_Datos_completos_data .csv', sep=";")
bd192= bd19.loc[(bd19['Entrada Salida (copia)']=='Entradas')& (bd19['Region Nacionalidad']=='Asia')]
bd193= bd192.groupby(['País Nacionalidad','Año','Meses1']).aggregate({'Femenino':np.sum, 
                                                            'Masculino': np.sum, 'Cantidad de filas (agregadas)':np.sum}).reset_index()
bd3 = pd.concat([bd3,bd193], axis=0)
bd3.rename(columns={'País Nacionalidad': 'Nacionalidad', 'Meses1': 'Mes', 
                      'Cantidad de filas (agregadas)': 'Total'}, inplace=True)
bd3


# In[11]:


#I extract the countries in a list to cross them with the other base since in the other I cannot filter by region
asia= list(bd3['Nacionalidad'].unique())
data2= data[data['Unnamed: 1'].isin(asia)]
list(data2['Unnamed: 1'].unique())


# In[12]:


#from the base from 2015 to 2017 I rename the columns and organize them to concatenate later
data2.rename(columns={'Unnamed: 1': 'Nacionalidad', 'Unnamed: 2': 'Femenino', 
                      'Unnamed: 3': 'Masculino', 'Unnamed: 4': 'Total'}, inplace=True)
data2= data2[['Nacionalidad', 'Año','Mes','Femenino','Masculino', 'Total']]
data2


# In[13]:


#I joined both bases, the one from 2015 to 2107 and the one from 2018-2019
data3 = pd.concat([data2,bd3], axis=0).reset_index()
data3.info()


# In[14]:


#I returned Date to datetime type and reshaped the base to parse by quarter, making sure the types are correct
import locale
locale.setlocale(locale.LC_ALL,'es_ES.UTF-8')
data3['Date']= data3['Mes'].map(str) + '-'+ data3['Año'].map(str)
data3['Date']= pd.to_datetime(data3["Date"], infer_datetime_format=True, format="%B-%Y")
data3['Date']= data3['Date'] + pd.offsets.MonthEnd(0) 
data3.sort_values(['Date'], ascending=True, inplace=True)
data3['Qtr'] = pd.PeriodIndex(data3['Date'], freq='Q')
data3["Femenino"] = data3["Femenino"].replace('                    -  ',0)
data3["Masculino"] = data3["Masculino"].replace('                    -  ',0)
data3["Total"] = data3["Total"].replace('                    -  ',0)
data3


# In[15]:


data3.info()


# In[16]:


#A final base grouping by quarter
datafinal= data3.groupby(['Nacionalidad', 'Qtr']).aggregate({'Femenino':np.sum,'Masculino': np.sum, 'Total':np.sum}).reset_index()
datafinal


# <h1><left> ISO codes for countries and Flags </left></h1>
# 
# I found a page with the flags of the world, unfortunately the graphics were not readable and I had to use another one. However, the process helped me extract the ISO codes and be able to create a database with the URLs of the flags on Wikipedia, which ultimately did help me in the graphics.

# In[17]:


from PIL import Image
import requests
from io import BytesIO

response = requests.get("https://www.countryflags.io/be/shiny/64.png")
img = Image.open(BytesIO(response.content))
img
#I leave the code as a reference to have the flags, but first you have to have the ISO codes
#images=[]
#for i in asiap['Codigo'].tolist():
    #images.append("https://www.countryflags.io/{}/shiny/64.png".format(i))
#images = pd.Series(images)
#asiap['image'] = images.values


# In[1]:


#Return the list made previously to series to be able to join it with other abses and thus get the URL's of the flags
asiap = pd.Series(asia).to_frame()

asiap.rename(columns={0: 'Pais'}, inplace=True)
asiap


# In[19]:


#Change the name of certain countries so that in the merge they have their corresponding values
countries=["República de Armenia", "República de Corea",
"República Árabe Siria",
"República Árabe de Yemen","Brunei Darussalam",
           "República de Tayikistán", 'República Democrática Popular Lao','República Democrática de Timor Oriental', 
          'República Democrática Popular de Corea']
nuevo_c= ["Armenia", "Corea del Sur", "Siria", "Yemen","Brunei","Tayikistán", "Laos",'Timor Oriental', 'Corea del Norte']
asiap['Pais'] = asiap['Pais'].replace(countries, nuevo_c)
asiap


# In[20]:


#This table from Wikipedia contains the two-character ISO codes which I used to loop the link,
# which unfortunately did not help me, but the codes helped me to merge with the links that did help
wiki=pd.read_html('https://es.wikipedia.org/wiki/ISO_3166-2',header=0)[0]
wiki.rename(columns={'Entrada(clic para ver los códigos)': 'Codigo', 
                     'País o Territorio(en cursiva el nombre oficial en la ONU y en la norma ISO)': 'Pais'}, inplace=True)
#Change the name of certain countries to do the merge correctly
countries=["BaréinBahrein", "BangladésBangladesh",
"República Popular ChinaChina",
"Emiratos Árabes Unidos","IrakIraq",
           "IránIrán (República Islámica de)", 'Iran (Islamic Republic of)','Myanmar [nota 3]',
          'Palestina, Estado de', 'CatarQatar', 'SiriaRepública Árabe Siria','VietnamViet Nam', 'ButánBhután',
          'BrunéiBrunei Darussalam', 'LaosRepública Democrática Popular Lao', 'Timor OrientalTimor-Leste', 
           'Corea del SurCorea (República de)', 'Corea del NorteCorea (República Popular Democrática de)']
nuevo_c= ["Bahréin", "Bangladesh", "China", "Emiratos Árabes","Iraq","Irán", "Iran",'Myanmar', 'Palestina',
       'Qatar', 'Siria','Vietnam', 'Bután','Brunei', 'Laos', 'Timor Oriental', 'Corea del Sur', 'Corea del Norte' ]
wiki['Pais'] = wiki['Pais'].replace(countries, nuevo_c)
wiki.iloc[5:150]


# In[21]:


asiap = asiap.merge(wiki[['Codigo', 'Pais']], how = 'left',
                on='Pais')
#Taiwan is in another base because it is a province of China and not recognized so I added it manually
#Myanmmar didn't want to cross me so I added it
asiap['Codigo'] = asiap.apply(lambda x: 'TW' if x['Pais'] == 'Taiwán' else ('MM' if x['Pais']=='Myanmar' else x['Codigo']), axis=1)
asiap


# In[22]:


#The base that is in dataworld with the links to the flags in Wikipedia
dfl= pd.read_csv('https://query.data.world/s/ikdif4hs6ic7uyqrszeotioo5sjj3x')
dfl


# In[23]:


#The base with the ISO codes but in English because the previous base the names of the countries are in English
df2=pd.read_html('https://en.wikipedia.org/wiki/ISO_3166-2',header=0)[0]
df2.rename(columns={'Country name (using title case)': 'Country', 
                     'Entry (click to view codes)': 'Codigo'}, inplace=True)
#Replace the names of some countries so that none are missing
#and the crossing is perfect, at least for the Asian countries that are being studied
countries=["Brunei Darussalam", "Iran (Islamic Republic of)",
"Palestine, State of",
"Lao People's Democratic Republic","Korea, Republic of",
           "Syrian Arab Republic", 'Taiwan, Province of China [note 2]','Viet Nam', "Korea (Democratic People's Republic of)"]
nuevo_c= ["Brunei", "Iran", "Palestine", "Laos","South Korea","Syria", "Republic of China",'Vietnam', 'North Korea']
df2['Country'] = df2['Country'].replace(countries, nuevo_c)
df2


# In[24]:


#A new database with the url of the images and the codes
df3 = dfl.merge(df2[['Codigo', 'Country']], how = 'left',
                on='Country')

df3


# In[25]:


#Merge of countries of interest with links through the ISO code
asiap = asiap.merge(df3[['Codigo', 'ImageURL']], how = 'left',
                on='Codigo')
asiap


# In[26]:


#In the case of Hong Kong and East Timor that are not in the flag base, I placed them "manually"
asiap['ImageURL'] = asiap.apply(lambda x: 'https://en.wikipedia.org/wiki/Hong_Kong#/media/File:Flag_of_Hong_Kong.svg' 
                              if x['Codigo'] == 'HK' 
                                else ('https://es.wikipedia.org/wiki/Timor_Oriental#/media/Archivo:Flag_of_East_Timor.svg' 
                                      if x['Codigo']=='TL' else x['ImageURL']), axis=1)
asiap['Codigo'] = asiap['Codigo'].apply(lambda x: x.lower())
asiap


# In[27]:


#To see the base with the flags
from IPython.core.display import HTML 
def path_to_image_html(path):
    return '<img src="'+ path + '" width="48" >'
HTML(asiap.to_html(escape=False ,formatters=dict(ImageURL=path_to_image_html)))


# In[28]:


#Change some names in the entry database so that they fit well with the flag base that was created
countries=["República de Armenia", "República de Corea",
"República Árabe Siria",
"República Árabe de Yemen","Brunei Darussalam",
           "República de Tayikistán", 'República Democrática Popular Lao','República Democrática de Timor Oriental',
          'República Democrática Popular de Corea']
nuevo_c= ["Armenia", "Corea del Sur", "Siria", "Yemen","Brunei","Tayikistán", "Laos",'Timor Oriental', 
          'Corea del Norte']
datafinal['Nacionalidad'] = datafinal['Nacionalidad'].replace(countries, nuevo_c)
datafinal



# In[29]:


#A database with input data and images
data_img= datafinal.merge(asiap, how='left', left_on='Nacionalidad', right_on='Pais')
data_img.drop('Pais', axis=1, inplace=True)
data_img


# <h1><left> Animated graphic </left></h1>
# 
# Finally, with the databases I proceeded to create the animated bar graph by sex. For this I made a graph with two subplots, one for the female sex and the other for the male sex. The final database was in quarters, therefore the total frames of the animation will be 20. I chose to show the top 8 so that the flags and numerical data could be seen since for the 9th and 10th positions the bars are already They are very small and not noticeable.

# In[30]:


#list with the quarters in order to make the loop with the frames
lista_tr = data_img.sort_values('Qtr', ascending = True)
lista_tr = lista_tr['Qtr'].astype(str)
lista_tr = list(lista_tr.unique())
lista_tr


# In[31]:


#import libraries for graphics
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
#A graph with two basic subplots
fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.05, print_grid=True, vertical_spacing=0.02)


# In[32]:


#For the first frame of the bar graph for the female sex corresponding to the first quarter of 2015
frame1 = data_img[data_img['Qtr'] == '2015Q1'].reset_index()

##Sort the data and choose the top 8 which can be modified if you want a broader top
top_entries = 8 
frame1 = frame1.sort_values('Femenino', ascending = False).iloc[:top_entries, :].reset_index()

##This is used to order the data in such a way that in the bar graph the country with the highest entries comes first
frame1 = frame1.sort_values('Femenino', ascending = True)

#3 Add the graph to the subplot, choose the color of the bars and the text font type
fig.add_trace(go.Bar(
  x = frame1['Femenino'],
  y = frame1['Nacionalidad'],
  marker_color = 'indianred',
  hoverinfo = 'all', 
  textposition = 'inside', 
  texttemplate = '%{y} <br>%{x:}', 
    textfont= dict(family= 'Luminari', color= 'white'),
  orientation = 'h', name= 'Femenino', textangle=0), 
row=1, col=1)


# In[33]:


#Do the same procedure but this time for the male sex
frame1m = data_img[data_img['Qtr'] == '2015Q1'].reset_index()
frame1m = frame1m.sort_values('Masculino', ascending = False).iloc[:top_entries, :].reset_index()
frame1m = frame1m.sort_values('Masculino', ascending = True)
fig.add_trace(go.Bar(
  x = frame1m['Masculino'],
  y = frame1m['Nacionalidad'],
  marker_color = 'darkslateblue',
  hoverinfo = 'all', 
  textposition = 'inside', 
  texttemplate = '%{y}<br>%{x:}', 
    textfont= dict(family= 'Luminari', color= 'white'),
  orientation = 'h', textangle=0, name='Masculino'), 
row=1, col=2)


# In[34]:


#Add layout details to the chart such as titles, axis range, and background
fig.update_layout(width=970, height=580, title = '<b>Top 8 entrada de viajeros a Colombia originarios de Asia por trimestre (2015-2019)<b>', 
                  titlefont=dict({'family': 'Lithos Pro', 'color': 'black', 'size': 26}))
fig.update_xaxes(range=[data_img['Femenino'].min()-30, data_img['Femenino'].max()], row=1, col=1)
fig.update_xaxes(range=[data_img['Masculino'].min(), data_img['Masculino'].max()], row=1, col=2)
fig.update_yaxes(showticklabels=False) #not to show the labels in the bar x axis
fig.update_layout(plot_bgcolor="white")

#A loop to add the images of the flag of each country in the top 8 in their respective position
#This is for the male sex
for i in range(0, len(frame1m)):
    fig.add_layout_image(dict(source=frame1m['ImageURL'][i],
                           x=0.458,
                           y=0.976-(0.124833*i), #en cada loop la posición de la imagen baja 0.12483 pixeles con respecto a la anterior 
                              sizex= 0.057,
                              sizey=2))  
#For the female sex
for i in range(0, len(frame1)):
    fig.add_layout_image(dict(source=frame1['ImageURL'][i],
                           x=0,
                           y=0.90-(0.124833*i),
                              sizex= 0.057,
                              sizey=2,
                              xanchor='right',xref= 'paper', yanchor='bottom', yref='paper')) 


#Add the subtitles and the annotation of the total tourism in Asia that will change each frame
fig.add_annotation(x=0.38, y=1.05, font= dict({
              'size': 14,
              'color': 'rgb(116, 101, 130)', 
                'family': 'Lithos Pro'}),
            align= 'center', text= 'Total entradas de personas originarias de Asia para 2015Q1: 14577', 
                     xanchor='center',xref= 'paper', yanchor='bottom', yref='paper', showarrow=False )
fig.add_annotation(x=0.025, y=1, font= dict({'size': 19, 'family': 'Lithos Pro', 'color': 'black'}),text= 'Femenino', 
                     xanchor='center',xref= 'paper', yanchor='bottom', yref='paper', showarrow=False)
fig.add_annotation(x=0.8574999999999999, y=1 , font= dict({'size': 19, 'family': 'Lithos Pro', 'color': 'black'}),text= 'Masculino', 
                     xanchor='center',xref= 'paper', yanchor='bottom', yref='paper', showarrow=False)


# In[35]:


#Add play & pause buttons while setting the duration of each frame
updatemenus= [{"buttons":[{"args": 
                           [None, {"frame": {"duration": 1850,"redraw": True}, 
                                "fromcurrent": True, 
                                   "transition": {"duration": 400, "easing": "linear-in-out"}}],
                "label": "Play", "method": "animate"},
            {"args": [[None], {"frame": {"duration": 0,"redraw": False}, 
                               "mode": "immediate", "transition": {"duration": 0}}],
                "label": "Pause",
                "method": "animate"}],
               "direction": "left", "pad": {"r": 10, "t": 87}, "showactive": True, 
        "type": "buttons", "x": 0.1, "y": 0}]


# In[36]:


#Add time slider
sliders_dict = {
    "active": 0,
    "yanchor": "top",
    "xanchor": "left",
    "currentvalue": {
        "font": {"size": 17, 'family':'Lithos Pro'},
        "prefix": "Trimestre:",
        "visible": True,
        "xanchor": "right"
    },
    "transition": {"duration": 400, "easing": "linear-in"},
    "pad": {"b": 10, "t": 50},
    "len": 0.8,
    "x": 0.2,
    "y": 0,
    "steps": []}


# In[37]:


#Make the frames
top_entries = 8
list_of_frames = []
for i in lista_tr:
    
    #Filtrar por trimestre
    qtr_data = data_img[data_img['Qtr'] == i]
    asia_sum= qtr_data['Total'].sum()
    ##Tener el top 8 para cada sexo
    qtr_data_f = qtr_data.sort_values('Femenino', ascending=False).iloc[:top_entries,:].reset_index()
    qtr_data_m = qtr_data.sort_values('Masculino', ascending=False).iloc[:top_entries,:].reset_index()
    qtr_data_f = qtr_data_f.sort_values('Femenino', ascending=True)
    qtr_data_m = qtr_data_m.sort_values('Masculino', ascending=True)
    #El loop para posicionar las imagenes de las banderas en cada frame
    images= []
    for k in range(0, len(qtr_data_m)):
        images.append(dict(source=qtr_data_m['ImageURL'][k],
                           x=0.458,
                           y=0.976-(0.124833*k),
                              sizex= 0.057,
                              sizey=2)) 
    for j in range(0, len(qtr_data_f)):
        images.append(dict(source=qtr_data_f['ImageURL'][j],
                           x=0,
                           y=0.90-(0.124833*j),
                              sizex= 0.057,
                              sizey=2,
                              xanchor='right',xref= 'paper', yanchor='bottom', yref='paper')) 
    #Anexarlo a la lista de frames y el texto irá cambiando mostrando el total de entradas desde asia
    list_of_frames.append(go.Frame(
            layout=go.Layout(images= images,
            annotations= [{
            'text': "Total entradas de personas originarias de Asia para "+ '{}'.format(i)+': '+ "{:}".format(asia_sum),
              'font': {
              'size': 14,
              'color': 'rgb(116, 101, 130)', 'family': 'Lithos Pro'},
            'showarrow': False,
            'align': 'center',
            'x': 0.38,
            'y': 1.05,}]),
        data=[
            go.Bar(
                x=qtr_data_f['Femenino'],
                y=qtr_data_f['Nacionalidad'],
                marker_color = 'indianred',
                hoverinfo = 'all', 
                textposition = 'inside', 
                texttemplate = '%{y} <br>%{x:}', 
                textfont= dict(family= 'Luminari', color= 'white'),
                orientation = 'h', textangle=0),
            go.Bar(x=qtr_data_m['Masculino'],
                  y=qtr_data_m['Nacionalidad'],
                  marker_color = 'darkslateblue',
                  hoverinfo = 'all', 
                  textposition = 'inside', 
                  texttemplate = '%{y}<br>%{x:}', 
                  textfont= dict(family= 'Luminari', color= 'white'),
                  orientation = 'h', textangle=0)],
                traces= [0,1],name= str(i)))
        

    # Unir los pasos del slider con cada frame
    slider_step = {"args": [
        [i], 
        {"frame": {"duration": 400, "redraw": True},
         "mode": "immediate",
         "transition": {"duration": 400}}
    ],
                   "label": str(i), # Para mostrar el trimestre del frame en el slider
                   "method": "animate"} 
    sliders_dict["steps"].append(slider_step)


# In[38]:


#Añadir la lista de frames y sliders a la figura
fig.update(frames=list(list_of_frames)),
fig.update_layout(updatemenus=updatemenus, sliders= [sliders_dict])
fig.show()


# In the graph you can see how for most quarters the top 8 is occupied in both sexes by the same countries, in some quarters Thailand enters the top. On the other hand, it can be seen how China and India are positioning themselves as those with the highest income, at least for the male sex. Which is a reflection of the growth that bilateral relations in business and tourism have had between Colombia and China and India.

# In[52]:


import datapane as dp
table    = dp.Table(data_img)
markdown = dp.Markdown("""En el gráfico se puede apreciar como para la mayoría de trimestres el top 8 de viajeros provenientes de Asia hacia Colombia es ocupado en ambos sexos por los mismos países, alguno que otro trimestre Tailandia entra en el top. Por otro lado, se puede apreciar como China e India se van posicionando como los de mayores entradas al menos para el sexo masculino. Esto último es un reflejo del crecimiento que han tenido las relaciones bilaterales en materia de negocios y turismo entre Colombia con China e India.""")
plot     = dp.Plot(fig)

report = dp.Report(markdown,plot,table)
report.publish(name = 'Top 8 entrada de viajeros a Colombia originarios de Asia por trimestre (2015-2019)')


# In[ ]:




