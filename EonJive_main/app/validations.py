from models import *
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, confusion_matrix, f1_score


def continuous_evaluations(actual,pred):
    """
    actual: true target
    pred: predicted target
    Check usual continuous target evaluations
    """
    print(f"R-squared(explained variance from the model compared against an average moded): {r2_score(actual,pred)}")
    if r2_score(actual,pred) < 0:
        print("Please check model fit")

    print(f"MAE(Average of absolute Residual): {mean_absolute_error(actual,pred)}")
    print(f"MSE(Average of Squared Residual): {mean_squared_error(actual,pred)}")
    print(f"RMSE(Root Average of Squared Residual): {np.sqrt(mean_squared_error(actual,pred))}")
