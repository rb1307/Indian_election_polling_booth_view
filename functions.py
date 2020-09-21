import logging
from difflib import get_close_matches
from collections import Counter
import jellyfish
import Errors


def setcolumnheaders(filetype='', dataframe=None):
    if filetype =='input_district':
        data_column_names =(dataframe.columns.tolist())
        column_nos = len(data_column_names)
        if column_nos == 4:
            new_column_names =['ac_no.', 'polling_station_no.', 'location', 'polling_areas']
            dataframe =rename_columns(old_headings=data_column_names, new_headings=new_column_names, data=dataframe)
            return  dataframe
        else:
            raise Errors.InputColumnError(file_type=filetype, input_col_numbers=column_nos, desired_col_numbers=4)


def rename_columns(old_headings=[], new_headings=[],data=None):
    col_rename_dict ={i: j for i, j in zip(old_headings, new_headings)}
    data.rename(columns=col_rename_dict, inplace=True)
    return data


def delete_null_rows(column_name=None, dataframe=None):
    if column_name is None:
        dataframe=dataframe.dropna()
    else:
        dataframe=dataframe[dataframe[column_name].notna()]
    return dataframe


def getacnos(data, district_name):
    data = data
    district_name = district_name
    ac_list = list(set(data['ac_no.'].tolist()))
    logging.info("The no of Assembly Constituents listed in district " + district_name + " is " + str(len(ac_list)) + "Assembly Constituencies are :" + str(ac_list).split("[")[-1].split("]")[0])
    return ac_list


def get_ac_data(input_data=None , ac_no=None):
    input_ac= ac_no
    data = input_data
    ac_data = data[data['ac_no.'] == input_ac]
    ac_data = ac_data.reset_index(drop=True)
    ac_data = cleaning(data=ac_data, column_name='polling_areas')
    logging.info("The number of polling booths with polling areas recorded in the data: " + str(len(ac_data)))
    return ac_data


def cleaning(data=None,column_name=None):
    # convert polling area to lower case and strip off extra spaces
    data[column_name] = data[column_name].str.lower().str.strip()
    # data[column_name] = data[column_name].lower().strip()
    return data


def get_total_null_value(data=None, col_name=''):
    data = data
    null = data.isnull().sum()
    total_null_values = null[col_name]
    return total_null_values


URBAN_REPR = ['(corp)', '(c)', '(corporation)']
NON_URBAN_REPR =['(r.v)', '(t.p)' ]


def extract_village(data=None,ac_no=None, village_identifer=None):
    ac_data = get_ac_data(input_data=data, ac_no=ac_no)
    ac_data['extracted_identifier'] = None
    urban_identification_count = 0
    for index, value in ac_data.iterrows():
        area = value['polling_areas']
        urban_flag = any(ur_repr in area for ur_repr in URBAN_REPR)
        if not urban_flag:
            try:
                village_name = area.split("1.")[-1].split("2.")[0].split(village_identifer)[0].strip()
                # can be subjected to change depending on the
            except:
                village_name = area.split("2")[0].split("1")[-1].split(village_identifer)[0].strip()
        else:
            urban_identification_count = urban_identification_count + 1
            village_name = None
        ac_data['extracted_identifier'][index] = village_name
    logging.info("The total number of polling area is "+str(len(ac_data))+".The total number of  urban and non_urban "
                "areas identified is " + str(urban_identification_count)+", "+ str(len(ac_data)
                                                                                   -urban_identification_count))

    return ac_data


WARD_IDENTIFIERS =['ward', 'w-', 'ward no.', 'ward number']


def get_ward_identifier(word=None,ident_list=[]):
    if word not in ident_list:
        ident_list.append(word)
    return ident_list


def extract_village_and_ward_numbers(district_data=None, input_ac=None, village_identifier=None, ward_identifier=None):
    data=extract_village(data=district_data, ac_no=input_ac, village_identifer=village_identifier)
    urban_extractor_count = 0
    data['ward_number'] = None
    for index, value in data.iterrows():
        if value['extracted_identifier'] is None:
            area = value['polling_areas']
            urban_repr = get_ward_identifier(word=ward_identifier, ident_list=WARD_IDENTIFIERS)
            urban_flag = any(ur_repr in area for ur_repr in urban_repr)
            if urban_flag:
                inp_str = area.split('1')[1].split("2.")[0].split(ward_identifier)[-1][:5]
            else:
                inp_str =area.split('1')[-1].split("2.")[0].split(ward_identifier)[-1][:5]
            ward_no=[]
            for char in inp_str:
                if char.isdigit():
                    ward_no.append(char)
                    ward_number=''.join(str(e) for e in ward_no)
                    data['ward_number'][index] = "Ward Number" + str(ward_number)
            urban_extractor_count = urban_extractor_count + 1
    return data


def get_list_of_villages(source_file=None, in_ac=None):
    data=source_file
    ac_data = data[data['AC No'] == in_ac]
    ac_data=ac_data.reset_index(drop=True)
    ac_data['Village.Name'] = ac_data['Village.Name'].str.lower().strip()
    villages = ac_data['Village.Name'].tolist()
    villages= remove_stopwords(villages=villages)
    villages_list=[]
    for item in villages:
        villages_list.append(item.split("(")[0].strip())
    logging.info("Ac no:" + str(in_ac) + ". The number of villages present in the ac from the source file is "
                 + str(len(villages_list)))
    return villages_list


STOPWORDS=['r.f', '(r.f)']
DIRECTIONS =['east', 'west', 'north', 'south']


def remove_stopwords(villages=[]):
    for item in villages:
        stop_words_flag = any(stop_word in item for stop_word in STOPWORDS  )
        if stop_words_flag:
            for s_w in STOPWORDS:
                updated_item = item.replace(s_w,'')
                villages.remove(item)
                villages.append(updated_item)
    return villages


# matching of villages using python difflib
def match_villages_1(ac_data=None,village_names=None):
    polling_areas_to_village = {}
    extracted_village_names = list(set(ac_data['extracted_identifier'].tolist()))
    org_village_list = village_names
    for item in org_village_list:
        inp = item.strip()
        poss = extracted_village_names
        matches = get_close_matches(inp, poss, 2, 0.70)

        if len(matches) > 1:
            for match in matches:
                polling_areas_to_village[match] = item
        elif len(matches) == 1:
            polling_areas_to_village[matches[0]] = item

    return polling_areas_to_village


def match_villages_2(ac_data=None, ac_bigrams={}):
    ac_data['mapped_identifier'] = None
    for index, value in ac_data.iterrows():
        extracted_identifier_name = value['extracted_identifier']
        extracted_identifier_name_word_list = extracted_identifier_name.split(" ")
        if len(extracted_identifier_name_word_list) > 2:
            extracted_identifier_name = ' '.join(extracted_identifier_name_word_list[:3])
        extracted_identifier_name =''.join(('$', extracted_identifier_name, '$'))
        identifier_bigram_list = create_bigram_list(word=extracted_identifier_name)
        matched_words =[]
        for each_bgram in identifier_bigram_list:
            matched_words.extend(ac_bigrams.get(each_bgram, []))
        matched_words_occurence = dict(Counter(matched_words))
        jacard_coff = {}
        for word, score in matched_words_occurence.items():
            jacard_coff[word] =get_jacob_index(word_1=word, word_2=extracted_identifier_name, union_score=score)
        if jacard_coff:
            jacard_coff =sorted(jacard_coff.items(), key=lambda kv: kv[1], reverse=True)[:6]
            ac_data['mapped_identifier'][index] = get_best_matched(query_word=extracted_identifier_name,
                                                               jacard_list=jacard_coff)
    return ac_data


def get_jacob_index(word_1, word_2, union_score):
    word1_length =len(word_1)
    word2_length = len(word_2)
    jacard_index = float(union_score/((word1_length + word2_length)-union_score))
    return jacard_index


def create_bigram_list(word):
    bigram_list=[]
    no_of_chars =len(word)
    for char_index in range(no_of_chars-1):
        bigram_list.append(word[char_index:char_index+2])
    return bigram_list


def get_best_matched(query_word='', jacard_list=None):
    index_value=jacard_list[0][1]
    word=jacard_list[0][0]
    if index_value>=0.40:
        return word.replace("$", '')
    elif 0.30 < index_value < 0.40:
        sound_query_word = jellyfish.soundex(query_word)
        sound_word = jellyfish.soundex(word)
        if sound_query_word[1:] == sound_word[1:]:
            return word.replace("$",'')
        else:
            return None
    else:
        return None