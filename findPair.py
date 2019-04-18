import re
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import itertools
import numpy as np
import math
import matplotlib.path as mplPath
import os
import os.path
import glob
from a1 import *

#--------------------------INPUTS/OUTPUTS---------------------------------------

inputFolder = sys.argv[1]
outputFolder = 'interpretations' # change this to the path where you want to dump your interpretation files from A1

files = glob.glob(outputFolder + '/*')
for f in files:
    os.remove(f)

inputFiles = glob.glob(inputFolder + '/*.txt') # gives a list of paths to all text files in inputFolder
for filePath in inputFiles:
    filePath = filePath.replace('\\','/') # in windows, glob returns path with '\\' instead of '/'
    main(filePath, outputFolder) # accessing the main function of A1

#--------------------------FUNCTIONS/CLASSES------------------------------------
shapesH = ['triangle', 'polygon', 'pentagon', 'hexagon', 'septagon', 'octagon', 'nonagon', 'decagon', 'hendecagon', 'dodecagon', 'square', 'rectangle']
# Reads a file and parses it
def readFile(fileName):
    # Getting contents from text file
    with open(fileName, 'r') as f:
        fileItems = f.readlines()

    contents = fileItems

    shapeNames = []
    vertices = []
    pskipped = False
    # Separating the file contents into different shapes
    for line in contents:
        split = re.split('\\=|,0,|\\,|\\(|\\)|\\[|\\]|\\:| ', line)
        split = list(filter(None, split))
        if line[0] == "p":
            if pskipped == False:
                pskipped = True
                continue
            pskipped = False
            if split[0] not in shapeNames:
                shapeNames.append(split[0])
                coords = []
                for i in range(2, len(split)-1, 2):
                    if (split[i][0] == 's'):
                        break
                    coords.append((float(split[i]), float(split[i+1])))
                vertices.append(coords)

        if line[0] == "c":
            if split[0] not in shapeNames and split[0] != "circle":
                shapeNames.append(split[0])

                coords = []
                coords.append((float(split[1]), float(split[2])))
                coords.append(float(split[3]))
                vertices.append(coords)

        if line[0] == "d":
            if split[0] not in shapeNames and split[0] != "dot":
                shapeNames.append(split[0])
                vertices.append([float(split[1]), float(split[2])])

    vloc = [0]*len(shapeNames)
    hloc = [0]*len(shapeNames)
    shapeType = [0]*len(shapeNames)
    properties = []
    shapeOf = []

    for i in range(len(shapeNames)):
        properties.append([])
        shapeOf.append([])

    for line in contents:
        split = re.split('\\=|,0,|\\,|\\(|\\)|\\[|\\]|\\:| ', line)
        split = list(filter(None, split))
        if split[0] == "vloc":
            vloc[shapeNames.index(split[1])] = split[2]
        if split[0] == "hloc":
            hloc[shapeNames.index(split[1])] = split[2]
        if split[0] == "dot" or split[0] == "circle" or split[0] == "triangle" or split[0] == "square" or split[0] == "rectangle":
            shapeType[shapeNames.index(split[1])] = split[0]
        if split[0] == "scc":
            if (len(vertices[shapeNames.index(split[1])]) < 13):
                shapeType[shapeNames.index(split[1])] = shapesH[len(vertices[shapeNames.index(split[1])])-4]
            else:
                shapeType[shapeNames.index(split[1])] = split[0]
        if split[0] == "left_of":
            properties[shapeNames.index(split[1])].append(split[0])
            shapeOf[shapeNames.index(split[1])].append(split[2])
            properties[shapeNames.index(split[2])].append("right_of")
            shapeOf[shapeNames.index(split[2])].append(split[1])
        if split[0] == "right_of":
            properties[shapeNames.index(split[1])].append(split[0])
            shapeOf[shapeNames.index(split[1])].append(split[2])
            properties[shapeNames.index(split[2])].append("left_of")
            shapeOf[shapeNames.index(split[2])].append(split[1])
        if split[0] == "below":
            properties[shapeNames.index(split[1])].append(split[0])
            shapeOf[shapeNames.index(split[1])].append(split[2])
            properties[shapeNames.index(split[2])].append("above")
            shapeOf[shapeNames.index(split[2])].append(split[1])
        if split[0] == "above":
            properties[shapeNames.index(split[1])].append(split[0])
            shapeOf[shapeNames.index(split[1])].append(split[2])
            properties[shapeNames.index(split[2])].append("below")
            shapeOf[shapeNames.index(split[2])].append(split[1])
        if split[0] == "overlap":
            properties[shapeNames.index(split[1])].append(split[0])
            shapeOf[shapeNames.index(split[1])].append(split[2])
            properties[shapeNames.index(split[2])].append(split[0])
            shapeOf[shapeNames.index(split[2])].append(split[1])
        if split[0] == "inside":
            properties[shapeNames.index(split[1])].append(split[0])
            shapeOf[shapeNames.index(split[1])].append(split[2])
            properties[shapeNames.index(split[2])].append("contains")
            shapeOf[shapeNames.index(split[2])].append(split[1])
        if split[0] == "large" or split[0] == "small":
            properties[shapeNames.index(split[1])].append(split[0])
            shapeOf[shapeNames.index(split[1])].append('')

    return shapeNames, vertices, shapeType, vloc, hloc, properties, shapeOf

# Area of a polygon
def area(vertices, shape):
    if shape == 'circle':
        return math.pi*vertices[1]*vertices[1]
    elif shape == 'dot':
        return 1
    else:
        sum = 0
        for i in range(len(vertices)-1):
            x1 = vertices[i][0]
            y1 = vertices[i][1]
            x2 = vertices[i+1][0]
            y2 = vertices[i+1][1]
            sum += ((x1*y2) - (x2*y1))
        return abs(sum/2)

# Matching pairs in each file
def makePairs(first, second):
    fileMatch = []
    fileCombos = []
    for i in range(len(first)):
        for j in range(len(second)):
            fileMatch.append((i, j))
            # If the lengths are different
            if len(second[j][0]) > len(first[i][0]):
                for l in range(len(first[i][0]), len(second[j][0])):
                    first[i][0].append('ADD')
            if len(second[j][0]) < len(first[i][0]):
                for l in range(len(second[j][0]), len(first[i][0])):
                    second[j][0].append('DEL')

            # Finding all the pairs of objects
            combos = []
            pairs = [zip(x,second[j][0]) for x in itertools.permutations(first[i][0],len(second[j][0]))]
            for pair in pairs:
                combos.append(list(pair))
            fileCombos.append(combos)
    return fileCombos, fileMatch

# Describing matched pairs in each file
def findMatches(filePair, f1, f2):
    filePairs = []
    costForEachFile = []
    descriptions = []
    words = []
    # For each interpretation of the file
    for i in range(len(filePair[0])):
        filePairs.append(filePair[1][i])
        word = []
        # For each pairings
        costForEachPairing = []
        description = []
        for pairings in filePair[0][i]:
            # Add, Delete, Change, Size, Move, Rel
            interpret = []
            descript = ""
            pairingCost = []
            totalCost = 0

            descript += str(pairings) + '\n'

            f1Ind = filePair[1][i][0] # First file index for shape info
            f2Ind = filePair[1][i][1] # Second file index
            interpret.append(pairings)

            firstPlace = []
            secondPlace = []
            for pair in pairings:
                # Essentially, pair[0] == pair[1]
                if pair[0] == 'ADD':
                    inf1 = pair[0]
                else:
                    inf1 = f1[f1Ind][0].index(pair[0]) # Place in vector of vectors of shapes

                if pair[1] == 'DEL':
                    inf2 = pair[1]
                else:
                    inf2 = f2[f2Ind][0].index(pair[1])

                firstPlace.append(inf1)
                secondPlace.append(inf2)

            file1 = f1[f1Ind]
            file2 = f2[f2Ind]

            # shape change > add/del > rel > move > size
            # add.del.change.size.move.rel

            # 0 is name of shape
            # 1 is coordinates of shape
            # 2 is type of shape
            # 3 is vloc of shape
            # 4 is hloc of shape
            # 5 is relation to other shapes
            # 6 is the shape of relation to other shapes
            pairDescript = []
            for j in range(len(pairings)):
                oneDescript = []
                changes = []
                addDeletes = []
                rels = []
                moves = []
                sizes = []
                # Check for addition/deletion
                if firstPlace[j] == 'ADD':
                    addDeletes.append(['add', file2[0][secondPlace[j]]])
                    descript+=str('add(' + file2[0][secondPlace[j]] + ')')+"\n"
                elif secondPlace[j] == 'DEL':
                    addDeletes.append(['delete', file1[0][firstPlace[j]]])
                    descript+=str('delete(' + file1[0][firstPlace[j]] + ')')+"\n"
                else:
                    # Checking type of shape
                    if file1[2][firstPlace[j]] != file2[2][secondPlace[j]]:
                        changes.append(([file1[2][firstPlace[j]], file2[2][secondPlace[j]]],[file1[0][firstPlace[j]], file2[0][secondPlace[j]]]))
                        descript+=str('change(' + file1[2][firstPlace[j]] + '(' + file1[0][firstPlace[j]]+ '),' + file2[2][secondPlace[j]] + '(' + file2[0][secondPlace[j]] + '))')+"\n"
                    else:
                        if area(file1[1][firstPlace[j]], file1[2][firstPlace[j]]) < area(file2[1][secondPlace[j]], file2[2][secondPlace[j]]):
                            sizes.append((['small', 'large'],[file1[0][firstPlace[j]],file2[0][secondPlace[j]]]))
                            descript+=str('change(small(' + file1[0][firstPlace[j]]+ '),large(' + file2[0][secondPlace[j]] + '))')+"\n"
                        elif area(file1[1][firstPlace[j]], file1[2][firstPlace[j]]) > area(file2[1][secondPlace[j]], file2[2][secondPlace[j]]):
                            sizes.append((['large', 'small'],[file1[0][firstPlace[j]],file2[0][secondPlace[j]]]))
                            descript+=str('change(large(' + file1[0][firstPlace[j]]+ '),small(' + file2[0][secondPlace[j]] + '))')+"\n"

                    # Checking vloc of shape
                    if file1[3][firstPlace[j]] != file2[3][secondPlace[j]]:
                        moves.append(([file1[3][firstPlace[j]], file2[3][secondPlace[j]]],[file1[0][firstPlace[j]], file2[0][secondPlace[j]]]))
                        descript+=str('move(' + file1[3][firstPlace[j]] + '(' + file1[0][firstPlace[j]]+ '),' + file2[3][secondPlace[j]] + '(' + file2[0][secondPlace[j]] + '))')+"\n"

                    # Checking hloc of shape
                    if file1[4][firstPlace[j]] != file2[4][secondPlace[j]]:
                        moves.append(([file1[4][firstPlace[j]], file2[4][secondPlace[j]]],[file1[0][firstPlace[j]], file2[0][secondPlace[j]]]))
                        descript+=str('move(' + file1[4][firstPlace[j]] + '(' + file1[0][firstPlace[j]]+ '),' + file2[4][secondPlace[j]] + '(' + file2[0][secondPlace[j]] + '))')+"\n"

                    hrels = []
                    vrels = []
                    crels = []
                    for k in range(len(pairings)):
                        if k == j:
                            continue
                        #pairings[j] = (0 -> 0.)
                        #pairings[k] = (1 -> 1.)

                        # Check for addition/deletion
                        if firstPlace[k] == 'ADD':
                            continue
                        if secondPlace[k] == 'DEL':
                            continue

                        hrel1t = [l for l, x in enumerate(file1[5][firstPlace[j]]) if x == "left_of" or x == "right_of"]
                        hrel2t = [l for l, x in enumerate(file2[5][secondPlace[j]]) if x == "left_of" or x == "right_of"]
                        hrel1s = [l for l, x in enumerate(file1[6][firstPlace[j]]) if x == pairings[k][0]]
                        hrel2s = [l for l, x in enumerate(file2[6][secondPlace[j]]) if x == pairings[k][1]]
                        hrel1 = list(set(hrel1t).intersection(hrel1s))
                        hrel2 = list(set(hrel2t).intersection(hrel2s))
                        if len(hrel1) == len(hrel2):
                            if len(hrel1) != 0:
                                if file1[5][firstPlace[j]][hrel1[0]] != file2[5][secondPlace[j]][hrel2[0]]:
                                    hrels.append(([file1[5][firstPlace[j]][hrel1[0]], file2[5][secondPlace[j]][hrel2[0]]], [(pairings[j][0], pairings[k][0]), (pairings[j][1], pairings[k][1])]))
                                    if k > j:descript+=str('rel(' + file1[5][firstPlace[j]][hrel1[0]] + '(' + pairings[j][0] + ',' + pairings[k][0] + '),' + file2[5][secondPlace[j]][hrel2[0]] + '(' + pairings[j][1] + ',' + pairings[k][1] + '))')+"\n"
                        elif len(hrel1) == 0:
                            hrels.append((['sameh', file2[5][secondPlace[j]][hrel2[0]]], [(pairings[j][0], pairings[k][0]), (pairings[j][1], pairings[k][1])]))
                            if k > j:descript+=str('rel(sameh(' + pairings[j][0] + ',' + pairings[k][0] + '),' + file2[5][secondPlace[j]][hrel2[0]] + '(' + pairings[j][1] + ',' + pairings[k][1] + '))')+"\n"
                        else:
                            hrels.append(([file1[5][firstPlace[j]][hrel1[0]], 'sameh'], [(pairings[j][0], pairings[k][0]), (pairings[j][1], pairings[k][1])]))
                            if k > j:descript+=str('rel(' + file1[5][firstPlace[j]][hrel1[0]] + '(' + pairings[j][0] + ',' + pairings[k][0] + '),sameh(' + pairings[j][1] + ',' + pairings[k][1] + '))')+"\n"

                        vrel1t = [l for l, x in enumerate(file1[5][firstPlace[j]]) if x == "above" or x == "below"]
                        vrel2t = [l for l, x in enumerate(file2[5][secondPlace[j]]) if x == "above" or x == "below"]
                        vrel1s = [l for l, x in enumerate(file1[6][firstPlace[j]]) if x == pairings[k][0]]
                        vrel2s = [l for l, x in enumerate(file2[6][secondPlace[j]]) if x == pairings[k][1]]
                        vrel1 = list(set(vrel1t).intersection(vrel1s))
                        vrel2 = list(set(vrel2t).intersection(vrel2s))
                        if len(vrel1) == len(vrel2):
                            if len(vrel1) != 0:
                                if file1[5][firstPlace[j]][vrel1[0]] != file2[5][secondPlace[j]][vrel2[0]]:
                                    vrels.append(([file1[5][firstPlace[j]][vrel1[0]], file2[5][secondPlace[j]][vrel2[0]]], [(pairings[j][0], pairings[k][0]), (pairings[j][1], pairings[k][1])]))
                                    if k > j:descript+=str('rel(' + file1[5][firstPlace[j]][vrel1[0]] + '(' + pairings[j][0] + ',' + pairings[k][0] + '),' + file2[5][secondPlace[j]][vrel2[0]] + '(' + pairings[j][1] + ',' + pairings[k][1] + '))')+"\n"
                        elif len(vrel1) == 0:
                            vrels.append((['samev', file2[5][secondPlace[j]][vrel2[0]]], [(pairings[j][0], pairings[k][0]), (pairings[j][1], pairings[k][1])]))
                            if k > j:descript+=str('rel(samev(' + pairings[j][0] + ',' + pairings[k][0] + '),' + file2[5][secondPlace[j]][vrel2[0]] + '(' + pairings[j][1] + ',' + pairings[k][1] + '))')+"\n"
                        else:
                            vrels.append(([file1[5][firstPlace[j]][vrel1[0]], 'samev'], [(pairings[j][0], pairings[k][0]), (pairings[j][1], pairings[k][1])]))
                            if k > j:descript+=str('rel(' + file1[5][firstPlace[j]][vrel1[0]] + '(' + pairings[j][0] + ',' + pairings[k][0] + '),samev(' + pairings[j][1] + ',' + pairings[k][1] + '))')+"\n"

                        crel1t = [l for l, x in enumerate(file1[5][firstPlace[j]]) if x == "inside" or x == "overlap" or x == "contains"]
                        crel2t = [l for l, x in enumerate(file2[5][secondPlace[j]]) if x == "inside" or x == "overlap" or x == "contains"]
                        crel1s = [l for l, x in enumerate(file1[6][firstPlace[j]]) if x == pairings[k][0]]
                        crel2s = [l for l, x in enumerate(file2[6][secondPlace[j]]) if x == pairings[k][1]]
                        crel1 = list(set(crel1t).intersection(crel1s))
                        crel2 = list(set(crel2t).intersection(crel2s))
                        if len(crel1) == len(crel2):
                            if len(crel1) != 0:
                                if file1[5][firstPlace[j]][crel1[0]] != file2[5][secondPlace[j]][crel2[0]]:
                                    crels.append(([file1[5][firstPlace[j]][crel1[0]], file2[5][secondPlace[j]][crel2[0]]], [(pairings[j][0], pairings[k][0]), (pairings[j][1], pairings[k][1])]))
                                    if k > j:descript+=str('rel(' + file1[5][firstPlace[j]][crel1[0]] + '(' + pairings[j][0] + ',' + pairings[k][0] + '),' + file2[5][secondPlace[j]][crel2[0]] + '(' + pairings[j][1] + ',' + pairings[k][1] + '))')+"\n"
                        elif len(crel1) == 0:
                            crels.append((['norel', file2[5][secondPlace[j]][crel2[0]]], [(pairings[j][0], pairings[k][0]), (pairings[j][1], pairings[k][1])]))
                            if k > j:descript+=str('rel(norel(' + pairings[j][0] + ',' + pairings[k][0] + '),' + file2[5][secondPlace[j]][crel2[0]] + '(' + pairings[j][1] + ',' + pairings[k][1] + '))')+"\n"
                        else:
                            crels.append(([file1[5][firstPlace[j]][crel1[0]], 'norel'], [(pairings[j][0], pairings[k][0]), (pairings[j][1], pairings[k][1])]))
                            if k > j:descript+=str('rel(' + file1[5][firstPlace[j]][crel1[0]] + '(' + pairings[j][0] + ',' + pairings[k][0] + '),norel(' + pairings[j][1] + ',' + pairings[k][1] + '))')+"\n"
                    rels.append(hrels)
                    rels.append(vrels)
                    rels.append(crels)
                oneDescript.append(sizes)
                oneDescript.append(moves)
                oneDescript.append(rels)
                oneDescript.append(addDeletes)
                oneDescript.append(changes)
                interpret.append(oneDescript)
            word.append(descript)
            description.append(interpret)
        words.append(word)
        descriptions.append(description)
    return descriptions, words, filePairs

# -------------------------PARSING THE INPUT------------------------------------

A = []
B = []
C = []
K1 = []
K2 = []
K3 = []
K4 = []
K5 = []

Apath = []
Bpath = []
Cpath = []
K1path = []
K2path = []
K3path = []
K4path = []
K5path = []

outputFiles = glob.glob(outputFolder + '/*.txt') # gives a list of paths to all text files in inputFolder
for filePath in outputFiles:
    filePath = filePath.replace('\\','/') # in windows, glob returns path with '\\' instead of '/'
    fileform = re.split('/', filePath)
    fileform = list(filter(None, fileform))
    if (fileform[1][0] == 'A'):
        A.append(readFile(filePath))
        Apath.append(filePath)
    if (fileform[1][0] == 'B'):
        B.append(readFile(filePath))
        Bpath.append(filePath)
    if (fileform[1][0] == 'C'):
        C.append(readFile(filePath))
        Cpath.append(filePath)
    if (fileform[1][0:2] == 'K1'):
        K1.append(readFile(filePath))
        K1path.append(filePath)
    if (fileform[1][0:2] == 'K2'):
        K2.append(readFile(filePath))
        K2path.append(filePath)
    if (fileform[1][0:2] == 'K3'):
        K3.append(readFile(filePath))
        K3path.append(filePath)
    if (fileform[1][0:2] == 'K4'):
        K4.append(readFile(filePath))
        K4path.append(filePath)
    if (fileform[1][0:2] == 'K5'):
        K5.append(readFile(filePath))
        K5path.append(filePath)

Kpath = []
Kpath.append(K1path)
Kpath.append(K2path)
Kpath.append(K3path)
Kpath.append(K4path)
Kpath.append(K5path)
# -------------------------ACTUALLY DOING STUFF---------------------------------

AB = makePairs(A, B)
CK1 = makePairs(C, K1)
CK2 = makePairs(C, K2)
CK3 = makePairs(C, K3)
CK4 = makePairs(C, K4)
CK5 = makePairs(C, K5)

ABcost, ABword, ABpair = findMatches(AB, A, B)
CK1cost, CK1word, CK1pair = findMatches(CK1, C, K1)
CK2cost, CK2word, CK2pair = findMatches(CK2, C, K2)
CK3cost, CK3word, CK3pair = findMatches(CK3, C, K3)
CK4cost, CK4word, CK4pair = findMatches(CK4, C, K4)
CK5cost, CK5word, CK5pair = findMatches(CK5, C, K5)

totalCost = []
bestCost = 10000000
bestK = []
Ktransform = []
bothDescripts = []
ABpares = []
CKpares = []
bestComboChange = []
bestCombos = []
for i in range(len(ABcost)):
    for j in range(len(ABcost[i])):
        for s in range(1,6):
            CKlist = CK1cost
            CKword = CK1word
            CKpair = CK1pair
            if s == 1:
                CKlist = CK1cost
                CKword = CK1word
                CKpair = CK1pair
            if s == 2:
                CKlist = CK2cost
                CKword = CK2word
                CKpair = CK2pair
            if s == 3:
                CKlist = CK3cost
                CKword = CK3word
                CKpair = CK3pair
            if s == 4:
                CKlist = CK4cost
                CKword = CK4word
                CKpair = CK4pair
            if s == 5:
                CKlist = CK5cost
                CKword = CK5word
                CKpair = CK5pair
            for k in range(len(CKlist)):
                for l in range(len(CKlist[k])):
                    ABindex = []
                    CKindex = []
                    for m in range(len(ABcost[i][j][0])):
                        ABindex.append(m)
                    for n in range(len(CKlist[k][l][0])):
                        CKindex.append(n)

                    # Finding all the pairs of objects
                    combos = []
                    pairs = [zip(x,CKindex) for x in itertools.permutations(ABindex,len(CKindex))]
                    for pair in pairs:
                        combos.append(list(pair))

                    totalCost = 100000000
                    fileComboChange = []
                    bestFileCombo = []
                    combosTogether = []
                    for o in range(len(combos)):
                        oneCombo = []
                        oneComboChange = []
                        oneComboCost = 0
                        for q in range(len(combos[o])):
                            oneCombo.append([ABcost[i][j][0][combos[o][q][0]], CKlist[k][l][0][combos[o][q][1]]])
                            pair = combos[o][q]
                            for p in range(len(ABcost[i][j][pair[0]+1])):
                                if len(ABcost[i][j][pair[0]+1][p]) == len(CKlist[k][l][pair[1]+1][p]) and len(CKlist[k][l][pair[1]+1][p]) == 0:
                                    continue
                                elif len(ABcost[i][j][pair[0]+1][p]) == 0 or len(CKlist[k][l][pair[1]+1][p]) == 0:
                                    if len(ABcost[i][j][pair[0]+1][p]) > 0:
                                        for c in range(len(ABcost[i][j][pair[0]+1][p])):
                                            ABtemp = ABcost[i][j][pair[0]+1][p][c]
                                            if len(ABtemp) == 0:
                                                continue
                                            if ABtemp[0][0][0] == 'left_of' or ABtemp[0][0][0] == 'right_of' or ABtemp[0][0][0] == 'above' or ABtemp[0][0][0] == 'below' or ABtemp[0][0][0] == 'contains' or ABtemp[0][0][0] == 'inside' or ABtemp[0][0][0] == 'norel' or ABtemp[0][0][0] == 'overlap' or ABtemp[0][0][0] == 'samev' or ABtemp[0][0][0] == 'sameh':
                                                oneComboChange.append('delete(' +  ABtemp[0][0][0] + '(' + str(ABtemp[0][1][0]) + ') -> ' + ABtemp[0][0][1] + '(' + str(ABtemp[0][1][1]) + '))')
                                            else:
                                                oneComboChange.append('delete(' +  ABtemp[0][0] + '(' + str(ABtemp[1][0]) + ') -> ' + ABtemp[0][1] + '(' + str(ABtemp[1][1]) + '))')
                                    else:
                                        for c in range(len(CKlist[k][l][pair[1]+1][p])):
                                            ABtemp = CKlist[k][l][pair[1]+1][p][c]
                                            if len(ABtemp) == 0:
                                                continue
                                            if ABtemp[0][0][0] == 'left_of' or ABtemp[0][0][0] == 'right_of' or ABtemp[0][0][0] == 'above' or ABtemp[0][0][0] == 'below' or ABtemp[0][0][0] == 'contains' or ABtemp[0][0][0] == 'inside' or ABtemp[0][0][0] == 'norel' or ABtemp[0][0][0] == 'overlap' or ABtemp[0][0][0] == 'samev' or ABtemp[0][0][0] == 'sameh':
                                                oneComboChange.append('add(' +  ABtemp[0][0][0] + '(' + str(ABtemp[0][1][0]) + ') -> ' + ABtemp[0][0][1] + '(' + str(ABtemp[0][1][1]) + '))')
                                            else:
                                                oneComboChange.append('add(' +  ABtemp[0][0] + '(' + str(ABtemp[1][0]) + ') -> ' + ABtemp[0][1] + '(' + str(ABtemp[1][1]) + '))')
                                    oneComboCost += len(ABcost[i][j][pair[0]+1][p])*(10**p)
                                    oneComboCost += len(CKlist[k][l][pair[1]+1][p])*(10**p)
                                else:
                                    # shape change > add/del > rel > move > size
                                    if p == 4:
                                        if ABcost[i][j][pair[0]+1][p][0][0] != CKlist[k][l][pair[1]+1][p][0][0]:
                                            ABtemp = ABcost[i][j][pair[0]+1][p][0]
                                            CKtemp = CKlist[k][l][pair[1]+1][p][0]
                                            ABside1 = 0
                                            ABside2 = 0
                                            CKside1 = 0
                                            CKside2 = 0
                                            if ABtemp[0][0] not in shapesH or ABtemp[0][1] not in shapesH or CKtemp[0][0] not in shapesH or CKtemp[0][1] not in shapesH:
                                                oneComboCost += (10**(p+1))
                                            else:
                                                if ABtemp[0][0] == 'square' or ABtemp[0][0] == 'rectangle':
                                                    ABside1 = 4
                                                else:
                                                    ABside1 = shapesH.index(ABtemp[0][0])+3
                                                if ABtemp[0][1] == 'square' or ABtemp[0][1] == 'rectangle':
                                                    ABside1 = 4
                                                else:
                                                    ABside2 = shapesH.index(ABtemp[0][1])+3
                                                if CKtemp[0][0] == 'square' or CKtemp[0][0] == 'rectangle':
                                                    CKside1 = 4
                                                else:
                                                    CKside1 = shapesH.index(CKtemp[0][0])+3
                                                if CKtemp[0][1] == 'square' or CKtemp[0][1] == 'rectangle':
                                                    CKside2 = 4
                                                else:
                                                    CKside2 = shapesH.index(CKtemp[0][1])+3
                                                subtract = abs(abs(ABside1-ABside2) - abs(CKside1-CKside2)) + 1
                                                oneComboCost += subtract*(10**p)
                                            oneComboChange.append('change(' +  ABtemp[0][0] + '(' + ABtemp[1][0] + ') -> ' + ABtemp[0][1] + '(' + ABtemp[1][1] + '), '+  CKtemp[0][0] + '(' + CKtemp[1][0] + ') -> ' + CKtemp[0][1] + '(' + CKtemp[1][1] + '))')
                                    if p != 2:
                                        if ABcost[i][j][pair[0]+1][p][0][0] != CKlist[k][l][pair[1]+1][p][0][0]:
                                            oneComboCost += (10**p)
                                            ABtemp = ABcost[i][j][pair[0]+1][p][0]
                                            CKtemp = CKlist[k][l][pair[1]+1][p][0]
                                            oneComboChange.append('change(' +  ABtemp[0][0] + '(' + ABtemp[1][0] + ') -> ' + ABtemp[0][1] + '(' + ABtemp[1][1] + '), '+  CKtemp[0][0] + '(' + CKtemp[1][0] + ') -> ' + CKtemp[0][1] + '(' + CKtemp[1][1] + '))')
                                    else:
                                        for r in range(len(combos[o])):
                                            pair2 = combos[o][r]
                                            if q == r:
                                                continue
                                            else:
                                                ABcompair = ABcost[i][j][0][pair2[0]]
                                                CKcompair = CKlist[k][l][0][pair2[1]]
                                                for t in range(len(ABcost[i][j][pair[0]+1][p])):
                                                    size = 0
                                                    if len(ABcost[i][j][pair[0]+1][p][t]) > len(CKlist[k][l][pair[1]+1][p][t]):
                                                        size = len(ABcost[i][j][pair[0]+1][p][t])
                                                    else:
                                                        size = len(CKlist[k][l][pair[1]+1][p][t])
                                                    for a in range(len(ABcost[i][j][pair[0]+1][p][t])):
                                                        for b in range(len(CKlist[k][l][pair[1]+1][p][t])):
                                                            rel = ABcost[i][j][pair[0]+1][p][t][a]
                                                            rel1 = CKlist[k][l][pair[1]+1][p][t][b]
                                                            if rel[0] == rel1[0]:
                                                                if ABcompair[0] == rel[1][0][1] and ABcompair[1] == rel[1][1][1] and CKcompair[0] == rel1[1][0][1] and CKcompair[1] == rel1[1][1][1]:
                                                                    size -= 1
                                                            else:
                                                                if b > a:
                                                                    newstr = 'change(' + rel[0][0] + str(rel[1][0]) + ' -> ' + rel[0][1] + str(rel[1][1]) + ', ' + rel1[0][0] + str(rel1[1][0]) + ' -> ' + rel1[0][1] + str(rel1[1][1]) + ')'
                                                                    if newstr not in oneComboChange:
                                                                        oneComboChange.append('change(' + rel[0][0] + str(rel[1][0]) + ' -> ' + rel[0][1] + str(rel[1][1]) + ', ' + rel1[0][0] + str(rel1[1][0]) + ' -> ' + rel1[0][1] + str(rel1[1][1]) + ')')
                                                    oneComboCost += size*(10**p)
                        if oneComboCost < totalCost:
                            totalCost = oneComboCost
                            fileComboChange = oneComboChange[:]
                            bestFileCombo = oneCombo[:]

                    if totalCost < bestCost:
                        bestCost = totalCost
                        bestK.clear()
                        Ktransform.clear()
                        bothDescripts.clear()
                        ABpares.clear()
                        CKpares.clear()
                        bestComboChange.clear()
                        bestCombos.clear()
                        bestK.append(s)
                        Ktransform.append(ABcost[i][j][pair[0]+1])
                        bothDescripts.append([ABword[i][j], CKword[k][l]])
                        ABpares.append(ABpair[i])
                        CKpares.append(CKpair[k])
                        bestComboChange.append(fileComboChange)
                        bestCombos.append(bestFileCombo[:])
                    elif totalCost == bestCost:
                        bestK.append(s)
                        Ktransform.append(ABcost[i][j][pair[0]+1])
                        bothDescripts.append([ABword[i][j], CKword[k][l]])
                        ABpares.append(ABpair[i])
                        CKpares.append(CKpair[k])
                        bestComboChange.append(fileComboChange)
                        bestCombos.append(bestFileCombo[:])



useIndex = 0
if len(bestK) == 1:
    useIndex = 0
else:
    bestKtransform = 0
    bestCost = 100000
    for u in range(len(Ktransform)):
        Kcost = 0
        for t in range(len(Ktransform[u])):
            if t == 4:
                for s in range(len(Ktransform[u][t])):
                    if Ktransform[u][t][s][0][0] not in shapesH or Ktransform[u][t][s][0][1] not in shapesH:
                        Kcost += (10**(t+1))
                    else:
                        sides1 = 0
                        sides2 = 0
                        if Ktransform[u][t][s][0][0] == 'square' or Ktransform[u][t][s][0][0] == 'rectangle':
                            sides1 = 4
                        else:
                            sides1 = (shapesH.index(Ktransform[u][t][s][0][0])+3)
                        if Ktransform[u][t][s][0][1] == 'square' or Ktransform[u][t][s][0][1] == 'rectangle':
                            sides2 = 4
                        else:
                            sides2 = (shapesH.index(Ktransform[u][t][s][0][1])+3)
                        Kcost += (abs(sides1-sides2)+1)*(10**(t))
            elif t != 2:
                Kcost += (len(Ktransform[u][t])*(10**t))
            else:
                for v in range(len(Ktransform[u][t])):
                    Kcost += (len(Ktransform[u][t][v])*(10**t))
        if Kcost < bestCost:
            bestCost = Kcost
            bestKtransform = u
    useIndex = bestKtransform


print("K =", bestK[useIndex])

printInfo = False
if (printInfo):
    print('')

    Afile = Apath[ABpares[useIndex][0]]
    Bfile = Bpath[ABpares[useIndex][1]]

    print('A FILE OUTPUT')
    with open(Afile, 'r') as f:
            print(f.read())
    print('B FILE OUTPUT')
    with open(Bfile, 'r') as f:
            print(f.read())

    Cfile = Cpath[CKpares[useIndex][0]]
    Kfile = Kpath[bestK[useIndex]-1][CKpares[useIndex][1]]

    print('C FILE OUTPUT')
    with open(Cfile, 'r') as f:
            print(f.read())
    print('K' + str(bestK[useIndex]) + ' FILE OUTPUT')
    with open(Kfile, 'r') as f:
            print(f.read())

    print('TRANSFORMATION FROM A TO B')
    print(bothDescripts[useIndex][0])
    print('TRANSFORMATION FROM C TO K')
    print(bothDescripts[useIndex][1])

    print('TRANSFORMATION FROM AB TO CK')
    print(bestCombos[useIndex])
    for line in bestComboChange[useIndex]:
        print(line)

    print("\nK =", bestK[useIndex])

    print('\nIf you do not want to see extra information, go to line 625 and set printInfo to False\n')
#else:
    #print('\nIf you want to see extra information, go to line 625 and set printInfo to True\n')
