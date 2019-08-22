###################################################################################################
# Project           : Global Challenges Research Fund (GCRF) African SWIFT (Science for Weather
#                     Information and Forecasting Techniques.
#
# Program name      : MARTIN
#
# Author            : Alexander J. Roberts, University of Leeds, NCAS
# 
# Date created      : Jan 2019
#
# Purpose           : Provide a user interface for navigating imagery for model data/case studies and allow
#                     users to annotate images and save. This has primarily been developed to 
#                     assist in SWIFT testbeds, teaching and workshops.
#
# Revision History  :
#
###################################################################################################

import tkinter as tk
from tkinter import colorchooser
from tkinter import filedialog
import PIL.Image
import PIL.ImageTk
import PIL.ImageDraw
import platform
plat = platform.system()
if plat == "Linux" or "Unix":
   import pyscreenshot as ImageGrab
else:
   import PIL.ImageGrab as ImageGrab
import datetime
import time
import os
import sys
import glob

###################################################################################################

# Set resource path to update based on whether code is being run as a python script or compiled to an executable.
# Once compiled the required imagery is included in the build and do not need seperate paths.

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("./resources/.")

    return os.path.join(base_path, relative_path)

# Function to flatten multidimensional lists.

def flat(alist):
    new_list = []
    for item in alist:
        if isinstance(item, (list, tuple)):
            new_list.extend(flat(item))
        else:
            new_list.append(item)
    return new_list

###################################################################################################

# Application

class App(tk.Frame):
   def __init__(self, master):

# This section of code looks in the current directory and generates dropdown menus based on the
# directories that are found.

      # Define variable, date and forecast dictionaries

      self.fore_dict = {}
      
      # define lists that will be used to populate dictionaries based on directory structure

      source_list = next(os.walk("."))[1]
      region_list = []
      init_list = []
      var_list = []
      self.trans_list = []

      region_count = 0
      init_count = 0
      var_count = 0

      # loop through top directory

      for i in range (0, len(source_list)):

         # check and populate first level forecast dictionary

         if not source_list[i] in self.fore_dict:
            self.fore_dict[source_list[i]] = {}

         # define values in second level of directory structure and add to list for use in dictionary

         region_list.append(next(os.walk(source_list[i]+"/."))[1])

         # loop through second level of directories

         for j in range (0, len(region_list[region_count])):

            # check and populate second level forecast dictionary

            if not region_list[region_count][j] in self.fore_dict[source_list[i]]:
               self.fore_dict[source_list[i]][region_list[region_count][j]] = {}

            # define values in third level of directory structure and add to list for use in dictionary

            init_list.append(next(os.walk(source_list[i]+"/"+region_list[region_count][j]+"/."))[1])

            # loop through third level of directories
 
            for k in range (0, len(init_list[init_count])):     #len(flat(source_list[:i]))+j])):

               # check and populate third level forecast dictionary

               if not init_list[init_count][k] in self.fore_dict[source_list[i]][region_list[region_count][j]]:
                  self.fore_dict[source_list[i]][region_list[region_count][j]][init_list[init_count][k]] = {}

               # define values in fourth level of directory structure and add to list for use in dictionary

               var_list.append(next(os.walk(source_list[i]+"/"+region_list[region_count][j]+"/"+init_list[init_count][k]+"/."))[1])

               # loop through fourth level of directories

               for l in range(0, len(var_list[var_count])):      #len(flat(region_list[i][:j]))+k])):

                  temp_file_names = glob.glob(source_list[i]+"/"+region_list[region_count][j]+"/"+init_list[init_count][k]+"/"+var_list[var_count][l]+"/*")
                  if temp_file_names:
                     img = PIL.Image.open(temp_file_names[0])
                     if img.mode == "RGBA" or "transparency" in img.info:
                        self.trans_list.extend(temp_file_names)
                  temp_fores_list = []
                  for tfn in temp_file_names:
                     tfn = os.path.basename(tfn)
                     if "analysis" in tfn:
                        temp_fores_list.append("000")
                     if (tfn[-7:-4]).isnumeric():
                         temp_fores_list.append(tfn[-7:-4])

                  if not var_list[var_count][l] in self.fore_dict[source_list[i]][region_list[region_count][j]][init_list[init_count][k]]:
                     self.fore_dict[source_list[i]][region_list[region_count][j]][init_list[init_count][k]][var_list[var_count][l]] = list(sorted(set(temp_fores_list)))

               var_count = var_count+1
            init_count = init_count+1
         region_count = region_count+1

###################################################################################################

# Here the tkinter GUI application is described

      # Basic setup

      tk.Frame.__init__(self, master)
      self.pack(padx=5, pady=5)
      self.master.title("Image Viewer")
      self.master.resizable(False, False)
      self.master.tk_setPalette(background='#ececec')

      self.master.protocol('WM_DELETE_WINDOW', self.click_cancel)
      self.master.bind('<Left>', self.previous)
      self.master.bind('<Right>', self.next)

      x = (self.master.winfo_screenwidth() - self.master.winfo_reqwidth()) // 4
      y = (self.master.winfo_screenheight() - self.master.winfo_reqheight()) // 3

      self.master.geometry("+{}+{}".format(x, y))
      self.master.config(menu=tk.Menu(self.master))

      # Logo

      self.height = root.winfo_screenheight()

      logo_file = resource_path("MARTINlogo_small.png")
      self.logo = PIL.Image.open(logo_file)
      self.relogo = self.logo.resize((int(self.height*0.15),int(self.height*0.15)))
      self.tklogo = PIL.ImageTk.PhotoImage(self.relogo)
      self.logo_label = tk.Label(self, image=self.tklogo)
      self.logo_label.grid(row = 1, column = 0, rowspan = 3)
 
      # Source drop down option box

      self.var1 = tk.StringVar(self)
      self.var1.trace('w', self.update_source)
      self.optionmenu1 = tk.OptionMenu(self, self.var1, *self.fore_dict.keys())
      tk.Label(self, text="Source").grid(row = 1, column = 3, columnspan=3)
      self.optionmenu1.grid(row = 2, column = 3, columnspan=3)

      # Region drop down option box

      self.var2 = tk.StringVar(self)
      self.var2.trace('w', self.update_region)
      self.optionmenu2 = tk.OptionMenu(self, self.var2, " ")
      tk.Label(self, text="Region").grid(row = 1, column = 6, columnspan=3)
      self.optionmenu2.grid(row = 2, column = 6, columnspan=3)

      # Init drop down option box

      self.var3 = tk.StringVar(self)
      self.var3.trace('w', self.update_init)
      self.optionmenu3 = tk.OptionMenu(self, self.var3, " ")
      tk.Label(self, text="Init").grid(row = 1, column = 9, columnspan=3)
      self.optionmenu3.grid(row = 2, column = 9, columnspan=3)

      # Var drop down option box

      self.var4 = tk.StringVar(self)
      self.var4.trace('w', self.update_var)
      self.optionmenu4 = tk.OptionMenu(self, self.var4, " ")
      tk.Label(self, text="Var").grid(row = 1, column = 12, columnspan=3)
      self.optionmenu4.grid(row = 2, column = 12, columnspan=3)

      # Previous button

      self.previous_button = tk.Button(self, text="<", command=self.previous)
      self.previous_button.grid(row = 2, column = 15)

      # Time drop down option box

      self.var5 = tk.StringVar(self)
      self.var5.trace('w', self.update_time)
      self.optionmenu5 = tk.OptionMenu(self, self.var5, " ")
      tk.Label(self, text="Time").grid(row = 1, column = 16, columnspan=3)
      self.optionmenu5.grid(row = 2, column = 16, columnspan=3)

      # Next button

      self.next_button = tk.Button(self, text=">", command=self.next)
      self.next_button.grid(row = 2, column = 19)

      # Overlay button
      
      self.var6 = tk.StringVar(self)
      self.var6.trace('w', self.check_overlay)
      self.optionmenu6 = tk.OptionMenu(self, self.var6, "")
      tk.Label(self, text="Overlay").grid(row = 1, column = 24, columnspan=3)
      self.optionmenu6.grid(row = 2, column = 24, columnspan=3)

      #  Submit button

      self.submit_button = tk.Button(self, text="Submit", command=self.check_vals)
      self.submit_button.grid(row = 2, column = 27, columnspan=3)

      # Select pen

      self.pen_button = tk.Button(self, text='pen', command=self.choose_pen)
      self.pen_button.grid(row=3, column = 3, columnspan=3)

      # Select color for annotations

      self.color_button = tk.Button(self, text='colour', command=self.choose_color)
      self.color_button.grid(row=3, column = 6, columnspan=3)

      # Select pen thickness
  
      self.thickness_button = tk.Scale(self, from_=1, to=10, orient='horizontal', label = "Pen thickness")
      self.thickness_button.set(5)
      self.thickness_button.grid(row=3, column=9, columnspan=3)

      # Undo button

      self.undo_button = tk.Button(self, text ='undo', command=self.undo)
      self.undo_button.grid(row=3, column=12, columnspan = 3)

      # Clear button

      self.clear_button = tk.Button(self, text ='clear notes', command=self.clear)
      self.clear_button.grid(row=3, column=15, columnspan=3)

      # Clear background button

      self.clear_back_button = tk.Button(self, text ='clear background', command=self.clear_back)
      self.clear_back_button.grid(row=3, column=18, columnspan=3)

      # white text button

      self.white_text_button = tk.Button(self, text ='white text', command=self.choose_white_text)
      self.white_text_button.grid(row=3, column=21, columnspan=3)

      # black text button

      self.black_text_button = tk.Button(self, text ='black text', command=self.choose_black_text)
      self.black_text_button.grid(row=3, column=24, columnspan=3)

      # text entry

      self.text_entry_box = tk.StringVar(self)
      self.text_entry = tk.Entry(self, textvariable=self.text_entry_box)
      tk.Label(self, text="Text Entry").grid(row = 1, column = 21, columnspan=3)
      self.text_entry.grid(row=2, column =21, columnspan=3)

      # Save with background button

      self.save_all_button = tk.Button(self, text ='save', command= lambda: self.save_all_crop(self.canvas))
      self.save_all_button.grid(row=3, column=27, columnspan = 3)

      # stamp button 1

      self.conv_img1 = PIL.Image.open(resource_path("Conv_blk.png"))
      self.conv_reimg1 = self.conv_img1.resize((30,30))
      self.conv_tkimg1 = PIL.ImageTk.PhotoImage(self.conv_reimg1)

      self.conv_button1 = tk.Button(self, image = self.conv_tkimg1, command= lambda: self.choose_stamp(self.conv_tkimg1))
      self.conv_button1.grid(row=1, column=1)

      # stamp button 2

      self.conv_img2 = PIL.Image.open(resource_path("Conv_wht.png"))
      self.conv_reimg2 = self.conv_img2.resize((30,30))
      self.conv_tkimg2 = PIL.ImageTk.PhotoImage(self.conv_reimg2)

      self.conv_button2 = tk.Button(self, image = self.conv_tkimg2, command= lambda: self.choose_stamp(self.conv_tkimg2))
      self.conv_button2.grid(row=1, column=2)

      # stamp button 3

      self.conv_img3 = PIL.Image.open(resource_path("Conv_blk_grw.png"))
      self.conv_reimg3 = self.conv_img3.resize((30,30))
      self.conv_tkimg3 = PIL.ImageTk.PhotoImage(self.conv_reimg3)

      self.conv_button3 = tk.Button(self, image = self.conv_tkimg3, command= lambda: self.choose_stamp(self.conv_tkimg3))
      self.conv_button3.grid(row=2, column=1)

      # stamp button 4

      self.conv_img4 = PIL.Image.open(resource_path("Conv_wht_grw.png"))
      self.conv_reimg4 = self.conv_img4.resize((30,30))
      self.conv_tkimg4 = PIL.ImageTk.PhotoImage(self.conv_reimg4)

      self.conv_button4 = tk.Button(self, image = self.conv_tkimg4, command= lambda: self.choose_stamp(self.conv_tkimg4))
      self.conv_button4.grid(row=2, column=2)

      # stamp button 5

      self.conv_img5 = PIL.Image.open(resource_path("Conv_blk_dcy.png"))
      self.conv_reimg5 = self.conv_img5.resize((30,30))
      self.conv_tkimg5 = PIL.ImageTk.PhotoImage(self.conv_reimg5)

      self.conv_button5 = tk.Button(self, image = self.conv_tkimg5, command= lambda: self.choose_stamp(self.conv_tkimg5))
      self.conv_button5.grid(row=3, column=1)

      # stamp button 6

      self.conv_img6 = PIL.Image.open(resource_path("Conv_wht_dcy.png"))
      self.conv_reimg6 = self.conv_img6.resize((30,30))
      self.conv_tkimg6 = PIL.ImageTk.PhotoImage(self.conv_reimg6)

      self.conv_button6 = tk.Button(self, image = self.conv_tkimg6, command= lambda: self.choose_stamp(self.conv_tkimg6))
      self.conv_button6.grid(row=3, column=2)
 

      # Setup image canvas

      self.canvas = tk.Canvas(self.master,height=int(self.height*0.666),width=self.height,bd=10, background = 'white')
      self.canvas.pack()

      # Input starting image

      self.im = PIL.Image.open(resource_path("No_image_loaded.png"))
      aspect_ratio = self.im.size[0]/self.im.size[1]
      self.reim = self.im.resize((int(self.height*0.666*aspect_ratio),int(self.height*0.666)))
      self.reim = self.im.resize((self.height,int(self.height*0.666)))
      self.tkim = PIL.ImageTk.PhotoImage(self.reim)
      self.canvas.create_image(self.height/2+10,int(self.height*0.666)/2+10, image=self.tkim, tags = "back")

      # Setup label

      self.status=tk.Label(self.master,text = 'Please make selection',bg='gray', font=('Helvetica',15),bd=2,fg='black',relief='sunken',anchor='w')
      self.status.pack(side='bottom',fill='x')

      self.setup()

   # Setup drawing on image

   def setup(self):
 
      self.draw_opt = "pen"
      self.old_x = None
      self.old_y = None
      self.line_width =self.thickness_button.get() 
      self.color = "black"
      self.canvas.bind('<B1-Motion>', self.paint)
      self.canvas.bind('<ButtonRelease-1>', self.reset)
      self.linecount = 1
         
   # Update dropdown menus based on selection of source

   def update_source(self, *args):

      regions = sorted(list(self.fore_dict[self.var1.get()].keys()))

      menu = self.optionmenu2['menu']

      menu.delete(0, 'end')


      for region in regions:

         menu.add_command(label=region, command=lambda reg=region: self.var2.set(reg))

   # Update dropdown menus based on the region selected

   def update_region(self, *args):

      inits = sorted(list(self.fore_dict[self.var1.get()][self.var2.get()].keys()))

      menu = self.optionmenu3['menu']

      menu.delete(0, 'end')

      for init in inits:

         menu.add_command(label=init, command=lambda ini=init: self.var3.set(ini))

   # Update dropdown menus based on the initiation selected

   def update_init(self, *args):

      varis = sorted(list(self.fore_dict[self.var1.get()][self.var2.get()][self.var3.get()].keys()))

      menu = self.optionmenu4['menu']

      menu.delete(0, 'end')

      for vari in varis:

         menu.add_command(label=vari, command=lambda v=vari: self.var4.set(v))


# Update dropdown menus based on the variable selected

   def update_var(self, *args):

      fores = self.fore_dict[self.var1.get()][self.var2.get()][self.var3.get()][self.var4.get()]

      menu = self.optionmenu5['menu']

      menu.delete(0, 'end')

      for fore in fores:

         menu.add_command(label=fore, command=lambda f=fore: self.var5.set(f))

# Update dropdown menus based on the time selected

   def update_time(self, *args):

      file_source = self.var1.get()
      file_region = self.var2.get()
      file_init = self.var3.get()
      file_fore = self.var5.get()

      if file_fore == "000":
         if glob.glob(file_source+"/"+file_region+"/"+file_init+"/*/*analysis*.png"):
            files = glob.glob(file_source+"/"+file_region+"/"+file_init+"/*/*analysis*.png")
         else:
            files = glob.glob(file_source+"/"+file_region+"/"+file_init+"/*/*"+file_fore+".png")
      else:
         if(glob.glob(file_source+"/"+file_region+"/"+file_init+"/*/*"+file_fore+".png")):
            files = glob.glob(file_source+"/"+file_region+"/"+file_init+"/*/*"+file_fore+".png")
         else:
            files = ""

      trans_files = set(files) & set(self.trans_list)
      trans_vars = []
      for tf in trans_files:
         trans_vars.append(tf.split("/")[3])

      overlays = ["grid_black_"+file_region, "grid_white_"+file_region, "map_black_"+file_region, "map_white_"+file_region]
     
      menu = self.optionmenu6['menu']

      menu.delete(0, 'end')
 
      for overlay in overlays:
         if glob.glob(resource_path(overlay+".png")):
            menu.add_command(label=overlay, command=lambda over=overlay: self.var6.set(over))
      for trans_var in trans_vars:
         menu.add_command(label=trans_var, command=lambda over=trans_var: self.var6.set(over))

   # Check the values in the drop down menues are sensible on the use of the submit button, advise on what needs changing or display image

   def check_vals(self, event=None):

      file_source = self.var1.get()
      file_region = self.var2.get()
      file_init = self.var3.get()
      file_var = self.var4.get()
      file_fore = self.var5.get()

      if file_fore == "000":
         if glob.glob(file_source+"/"+file_region+"/"+file_init+"/"+file_var+"/*analysis*.png")[0]:
            file_name = glob.glob(file_source+"/"+file_region+"/"+file_init+"/"+file_var+"/*analysis*.png")[0]
         else:
            file_name = glob.glob(file_source+"/"+file_region+"/"+file_init+"/"+file_var+"/*"+file_fore+".png")[0]
      else:
         if(glob.glob(file_source+"/"+file_region+"/"+file_init+"/"+file_var+"/*"+file_fore+".png")):
            file_name = glob.glob(file_source+"/"+file_region+"/"+file_init+"/"+file_var+"/*"+file_fore+".png")[0]
         else:
            file_name = ""

      if file_name:
         self.status['text']='Annotate image as required'
      else:
         file_name = resource_path("No_image_loaded.png")
         self.status['text']='Cannot find image please select other options'

      self.im = PIL.Image.open(file_name)
      aspect_ratio = self.im.size[0]/self.im.size[1]
      self.reim = self.im.resize((int(self.height*0.666*aspect_ratio),int(self.height*0.666)))
      self.tkim = PIL.ImageTk.PhotoImage(self.reim)
      self.canvas.delete(self.tkim)
      self.canvas.create_image(self.height/2+10,int(self.height*0.666)/2+10, image=self.tkim, tags = "back")
      self.canvas.tag_raise("lines")
      
   # Check the values in the drop down menues are sensible on the use of the submit button, advise on what needs changing or display image

   def check_overlay(self, *args):

      file_source = self.var1.get()
      file_region = self.var2.get()
      file_init = self.var3.get()
      file_fore = self.var5.get()
      file_var = self.var6.get()

      if file_fore == "000":
         if (glob.glob(file_source+"/"+file_region+"/"+file_init+"/"+file_var+"/*analysis*.png")):
            ol_file_name = glob.glob(file_source+"/"+file_region+"/"+file_init+"/"+file_var+"/*analysis*.png")[0]
         elif (glob.glob(file_source+"/"+file_region+"/"+file_init+"/"+file_var+"/*"+file_fore+".png")):
            ol_file_name = glob.glob(file_source+"/"+file_region+"/"+file_init+"/"+file_var+"/*"+file_fore+".png")[0]
         else:
            ol_file_name = resource_path(file_var+".png")
      else:
         if(glob.glob(file_source+"/"+file_region+"/"+file_init+"/"+file_var+"/*"+file_fore+".png")):
            ol_file_name = glob.glob(file_source+"/"+file_region+"/"+file_init+"/"+file_var+"/*"+file_fore+".png")[0]
         else:
            ol_file_name = resource_path(file_var+".png")

      self.olim = PIL.Image.open(ol_file_name)
      aspect_ratio = self.olim.size[0]/self.olim.size[1]
      self.olreim = self.olim.resize((int(self.height*0.666*aspect_ratio),int(self.height*0.666)))
      
      globals()["oltkim%04d" % self.linecount] = PIL.ImageTk.PhotoImage(self.olreim)
      
      self.canvas.create_image(self.height/2+10,int(self.height*0.666)/2+10, image=globals()["oltkim%04d" % self.linecount], tags = ("lines", "%04d" % self.linecount))
      self.linecount = self.linecount + 1

   # Set background image to previous time

   def previous(self, event=None):

      file_source = self.var1.get()
      file_region = self.var2.get()
      file_init = self.var3.get()
      file_var = self.var4.get()
      file_fore = self.var5.get()

      if file_fore == "":
         file_fore = self.fore_dict[file_source][file_region][file_init][file_var][0]
      if file_fore == self.fore_dict[file_source][file_region][file_init][file_var][0]:
         file_fore = self.fore_dict[file_source][file_region][file_init][file_var][0]
      else:
         file_fore = "%03d" % (int(file_fore)-3)

# Maybe keep for satellite imagery at later date.

#      elif file_source == "GFS":
#         if file_time == "000":
#            file_time = "000"
#         else:
#            file_time = "%03d" % (int(file_time)-3)
#      else:
#         if file_time == "000":
#            date_pos = self.date_dict[file_type][file_case][file_var].index(file_date)
#            if(date_pos > 0):
#               file_time = "021"
#               file_date = self.date_dict[file_type][file_case][file_var][date_pos-1]
#               self.var4.set(file_date)
#         else:
#            file_time = "%03d" % (int(file_time)-3)

      self.var5.set(file_fore)
      self.check_vals()

# Set background image to next time

   def next(self, event=None):

      file_source = self.var1.get()
      file_region = self.var2.get()
      file_init = self.var3.get()
      file_var = self.var4.get()
      file_fore = self.var5.get()

      if file_fore == "":
         file_fore = self.fore_dict[file_source][file_region][file_init][file_var][0]
      
      list_len = len(self.fore_dict[file_source][file_region][file_init][file_var])
      fore_pos = self.fore_dict[file_source][file_region][file_init][file_var].index(file_fore)
      if (fore_pos+1 < list_len):
         file_fore = "%03d" % (int(file_fore)+3)
      else:
         file_fore = self.fore_dict[file_source][file_region][file_init][file_var][list_len-1]

# Keep for when satellite data is to be used

#      elif file_type == "GFS":
#         if file_time >= "048":
#            file_time = "048"
#         else:
#            file_time = "%03d" % (int(file_time)+3)
#      else:
#         if file_time >= "021":
#            list_len = len(self.date_dict[file_type][file_case][file_var])
#            date_pos = self.date_dict[file_type][file_case][file_var].index(file_date)
#            if(date_pos+1 < list_len):
#               file_time = "000"
#               file_date = self.date_dict[file_type][file_case][file_var][date_pos+1]
#               self.var4.set(file_date)
#         else:
#            file_time = "%03d" % (int(file_time)+3)

      self.var5.set(file_fore)
      self.check_vals()

   # Choose pen option

   def choose_pen(self):
      self.draw_opt = "pen"
      self.canvas.bind('<B1-Motion>', self.paint)
      self.canvas.bind('<ButtonRelease-1>', self.reset)

   # Choose stamp option

   def choose_stamp(self, img):
      self.draw_opt = "stamp"
      self.stamp_img = img
      self.canvas.bind('<Button-1>', self.stamp)

   # Choose white text option

   def choose_white_text(self):
      self.draw_opt = "white_text"
      self.text_stamp = self.text_entry_box.get()
      self.canvas.bind('<Button-1>', self.white_text)

   # Choose black text option

   def choose_black_text(self):
      self.draw_opt = "black_text"
      self.text_stamp = self.text_entry_box.get()
      self.canvas.bind('<Button-1>', self.black_text)

   # Paint smooth lines on canvas

   def paint(self, event):
      if self.draw_opt == "pen":
         paint_color = self.color
         self.line_width = self.thickness_button.get()
         if self.old_x and self.old_y:
             self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                width=self.line_width, fill=paint_color,
                                capstyle='round', smooth='true', splinesteps=36, tags = ("lines", "%04d" % self.linecount))
         self.old_x = event.x
         self.old_y = event.y

   # Stamp image on canvas when clicked

   def stamp(self,event):
      if self.draw_opt == "stamp":
         self.canvas.create_image(event.x, event.y, image = self.stamp_img, tags = ("lines", "%04d" % self.linecount))

   # White text stamp when clicked

   def white_text(self,event):
      if self.draw_opt == "white_text":
         self.canvas.create_text(event.x, event.y, text=self.text_stamp, font="Helvetica 15", fill ="white", tags = ("lines", "%04d" % self.linecount), width=200)

   # Black text stamp when clicked

   def black_text(self,event):
      if self.draw_opt == "black_text":
         
         self.canvas.create_text(event.x, event.y, text=self.text_stamp, font="Helvetica 15", fill ="black", tags = ("lines", "%04d" % self.linecount), width=200)

   # Reset before next event

   def reset(self, event):
      self.linecount = self.linecount + 1
      self.old_x, self.old_y = None, None

   # Call the colour chooser and update paint colour

   def choose_color(self):
      self.color = colorchooser.askcolor(color=self.color)[1]

   # Undo the last line drawn

   def undo(self):
      if self.linecount >= 1:
         del_id = self.linecount-1
         self.canvas.delete("%04d&&lines" % del_id)
         self.linecount = self.linecount - 1

   # Clear all lines drawn so far

   def clear(self):
      self.canvas.delete("lines")
      self.linecount = 1

   # Clear background image

   def clear_back(self):
      self.canvas.delete("back")

   # Grab all on current canvas

   def save_all_crop(self, canvas):
      x=root.winfo_rootx()+canvas.winfo_x()+11
      y=root.winfo_rooty()+canvas.winfo_y()+11
      x1=x+canvas.winfo_width()-23
      y1=y+canvas.winfo_height()-24
      self.grab_img = ImageGrab.grab(bbox=(x,y,x1,y1))
      self.check_img()

   # Check to see if grabbed canvas is black
 
   def check_img(self):
      if self.grab_img.getbbox() == None:
         self.save_all_crop(self.canvas)
      else:
         self.save_as(self.grab_img)

   def save_as(self, img):
      name=filedialog.asksaveasfilename(defaultextension =".png")
      if name:
         img.save(name)

   # exit program when window is closed

   def click_cancel(self, event=None):
      self.master.destroy()

# Main, calls app

if __name__ == '__main__':

   root = tk.Tk()
   app = App(root)
   app.mainloop()

