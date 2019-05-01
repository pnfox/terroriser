#!/usr/bin/env python

import os
from sklearn.linear_model import LinearRegression
import terroriser

# Main function for regression analysis
if __name__=="__main__":
    
    comparisonBranch = getComparisonBranch()
    branch = getUserBranch()
    
    loginVSImax = "http://rage/?som=512&xaxis=numvms&f_branch=1&v_branch=" + comparisonBranch "&v_branch=" + userBranch
    config = [0,0]
    terroriser.analyseData(loginVSImax, config)
