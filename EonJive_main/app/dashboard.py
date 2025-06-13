import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

from datetime import datetime,timedelta

from visualizations import *
from models import *

import arviz as az
import pymc as pm
import yaml


#Configs
px.defaults.template = "plotly_dark"


with open("config.yaml","r") as file:
    config = yaml.safe_load(file)

home_path = config['LOCAL_HOME_PATH']


#Data Reads
df = pd.read_csv(home_path + '/data/cleaned_data/pos_dd.csv')
df.columns = [col.replace("_e","") for col in df.columns]
df['source'] = np.where(df['source'] == 'dd','DoorDash',df['source'])


#### Grouped DFs

# Overall Sales
weekly_sales = df.groupby(['week']).agg(total_sales = ('subtotal','sum'),
                                        total_unit_sales = ('week','size'),
                                        average_sale_price = ('subtotal','mean') ).reset_index()
weekly_sales['week'] = pd.to_datetime(weekly_sales['week'])
weekly_sales_melt = pd.melt(weekly_sales,id_vars = ['week'],value_vars = ['total_sales','total_unit_sales','average_sale_price'], var_name = "weekly_stat_type",value_name= 'weekly_stat')
print(weekly_sales_melt.head())
weekly_stat_type = weekly_sales_melt['weekly_stat_type'].unique()
weekly_plots = {}
for val in weekly_stat_type:
    weekly_plots[val] = px.scatter(weekly_sales_melt[(weekly_sales_melt['weekly_stat_type'] == val) & (weekly_sales_melt['week'] > '2024-11-30')],x = 'week', y = 'weekly_stat',trendline = 'lowess')
    weekly_plots[val].update_traces(mode = 'lines+markers')
    weekly_plots[val].update_yaxes(matches = None)


# overall_trend = px.scatter(weekly_sales.query("week > '2024-11-30'"),x = 'week', y= 'total_sales',trendline = 'lowess')
# overall_trend.update_traces(mode = 'lines+markers')
# overall_trend.update_yaxes(matches = None)

# source proportion 
day_of_week_prop = df.groupby(['week','day_of_week_name','source']).agg(daily_sales = ('day_of_week_name','size'))
day_of_week_prop['weekly_prop'] = day_of_week_prop['daily_sales']/day_of_week_prop.groupby(['week','source']).size()
day_of_week_prop = day_of_week_prop.reset_index()


# daily sales
day_of_week_sales = df.groupby(['ts_date','day_of_week_name','day_of_week']).agg(total_sales = ('day_of_week','size')).reset_index()

model, coords = daywise_expected_total_sales_model(day_of_week_sales,'ts_date','total_sales',False)
trace = load_latest_model()
if trace:
    print("trace loaded")
today = [datetime.weekday(datetime.today())]
print(model.data_vars[0])
with model:
    pm.set_data({"day_idx":today})
    pred = pm.sample_posterior_predictive(trace)

# expected sales to be between:
min_sales = int(np.quantile(np.ravel(pred.posterior_predictive['obs'].mean(axis =0)),.2))
max_sales = int(np.quantile(np.ravel(pred.posterior_predictive['obs'].mean(axis =0)),.8))

print("expected sales to be between : ")
print(min_sales)
print("and ")
print(max_sales)





####


#### Main APP ####
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

app.layout = dbc.Container([
    
    
    html.H1("Pizza Palace Dashboard", className="text-center text-dark my-4"),

    html.Br(),
    html.Br(),

    html.Div([
    dbc.Card([
        dbc.CardHeader(f"Expected Sales Today ({datetime.today().strftime("%m-%d-%Y")})", className="text-black", style={"backgroundColor": "#EAB436", "color": "black"}), #EAB436
        dbc.CardBody([
            html.H5("Estimated Range", className="card-title"),
            html.P(f"Between {min_sales:,} and {max_sales:,} orders", className="card-text")
        ])
    ], className="mb-4 shadow", style={"width": "100%", "border": "2px solid #E5613D"})
], className="col-md-4"),

    html.Br(),

    # Overall Trends
    dbc.Container([html.H4("Weekly Stats", className = "text-left text-dark my-4"),
    dcc.Tabs([dcc.Tab(label = weekly_stat_type[i], children = dcc.Graph(id = 'weekly_trend'+val ,figure = weekly_plots[val])) for i,val in enumerate(weekly_stat_type) ]) ],fluid = True),
    

    html.Br(),
    
    #dbc.Container([html.Div(id='overall-trend-plot'),dcc.Graph(id = 'source_trend_overall',figure = overall_trend)],fluid = True),

    # Week-day trends
    html.Br(),
    html.H4("Daywise Sales Proportion From Different Point of Sales", className = "text-left text-dark my-4"),
    html.Br(),
    dbc.Container(dcc.Dropdown(df.source.unique(),id = 'source_dropdown',placeholder = 'Please select the service to check sales proportions every week'),className="bg-light shadow rounded", fluid = True),
    dbc.Container([html.Div(id='trend-plot'),
                            dcc.Graph(id = 'source_trend_weekly_output')
                            ],fluid = True),

    
    # Expected Sales from Pymc model
    html.Br(),
  





],fluid = True)


#### Main APP END ####



## Callbacks
@callback(
    Output(component_id = 'source_trend_weekly_output',component_property = 'figure'),
    Input(component_id = 'source_dropdown',component_property = 'value')
)
def update_source_graph(source_value):
    source_weekly_dat = day_of_week_prop[day_of_week_prop['source'] == source_value]
    fig = px.line(source_weekly_dat.query('week > "2024-11-26" & week < "2025-05-13"'),x = 'week',y = 'weekly_prop',color = 'day_of_week_name',markers = '-o-')
    fig.update_layout(yaxis = {'matches':None})
    return fig