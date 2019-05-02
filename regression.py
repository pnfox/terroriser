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
    userBranch = args.branch

    loginVSImax = "http://rage/?p=som_data&id=512&xaxis=numvms&f_branch=1&v_branch=" + comparisonBranch + "&v_branch=" + userBranch
    passmarkCPUScore = "http://rage/?p_som_data&id=562&xaxis=branch&xaxis=build_number&xaxis=build_date&f_branch=1&v_branch=" + comparisonBranch + "&v_branch" + userBranch
    config = [0,0,0]
    try:
        x, y = terroriser.analyseData(loginVSImax, config, True)
    except TypeError:
        print("Invalid arguments (wrong branch name)")
        exit()
    except terroriser.TerroriserError as e:
        print("Terroriser failed")
        exit()

    # start finding linear regressions
    
