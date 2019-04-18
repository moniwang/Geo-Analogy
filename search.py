import re
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import math
import matplotlib.path as mplPath
import os
import os.path

#--------------------------FUNCTIONS/CLASSES------------------------------------

# Plots a line
# ((x1, y1), (x2, y2))
def plotpoints(points, color):
    x1, x2 = points[0][0], points[1][0]
    y1, y2 = points[0][1], points[1][1]
    plt.plot([x1,x2],[y1,y2], color + '-')

# Plots all polygons, circles, and dots with different color and saves it
def makeFigure(shapes, circles, dots, filename, numFig):
    # [[shape][shape]] 
    # [[[x1,y1], [x2,y2]]]

    # Setting the x and y axis to be 100x100
    plt.gcf().gca().set_xlim((0, 100))
    plt.gcf().gca().set_ylim((0, 100))
    plt.gca().set_aspect('equal', adjustable='box')

    # Gets rid of tick marks
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)


    # Colors to cycle through
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    colorNum = 0
    
    # Plotting each shape
    for shape in shapes:
        for lines in shapes:
            for line in lines:
                plotpoints(line, colors[colorNum])
            colorNum+=1
            colorNum = colorNum%len(colors)

    # Plotting each circle
    for circle in circles:
        plotCircle = plt.Circle((float(circle[0][0]), float(circle[0][1])), float(circle[1]), color = colors[colorNum], fill = False)
        plt.gcf().gca().add_artist(plotCircle)
        colorNum+=1
        colorNum = colorNum%len(colors)

    # Plotting each dot
    for dot in dots:
        plt.plot(float(dot[0]), float(dot[1]), colors[colorNum]+'o')
        colorNum+=1
        colorNum = colorNum%len(colors)

    # Path
    splitpath = []
    split2 = []
    newFile = filename + numFig + ".png"
    splitpath = newFile.split('/')
    extract = splitpath[-1]
    pathCurrent = os.getcwd()
    split2 = pathCurrent.split('/')
    finalpath = ""
    for i in range(len(split2)-1):
        finalpath += split2[i] + "/"
    finalpath += sys.argv[2] + "/" + extract

    # Saves figure
    plt.savefig(finalpath)


    # Clears figure for next interpretation
    plt.clf()
    plt.cla()

# Checks if two arrays are equal
def checkEqual(one, two):
    if len(one) != len(two):
        return False
    for coord in one:
        if coord not in two:
            return False
    return True

# Checks if two containers of interpretations are equal
def checkContainer(one, two):
    # A lot of sorting in this
    oneCopy = one[:]
    twoCopy = two[:]

    shapeCoords = []
    for shape in oneCopy:
        oneShape = []
        for coords in shape:
            if coords[0] not in oneShape:
                oneShape.append(coords[0])
            if coords[1] not in oneShape:
                oneShape.append(coords[1])
        oneShape.sort()
        shapeCoords.append(oneShape)
    shapeCoords.sort()
    
    shapeCoords2 = []
    for shape in twoCopy:
        oneShape = []
        for coords in shape:
            if coords[0] not in oneShape:
                oneShape.append(coords[0])
            if coords[1] not in oneShape:
                oneShape.append(coords[1])
        oneShape.sort()
        shapeCoords2.append(oneShape)
    shapeCoords2.sort()
    return shapeCoords == shapeCoords2
    
# Finds all interpretations of the lines given
def findShapes (lines):

    # ULTIMATE CONTAINER OF ALL INTERPRETATIONS
    container = []
    textContainer = []

    # Copying lines to avoid changing the original
    linesCopy = lines[:]

    # Interpretations but in a different form
    interpretations = []

    # [ (parent, point), (parent, point) ]
    stack = []
    stack.append((linesCopy[0][0], linesCopy[0][0]))

    # [ (point), (point) ]
    visited = []

    # While stack still has items
    while len(stack) > 0:
        # If moved to a different point, we have to make sure lines are connected
        if len(visited) > 0:
            while stack[len(stack)-1][0] != visited[len(visited)-1]:
                visited.pop()
        
        # Adding point to visited
        visited.append(stack[len(stack)-1][1])
        # Point for comparison
        point = stack[len(stack)-1]
        # Pop from stack
        stack.pop()

        # For each line, compare with current point
        for line in linesCopy:
            # Compare to see if connects with first point
            if point[1] == line[0] and line[1] == visited[0] and point[0] != line[1]:
                new = visited[:]
                interpretations.append(new)
            elif point[1] == line[1] and line[0] == visited[0] and point[0] != line[0]:
                new = visited[:]
                interpretations.append(new)
            # Compare to see if connects to current point
            elif point[1] == line[0] and point[0] != line[1] and line[1] not in visited:
                stack.append((point[1], line[1]))
            elif point[1] == line[1] and point[0] != line[0] and line[0] not in visited:
                stack.append((point[1], line[0]))

    # Getting rid of duplicates
    for i in range(len(interpretations)):
        j = i+1
        while j < len(interpretations):
            if checkEqual(interpretations[i], interpretations[j]):
                del interpretations[j]
                j-=1
            j+=1

    for each in interpretations:
        # Putting the points in line form and separating them into used lines
        # and unused lines
        linesUsed = []
        unusedLines = []
        flag = True
        # Checking to see if the line was used
        for i in range(len(each)-1):
            for line in linesCopy:
                if (each[i] == line[0] and each[i+1] == line[1]) or (each[i] == line[1] and each[i+1] == line[0]):
                    linesUsed.append(line)
                elif (each[0] == line[0] and each[len(each)-1] == line[1]) or (each[0] == line[1] and each[len(each)-1] == line[0]):
                    if flag:
                        flag = False
                        linesUsed.append(line)

        # Checking to see if the line was not used
        for line in linesCopy:
            if line not in linesUsed:
                unusedLines.append(line)
        
        # If unused lines was greater than 0, we recursively call this function
        # until all lines are used and we have an interpretation
        if len(unusedLines) > 0:
            more, diff = findShapes(unusedLines)
            for anInt in more:
                oneInt = []
                oneInt.append(linesUsed)
                for aShape in anInt:
                    oneInt.append(aShape)
                container.append(oneInt)
            for aInt in diff:
                twoInt = []
                twoInt.append(each)
                for shape in aInt:
                    twoInt.append(shape)
                textContainer.append(twoInt)
        else:
            container.append([linesUsed])
            textContainer.append([each])

    # Format for this variable
    # [  ALL INTERPRETS[ALL SHAPES/ONE INTERPRET[ONE SHAPE][ONE SHAPE]]  [INTERPRETATION[SHAPE][SHAPE]]  ]
    return container, textContainer

# Area of a polygon
def area(vertices):
    sum = 0
    for i in range(len(vertices)-1):
        x1 = float(vertices[i][0])
        y1 = float(vertices[i][1])
        x2 = float(vertices[i+1][0])
        y2 = float(vertices[i+1][1])
        sum += ((x1*y2) - (x2*y1))
    return abs(sum/2)

# Center of mass of a polygon
def centroid(vertices):
    cxSum = 0
    cySum = 0
    for i in range(len(vertices)-1):
        x1 = float(vertices[i][0])
        y1 = float(vertices[i][1])
        x2 = float(vertices[i+1][0])
        y2 = float(vertices[i+1][1])
        cxSum += ((x1+x2)*((x1*y2) - (x2*y1)))
        cySum += ((y1+y2)*((x1*y2) - (x2*y1)))
    shapeArea = area(vertices)
    cxSum = abs(cxSum/(6*shapeArea))
    cySum = abs(cySum/(6*shapeArea))

    return cxSum, cySum

# hloc (left, middle, right) : compare with value 50
# vloc (top, middle, bottom) : compare with value 50
def loc(x, y):
    x = float(x)
    y = float(y)
    xLoc = ""
    yLoc = ""
    if x > 50:
        xLoc = "right"
    elif x < 50:
        xLoc = "left"
    else:
        xLoc = "center"

    if y > 50:
        yLoc = "top"
    elif y < 50:
        yLoc = "bottom"
    else:
        yLoc = "center"
    
    return xLoc, yLoc

# Finds the slope of a line
def slope(first, second):
    rise = float(second[1]) - float(first[1])
    run = float(second[0]) - float(first[0])
    if run == 0:
        return "vert"
    else:
        return (rise/run)

# Finds the distance of a line
def distance(first, second):
    x1 = float(first[0])
    y1 = float(first[1])
    x2 = float(second[0])
    y2 = float(second[1])
    distance = (x2-x1)**2 + (y2-y1)**2
    return math.sqrt(distance)

# Generating text files
def makeText(shapes, circles, circleName, dots, dotName, filename, numFig):

    # Path
    splitpath = []
    split2 = []
    newFile = filename + numFig + ".txt"
    splitpath = newFile.split('/')
    extract = splitpath[-1]
    pathCurrent = os.getcwd()
    split2 = pathCurrent.split('/')
    finalpath = ""
    for i in range(len(split2)-1):
        finalpath += split2[i] + "/"
    finalpath += sys.argv[2] + "/" + extract

    write = open(finalpath, "w")

    centroids = []
    centroidName = []
    listShapes = []

    index = len(lines)

    # Finding scc
    for i in range(len(shapes)):
        shape = shapes[i][:]

        oneShape = []
        for coords in shape:
            oneShape.append([float(coords[0]), float(coords[1])])
        listShapes.append(oneShape)

        shape.append(shape[0])
        scc = []
        for j in range(len(shape)-1):
            for k in range(len(lines)):
                if (shape[j] == lines[k][0] and shape[j+1] == lines[k][1]) or (shape[j] == lines[k][1] and shape[j+1] == lines[k][0]):
                    scc.append(lineName[k])

        # Finding the shape of the shape :O
        longerLines = []
        sccLongLine = []

        pointsRemoved = []

        prevSlope = slope(shape[0], shape[1])
        startPoint = shape[0]
        endPoint = shape[1]

        startHere = 0

        for j in range(1, len(shape)-1):
            if slope(shape[j], shape[j+1]) != prevSlope:
                prevSlope = slope(shape[j], shape[j+1])
                startPoint = shape[j]
                endPoint = shape[j+1]
                startHere = j
                break

        sccLong = []
        longerLines.append(startPoint)
        # Starts at first and second point of polygon
        for l in range(len(shapes[i])):
            j = (l+startHere)%len(shapes[i])
            k = (l+startHere+1)%len(shapes[i])
            # If the slope of the line equals the slope of the previous line
            if slope(shapes[i][j], shapes[i][k]) == prevSlope:
                # Add line name and change the end point
                sccLong.append(scc[j])
                pointsRemoved.append(endPoint)
                endPoint = shapes[i][k]
            # If the slope does not equal slope of previous line
            else:
                # Add start point and end point of previous line
                longerLines.append(endPoint)
                # Add line names
                sccLongLine.append(sccLong[:])
                sccLong.clear()
                # Change start point and end point to current line
                # Change slope to this line too
                startPoint = shapes[i][j]
                endPoint = shapes[i][k]
                prevSlope = slope(shapes[i][j], shapes[i][k])
                sccLong.append(scc[j])

        sccLongLine.append(sccLong[:])
        longerLines.append(endPoint)

        sccUpdate = []

        for j in range(len(sccLongLine)):
            if len(sccLongLine[j]) > 1:
                newline = 's' + str(index+1)
                index+=1
                sccUpdate.append(newline)
                print (newline + '=line(' + str(longerLines[j][0]) + "," + str(longerLines[j][1])+ "," + str(longerLines[j+1][0])+ "," + str(longerLines[j+1][1]) + ") = ", end = "", file = write)
                for k in range(len(sccLongLine[j])-1):
                    print (sccLongLine[j][k], end = "", file = write)
                    print (" + ", end = "", file = write)
                print (sccLongLine[j][-1], file = write)
            else:
                sccUpdate.append(sccLongLine[j][0])

        print ('p' + str(i+1) + "=scc(", end = "", file = write)
        for j in range(len(longerLines)-1):
            print (str(longerLines[j]) + ",0,", end = "", file = write)
        print(str(longerLines[0]) + ") = ", end = "", file = write)
        for l in range(len(sccUpdate)-1):
            print(sccUpdate[l] + " + ", end = "", file = write)
        print (sccUpdate[-1], file = write)
        

        if len(longerLines) == 5:
            if (slope(longerLines[0], longerLines[1]) == slope(longerLines[2], longerLines[3]) and slope(longerLines[1], longerLines[2]) == slope(longerLines[3], longerLines[4]) ):
                rectangle = False
                if (slope(longerLines[0], longerLines[1]) == 0 and slope(longerLines[1], longerLines[2]) == "vert"):
                    rectangle = True
                elif (slope(longerLines[0], longerLines[1]) == "vert" and slope(longerLines[1], longerLines[2]) == 0):
                    rectangle = True
                elif (slope(longerLines[0], longerLines[1]) != 0 and slope(longerLines[1], longerLines[2]) != "vert" and slope(longerLines[1], longerLines[2]) != 0 and slope(longerLines[0], longerLines[1]) != "vert" and slope(longerLines[0], longerLines[1]) == (-1/slope(longerLines[1], longerLines[2]))):
                    rectangle = True
                if (rectangle):
                    if distance(longerLines[0], longerLines[1]) == distance(longerLines[1], longerLines[2]):
                        print("square(" + 'p' + str(i+1) + ")", file = write)
                    else:
                        print("rectangle(" + 'p' + str(i+1) + ")", file = write)

        if (len(longerLines)) == 4:
            print("triangle(" + 'p' + str(i+1) + ")", file = write)
        
        # Centroid of the shape
        cX, cY = centroid(shape)
        centroids.append((cX, cY))
        centroidName.append('p'+ str(i+1))

        # vloc and hloc
        xloc, yloc = loc(cX, cY)
        print("vloc(p" + str(i+1) + "," + yloc + ")", file = write)
        print("hloc(p" + str(i+1) + "," + xloc + ")", file = write)

    # Circle description
    for i in range(len(circles)):
        centroids.append((float(circles[i][0][0]), float(circles[i][0][1])))
        centroidName.append(circleName[i])
        print("circle(" + circleName[i] + ")", file = write)
        xloc, yloc = loc(circles[i][0][0], circles[i][0][1])
        print("vloc(" + circleName[i] + "," + yloc + ")", file = write)
        print("hloc(" + circleName[i] + "," + xloc + ")", file = write)

    # Dot description
    for i in range(len(dots)):
        centroids.append((float(dots[i][0]), float(dots[i][1])))
        centroidName.append(dotName[i])
        print("dot(" + dotName[i] + ")", file = write)
        xloc, yloc = loc(dots[i][0], dots[i][1])
        print("vloc(" + dotName[i] + "," + yloc + ")", file = write)
        print("hloc(" + dotName[i] + "," + xloc + ")", file = write)

    # Position
    for i in range(len(centroids)):
        for j in range(i+1, len(centroids)):
            if centroids[i][0] < centroids[j][0]:
                print ("left_of(" + centroidName[i] + "," + centroidName[j] + ")", file = write)
            elif centroids[i][0] > centroids[j][0]:
                print ("right_of(" + centroidName[i] + "," + centroidName[j] + ")", file = write)
            if centroids[i][1] < centroids[j][1]:
                print ("below(" + centroidName[i] + "," + centroidName[j] + ")", file = write)
            elif centroids[i][1] > centroids[j][1]:
                print ("above(" + centroidName[i] + "," + centroidName[j] + ")", file = write)

    # Overlap/Inside
    for i in range(len(centroidName)):
        alreadyHappened = False
        for j in range(i+1, len(centroidName)):
            # Comparing polygon to a polygon
            if centroidName[i][0] == 'p' and centroidName[j][0] == 'p':
                edgeInside, edgeOutside = checkInside(listShapes[i], listShapes[j])

                # Getting rid of shared points by both figures
                values = []
                for k in range(len(edgeInside)):
                    if edgeOutside[k] == edgeInside[k]:
                        values.append(edgeInside[k])
                
                if len(values) == 0:
                    print("inside(" + centroidName[j] + "," + centroidName[i] + ")", file = write)
                    continue

                result = values[0]

                # Checking for overlap
                flag = True
                for k in range(0, len(values)):
                    if values[k] != result:
                        print("overlap(" + centroidName[i] + "," + centroidName[j] + ")", file = write)
                        alreadyHappened = True
                        flag = False
                        break

                # All points inside
                if result == True and flag:
                    print("inside(" + centroidName[j] + "," + centroidName[i] + ")", file = write)
                # All points outside, checking the other way around
                elif result == False and flag:
                    edgeIn, edgeOut = checkInside(listShapes[j], listShapes[i])
                    values2 = []
                    for k in range(len(edgeIn)):
                        if edgeIn[k] == edgeOut[k]:
                            values2.append(edgeIn[k])
                    final = values2[0]

                    # Checking for overlap
                    flag2 = True
                    for k in range(0, len(values2)):
                        if values2[k] != final:
                            flag2 = False
                            alreadyHappened = True
                            print("overlap(" + centroidName[i] + "," + centroidName[j] + ")", file = write)
                            break
                    
                    # All points inside
                    if final == True and flag2:
                        print("inside(" + centroidName[i] + "," + centroidName[j] + ")", file = write)
                
                # More checking for overlap
                # Keep track of all segmented points
                # Iterate through them as pairs and check if the midpoint of those lines are on the shape
                # using edge inside and if that midpoint is also inside the current shape, then overlap has occurred
                if not alreadyHappened and len(pointsRemoved) > 1:
                    isoverlapping = False
                    del pointsRemoved[0]
                    for q in range(len(pointsRemoved)-1):
                        midpointX, midpointY = findMidpoint(pointsRemoved[q], pointsRemoved[q+1])
                        midpoints = []
                        midpoints.append([midpointX, midpointY])
                        newedgein, newedgeout = checkInside(listShapes[i], midpoints)
                        anotheredgein, anotheredgeout = checkInside(listShapes[j], midpoints)
                        if (newedgein[0] == True and newedgein[0] == anotheredgein[0]):
                            isoverlapping = True
                    
                    if not isoverlapping:
                        midpointX, midpointY = findMidpoint(pointsRemoved[0], pointsRemoved[-1])
                        midpoints = []
                        midpoints.append([midpointX, midpointY])
                        newedgein, newedgeout = checkInside(listShapes[i], midpoints)
                        anotheredgein, anotheredgeout = checkInside(listShapes[j], midpoints)
                        if (newedgein[0] == True and newedgein[0] == anotheredgein[0]):
                            isoverlapping = True

                    if isoverlapping:
                        print("overlap(" + centroidName[i] + "," + centroidName[j] + ")", file = write)
                
            # Comparing polygon to a circle
            elif centroidName[i][0] == 'p' and centroidName[j][0] == 'c':
                circlePoints = []
                circleIndex = int(centroidName[j][1])-1
                cirX = float(circles[circleIndex][0][0])
                cirY = float(circles[circleIndex][0][1])
                radius = float(circles[circleIndex][1])
                circlePoints.append([cirX+radius, cirY])
                circlePoints.append([cirX-radius, cirY])
                circlePoints.append([cirX, cirY+radius])
                circlePoints.append([cirX, cirY-radius])
                
                circleIn, circleOut = checkInside(listShapes[i], circlePoints)
                
                # The circle is in the polygon
                if circleIn[0] == True:
                    print("inside(" + centroidName[j] + "," + centroidName[i] + ")", file = write)

                # Check if the polygon is in the circle
                else:
                    inCircle = [insideCircle(pnt, [cirX, cirY], radius) for pnt in listShapes[i]]

                    insideCir = True
                    for p in inCircle:
                        if p == False:
                            insideCir = False
                    
                    if insideCir:
                        print("inside(" + centroidName[i] + "," + centroidName[j] + ")", file = write)
            
            # Comparing polygon to a dot
            elif centroidName[i][0] == 'p' and centroidName[j][0] == 'd':
                dotLoc = dots[int(centroidName[j][1])-1]
                dotX = float(dotLoc[0])
                dotY = float(dotLoc[1])
                edgeInside, edgeOutside = checkInside(listShapes[i], [[dotX, dotY]])
                
                if edgeInside[0] == edgeOutside[0]:
                    if edgeInside[0] == True:
                        print("inside(" + centroidName[j] + "," + centroidName[i] + ")", file = write)
                else:
                    print("overlap(" + centroidName[j] + "," + centroidName[i] + ")", file = write)
    
            # Comparing circle to circle
            elif centroidName[i][0] == 'c' and centroidName[j][0] == 'c':
                # Points on the second circle
                circlePoints = []
                circleIndex = int(centroidName[j][1])-1
                cirX = float(circles[circleIndex][0][0])
                cirY = float(circles[circleIndex][0][1])
                radius = float(circles[circleIndex][1])
                circlePoints.append([cirX+radius, cirY])
                circlePoints.append([cirX-radius, cirY])
                circlePoints.append([cirX, cirY+radius])
                circlePoints.append([cirX, cirY-radius])

                # Points on the first circle
                circlePoints2 = []
                circleIndex2 = int(centroidName[i][1])-1
                cirX2 = float(circles[circleIndex2][0][0])
                cirY2 = float(circles[circleIndex2][0][1])
                radius2 = float(circles[circleIndex2][1])
                circlePoints2.append([cirX2+radius2, cirY2])
                circlePoints2.append([cirX2-radius2, cirY2])
                circlePoints2.append([cirX2, cirY2+radius2])
                circlePoints2.append([cirX2, cirY2-radius2])

                inCircle = [insideCircle(pnt, [cirX, cirY], radius2) for pnt in circlePoints]
                if inCircle[0] == True:
                    print("inside(" + centroidName[j] + "," + centroidName[i] + ")", file = write)
                else:
                    inCircle2 = [insideCircle(pnt, [cirX2, cirY2], radius) for pnt in circlePoints2]
                    if inCircle2[0] == True:
                        print("inside(" + centroidName[i] + "," + centroidName[j] + ")", file = write)
            
            # Comparing circle to dot
            elif centroidName[i][0] == 'c' and centroidName[j][0] == 'd':

                dotLoc = dots[int(centroidName[j][1])-1]
                dotX = float(dotLoc[0])
                dotY = float(dotLoc[1])

                circleIndex = int(centroidName[i][1])-1
                cirX = float(circles[circleIndex][0][0])
                cirY = float(circles[circleIndex][0][1])
                radius = float(circles[circleIndex][1])

                if insideCircle([dotX, dotY], [cirX, cirY], radius):
                    print("inside(" + centroidName[j] + "," + centroidName[i] + ")", file = write)


# Checks if a point is inside a circle
def insideCircle(point, center, r):
    x = point[0]
    y = point[1]
    a = center[0]
    b = center[1]
    return ((x - a)*(x - a) + (y - b)*(y - b)) < (r*r)

# Checks if points are inside polygon
def checkInside(polygonOne, polygonTwo):
    polygon = np.array(polygonOne) # All points of polygon (but in different form)
    path = mplPath.Path(polygon) # Makes polygon
    checkPoints = polygonTwo # The inside polygon (points, not lines)
    edgeInside = [path.contains_point(point, radius = 0.001) or path.contains_point(point, radius = -0.001) for point in checkPoints]
    edgeOutside = [(path.contains_point(point, radius = 0) or path.contains_point(point, radius = 0)) and point not in polygonOne for point in checkPoints]
    return edgeInside, edgeOutside

# Find the midpoint of a line
def findMidpoint(point1, point2):
    x1 = float(point1[0])
    y1 = float(point1[1])
    x2 = float(point2[0])
    y2 = float(point2[1])
    return ((x1+x2)/2, (y1+y2)/2)

# -------------------------PARSING THE INPUT------------------------------------

# Getting contents from text file
with open(sys.argv[1], 'r') as f:
    contents = f.readlines()

filename = re.split('\\.', sys.argv[1])

# Stores lines, circles and dots
lineName = []
lines = []
circleName = []
circles = []
dotName = []
dots = []

# Separating the file contents into different shapes
for line in contents:
    split = re.split('\\=|\\,|\\(|\\)| ', line)
    if split[3] == "line":
        lines.append(((split[4], split[5]), (split[6], split[7])))
        lineName.append(split[0])
    elif split[3] == "circle":
        circleName.append(split[0])
        circles.append(((split[4], split[5]), split[6]))
    elif split[3] == "dot":
        dotName.append(split[0])
        dots.append((split[4], split[5]))

#--------------------------FINDING ALL INTERPRETATIONS--------------------------

container, textContainer = findShapes(lines)

#--------------------------DESCRIBING PROPERTIES--------------------------------

#--------------------------MAKING FIGURES AND TEXT FILES------------------------
   
# Getting rid of duplicates in the container of interpretations
for i in range(len(container)):
    j = i+1
    while j < len(container):
        if checkContainer(container[i], container[j]):
            del container[j]
            j-=1
        j+=1

# Iterating through the container to print each interpretation and their details
for i in range(len(container)):
    if i > 26:
        makeFigure(container[i], circles, dots, filename[0], '_' + str(i-27))
        makeText(textContainer[i], circles, circleName, dots, dotName, filename[0], '_' + str(i-27))
    else:
        makeFigure(container[i], circles, dots, filename[0], chr(97 + i))
        makeText(textContainer[i], circles, circleName, dots, dotName, filename[0], chr(97 + i))
