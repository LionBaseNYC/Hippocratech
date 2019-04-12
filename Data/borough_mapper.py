import pandas as pd
import geojsonio
import folium
import re
import math
from sklearn import preprocessing

directory = "/Users/brandonzhang/Desktop/Lionbase_Material/Data/core-set"
datafile = directory + "/properties/properties.csv"

zip_codes = directory + "/properties/Zip_Code_Data.csv"

puma_txt = "/Users/brandonzhang/Desktop/Lionbase_Material/Data/puma.txt"

weights = [0.08757672, 0.03230614, 0.05532291, 0.04805972, 0.0849674, 0.13466479,
 0.04604631, 0.07536783, 0.05275271, 0.03557622, 0.1026015,  0.04068348,
 0.07582808, 0.07257706, 0.05566913]

from clean_gentrification_data import get_cleaned_data, get_puma_dict, get_valid_rows

def get_indexes():
	index_list = list()
	df_objs = get_cleaned_data()
	weight_index = 0; 
	valid_rows = get_valid_rows()
	puma_dict = get_puma_dict()
	indexes = list()
	for i in range(len(valid_rows)):
		indexes.append(0)
	for df in df_objs:
		curr_index = 0
		sba_list = list()
		for sba in df['Sub-Borough Area']:
			sba_list.append(sba)
		data = list()
		for d in df['2011-2015']:
			data.append(d)
		for i in range(len(sba_list)):
			if sba_list[i] in valid_rows:
				indexes[curr_index] += data[i]*weights[weight_index]
				curr_index += 1
		weight_index += 1

	puma_list = list()
	for i in range(len(valid_rows)):
		puma_list.append(puma_dict[valid_rows[i]])
	return puma_list, indexes

def get_pumas():
	file = open(puma_txt, 'r')
	file_str = ""
	for line in file:
		file_str = file_str + line
	puma_gen = [m.start() for m in re.finditer('puma', file_str)]
	puma_list = list()
	count_list = list()
	count = 0
	for index in puma_gen:
		puma_code = file_str[index+7] + file_str[index+8] + file_str[index+9] + file_str[index+10]
		puma_list.append(puma_code)
		count_list.append(count)
		count += 1
		#print(puma_code)

	df_new = pd.DataFrame(list(zip(count_list, puma_list)), columns = ['index', 'puma'])
	return df_new


def reform_zips():
	df = pd.read_csv(zip_codes)
	df = df[df['Zip-Codes'].notnull()]
	sba_list = list()
	zip_list = list()
	for sba in df['Sub-Borough']:
		sba_list.append(sba)
	for zip_code in df['Zip-Codes']:
		zip_str = str(zip_code)
		zip_list.append(zip_str.split())
	
	sing_sba_list = list()
	sing_zip_list = list()
	count_list = list()
	count = 0

	for index in range(len(sba_list)):
		curr_sba = sba_list[index]
		curr_zips = zip_list[index]
		for num in range(len(curr_zips)):
			sing_sba_list.append(curr_sba)
			sing_zip_list.append(curr_zips[num])
			count_list.append(count)
			count += 1
	df_new = pd.DataFrame(list(zip(count_list, sing_sba_list, sing_zip_list)), columns = ['index', 'sub_borough','zip_code'])
	return df_new

def generate_map(df):
	zip_map = folium.Map(location = [40.7589, -73.9851], zoom_start = 12)
	zip_map.choropleth(geo_data = 'puma.geojson', 
		data = df, 
		columns = ['zip_code', 'index'], 
		key_on = 'feature.properties.postalCode',
		fill_color = 'RdYlGn', fill_opacity = 0.7, line_opacity = 0.8,
		legend_name = "Zip Code plot")
	folium.LayerControl().add_to(zip_map)
	return zip_map

def generate_puma_map(df):
	zip_map = folium.Map(location = [40.7589, -73.9851], zoom_start = 12)
	zip_map.choropleth(geo_data = 'puma.geojson', 
		data = df, 
		columns = ['puma', 'index'], 
		key_on = 'feature.properties.puma',
		fill_color = 'RdYlGn', fill_opacity = 0.7, line_opacity = 0.8,
		legend_name = "Sub Borough Plot")
	folium.LayerControl().add_to(zip_map)
	return zip_map


def print_overlaps():
	count = 0
	df = pd.read_csv(zip_codes)
	df = df[df['Zip-Codes'].notnull()]
	zip_dict = dict()
	sba_list = list()
	zip_list = list() 
	overlap_set = set()
	for sba in df['Sub-Borough']:
		sba_list.append(sba)
	for zip_code in df['Zip-Codes']:
		zip_str = str(zip_code)
		zip_split = zip_str.split()
		zip_list_sub = list()
		for i in range(len(zip_split)):
			zip_list_sub.append(zip_split[i])
		zip_list.append(zip_list_sub)
	for i in range(len(zip_list)):
		for j in range(i+1, len(zip_list)):
			curr_zip_list = zip_list[i]
			other_zip_list = zip_list[j]

			for k in range(len(curr_zip_list)):
				if(curr_zip_list[k] in other_zip_list):
					sba_tuple = (sba_list[i], sba_list[j])
					print(sba_tuple)
					count += 1
	print(count)

def get_puma_list(df):
	return df['puma'].tolist()

def make_df(list1, list2):
	df_new = pd.DataFrame(list(zip(list1, list2)), columns = ['puma', 'index'])
	df_new['index'] = (df_new['index']-df_new['index'].min())/(df_new['index'].max()-df_new['index'].min())
	return df_new

#HTML Rendering pulled from https://github.com/python-visualization/folium/issues/946#issuecomment-417272388

# ------------------------------------------------------------------------------------------------
# so let's write a custom temporary-HTML renderer
# pretty much copy-paste of this answer: https://stackoverflow.com/a/38945907/3494126
import subprocess
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer


PORT = 7000
HOST = '127.0.0.1'
SERVER_ADDRESS = '{host}:{port}'.format(host=HOST, port=PORT)
FULL_SERVER_ADDRESS = 'http://' + SERVER_ADDRESS


def TemproraryHttpServer(page_content_type, raw_data):
    """
    A simpe, temprorary http web server on the pure Python 3.
    It has features for processing pages with a XML or HTML content.
    """

    class HTTPServerRequestHandler(BaseHTTPRequestHandler):
        """
        An handler of request for the server, hosting XML-pages.
        """

        def do_GET(self):
            """Handle GET requests"""

            # response from page
            self.send_response(200)

            # set up headers for pages
            content_type = 'text/{0}'.format(page_content_type)
            self.send_header('Content-type', content_type)
            self.end_headers()

            # writing data on a page
            self.wfile.write(bytes(raw_data, encoding='utf'))

            return

    if page_content_type not in ['html', 'xml']:
        raise ValueError('This server can serve only HTML or XML pages.')

    page_content_type = page_content_type

    # kill a process, hosted on a localhost:PORT
    subprocess.call(['fuser', '-k', '{0}/tcp'.format(PORT)])

    # Started creating a temprorary http server.
    httpd = HTTPServer((HOST, PORT), HTTPServerRequestHandler)

    # run a temprorary http server
    httpd.serve_forever()


def run_html_server(html_data=None):

    if html_data is None:
        html_data = """
        <!DOCTYPE html>
        <html>
        <head>
        <title>Page Title</title>
        </head>
        <body>
        <h1>This is a Heading</h1>
        <p>This is a paragraph.</p>
        </body>
        </html>
        """

    # open in a browser URL and see a result
    webbrowser.open(FULL_SERVER_ADDRESS)

    # run server
    TemproraryHttpServer('html', html_data)

# ------------------------------------------------------------------------------------------------
zip_df = reform_zips()
zip_map = generate_map(zip_df)

puma_list, indexes = get_indexes()

print(len(indexes))
print(len(puma_list))

for i in range(len(puma_list)):
	if(math.isnan(indexes[i])):
		del puma_list[i]
		del indexes[i]
		break

#puma_dict_all = get_puma_dict()

all_puma_df = get_pumas()

all_pumas = get_puma_list(all_puma_df)
all_indexes = list()
index = 0
for puma in all_pumas:
	if(not int(puma) in puma_list):
		all_indexes.append(0)
	else:
		all_indexes.append(indexes[index])
		index += 1

print(all_indexes)
print(all_pumas)

puma_df = make_df(all_pumas, all_indexes) #get_pumas()
print(puma_df.info())
puma_map = generate_puma_map(puma_df)

# now let's save the visualization into the temp file and render it
from tempfile import NamedTemporaryFile
tmp = NamedTemporaryFile()
puma_map.save(tmp.name)
with open(tmp.name) as f:
    folium_map_html = f.read()

#print(zip_map)

iframe = puma_map._repr_html_()

run_html_server(folium_map_html)






