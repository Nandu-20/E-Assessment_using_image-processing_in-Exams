
from tkinter import messagebox
from tkinter import *
from tkinter import simpledialog
import tkinter
from tkinter.filedialog import askopenfilename
from tkinter import simpledialog
from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import matplotlib.pyplot as plt
import time


confid = 0.5
thresh = 0.5
mouse_pts = []



main = tkinter.Tk()
main.title("Faculty Login Screen")
main.geometry("1200x800")

global paper
global newwin

ANSWER_KEY = {0: 1, 1: 4, 2: 0, 3: 3, 4: 1}

global password_login_entry
global username_login_entry

global username_verify
global password_verify

 
username_verify = StringVar()
password_verify = StringVar()


def uploadPaper():
    global newwin
    sname = simpledialog.askstring("Enter Student Name", "Enter Student Name",parent=newwin)
    global paper
    paper = askopenfilename(initialdir = "images")
    print("[INFO] accessing image ..paper .",paper)
    image = cv2.imread(paper)
    
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    docCnt = None

    if len(cnts) > 0:
       cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
       for c in cnts:
          peri = cv2.arcLength(c, True)
          approx = cv2.approxPolyDP(c, 0.02 * peri, True)
          if len(approx) == 4:
             docCnt = approx
             break

    paper = four_point_transform(image, docCnt.reshape(4, 2))
    warped = four_point_transform(gray, docCnt.reshape(4, 2))

    thresh = cv2.threshold(warped, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    questionCnts = []

    for c in cnts:
       (x, y, w, h) = cv2.boundingRect(c)
       ar = w / float(h)

       if w >= 20 and h >= 20 and ar >= 0.9 and ar <= 1.1:
          questionCnts.append(c)

    questionCnts = contours.sort_contours(questionCnts,method="top-to-bottom")[0]
    correct = 0

    for (q, i) in enumerate(np.arange(0, len(questionCnts), 5)):
       cnts = contours.sort_contours(questionCnts[i:i + 5])[0]
       bubbled = None
       for (j, c) in enumerate(cnts):
          mask = np.zeros(thresh.shape, dtype="uint8")
          cv2.drawContours(mask, [c], -1, 255, -1)
          mask = cv2.bitwise_and(thresh, thresh, mask=mask)
          total = cv2.countNonZero(mask)
          if bubbled is None or total > bubbled[0]:
             bubbled = (total, j)

       color = (0, 0, 255)
       k = ANSWER_KEY[q]

       if k == bubbled[1]:
          color = (0, 255, 0)
          correct += 1
       cv2.drawContours(paper, [cnts[k]], -1, color, 3)

    score = (correct / 5.0) * 100
    f = open("marks.txt", "a+")
    f.write(sname+","+str(score)+"\n")
    f.close()
    print("[INFO] score: {:.2f}%".format(score))
    cv2.putText(paper, "{:.2f}%".format(score), (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    cv2.imshow("Original", image)
    cv2.imshow("Exam", paper)
    cv2.waitKey(0)
    

def marksGraph():
    names = []
    marks = []

    # Read data from marks.txt
    with open("marks.txt", "r") as file:
        for line in file:
            line = line.strip('\n')
            arr = line.split(",")
            names.append(arr[0])
            marks.append(float(arr[1]))

    # Create Bar Graph
    plt.figure(figsize=(10, 5))
    plt.title("Student Marks Comparison", fontsize=18)
    plt.bar(names, marks)

    # Labels
    plt.xlabel("Student Names", fontsize=12)
    plt.ylabel("Marks (%)", fontsize=12)

    # Display values above bars
    for i, v in enumerate(marks):
        plt.text(i, v + 1, f"{v:.1f}", ha='center', fontsize=10)

    plt.ylim(0, 110)   # Marks out of 100
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    plt.show()

   

def loadPaper():
    global main
    global newwin

    font1 = ('times', 14, 'bold')
    newwin = Toplevel(main)
    newwin.geometry("1200x1200")
    main.withdraw()
    
    
    uploadbutton = Button(newwin, text="Upload MCQ Paper", command=uploadPaper)
    uploadbutton.place(x=400,y=50)
    uploadbutton.config(font=font1)  

    markschart = Button(newwin, text="View Marks Graph", command=marksGraph)
    markschart.place(x=400,y=100)
    markschart.config(font=font1)

def viewmarks():
    index = 0
    sname = simpledialog.askstring("Enter Your Name", "Enter Your Name",parent=main)
    with open("marks.txt", "r") as file:
       for line in file:
          line = line.strip('\n')
          arr = line.split(",")
          if arr[0] == sname:
             messagebox.showinfo("View Marks Screen","Your Marks : "+arr[1])
             index = 1	   
    if index == 0:
       messagebox.showinfo("View Marks Screen","Given name does not exists")    

    

def login():
    global password_login_entry
    global username_login_entry
    username = username_verify.get()
    password = password_verify.get()

    username_login_entry.delete(0, END)
    password_login_entry.delete(0, END)    

    if username == 'faculty' and password == 'faculty':
       loadPaper()
    else:
       messagebox.showinfo("Invalid Login Details","Invalid Login Details")       


font = ('times', 20, 'bold')
title = Label(main, text='E-ASSESSMENT USING IMAGE PROCESSING IN ∞EXAMS')
title.config(bg='brown', fg='white')  
title.config(font=font)           
title.config(height=3, width=80)       
title.place(x=5,y=5)

font1 = ('times', 14, 'bold')

l1 = Label(main, text="Username * ")
l1.place(x=500,y=150)
l1.config(font=font1)  
username_login_entry = Entry(main, textvariable=username_verify)
username_login_entry.place(x=650,y=150)

l2 = Label(main, text="Password * ")
l2.place(x=500,y=200)
l2.config(font=font1)  
password_login_entry = Entry(main, textvariable=password_verify, show= '*')
password_login_entry.place(x=650,y=200)



upload = Button(main, text="Login", command=login)
upload.place(x=550,y=250)
upload.config(font=font1)  

viewmark = Button(main, text="Student View Marks", command=viewmarks)
viewmark.place(x=550,y=300)
viewmark.config(font=font1)

main.config(bg='skyblue')
main.mainloop()
