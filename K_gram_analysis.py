"""
@Romit Bhattacharyya
Uses bi-gram overlap analysis to create the input file to find closely matched words from database

Input_file 
"""


import pandas as pd
import logging
import input
import functions
from collections import Counter
import Errors
import json
import configargparse
logging.root.setLevel(logging.NOTSET)


class Kgram_Analysis():
    def __init__(self):
        parser = configargparse.ArgParser()
        parser.add_argument('-c', '--config_file', required=True, is_config_file = True, help= "This is the name of the config file.")
        parser.add_argument('--io_storage_path', required=False, type= str, 
        help = "Provide the path to the storage directory. e.g : Romit/Home/C/Election_work/")
        parser.add_argument("--input_data_type", required=False, type=str, help = ' The extension of the file. Currently this version supports only excel and csv. ')
        parser.add_argument('--state_village_input_file_name', required=False, type=str, help = "File name containing all villages and its details in the state.")
        parser.add_argument('--village_column_identifier', required=False, help = "The column name with all the villages in the file : state_village_input_file_name")
        parser.add_argument('--ac_column_identifier', required=False, help="The column with the ac_numbers in the file : state_village_input_file_name")
        parser.add_argument('--output_file_name', required=False, help = 'Name of the file where bigrams to villages are mapped.')
        self.params = parser.parse_args()

    def get_input_data(self):
        input_type =self.params.input_data_type
        if input_type =='csv':
            data=input.read_csv(path=self.params.io_storage_path, file_name=self.params.state_village_input_file_name)
        elif input_type =='excel':
            data=input.read_excel(path=self.params.io_storage_path, file_name=self.params.state_village_input_file_name, sheet ='TN')
        else :
            raise Errors.InputTypeError()
        return data

    def villagetobigrams(self):
        """
        function : to obtain the bigrams from village names in each ac
        """
        data=self.get_input_data()
        village_column_identifier = self.params.village_column_identifier
        ac_column_identifier = self.params.ac_column_identifier
        presentacs=list(set(data[ac_column_identifier].tolist()))
        ac_response = {}
        for ac_no in presentacs:
            ac_data=data[data[ac_column_identifier]==ac_no].reset_index(drop=True)
            ac_data=functions.cleaning(data=ac_data,column_name=village_column_identifier)
            villages = list(set(ac_data[village_column_identifier].tolist()))
            details={}
            for village in villages:
                village = ''.join(('$',village,'$'))
                word=[]
                # create the bigrams of each villages
                for items in range(len(village)-1):
                    bgrams=village[items:items+2]
                    word.append(bgrams)
                details[village] = word
            ac_response[ac_no] = details
        return ac_response

    def getfinalstructure(self):
        """
        function : to create the final structure of strong the village names mapped to a bigram per ac. 
        """
        data=self.villagetobigrams()
        final_response = {}
        for ac_no,details in data.items():
            bigram_list = []
            for village,bigr in details.items():
                bigram_list.extend(bigr)
            bigram_list=list(set(bigram_list))
            bigramtovillagemappings = {}
            for bigram in bigram_list:
                inclusion_list=[]
                for v, b in details.items():
                    if bigram in b:
                        inclusion_list.append(v)
                bigramtovillagemappings[bigram] = inclusion_list
            #if bigramtovillagemappings is None:
            #    raise Errors.NoneTypeError(variable='bigramtovillagemappings')
            #else:
            final_response[ac_no] = bigramtovillagemappings
        return final_response

    def outputjson(self):
        response = self.getfinalstructure()
        with open(self.params.io_storage_path + self.params.output_file_name,mode='w' ) as output:
            json.dump(response, output)


if __name__ == '__main__':
    # config_file = input.read_json(path = 0, json_file='TN_K_gram_analysis_config_file.json')
    class_obj =  Kgram_Analysis()
    class_obj.outputjson()




