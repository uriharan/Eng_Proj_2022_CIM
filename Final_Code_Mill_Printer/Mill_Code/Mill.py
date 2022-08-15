# this file activates the milling machine
import pyautogui
import time
import sys
import os
import ctypes


# locations of buttons

DELAY_OPEN = 1
DELAY_SEARCHBAR = 1
DELAY_VERIFY = 1
DELAY_VERIFY2 = 1
DELAY_VICE = 1
DELAY_CLOSEWINDOW = 20
DELAY_RUN = 0.4
VERIFY = True


def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

path = sys.argv[1]
if len(sys.argv)>2:
    for i in range(2,len(sys.argv)):
        path += " " + sys.argv[i]

if __name__ == "__main__":
    # code of running gcode verification
    time.sleep(3)
    # click with (varying) delay on FILE, OPEN, SEARCHBAR
    pyautogui.keyDown('ctrl')
    pyautogui.press('o')
    pyautogui.keyUp('ctrl')

    time.sleep(DELAY_OPEN)
    # enter file name, from arguments
    pyautogui.typewrite(os.path.basename(path))
    pyautogui.press('enter')
    time.sleep(DELAY_SEARCHBAR)
    if VERIFY:
        # click with (varying) delay on VERIFY1, VERIFY2, OK
        pyautogui.press('f6')
        time.sleep(DELAY_VERIFY)
        pyautogui.press('enter')
        time.sleep(DELAY_VERIFY2)
        pyautogui.press('f5')

        # code for confirmation
        # wait for 'Y' key to be pressed - if pressed continue, if other key is pressed terminate
        programstop = False
        while not programstop:
            if pyautogui.locateOnScreen("ProgramStop.PNG")!=None:
                programstop=True
            else:
                time.sleep(0.5)
        retval = Mbox(u'Milling Confirmation', u'Confirm Milling', 1 + 32 + 256 + 4096)
        # 1 - OK/Cancel, 32 - ? symbol, 256 - default Cancel, 4096 - window on top
        if retval != 1:  # button pressed is not OK
            pyautogui.press('enter')
            exit()

        pyautogui.press('enter')

    # code for activating the milling machine
    pyautogui.click(pyautogui.center(pyautogui.locateOnScreen("Vise.PNG")))
    time.sleep(DELAY_VICE)
    pyautogui.click(pyautogui.center(pyautogui.locateOnScreen("Close.PNG")))
    time.sleep(DELAY_CLOSEWINDOW)
    pyautogui.press('f5')
    time.sleep(DELAY_RUN)
    pyautogui.press('enter')
    pyautogui.press('enter')
    pyautogui.press('enter')
