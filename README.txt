Code Instructions

The code is stored in the Final_Code folder.
each section should be moved to the following location:
1. Mill_Code folder should be placed at \\MILL-CIM\Users\cimlab\Documents\
2. Printer_Code folder should be placed at \\cim9\

Note that for the student’s GUI to function, these folders should have network write permissions.
[Right Click - Properties - Sharing - Advanced Sharing - Permissions - Change]

to run the code, detector_final.py should be run (requires watchdog installed)
-the code deletes previous iterations of the waiting and completed list. This may be disabled by switching the global variable DELETE_PRIOR to false.
--after termination of the program, it is recommended to edit or remove the created WaitingList.txt in the folder if the aforementioned variable is false, as when re-running the code it will act equivalently to not having terminated it and continue where it left off.
