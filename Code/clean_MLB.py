import pandas as pd
import re
import os

PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

# Set the data folder path (update the path as needed)
DATA_FOLDER = PATH + r'\Data'
OUTPUT_FOLDER = PATH + r'\Output'

def clean_data(data):
    # Convert date format
    try:
        data['Date'] = pd.to_datetime(data['Date'], format='%A, %B %d, %Y')
    except:
        pass

    try:
        data['Date'] = pd.to_datetime(data['Date'])
    except:
        pass

    # Convert time format
    def get_start_time(row):
        time = re.search(r'\d+:\d+', row['Time'])
        if pd.isnull(time):
            return None
        pm = re.search(r'p.m.', row['Time'])
        if pm:
            hour = int(time.group(0).split(':')[0]) + 12
            if hour == 24:
                hour = 12
            return str(hour) + ':' + time.group(0).split(':')[1]
        return time.group(0)

    data['Time'] = data.apply(get_start_time, axis=1)

    # Convert attendance format
    def get_attendance(row):
        if pd.isnull(row['Attendance']):
            return None
        attendance = re.search(r'Attendance: (\d+,\d+)', row['Attendance'])
        if attendance:
            return int(attendance.group(1).replace(',', ''))
        return None

    data['Attendance'] = data.apply(get_attendance, axis=1)

    # Convert venue format
    def get_venue(row):
        if pd.isnull(row['Venue']):
            return None
        venue = re.search(r'Venue: (.+)', row['Venue'])
        if venue:
            return venue.group(1)
        return None

    data['Venue'] = data.apply(get_venue, axis=1)

    def get_duration(row):
        if pd.isnull(row['Duration']):
            return None
        duration = re.search(r'Game Duration: (\d+:\d+)', row['Duration'])
        if duration:
            return duration.group(1)
        return None
    
    data['Duration'] = data.apply(get_duration, axis=1)


    # Create interaction terms
    for i in range(7):
        data[f'day_of_week_{i}_day_night'] = data[f'day_of_week_{i}'] * data['day_night']


    return data


def main():
    # Get all the files in the folder
    file_path = DATA_FOLDER + '\\Event\\Baseball_in_wrigley_field\\' + '2023_scorebox.csv'

    data = pd.read_csv(file_path)
    data = clean_data(data)

    data['Date'] = pd.to_datetime(data['Date'])

    data['day_of_week'] = data['Date'].dt.dayofweek  # Monday is 0 and Sunday is 6

    # make day_of_week 0 to 3 as Weekday(nofriday) and 4 Friday, 5 Saturday, 6 Sunday
    data['day_of_week'] = data['day_of_week'].apply(lambda x: 'Weekday(nofriday)' if x < 4 else x)
    data['day_of_week'] = data['day_of_week'].apply(lambda x: 'Friday' if x == 4 else x)
    data['day_of_week'] = data['day_of_week'].apply(lambda x: 'Saturday' if x == 5 else x)
    data['day_of_week'] = data['day_of_week'].apply(lambda x: 'Sunday' if x == 6 else x)

    data['day_night'] = data['Time'].apply(lambda x: 0 if x.split(':')[0] < '17' else 1) # 0 for day and 1 for night

    # except weekday(nofriday), make all other day and night as 0
    data.loc[data['day_of_week'] != 'Weekday(nofriday)', 'day_night'] = 0

    # create column weekday(nofriday) day and night, Friday, Saturday, Sunday 
    data = data.join(pd.get_dummies(data['day_of_week'], prefix=None, dtype=int))
    data.drop(columns=['day_of_week'], inplace=True)

    # Create interaction terms
    data['sport_game_attendence_day_weekday(nofri)'] = 0
    data['sport_game_attendence_night_weekday(nofri)'] = 0

    data.loc[(data['Weekday(nofriday)'] == 1) & (data['day_night'] == 0), 'sport_game_attendence_day_weekday(nofri)'] = 1
    data.loc[(data['Weekday(nofriday)'] == 1) & (data['day_night'] == 1), 'sport_game_attendence_night_weekday(nofri)'] = 1

    # let column Friday, Saturday, Sunday, sport_game_attendence_day_weekday(nofri), sport_game_attendence_night_weekday(nofri) multiply with Attendance
    data['sport_game_attendence_fri'] = data['Friday'] * data['Attendance']
    data['sport_game_attendence_sat'] = data['Saturday'] * data['Attendance']
    data['sport_game_attendence_sun'] = data['Sunday'] * data['Attendance']
    data['sport_game_attendence_day_weekday(nofri)'] = data['sport_game_attendence_day_weekday(nofri)'] * data['Attendance']
    data['sport_game_attendence_night_weekday(nofri)'] = data['sport_game_attendence_night_weekday(nofri)'] * data['Attendance']

    # only keep record in wrigley field
    data = data[data['Venue'] == 'Wrigley Field']

    # keep only the columns that are needed
    data = data[['Date', 'sport_game_attendence_fri', 'sport_game_attendence_sat', 'sport_game_attendence_sun', 'sport_game_attendence_day_weekday(nofri)', 'sport_game_attendence_night_weekday(nofri)']]

    data.rename(columns={'Date': 'date'}, inplace=True)

    data.to_csv(DATA_FOLDER + '\\Event\\Baseball_in_wrigley_field\\' + 'addison.csv', index=False)

    return data