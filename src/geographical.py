import folium
import json
import numpy as np
import pandas as pd
import plotly.plotly as py
import plotly.figure_factory as ff
import plotly.graph_objs as go

from geopy.geocoders import Nominatim

geolocator = Nominatim(scheme='http')

# read the files into dataframes
h1b_frame = pd.read_csv('../data/h1b.csv') # dataset to large, please download from README.md


#### Applications by State #####
####    Certified / Map    #####
def number_by_states(frame):
    # data transforming
    geo_frame = pd.read_csv('../data/state_geocodes.csv')

    states_frame = geo_frame.drop('fips', axis=1)
    states_frame['count'] = 0
    states_frame = states_frame.set_index('name')

    t = frame.loc[frame['CASE_STATUS'] == 'CERTIFIED']['WORKSITE'].value_counts()
    
    for worksite, count in t.items():
        locations = worksite.split(',')
        state = locations[len(locations)-1].strip().lower().title()
        if state in states_frame.index:
            states_frame.at[state, 'count'] += count
    states_frame = states_frame[states_frame['count'] != 0]

    # data plotting
    map_data = '/Users/hirad.pourtahmasbi/Dev/h1b-analysis/data/map/us_states.json'
    m = folium.Map(location=[37, -102], zoom_start=4)

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

    m.save('../graphs/applications_by_states.html')


def number_by_state(frame, state):
    print(f'{state} - Applications by County')
    print('Transforming Data..')
    data = frame[frame['CASE_STATUS'] == 'CERTIFIED'][frame['WORKSITE'].str.contains(state.upper())]
    data = data[np.isfinite(data['lat']) & np.isfinite(data['lon'])]
    fips_frame = pd.read_csv('../data/county_geocodes.csv', dtype=str)
    fips_frame = fips_frame.set_index('Name')
    fips_frame['fips'] = fips_frame['State'] + fips_frame['County']
    state_code = fips_frame.at[state, 'State']
    fips_frame = fips_frame[fips_frame['State'] == state_code]

    print('Setting up dataframe...')
    columns = ['name', 'count', 'lat', 'lon', 'county', 'fips']
    df = pd.DataFrame(columns=columns)
    df = df.set_index('name')
   
    i = data.shape[0]
    print('Starting Iterations....')
    for index, row in data.iterrows():
        city = row['WORKSITE']
        if city in df.index:
            df.at[city, 'count'] += 1
        else:
            lat = row['lat']
            lon = row['lon']
            county = get_county( (lat, lon) )
            if county in fips_frame.index:
                fips_code = fips_frame.at[county, 'fips']
            else:
                print(f'Unable to process {county}')
            df.loc[city] = [1, lat, lon, county, fips_code]
        print(f'------- {i} -------')
        i -= 1

    df = df[df['count'] != 0]
    df = df.sort_values(by='count')
    # print(df)

    values = df['count'].tolist()
    fips = df['fips'].tolist()

    colorscale = [
        'rgb(193, 193, 193)',
        'rgb(239,239,239)',
        'rgb(195, 196, 222)',
        'rgb(144,148,194)',
        'rgb(101,104,168)',
        'rgb(65, 53, 132)'
    ]

    scope = None
    if state is 'California':
        scope = 'CA'
    elif state is 'New York':
        scope = 'NY'
    elif state is 'Texas':
        scope = 'TX'

    fig = ff.create_choropleth(
        fips=fips, values=values, scope=[scope],
        binning_endpoints=[10, 100, 500, 1000, 10000], colorscale=colorscale,
        county_outline={'color': 'rgb(255,255,255)', 'width': 0.5}, round_legend_values=True,
        legend_title='# of Applications', title='Applications by County'
    )

    py.image.save_as(fig, filename=f'../graphs/{scope}.png')


def employer_by_state(frame):
    geo_frame = pd.read_csv('../data/state_geocodes.csv')

    states_frame = geo_frame.drop('fips', axis=1)
    states_frame['top_employer'] = ''
    states_frame['count'] = 0
    states_frame = states_frame.set_index('name')

    for state in states_frame.index:
        print(f'Computing {state}...')
        data = frame[frame['CASE_STATUS'] == 'CERTIFIED'][frame['WORKSITE'].str.contains(state.upper())]
        counts = data['EMPLOYER_NAME'].value_counts()
        top_employer = counts.keys().tolist()[0]
        top_count = counts.tolist()[0]
        states_frame.at[state, 'top_employer'] = top_employer
        states_frame.at[state, 'count'] = top_count

    states_frame = states_frame.sort_values('count')
    # print(states_frame)
    states_frame.to_csv('../data/top_employer_by_state.csv')

    X = states_frame[['code']].values.flatten()
    Y = states_frame[['count']].values.flatten()
    text = states_frame[['top_employer']].values.flatten()

    trace_states = go.Bar(
        x=X, 
        y=Y, 
        name="State", 
        text=text, 
        textposition = 'auto')

    data = [trace_states]
    layout = go.Layout(
        title="H1Bs by State",
        barmode='stack'  
    )
    fig = go.Figure(
        data=data, 
        layout=layout
    )
    py.iplot(fig, filename='stacked-bar')
    py.image.save_as(fig, filename=f'../graphs/employer_by_state.png')


def salary_by_employer(frame):
    data = frame[frame['CASE_STATUS'] == 'CERTIFIED']
    df = pd.read_csv('../data/top_employer_by_state.csv')
    df = df.set_index('name')

    for state, row in df.iterrows():
        employer = row['top_employer']
        wages = data[data['WORKSITE'].str.contains(state.upper())][data['EMPLOYER_NAME'] == employer]['PREVAILING_WAGE']
        df.at[state, 'average_salary'] = round(wages.mean(), 2)
        
    map_data = '/Users/hirad.pourtahmasbi/Dev/h1b-analysis/data/map/us_states.json'
    m = folium.Map(location=[37, -102], zoom_start=4)

    m.choropleth(
        geo_data=map_data,
        name='2011-2016 Average Salary of Top Employer per State',
        data=df,
        columns=['code', 'average_salary'],
        key_on='feature.id',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Average Salary'
    )
    folium.LayerControl().add_to(m)
    m.save('../graphs/salary_by_employer_by_state.html')

    print(df.style)


def get_county(coordinate):
    location = geolocator.reverse(f'{coordinate[0]}, {coordinate[1]}')
    return location.raw['address']['county']


# number_by_states(h1b_frame)
# number_by_state(h1b_frame, 'California')
# number_by_state(h1b_frame, 'Texas')
# number_by_state(h1b_frame, 'New York')
# employer_by_state(h1b_frame)
salary_by_employer(h1b_frame)