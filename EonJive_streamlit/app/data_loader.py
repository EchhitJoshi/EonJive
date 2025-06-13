import pandas as pd
import numpy as np
from sqlalchemy import create_engine

def get_mysql_con():
    """
    returns the mysql connection engine
    """
    return create_engine("mysql+pymysql://echhitjoshi:mz4DTyW6iyiJEnzdnmRg@database-eonjive.ctkiqcsu6x6o.us-east-1.rds.amazonaws.com")

def lower_columns(df):
    df.columns = [col.lower().replace(" ","_") for col in df.columns]
    return df

def read_sql(query,con):
    """
    query: sql query string
    con: connection engine
    returns extracted data with columns lowered and joined with '_'
    """
    with con.connect() as conn:
        raw_dat =  pd.read_sql(query,con = conn)
    
    raw_dat = lower_columns(raw_dat)
    print(raw_dat.info())
    return raw_dat
    
def create_datetime_columns(data,dt_col):
    """
    data: pandas DF
    dt_col: datetime column to parse dt values
    returns year, month(floored month/year), month_name, day_of_week, day_of_week_name, week( floored week)
    suffixed with _e for uniqueness
    """
    
    data[dt_col] = pd.to_datetime(data[dt_col])
    data['year_e'] = data[dt_col].dt.year
    data['month_e'] = data[dt_col].dt.to_period('M')
    data['month_name_e'] = data[dt_col].dt.month_name()
    data['day_of_week_e'] = data[dt_col].dt.day_of_week
    data['day_of_week_name_e'] = data[dt_col].dt.day_name()
    data['week_e'] = data[dt_col].dt.to_period('W-MON')
    data['week_e'] = data['week_e'].dt.start_time
    return data
    
        
    

    
