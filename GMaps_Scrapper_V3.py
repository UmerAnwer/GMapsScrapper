# Author: Harish Mohan <harishprofile001@gmail.com>
# Name: GMaps Scrapper
# Version: 3.0
# Description: Scraps data(name, category, address, geocode) from google maps

from splinter import Browser
from easygui import *
from sys import exit
from time import sleep
from re import sub
from os import path, makedirs


# Recursive function that does the actual scrapping
# @rtype: None


def recursive_scrapper():
    if chrome.is_element_present_by_xpath(
            "//div[contains(@class,'widget-pane-section-listbox widget-pane-section-scrollbox "
            "widget-pane-scrollable')]"):
        div_count = len(chrome.find_by_xpath("//div[contains(@jsaction, 'pane.resultSection.click;"
                                             "keydown:pane.resultSection.keydown;mouseover:pane.resultSection.in;"
                                             "mouseout:pane.resultSection.out;focus:pane.resultSection.focusin;"
                                             "blur:pane.resultSection.focusout')]"))
        for count in range(0, div_count):
            # noinspection PyBroadException
            try:
                chrome.find_by_xpath("//div[contains(@jsaction, 'pane.resultSection.click;"
                                     "keydown:pane.resultSection.keydown;mouseover:pane.resultSection.in;"
                                     "mouseout:pane.resultSection.out;focus:pane.resultSection.focusin;"
                                     "blur:pane.resultSection.focusout')]")[count].click()
                sleep(2)
                name = chrome.find_by_id("widget-pane-section-header-title").text
                print name
                address = chrome.find_by_xpath("//div[contains(@class, 'widget-pane-section-info')]")[0].text
                category = chrome.find_by_xpath("//a[contains(@jsaction, 'pane.rating.category')]").text
                geocode_url = chrome.url.split("@")
                geocode_arr = geocode_url[1].split(",")
                lat = geocode_arr[0]
                lng = geocode_arr[1]
                file_handler.write(name.strip().encode("UTF-8") + "\t" + category.strip().encode(
                    "UTF-8") + "\t" + address.strip().encode("UTF-8") + "\t" + str(lat) + "\t" + str(lng) + "\n")
                chrome.find_by_xpath("//a[contains(@class, 'widget-pane-section-back-to-list-link noprint')]").click()
            except:
                continue
        next_button = chrome.find_by_xpath('//button[@jsaction="pane.paginationSection.nextPage"]') \
            if chrome.is_element_present_by_xpath('//button[@jsaction="pane.paginationSection.nextPage"]') \
            else {"disabled": "false"}
        if next_button["disabled"] == "true":
            file_handler.close()
        else:
            # noinspection PyBroadException
            try:
                next_button.click()
                sleep(3)
                while 1:
                    if chrome.is_element_present_by_xpath(
                            "//button[contains(@class, "
                            "'widget-zoom-button widget-zoom-in widget-zoom-button-disabled')]"):
                        break
                    chrome.find_by_xpath("//button[contains(@class, 'widget-zoom-button widget-zoom-in')]").click()
                recursive_scrapper()
            except:
                file_handler.close()
    else:
        print "No data Available"
        file_handler.close()


# GUI creation
msg = "Enter required * information"
title = "BI GMaps Scrapper"
fieldNames = ["Folder Name * (Enter City Name)",
              "Lifestyle Indicator Name *",
              "Places * (Separate each place with a ('$') dollar)"]
fieldValues = multenterbox(msg, title, fieldNames)
while 1:  # make sure that none of the fields was left blank
    if fieldValues is None:
        break
    errmsg = ""
    for i in range(len(fieldNames)):
        if fieldValues[i].strip() == "":
            errmsg += '"%s" is a required field.\n\n' % fieldNames[i]
    if errmsg == "":  # if no problems found
        break
    fieldValues = multenterbox(errmsg, title, fieldNames, fieldValues)

if fieldValues is None:
    exit(0)

# Processing input and sending it to the scrapper function
folder_name = "XLS\\" + fieldValues[0].lower()
lifestyle_indicator = sub(r"\s+", '+', fieldValues[1].lower())
places = fieldValues[2]
print "Connecting To Google Maps..."
places_arr = places.split("$")
chrome = Browser("chrome")
for place in places_arr:
    place = sub(r"\s+", '+', place)
    chrome.visit("https://www.google.co.in/maps/search/" + lifestyle_indicator.strip() + "+in+" + place.strip() +
                 "/@13.0318799,80.1985061,21z")
    sleep(3)
    if not path.exists(folder_name):
        makedirs(folder_name)
    if not path.exists(folder_name + "/" + lifestyle_indicator):
        makedirs(folder_name + "/" + lifestyle_indicator)
    file_handler = open(folder_name + "/" + lifestyle_indicator + "/" + place.strip() + "_" +
                        lifestyle_indicator.strip() + ".xls", "w")
    file_handler.write("Name\tCategory\tAddress\tLatitude\tLongitude\n")
    recursive_scrapper()

print "Successfully Scrapped All Available Data!"
print "Disconnecting Google Maps..."
chrome.quit()
