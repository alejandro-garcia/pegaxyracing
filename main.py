import cv2 as cv2
import numpy
import pyautogui
import mss
import time
from os import listdir, remove
import colorama
from colorama import Fore, Back, Style
from datetime import datetime
import sys
import glob
import random

now = datetime.now()

colorama.init()

horseName = ""
countRace = 0


logo0 = """
 _______   _______   _______   _______   _    _   _    _
|  ___  | |  _____| |  _____| |  ___  | \ \  / / \ \  / /
| |___| | | |____   | | ____  | |   | |  \ \/ /   \ \/ /
|  _____| |  ____|  | ||__  | | |___| |   >  <     \  /
| |       | |_____  | |___| | |  ___  |  / /\ \    / /
|_|       |_______| |_______| |_|   |_| /_/  \_\  /_/        

"""


logo1 = """
           _                     _          
          |_)  _.  _ o ._   _   |_)  _ _|_  
          | \ (_| (_ | | | (_|  |_) (_) |_
                            _|         
"""


logo2 = """
            /\                       /\                         
            \ \                     / /
          __/_/,,;;;`;       ;';;;,,\_\__        
       ,~(  )  , )~~\|       |/~~( ,  (  )~;
       ' / / --`--,             .--'-- \ \ `
        /  \    | '             ` |    /  \      
"""

logo3 = """
        #####################################
        #            Opensource             #
        #####################################   
"""

logo4 = """
        #####################################
        #    Press CTRL + C to stop bot     #
        #####################################   
"""

print(Fore.MAGENTA + logo0 + Style.RESET_ALL)

print(Fore.CYAN + logo1 + Style.RESET_ALL)

print(Fore.YELLOW + logo2 + Style.RESET_ALL)

print(logo3)
print(Fore.RED + logo4 + Style.RESET_ALL)
print('Starting pegaxy racing bot...')
print('\n')
time.sleep(3)

"""
to get window name:

window = pygetwindow.getWindowsWithTitle('Pegaxy')[0]
print(window)

"""

active_window_name = None
if sys.platform in ['linux', 'linux2']:
    pass
    # import gi
    # gi.require_version('Wnck', '3.0')
    # from gi.repository import Gtk, Wnck
    # Gtk.init([])  # necessary if not using a Gtk.main() loop
    # screen = Wnck.Screen.get_default()
    # screen.force_update()  # recommended per Wnck documentation
    # active_window = screen.get_active_window()
    # pid = active_window.get_pid()
    # with open("/proc/{pid}/cmdline".format(pid=pid)) as f:
    #     active_window_name = f.read()
    # print("Active window: %s" % str(active_window_name))
elif sys.platform in ['Windows', 'win32', 'cygwin']:
    import pygetwindow
    window = pygetwindow.getWindowsWithTitle('Pegaxy - Mozilla Firefox')[0]
    time.sleep(2)
    window.maximize()
    time.sleep(3)


def print_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = numpy.array(sct.grab(monitor))        
                
        # Grab the data
        return sct_img[:, :, :3]

def locate_coordinates(img, threshold=0.8):
    print = print_screen()
    result = cv2.matchTemplate(print, img, cv2.TM_CCOEFF_NORMED)
    w = img.shape[1]
    h = img.shape[0]

    yloc, xloc = numpy.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles
    

def move_cursor(x, y, t):
    pyautogui.moveTo(x, y, t, pyautogui.easeInOutQuad)
    
def load_screenshots(dir_path='./screenshots/'):

    file_names = listdir(dir_path)
    targets = {}
    for file in file_names:
        path = 'screenshots/' + file
        targets[file.removesuffix('.png')] = cv2.imread(path)

    return targets


def already_race_menu():
    print('verifying racing menu...')
    matches = locate_coordinates(images['racing_menu_on'])
    result = len(matches[0]) > 0
    if result:
        if not do_click(images['next_match']):
            print('you are already in race menu')
    return result


def validate_image_present(img):
    matches = locate_coordinates(images[img], 0.8)
    return len(matches[0]) > 0

def do_click(img, timeout=3, threshold=0.8, maxrecursion=1, randomx=False):
    tryes_count = 0
    
    def inner_do_click():
        start = time.time()
        has_timed_out = False
        while(not has_timed_out):
            matches = locate_coordinates(img, threshold)

            if(len(matches[0]) == 0):
                has_timed_out = time.time()-start > timeout
                continue

            x, y, w, h = matches[0][0]
            pos_x = x + w / 2
            if randomx:
                seed_value = random.randint(1,15)
                print(f'seed increment: {seed_value}')
                pos_x += seed_value

            pos_y = y + h / 2
            print(f'template match found... coordinates: x=>{pos_x}, y=>{pos_y}')
            move_cursor(pos_x, pos_y, 1)

            if maxrecursion != 1:
                pyautogui.click(clicks=2,interval=0.7)
                pos_x, pos_y = pyautogui.position()
                pos_y -= 50
                move_cursor(pos_x, pos_y, 1)
            else:
                pyautogui.click(clicks=2)

            return True

        return False
       
    wasClicked = False
    
    while  wasClicked == False and tryes_count < maxrecursion:
        tryes_count += 1
        if tryes_count > 1:
            time.sleep(1)
        wasClicked = inner_do_click()

    if maxrecursion != 1 and wasClicked == False:
        print('Max tries was reached without any matches!')

    return wasClicked    
         
    
def workbot():

    global images
    images = load_screenshots()


    while True:
        print('Pressing start...')

        if not do_click(images['start3'],maxrecursion=5, randomx=True):
            #do_click(images['start2'],maxrecursion=5)
            print('Cannot find start button...')
            pyautogui.hotkey('ctrl', 'f5')
            time.sleep(3)
            break

        elif (do_click(images['empty_energy'], 0.7)):

            print(Fore.RED + f'{horseName} horse without energy...' + Style.RESET_ALL)

            #print('Refreshing page...')
            #pyautogui.hotkey('ctrl', 'f5')
            time.sleep(3)
            break
        else:

            
            while True:
                print('Waiting metamask sign...')
                do_click(images['sign_firefox'], 30)
                time.sleep(5)
                if (do_click(images['find_another'],randomx=True)):
                    print(Fore.YELLOW + 'Fail to start race, searching for another...' + Style.RESET_ALL)
                elif validate_image_present('reload'):
                    if (do_click(images['lobby'])):
                        print(Fore.YELLOW + 'Fail to start race, searching for another...' + Style.RESET_ALL)
                    else:
                        print('Join to race Error')
                        print('Refreshing page...')
                        pyautogui.hotkey('ctrl', 'f5')                        
                elif validate_image_present('joining'):
                    print(Fore.YELLOW + 'Fail to start race, searching for another...' + Style.RESET_ALL)
                elif validate_image_present('sign_firefox'):
                    print(Fore.YELLOW + 'Fail to start race, metamask sign button still present...' + Style.RESET_ALL)
                else:
                    print('Starting race...') 
                    global countRace
                    countRace = countRace + 1
                    print(Fore.GREEN + f'{horseName} horse running the race number {countRace}, please wait...' + Style.RESET_ALL)
                    time.sleep(100)
                    if do_click(images['next_match'], 300,randomx=True):                        
                      print('Next race...')
                      break
                    elif do_click(images['cancel'], 300):
                      print('Join to race Error')
                      print('Refreshing page...')
                      pyautogui.hotkey('ctrl', 'f5')
                      time.sleep(5)
                      break
            
        
    time.sleep(3)

print('Clenaup old capture files...')    
try:
    for f in glob.glob('Capture*.png'):
        remove(f)
except Exception as e:
    print(f'Error when delete files: {str(e)}')


print('loading screenshots...')    
images = load_screenshots()
 
if not already_race_menu():
  print('Acessing racing menu...')
  do_click(images['racing_menu'])

print('Picking the pegaxy...')
do_click(images['pick_a_pega'])
time.sleep(2)
print("\nCounting horses, please wait...")


# Takes a screen shot and saves the file in the specified location
loc1 = (r'Capture.png')
pyautogui.screenshot(loc1)

# Reads the screen shot and loads the image it will be compared too
img_rgb = cv2.imread(loc1)
count = 0

# Reads the file
template_file_ore = r"horse.png"
template_ore = cv2.imread(template_file_ore)
w, h = template_ore.shape[:-1]

# Compares screen shot to given image, gives error thresh hold
res = cv2.matchTemplate(img_rgb, template_ore, cv2.TM_CCOEFF_NORMED)
threshold = 0.8
loc = numpy.where(res >= threshold)


# Puts red box around matched images and counts horses
for pt in zip(*loc[::-1]):
    loc1 = (r'Capture.png')
    pyautogui.screenshot(loc1)

 # Reads the file
    template_file_ore = r"horse.png"
    template_ore = cv2.imread(template_file_ore)
    w, h = template_ore.shape[:-1]

 # Compares screen shot to given image, gives error thresh hold
    res = cv2.matchTemplate(img_rgb, template_ore, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = numpy.where(res >= threshold)

  # Reads the screen shot and loads the image it will be compared too
    img_rgb = cv2.imread(loc1)
    cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
    count += 1  

    #if count > 0:            
    print(f"Horse {count} found.")


horses = locate_coordinates(template_ore)

if count == 0:
    print('You not have horses')
    sys.exit()

#del(horses[0])

print('*** begin: horses ***')
print(horses)
print('*** end: horses ***')

if count >= 1:
    horse1X = horses[0][0][0]
    horse1Y = horses[0][0][1]

if count >= 2:
    horse2X = horses[0][1][0]
    horse2Y = horses[0][1][1]

if count >= 3:
    horse3X = horses[0][2][0]
    horse3Y = horses[0][2][1]


while True:
    #pyautogui.hotkey('ctrl', 'f5')
    if count >= 1:
        horseName= "First"
        print(f"Clicking {horseName} horse")
        time.sleep(3)
        pyautogui.click(horse1X, horse1Y)
        time.sleep(3)
        workbot()

    if count >= 2:
        horseName= "Second"
        print(f"Clicking {horseName} horse")
        time.sleep(3)
        pyautogui.click(horse2X, horse2Y)
        time.sleep(3)
        workbot()

    if count == 3:
        horseName= "Third"
        print(f"Clicking {horseName} horse")
        time.sleep(3)       
        pyautogui.click(horse3X,  horse3Y)
        time.sleep(3)
        workbot()
    
    sleepMinutes = 60
    sleepScript = sleepMinutes*60
    nowHour = now.strftime("%H:%M:%S")
    nowDate = now.strftime("%d/%m/%Y")
    nowString = nowHour + " - " + nowDate
    print(Back.CYAN + Fore.RED + f'Sleeping {sleepMinutes} minutes after {countRace} race(s).  {nowString}' + Style.RESET_ALL)
    time.sleep(sleepScript)
    pyautogui.hotkey('ctrl', 'f5')
    
