import os, sys, json
import cv2, random, time

from PIL import Image, ImageTk
import create_json

def drawBB(image, bb, width, height, color=(0, 0, 250), padding=0):
    ######### resizing of image for fitting into the screen
    start_x, start_y, end_x, end_y, width, height = resizing_image(x = bb['x'], y = bb['y'], x1 = bb['x1'], y1 = bb['y1'], height = 0, width = 0 )

    cv2.rectangle(image, (start_x, start_y), (end_x, end_y),
                  color, 2)

def resizing_image(x=0, y=0, x1=0, y1=0, height = 0, width = 0):
    scale_percent = 45
    start_x = int(x * scale_percent / 100)
    start_y = int(y * scale_percent / 100)
    end_x = int(x1 * scale_percent / 100) 
    end_y = int(y1 * scale_percent / 100)
    width = int(width * scale_percent / 100)
    height = int(height * scale_percent / 100)

    return start_x, start_y, end_x, end_y, width, height
    

def annotate_section(image_file_name, json_data):
    if not os.path.exists(image_file_name):
        print('image file does not exists Please check !!! for image file : ',image_file_name)
        sys.exit()
    img = cv2.imread(image_file_name)
    height, width, channels = img.shape

    ######### resizing of image for fitting into the screen
    start_x, start_y, end_x, end_y, width, height = resizing_image(x=0, y=0, x1=0, y1=0, height = height, width = width )

    # resize image
    resized = cv2.resize(img, (width, height), interpolation = cv2.INTER_AREA)
    resized_org_copy = resized.copy()

    for each_object in json_data['elements']:
        bbox = each_object["object"]
        drawBB(image=resized, bb=bbox, width=width, height=height, color=(0, 0, 255), padding=2)
    bounding_box_image_name = 'Bounding Box Image:' + json_data['imageMetadata']['asset']
    original_image_name = 'Original Image:' + json_data['imageMetadata']['asset']
    # cv2.imshow(bounding_box_image_name, resized)
    # cv2.imshow(original_image_name, resized_copy)
    # cv2.waitKey(0) # 0==wait forever

    ### to show in the gui window
    return resized,resized_org_copy

def read_data_from_json_file(json_file_name):
    json_file_path = os.getcwd() + '/annotation/' + json_file_name
    if not os.path.exists(json_file_path):
        print('json file does not exixts Please check !!! for json file : ', json_file_name)
        sys.exit()
    with open(json_file_path) as f:
        data = json.load(f)
        return data

def get_files_to_visualize():
    json_file_path = os.getcwd() + '/annotation/'
    if not os.path.exists(json_file_path):
       print('Annotation/Assets folder does not exixts Please check !!')
       sys.exit() 

    files = sorted(os.listdir(json_file_path))
    return files

def convert_opncv_to_pil_image(opencv_image):
    try:
        img = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
        annotated_img = Image.fromarray(img)
        Tk_annotated_img = ImageTk.PhotoImage(annotated_img)
        return Tk_annotated_img
    except:
        print ("Unexpected error:", sys.exc_info()[0])
        raise

def visualization_main(master, file):
    print('in visualization_main : ',file)
    image_file_path = os.getcwd() + '/assets/'
    # for file in files:
    image_file_name_with_path = image_file_path + file.split('.')[0]+'.jpg'
    json_data = read_data_from_json_file(file)
    resized_annotated_img,resized_org_copy = annotate_section(image_file_name_with_path, json_data)
    return json_data,resized_annotated_img,resized_org_copy
    print('Object Visualization done....')

# visualization_main()
