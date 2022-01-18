import datetime
import json
import logging
import os


def get_maps():
    try:
        with open(os.path.dirname(__file__) + f'/maps.json') as f:
            maps = json.load(f)
    except FileNotFoundError as error:
        logging.error(
            f"Map data does not exist!")
    return maps


def input_to_timedelta(time):
    milliseconds = "0"
    seconds = "0"
    minutes = "0"
    hours = "0"
    # check for milliseconds
    if time.count(".") == 1:
        milliseconds = time.split(".")[1] + "00"
        # remove milliseconds from time str
        time = time.split(".")[0]
        if time == '':
            time = '0'
    # SS
    if time.count(":") == 0:
        seconds = time
    # MM:SS
    if time.count(":") == 1:
        seconds = time.split(":")[1]
        minutes = time.split(":")[0]
    # HH:MM:SS
    if time.count(":") == 2:
        seconds = time.split(":")[2]
        minutes = time.split(":")[1]
        hours = time.split(":")[0]

    if (len(seconds) > 2 and time.count(":") != 0) or len(minutes) > 2 or len(hours) > 2:
        return None

    return datetime.timedelta(
        hours=int(hours), minutes=int(minutes), seconds=int(seconds), milliseconds=int(milliseconds))
