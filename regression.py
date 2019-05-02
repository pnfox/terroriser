#!/usr/bin/env python

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
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

    loginVSImax = "http://rage/?p=som_data&id=33&xaxis=numvms&f_branch=1&v_branch=" + comparisonBranch + "&v_branch=" + userBranch + "&"
    passmarkCPUScore = "http://rage/?p_som_data&id=562&xaxis=branch&xaxis=build_number&xaxis=build_date&f_branch=1&v_branch=" + comparisonBranch + "&v_branch" + userBranch
    config = [0,0,0]
    try:
        # groupedX takes the form of an array of arrays
        # with each subarray being data of a particular branch
        print("Getting data...")
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

    X = []
    for i in range(len(x[0])):
        X.append([x[0][i], y[0][i]])

    X = np.asarray(X)
    Y = np.dot(X, np.array([1,2])) + 3

    print("Training data...")
    reg = LinearRegression().fit(X, Y)
    reg.score(X, Y)

    branchData = []
    print(len(x[1]))
    for i in range(len(x[1])):
        branchData.append([x[1][i], y[1][i]])
    branchData = np.asarray(branchData)
    Y = np.dot(branchData, np.array([1,2])) + 3

    print(" Make predictions useing the testing set...")
    data = reg.predict(branchData)
    print(data)
    print(reg.score(branchData, Y))

#    print("Mean squared error: %.2f" % mean_squared_error(y[1], y[0]))

#    classifier.fit(learningData, targetValues)

#    plt.scatter(x[1], Y)

    yvalues = []
    for i in range(len(data)):
        yvalues.append(i)
    plt.scatter(data, yvalues)
    plt.show()
