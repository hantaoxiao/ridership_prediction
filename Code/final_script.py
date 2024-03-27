"""
This script performs linear regression analysis on airport ridership data.
It includes data preprocessing, model training, model evaluation, and visualization of results.

Libraries used:
- pandas for data manipulation and analysis.
- numpy for mathematical operations.
- matplotlib for data visualization.
- sklearn for machine learning algorithms and evaluation metrics.
- statsmodels for statistical modeling.

Please update the DATA_FOLDER and OUTPUT_FOLDER paths as needed.

"""

# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler, PolynomialFeatures
import os
import json
import warnings
warnings.filterwarnings('ignore')

# Helper function
import pull_data

# Print the current working directory's parent directory
PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

# Set the data folder path (update the path as needed)
DATA_FOLDER = PATH + r'\Data'
OUTPUT_FOLDER = PATH + r'\Output'

def analysis(data, place, event_lst):


    #preprocess the dataset
    data['date'] = pd.to_datetime(data['date'])
    data['year'] = data['date'].dt.year
    data['month'] = data['date'].dt.month
    data['day_of_week'] = data['date'].dt.dayofweek  # Monday is 0 and Sunday is 6
    data['week'] = data['date'].apply(lambda x: x.isocalendar()[1])
    data['day_of_year'] = data['date'].dt.dayofyear
    data['p2_week'] = data['week'] ** 2 
    data['p2_temperature'] = data['temperature'] ** 2
    data = data.fillna(0)
    data = data.join(pd.get_dummies(data['day_of_week'], prefix='day_of_week', dtype=int))
    data.drop(columns=['day_of_week'], inplace=True)

    # Create interaction terms
    for i in range(7):
        data[f'day_of_week_{i}_week'] = data[f'day_of_week_{i}'] * data['week']

    # Convert categorical features to dummy variables
    categorical_features = ['month', 'week', 'p2_week']
    data = pd.get_dummies(data, columns=categorical_features, dtype=int)

    # Split the data into training and testing sets
    # Linear_train = data[data['year'] == 2023]
    # Linear_test = data[data['year'] == 2023]

    Linear_train = data.copy()
    Linear_test = data.copy()


    # Clean event effect
    for event in event_lst:
        Linear_test[event] = 0

    # Prepare features and target variable
    X_train = Linear_train.drop(['date', 'ridership', 'year'], axis=1)
    y_train = Linear_train['ridership']
    X_test = Linear_test.drop(['date', 'ridership', 'year'], axis=1)
    y_test = Linear_test['ridership']

    # Perform grid search to optimize model parameters
    param_grid = {'fit_intercept': [True, False]}
    grid_search = GridSearchCV(estimator=LinearRegression(), param_grid=param_grid, cv=5)
    grid_search.fit(X_train, y_train)

    # Predict using the optimized model
    y_pred = grid_search.predict(X_test)
    y_pred_event = grid_search.predict(X_train)


    # Display metrics
    print(f'Mean Squared Error: {mean_squared_error(y_test, y_pred)}')
    print(f'R-squared: {r2_score(y_test, y_pred)}')
    print(f'R-squared_event: {r2_score(y_test, y_pred_event)}')

    # save residuals
    plt.figure(figsize=(20, 6))
    plt.scatter(Linear_test['date'], y_test - y_pred_event, color='red')
    plt.axhline(y=0, color='black', linestyle='--')
    plt.xlabel('Date')
    plt.ylabel('Residuals')
    plt.title('Residuals for 2023')
    plt.savefig(OUTPUT_FOLDER + f'\img\{place}_residuals.png')

    # save actual vs. predicted ridership with event effect and without event effect
    plt.figure(figsize=(20, 6))
    plt.plot(Linear_test['date'], y_test, label='Actual')
    #plt.plot(Linear_test['date'], y_pred, label='Predicted', alpha=0.5, color='green')
    plt.plot(Linear_test['date'], y_pred_event, label='Predicted_event', alpha=0.5, color='red')
    plt.xlabel('Date')
    plt.ylabel('Ridership')
    plt.title(f'Ridership Regression for 2023 in {place} with and without event effect')
    plt.legend()
    plt.savefig(OUTPUT_FOLDER + f'\img\{place}_ridership.png')



    # Calculate coefficients
    coefficients = pd.DataFrame({'Feature': X_train.columns, 'Coefficient': grid_search.best_estimator_.coef_})

    #coefficients = coefficients.sort_values('Coefficient', ascending=False)
    

    # Add predicted values to the dataframe, right next to the actual values
    Linear_train['predicted_event'] = y_pred_event
    Linear_train['predicted'] = y_pred

    # Save the results to an Excel file
    with pd.ExcelWriter(OUTPUT_FOLDER + f'\excel\{place}_analysis_results.xlsx', engine='xlsxwriter') as writer:
        # Write the Linear_train dataframe to a sheet named 'Predictions'
        Linear_train.to_excel(writer, sheet_name='Predictions', index=False)

        # Write the coefficients dataframe to a sheet named 'Coefficients'
        coefficients.to_excel(writer, sheet_name='Coefficients', index=False)


def get_clean_data(raw_path, place_name):
    # Read the data
    raw_data = pd.read_csv(raw_path)
    temperature = pd.read_csv(DATA_FOLDER + '\\Clean\\' + 'temperature.csv')
    event_list = json.load(open(r'event_list.json', 'r'))
    event_data = pd.read_csv(DATA_FOLDER + r'\Event\event.csv')[event_list[place_name] + ['date']]
    #event_data = pd.read_csv(DATA_FOLDER + r'\Event\event.csv')[event_list['roosevelt'] + ['date']]

    # preporcess the temperature data
    temperature['DATE'] = pd.to_datetime(temperature['DATE'])
    temperature['temperature'] = (temperature['TMAX'] + temperature['TMIN']) / 2

    # preprocess the event data
    event_data['date'] = pd.to_datetime(event_data['date'])

    # Check data format
    standard_col = ['YEAR', 'MONTH', 'SERVICE_DATE', 'SORT_ALL', 'BRANCH', 'STATION', 'RIDES'] 
    assert all([col in raw_data.columns for col in standard_col]), 'Data format is not standard, please follow the SQL query'

    # clean raw_data
    raw_data.drop(columns=['YEAR', 'MONTH', 'SORT_ALL', 'BRANCH', 'STATION'], inplace=True)
    raw_data.rename(columns={'SERVICE_DATE': 'date', 'RIDES': 'ridership'}, inplace=True)
    raw_data['date'] = pd.to_datetime(raw_data['date'])

    # group by date
    raw_data = raw_data.groupby('date').sum().reset_index()

    # merge the temperature data
    clean_data = raw_data.merge(temperature[['DATE', 'temperature', 'WT01', 'WT02', \
                                            'WT03', 'WT04', 'WT05', 'WT06', 'WT08', 'WT09', 'WT10']], \
                                left_on='date', right_on='DATE', how='left').drop(columns='DATE').fillna(0)
    
    # merge the event data
    clean_data = clean_data.merge(event_data, on='date', how='left').fillna(0)

    return clean_data





if __name__ == '__main__':
    # run the pull_data script
    pull_data.main()
    
    # Read the data
    event_list = json.load(open(r'event_list.json', 'r'))
    file_list = os.listdir(DATA_FOLDER + '\\' + 'Raw')

    for file in file_list:
        if file.endswith('.csv'):
            data_path = DATA_FOLDER + '\\' + 'Raw\\' + file
            place = file.split('.csv')[0]
            data = get_clean_data(data_path, place)
            data.to_csv(DATA_FOLDER + '\\' + 'Clean\\' + f'{place}.csv', index=False)


            print(f'Working on {place}')
            event_lst = event_list[place]
            analysis(data, place, event_lst)
            print(f'{place} is done')
