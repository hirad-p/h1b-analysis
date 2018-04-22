import folium
import pandas as pd

# read the files into dataframes
h1b_frame = pd.read_csv('./data/h1b.csv') # dataset to large, please download from README.md
geo_frame = pd.read_csv('./data/state_geocodes.csv')

#### Applications by State ######
states = geo_frame['name'].tolist()
states_frame = geo_frame.drop('fips', axis=1)
states_frame['count'] = 0
states_frame = states_frame.set_index('name')

top_cities = h1b_frame['WORKSITE'].value_counts()[:100]

for worksite, count in top_cities.items():
    state = worksite.split(',')[1].strip().lower().title()
    states_frame.at[state, 'count'] += count
states_frame = states_frame[states_frame['count'] != 0]

# plot
map_data = '/Users/hirad.pourtahmasbi/Dev/h1b-analysis/data/map/us_states.json'
m = folium.Map(location=[37, -102], zoom_start=5)

m.choropleth(
 geo_data=map_data,
 name='2011-2016 H-1B Visa Applications',
 data=states_frame,
 columns=['code', 'count'],
 key_on='feature.id',
 fill_color='YlGn',
 fill_opacity=0.7,
 line_opacity=0.2,
 legend_name='# of Applications'
)
folium.LayerControl().add_to(m)

m.save('./graphs/applications_by_states.html')
