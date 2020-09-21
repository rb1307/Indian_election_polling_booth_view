import pandas as pd
import logging
import input
import functions
from collections import Counter
import Errors
import json
logging.root.setLevel(logging.NOTSET)


class CreateBigramAnalysisInput():
    def __init__(self, **kwargs):
        self.params={}
        self.params.update(kwargs)

    def get_input_data(self):
        input_type =self.params.get('input_data_type')
        if input_type =='csv':
            data=input.read_csv(path=self.params.get("config_file_path"), file_name=self.params.get("file_name"))
        else:
            data=input.read_excel(path=self.params.get("config_file_path"), file_name=self.params.get("file_name"))
        return data

    def getkgramvillagefile(self):
        data=self.get_input_data()
        village_column_identifier = self.params.get("village_column_identifier")
        ac_column_identifier = self.params.get("ac_column_identifier")
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
                for items in range(len(village)-1):
                    bgrams=village[items:items+2]
                    word.append(bgrams)
                details[village] = word
            ac_response[ac_no] = details
        return ac_response

    def getfinalstructure(self):
        data=self.getkgramvillagefile()
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
        with open(self.params.get("folder_path") + self.params.get("output_file_name"),mode='w' ) as output:
            json.dump(response, output)


if __name__ == '__main__':
    config_file = input.read_json(path = 0 , json_file='TN_K_gram_analysis_config_file.json')
    class_obj =  CreateBigramAnalysisInput(**config_file)
    class_obj.outputjson()




