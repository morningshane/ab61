#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import json
import logging
import traceback
from mod_infowindow import infowindow
import sys
import os
import time
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

reload(sys)
sys.setdefaultencoding('utf-8')
time.sleep(10)

# Select pluggable module for todo list, calendar and weather.
# Replace the mod_<name> with one of:
# TODO: mod_todoist, mod_teamwork
# CALENDAR: mod_google, mod_ical
# WEATHER: mod_owm, mod_wunderground

from mod_utils import iw_utils
from mod_todo import mod_todoist as modTodo             # TODO
from mod_calendar import mod_google as modCalendar      # CALENDAR
from mod_weather import mod_owm as modWeather           # WEATHER

# TODO: Create dictionaries for API args. so that they can be custom.

# Configuration ###############################################################
with open(iw_utils.getCWD()+"/config.json") as config_file:
    config_data = json.load(config_file)

## Rotation. 0 for desktop, 180 for hanging upside down
rotation = config_data["general"]["rotation"]
todo_opts = config_data["todo"]
calendar_opts = config_data["calendar"]
weather_opts = config_data["weather"]

# END CONFIGURATION ###########################################################
###############################################################################

# Setup Logging -  change to logging.DEBUG if you are having issues.
logging.basicConfig(level=logging.DEBUG)
logging.info("Configuration Complete")

# Custom exception handler. Need to handle exceptions and send them to the
# display since this will run headless most of the time. This gives the user
# enough info to know that they need to troubleshoot.
def HandleException(et, val, tb):
    iw = infowindow.InfoWindow()
    iw.text(0, 10, "EXCEPTION IN PROGRAM", 'robotoBlack18', 'black')
    iw.text(0, 30, str(val), 'robotoBlack18', 'black')
    iw.text(0, 60, "Please run program from command line interactivly to resolve", 'robotoBlack18', 'black')
    print ("EXCEPTION IN PROGRAM ==================================")
    print (val)
    print (et)
    print (tb)
    print ("END EXCEPTION =========================================")
    iw.display(rotation)

sys.excepthook = HandleException

# Main Program ################################################################
def main():
    # Instantiate API modules
    todo = modTodo.ToDo(todo_opts)
    cal = modCalendar.Cal(calendar_opts)
    weather = modWeather.Weather(weather_opts)

    ## Setup e-ink initial drawings
    iw = infowindow.InfoWindow()

    ### Weather Grid
    temp_rect_width = 102
    temp_rect_left = (iw.width / 2) - (temp_rect_width / 2)
    temp_rect_right = (iw.width / 2) + (temp_rect_width / 2)

    iw.rectangle(temp_rect_left, 0, temp_rect_right, 64, 'red')

    iw.bitmap(375, 0, "windSmall.bmp")      # Wind Icon
    iw.line(461, 0, 461, 64, 'black')       # Third Vertical Line

    iw.bitmap(464, 0, "rainSmall.bmp")      # Rain Icon
    iw.line(550, 0, 550, 64, 'black')       # Fourth Vertical Line

    iw.bitmap(554, 0, "snowSmall.bmp")      # Snow Icon
    
    # Center cal/todo divider line
    iw.rectangle(315, 64, 325, 384, 'red')  # Red Rectangle


    # Calendar / Todo Title Line
    iw.rectangle(0, 65, 640, 90, 'red')     # Red Rectangle 

    # Todo / Weather Titles
    iw.text(460, 60, u"待办", 'yaheiRegular24', 'white')
    iw.text(130, 60, u"日历", 'yaheiRegular24', 'white')
    iw.text(68, 32, time.strftime("%a %d-%m-%Y"), 'robotoBlack24', 'red')


    # DISPLAY TODO INFO
    # =========================================================================
    todo_items = todo.list()
    logging.debug("Todo Items")
    logging.debug("-----------------------------------------------------------------------")
    t_y = 93
    for todo_item in todo_items:
        iw.text(329, t_y, unicode(todo_item['content']), 'yaheiRegular18', 'black')
        t_y = (t_y + 26)
        iw.line(325, (t_y - 2), 640, (t_y - 2), 'black')
        logging.debug("ITEM: "+todo_item['content'])
        
    # DISPLAY CALENDAR INFO
    # =========================================================================
    cal_items = cal.list()
    logging.debug("Calendar Items")
    logging.debug("-----------------------------------------------------------------------")
    c_y = 94

    # Time and date divider line
    (dt_x, dt_y) = iw.getFont('robotoRegular10').getsize('99-12-2000')

    for cal_item in cal_items:
        (x, y) = iw.text(3, (c_y - 1), str(cal_item['date']), 'robotoRegular10', 'black')
        iw.line((dt_x + 5), c_y, (dt_x + 5), (c_y +32), 'black')
        iw.text(3, (c_y + 10), str(cal_item['time']), 'robotoRegular10', 'black')
        iw.text((dt_x + 9), (c_y - 1), iw.truncate(unicode(cal_item['content']), 'yaheiRegular18'), 'yaheiRegular18', 'black')
        c_y = (c_y + 26)
        iw.line(0, (c_y - 3), 313, (c_y - 3), 'black')
        # logging.debug("ITEM: "+str(cal_item['date']), str(cal_item['time']), str(cal_item['content']))
        logging.debug("ITEM: "+str(cal_item['content']))
        
    # DISPLAY WEATHER INFO
    # =========================================================================
    weather = weather.list()
    logging.debug("Weather Info")
    logging.debug("-----------------------------------------------------------------------")
    # Set unit descriptors
    if weather_opts['units'] == 'imperial':
        u_speed = "mph"
        u_temp = "F"
    elif weather_opts['units'] == 'metric':
        u_speed = "m/sec"
        u_temp = "C"
    else:
        u_speed = "m/sec"
        u_temp = "K"

    deg_symbol = u"\u00b0"
    iw.bitmap(2, 2, weather['icon'])
    iw.text(70, 2, weather['description'].title(), 'robotoBlack24', 'black')
    
    # Temp ( adjust for str length )
    (t_x, t_y) = iw.getFont('robotoBlack48').getsize(str(weather['temp_cur'])+deg_symbol)
    temp_left = (iw.width / 2) - (t_x / 2)
    iw.text(temp_left, 2, str(weather['temp_cur'])+deg_symbol, 'robotoBlack48', 'white')
    t_desc_posx = (temp_left + t_x) - 15
    iw.text(t_desc_posx, 25, u_temp, 'robotoBlack18', 'white')

    # Wind 
    iw.text(405, 5, weather['wind']['dir'], 'robotoRegular14', 'black')
    iw.text(375, 31, str(weather['wind']['speed'])+u_speed, 'robotoRegular14', 'black')

    # Rain
    iw.text(465, 31, "1hr: "+str(weather['rain']['1h']), 'robotoRegular14', 'black')
    iw.text(465, 46, "3hr: "+str(weather['rain']['3h']), 'robotoRegular14', 'black')

    # Snow
    iw.text(553, 31, "1hr: "+str(weather['snow']['1h']), 'robotoRegular14', 'black')
    iw.text(553, 46, "3hr: "+str(weather['snow']['3h']), 'robotoRegular14', 'black')

    # Write to screen
    # =========================================================================
    iw.display(rotation)

if __name__ == '__main__':
    main()
