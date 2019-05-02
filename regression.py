#!/usr/bin/env python

import os
import argparse
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn import svm
import terroriser

def cleanString(string):
    return string.replace("/", "%2f")

def getUserArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('baseline', type=str,
                       help='branch name to compare against')
    parser.add_argument('branch', type=str,
                       help='branch name to find regressions in')

    return parser.parse_args()

# Main function for regression analysis
if __name__=="__main__":

    args = getUserArguments()

    comparisonBranch = cleanString(args.baseline)
    userBranch = cleanString(args.branch)

    loginVSImax = "http://rage/?p=som_data&id=512&xaxis=numvms&f_branch=1&v_branch=" + comparisonBranch + "&v_branch=" + userBranch + "&"
    passmarkCPUScore = "http://rage/?p_som_data&id=562&xaxis=branch&xaxis=build_number&xaxis=build_date&f_branch=1&v_branch=" + comparisonBranch + "&v_branch" + userBranch
    config = [0,0,0]
    try:
        # groupedX takes the form of an array of arrays
        # with each subarray being data of a particular branch
        groupedX, groupedY = terroriser.analyseData(loginVSImax, config, True)
        assert(len(groupedX) == len(groupedY))

    except TypeError:
        print("Invalid arguments (wrong branch name)")
        exit()
    except terroriser.TerroriserError as e:
        print("Terroriser failed")
        exit()

    print("len(groupedX)", len(groupedX))

    # format data for sklearn
    x = []; y = []
    for i in range(len(groupedX)):

        tmpX = []; tmpY = []
        lenX = len(groupedX[i]); lenY = len(groupedY[i])
        assert(lenX == lenY)
        for k in range(lenX):
            tmpX.append(groupedX[i][k][1])
            tmpY.append(groupedY[i][k][1])
        tmpX, tmpY = terroriser.order(tmpX, tmpY)

        x.append(tmpX); y.append(tmpY)

    # start finding linear regressions
    classifier = svm.SVR()

    learningData = np.asarray(x[0])
    targetValues = []

#    classifier.fit(learningData, targetValues)

