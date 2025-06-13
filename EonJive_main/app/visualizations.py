import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

"""
General functions for plots and facets
Some customizations for dashboarding, functions suffixed with _d
"""


def plot_pie(df:pd.DataFrame,col:str, facet_col:str = None):
    if facet_col:
        fig = px.pie(df,names = col,facet_col = facet_col)
    else:
        fig = px.pie(df,names = col)
    fig.show()
    
def plot_bar(df:pd.DataFrame,col:str, facet_col:str = None):
    if facet_col:
        return px.bar(df,x= col,facet_col = facet_col)
    else:
        return px.bar(df,x = col)