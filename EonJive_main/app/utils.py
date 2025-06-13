import pandas as pd





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