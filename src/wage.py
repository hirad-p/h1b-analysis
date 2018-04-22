import matplotlib 
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter

# read the files into dataframes
h1b_frame = pd.read_csv('../data/h1b.csv') # dataset to large, please download from README.md

def wages():
    title = 'H-1B Salary From 2011 to 2016'
    df = h1b_frame[(h1b_frame['PREVAILING_WAGE'] < 400000) & (h1b_frame['CASE_STATUS'] == 'CERTIFIED')]
    df = df.dropna(axis=0, how='all')

    with plt.style.context('fivethirtyeight'):
        fig, ax = plt.subplots(1, 1, figsize=(10, 4))
        ax.hist(df['PREVAILING_WAGE'], bins=200, edgecolor='#ffffff', color='#169630')
    plt.xlim([15000, 200000])

    plt.xlabel('Salary',size=10)
    plt.ylabel('# of Applicants', size=20)
    ax.set_title(title)

    plt.savefig('../graphs/' + title + '.png')
    plt.show()

wages()