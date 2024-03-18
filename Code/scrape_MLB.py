import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import os
import tqdm
import clean_MLB

BOXSCORE_PREFIX = 'https://www.baseball-reference.com/'
# Print the current working directory's parent directory
PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

# Set the data folder path (update the path as needed)
DATA_FOLDER = PATH + r'\Data'
OUTPUT_FOLDER = PATH + r'\Output'

# Function to make a request with a delay
def make_request(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print('Successfully Get the Connection')
            return response
        elif response.status_code == 429:
            # Respect the Retry-After header if available
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limit reached. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            return make_request(url)
        else:
            print("Failed to retrieve the page, status code:", response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def get_each_game(url):
    scorebox_url = []
    response = make_request(url)
    if response and response.status_code == 200:
        # Create a soup object from the HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        game_elements = soup.find_all('p', class_='game')
        for game in game_elements:
            # Find all <a> tags, assuming the second one is the team after '@'
            a_tags = game.find_all('a')
            if len(a_tags) > 1:
                # The team after '@' is in the second <a> tag
                team = a_tags[1].get_text().strip()

                if team in ['Chicago Cubs', 'Chicago White Sox']:

                    # The 'Boxscore' link is in the last <a> tag
                    boxscore_link = a_tags[-1]['href'] if a_tags[-1].get_text() == 'Boxscore' else None

                    # Save the extracted information
                    scorebox_url.append((team, boxscore_link))

    else:
        print("Failed to retrieve the page")

    df = pd.DataFrame(scorebox_url, columns=['team', 'boxscore_link'])
    df['boxscore_link'] = BOXSCORE_PREFIX + df['boxscore_link']

    return df


def get_scorebox(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # in the class of scorebox, find all the strong tags
        strong_tags = soup.find('div', class_='scorebox').find_all('strong')
        teama = strong_tags[0].text.strip()
        teamb = strong_tags[1].text.strip()

        date = soup.find("div", class_="scorebox_meta").find_all("div")[0].text.strip()
        start_time = soup.find("div", class_="scorebox_meta").find_all("div")[1].text.strip()
        attendance = soup.find("div", class_="scorebox_meta").find_all("div")[2].text.strip()
        venue = soup.find("div", class_="scorebox_meta").find_all("div")[3].text.strip()
        duration = soup.find("div", class_="scorebox_meta").find_all("div")[4].text.strip()

        return {
            "teama": teama,
            "teamb": teamb,
            "date": date,
            "start_time": start_time,
            "attendance": attendance,
            "venue": venue,
            "duration": duration
        }
    
    else:
        return None


def scrape_each_scorebox(url, year):
    # Create an empty list to store the extracted information

    TeamA = []
    TeamB = []
    Date = []
    Time = []
    Attendance = []
    Venue = []
    Duration = []

    # read the csv file
    df = get_each_game(url)
    print('Successfully get the game scorebox url')

    # get the scorebox for each url
    scorebox_url = df['boxscore_link'].tolist()



    for url in tqdm.tqdm(scorebox_url):
        scorebox = get_scorebox(url)

        if scorebox:
            TeamA.append(scorebox["teama"])
            TeamB.append(scorebox["teamb"])
            Date.append(scorebox["date"])
            Time.append(scorebox["start_time"])
            Attendance.append(scorebox["attendance"])
            Venue.append(scorebox["venue"])
            Duration.append(scorebox["duration"])

        # Sleep for 2 seconds to avoid being blocked
            time.sleep(2)
        else:
            print("Failed to retrieve the scorebox")
            time.sleep(2)
            continue

    data_frame = {
        "TeamA": TeamA,
        "TeamB": TeamB,
        "Date": Date,
        "Time": Time,
        "Attendance": Attendance,
        "Venue": Venue,
        "Duration": Duration
    }

    data_frame = pd.DataFrame(data_frame)

    data_frame['link'] = scorebox_url

    data_frame.to_csv(DATA_FOLDER + '\\Event\\Baseball_in_wrigley_field' f'\\{year}_scorebox.csv', index=False)

    ### The reason why I didn't use the clean_data function is because there are several error in the data 
    ### that need user manual fix. It will take you several minutes to fix the data.
    ### Ater you fix the data, you can run clean_MLB.py to clean the data

    return data_frame


if __name__ == '__main__':
    years = [2023, 2019, 2020, 2021, 2022]

    for year in years:
        url = f'https://www.baseball-reference.com/leagues/majors/{year}-schedule.shtml'
        print(f"Scraping {year}...")
        data = scrape_each_scorebox(url, year)
        print(f"Scraping {year} complete")
        time.sleep(10)  # Sleep to avoid being blocked
        break
