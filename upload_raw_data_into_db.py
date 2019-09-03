import os, sys, json
import cv2
import mysql.connector
from mysql.connector import Error
from collections import OrderedDict 

class RawData(object):
	"""docstring for RawData"""
	def __init__(self, image_name, total_no_obj):
		super(RawData, self).__init__()

		self.image_name = image_name
		self.total_no_obj = total_no_obj
		self.object_dict = OrderedDict()


def read_from_raw_input(filename):
	with open(filename) as f:
		mylist = [line.rstrip('\n') for line in f]

	class_obj_list = []
	for line in mylist:
		if len(line) == 0:
			continue
		line_split_data= line.split(',')
		try:
			obj_rawData = RawData(line_split_data[0],int(line_split_data[1]))
			for index, data in enumerate(line_split_data, start = 0):
				# print(index, data)
				if data.lower().find('bottle') >= 0:
					obj_rawData.object_dict[line_split_data[index]] = [int(line_split_data[index-4]),int(line_split_data[index-3]),int(line_split_data[index-2]),int(line_split_data[index-1])]
			class_obj_list.append(obj_rawData)
		except Error as e:
			print('this is because of incomplete end of file  : ',e)
			print('Please process the RawData file before upload')
			sys.exit()
	return class_obj_list

# sample dict
# 019.jpg 7 {'Bottle0': ['200', '353', '283', '513'], 'Bottle1': ['622', '346', '700', '498'],
# 'Bottle2': ['966', '332', '1042', '484'], 'Bottle3': ['1', '365', '61', '522'], 
#'Bottle4': ['418', '350', '473', '406'], 'Bottle5': ['632', '319', '683', '401'], 'Bottle6': ['1118', '343', '1190', '496']} 


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

def insert_into_database(connection, class_obj_list):
	try:
		cursor = connection.cursor()
		for class_obj in class_obj_list: 

			# check whether this image is present or not by it's image name in the image_asset table:
			check_sql_query = '''SELECT COUNT(*) FROM image_asset WHERE image_name = '%s' ''' %(class_obj.image_name)
			cursor.execute(check_sql_query)
			if cursor.fetchone()[0] > 0:
				print("%s image file is already present in the database.." %(class_obj.image_name))
				continue

			insert_query = '''INSERT INTO image_asset (image_name, total_objects) VALUES('%s',%d)''' %(class_obj.image_name, class_obj.total_no_obj)
			cursor.execute(insert_query)
			connection.commit()

			### insert into asset_details table:
			cursor.execute('select max(id) from image_asset')
			image_asset_id = cursor.fetchone()[0]
			# need to loop for multiple object of single image file
			for key in class_obj.object_dict:
				coord_list = class_obj.object_dict[key]
				insert_into_asset_detail_query = '''INSERT INTO asset_details (img_id, obj_name, x_crd,y_crd,x1_crd,y1_crd) VALUES(%d,'%s',%d,%d,%d,%d)''' %(image_asset_id, key,coord_list[0],coord_list[1],coord_list[2],coord_list[3])
				cursor.execute(insert_into_asset_detail_query)
				connection.commit()

		connection.close()
		cursor.close()
	except Error as e:
	    print("Error reading data from MySQL table", e)
	    sys.exit()

def upload_into_db(filename):
	print("inside upload_into_db file...", filename)
	connection = create_database_connection()
	class_obj_list = read_from_raw_input(filename)
	insert_into_database(connection, class_obj_list)
	print('successfully RawData inserted in corresponding tables...')

# filename = 'BottleInspection_gt.txt'
# upload_into_db(filename)

