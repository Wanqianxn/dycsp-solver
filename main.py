'''
Dynamic Constraint Satisfaction Problem (DyCSP) solver, using DnAC-4 and DnAC-6
algorithms for arc-consistency, coupled with classical backtracking search.

'''

import sys, argparse, time
from dyCSPAgent import *
#from memory_profiler import profile

#@profile
def main():
    parser = argparse.ArgumentParser(description='Solve a dynamic CSP.')
    parser.add_argument('input', help='input file')
    parser.add_argument('output', help='output file')
    parser.add_argument('--a', nargs='?', const='dnac4', default='dnac4', help='select arc consistency algorithm')
    parseArgs = parser.parse_args()

    infile = open(parseArgs.input, 'r')
    outfile = open(parseArgs.output, 'w')

    # Parse input file.
    N, D, C = 0, dict(), dict()
    for i, line in enumerate(infile):
        line = line.strip("\n")
        if i == 0:
            N = int(line)
        else:
            domain = [x for x in line.split()]
            if domain[0].isdigit():
                D[int(domain[0])] = domain[1:]
            else:
                t, i, j = int(domain[1]), int(domain[3]), int(domain[4])
                if t not in C:
                    C[t] = dict()
                if domain[2] == 'r':
                    C[t][(i, j)] = (domain[2], None)
                else:
                    validPairs1, validPairs2 = set(), set()
                    for k in range(5, len(domain) - 1, 2):
                        validPairs1.add((domain[k], domain[k+1]))
                        validPairs2.add((domain[k+1], domain[k]))
                    C[t][(i, j)] = (domain[2], validPairs1)
                    C[t][(j, i)] = (domain[2], validPairs2)
    infile.close()
    maxT = max(C.keys())

    # Run dynamic CSP agent and print to output file.
    start = time.time()
    if parseArgs.a == 'dnac4':
        dycsp = DnAC4(N, D, C, maxT, outfile)
    else:
        dycsp = DnAC6(N, D, C, maxT, outfile)
    dycsp.solveCSP()
    end = time.time()

    outfile.write("\n\n")
    outfile.write("Start time: " + str(start) + "\n")
    outfile.write("End time: " + str(end) + "\n")
    outfile.write("Time elapsed: " + str((end - start)) + "\n")
    outfile.close()


if __name__ == '__main__':
    main()
