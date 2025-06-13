import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import pymc as pm
import arviz as az
import pytensor

from datetime import datetime, timedelta
import os
import glob
import yaml

# Configs
#os.chdir("/Users/echhitjoshi/Library/Mobile Documents/com~apple~CloudDocs/Work/EonJive")
if os.uname().machine.lower() == "arm64":
    pytensor.config.cxx = '/usr/bin/clang++'

with open("config.yaml","r") as file:
    config = yaml.safe_load(file)

home_path = config['LOCAL_HOME_PATH']


def daywise_expected_total_sales_model(dat, date_col,target_col:str,sample:bool = True):
    """
    dat: data
    date_col: datetime column(should be datetime type for parsing)
    target_col: observed continuous sales column
    sample: True to sample posterior (Returns Model and Trace), False returns Model graph
    Bayesian Model to track expected sales given day of week
    Either samples or returns the model structure for inference
    """
    
    # Process data
    dat_model = dat[[date_col,target_col]].copy()
    dat_model[date_col] = pd.to_datetime(dat_model[date_col])
    dat_model['day_of_week'] = dat_model[date_col].dt.day_of_week
    dat_model['day_of_week_name'] = dat_model[date_col].dt.day_name()


    # Coordinate Map
    coords = {"day_of_week_name":dat_model[['day_of_week','day_of_week_name']].sort_values('day_of_week')['day_of_week_name'].unique()}

    
    # Model
    with pm.Model(coords = coords) as model:

        # model: 
        # sales ~ Normal(mu[day],sigma[day])
        # mu ~ Normal(20,100)
        # sigma ~ HalfNormal(20)

        # Define categorical indexes for day names
        day_idx = pm.Data("day_idx",dat_model['day_of_week'].values, dims = 'obs_id')

        # priors
        mu = pm.Normal("mu",mu = 50,sigma = 100,dims = 'day_of_week_name')
        sigma = pm.HalfNormal("sigma", sigma = 20, dims = 'day_of_week_name')
        
        #vectorize mu
        mu_day = mu[day_idx]
        sigma_day = sigma[day_idx]

        #likelihood
        obs = pm.Normal("obs", mu = mu_day,sigma = sigma_day,observed = dat_model[target_col].values, dims = 'obs_id')

        #sample
        if sample:
            trace = pm.sample(draws = 1000, tune = 300,chains = 4,return_inferencedata = True)
            az.to_netcdf(trace, home_path + f"/models/sales_model_trace_{datetime.now().strftime("%Y_%m_%d_%H_%M")}.nc")
            return model, trace, coords
            
        else:
            return model, coords




def plot_trace(trace):
    pm.plot_trace(trace,figsize = (15,8),legend = True)
    plt.show()


def load_latest_model(directory = home_path + '/models', pattern = '*'):
    files = glob.glob(os.path.join(directory,pattern))
    print("Reading from ",files)
    if not files:
        return None
    latest_file = max(files,key = os.path.getmtime)
    print('latest model is : ', latest_file)
    trace = az.from_netcdf(latest_file)
    return trace

def load_last_model(filepath = home_path + '/models/'):
    models = os.listdir(filepath)
    models.sort(reverse = True)
    trace = az.from_netcdf(filepath + models[0])
    return trace
    