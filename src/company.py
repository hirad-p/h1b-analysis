import numpy as np
import pandas as pd
import plotly.plotly as py
import plotly.figure_factory as ff
import plotly.graph_objs as go


h1b_frame = pd.read_csv('../data/h1b.csv') # dataset to large, please download from README.md

def infoaxe():
    frame = h1b_frame[h1b_frame['CASE_STATUS'] == 'CERTIFIED'][h1b_frame['EMPLOYER_NAME'] == 'INFOAXE INC.']
    frame.to_csv('../data/infoaxe.csv')
    print(frame)

def mapr():
    frame =  pd.read_csv('../data/mapr.csv')
    # frame = frame.loc[frame['CASE_STATUS'] == 'CERTIFIED'].groupby('YEAR').count()
    
 
    columns = ['count', 'wages']
    index = [ 2011, 2012, 2013, 2014, 2015, 2016]
    df = pd.DataFrame(index=index,columns=columns)
    df['count'] = 0
    df['wages'] = 0
    print(df)

    for index, row in frame.iterrows():
        year = int(row['YEAR'])
        wage = row['PREVAILING_WAGE']
        
        df.at[ year, 'count'] += 1
        df.at[ year, 'wages'] += wage
        
    df['average_wage'] = round(df['wages'] / df['count'], 2)
    df = df.drop([2011])    

    print(df)

    X = df.index.values.flatten()
    Y = df[['count']].values.flatten()
    text = df[['average_wage']].values.flatten()
    bar = go.Bar(x=X, 
                 y=Y, 
                 name="MapR Applications", 
                 text=text, 
                 textposition = 'auto')

    data = [bar]
    layout = go.Layout(
        title="MapR Applications per Year",
        barmode='stack'  
    )
    fig = go.Figure(
        data=data, 
        layout=layout
    )
    py.image.save_as(fig, filename=f'../graphs/mapr.png')

def jitterbit():
    frame = h1b_frame[h1b_frame['CASE_STATUS'] == 'CERTIFIED'][h1b_frame['EMPLOYER_NAME'] == 'JITTERBIT, INC.']
    frame.to_csv('../data/jitterbit.csv')
    print(frame)


mapr()
