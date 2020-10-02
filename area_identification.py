"""
The script :takes in input polling area data and aggregate all polling booths to find village/ward data.
           : works for both mapped and unmapped data
           :uses k_gram analysis and jacobian index to find the closely matched word
Inputs : 1. District Data of polling area
         2. Village list of District
         3. Polling booth result of previous years.  

"""

import logging
import input
import functions
import pandas as pd
import Errors
import json


logging.basicConfig(level=logging.INFO)


class MapVillageNames:
    def __init__(self, **kwargs):
        self.params={}
        self.params.update(kwargs)
        self.PATH = self.params.get("state_file_path")

    def getinputdata(self):
        mapped_flag = self.params.get("mapped_flag")
        if mapped_flag ==1:
            logging.info("Input data :" + self.params.get("district_file") + " is mapped for the years " +
                         ','.join(self.params.get("years")))
            # call mapped_file_function
        else:
            logging.warning("Unmapped data. Need to extract villages from the years " +
                            ','.join(self.params.get("years")) + " seperately.")
            # call_unmapped_file_function

    def getvillagesorwards(self):
        input_file_type = self.params.get("input_file_type")
        if input_file_type == 'excel':
            data = input.read_excel(path=self.PATH+ self.params.get("district") + "/", file_name=self.params.get("district_file"), sheet=self.params
                                    .get("election_years")[-1])
        elif input_file_type == 'csv':
            data = input.read_csv(path=self.PATH+ self.params.get("district") + "/", file_name=self.params.get("district_file"))
        else:
            raise Errors.EmptyInputError
        data = functions.setcolumnheaders(filetype='input_district', dataframe=data)
        data = functions.delete_null_rows(column_name='ac_no.', dataframe=data)
        assemblies = functions.getacnos(data=data, district_name=self.params.get("district"))
        #logging.info("The assembly constitutions in the district : " + self.params.get(""))
        district_response =pd.DataFrame()
        bigram_to_village_data = input.read_json(path=self.PATH, json_file=self.params.get("bigram_match_file"))
        for assembly in assemblies:
            logging.info("Assembly Constitution Number : " + str(assembly))
            extracted_data = functions.extract_village_and_ward_numbers(district_data=data,input_ac=assembly,
                                                            village_identifier=self.params.get("village_identifier"),
                                                            ward_identifier=self.params.get("ward_identifier"))
            if self.params.get("match_type") =='difflib':
                village_list_data = functions.get_list_of_villages(source_file=self.params.get("village_file"),
                                                               in_ac=assembly)
                ac_response=None
            elif self.params.get("match_type") == 'bigram':
                ac_bigrams =bigram_to_village_data.get(str(int(assembly)))
                if ac_bigrams is not None:
                    ac_response =functions.match_villages_2(ac_data=extracted_data, ac_bigrams=ac_bigrams)
                    frames = [district_response, ac_response]
                    district_response = pd.concat(frames)
            else:
                raise Errors.MatchTypeError()

        return district_response

    def output_excel(self):
        district_response = self.getvillagesorwards()
        path=self.PATH+ "/" + self.params.get("district") + "/"
        file_name=path + self.params.get("district") + "_" + self.params.get("output_file") + ".xlsx"
        district_response.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        district_response.to_excel(file_name, index=False, index_label=False)


if __name__ == '__main__':
    config_dict = input.read_json(json_file="input_config.json")
    state_object = MapVillageNames(**config_dict)
    state_object.output_excel()