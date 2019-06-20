#!/usr/bin/env python

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn import svm
from sklearn import preprocessing
import terroriser

#degug
import code

def cleanString(string):
    return string.replace("/", "%2F")

def getUserArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('branch', type=str,
                       help='branch name to find regressions in')
    parser.add_argument('--branch2', type=str,
                        help='branch name to compare performance results with')

    return parser.parse_args()

def ordinalEncode(data):

    encoder = preprocessing.OrdinalEncoder()
    encodedData = encoder.fit_transform(data)

    return encodedData

# Used on arrays which store all point information
# including branch, build_date, ...
#
# sklearn doesnt understand strings so we turn
# these into integers such that all information is grouped
# e.g. if we have data from master and ely
# we turn master strings into 0 and ely into value 1 etc...
def preprocessData(data):

    newData = []
    tmp = []

    for i in data:
        tmp.append(i[3:])
    tmp = ordinalEncode(tmp)
    assert len(tmp) == len(data)

    entry = []
    for i in range(len(data)):
        entry = [data[i][0], data[i][1], data[i][2]] + list(tmp[i])
        newData.append(entry)

    return newData

def numpyData(t, points):
    groupdX, groupedY, labels = t.groupData()

    # format data for sklearn
    x = []; y = []
    for i in range(len(groupedX)):

        tmpX = []; tmpY = []
        lenX = len(groupedX[i]); lenY = len(groupedY[i])
        assert(lenX == lenY)
        for k in range(lenX):
            # pointID is at groupedX[i][k][0]
            tmpX.append(groupedX[i][k][1])
            tmpY.append(groupedY[i][k][1])
        tmpX, tmpY = terroriser.order(tmpX, tmpY)

        x.append(np.asarray(tmpX)); y.append(np.asarray(tmpY))
        varX = np.var(tmpX)
        varY = np.var(tmpY)
        # TODO: Maybe this should be varX / meanX ?
        if varX < 0.4:
            print("WARNING: low variance on X " + str(varX))
            print("X axis doesn't provide a lot of information on " + labels[i])
        if varY < 0.4:
            print("WARNING: low variance on Y " + str(varY))
            print("Y axis doesn't provide a lot of information on " + labels[i])

def findRegression(url):
    config = [1,1,0,0,0,0]

    t = Terroriser()
    t.config = config
    t.url = url
    try:
        p = t.getData(True)
    except TypeError:
        print("Invalid arguments")
        exit()
    except terroriser.TerroriserError as e:
        print("Terroriser failed")

    code.interact(local=locals())

# Main function for regression analysis
if __name__=="__main__":

    args = getUserArguments()

    comparisonBranch = cleanString(args.branch)
    userBranch = ""
    if args.branch2:
        userBranch = cleanString(args.branch2)

    loginVSImax = "http://rage/?p=som_data&id=33&xaxis=numvms&f_branch=1&v_branch=" + comparisonBranch + "&v_branch=" + userBranch + "&"
    passmarkCPUScore = "http://rage/?p=som_data&id=562&xaxis=branch&xaxis=build_number&xaxis=build_date&f_branch=1&v_branch=" + comparisonBranch + "&v_branch" + userBranch
    passmarkDiskMark = "http://rage/?p=som_data&id=565&xaxis=branch&xaxis=build_number&xaxis=build_date&auto_redraw=on&v_product=XenServer&v_product=XenServer-Transformer&f_branch=1" \
        "&v_branch=" + comparisonBranch + "&v_branch=" + userBranch + "&v_build_tag=all_hotfixes" \
        "&v_build_tag=all_hotfixes%2Chttp%3A%2F%2Fcoltrane.uk.xensource.com%2Fusr%2Fgroups%2Fbuild" \
        "%2Fdundee-lcm%2F513036%2Fhotfix-XS70E068%2FXS70E068.xsupdate%2Chttps%3A%2F%2Frepo.citrite.net" \
        "%2Fxs-local-release-candidate%2FXenServer-7.x%2FXS-7.6%2Fupdates%2FXS76E004-UPD-484%2F24%2FXS76E004.iso" \
        "%2Chttps%3A%2F%2Frepo.citrite.net%2Fxs-local-release-candidate%2FXenServer-7.x%2FXS-7.1.2%2Fupdates" \
        "%2FXS71ECU2008-UPD-482%2F48%2FXS71ECU2008.iso%2Chttps%3A%2F%2Frepo.citrite.net%2Fxs-local-release-candidate" \
        "%2FXenServer-8.x%2FXS-8.0%2Fupdates%2FXS80E001-UPD-483%2F21%2FXS80E001.iso&v_build_tag=all_hotfixes" \
        "%2Cmandiant_installed%2Chttps%3A%2F%2Frepo.citrite.net%2Flist%2Fxs-local-assembly%2Fxenserver%2Frelease" \
        "%2Fhavana%2FUPD-482%2F41%2FXS71ECU2008.iso&v_distro=win10-x64&v_vm_ram=8192&v_vcpus=4&v_postinstall=installDrivers"
    durationOfNthVMClone = "http://rage/?p=som_data&id=266&xaxix=branch&xaxis=build_date&f_branch=1&f_build_date=1&v_branch=" + comparisonBranch + "&v_branch=" + userBranch + "&"
    simpleSyscall = "http://rage/?p=som_data&id=41&xaxis=branch&xaxis=build_number&xaxis=build_date&v_branch=" \
        + comparisonBranch + "&v_branch=" + userBranch + "&v_arch=x86-64&v_vmvcpus=2&f_vmvcpus=1"

    findRegression(simpleSyscall)

