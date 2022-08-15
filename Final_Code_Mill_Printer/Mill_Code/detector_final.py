import time
import logging
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

"""ToDo:
1. Check to Ensure .stl files/Gcode files are formatted correctly



"""

"""CONTENT is a Variable which is Milling or 3Dprinter, and controls
 which side of the code is called when detecting a new file - a Gcode file to 
 send to the milling machine, to verify, and to run, or a .stl file to
 send to cura, translate to gcode, and forward to the 3Dprinter. each section of
 the code is intended to run on the computer connected to the corresponding machine
"""

CONTENT = "3Dprinter"
PATH = r'.\py\Observe'
# toDo: actual folder location fo MILL
PRINTPATH = "C:"+"\\"+"toPrint"
MILLPATH = r"\\MILL-CIM\Users\cimlab\Documents\cncFiles"
DELAY = 1  # Delay between reading lines from the waiting list
DELETE_AFTER = True

if CONTENT == "Milling":
    PATH = MILLPATH
if CONTENT == "3Dprinter":
    PATH = PRINTPATH


class ActivationEventHandler(FileSystemEventHandler):
    """Logs all the events captured."""

    def __init__(self, filename):
        super(ActivationEventHandler, self).__init__()
        self.f = filename

    def on_created(self, event):
        super(ActivationEventHandler, self).on_created(event)

        # This part appends new items to the waiting list
        print("Detected: " + event.src_path)
        self.f.write("0"+event.src_path+"\n")
        self.f.flush()

    def on_moved(self, event):
        super(ActivationEventHandler, self).on_moved(event)

    def on_deleted(self, event):
        super(ActivationEventHandler, self).on_deleted(event)

    def on_modified(self, event):
        super(ActivationEventHandler, self).on_modified(event)



# reads a line from file <file> without moving the file pointer
def peek_line(file):
    pos = file.tell()
    line = file.readline()
    file.seek(pos)
    return line


# rewrites a part of the file <file> to be the string <s>, starting from position <pos>.
def overwrite(file, s, pos):
    file.seek(pos)
    file.write(s)
    file.seek(pos)
    file.flush()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = PATH

    # opening the waiting list file:
    # if an old one exists, copy the data because opening in write mode causes deletion of the old file.
    data = ""
    if os.path.exists("WaitingList.txt"):
        f = open("WaitingList.txt", "r")
        data = f.read()
        f.close()
    f = open("WaitingList.txt", "w+")
    overwrite(f, data, f.tell())
    f.flush()

    # opening the file for completion updates (Note: it is reset every time this program is activated.)
    f2 = open("CompletedList.txt", "w+")

    # create watchdog observer
    f_append = open("WaitingList.txt", "a")
    event_handler = ActivationEventHandler(f_append)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    # run on waiting list
    CurrentLine = ""
    print("Detector Activated")
    try:
        while True:
            CurrentLine = peek_line(f)
            if len(CurrentLine) > 0:
                if CurrentLine[0] == '0':  # Next item is in 'Waiting' Mode (marked by '0').
                    print("Activating: "+CurrentLine[1:-1])
                    # Set item in waiting list to be in 'Active' Mode (marked by '1').
                    overwrite(f, "1", f.tell())

                    # run correct code
                    if CONTENT == "3Dprinter":
                        # run printing code
                        os.system("python Printer.py " + CurrentLine[1:-1])

                    elif CONTENT == "Milling":
                        # run milling code
                        os.system("python Mill.py " + CurrentLine[1:-1])
                    else:
                        # not Mill/3Dprinter - is a Test.
                        print("Test Mode: activation of " + CurrentLine[1:-1])

                if CurrentLine[0] == '1':  # Next item is in 'Active' Mode (marked by '1').
                    # Check Completed List
                    f2.seek(0)
                    loc = 0
                    check = f2.readline()
                    while len(check) > 0:
                        if check == CurrentLine[1:]:
                            # Found Match : Set Item to 'Completed' Mode (marked by '2').
                            overwrite(f, "2", f.tell())
                            # Remove from Completed List (Replace by "000...0" line)
                            overwrite(f2, "0"*(len(check)-1)+"\n", loc)
                            print("Completed: " + CurrentLine[1:-1])
                            break
                        loc = f2.tell()
                        check = f2.readline()
                while CurrentLine[0] == '2':  # Next item is in 'Completed' Mode (marked by '2').
                    # Move to next item on the list until the line starts with:
                    # '0' - 'Waiting'
                    # '1' - 'Active' (This will happen only if the detector was previously closed before completion)
                    # Empty string - There are no more items in the waiting list
                    f.readline()
                    CurrentLine = peek_line(f)
                    if len(CurrentLine) == 0:
                        break
            time.sleep(DELAY)  # Delay for checking the status of the current list item

    except KeyboardInterrupt:
        observer.stop()
    observer.join()

    f_append.close()
    f.close()

    if DELETE_AFTER:
        os.remove("CompletedList.txt")
        os.remove("WaitingList.txt")
