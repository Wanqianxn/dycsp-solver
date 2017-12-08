from collections import deque

# Format dictionaries to write to an output file.
def writeDict(file, dict, dictName):
    file.write(dictName + ": \n")
    for key, values in dict.items():
        file.write(str(key) + ": " + str(values) + "\n")
    file.write("\n")

# Class functionality for a dynamic CSP.
class DyCSP:

    def __init__(self, N, D, C, maxT, file):
        self.variables = [i for i in range(1, N + 1)]
        self.domains = D
        self.allConstraints = C
        self.currentConstraints = dict()
        self.time = 0
        self.maxTime = maxT
        self.file = file

        self.supportSet = dict()
        self.justif = dict()
        self.D = dict()

        for i in self.variables:
            self.D[i] = set()
            for j in self.domains[i]:
                self.D[i].add(j)
                self.justif[(i, j)] = None

        self.file.write("---CSP Parameters---\n\n")
        self.file.write("Variables: " + str(self.variables) + "\n\n")
        writeDict(self.file, self.domains, "Domains")

    def solveCSP(self):
        while self.time <= self.maxTime:
            self.file.write("---Time: t = " + str(self.time) + "---\n\n")
            if self.time in self.allConstraints:
                for key, value in self.allConstraints[self.time].items():
                    if value[0] == 'a':
                        i, j = key
                        if (i, j) not in self.currentConstraints:
                            self.addConstraint(key, self.time)
                    else:
                        self.relaxConstraint(key)
                self.getValidAssignments()
                assn = self.backtrackingSearch()
                if assn == None:
                    self.file.write("\n" + "No possible assignment returned from backtracking search.\n\n")
                else:
                    self.file.write("Complete assignment from backtracking search:\n")
                    for varAss in assn[1:]:
                        self.file.write(str(varAss[0]) + ": " + str(varAss[1]) + "\n")
                    self.file.write("\n")
            self.time += 1

    def addConstraint(self, key, t):
        i, j = key
        self.currentConstraints[(i, j)] = self.allConstraints[t][(i, j)][1]
        self.currentConstraints[(j, i)] = self.allConstraints[t][(j, i)][1]
        self.file.write("Adding constraint " + str(key) + "...\n")

        supList = deque()
        supList = self.begAdd(i, j, supList)
        supList = self.begAdd(j, i, supList)
        self.propagSuppress(supList)

    def relaxConstraint(self, key):
        self.file.write("Relaxing constraint " + str(key) + "...\n")
        k, m = key
        supList = deque()
        supList = self.initPropagRelax(k, m, supList)
        self.propagSuppress(supList)

    def getValidAssignments(self):
        self.file.write("\n")
        self.file.write("Valid values after arc consistency check:\n")
        for key, value in sorted(self.D.items(), key=lambda x: x[0]):
            self.file.write(str(key) + ": " + ', '.join(value) + "\n")
        self.file.write("\n")

    def backtrackingSearch(self):
        frontier = deque()
        frontier.append([(0, None)])
        while frontier:
            assn = frontier.pop()
            next = len(assn)
            if next > len(self.variables):
                return assn
            elif next not in self.D:
                return None
            for v in self.D[next]:
                isValid = True
                for y in assn[1:]:
                  if (y[0], next) in self.currentConstraints:
                      if (y[1], v) not in self.currentConstraints[(y[0], next)]:
                          isValid = False
                          continue
                if isValid:
                    frontier.append(assn + [(next, v)])
        return None


# DnAC-4 algorithm for arc consistency by Christian Bessiere.
# http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.107.2229&rep=rep1&type=pdf
class DnAC4(DyCSP):

    def __init__(self, N, D, C, maxT, file):
        DyCSP.__init__(self, N, D, C, maxT, file)
        self.counter = dict()

        self.file.write("Dynamic arc consistency algorithm used: DnAC-4\n\n")

    def begAdd(self, i, j, SL):
        for b in self.domains[j]:
            self.supportSet[(j,i,b)] = set()
        for a in self.domains[i]:
            total = 0
            for b in self.domains[j]:
                if (a, b) in self.currentConstraints[(i, j)]:
                    if b in self.D[j]:
                        total += 1
                    self.supportSet[(j,i,b)].add(a)
            self.counter[((i, j), a)] = total
            if self.counter[((i, j), a)] == 0:
                SL.append(((i, j), a))
        return SL

    def propagSuppress(self, SL):
        while SL:
            (i, m), a = SL.pop()
            if a in self.D[i] and self.counter[((i, m), a)] == 0:
                self.justif[(i, a)] = m
                self.D[i].remove(a)
                for x, j in self.currentConstraints.keys():
                    if x == i:
                        if (i,j,a) in self.supportSet:
                            for b in self.supportSet[(i, j, a)]:
                                self.counter[((j, i), b)] -= 1
                                if self.counter[((j, i), b)] == 0:
                                    SL.append(((j, i), b))

    def initPropagRelax(self, k, m, SL):
        RL = deque()
        for a in self.domains[k]:
            if self.justif[(k, a)] == m:
                RL.append((k, a))
                self.justif[(k, a)] = None
            del self.counter[((k, m), a)]
            del self.supportSet[(k,m,a)]
        for b in self.domains[m]:
            if self.justif[(m, b)] == k:
                RL.append((m, b))
                self.justif[(m, b)] = None
            del self.counter[((m, k), b)]
            del self.supportSet[(m,k,b)]
        del self.currentConstraints[(k, m)]
        del self.currentConstraints[(m, k)]

        while RL:
            i, a = RL.popleft()
            self.D[i].add(a)
            for x, j in self.currentConstraints.keys():
                if x == i:
                    for b in self.supportSet[(i,j,a)]:
                        self.counter[((j, i), b)] += 1
                        if self.justif[(j, b)] == i:
                            RL.append((j, b))
                            self.justif[(j, b)] = None
                    if self.counter[((i, j), a)] == 0:
                        SL.append(((i, j), a))

        return SL


# DnAC-6 algorithm for arc consistency by Romuald Debruyne.
# http://ieeexplore.ieee.org.ezp-prod1.hul.harvard.edu/stamp/stamp.jsp?arnumber=560467
class DnAC6(DyCSP):

    def __init__(self, N, D, C, maxT, file):
        DyCSP.__init__(self, N, D, C, maxT, file)

        self.absent = dict()
        self.present = dict()
        for k in self.variables:
            self.present[k] = list(self.D[k])
            self.absent[k] = list(set(self.domains[k]).difference(self.D[k]))

        self.file.write("Dynamic arc consistency algorithm used: DnAC-6\n\n")

    def next(self, i, a):
        if a in self.present[i]:
            index = self.present[i].index(a)
            if index < len(self.present[i]) - 1:
                return self.present[i][index + 1]
        return None

    def firstLast(self, i, order):
        if self.present[i]:
            if order == "first":
                return self.present[i][0]
            else:
                return self.present[i][-1]
        return None

    def nextSupport(self, i, j, a, b):
        while b != None:
            if (a, b) in self.currentConstraints[(i, j)]:
                if (j,i,b) not in self.supportSet:
                    self.supportSet[(j,i,b)] = set()
                self.supportSet[(j,i,b)].add(a)
                return True
            else:
              b = self.next(j, b)
        return False

    def begAdd(self, i, j, SL):
        for b in self.present[j]:
            self.supportSet[(j,i,b)] = set()
        for a in self.present[i]:
            supported = self.nextSupport(i, j, a, self.firstLast(j, "first"))
            if not supported:
                SL.append([i, j, a, False, None])
        return SL

    def propagSuppress(self, SL):
        while SL:
            i, j, a, pOfSupport, lastTested = SL.pop()
            if a in self.D[i]:
                supported = False
                if pOfSupport:
                    if lastTested != None:
                        b = self.next(j, lastTested)
                    else:
                        b = self.firstLast(j, "first")
                    supported = self.nextSupport(i, j, a, b)
                if not supported:
                    for k, x in self.currentConstraints.keys():
                        if x == i and (i,k,a) in self.supportSet:
                            for b in self.supportSet[(i,k,a)].intersection(self.D[k]):
                                support = self.nextSupport(k, i, b, self.next(i, a))
                                if not support:
                                    SL.append([k, i, b, False, None])
                            self.supportSet[(i,k,a)] = set()
                    if a in self.present[i]:
                        self.D[i].remove(a)
                        self.present[i].remove(a)
                        if self.absent:
                            self.absent[i].append(a)
                    self.justif[(i, a)] = j

    def initPropagRelax(self, k, m, SL):
        RL = deque()
        for a in self.absent[k]:
            if self.justif[(k, a)] == m:
                RL.append([k, m, a])
                self.justif[(k, a)] = None
                del self.supportSet[(k,m,a)]
        for b in self.absent[m]:
            if self.justif[(m, b)] == k:
                RL.append([m, k, b])
                self.justif[(m, b)] = None
                del self.supportSet[(m,k,b)]
        del self.currentConstraints[(k, m)]
        del self.currentConstraints[(m, k)]

        while RL:
            i, k, a = RL.popleft()
            if a in self.absent[i]:
                self.D[i].add(a)
                self.absent[i].remove(a)
                self.present[i].append(a)
            for x, j in self.currentConstraints.keys():
                if x == i and j != k:
                    supported = self.nextSupport(i, j, a, self.firstLast(j, "first"))
                    for c in self.absent[j]:
                        if self.justif[(j, c)] == i:
                            if (a, c) in self.currentConstraints[(i, j)]:
                                self.justif[(j, c)] = None
                                RL.append([j, i, c])
                                if (i,j,a) not in self.supportSet:
                                    self.supportSet[(i,j,a)] = set()
                                self.supportSet[(i,j,a)].add(c)
                    if not supported:
                        SL.append([i, j, a, True, self.firstLast(j, "last")])

        return SL
