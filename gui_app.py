#https://python-textbok.readthedocs.io/en/1.0/Introduction_to_GUI_Programming.html

from tkinter import Tk, Label, Button, BOTH, Frame, messagebox
from tkinter import filedialog, Scrollbar, Entry, scrolledtext
from tkinter import *
from PIL import Image, ImageTk
from tkinter.ttk import Style
from PIL import Image, ImageTk

import os, sys, cv2, json,time
import create_json
import visualize_object_resized
import upload_raw_data_into_db

class SimpleGUI:
    def __init__(self, master):
        self.master = master
        self.files = []  # holds all the images to be displayed
        master.title('Automate Annotation')
        master.geometry("1200x700+300+300")
        master.configure(background='white')
        # annotation area
        demo = Image.open("leaf.png")
        tk_demo = ImageTk.PhotoImage(demo)
        self.label1 = Label(master, image = tk_demo)
        # self.label1 = Label(master)
        self.label1.image = tk_demo
        self.label1.place(x=200, y=22)

        # menubar
        menubar = Frame(bg = 'white')
        menubar.pack(side=LEFT, fill=Y, padx=20,pady=20)

        self.upload_button = Button(menubar, text="File Upload",fg='#443472',width=17, height=1, bg='wheat', command=lambda: self.upload_action('copying raw data..'))
        self.upload_button.pack(padx=2, pady=1)

        self.gen_json_button = Button(menubar, text="Generate Json Schema", fg='#443472',width=17, height=1, bg='wheat', command=lambda: self.generate_json('Going to generate json file...'))
        self.gen_json_button.pack(padx=2, pady=1)

        self.annotate_button = Button(menubar, text="Auto Annotation", fg='#443472', width=17, height=1, bg='wheat', command=lambda: self.annotate_object('Going to annotate object...', self.label1, master))
        self.annotate_button.pack(padx=2, pady=1)

        self.quit_button = Button(menubar, text = "Quit",fg='#443472',width=17, height=1, bg='wheat', command=self.quit)
        self.quit_button.pack(padx=2, pady=1)


    def generate_json(self, msg):
        print(msg)
        create_json.create_json_main()

    def annotate_object(self, msg,label1, master):
        print(msg)
        self.files = visualize_object_resized.get_files_to_visualize()
        # for file in files:
        print('Initially All image files are : ',self.files)
        self.visualisation()

    def visualisation(self):
        if not self.files:
            messagebox.showinfo("Image Files Info", "All The Image Files Visualization done !!!")
            return
        json_data,resized_annotated_img,resized_org_copy = visualize_object_resized.visualization_main(self.master, self.files.pop(0))
        self.show_annotated_image_on_gui_window(json_data,resized_annotated_img,resized_org_copy)
        print("After click on Next: remaining files are : ", self.files)


    def update_status(self, image_name, status):
        print("update_status for image_asset: ", image_name,status)
        #update db
        connection = create_json.create_database_connection()
        sql_query = '''update image_asset set asset_status=%d ''' %(status) + '''where image_name = '%s' ''' %(image_name)
        cursor = connection.cursor()
        cursor.execute(sql_query)
        connection.commit()
        connection.close()
        cursor.close()

    def show_annotated_image_on_gui_window(self,json_data,resized_annotated_img,resized_org_copy):
        try:
            # label for annotated images
            image_name = json_data['imageMetadata']['asset']
            Tk_annotated_img = visualize_object_resized.convert_opncv_to_pil_image(resized_annotated_img)
            print('after image convertion...')
            label1 = Label(self.master, image = Tk_annotated_img)
            label1.image = Tk_annotated_img
            label1.place(x=200, y=40)
            # label1.pack()
            # label for review buttons
            revw_label = Label(self.master)
            revw_label.place(x=200, y=365)

            btn_good = Button(revw_label, text="Good",fg='white',width=10, height=1, bg='#456296', command=lambda: self.update_status(image_name,1))
            btn_good.pack(padx=5, pady=1, side=LEFT)

            btn_bad = Button(revw_label, text="Bad",fg='white',width=10, height=1, bg='#456296', command=lambda: self.update_status(image_name,2))
            btn_bad.pack(padx=5, pady=1,side=LEFT)

            btn_worse = Button(revw_label, text="Worse",fg='white',width=10, height=1, bg='#456296', command=lambda: self.update_status(image_name,3))
            btn_worse.pack(padx=5, pady=1, side=LEFT)

            ########################################################################################
            #button Next to see new image
            next_label = Label(self.master)
            next_label.place(x=665, y=365)
            btn_next = Button(next_label, text="Next",fg='white',width=10, height=1, bg='gray', command=lambda: self.visualisation())
            btn_next.pack(padx=5, pady=1, side=RIGHT)

            # Label for Original Image
            Tk_annotated_img = visualize_object_resized.convert_opncv_to_pil_image(resized_org_copy)
            label2 = Label(self.master, image = Tk_annotated_img)
            label2.image = Tk_annotated_img
            label2.place(x=200, y=400)
            # label2.pack()

            # Label for Json file of that image
            text = json.dumps(json_data, indent=2)
            txt = scrolledtext.ScrolledText(self.master,width=40,height=40)
            txt.place(x=850,y=40)
            txt.insert(INSERT,text)   
        except:
            print ("Unexpected error:", sys.exc_info()[0])
            raise

    def upload_action(self, event=None):
        filename = filedialog.askopenfilename()
        fname, file_extension = os.path.splitext(filename)
        if file_extension != '.txt':
            print("Please enter .txt file to upload")
            # sys.exit()
        else:
            upload_raw_data_into_db.upload_into_db(filename)
            print('Upload done properly...')

    def quit(self):
        sys.exit()

root = Tk()
my_gui = SimpleGUI(root)
root.mainloop()
