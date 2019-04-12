import pandas as pd 
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from collections import OrderedDict


np.random.seed(0)

#Change directory to your own that leads to the core-set folder
directory = "/Users/brandonzhang/Desktop/Lionbase_Material/Data/core-set"

borough_labels = "sub_borough_labels_2015.csv"

puma_labels = "sub_borough_puma.csv"

datafiles = ["/affordability/sub-borougharea-rentalunitsaffordableat30amiofrecentlyavailableunits.csv",
			 "/affordability/sub-borougharea-rentalunitsaffordableat80amiofrecentlyavailableunits.csv",
			 "/affordability/sub-borougharea-rentalunitsaffordableat120amiofrecentlyavailableunits.csv",
			 "/households/sub-borougharea-householdswithchildrenunder18yearsold.csv",
			 "/households/sub-borougharea-single-personhouseholds.csv",
			 "/labor_market/sub-borougharea-unemploymentrate.csv",
			 "/income_poverty/sub-borougharea-medianhouseholdincomehomeowners2017.csv",
			 "/income_poverty/sub-borougharea-medianhouseholdincomerenters2017.csv",
			 "/income_poverty/sub-borougharea-povertyrate.csv",
			 "/median_rent/sub-borougharea-medianrentrecentmovers2017.csv",
			 "/median_rent/sub-borougharea-medianrentstudiosand1-bedrooms2017.csv",
			 "/population/sub-borougharea-borninnewyorkstate.csv",
			 # "/race_ethnicity/sub-borougharea-percentasian.csv",
			 # "/race_ethnicity/sub-borougharea-percentblack.csv",
			 # "/race_ethnicity/sub-borougharea-percenthispanic.csv",
			 # "/race_ethnicity/sub-borougharea-percentwhite.csv",
			 "/race_ethnicity/sub-borougharea-racialdiversityindex.csv",
			 "/rental_subsidy/sub-borougharea-medianrent2-and3-bedrooms2017.csv",
			 "/rent_burden/sub-borougharea-medianrentburden.csv"]

data_names = ["rentalunitsaffordableat30amiofrecentlyavailableunits",
			 "rentalunitsaffordableat80amiofrecentlyavailableunits",
			 "rentalunitsaffordableat120amiofrecentlyavailableunits",
			 "householdswithchildrenunder18yearsold",
			 "single-personhouseholds",
			 "unemploymentrate",
			 "medianhouseholdincomehomeowners2017",
			 "medianhouseholdincomerenters2017",
			 "povertyrate",
			 "medianrentrecentmovers2017",
			 "medianrentstudiosand1-bedrooms2017",
			 "borninnewyorkstate",
			 # "percentasian",
			 # "percentblack",
			 # "percenthispanic",
			 # "percentwhite",
			 "racialdiversityindex",
			 "medianrent2-and3-bedrooms2017",
			 "medianrentburden"]

for index in range(len(datafiles)):
	datafiles[index] = directory + datafiles[index]

def remove_all_nans():
	df_list = []
	for datafile in datafiles:
		df_list.append(remove_nan(datafile))
	return df_list

def remove_nan(datafile):
	df = pd.read_csv(datafile)
	borough_list_raw = get_boroughs_in_dataframe(df)
	for col in df:
		if(col == '2011-2015'): 
			df = df[df[col].notnull()]
	#borough_list_clean = get_boroughs_in_dataframe(df)
	# for place in borough_list_raw:
	# 	if place not in borough_list_clean:
			#print(place)
	return df

def get_valid_rows():

	sba_list = list()
	b = list()
	for datafile in datafiles:
		df = pd.read_csv(datafile)
		borough_list_raw = get_boroughs_in_dataframe(df)
		b = borough_list_raw
		for col in df:
			if(col == '2011-2015'): 
				df = df[df[col].notnull()]
		borough_list_clean = get_boroughs_in_dataframe(df)
		for place in borough_list_raw:
			if place not in borough_list_clean:
				if place not in sba_list:
					sba_list.append(place)
	valid_rows = list()
	for place in b:
		if place not in sba_list:
			valid_rows.append(place)

	return valid_rows

def del_col(df, col):
	if col in df:
		del df[col]

def create_all_averages(df_list):
	start_col = '2005'
	years = 4
	for df in df_list:
		create_df_averages(start_col, df, years)

def create_df_averages(start_col, df, years):
	if start_col in df.columns:
		temp = int(start_col)
		while(str(int(start_col) + years) in df.columns):
			create_rolling_average(start_col, df, years)
			start_col = str(int(start_col) + 1)
		while(temp < int(start_col) + years):
			del df[str(temp)]
			temp = temp + 1

def create_rolling_average(start_col, df, years):
	end_col = int(start_col) + years
	new_name = start_col + "-" + str(end_col)
	curr_year = int(start_col)
	temp = curr_year
	df[new_name] = 0
	while(curr_year <= end_col):
		df[new_name] = df[new_name] + df[str(curr_year)]
		curr_year = curr_year + 1
	df[new_name] = df[new_name]/(years+1)

def get_boroughs_in_dataframe(df):
	boroughs = list()
	for name in df['Sub-Borough Area']:
		boroughs.append(name)
	return boroughs

def get_present_boroughs():
	present_boroughs = []
	name_freq = OrderedDict()
	for datafile in datafiles:
		df = pd.read_csv(datafile)
		for name in df['Sub-Borough Area']:
			if(name in name_freq):
				curr_freq = name_freq.get(name)
				name_freq[name] = curr_freq + 1
			else:
				name_freq[name] = 1
	
	for name in name_freq:
		#means that the sub-borough appears in all datasets
		if(name_freq[name] == len(datafiles)):
			present_boroughs.append(name)
	return present_boroughs

def get_borough_labels():
	df = pd.read_csv(borough_labels)
	borough_dict = OrderedDict()
	key_list = list()
	val_list = list()
	for name in df['Sub-Borough']:
		key_list.append(name)
	for label in df['Label']:
		val_list.append(label)
	for id_num in range(len(key_list)):
		borough_dict[key_list[id_num]] = val_list[id_num]
	return borough_dict

def get_puma_dict():
	df = pd.read_csv(puma_labels)
	borough_dict = OrderedDict()
	key_list = list()
	val_list = list()
	for name in df['Sub-Borough']:
		key_list.append(name)
	for label in df['puma']:
		val_list.append(label)
	for id_num in range(len(key_list)):
		borough_dict[key_list[id_num]] = val_list[id_num]
	return borough_dict

def check_labels(borough_labels):
	boroughs = get_present_boroughs()
	count = 0
	for b in borough_labels:
		if b in boroughs:
			count += 1
		else:
			print(b)
	print(count)
	print(len(borough_labels))

def del_row(df, row_name):
	df = df[df.name != row_name]

def get_cleaned_data():
	df_objs = remove_all_nans()
	create_all_averages(df_objs)
	present_boroughs = get_present_boroughs()
	for df in df_objs:
		boroughs = get_boroughs_in_dataframe(df)
		del_col(df, '2000') 
	return df_objs

def get_complete_df(df_objs, label_dict):
	puma_dict = get_puma_dict()

	row_list = get_valid_rows()
	
	puma_list = list()

	stage_1_list = list()
	stage_2_list = list()
	stage_3_list = list()

	clean_data_2015 = list()

	index = 0
	name_data_dict = OrderedDict()
	for df in df_objs:
		data_2015 = list()
		sba_list = list()
		for name in df['Sub-Borough Area']:
			sba_list.append(name)
		for data in df['2011-2015']:
			data_2015.append(data)

		clean_2015 = list()
		for num in range(len(sba_list)):
			if sba_list[num] in row_list:
				clean_2015.append(data_2015[num])

		name_data_dict[data_names[index]] = clean_2015
		index += 1
	
	labels = list()

	for index in range(len(row_list)):
		curr_sba = row_list[index]
		puma_list.append(puma_dict[curr_sba])
		label = label_dict[curr_sba]
		labels.append(label)
		
	df_new = pd.DataFrame(list(zip(puma_list)), columns = ['puma'])

	for name in name_data_dict:
		df_new[name] = name_data_dict[name]

	df_new['actual'] = labels 
	df_new['is_train'] = np.random.uniform(0, 1, len(df_new)) <= .75

	for col in df_new:
		df_new = df_new[df_new[col].notnull()]

	return df_new
	
def do_training(features):
	print(features.info())
	x = features.values
	train, test = features[features['is_train'] == True], features[features['is_train'] == False]
	labels = pd.factorize(train['actual'])[0]

	feature_set = features.columns[1:-2]
	#print(feature_set)
	clf = RandomForestClassifier(n_jobs = 2, max_features = 5, random_state = 0)

	clf.fit(train[feature_set], labels)

	arr = clf.predict(test[feature_set])
	print(arr)

	feature_importance = list(zip(train[feature_set], clf.feature_importances_))
	print(clf.feature_importances_)
	

if __name__ == '__main__':
	df_objs = get_cleaned_data()
	for df in df_objs:
		print(df.info())
	borough_labels = get_borough_labels()
	check_labels(borough_labels)

	final_df = get_complete_df(df_objs, borough_labels)

	print(final_df)
	do_training(final_df)
	# for df in df_objs:
	# 	print(df.describe())

