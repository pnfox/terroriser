#!/usr/bin/env python

import os
import argparse
from sklearn.linear_model import LinearRegression
import terroriser

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

    comparisonBranch = args.baseline
    branch = args.branch

    loginVSImax = "http://rage/?som=512&xaxis=numvms&f_branch=1&v_branch=" + comparisonBranch "&v_branch=" + userBranch
    config = [0,0]
    terroriser.analyseData(loginVSImax, config)
