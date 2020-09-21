import pandas as pd
import logging
import Errors
import json


def read_excel(path=None, file_name=None, sheet=None):

    # HAVE TO SPECIFY SHEET NAME CONDITION
    pd_df=pd.read_excel(path+file_name, sheet_name=sheet)
    cols=list(pd_df.columns)
    logging.info("Reading File : " + str(file_name) + " , sheet_name :" + str(sheet)+" ......")
    logging.info("The number of cols in the excel file is " + str(len(cols)) + "\nColumns are " +
                 ','.join(cols))

    return pd_df


def read_csv(path=None, file_name=None):

    pd_df=pd.read_csv(path + file_name)
    cols=pd_df.columns()
    logging.info("Reading File : " + str(file_name.split("/")[-1]) + " ......")
    logging.info("The number of cols in the excel file is " + str(len(cols)) + "\nColumns are " +
                 ','.join(cols))

    return pd_df


def read_json(path=None, json_file=None):
    if path is not None :
        with open(path + json_file, mode='r') as f:
            data=json.load(f)
        return data
    else:
        with open(json_file, mode='r') as f:
            data=json.load(f)
        return data


