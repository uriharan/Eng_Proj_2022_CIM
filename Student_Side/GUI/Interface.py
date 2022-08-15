import os.path

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.properties import ObjectProperty

from pathlib import Path

currentfile = ""
location = ""
SHOW_COMPLETED = False

class InputScreen(Screen):
    machine = ObjectProperty()
    path = ObjectProperty()

    global location
    global currentfile

    def connect(self):
        self.file.text = "Current File: " + self.path.text
        global currentfile
        currentfile = self.path.text
        print(currentfile)

    def insert(self):
        global currentfile
        dest = currentfile
        correct_type = True
        if self.machine.text == "CNC":
            dest = r"\\MILL-CIM\Users\cimlab\Documents\cncFiles" + '\\'
            correct_type = currentfile.endswith(".gcode")
        if self.machine.text == "Printer":
            dest = r"\\cim9\toPrint" + '\\'
            correct_type = currentfile.endswith(".stl")
        if correct_type:
            #Path(currentfile).rename(dest + os.path.basename(currentfile))
            cmd = "copy " + currentfile + " " + dest + os.path.basename(currentfile)
            os.system(cmd)
            # print(currentfile + " To " + dest + os.path.basename(currentfile))
        else:
            print(currentfile + " is wrong file type for " + dest)

    def complete(self):
        self.manager.current = 'complete'
        global location
        location = self.machine.text



class CompleteScreen(Screen):

    global location
    global currentfile

    list = ObjectProperty()
    info = ObjectProperty()
    upd = ObjectProperty()

    def update(self):
        if self.upd.text == "Show List":
            self.show()
            self.upd.text = "Show Info"
        else:
            self.list.text = ""
            self.info.text = "This option is for marking that your product is completed, and allowing the next to be sent.\nDo not click yes before your product is done.\nIf milling: please remove the used material block and replace with another for the next student.\nIf printing: please remove the finished product\n"
            self.upd.text = "Show List"

    def show(self):

        global location
        global currentfile

        # open the waiting list
        folder = "./"
        if location == "CNC":
            folder = r"\\MILL-CIM\Users\cimlab\Documents\Mill_Code" + '\\'
        elif location == "Printer":
            folder = r"\\cim9\Printer_Code" + '\\'
        try:
            f = open(folder + "WaitingList.txt", "r")
            # read the waiting list
            data = ""
            state = -1
            for line in f:
                if line[0] == '0':
                    data += "Waiting: "
                if line[0] == '1':
                    data += "In Progress: "
                if line[0] == '2' and SHOW_COMPLETED:
                    data += "Completed: "
                # check if current file in list, and state
                if line[1:len(line) - 1] == os.path.basename(currentfile) and state == -1:
                    state = int(line[0])
                if (line[0] != '2') or SHOW_COMPLETED:  # skip completed
                    data += line[1:]

            # update GUI with list
            self.list.text = data
            # update GUI current file's status
            status = "not in list"
            if state != -1:
                if state == 0:
                    status = "waiting"
                if state == 1:
                    status = "in progress"
                if state == 2:
                    status = "completed"
            self.file.text = currentfile + " is " + status
            # print(currentfile + " is " + status)
            f.close()
        except:
            self.list.text = "List not found!"
        self.info.text = ""
        
    def done(self):
        global location
        global currentfile

        # open completed list
        folder = ""
        if location == "CNC":
            folder = r"\\MILL-CIM\Users\cimlab\Documents\Mill_Code" + '\\'
        elif location == "Printer":
            folder = r"\\cim9\Printer_Code" + '\\'
        f = open(folder + "CompletedList.txt", "a")

        if location == "CNC":
            folder = r"\\MILL-CIM\Users\cimlab\Documents\cncFiles" + '\\'
        elif location == "Printer":
            folder = r"\\cim9\toPrint" + '\\'
        # append current file to list
        f.write(folder + os.path.basename(currentfile) + "\n")

        f.close()


class GUIApp(App):
    # Declare both screens

    def build(self):
        # Create the screen manager
        # sm = ScreenManager(transition=NoTransition())
        sm = ScreenManager()
        sm.add_widget(InputScreen(name='input'))
        sm.add_widget(CompleteScreen(name='complete'))

        return sm


if __name__ == '__main__':
    GUIApp().run()
