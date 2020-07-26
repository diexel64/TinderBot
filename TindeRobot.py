Python 3.8
## by Diexel64

import os, wx, sys, time, random, getpass
from datetime import timedelta
from tabulate import tabulate
from datetime import datetime
from time import sleep, strftime, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from db import get_from_mongo, query_date, query_user, query_word, add_to_mongo

baseFolder = os.path.dirname(os.path.abspath("__file__"))
user = getpass.getuser()

LIKE_BUTTON_XPATH = '//*[@id="content"]/div/div[1]/div/main/div[1]/div/div/div[1]/div/div[2]/div[4]/button'
DISLIKE_BUTTON_XPATH = '//*[@id="content"]/div/div[1]/div/main/div[1]/div/div/div[1]/div/div[2]/div[2]/button'
NAME = '/html/body/div[1]/div/div[1]/div/main/div[1]/div/div/div[1]/div/div[1]/div[3]/div[6]/div/div[1]/div/div/span'
AGE = '/html/body/div[1]/div/div[1]/div/main/div[1]/div/div/div[1]/div/div[1]/div[3]/div[6]/div/div[1]/div/span'
DESCRIPTION = '/html/body/div[1]/div/div[1]/div/main/div[1]/div/div/div[1]/div/div[1]/div[3]/div[6]/div/div[2]/div/div/span[1]'
IMAGE = '/html/body/div[1]/div/div[1]/div/main/div[1]/div/div/div[1]/div/div[1]/div[3]/div[1]/div[1]/div/div[1]/div/div'


def scale_bitmap(bitmap, width, height):
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.BitmapFromImage(image)
        return result


class TinderBot:
    """ Tinder bot class with all the methods"""
    def __init__(self, mins):
        """Method to initialize chrome webdriver with settings"""
        chrome_options = Options()

        # This will create a new profile in your chrome browser
        chrome_options.add_argument(
            f"--user-data-dir=C:\\Users\\{user}\\AppData\\Local\\Google Selenium\\Chrome\\User Data"
        )
        chrome_options.add_argument(
            "--profile-directory=Default"
        )

        # Changing the user agent so that tinder.com doesn't know
        # that this is an automated script running using selenium
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.'
            '4044.113 Safari/537.36'
        )
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])

        self.driver = webdriver.Chrome(
            executable_path=baseFolder + "\\chromedriver.exe",          # Path to chrome driver
            chrome_options=chrome_options
        )
        self.mins = mins

    def start(self):
        """Method to start the bot"""
        self.driver.get('https://tinder.com')
        sleep(5)

    def swipe_right(self):
        """Method to swipe right on the current profile"""
        btn_like = self.driver.find_element_by_xpath(LIKE_BUTTON_XPATH)
        btn_like.click()

    def swipe_left(self):
        """Method to swipe left of the current profile"""
        btn_dislike = self.driver.find_element_by_xpath(DISLIKE_BUTTON_XPATH)
        btn_dislike.click()

    def get_data(self):
        """Method to get the name and description of the current profile"""
        PersonName = self.driver.find_element_by_xpath(NAME).text
        Age = self.driver.find_element_by_xpath(AGE).text
        if Age == '':
            Age = 0
        image = self.driver.find_element_by_xpath(IMAGE).get_attribute('style')
        try:
            PersonDescription = self.driver.find_element_by_xpath(DESCRIPTION).text
        except:
            PersonDescription = 'No Description'
        data = {
            'name': PersonName,
            'age': int(Age),
            'description': PersonDescription,
            'image': image.split('"')[1],
            'date': datetime.now()
        }
        return data

    def check_conditions(self, badwords, goodwords):            # False = LEFT ; True = RIGHT
        """Method to check if defined words exist in description of the profile and decide where to swipe"""
        data = self.get_data()
        badword = goodword = False
        for x in badwords:
            if x.lower() in data['description'].lower():
                badword = True 
        for x in goodwords:
            if x.lower() in data['description'].lower():
                goodword = True 
        if badword == True:
            return 'left'
        if goodword == True:
            return 'right'
        else:
            return 'probability'

    def rand_sleep(self):
        """
        Method to sleep randomly between 1 to 3 seconds (float)
        This randomness prevents our bot from getting detected by tinder
        :return:
        """
        sleep_sec = random.uniform(1, 3)
        print('Sleeping for {} seconds'.format(str(round(sleep_sec, 2))))
        sleep(sleep_sec)

    def auto_swipe(self, badwords, goodwords):
        """Method to start swiping"""
        likes, dislikes = 0, 0  # Count of swipes
        endTime = datetime.now() + timedelta(minutes= self.mins)
        while True:
            if datetime.now() >= endTime:
                print('Swiped for {} minutes !'.format(str(self.mins)))
                break
            self.rand_sleep()
            try:
                data = self.get_data()
                print(data)
                decision = self.check_conditions(badwords, goodwords)
                if decision == 'right':
                    self.swipe_right()
                    likes += 1
                    print('Swiped Right because of a good word, Count {}'.format(likes))
                    add_to_mongo('RIGHT', data)
                if decision == 'left':
                    self.swipe_left()
                    dislikes += 1
                    print('Swiped Left because of a bad word, Count {}'.format(dislikes))
                    add_to_mongo('LEFT', data)
                if decision == 'probability':
                    rand = random.random()
                    if rand < .78:  # Probability of swiping right on a profile
                        self.swipe_right()
                        likes += 1
                        print('Swiped Right, Count {}'.format(likes))
                        add_to_mongo('RIGHT', data)
                    else:
                        self.swipe_left()
                        dislikes += 1
                        print('Swiped Left, Count {}'.format(dislikes))
                        add_to_mongo('LEFT', data)

            except ElementClickInterceptedException as e:
                # Handling if any unexpected popup occurs on screen
                webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                sleep(5)
            except Exception as e:
                print(str(e))
                return -1


class Global(wx.Frame):
    def __init__(self, parent, title): 
        super(Global, self).__init__(parent, title=title, size=(900, 500))
        self.InitUI()
        self.Centre()
        self.SetTitle("Tinder Robot")
        try:
            icon = wx.EmptyIcon()
            icon.CopyFromBitmap(wx.Bitmap("img\\logo.ico", wx.BITMAP_TYPE_ANY))
            self.SetIcon(icon)
        except Exception as e:
            print("The favicon was not found, please save the favicon in the img directory as icon.png")
         
    def InitUI(self):    
        nb = wx.Notebook(self) 
        nb.AddPage(Panel1(nb), "Commands")
        nb.AddPage(Panel2(nb), "Data")
        self.Show(True) 


class Panel1(wx.Panel):
    def __init__(self, parent): 

        super(Panel1, self).__init__(parent)
        sizer = wx.GridBagSizer(5, 5)

        # Entête
        try:
            imageFile = "img\\logo.jpg"
            png = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            png = scale_bitmap(png, 200, 80)
            logo = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
            sizer.Add(logo, pos=(0, 0), span=(1, 10), flag=wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER, border=10)
        except Exception as e:
            print("The logo file was not found, please save the logo file in the img directory as logo.png")

        ligne = wx.StaticLine(self)
        sizer.Add(ligne, pos=(1, 0), span=(1, 10), flag=wx.EXPAND | wx.BOTTOM | wx.LEFT, border=10)

        # Inputs
        lbl3 = wx.StaticText(self, label="Console:", style=wx.ALIGN_LEFT)
        sizer.Add(lbl3, pos=(2, 4), flag=wx.LEFT | wx.RIGHT, border=15)

        self.ResultBox = wx.TextCtrl(self, style=wx.TE_READONLY|wx.TE_MULTILINE)
        sizer.Add(self.ResultBox, pos=(3, 4), span=(7, 7), flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=15)

        # Buttons
        minutes = ['1', '3', '5', '10', '15', '20', '30', '45', '60', '120', '300', '600']
        lbl_minutes = wx.StaticText(self, label="Executions lasts (min): ", style=wx.ALIGN_LEFT)
        sizer.Add(lbl_minutes, pos=(5, 1), flag=wx.LEFT | wx.RIGHT, border=15)
        self.minutes = wx.ComboBox(self, choices=minutes, value='10')
        sizer.Add(self.minutes, pos=(5, 2), flag=wx.ALIGN_LEFT, border=15)

        lbl_badwords = wx.StaticText(self, label="Bad words : ", style=wx.ALIGN_LEFT)
        sizer.Add(lbl_badwords, pos=(3, 1), flag=wx.LEFT | wx.RIGHT, border=15)
        self.badwords = wx.TextCtrl(self, value='mom')
        sizer.Add(self.badwords, pos=(3, 2), flag=wx.ALIGN_LEFT, border=15)

        lbl_goodwords = wx.StaticText(self, label="Good words : ", style=wx.ALIGN_LEFT)
        sizer.Add(lbl_goodwords, pos=(4, 1), flag=wx.LEFT | wx.RIGHT, border=15)
        self.goodwords = wx.TextCtrl(self, value='model, adventurous')
        sizer.Add(self.goodwords, pos=(4, 2), flag=wx.ALIGN_LEFT, border=15)

        btn_TXT = wx.Button(self, label="Generate .txt")
        sizer.Add(btn_TXT, pos=(9, 2), flag=wx.RIGHT | wx.TOP | wx.BOTTOM, border=5)
        self.Bind(wx.EVT_BUTTON, self.onTxt, btn_TXT)

        btn_GO = wx.Button(self, label="Launch")
        sizer.Add(btn_GO, pos=(8, 2), flag=wx.RIGHT, border=15)
        self.Bind(wx.EVT_BUTTON, self.onLaunch, btn_GO)

        try:
            tinderImageFile = "img\\tinder.png"
            png = wx.Image(tinderImageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            png = scale_bitmap(png, 80, 80)
            logo = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
            sizer.Add(logo, pos=(7, 0), span=(3, 2), flag=wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER, border=10)
        except Exception as e:
            print("The logo file was not found, please save the logo file in the img directory as tinder.png")


        # Footer
        line = wx.StaticLine(self)
        sizer.Add(line, pos=(11, 0), span=(1, 10), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
        titre = wx.StaticText(self, label="© 2020 - alber.py")
        font = wx.Font(7, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        titre.SetFont(font)
        sizer.Add(titre, pos=(12, 0), span=(1, 10), flag=wx.BOTTOM | wx.ALIGN_CENTER | wx.TOP, border=5)

        sizer.AddGrowableCol(8, 0)
        sizer.AddGrowableRow(10, 0)
        self.SetSizer(sizer)
        sizer.Fit(self)
        sys.stdout = self.ResultBox

    def getList(self, lst):
        if lst == '':
            lst = []
        else:
            lst = lst.replace(',', ' ').replace(';', ' ').replace('  ', ' ').split(' ')
        return lst

    def onLaunch(self, event):
        mins = int(self.minutes.GetValue())
        badwords = self.badwords.GetValue()
        goodwords = self.goodwords.GetValue()
        badwords = self.getList(badwords)
        goodwords = self.getList(goodwords)        
        tinder = TinderBot(mins)
        tinder.start()
        tinder.auto_swipe(badwords, goodwords)

    def onTxt(self, event):
        log = self.ResultBox.GetValue()
        if not os.path.exists(baseFolder + "\\Logs"):
                os.makedirs(baseFolder + "\\Logs\\")
        f = open(baseFolder + "\\Logs\\" + time.strftime("%Y%m%d-%H%M%S") + "_Log.txt", "w")
        f.write(log)
        f.close()


class Panel2(wx.Panel):

    def __init__(self, parent): 

        super(Panel2, self).__init__(parent)
        sizer = wx.GridBagSizer(5, 5)

        # Entête
        try:
            imageFile = "img\\logo.jpg"
            png = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            png = scale_bitmap(png, 200, 80)
            logo = wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
            sizer.Add(logo, pos=(0, 0), span=(1, 10), flag=wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER, border=10)
        except Exception as e:
            print("The logo file was not found, please save the logo file in the img directory as logo.png")

        ligne = wx.StaticLine(self)
        sizer.Add(ligne, pos=(1, 0), span=(1, 10), flag=wx.EXPAND | wx.BOTTOM | wx.LEFT, border=10)

        ## Inputs
        lblList = ['RIGHT', 'LEFT']
        self.rbox_collections = wx.RadioBox(self, label = 'Search in collection : ', choices=lblList, majorDimension = 1, style = wx.RA_SPECIFY_ROWS)
        sizer.Add(self.rbox_collections, pos=(2, 6), span=(2, 1), flag=wx.EXPAND|wx.BOTTOM|wx.RIGHT, border=20)

        lbl_user = wx.StaticText(self, label="Search for name : ")
        sizer.Add(lbl_user, pos=(2, 0), span=(1, 2), flag=wx.LEFT, border=15)

        self.user = wx.TextCtrl(self, value="")
        sizer.Add(self.user, pos=(3, 0), span=(1, 2), flag=wx.LEFT, border=15)

        lbl_date = wx.StaticText(self, label="Search for date")
        sizer.Add(lbl_date, pos=(2, 2), span=(1, 2), flag=wx.LEFT, border=15)

        self.date = wx.TextCtrl(self, value="")
        sizer.Add(self.date, pos=(3, 2), span=(1, 2), flag=wx.LEFT, border=15)

        lbl_word = wx.StaticText(self, label="Word in description : ")
        sizer.Add(lbl_word, pos=(2, 4), span=(1, 2), flag=wx.LEFT | wx.RIGHT, border=15)

        self.word = wx.TextCtrl(self, value="")
        sizer.Add(self.word, pos=(3, 4), span=(1, 2), flag=wx.LEFT, border=15)

        self.ResultBox = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE)
        sizer.Add(self.ResultBox, pos=(4, 0), span=(4, 10), flag=wx.RIGHT | wx.LEFT | wx.BOTTOM | wx.EXPAND, border=15)

    ## Buttons

        btn_find = wx.Button(self, label="Search")
        sizer.Add(btn_find, pos=(3, 8), flag=wx.LEFT, border=15)
        self.Bind(wx.EVT_BUTTON, self.onGet2, btn_find) 

        btn_CSV = wx.Button(self, label="Generate CSV")
        sizer.Add(btn_CSV, pos=(3, 9), flag=wx.LEFT, border=15)
        self.Bind(wx.EVT_BUTTON, self.onCSV, btn_CSV)

        # Footer
        line = wx.StaticLine(self)
        sizer.Add(line, pos=(9, 0), span=(1, 10), flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
        titre = wx.StaticText(self, label="© 2020 - alber.py")
        font = wx.Font(7, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        titre.SetFont(font)
        sizer.Add(titre, pos=(10, 0), span=(1, 10), flag=wx.BOTTOM | wx.ALIGN_CENTER | wx.TOP, border=5)

        sizer.AddGrowableCol(9, 0)
        sizer.AddGrowableRow(7, 0)
        self.SetSizer(sizer)
        sizer.Fit(self)
        
    def onGet(self, event):
        col = self.rbox_collections.GetStringSelection().upper()
        result, nb = get_from_mongo(col)
        result_tab = tabulate(result, headers='keys', showindex=False)
        self.ResultBox.SetValue('There are {0} entries ! \n\rHere is the list : \n\r {1}'.format(nb, result_tab))

    def onGet2(self, event):
        col = self.rbox_collections.GetStringSelection().upper()
        username = self.user.GetValue()
        date = self.date.GetValue()
        word = self.word.GetValue()
        result = ''
        if username != '':
            result = query_user(col, username)
            result_tab = tabulate(result, headers='keys', showindex=False)
            self.ResultBox.SetValue(result_tab)
        if date != '':
            result, nb = query_date(col, date)
            result_tab = tabulate(result, headers='keys', showindex=False)
            self.ResultBox.SetValue('There are {0} entries ! \n\r {1}'.format(nb, result_tab))
        if word != '':
            result, nb = query_word(col, word)
            result_tab = tabulate(result, headers='keys', showindex=False)
            self.ResultBox.SetValue('There are {0} entries ! \n\r {1}'.format(nb, result_tab))
        else:
            self.onGet(event)
        return result

    def onCSV(self, event):
        result = self.onGet2(event)
        if not os.path.exists(baseFolder + "\\Extractions"):
                os.makedirs(baseFolder + "\\Extractions\\")
        result.to_csv(baseFolder + "\\Extractions\\ " + strftime("%Y%m%d-%H%M%S") + "_Extract.csv")


def main():
    app = wx.App()
    Global(None, 'Robot').Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
