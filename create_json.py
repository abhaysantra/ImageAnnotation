import os, sys, json
import mysql.connector
from mysql.connector import Error

def write_into_json(each_img_asset, asset_records):
	# print('inside write_into_json func : ')
	image_data = {}
	image_data['imageMetadata'] = {}
	image_data['imageMetadata']['asset'] = each_img_asset[1]
	image_data['imageMetadata']['assetid'] = each_img_asset[0]
	image_data['imageMetadata']['noOfObjects'] = each_img_asset[2]
	image_data['elements'] = []
	for asset in asset_records:
		asset_dict = {}
		asset_dict['objectid'] = asset[0]
		asset_dict['assetid'] = asset[1]
		asset_dict['objname'] = asset[2]

		asset_dict['object'] = {}
		asset_dict['object']['x'] = asset[3]
		asset_dict['object']['y'] = asset[4]
		asset_dict['object']['x1'] = asset[5]
		asset_dict['object']['y1'] = asset[6]
		image_data['elements'].append(asset_dict)

	output_file_name = str(each_img_asset[1].split('.')[0]+ '.json')
	json_file_path = os.getcwd() + '/annotation/'
	if not os.path.exists(json_file_path):
	   print('Annotation folder does not exixts Please check !!')
	   sys.exit() 

	with open(os.path.join(json_file_path,output_file_name), 'w') as outfile:
		json.dump(image_data, outfile, indent =4)
	# sys.exit(-99)

def create_database_connection():
	try:
		connection = mysql.connector.connect(host='localhost',
		                                     database='image_gallery',
		                                     user='root',
		                                     password='')
		return connection
	except Error as e:
	    print("unable to connect to database :", e)
	    sys.exit()

def read_data_from_database(connection):
	try:
		sql_select_query = 'select * from image_asset'
		cursor = connection.cursor()
		cursor.execute(sql_select_query)
		image_asset_records = cursor.fetchall()
		# print("Total number of rows in Image Asset Table is: ", cursor.rowcount)
		for each_img_asset in image_asset_records:
			asset_detail_query = 'select * from asset_details where img_id = '+ str(each_img_asset[0])
			cursor.execute(asset_detail_query)
			asset_records = cursor.fetchall()
			write_into_json(each_img_asset, asset_records)
		connection.close()
		cursor.close()
		# print("MySQL connection is closed")
	except Error as e:
	    print("Error reading data from MySQL table", e)
	    sys.exit()

def create_json_main():
	print("Making database connection and reading data from it and writing in json file:")
	connection = create_database_connection()
	read_data_from_database(connection)
	print("json file created successfully...")

# create_json_main()
# if __name__ == "__main__":
#     main()
