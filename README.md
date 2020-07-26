# TinderBot
A robot coded in python for swiping on tinder

1. Before using

You will need to install a few libraries listed below. To do this, just type pip install {nameofthelibrary}.
- wxPython
- selenium
- pandas
- xlrd
- getpass
- pymongo
- tabulate

2. Use

To use the robot just launch the file "TindeRobot.py". Then, a GUI interface shows with some of the fields already completed. This fields can be modified by the user. 
The first execution will crash because the web browser won't be able to log into the account. Therefore, launch the robot and access to your tinder account on the webdriver so that it gets the session for the next uses.

Select the time the execution should last and click on the "Launch" button.

3. Data

The robot will automatically save the data of users that have been swiped right and left in mongoDB. It is possible to extract this data in the second tab of the GUI.
It is possible to search for specific user names or filter by date or word in description. Finally, a button allows to generate a .csv file for further analysis.

4. Further ideas

- add a chat functionality, making the robot able to read a conversation and respond accordingly
