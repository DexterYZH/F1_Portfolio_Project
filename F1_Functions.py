import pandas as pd
import numpy as np
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
import sys
from IPython.display import HTML, display
import matplotlib.image as mpimg
import matplotlib.colors as mcolors
import inspect
import webbrowser
from datetime import datetime
import platform
import colorsys
from PIL import Image, ImageDraw, ImageFont
import getpass



curr_os = platform.system()

if curr_os == "Windows":
    os_path = "C:/Users/User/PycharmProjects/F1 Python/"

elif curr_os == "Darwin":
    os_path = "/Users/dexteryippro/Documents/F1 Python/"


# --------------------------------------------------------------------------------------------------
def get_valid_laps(df):
    valid_laps = df.loc[df['lapNum'] != -1, 'lapNum'].unique()  # Step 1: Get unique lapNums that are not -1

    valid_laps = [lap for lap in valid_laps if not (df.loc[df['lapNum'] == lap, 'lap_number'] == -1).any()]
    return valid_laps
    
#----------------------------------------------------------------------------------------------------------------------------------------------------------
# Function gameMode
# returns: game_mode type; e.g. "career"/"braking point" 
def get_game_mode(df_file):
    game_mode_val = df_file[df_file["gameMode"] != -1]["gameMode"].unique()[0]

    if game_mode_val == 4:  # F1 World
        game_mode = "f1 world"

    elif game_mode_val == 5:
        game_mode = "time trial"

    elif game_mode_val == 17:
        game_mode = "braking point"

    elif game_mode_val == 21:
        game_mode = "career"

    else:
        game_mode = "unknown gameMode"

    return game_mode
#----------------------------------------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------------------------------------
# Function Session Race Details
# returns:
def get_session_race_details(df_file, session_track, session_track_length, session_laps, session_sessionLength_val,
                             session_type):
    svr_session_distance = session_laps * session_track_length

    # Default Session Fixed laps for "Quickfire" and "Very Short"
    session_length_fixed_laps = 0

    if session_sessionLength_val == 2:
        svr_session_length_title = "Quickfire"
        session_length_fixed_laps = 3
        svr_session_perc = 0

    elif session_sessionLength_val == 3:
        svr_session_length_title = "Very Short"
        session_length_fixed_laps = 5
        svr_session_perc = 0

    elif session_sessionLength_val == 4:
        svr_session_length_title = "Short"
        svr_session_perc = 25 / 100

    elif session_sessionLength_val == 5:
        svr_session_length_title = "Medium"
        svr_session_perc = 35 / 100

    elif session_sessionLength_val == 6:
        svr_session_length_title = "Long"
        svr_session_perc = 50 / 100

    elif session_sessionLength_val == 7:
        svr_session_length_title = "Full"
        svr_session_perc = 100 / 100

    else:
        print("\nError somewhere")

    # Distance covered during session
    if session_track == "monaco":  # Special Case
        full_race_target_distance = 260 * 1000  # Only monaco Full Race Distance = 260km

    elif session_track == "spa":  # Special Case
        full_sprint_target_distance = 77.044 * 1000  # Only Belgium Full Sprint Distance = 77.044 km

    else:  # Normal Circumstance
        full_race_target_distance = 305 * 1000  # Full Race Distance usually = 305km
        full_sprint_target_distance = 100 * 1000  # Full Sprint Distance usually = 100km

    if session_length_fixed_laps == 0:

        if session_laps % 2 == 0:  # Even Number
            full_session_laps = int(session_laps / svr_session_perc)

        elif session_laps % 2 == 1:  # Odd Number
            full_session_laps = int((session_laps / svr_session_perc) + 1)  # Return full_session_laps

        full_session_distance = int(full_session_laps * session_track_length)

        # Type: Race
        if full_session_distance >= full_race_target_distance:
            session_type = "race"  # Return session_type
            session_target_distance = full_race_target_distance  # Return session_target_distance
            # Redefine the full_session_laps and full_session_distance
            full_session_laps = int(math.ceil(full_race_target_distance / session_track_length))
            full_session_distance = full_session_laps * session_track_length  # Return full_session_distance

        # Type: Sprint
        elif (full_session_distance >= full_sprint_target_distance) & (
                full_session_distance < full_race_target_distance):
            session_type = "sprint"
            session_target_distance = full_sprint_target_distance

        else:
            # check for aborted session telltale signs
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            session_end_lap = session_laps.max()
            session_end_binIndex = session_end_lap['binIndex'].max()
            if (session_end_lap == df_file["lapNum"].unique().max()) & (session_end_binIndex > 1):
                session_type = "aborted"
                session_target_distance = full_race_target_distance

            # Redefine the full_session_laps and full_session_distance
            full_session_laps = int(math.ceil(full_race_target_distance / session_track_length))
            full_session_distance = full_session_laps * session_track_length  # Return full_session_distance

    # For "Quickfire" and "Very Short"
    elif (session_length_fixed_laps == 3) | (session_length_fixed_laps == 5):
        session_type = "race"

        full_session_laps = int(math.ceil(full_race_target_distance / session_track_length))
        full_session_distance = full_session_laps * session_track_length
        session_target_distance = full_race_target_distance

    else:  # Error exit clause
        session_type = "definition error"
        full_session_laps = -1
        full_session_distance = -1
        session_target_distance = -1

    # print(f"Session Game Mode : {session_gameMode.title()}\n")

    return (session_type, svr_session_perc, svr_session_distance,
            full_session_laps, session_target_distance, svr_session_length_title, full_session_distance
            )
#----------------------------------------------------------------------------------------------------------------------------------------------------------

# Function: SRT Lib from google sheet
# returns: f1_23_srt_lib
#----------------------------------------------------------------------------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------------------------------------------------------------------------
# Function: get sector distances
# returns: sec_1_distance, sec_2_distance, sec_3_distance
def get_session_sector_distance(f1_23_srt_lib, session_track):
    matched_track = f1_23_srt_lib.loc[
        f1_23_srt_lib['F1 23 Track'] == session_track.title(),
        [
            'Sector 1 (End) (m)', 'Sector 2 (End) (m)', 'Sector 3 (End) (m)',
        ]
    ].values

    if matched_track.size > 0:
        sec_1_distance = matched_track[0][0]
        sec_2_distance = matched_track[0][1]
        sec_3_distance = matched_track[0][2]

        return (
            sec_1_distance, sec_2_distance, sec_3_distance
        )

    else:
        print("No matching track found.")
#----------------------------------------------------------------------------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------------------------------------------------------------------------
# Function: Session Tyres for mapping
# returns: weekend_tyres; tyre value types for tyre set mapping
def get_weekend_tyres(f1_23_srt_lib, session_tyre_set):
    weekend_tyres = pd.concat([
        f1_23_srt_lib.loc[
        f1_23_srt_lib['Tyre Set Group'] == session_tyre_set,
        'Compound': 'Tyre Set Group'
        ],
        f1_23_srt_lib.loc[9:10, "Compound": "Tyre Set Group"].fillna(
            {
                "Compound": "-",
                "Tyre Set Group": session_tyre_set
            }
        )
    ], ignore_index=True)

    weekend_tyres['Tyre Value'] = weekend_tyres['Tyre Value'].astype(int)
    weekend_tyres.reset_index(drop=True, inplace=True)

    if not weekend_tyres.empty:
        return weekend_tyres

    else:
        print("No matching tyres found.")
#----------------------------------------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------------------------------------
# LOOKUP Session Titles
# returns: 
def get_session_lib_titles(f1_23_srt_lib, session_track):
    matched_track = f1_23_srt_lib.loc[
        f1_23_srt_lib['F1 23 Track'] == session_track.title(),
        [
            'Grand Prix', 'Track Name', 'Track Type', 'Country', 'City', 'Direction', 'Tyre Set',
            '2023 Round', 'Grand Prix Title', 'No.of Turns', 'DRS Zones'
        ]
    ].values

    # Extract Number of rounds from google sheets
    total_calendar_round = f1_23_srt_lib["2023 Round"].dropna().nunique()

    if matched_track.size > 0:
        session_grand_prix = matched_track[0][0]
        session_track_name = matched_track[0][1]
        session_track_type = matched_track[0][2]
        session_country = matched_track[0][3]
        session_city = matched_track[0][4]
        session_direction = matched_track[0][5]
        session_tyre_set = matched_track[0][6]
        session_calendar_round = int(matched_track[0][7])
        session_grand_prix_title = matched_track[0][8]
        session_total_turns = int(matched_track[0][9])
        session_drs_zones = matched_track[0][10]

        weekend_tyres = get_weekend_tyres(f1_23_srt_lib, session_tyre_set)
        return (
            session_grand_prix, session_track_name, session_track_type,
            session_country, session_city, session_direction, session_tyre_set,
            session_calendar_round, session_grand_prix_title, session_total_turns,
            total_calendar_round, weekend_tyres, session_drs_zones
        )

    else:
        print("No matching track found.")
# get_session_lib_titles -----END-----

# LOOKUP Session Weather Description
# --------------------------------------------------------------------------------------------------
def get_session_lib_weather(f1_23_srt_lib, session_weather_val_start):
    param_to_return_weather = ['Weather Description']

    # Assuming that 'session_track' and 'f1_23_srt_lib' are defined earlier in the code
    matched_weather = f1_23_srt_lib.loc[
        f1_23_srt_lib['Weather Val'] == session_weather_val_start,
        param_to_return_weather
    ].values

    session_weather_descrip_start = {}  # Create an empty dictionary to store the session parameters

    if matched_weather.size > 0:
        session_weather_descrip_start = matched_weather[0][0]
        return session_weather_descrip_start

    else:
        print("No matching weather found.")
# get_session_lib_weather -----END-----

# --------------------------------------------------------------------------------------------------

# HTML Main Title
# --------------------------------------------------------------------------------------------------
def display_main_title_html(dash_type, df_working_file):
    # Get race details
    # Maybe unpack from a separate function that only stores title?

    (
        session_grand_prix, session_game_mode, session_team, session_track,
        svr_session_length_title, session_type, session_calendar_round, total_calendar_round
    ) = variables_main_title(df_working_file)

    # Create Dataframe Title with variables
    main_title_html = f"""
    <div style="background-color:#1e1e1e; color:#f3f3f3; padding:20px, border-radius:8px;">
        <div style="text-align:center; font-weight:bold; text-transform:uppercase; line-height: 1.75; font-size:37px;">
            F1®23 &ensp; {session_grand_prix}
        </div>
        <div style="text-align:center; font-weight:bold; text-transform:uppercase; line-height: 1.75; font-size:30px;">
            {session_game_mode}  |  {session_team} 
        </div>
        <div style="text-align:center; font-weight:bold; text-transform:uppercase; line-height: 1.75; font-size:28px;">
            {session_track} | {svr_session_length_title}   {session_type} | Round {session_calendar_round:02d}/{total_calendar_round}
        </div>
        <br>
        <div style ="text-align:center; font-weight:bold; text-transform:uppercase; line-height: 1; font-size:22px;">
            {dash_type} Dashboard
        </div>
        <br>
    </div>
    """
    return main_title_html

#----------------------------------------------------------------
def create_html_styled_image_1(user_text, user_font_size):
   
    width=110
    height=62

    bg_color="#1a1a1a"

    # Create image
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Load fonts (requires valid .ttf font files)
    try:
        font_1 = ImageFont.truetype(r"D:\Fonts\F1 Font Files (with important Message)\Formula1-Bold.otf", user_font_size)  # First font
        #font_1 = ImageFont.truetype(r"D:\Fonts\F1 Font Files (with important Message)\Formula1-Regular.otf", 14)  # First font
        
    except IOError:
        font_1 = ImageFont.load_default()
        
    # Define texts and styles
    user_text_color = "#F2F2F2"
    
    # Get text sizes
    user_text_size = draw.textbbox((0, 0), user_text, font=font_1)
    user_text_width = user_text_size[2] - user_text_size[0]

    # Calculate positions
    user_text_x = (width - user_text_width) // 2
    user_text_y = height // 2.5
    
    # Draw texts
    draw.text((user_text_x, user_text_y), user_text, font=font_1, fill=user_text_color)
    
    return image
#

def create_html_styled_image_3(user_text, width=110, height=62):
    bg_color = "#1a1a1a"

    # Create image
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # Load font and dynamically adjust size
    font_path = r"D:\Fonts\F1 Font Files (with important Message)\Formula1-Bold.otf"

    max_font_size = height  # Start with the max possible font size
    font_size = max_font_size

    while font_size > 5:  # Prevent the font from being too small
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()
        
        # Measure text size
        text_width, text_height = draw.textbbox((0, 0), user_text, font=font)[2:]

        # Check if text fits within width
        if text_width <= width * 0.9:  # Leave some padding
            break
        
        # Reduce font size and try again
        font_size -= 1  

    # Define text color
    user_text_color = "#F2F2F2"

    # Calculate positions (center alignment)
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2

    # Draw text
    draw.text((text_x, text_y), user_text, font=font, fill=user_text_color)

    return image


# ---------------------------------------------------------------
def create_html_styled_image_2(text_1, text_2):
   
    width=1920
    height=1080

    bg_color="#1a1a1a"

    # Create image
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Load fonts (requires valid .ttf font files)
    try:
        font_1 = ImageFont.truetype(r"D:\Fonts\F1 Font Files (with important Message)\Formula1-Bold.otf", 200)  # First font
        font_2 = ImageFont.truetype(r"D:\Fonts\F1 Font Files (with important Message)\Formula1-Bold.otf", 150)  # Second font
    except IOError:
        font_1 = ImageFont.load_default()
        font_2 = ImageFont.load_default()
    
    # Define texts and styles
    text_1_color = "#F2F2F2"
    text_2_color = "#F2F2F2"
    
    # Get text sizes
    text_1_size = draw.textbbox((0, 0), text_1, font=font_1)
    text_2_size = draw.textbbox((0, 0), text_2, font=font_2)
    text_1_width = text_1_size[2] - text_1_size[0]
    text_2_width = text_2_size[2] - text_2_size[0]
    
    # Calculate positions
    text_1_x = (width - text_1_width) // 2
    text_1_y = height // 3
    text_2_x = (width - text_2_width) // 2
    text_2_y = 2 * height // 3
    
    # Draw texts
    draw.text((text_1_x, text_1_y), text_1, font=font_1, fill=text_1_color)
    draw.text((text_2_x, text_2_y), text_2, font=font_2, fill=text_2_color)
    
    return image
# ---------------------------------------------------------------

def resize_image(input_image, width, height):
    """
    Resizes an image to the specified size and returns it.
    
    :param input_image: PIL Image object or path to the input image
    :param size: Tuple containing the new width and height
    :return: Resized Image object
    """
    size = (width, height)
    if isinstance(input_image, str):  # If input is a file path, open it
        with Image.open(input_image) as img:
            img_resized = img.resize(size, Image.LANCZOS)
    else:  # If input is already an Image object
        img_resized = input_image.resize(size, Image.LANCZOS)

    return img_resized



# ---------------------------------------------------------------
# Retrieve Race Lap Data
# ---------------------------------------------------------------
def get_race_lap_data(df_file, lap):
    # Filter the data for the current lap
    # if lap not in

    race_lap_data = df_file[(df_file['lapNum'] == lap) & (df_file['lapFlag'] == 0)].copy()

    # Finding Index of first and last row of each Lap
    race_lap_index_start = (race_lap_data["binIndex"] == race_lap_data["binIndex"].min())
    race_lap_index_end = (race_lap_data["binIndex"] == race_lap_data["binIndex"].max())

    # Debugging Errors
    race_lap_index_one_third = (race_lap_data["binIndex"] == int(race_lap_data["binIndex"].max() / 3))

    # Finding First and Last row of each Lap by assigning index
    race_start_lap = race_lap_data[race_lap_index_start].iloc[0]
    race_end_lap = race_lap_data[race_lap_index_end].iloc[0]
    race_one_third_lap = race_lap_data[race_lap_index_one_third].iloc[0]

    return race_lap_data, race_start_lap, race_end_lap, race_one_third_lap
# get_race_lap_data() ----------ENDS----------

# Calculate Sector Times
def calculate_sector_times(f1_23_srt_lib, session_track, lap_data):
    # Unpack the sector distances from sector_distances()
    sec_1_distance, sec_2_distance, sec_3_distance, = get_session_sector_distance(f1_23_srt_lib, session_track)

    sec_1_closest_index = (lap_data["lap_distance"] - sec_1_distance).abs().idxmin()
    sec_1_time = round(lap_data.loc[sec_1_closest_index, "lap_time"], 3)

    sec_2_closest_index = (lap_data["lap_distance"] - sec_2_distance).abs().idxmin()
    sec_2_time = round((lap_data.loc[sec_2_closest_index, "lap_time"] - sec_1_time), 3)

    sec_3_closest_index = (lap_data["lap_distance"] - sec_3_distance).abs().idxmin()
    sec_3_time = round((lap_data.loc[sec_3_closest_index, "lap_time"] - (sec_1_time + sec_2_time)), 3)

    sec_1_time = format_val(sec_1_time, '.3f')
    sec_2_time = format_val(sec_2_time, '.3f')
    sec_3_time = format_val(sec_3_time, '.3f')

    return sec_1_time, sec_2_time, sec_3_time


def fetch_google_sheet_data(sheet_name):   
    workbook_url = "https://docs.google.com/spreadsheets/d/1ErqGHw_n06l7J_7NrSh9kR4TIUxbOPj2WwRiqH8ZdvI/edit?pli=1"
    try:
        # Extract the spreadsheet ID
        spreadsheet_id = workbook_url.split("/d/")[1].split("/")[0]
        # Construct the export URL
        csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name.replace(' ', '%20')}"
        # Fetch the data
        data = pd.read_csv(csv_url)
    except Exception as e:
        raise ValueError(f"Failed to fetch data for sheet '{sheet_name}': {e}")
    return data



def format_val(value, form):
    if value > 0:
        val = format(value, form)
    else:
        val = "-"

    return val

def get_pit_status(race_lap_data):
    if (race_lap_data['pit_status'] == 1).any():
        pit_status = "pit"
    else:
        pit_status = "-"
    return (pit_status.upper())



def get_pit_status_in_out(race_end_lap, race_start_lap):
    if race_end_lap['pit_status'] >= 1:
        pit_status = "In-lap"
    elif race_start_lap['pit_status'] >= 1:
        pit_status = "Out-lap"
    else:
        pit_status = "-"
    return pit_status

def get_pit_var_range(race_lap_data, col):
    #Get range of when car is in pits
    pit_var_range = race_lap_data.loc[(race_lap_data['pit_status'] == 1 ) & (race_lap_data[col] > 0 )]
    return pit_var_range

def get_pit_2vars_time(race_lap_data, col): #col = "pitLaneTime"
    pit_var_range = get_pit_var_range(race_lap_data, col)

    if len(pit_var_range) >= 2:
        # If the pit range is big, find last two index rows
        pit_var_time_1 = pit_var_range[col].iloc[-1]
        pit_var_time_2 = pit_var_range[col].iloc[-2]
    elif len(pit_var_range) == 1:
        # If the pit range only contains 1 row value;
        pit_var_time_1 = pit_var_range[col].iloc[-1]
        pit_var_time_2 = "-"  #
    else:
        # No rows; return default values
        pit_var_time_1 = "-"  #
        pit_var_time_2 = "-"  #

    return pit_var_time_1, pit_var_time_2

def get_pit_var_time(race_lap_data, col): #col = "pitLaneTime"
    # Retrieve pit variable times
    pit_var_time_1, pit_var_time_2 = get_pit_2vars_time(race_lap_data, col) #col = "pitLaneTime"
    pit_lap_time_1, pit_lap_time_2 = get_pit_2vars_time(race_lap_data, "lap_time") #col = "lap_time"
    # Check for None and handle them appropriately
    if pit_var_time_1 != "-" and pit_var_time_2 != "-":
        if pit_var_time_1 > pit_var_time_2:
            pit_var_time = pit_var_time_1
        else:
            pit_var_time = (pit_lap_time_1 - pit_lap_time_2) + pit_var_time_2
    else:
        # Handle cases where one or both times are None
        pit_var_time = "-"  # Or choose a suitable default value like 0 or "-"

    # If pit_var_time is not None, round it; otherwise, return it as is
    if pit_var_time != "-":
        pit_var_time = round(pit_var_time, 3)

    return pit_var_time

def get_most_recurring_value(race_lap_data, var):
    # Get the filtered range
    pit_var_range = get_pit_var_range(race_lap_data, var)

    # Ensure the column contains data
    if not pit_var_range[var].empty:
        # Calculate the mode and check for results
        mode_values = pit_var_range[var].mode()
        if not mode_values.empty:
            pit_recurr_val = round(mode_values[0], 3)  # Get the most recurring value
            return pit_recurr_val

    # Fallback if no recurring value is found
    return "-"

# ----------------------PARENT pit details START----------------------
def get_pit_details(race_lap_data, race_end_lap, race_start_lap):
    pit_status = get_pit_status(race_lap_data)

    pit_stop_time = get_most_recurring_value(race_lap_data, 'pitStopTime')

    pit_lane_time = get_pit_var_time(race_lap_data, 'pitLaneTime')

    return pit_status, pit_stop_time, pit_lane_time
# ----------------------PARENT pit details START----------------------

# Function to format time values to MM:SS.SSS
def lap_time_format(time):
    if isinstance(time, (int, float)) and time > 0:  # Check if the value is numeric and positive
        time_min = int(time // 60)
        time_sec = int(time) % 60
        time_sss = int((time - int(time)) * 1000)
        return f"{time_min:02d}:{time_sec:02d}.{time_sss:03d}"
    else:
        return "-"  # Return "RF" for invalid or non-numeric times



# Function to highlight the minimum value in the column (adapted for simple numeric values, excluding values <= 10)
def html_highlight_fastest_time(df, column):
    from bs4 import BeautifulSoup

    # Helper to strip existing HTML tags
    def strip_html_tags(value):
        if isinstance(value, str):
            return BeautifulSoup(value, 'html.parser').get_text()
        return value

    # Preprocess the column to handle various issues
    df[column] = df[column].apply(lambda x: str(x).strip() if isinstance(x, str) else x)  # Remove extra spaces
    df[column] = df[column].replace("", float("inf"))  # Replace empty strings with infinity
    df[column] = df[column].fillna(float("inf"))  # Replace nulls with infinity

    # Strip any existing HTML tags in the column
    df[f"{column}_stripped"] = df[column].apply(strip_html_tags)

    # Convert stripped value to numeric for comparison
    df['numeric_time'] = df[f"{column}_stripped"].apply(lambda x: convert_to_seconds(x))

    # Find the minimum numeric value that is greater than 10 and not infinity
    min_time = df[(df['numeric_time'] != float('inf')) & (df['numeric_time'] > 10)]['numeric_time'].min()

    # Highlight the cell with the minimum value in the original column
    df[column] = df.apply(
        lambda row: f"<span style='color:#a57dff; font-weight:600;'>{row[f'{column}_stripped']}</span>"
        if row['numeric_time'] == min_time else row[column],
        axis=1
    )

    # Drop the temporary numeric_time and stripped column
    df.drop(columns=['numeric_time', f"{column}_stripped"], inplace=True)

    return df

# HTML 1 - Child
# Helper function to convert formatted time to numeric value (adapted for straightforward numbers)
def convert_to_seconds(value):
    if value == "RF" or value == float("inf"):
        return float('inf')  # Use infinity for invalid data
    try:
        # Direct conversion for numeric values
        return float(value)
    except (ValueError, AttributeError):
        return float('inf')  # Return infinity for invalid data


def html_cards_status(df, html_card, replace_value, exclude_columns=None):
    
    """
    HTML 2 - Replace SC or RF laps with cards
    """
    # Ensure 'exclude_columns' is a list
    exclude_columns = exclude_columns or []

    # Determine the columns to span (from 'Time(s)' to the last column, excluding 'Lap' and others)
    span_columns = [col for col in df.columns if col not in exclude_columns and col != "Lap"]

    for index, row in df.iterrows():
        # Check if all span columns contain the replace_value
        if all(row[col] == replace_value for col in span_columns):
            # Replace the entire row's span columns with a single HTML card
            for col in span_columns:
                df.at[index, col] = ""  # Clear existing content
            df.at[index, span_columns[0]] = (
                f"<td colspan='{len(span_columns)}' style='text-align: center;'>{html_card}</td>"
            )

    return df

def html_highlight_pit_lap_times(df, column, col_colour):
#---------------------------------------------
# HTML 3 - Convert ss.sss to mm:ss.sss
#---------------------------------------------
    # Apply conditional formatting for 'In-lap' and 'Out-lap'
    df[col_colour] = df.apply(
        lambda row: (
            f"<span style='color:#CC5500; font-weight:600;'>{row[col_colour]}</span>"
            if row[column] == "In-lap" else
            f"<span style='color:#189b6c; font-weight:600;'>{row[col_colour]}</span>"
            if row[column] == "Out-lap" else row[col_colour]
        ),
        axis=1
    )
    return df

#Pit Functions*
#Bring to top When done

#---------------------------------------------
# HTML 4 - Colour tyres for Aesthetics
#---------------------------------------------
def html_highlight_tyres(df, col_colour):
    # Define tyre types and their colors
    tyre_colors = {
        "H": "#f4f4f4",  # Hard
        "M": "#fbcc1c",  # Medium
        "S": "#f12f32",  # Soft
        "I": "#128330",  # Intermediate
        "W": "#1f6da1"   # Wet
    }

    # Apply conditional formatting
    df[col_colour] = df.apply(
        lambda row: (
            f"<div style='position: relative; width: 30px; height: 30px; display: inline-flex; justify-content: center; align-items: center; background-color: #000000; border-radius: 50%;'>"
            f"<div style='position: absolute; width: 90%; height: 90%; background-color: {tyre_colors.get(row[col_colour], '#000000')}; border-radius: 50%; z-index: 1;'></div>"
            f"<div style='position: absolute; width: 70%; height: 70%; background-color: #000000; border-radius: 50%; z-index: 2;'></div>"
            # Rotating the black line by 45 degrees as an example
            f"<div style='position: absolute; width: 10%; height: 100%; background-color: #000000; left: 50%; transform: translateX(-50%) rotate(5deg); z-index: 3;'></div>"
            f"<div style='position: absolute; width: 10%; height: 100%; background-color: #000000; left: 50%; transform: translateX(-50%) rotate(-5deg); z-index: 3;'></div>"
            f"<div style='position: absolute; width: 100%; height: 100%; font-family: monospace; display: flex; justify-content: center; align-items: center; color: #ffffff; font-weight: 700; font-size: 18px;z-index: 4;'>{row[col_colour]}</div>"
            f"</div>"
        ) if row[col_colour] in tyre_colors else row[col_colour],
        axis=1
    )
    return df

#HTML 5 -
#--------------------------
def html_colour_status(df, col_colour):
    # Apply conditional formatting for different tyre types
    df[col_colour] = df.apply(
        lambda row: (
            f"<div style='color:#ffFfff; font-family:Digital-7 ;font-weight:600; background-color: #e10101; width: 30px; height: 30px; display: inline-flex; justify-content: center; align-items: center;;'>{row[col_colour]}</div>"
            #-----Red Flag-----
            if row[col_colour] == "RF" else
            #-------Safety Car-------
            f"<div style='position: relative; width: 30px; height: 30px; display: inline-flex; justify-content: center; align-items: center; background-color: #000000; border-radius: 0%;z-index: 1;'>"
            f"<div style='position: absolute; width: 90%; height: 90%; display: inline-flex; justify-content: center; align-items: center; background-color: #f3df09; border-radius: 0%;z-index: 2;'></div>"
            f"<div style='position: absolute; width: 75%; height: 70%; display: inline-flex; justify-content: center; align-items: center; background-color: #000000; border-radius: 20%;z-index: 3;'></div>"                        
            f"<div style='color:#fffcf2; font-family:monospace ;font-weight:800; font-size: 16px; display: inline-flex; justify-content: center; align-items: center; transform: scale(1.0, 1.0); z-index: 4;'>{row[col_colour]}</div>"
            f"</div>"
            if row[col_colour] == "SC" else
            #-------Virtual Safety Car-------
            f"<div style='position: relative; width: 30px; height: 30px; display: inline-flex; justify-content: center; align-items: center; background-color: #000000; border-radius: 0%;z-index: 1;'>"
            f"<div style='position: absolute; width: 90%; height: 90%; display: inline-flex; justify-content: center; align-items: center; background-color: #f8a608; border-radius: 0%;z-index: 2;'></div>"
            f"<div style='position: absolute; width: 75%; height: 75%; display: inline-flex; justify-content: center; align-items: center; background-color: #000000; border-radius: 25%;z-index: 3;'></div>"                        
            f"<div style='color:#fffcf2; font-family:monospace ;font-weight:800; font-size: 16px; display: inline-flex; justify-content: center; align-items: center; transform: scale(0.75, 1.0); z-index: 4;'>{row[col_colour]}</div>"
            f"</div>"
            if row[col_colour] == "VSC" else row[col_colour]
        ),
        axis=1
    )
    return df

#HTML 6
def html_colour_position_change(df, column):
    # Check if the column is already formatted with HTML and return if so
    if df[column].apply(lambda x: isinstance(x, str) and x.startswith("<span")).all():
        return df

    # Convert the column to numeric, coercing errors to NaN and filling NaNs with 0
    df[column] = pd.to_numeric(df[column], errors='coerce').fillna(0)

    # Apply a function to format position change only to numeric values
    df[column] = df[column].apply(
        lambda x: f"<span style='color: #31ba3a;'>▲</span> {int(x)}" if x > 0 and x == int(x) else
                  f"<span style='color: #f63f3f;'>▼</span> {-int(x)}" if x < 0 and x == int(x) else

                  f"<span style='color: #31ba3a;'>▲</span> {x:.1f}" if x > 0 else
                  f"<span style='color: #f63f3f;'>▼</span> {abs(x):.1f}" if x < 0 else
                  f"<span style='color:grey;'>-</span>"
    )
    return df



def run_dash_title_overview(df_file, dash_name):
    
    print("Generating Dataframe  ...........")
    df_preview = session_overview_df(df_file)
    
    print("Converting Dataframe to HTML ...........")
    df_session_html = dashboard_session_overview_html(df_preview)

    print("Styling HTML ...........")
    df_final_html = dashboard_full_html(df_session_html, df_file, dash_name)

    return df_final_html
    
# Resize Image to tkinter Label
def update_image(event, label, img_path):
    # Get the current width and height of the label
    label_width = event.width
    label_height = event.height

    # Open the image
    img = Image.open(img_path)

    # Resize the image to fit the label's current size
    img = img.resize((label_width, label_height), Image.ANTIALIAS)

    # Convert the image to PhotoImage
    resized_img = ImageTk.PhotoImage(img)

    # Update the label with the resized image
    label.config(image=resized_img)
    label.image = resized_img


# Retrieve date from filepath name
def get_filepath_date(filepath):
   
    filepath = filepath[(filepath.rfind("/")+1):-4] # Returns the File Name

    date = filepath[: 10]
    date_parsed = datetime.strptime(date, "%Y-%m-%d")
    format_date = date_parsed.strftime("%d %b %Y").upper()
    return format_date

# Retrieve date from filepath name
def get_filepath_time(filepath):
    
    filepath = filepath[(filepath.rfind("/")+1):-4] # Returns the File Name
    #print(f"FP: {filepath}")

    sess_time = filepath[11:15]

    return sess_time


#------------RENDER HTMLS------------------------
def render_html_gui(html_content):
    app = QApplication(sys.argv)
    window = QMainWindow()
    window_title = "Session Preview"
    window.setWindowTitle(window_title)

    # Set up the QWebEngineView
    web_view = QWebEngineView()
    web_view.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
    web_view.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
    web_view.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
    web_view.setHtml(html_content)
    # Layout setup
    container = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(web_view)
    container.setLayout(layout)
    window.setCentralWidget(container)

    # Show the window
    window.show()
    sys.exit(app.exec_())

def render_html_browser(df_input):
    if isinstance(df_input, pd.DataFrame):
        df_input = df_input.to_html()  

    html_file = "dashboard_full_session_overview.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(df_input)
    webbrowser.open(html_file)

def get_lib_match(var, match_header, return_header):
    lib = fetch_google_sheet_data("File Details") 
    matched_var = lib.loc[lib[match_header] == var, [return_header]].values[0][0]
    return matched_var

def get_lib_match_SRT_full(lib, var, header):
    header = header.title()
    if type(var) == str:
        var = var.title()

    matched_var = lib.loc[lib['SRT ' + header] == var, [header]].values[0][0]
    return matched_var

def get_lib_match_SRT_code(lib, var, header):
    header = header.title()
    if type(var) == str:
        var = var.title()

    matched_var = lib.loc[lib['SRT ' + header] == var, [header + ' Code']].values[0][0]
    return matched_var



def get_file_terms_SRT(df):
    
    sess_mode = df.loc[df['gameMode']!= -1]['gameMode'].unique()[0]
    sess_track = df.loc[df['trackId']!= -1]['trackId'].unique()[0]
    sess_team = df.loc[df['carId']!= -1]['carId'].unique()[0]
    sess_length =df.loc[df['sessionLength']!= -1]['sessionLength'].unique()[0]
    sess_type = get_sess_type_simple(df)[0].upper()

    return sess_mode, sess_track, sess_team, sess_length, sess_type


def get_country_flag(code):
    
    # Bug Here
    folder_path = r"F1 Images\F1_Flags\F1_Flags_New\\"
    #    
    #folder_path = "F1 Images/F1_Flags/F1_Flags_New/"
    folder_path = os_convert(folder_path)
    file_path = os_path + folder_path  + code +".png"

    img = Image.open(file_path)
    print("Country Flag loaded......")
    return(img)



def get_team_logo_full(code): # Currently on re-sized folder
    
    folder_path = r"F1 Images\F1_Teams\Teams_Logo_Short\\"
    
    folder_path = os_convert(folder_path)
    file_path = os_path + folder_path  + code  +".png"

    img = Image.open(file_path)
    print("Team Logo loaded......")
    return(img)


def get_track_map(code):
    
    folder_path = r"F1 Images\F1_Track_Map\F1_TrackMaps_final\\"

    folder_path = os_convert(folder_path)
    file_path = os_path + folder_path  + code +".png"

    
    img = Image.open(file_path)
    
    print("Track Map loaded......")
    return(img)


def get_grandprix_logo(code):
    
    folder_path = r"F1 Images\F1_GrandPrix_logo_new\\"

    folder_path = os_convert(folder_path)
    file_path = os_path + folder_path  + code +".png"

    img = Image.open(file_path)
    
    print("Grandprix logo loaded......")
    return(img)

def get_file_terms_disp_SRT(df):
    
    lib_file = fetch_google_sheet_data("File Details") 

    (sess_mode_code, sess_team_code, sess_track_code, sess_length_code, sess_type_code) = get_file_terms_code(df)
    
    sess_track_flag_img = get_country_flag(sess_track_code)
    
    sess_team_logo_img = get_team_logo_full(sess_team_code)

    sess_track_map_img = get_track_map(sess_track_code)

    sess_grandprix_img = get_grandprix_logo(sess_track_code)

    return sess_team_logo_img, sess_track_flag_img, sess_track_map_img, sess_grandprix_img 



def get_file_terms_full(df):
    
    (sess_mode, sess_track, sess_team, sess_length, sess_type) = get_file_terms_SRT(df)
    
    ''' Debugging
    print("\nIn get_file_terms_full")
    
    print(f"Mode: {sess_mode}")
    print(f"Track: {sess_track}")
    print(f"Team: {sess_team}")
    print(f"Length: {sess_length}")
    print(f"Type: {sess_type}")
    '''
    
    lib_file = fetch_google_sheet_data("File Details") 
    sess_mode_full = get_lib_match_SRT_full(lib_file, sess_mode, 'Mode')
    sess_team_full = get_lib_match_SRT_full(lib_file, sess_team, 'Team')
    sess_track_full = get_lib_match_SRT_full(lib_file, sess_track, 'Track')
    sess_length_full = get_lib_match_SRT_full(lib_file, sess_length, 'Length')
    sess_type_full = get_lib_match_SRT_full(lib_file, sess_type, 'Type')

    return (sess_mode_full, sess_team_full, sess_track_full, sess_length_full, sess_type_full)
    

def get_file_terms_code(df):
    
    (sess_mode, sess_track, sess_team, sess_length, sess_type) = get_file_terms_SRT(df)
    lib_file = fetch_google_sheet_data("File Details") 
    sess_mode_code = get_lib_match_SRT_code(lib_file, sess_mode, 'Mode')
    sess_team_code = get_lib_match_SRT_code(lib_file, sess_team, 'Team')
    sess_track_code = get_lib_match_SRT_code(lib_file, sess_track, 'Track')
    sess_length_code = get_lib_match_SRT_code(lib_file, sess_length, 'Length')
    sess_type_code = get_lib_match_SRT_code(lib_file, sess_type, 'Type')
    return (sess_mode_code, sess_team_code, sess_track_code, sess_length_code, sess_type_code)
    # print(f"Mode: {sess_mode_code}")
    # print(f"Track: {sess_track_code}")
    # print(f"Team: {sess_team_code}")
    # print(f"Length: {sess_length_code}")
    # print(f"Type: {sess_type_code}")
    

    return (sess_mode_code, sess_team_code, sess_track_code, sess_length_code, sess_type_code)

def recommend_file_path(sess_mode, sess_team, sess_track, sess_length, sess_type):
    filepath = (f"{sess_mode}_{sess_team}_{sess_track}_{sess_length}_{sess_type}")
    return filepath
    #print(f"\nRecommended Filepath: \n{filepath}")


def get_sess_type_simple(df_file):
    sess_ruleSet_val = df_file[df_file["ruleSet"] != -1]["ruleSet"].unique()[0]

    # retrieve ruleset
    sess_ers_deployMode_val = df_file[df_file["ers_deployMode"] != -1]["ers_deployMode"].unique()[0]

    # Retrieve sessionLength_val from df_file
    sess_length_val = df_file[df_file["sessionLength"] != -1]["sessionLength"].unique()[0]
    
    session_track = df_file[df_file["trackId"] != -1]["trackId"].unique()[0].title()
    sess_track_length = df_file["trackLength"].unique()[0]

    sess_laps = float(df_file[df_file["lapNum"] != -1]["lapNum"].nunique())

    # Distance covered during session
    if session_track == "monaco":  # Special Case
        full_race_target_dist = 260 * 1000  # Only monaco Full Race Distance = 260km

    elif session_track == "spa":  # Special Case
        full_sprint_target_dist = 77.044 * 1000  # Only Belgium Full Sprint Distance = 77.044 km

    else:  # Normal Circumstance
        full_race_target_dist = 305 * 1000  # Full Race Distance usually = 305km
        full_sprint_target_dist = 100 * 1000  # Full Sprint Distance usually = 100km


    # -------------------------------------------------------------------------------
    if (sess_ruleSet_val == 2) & (sess_ers_deployMode_val == 2):  # time attack
        sess_type = "time attack"

    elif (sess_ruleSet_val == 0) & (sess_ers_deployMode_val != 2) & (sess_length_val == 0):
        sess_type = "practice"
    
    elif (sess_ruleSet_val == 0) & (sess_ers_deployMode_val == 2):
        sess_type = "qualifying"

    elif (sess_ruleSet_val == 1): #Sprint or Race
        sess_length_perc = float(get_lib_match(sess_length_val, "SRT Length", "Length Laps"))

        if sess_laps % 2 == 0:  # Even Number
            full_sess_laps = int(sess_laps / sess_length_perc)

        elif sess_laps % 2 == 1:  # Odd Number
            full_sess_laps = int((sess_laps / sess_length_perc) + 1)  # Return full_sess_laps

        full_sess_dist = int(full_sess_laps * sess_track_length)

        # Type: Race
        if full_sess_dist >= full_race_target_dist:

            sess_type = "race"  # Return sess_type
            
            
        # Type: Sprint
        elif (full_sess_dist >= full_sprint_target_dist) & (
                full_sess_dist < full_race_target_dist):
            
            sess_type = "sprint"

        else:
            # check for aborted session telltale signs
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            session_end_lap = sess_laps.max()
            session_end_binIndex = session_end_lap['binIndex'].max()

            if (session_end_lap == df_file["lapNum"].unique().max()) & (session_end_binIndex > 1):

                sess_type = "aborted"
               

    else:
        sess_type = "china"

    return sess_type



#------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_session_type_details(df_working_file, session_track, session_track_length, session_laps):
    session_ruleSet_val = df_working_file[df_working_file["ruleSet"] != -1]["ruleSet"].unique()[0]

    # retrieve ruleset
    session_ers_deployMode_val = df_working_file[df_working_file["ers_deployMode"] != -1]["ers_deployMode"].unique()[0]

    # Retrieve sessionLength_val from df_working_file
    session_sessionLength_val = df_working_file[df_working_file["sessionLength"] != -1]["sessionLength"].unique()[0]
    # -------------------------------------------------------------------------------
    if (session_ruleSet_val == 2) & (session_ers_deployMode_val == 2):  # time attack
        session_type = "time attack"

        session_type = "-2"
        svr_session_length_title = "-2"
        svr_session_perc = -2
        svr_session_distance = -2
        full_session_laps = -2
        session_target_distance = -2
        svr_session_length_title = "-2"
        full_session_distance = "-2"

    elif (session_ruleSet_val == 0) & (session_ers_deployMode_val != 2) & (session_sessionLength_val == 0):
        session_type = "practice"
        #get_session_prac_details(df_working_file, session_laps, session_type)

        session_type = "-3"
        svr_session_length_title = "-3"
        svr_session_perc = -3
        svr_session_distance = -3
        full_session_laps = -3
        session_target_distance = -3
        svr_session_length_title = "-3"
        full_session_distance = "-3"

    elif (session_ruleSet_val == 0) & (session_ers_deployMode_val == 2):
        session_type = "qualifying"
        #get_session_quali_details(df_working_file, session_laps, session_type)

        session_type = "-4"
        svr_session_length_title = "-4"
        svr_session_perc = -4
        svr_session_distance = -4
        full_session_laps = -4
        session_target_distance = -4
        svr_session_length_title = "-4"
        full_session_distance = "-4"

    elif (session_ruleSet_val == 1):
        session_type = "race"
        (
            session_type, svr_session_perc, svr_session_distance,
            full_session_laps, session_target_distance, svr_session_length_title, full_session_distance
        ) = get_session_race_details(df_working_file, session_track, session_track_length, session_laps,
                                     session_sessionLength_val, session_type)

    return (
        session_type, svr_session_perc, svr_session_distance,
        full_session_laps, session_target_distance, svr_session_length_title, full_session_distance
    )


# ---------------------------------------------------------------------------
# Retrieve Session Details
# ---------------------------------------------------------------------------
def get_session_details(df_working_file):
    # Google Sheets
    
    f1_23_srt_lib = fetch_google_sheet_data("Race Details")
    #
    session_team = df_working_file["carId"].unique()[0].lower()

    session_air_temp_start = df_working_file[df_working_file["air_temp"] != -1]["air_temp"].unique()[0]

    # Weather and weather function
    session_weather_val_start = df_working_file[df_working_file["weather"] != -1]["weather"].unique()[0]

    # Session weather Description
    session_weather_descrip_start = get_session_lib_weather(f1_23_srt_lib, session_weather_val_start)

    # Game Mode Function
    session_gameMode = get_game_mode(df_working_file)

    # lap where session ends
    session_end_lap = df_working_file[(df_working_file["validBin"] == 0) & (df_working_file["lap_time"] == -1)][
        "lapNum"].min()

    # binIndex where session ends
    session_end_binIndex = df_working_file[(df_working_file["validBin"] == 0) & (df_working_file["lap_time"] == -1)][
        "binIndex"].min()

    # Check for safety car
    df_working_file[df_working_file["safetyCarStatus"] == 1].any

    session_track = df_working_file["trackId"].unique()[0].lower()
    session_track_length = df_working_file["trackLength"].unique()[0]

    session_laps = df_working_file[
                       (df_working_file["binIndex"] == df_working_file["binIndex"].max()) &
                       (df_working_file["validBin"] == 1) &
                       (df_working_file["lap_time"] != -1)
                       ]["lapNum"].max() + 1

    (
        session_grand_prix, session_track_name, session_track_type,
        session_country, session_city, session_direction, session_tyre_set,
        session_calendar_round, session_grand_prix_title, session_total_turns,
        total_calendar_round, weekend_tyres, session_drs_zones
    ) = get_session_lib_titles(f1_23_srt_lib, session_track)

    sec_1_distance, sec_2_distance, sec_3_distance, = get_session_sector_distance(f1_23_srt_lib, session_track)

    ##Fnction to return session type
    (session_type, svr_session_perc, svr_session_distance,
     full_session_laps, session_target_distance, svr_session_length_title,
     full_session_distance) = get_session_type_details(df_working_file, session_track, session_track_length, session_laps)
    # -------------------------------------------------------------------------------
    # 2nd return (revised)
    return (
        session_team, session_air_temp_start, session_weather_descrip_start, session_gameMode, session_track,
        session_track_length, session_laps,
        session_grand_prix, session_track_name, session_track_type,
        session_country, session_city, session_direction, session_tyre_set,
        session_calendar_round, session_grand_prix_title, session_total_turns,
        total_calendar_round, weekend_tyres,
        sec_1_distance, sec_2_distance, sec_3_distance,
        session_type, svr_session_perc, svr_session_distance,
        full_session_laps, session_target_distance, svr_session_length_title, full_session_distance,
        f1_23_srt_lib, session_drs_zones
    )
# return get_session_details() -----ENDS----------------

def variables_main_title(df_working_file):
    (
    session_team, session_air_temp_start, session_weather_descrip_start, session_gameMode, session_track, session_track_length, session_laps,
    session_grand_prix, session_track_name, session_track_type,
    session_country, session_city, session_direction, session_tyre_set,
    session_calendar_round, session_grand_prix_title, session_total_turns,
    total_calendar_round, weekend_tyres,
    sec_1_distance, sec_2_distance, sec_3_distance,
    session_type, svr_session_perc, svr_session_distance,
    full_session_laps, session_target_distance, svr_session_length_title, full_session_distance,
    f1_23_srt_lib, session_drs_zones
    ) = get_session_details(df_working_file)

    return (
        session_grand_prix, session_gameMode, session_team, session_track,
        svr_session_length_title, session_type, session_calendar_round, total_calendar_round
    )


# Fetch data from specific sheets
lib_drs_zones = fetch_google_sheet_data("DRS Zones")

#race_details_data.infer_objects(copy=False)

lib_drs_zones = lib_drs_zones.infer_objects(copy=False)


def display_title_html(dash_type, df_working_file):
    # Create Dataframe Title with variables
    main_title_html = f"""
    <div style="background-color:#1e1e1e; color:#f3f3f3; padding:20px, border-radius:8px;">
        <div style ="text-align:center; font-weight:bold; text-transform:uppercase; line-height: 1; font-size:22px;">
            {dash_type} Dashboard
        </div>
    </div>
    """
    return main_title_html


def dashboard_test_html(df_input_html, df_working_file, namespace):
    dash_type = get_dataframe_name(df_input_html, namespace)
    print(f"\ndashboard_test_html; dash name= {dash_type}\n")
    #Fix display_main_title ; specifically variables involved
    main_title_html = display_title_html(dash_type, df_working_file)
    
    dash_title_html = main_title_html + df_input_html
    return dash_title_html


def dashboard_full_html(df_input_html, df_working_file, dash_name):
    
    main_title_html = display_main_title_html(dash_name, df_working_file)
    
    dashboard_session_overview = main_title_html + df_input_html
    return dashboard_session_overview



def get_dataframe_name(dataframe, namespace):
    name = next(
        (var_name for var_name in namespace
         if namespace[var_name] is dataframe and not var_name.startswith('_')),
        None
    )
    if name:
        name = name.replace("dashboard_", "").replace("df_", "").replace("_html", "")
        name = name.replace("full_", "").replace("_full", "").replace("Full ", "")
        name = name.replace("_", " ").title()
        return name
    return None


def highlight_rows(row):
    # Apply alternating colors
    if row.name % 2 == 0:
        # Index even rows
        return ['background-color: lightblue'] * len(row)
    else:
        # Index odd rows
        return ['background-color: lightgray'] * len(row)


#Replace in-lap/out-lap with PIT static graphic
def html_highlight_pit_status(df, col_colour):
    # Define tyre types and their colors
    pit_status_colours = {
        "PIT": "#07d6fa",  # PIT - Blue
        #"-": "#a1a1aa",  # No PIT - grey
        
    }

    # Apply conditional formatting
    df[col_colour] = df.apply(
        lambda row: (
            f"<div style='position: relative; width: 35px; height: 25px; display: inline-flex; justify-content: center; align-items: center; border: 3px solid {pit_status_colours.get(row[col_colour], '#000000')}; border-radius: 10%;'>"
            f"<span style='position: absolute; width: 100%; height: 100%; font-family: monospace; display: flex; justify-content: center; align-items: center; color: {pit_status_colours.get(row[col_colour], '#000000')}; font-weight: 700; font-size: 15px;z-index: 4;'>{row[col_colour]}</span>"
            f"</div>"
        ) if row[col_colour] in pit_status_colours else row[col_colour],
        axis=1
    )
    return df

def html_highlight_drs_zone_status(df, col_colour):
    # Define tyre types and their colors
    drs_colours = {
        1: "#10b981",  # DRS - Green
        0: "#3f3f46",  # No DRS - Dark Grey
        
    }

    # Apply conditional formatting
    df[col_colour] = df.apply(
        lambda row: (
            f"<div style='position: relative; width: 35px; height: 25px; display: inline-flex; justify-content: center; align-items: center; border: 3px solid {drs_colours.get(row[col_colour], '#000000')}; border-radius: 10%;'>"
            f"<span style='position: absolute; width: 100%; height: 100%; font-family: monospace; display: flex; justify-content: center; align-items: center; color: {drs_colours.get(row[col_colour], '#000000')}; font-weight: 700; font-size: 15px;z-index: 4;'>DRS</span>"
            f"</div>"
        ) if row[col_colour] in drs_colours else row[col_colour],
        axis=1
    )
    return df

def get_drs_zones(lib, session_track):
    matched_track = lib.loc[lib['F1 23 Track'] == session_track.title()]
    
    if not matched_track.empty:
        return matched_track
    else:
        print("No matching track found.")
        return None  # Explicitly return None if no match is found

def get_session_valid_laps(df_working_file):
    valid_laps = (df_working_file[
                      (df_working_file["lapNum"] != -1) &
                      (df_working_file["validBin"] == 1) &
                      (df_working_file["binIndex"] == 50)
                      ]["lapNum"].max()) + 1
    return valid_laps

# Dataframe Summary Output
def session_overview_df(df_working_file):
    # Looping through laps
    df_session_overview = []

    # Highlighting Fastest Lap Time
    # min_lap_time = float('inf')  # Initialize to infinity to find the minimum lap time
    # min_lap_index = None
    (
        session_team, session_air_temp_start, session_weather_descrip_start, session_gameMode, session_track,
        session_track_length, session_laps,
        session_grand_prix, session_track_name, session_track_type,
        session_country, session_city, session_direction, session_tyre_set,
        session_calendar_round, session_grand_prix_title, session_total_turns,
        total_calendar_round, weekend_tyres,
        sec_1_distance, sec_2_distance, sec_3_distance,
        session_type, svr_session_perc, svr_session_distance,
        full_session_laps, session_target_distance, svr_session_length_title, full_session_distance,
        f1_23_srt_lib, session_drs_zones
    ) = get_session_details(df_working_file)

    # Looping through the valid laps,
    valid_laps = get_session_valid_laps(df_working_file)

    laps_in_session = (df_working_file[(df_working_file["lapNum"] != -1)]["lapNum"].unique())

    matched_track = get_drs_zones(lib_drs_zones, df_working_file['trackId'].unique()[0])
    drs_zone_distances = matched_track.loc[:, "DRS Z1 Start" : "DRS Z4 End"].dropna(axis=1, how="all").to_dict(orient="records")

    
    for lap in range(valid_laps):
        # Check if next lap exists
        if lap in laps_in_session:
            # Calling function for lap indexing
            race_lap_data, race_start_lap, race_end_lap, race_one_third_lap = get_race_lap_data(df_working_file, lap)
            
            # Extract Lap Time
            lap_time = race_end_lap["lap_time"]

            # tyre age (mid lap or 1/3 of lap) : tyre change happens slightly after race_start_lap
            if race_one_third_lap["tyres_age"] != -1:
                tyres_age = race_one_third_lap["tyres_age"]
            else:
                tyres_age = race_end_lap["tyres_age"]
            # if race_one_third_lap tyre age returns -1, then race_end_lap


            #-------------------DRS START------------------ 
            drs_active_zones = []
            # Iterate through each DRS zone set in drs_zone_distances
            for zone in drs_zone_distances:
                for i in range(1, len(zone)//2 + 1):
                    start_key = f"DRS Z{i} Start"
                    end_key = f"DRS Z{i} End"
                    
                    # Check if the start and end keys exist in the current zone dictionary
                    start, end = zone[start_key], zone[end_key]
                    
                    # Define the condition for DRS activation in this zone
                    drs_condition = (
                        (race_lap_data["lap_distance"] >= start) &
                        (race_lap_data["lap_distance"] <= end) &
                        (race_lap_data["drs"] == 1)
                    )

                    # Determine if DRS is active
                    drs_active = 1 if drs_condition.any() else 0
                    drs_active_zones.append(drs_active)

            #-------------------DRS END------------------
            
            
            # ---------------get lap_position---------------
            # Position at the start of lap
            position_lap_start = race_lap_data[race_lap_data["validBin"] == 1].iloc[0]["race_position"]

            # Position at the end of lap
            position_lap_end = race_lap_data[race_lap_data["validBin"] == 1].iloc[-1]["race_position"]

            # Positions gained/lost within lap
            position_change = -1 * (position_lap_end - position_lap_start)

            # Check if lap end exists
            if race_end_lap["validBin"] >= 1:
                race_lap_tyre = race_end_lap["tyre_compound_0"]
            else:
                race_lap_tyre = race_start_lap["tyre_compound_0"]
                
            # Map the tyre compound value to its type using tyre_dict
            if race_lap_tyre > 0:
                tyre_name_full = weekend_tyres.loc[weekend_tyres["Tyre Value"] == race_lap_tyre, "Tyre Type"].values[0]
            else:
                tyre_name_full = "-"

            tyre_name_short = tyre_name_full[0]

            # calculate_sector_times(lap_data, sector_distances)
            sec_1_time, sec_2_time, sec_3_time = calculate_sector_times(f1_23_srt_lib, session_track, race_lap_data)

            # Formatted Lap Time per lap
            race_final_lap_time = lap_time_format(race_end_lap['lap_time'].round(3))  # in laps_in_session definition
            # race_final_lap_time = race_end_lap['lap_time'] #in laps_in_session definition

            # ----------------------get pit details START----------------------
            if race_lap_data['pit_status'].any():
                pit_status, pit_stop_time, pit_lane_time = get_pit_details(race_lap_data, race_end_lap, race_start_lap)
                if isinstance(pit_stop_time, float): 
                    pit_stop_time = f"{pit_stop_time:.2f}"
                    
                if isinstance(pit_lane_time, float): 
                    pit_lane_time = f"{pit_lane_time:06.3f}"
            else:
                pit_status = "-"
                pit_stop_time = "-"
                pit_lane_time = "-"

            # ----------------------get pit details END----------------------

            # Red Flag
            red_flag_curr_lap = df_working_file[(df_working_file["lapNum"] == lap)]["num_red"].max()
            red_flag_prev_lap = df_working_file[(df_working_file["lapNum"] == (lap - 1))]["num_red"].max()
            increment_red_flag_per_lap = red_flag_curr_lap - red_flag_prev_lap

            # Safety Car
            safety_car = ((race_lap_data['safetyCarStatus'].unique()) > 0).any()

            # Status
            race_status = "SC" if (safety_car == True) else ("RF" if (increment_red_flag_per_lap == 1) else "-")

        else:  # if lap NOT in laps_in_session:
            if lap > 0:  # to prevent (lap-1) index error

                prev_red_flag = (df_working_file[(df_working_file["lapNum"] == (lap - 1))]["num_red"].max()) - (
                    df_working_file[(df_working_file["lapNum"] == (lap - 2))]["num_red"].max())

                if prev_red_flag == 1:
                    empty_val = "RF"
                    # elif DNFs (abrupt quit)
                # elif Invalid Lap due to track limits or others
                # elif
                else:
                    empty_val = "-"
            else:
                empty_val = "-"

            race_final_lap_time = empty_val
            sec_1_time = empty_val
            sec_2_time = empty_val
            sec_3_time = empty_val
            tyre_name_short = empty_val
            tyres_age = empty_val
            position_lap_end = empty_val
            position_change = empty_val
            pit_status = empty_val
            pit_stop_time = empty_val
            pit_lane_time = empty_val
            race_status = empty_val

        # Append the lap info to race_laps list
        lap_info = ({
            "Lap": lap,
            "Time(s)": race_final_lap_time,
            "Sector 1": sec_1_time,
            "Sector 2": sec_2_time,
            "Sector 3": sec_3_time,
            "Tyre": tyre_name_short.upper(),
            "Tyre Age": tyres_age,
            "Position End": position_lap_end,
            "Position (+/-)": position_change,
            "Pit Status": pit_status,
            "Pit Stop (s)": pit_stop_time,
            "Pit Lane (s)": pit_lane_time,
            "Status": race_status,
        })
        #df_session_overview.update(drs_zone_columns)
        
        # Add the dynamically created DRS zone columns
        for i, drs_zone in enumerate(drs_active_zones, start=1):
            lap_info[f"DRS Zone {i}"] = drs_zone
    
        # Append to session overview list
        df_session_overview.append(lap_info)
    
    # for lap in range(valid_laps) EXIT
    # -------------------------------------------------
   

    
    # Convert the dictionary to a DataFrame and append to df_session_overview
    df_session_overview = pd.DataFrame(df_session_overview)

    return df_session_overview

def dashboard_session_overview_html(df_input):
    # ------------------------------------------------
    # Red Flag Sign Banner v1
    # ------------------------------------------------
    card_RF_sign_1 = f"""<div style="height: 30px; width: 100%; background-color: #010101; font-family: Verdana; text-align: center;color: #e10101; font-weight: 650; font-size: 15px; display: flex; justify-content: center; align-items: center; padding: 5px 0;"><img src="flag_red.png" style="height: 30px; vertical-align: middle;">&ensp;&ensp;RED FLAG RACE SUSPENDED</div>"""
    # ------------------------------------------------
    # Safety Car Sign Banner
    # ------------------------------------------------
    card_SC_sign_1 = f"""<div style="height: 30px; width: 100%; background-color: #010101; font-family: Verdana; text-align: center; display: flex; justify-content: center; align-items: center; padding: 5px 0;"><div style="margin-right: 10px;"><img src="flag_yellow.png" style="height: 30px; vertical-align: middle;"></div><div style="color: #fff407; font-weight: 650; font-size: 15px; padding-left: 10px; display: flex; align-items: center;">SAFETY CAR</div></div>"""
    # ---------------------------------------------------------


    # Highlight the fastest lap and sectors using the helper function
    df_input = html_highlight_fastest_time(df_input, "Time(s)")
    df_input = html_highlight_fastest_time(df_input, "Sector 1")
    df_input = html_highlight_fastest_time(df_input, "Sector 2")
    df_input = html_highlight_fastest_time(df_input, "Sector 3")

    # Replace Red Flag Shutdown lap with "-"
    df_input = html_cards_status(df_input, card_RF_sign_1, "RF", exclude_columns=["Lap"])

    # Replace Safety Car lap with "-"
    df_input = html_cards_status(df_input, card_SC_sign_1, "SC", exclude_columns=["Lap"])
    
    # Highlight the in-lap and out-lap timings
    df_input = html_highlight_pit_lap_times(df_input, "Pit Status", "Time(s)")

    # Highlight the in-lap and out-lap timings
    df_input = html_highlight_pit_status(df_input, "Pit Status")

    # Highlight the DRS zone activation
    for i in range(len(df_input.filter(like="DRS").columns)):
        print(f"Zone {i+1}")
        df_input = html_highlight_drs_zone_status(df_input, f"DRS Zone {i+1}")

    # Colour Tyre Types in DataFrame
    df_input = html_highlight_tyres(df_input, "Tyre")
    
    # Colour Safety Car Sign in DataFrame
    df_input = html_colour_status(df_input, "Status")

    # Apply the colour_position_change function only once
    df_input = html_colour_position_change(df_input, "Position (+/-)")

    # Styled dataframe
    styled_df = df_input.style.set_table_styles(
        [
            # Header styling
            {'selector': 'thead th', 'props': [('background-color', '#1e1e1e'), ('color', '#e88c1e'), ('font-weight', 'bold'), ('font-size', '18px'), ('height', '50px')]},
            
            # Header row height
            #{'selector': 'thead th', 'props': [('height', '30px')]},  

            # Center-align all cells
            {'selector': 'thead th, tbody td', 'props': [('text-align', 'center')]},
          
            # Odd rows styling
            {'selector': 'tbody tr:nth-of-type(odd)', 'props': [('background-color', '#2d2e31'), ('color', '#f3f3f3')]},
            
            # Even rows styling
            {'selector': 'tbody tr:nth-of-type(even)', 'props': [('background-color', '#262626'), ('color', '#f3f3f3')]},
            
            # Column widths for specific columns based on respective headers
            {'selector': 'th:nth-child(1), td:nth-child(1)', 'props': [('width', '2%')]},   # Index Column
            {'selector': 'th:nth-child(2), td:nth-child(2)', 'props': [('width', '3%')]},   # Lap column, 
            
            {'selector': 'th:nth-child(3), td:nth-child(3)', 'props': [('width', '7%')]},  # Time(s) column
            {'selector': 'th:nth-child(4), td:nth-child(4)', 'props': [('width', '5%')]},  # Sector 1 column
            {'selector': 'th:nth-child(5), td:nth-child(5)', 'props': [('width', '5%')]},   # Sector 2 column
            {'selector': 'th:nth-child(6), td:nth-child(6)', 'props': [('width', '5%')]},  # Sector 3 column

            {'selector': 'th:nth-child(7), td:nth-child(7)', 'props': [('width', '7.5%')]},  # Tyre Column 
            {'selector': 'th:nth-child(8), td:nth-child(8)', 'props': [('width', '7%')]},  # Tyre Age column
            
            {'selector': 'th:nth-child(9), td:nth-child(9)', 'props': [('width', '5%')]},  # Position column
            {'selector': 'th:nth-child(10), td:nth-child(10)', 'props': [('width', '5%')]},  # Pos Gain/Lost column 

            {'selector': 'th:nth-child(11), td:nth-child(11)', 'props': [('width', '5%')]},  # Pit Status column 
            {'selector': 'th:nth-child(12), td:nth-child(12)', 'props': [('width', '5%')]},  # Pit Stop(s) column 
            {'selector': 'th:nth-child(13), td:nth-child(13)', 'props': [('width', '5%')]},  # Pit Lane(s) column 

            {'selector': 'th:nth-child(14), td:nth-child(14)', 'props': [('width', '5%')]},  # Status column 

            {'selector': 'th:nth-child(15), td:nth-child(15)', 'props': [('width', '4.5%')]},  # Status column 
            {'selector': 'th:nth-child(16), td:nth-child(16)', 'props': [('width', '4.5%')]},  # Status column 
        
        ]   
    )

    # Convert DataFrame to HTML
    df_html = styled_df.to_html(escape=False)

    # Return combined HTML 
    return df_html


def os_filepath(filepath_race):
    
    system_user = getpass.getuser()
    
    os = platform.system()

    if system_user == "User":       # Home Windows PC
        os_path = r"C:\Users\User\PycharmProjects\F1 Python\\"

    if system_user == "dextery":    # PSA Work Laptop
        os_path = r"C:Users\dextery\Documents\Dexter Documents\Python\f1_data\\"
        
    elif system_user == "dexteryippro":            # Home Macbook Pro
        os_path = "/Users/dexteryippro/Documents/F1 Python/"
    
    folder_path = filepath_race[(filepath_race.find("F1 Python")+(len("F1 Python")+1)):]
    
    final_path = os_path + folder_path.replace('\\', '/')
    print(f"{final_path}\n")
    
    return final_path


def unique_col_values(df_file, list):
    col_unique_values = {}  # dict to store unique setup values

    for col in list:
        if col in df_file.columns:  # precautionary ; Check if column exists in df
            #Check metric max and min values from 
            unique_values = df_file[df_file[col]!= -1][col].unique().tolist()  # Convert unique values to a list
            col_unique_values[col] = unique_values
        else:
            col_unique_values[col] = "Column not found in the DataFrame."

    return col_unique_values

def os_convert(folder_path):
    curr_os = platform.system()
    
    if folder_path.count("\\") >= 1: # Windows-added filepath 
        if curr_os == "Windows":
            folder_path = folder_path
        elif curr_os == "Darwin": 
            folder_path = folder_path.replace('\\', '/')
    else: # Mac-Added Filepath
        if curr_os == "Darwin":
            folder_path = folder_path
        elif curr_os == "Windows": 
            folder_path = folder_path.replace('\\', '/')# Check here
    return folder_path


def get_tyre_map_only(df_working_file):
    session_track = df_working_file["trackId"].unique()[0].lower()
    f1_23_srt_lib = fetch_google_sheet_data("Race Details")
    matched_track = f1_23_srt_lib.loc[
        f1_23_srt_lib['F1 23 Track'] == session_track.title(),
        [
            'Grand Prix', 'Track Name', 'Track Type', 'Country', 'City', 'Direction', 'Tyre Set',
            '2023 Round', 'Grand Prix Title', 'No.of Turns',
        ]
    ].values

    session_tyre_set = matched_track[0][6]

    weekend_tyres = get_weekend_tyres(f1_23_srt_lib, session_tyre_set)
    return weekend_tyres

def format_mins_time(mins):
    hh = mins // 60
    mm = mins % 60
    final_time = f"{hh:02d}:{mm:02d}"
    return final_time


def calculate_soc(df):
    max_ers_val = df.iloc[0]['ers_store']
    df_new = df.copy()
    ers_store_val = df_new['ers_store']
    ers_harv_mguh_val = df_new['ers_harv_mguh']
    ers_harv_mguk_val = df_new['ers_harv_mguk']
    ers_deployed_val = df_new['ers_deployed']

    col_soc = (ers_store_val)/(max_ers_val) * 100
    df_new['SOC'] = col_soc

    return df_new


def get_tyre_alloc(tyre_set, tyre):
    tyre_name = tyre_set[tyre_set["Tyre Value"] == tyre]['Tyre Abv'].values[0]
    return tyre_name

def get_tyre_life(df):
    for i in range(4):
        df[f'tyre_life_{i}'] = (1 - df[f'tyre_wear_{i}'])*100
        
    return df


def get_delta_name(metric): 
    if metric.count("_") > 1:
        extract = metric[metric.find("_") + 1:metric.rfind("_")]
        suffix = metric[metric.rfind("_")+1 :]  
        final = extract + "_Delta_" + suffix
    else:
        extract = metric[metric.find("_") + 1:]
        final = extract + "_Delta"
    
    return final    


def replace_np(df_series, string):
    df_series = np.where(df_series == 1, string, '-') 
    return df_series


def calculate_deltas(df, header):
    df = df.copy()  # Avoid modifying the original DataFrame
    # add passed-header string 
    name_delta = get_delta_name(header)

    for lap in df['lapNum'].unique():
        if lap == df['lapNum'].min():
            # First lap: time delta should be 0
            df.loc[df['lapNum'] == lap, name_delta] = 0  
        else:
            # Filter for current and previous lap
            df_lap = df[df['lapNum'] == lap].copy()
            df_lap_pr = df[df['lapNum'] == (lap - 1)][['binIndex', header]].copy()

            # Merge on binIndex, using an **inner** join to avoid NaNs
            merged = df_lap.merge(df_lap_pr, on='binIndex', how='left', suffixes=('', '_prev'))

            # Dynamically reference the previous lap column
            prev_col = f"{header}_prev"
            merged[prev_col] = merged[prev_col].fillna(0)

            # Calculate time delta
            merged[name_delta] = (merged[header] - merged[prev_col]).round(3)

            # Update df using .loc
            df.loc[df['lapNum'] == lap, name_delta] = merged[name_delta].values
    
    return df


def get_magnitude(df, column_list, final_metric):
    sq_total = 0

    for idx, metric in enumerate(column_list):
        metric_val_sq = df[metric] ** 2
        sq_total += metric_val_sq
        
    df[final_metric] = (sq_total) ** 0.5
    return df.copy()


def tyre_colour(df_import):
    df = df_import.copy()
    tyre_colour_lib = {
            "H": "#f4f4f4",  # Hard
            "M": "#fbcc1c",  # Medium
            "S": "#f12f32",  # Soft
            "I": "#128330",  # Intermediate
            "W": "#1f6da1"   # Wet
        }

    df["tyre_colour"] = df["tyre_compound_0"].map(tyre_colour_lib)
    return df

# ---------------------------------
# PROCESSING & CLEAN UP
# ---------------------------------
def raw_df(path):
    new_filepath = os_filepath(path)

    df = pd.read_csv(new_filepath, delimiter='\t')
    return df


def clean_df(df):
    valid_laps = get_valid_laps(df)
    
    df_clean = df[
        df['lapNum'].isin(valid_laps)
    ]
    return df_clean


def process_df(df):
    
    print("....Calculating Preliminaries.......")
    lib_param = fetch_google_sheet_data("F1 23 Parameters")
    

    df_new = calculate_soc(df)
    
    df_new = get_tyre_life(df_new)
    
    df_new = calculate_deltas(df_new, 'lap_time')
    
    df_new = get_magnitude(df_new, ['gforce_X', 'gforce_Y', 'gforce_Z'], 'gforce')

    df_new['lap_time_i'] = df_new['lap_time'].diff()
    df_new.loc[
        df_new['binIndex'] == 0, "lap_time_i" 
    ] = df_new['lap_time'] 


    print("....Converting Header Metrics.......")

    # for i in range(4):
    #     metric = f'tyre_temp_{i}'
    #     df_new = calculate_deltas(df_new, metric)
    #     # Write

    # for i in range(4):
    #     metric = f'tyre_tempInternalAir_{i}'
    #     df_new = calculate_deltas(df_new, metric)

    total_df_columns = len(df.columns)

    for idx, header in enumerate(df):
        metric_type = lib_param[lib_param['Parameter'] == header]["Convert Type"].values[0]
        metric_rate = lib_param[lib_param['Parameter'] == header]["Conversion"].values[0]
        
        if idx == (total_df_columns/2):
            print("At halfway Point.....")
            

        if header == "lap_time":
            df_new["lap_time_f"] = df_new[header].apply(globals()[metric_rate])

        elif metric_type == "str":
            df_new[header] = df_new[header].copy()
            
        elif metric_type == "int":
            df_new[header] *= int(metric_rate)
            
        elif metric_type == "float":
            df_new[header] *= float(metric_rate)
            
        elif metric_type == "func":
            df_new[header] = df_new[header].apply(globals()[metric_rate])
        

        elif metric_type == "strfunc":
            func_name, str_arg = metric_rate.split(",")  # Expecting "replace_np,PIT LIMIT"
            df_new[header] = df_new[header].apply(lambda x: globals()[func_name](x, str_arg.strip()))
        
        
        elif metric_type == "tyre":
            tyre_dict = get_tyre_map_only(df).set_index("Tyre Value")["Tyre Abv"].to_dict()
            df_new[header] = df_new[header].map(tyre_dict)

        else:
            df_new[header] *= eval(metric_rate)
    
    df_final = tyre_colour(df_new) 

    print("....Processing Complete.......")
    return df_final

# ======================

def full_df(filepath):
    print("Importing df......")
    df_raw = raw_df(filepath)

    print("Cleaning df......")
    df_clean = clean_df(df_raw)

    print("Processing df......")
    df_file = process_df(df_clean)

    return df_file


def increment_hex_colour(hex_colour, step):
    # Convert hex to integer
    colour_int = int(hex_colour.lstrip("#"), 16)
    
    # Increment color value
    colour_int = (colour_int + step) % 0xFFFFFF  # Loop within valid hex range
    
    # Convert back to hex, ensuring it's always 6 characters
    return f"#{colour_int:06X}"




def get_ext_value(df, metric, inp):
    ext = inp.lower()

    if ext == "min":
        return_val = df[
                (df[metric] == df[metric].min())
            ][metric].values[0]
    elif ext == "max": 
        return_val = df[
                (df[metric] == df[metric].max())
            ][metric].values[0]
    else:
        print(f"\n{inp.title()} is Invalid\n")
        return_val = "!"
    return return_val


def get_limits(df, metric):
    metric_min = get_ext_value(df, metric, "min")
    metric_max = get_ext_value(df, metric, "max")
    comp_list = [abs(metric_min), abs(metric_max)]
    limit = round(max(comp_list) + 1, 0)
    return limit


COLOUR_MAP_51 = {
    0: "#2ea934",
    10: "#2c9b27",
    15: "#60a638",
    20: "#90af3c",
    25: "#a2b246",
    30: "#bdb84c",
    35: "#d0c058",
    40: "#ddbf54",
    45: "#d4ba5b",
    50: "#d8b64d",
    55: "#cba843",
    60: "#d99c55",
    65: "#db9348",
    70: "#cf7c45",
    75: "#cb7346",
    80: "#be5f37",
    85: "#a64333",
    90: "#a43127",
    95: "#a0252e",
    100: "#8a191c"
}



COLOUR_MAP_2 = {
    0: "#30d058",   # Brighter green
    10: "#38b24a",
    15: "#50a63f",
    20: "#6a9e3a",
    25: "#81a437",
    30: "#a2a834",
    35: "#c2ae38",
    40: "#dab83e",
    45: "#e4b33b",
    50: "#e8a739",
    55: "#e6973b",
    60: "#e1883c",
    65: "#db733b",
    70: "#d15e37",
    75: "#c54933",
    80: "#b83630",
    85: "#a8272d",
    90: "#981e29",
    95: "#891a25",
    100: "#ff443b"   # Bright red
}

def hex_to_rgb(hex_color):
    return np.array(mcolors.hex2color(hex_color)) * 255

def rgb_to_hex(rgb_tuple):
    return mcolors.to_hex(np.array(rgb_tuple) / 255)

def map_wear_colour(wear_percentage):
    """
    Interpolates colour based on wear percentage
    """
    wear_levels = sorted(COLOUR_MAP_2.keys())
    rgb_values = [hex_to_rgb(COLOUR_MAP_2[level]) for level in wear_levels]
    
    if wear_percentage <= wear_levels[0]:
        return COLOUR_MAP_2[wear_levels[0]]
    elif wear_percentage >= wear_levels[-1]:
        return COLOUR_MAP_2[wear_levels[-1]]
    
    for i in range(len(wear_levels) - 1):
        if wear_levels[i] <= wear_percentage <= wear_levels[i + 1]:
            fraction = (wear_percentage - wear_levels[i]) / (wear_levels[i + 1] - wear_levels[i])
            interpolated_rgb = (1 - fraction) * rgb_values[i] + fraction * rgb_values[i + 1]
            return rgb_to_hex(interpolated_rgb)


def convert_hex_rgb(colour):
    colour_len = len(colour)
    if colour_len == 3: # RGB
        colour_type = "rgb"
    else:
        colour_type = "hex"
        colour = colour.replace("#", "")


    if colour_type == "hex":
        r = int(colour[:2], 16)
        g = int(colour[2:4], 16)
        b = int(colour[4:6], 16)

        final_code = (r, g, b) 

    elif colour_type == "rgb":
        h_0 = hex(colour[0])[2:].zfill(2).upper()
        h_1 = hex(colour[1])[2:].zfill(2).upper()
        h_2 = hex(colour[2])[2:].zfill(2).upper()

        final_code = f"#{h_0}{h_1}{h_2}"

    else:
        final_code = "unknown"

    return final_code


def darken_colour(colour, ):
    factor = 0.5
    # Convert HEX to RGB
    old_r, old_g, old_b = convert_hex_rgb(colour)
   
    # Convert RGB to HLS
    h, l, s = colorsys.rgb_to_hls(old_r/255, old_g/255, old_b/255)

    # Darken by factor
    l = max(0, l* factor)
    
    # Convert HLS to RGB
    new_r, new_g, new_b = colorsys.hls_to_rgb(h, l, s)
    new_rgb =  (int(new_r*255), int(new_g*255), int(new_b*255))

    new_hex = convert_hex_rgb(new_rgb)

    return new_hex

