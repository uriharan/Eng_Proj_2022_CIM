import cv2, numpy as np, openpyscad as ops


class Cnc:

    def __init__(self, pic):

        '''
        Reads image and resizes it to the size of the raw block material 90,50
        Takes contours from image, and
        :argument
        '''
        self.hight = 90
        self.width = 50
        self.thick = 15
        # Read image
        im = cv2.imread(pic)
        # If image orientation is portrait
        dim = im.shape
        if (dim[0] > dim[1]):
            # Resize to portrait
            im = cv2.resize(im, (self.width, self.hight))
        # Else
        else:
            # Resize to landscape
            im = cv2.rotate(im, cv2.ROTATE_90_CLOCKWISE)
            im = cv2.resize(im, (self.width, self.hight))
        self.im = im
        # Convert image to gray.
        self.imgray = cv2.cvtColor(self.im, cv2.COLOR_BGR2GRAY)
        # Threshold the image with correct threshold parameter.
        ret, thresh = cv2.threshold(self.imgray, 127, 255, cv2.THRESH_BINARY_INV)
        # Find image contours.
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:]
        # Initial code for milling.
        self.contours = contours
        self.txt1 = '''
         m6 t3 
         T01 ( TOOL NAME: 3   )
         N10 G54 G90 G00 Z50 S2000 M03
         X0 Y0.
         '''
        # Gcode for entering the mill block.
        self.txt2 = '''
         Z2.
         Z1.
         G01 Z-2. F105
        '''
        # Gcode for exiting the mill block.
        self.txt3 = '''
         G00 Z5.
         Z50.
         '''
        self.number = -1
        self.cont_dict = {}
        self.c_contour = []
        self.txt4 = '''
         Z2.
         Z1.
         G01 Z-4. F105
        '''
    def show(self):

        '''
        Show all contours the user selects the best contour for printing by its number.
        :return:
        '''
        # Declare dictionary
        cont_dict = {}
        # Loop all the enumerate contours
        for num in range(len(self.contours)):
            # Set dictionary key as img# num and value as a copy of the image
            cont_dict[num] = self.im.copy()
            # Draw each contour separately
            cont_dict[num] = cv2.drawContours(cont_dict[num], self.contours, num, (0, 255, 0), 2)
            # Write the number of the contour on the image
            cv2.putText(cont_dict[num], str(num), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0))
            # Show it

            cv2.imshow('cont' + str(num), cv2.resize(cont_dict[num], (200, 360)))

        # Wait for user to choose the number.
        chosen_num = -1
        while True:
            k = cv2.waitKey(1) & 0xFF
            flag = False
            for num in cont_dict.keys():
                if k == 48 + num:
                    chosen_num = num
                    flag = True
            if flag:
                break
        # Store that number as class variable
        self.number = chosen_num
        self.cont_dict = cont_dict
        # Destroy all windows.
        cv2.destroyAllWindows()
        # Flatten the chosen contour for milling.
        self.c_contour = self.contours[self.number].squeeze()
        self.c_contour = [[x[0], x[1]] for x in self.c_contour]

    def make_3Dprint(self, file):

        '''
        Take chosen contour from show method, makes polygon with openscad from it,
        extrude it to desired thickness and writes it to a scad file.
        parameter: File name of output file.
        :return:
        '''
        # Declare list of points.
        pts = []
        # Loop all points of chosen contour.
        for point in self.c_contour:
            # Add point of contour to list of points
            pts.append(point)
        # Construct poligon
        p = ops.Polygon(points=pts)
        # # linear extrude the poligon to material thickness.
        le = p.linear_extrude(4)
        # center model in z axe translate it to -self.thick/2
        le = le.translate([0, 0, -int(self.thick / 2)])
        # Write the extruded model to a scad file.
        le.write(file)

    def sketch(self, file):

        '''
        Write a gcode milling file of the chosen contour.
        :argument Output file name.
        '''
        # Open file for writing.
        f = open(file, "w")
        # Write initial milling code
        f.write(self.txt1)
        # Gcode run in fast mode to start point of the chosen contour 10 mm above material and operate flood mode M8
        f.write("G00 Y" + str(self.c_contour[0][0]) + " X" + str(self.c_contour[0][1]) + " Z" + str(
            self.thick + 10) + " M8")
        # Gcode enter the mill block
        f.write(self.txt2)
        # Loop every second item in flatten contour
        for point in self.c_contour:
            # Write as Gcode the contour x and y
            f.write("Y" + str(point[0]) + " X" + str(point[1]) + "\n")
        # Write Gcode for exit the milling block.
        f.write(self.txt3)
        f.close()

    def mill(self, frame, x, y, f):
        frame[x][y]=128
        dir = 0
        arr = [[0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1]]
        flag = False
        while not flag:
            for i in range(0, 9):
                if (not ((x + arr[(dir + i) % 8][0] >= len(frame)) or (y + arr[(dir + i) % 8][1] >= len(frame[0])))) and ( not ((x + arr[(dir + i) % 8][0] <0) or (y + arr[(dir + i) % 8][1] < 0))):
                    print((dir + i) % 8)
                    print(x + arr[(dir + i) % 8][0])
                    print(y + arr[(dir + i) % 8][1])
                    if frame[x + arr[(dir + i) % 8][0]][y + arr[(dir + i) % 8][1]] == 255:
                        frame[x + arr[(dir + i) % 8][0]][y + arr[(dir + i) % 8][1]] = 128
                        x = x + arr[(dir + i) % 8][0]
                        y = y + arr[(dir + i) % 8][1]
                        f.write("X" + str(x) + " Y" + str(y) + "\n")
                        dir = dir + i + 4
                        break
                if i == 8:
                    flag = True


    def search(self, file, name, loc):
        ret, thresh = cv2.threshold(self.imgray, 127, 255, cv2.THRESH_BINARY_INV)
        frame = np.asarray(thresh)
        # Open file for writing.
        f = open(file, "w")
        f.write(self.txt1)
        for x in range(len(frame)):
            for y in range(len(frame[x])):
                if frame[x][y]==255:
                    f.write("G00 X" + str(x) + " Y" + str(y) + " Z" + str(5) + " M8")
                    f.write(self.txt2)
                    self.mill(frame, x, y, f)
                    f.write("G00 Z5.\n")

        cv2.putText(frame, name, loc, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0))
        angle = -90
        M = cv2.getRotationMatrix2D(loc, angle, 1)
        out = cv2.warpAffine(frame, M, (frame.shape[1], frame.shape[0]))

        for x in range(len(out)):
            for y in range(len(out[x])):
                if out[x][y] == 255:
                    f.write("G00 X" + str(x) + " Y" + str(y) + " Z" + str(5) + " M8")
                    f.write(self.txt4)
                    self.mill(out, x, y, f)
                    f.write("G00 Z5.\n")
        f.write(self.txt3)
        f.close()



cnc = Cnc('TAU.jpg')
cnc.show()
cnc.sketch('contour.gcode')
cnc.make_3Dprint('newTau.scad')
cnc.search('base.gcode', "UR", (20, 25))


