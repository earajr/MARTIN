###################################################################################################
# Project           : Global Challenges Research Fund (GCRF) African SWIFT (Science for Weather
#                     Information and Forecasting Techniques.
#
# Program name      : CasestudyGUI
#
# Author            : Alexander J. Roberts, University of Leeds, NCAS
# 
# Date created      : Dec 2018
#
# Purpose           : Provide a user interface for navigating imagery for case studies and allow
#                     users to annotate images and save. This has primarily been developed to 
#                     assist in teaching and workshops.
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
else
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
 
      self.var_dict = {}
      self.date_dict = {}
      self.fore_dict = {}
      
      # define lists that will be used to populate dictionaries based on directory structure

      type_list = next(os.walk("."))[1]
      case_list = []
      var_list = []

      # loop through top directory

      for i in range (0, len(type_list)):

         # check and populate first level of variable, date and forecast dictionaries

         if not type_list[i] in self.var_dict:
            self.var_dict[type_list[i]] = {}
         if not type_list[i] in self.date_dict:
            self.date_dict[type_list[i]] = {}
         if not type_list[i] in self.fore_dict:
            self.fore_dict[type_list[i]] = {}

         # define values in second level of directory structure and add to list for use in disctionaries

         case_list.append(next(os.walk(type_list[i]+"/."))[1])

         # loop through second level of directories

         for j in range (0, len(case_list[i])):

         # check and populate first level of variable, date and forecast dictionaries

            if not case_list[i][j] in self.var_dict[type_list[i]]:
               self.var_dict[type_list[i]][case_list[i][j]] = (next(os.walk(type_list[i]+"/"+case_list[i][j]+"/."))[1])
            if not case_list[i][j] in self.date_dict[type_list[i]]:
               self.date_dict[type_list[i]][case_list[i][j]] = {}
            if not case_list[i][j] in self.fore_dict[type_list[i]]:
               self.fore_dict[type_list[i]][case_list[i][j]] = {}

            # define values in third level of directory structure and add to list for use in disctionaries

            var_list.append(next(os.walk(type_list[i]+"/"+case_list[i][j]+"/."))[1])

            for k in range (0, len(var_list[len(flat(case_list[:i]))+j])):

               # using file names identify the dates and forecast/valid times for which images are present

               temp_file_names = glob.glob(type_list[i]+"/"+case_list[i][j]+"/"+var_list[len(flat(case_list[:i]))+j][k]+"/*")
               temp_dates_list = []
               temp_fores_list = []
               for tfn in temp_file_names:
                   tfn = os.path.basename(tfn)
                   if type_list[i] == "GFS":
                      if tfn.split("_")[0] == "GFSforecast":
                         temp_dates_list.append(tfn.split("_")[-2][:10])
                         temp_fores_list.append((tfn.split("_")[-1]).split(".")[0])
                      else:
                         temp_dates_list.append(tfn.split("_")[1][:10])
                         temp_fores_list.append("000")
                   else:
                      temp_dates_list.append(tfn.split("_")[1][:8])
                      if var_list[len(flat(case_list[:i]))+j][k] != "Hov":
                         temp_fores_list.append("%03d" % int(tfn.split("_")[1][8:10]))

               # check and populate second level of variable, date and forecast dictionaries

               if not var_list[len(flat(case_list[:i]))+j][k] in self.date_dict[type_list[i]][case_list[i][j]]:
                  self.date_dict[type_list[i]][case_list[i][j]][var_list[len(flat(case_list[:i]))+j][k]] = list(sorted(set(temp_dates_list)))
               if not var_list[len(flat(case_list[:i]))+j][k] in self.fore_dict[type_list[i]][case_list[i][j]]:
                  self.fore_dict[type_list[i]][case_list[i][j]][var_list[len(flat(case_list[:i]))+j][k]] = list(sorted(set(temp_fores_list)))

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

      logo_file = resource_path("SWIFT_logo.png")
      self.logo = PIL.Image.open(logo_file)
      self.relogo = self.logo.resize((250,96))
      self.tklogo = PIL.ImageTk.PhotoImage(self.relogo)
      self.logo_label = tk.Label(self, image=self.tklogo)
      self.logo_label.grid(row = 1, column = 0, rowspan = 3)
 
      # Type drop down option box

      self.var1 = tk.StringVar(self)
      self.var1.trace('w', self.update_type)
      self.optionmenu1 = tk.OptionMenu(self, self.var1, *self.var_dict.keys())
      tk.Label(self, text="Type").grid(row = 1, column = 3, columnspan=3)
      self.optionmenu1.grid(row = 2, column = 3, columnspan=3)

      # Case drop down option box

      self.var2 = tk.StringVar(self)
      self.var2.trace('w', self.update_case)
      self.optionmenu2 = tk.OptionMenu(self, self.var2, " ")
      tk.Label(self, text="Case").grid(row = 1, column = 6, columnspan=3)
      self.optionmenu2.grid(row = 2, column = 6, columnspan=3)

      # Var drop down option box

      self.var3 = tk.StringVar(self)
      self.var3.trace('w', self.update_vars)
      self.optionmenu3 = tk.OptionMenu(self, self.var3, " ")
      tk.Label(self, text="Var").grid(row = 1, column = 9, columnspan=3)
      self.optionmenu3.grid(row = 2, column = 9, columnspan=3)

      # Date drop down option box

      self.var4 = tk.StringVar(self)
      self.optionmenu4 = tk.OptionMenu(self, self.var4, " ")
      tk.Label(self, text="Date").grid(row = 1, column = 12, columnspan=3)
      self.optionmenu4.grid(row = 2, column = 12, columnspan=3)

      # Previous button

      self.previous_button = tk.Button(self, text="<", command=self.previous)
      self.previous_button.grid(row = 2, column = 15)

      # Time drop down option box

      self.var5 = tk.StringVar(self)
      self.optionmenu5 = tk.OptionMenu(self, self.var5, " ")
      tk.Label(self, text="Time").grid(row = 1, column = 16, columnspan=3)
      self.optionmenu5.grid(row = 2, column = 16, columnspan=3)

      # Next button

      self.next_button = tk.Button(self, text=">", command=self.next)
      self.next_button.grid(row = 2, column = 19)

      # Overlay button

      overlays = ["map_black", "map_white", "grid_black", "grid_white"]

      self.var6 = tk.StringVar(self)
      self.var6.trace('w', self.check_overlay)
      self.optionmenu6 = tk.OptionMenu(self, self.var6, *overlays)
      tk.Label(self, text="Overlay").grid(row = 1, column = 20, columnspan=3)
      self.optionmenu6.grid(row = 2, column = 20, columnspan=3)

      #  Submit button

      self.submit_button = tk.Button(self, text="Submit", command=self.check_vals)
      self.submit_button.grid(row = 2, column = 23, columnspan=3)

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

      # Save with background button

      self.save_all_button = tk.Button(self, text ='save', command= lambda: self.save_all_crop(self.canvas))
      self.save_all_button.grid(row=3, column=21, columnspan = 3)

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

      self.canvas = tk.Canvas(self.master,height=600,width=900,bd=10, background = 'white')
      self.canvas.pack()

      # Input starting image

      self.im = PIL.Image.open(resource_path("No_image_loaded.png"))
      self.reim = self.im.resize((900,600))
      self.tkim = PIL.ImageTk.PhotoImage(self.reim)
      self.canvas.create_image(900/2+10,600/2+10, image=self.tkim, tags = "back")

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
         
         

   # Update dropdown menus based on selection of type

   def update_type(self, *args):

      # base case list on contents of source of first dropdown menu

      cases = list(self.date_dict[self.var1.get()].keys())

      menu = self.optionmenu2['menu']

      menu.delete(0, 'end')


      for case in cases:

         menu.add_command(label=case, command=lambda cas=case: self.var2.set(cas))

   # Update dropdown menus based on the case study selected

   def update_case(self, *args):

      # base variable list on contents of first dropdown menu

      varis = self.var_dict[self.var1.get()][self.var2.get()]

      menu = self.optionmenu3['menu']

      menu.delete(0, 'end')

      for vari in varis:

         menu.add_command(label=vari, command=lambda var=vari: self.var3.set(var))

   # Update dropdown menus based on the variable selected

   def update_vars(self, *args):

      # base dates list on contents of first and second dropdown menus

      dates = list(self.date_dict[self.var1.get()][self.var2.get()][self.var3.get()])

      menu = self.optionmenu4['menu']

      menu.delete(0, 'end')

      for date in dates:

         menu.add_command(label=date, command=lambda time=date: self.var4.set(time))


      # base fore list on contents of first

      fores = self.fore_dict[self.var1.get()][self.var2.get()][self.var3.get()]

      menu = self.optionmenu5['menu']

      menu.delete(0, 'end')

      for fore in fores:

         menu.add_command(label=fore, command=lambda time=fore: self.var5.set(time))

   # Check the values in the drop down menues are sensible on the use of the submit button, advise on what needs changing or display image

   def check_vals(self, event=None):

      file_type = self.var1.get()
      file_case = self.var2.get()
      file_var = self.var3.get()
      file_date = self.var4.get()
      file_time = self.var5.get()

      if file_type in (list(self.date_dict.keys())):
         if file_case in (list(self.date_dict[file_type].keys())):
            if file_var in (self.var_dict[file_type][file_case]):
               if file_date in (self.date_dict[file_type][file_case][file_var]):
                  if file_time in (self.fore_dict[file_type][file_case][file_var]) or file_var == "Hov":
                     if file_type == "GFS":
                        if file_time == "000":
                           if file_var == "PRATE":
                              file_name = resource_path("No_image_loaded.png")
                              self.status['text']='Precipitation rate not available for analysis step'
                           elif file_var == "DPandHL_2M":
                              file_name = resource_path("No_image_loaded.png")
                              self.status['text']='Heat low metric only valid at 0600 UTC (times = 018 or 042)'
                           else:
                              file_name = file_type+"/"+file_case+"/"+file_var+"/"+file_type+"analysis_"+file_date+"_"+file_var+".png"
                              self.status['text']='Annotate image as required'
                        else:
                           if file_var == "DPandHL_2M" and (file_time == "018" or file_time == "042"):
                              valid_date = (datetime.datetime(int(file_date[:4]), int(file_date[4:6]), int(file_date[6:8]), int(file_date[8:10])) + datetime.timedelta(hours=int(file_time))).strftime("%Y%m%d%H")
                              file_name = file_type+"/"+file_case+"/"+file_var+"/"+file_type+"forecast_"+valid_date+"_"+file_var+"_"+file_date+"_"+file_time+".png"
                              self.status['text']='Annotate image as required'
                           elif file_var == "DPandHL_2M":
                              file_name = resource_path("No_image_loaded.png")
                              self.status['text']='Heat low metric only valid at 0600 UTC (times = 018 or 042)'
                           else:
                              valid_date = (datetime.datetime(int(file_date[:4]), int(file_date[4:6]), int(file_date[6:8]), int(file_date[8:10])) + datetime.timedelta(hours=int(file_time))).strftime("%Y%m%d%H")
                              file_name = file_type+"/"+file_case+"/"+file_var+"/"+file_type+"forecast_"+valid_date+"_"+file_var+"_"+file_date+"_"+file_time+".png"
                              self.status['text']='Annotate image as required'
                     else:

                        if file_var == "IR" or file_var == "VIS" or file_var == "WV":
                           file_name = glob.glob(file_type+"/"+file_case+"/"+file_var+"/SEVIRI_"+file_date+file_time[1:]+"*_"+file_var+"_*.png")[0]
                           self.status['text']='Annotate image as required'
                        elif file_var == "precip":
                           file_name = file_type+"/"+file_case+"/"+file_var+"/TRMM_"+file_date+file_time[1:]+"_"+file_var+".png"   
                        elif file_var == "Hov":
                           file_name = glob.glob(file_type+"/"+file_case+"/"+file_var+"/Hovmoeller_"+file_date+"*.png")[0]

                     self.im = PIL.Image.open(file_name)
                     self.reim = self.im.resize((900,600))
                     self.tkim = PIL.ImageTk.PhotoImage(self.reim)
                     self.canvas.delete(self.tkim)
                     self.canvas.create_image(900/2+10,600/2+10, image=self.tkim, tags = "back")
                     self.canvas.tag_raise("lines")

                  else:
                     self.status['text']='Please select appropriate time'
               else:
                  self.status['text']='Please select appropriate date'
            else:
               self.status['text']='Please select appropriate variable'
         else:
            self.status['text']='Please select appropriate case'
      else:
         self.status['text']='Please select appropriate type'

   # Check the values in the drop down menues are sensible on the use of the submit button, advise on what needs changing or display image

   def check_overlay(self, *args):

      file_var = self.var6.get()

      ol_file_name = resource_path(file_var+".png")

      self.olim = PIL.Image.open(ol_file_name)
      self.olreim = self.olim.resize((900,600))

      globals()["oltkim%04d" % self.linecount] = PIL.ImageTk.PhotoImage(self.olreim)
      
      self.canvas.create_image(900/2+10,600/2+10, image=globals()["oltkim%04d" % self.linecount], tags = ("lines", "%04d" % self.linecount))
      self.linecount = self.linecount + 1

   # Set background image to previous time

   def previous(self, event=None):

      file_type = self.var1.get()
      file_case = self.var2.get()
      file_var = self.var3.get()
      file_date = self.var4.get()
      file_time = self.var5.get()

      file_time = self.var5.get()
      if file_time == "":
         file_time = "000"
      elif file_type == "GFS":
         if file_time == "000":
            file_time = "000"
         else:
            file_time = "%03d" % (int(file_time)-3)
      else:
         if file_time == "000":
            date_pos = self.date_dict[file_type][file_case][file_var].index(file_date)
            if(date_pos > 0):
               file_time = "021"
               file_date = self.date_dict[file_type][file_case][file_var][date_pos-1]
               self.var4.set(file_date)
         else:
            file_time = "%03d" % (int(file_time)-3)

      self.var5.set(file_time)
      self.check_vals()

   # Set background image to previous time

   def next(self, event=None):

      file_type = self.var1.get()
      file_case = self.var2.get()
      file_var = self.var3.get()
      file_date = self.var4.get()
      file_time = self.var5.get()

      if file_time == "":
         file_time = "000"
      elif file_type == "GFS":
         if file_time >= "048":
            file_time = "048"
         else:
            file_time = "%03d" % (int(file_time)+3)
      else:
         if file_time >= "021":
            list_len = len(self.date_dict[file_type][file_case][file_var])
            date_pos = self.date_dict[file_type][file_case][file_var].index(file_date)
            if(date_pos+1 < list_len):
               file_time = "000"
               file_date = self.date_dict[file_type][file_case][file_var][date_pos+1]
               self.var4.set(file_date)
         else:
            file_time = "%03d" % (int(file_time)+3)

      self.var5.set(file_time)
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


