# this file activates the milling machine
import pyautogui
import time
import sys
import os
import ctypes



DELAY_LOAD = 10
DELAY_OPEN = 1
DELAY_SEARCHBAR = 2


def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


path = sys.argv[1]
if len(sys.argv)>2:
    for i in range(2,len(sys.argv)):
        path += " " + sys.argv[i]

if __name__ == "__main__":
    # code of running gcode verification
    time.sleep(DELAY_LOAD)
    # click with (varying) delay on FILE, OPEN, SEARCHBAR
    pyautogui.keyDown('ctrl')
    pyautogui.press('d')
    pyautogui.press('o')
    pyautogui.keyUp('ctrl')

    time.sleep(DELAY_OPEN)
    # enter file name, from arguments
    pyautogui.typewrite(os.path.basename(path))
    pyautogui.press('enter')
    time.sleep(DELAY_SEARCHBAR)
    # click on Prepare
    pyautogui.click(pyautogui.center(pyautogui.locateOnScreen("Prepare.PNG")))


    # code for confirmation
    # wait for 'Y' key to be pressed - if pressed continue, if other key is pressed terminate
    ready = False
    while not ready:
        if pyautogui.locateOnScreen("Print.PNG")!=None:
            ready=True
        else:
            time.sleep(0.5)

    pyautogui.click(pyautogui.center(pyautogui.locateOnScreen("Print.PNG")))

