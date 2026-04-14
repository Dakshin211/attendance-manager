import csv
import datetime
from tkinter import *
from tkinter import messagebox
import cv2
import mysql.connector as msc
import PIL
import schedule
from PIL import ImageTk
mode = ''
con = msc.connect(host="localhost",user="root",passwd="tiger",database="att_man")
cursor = con.cursor()

time = datetime.datetime.now()
t_adding_time = time.replace(hour=00, minute=00, second=0, microsecond=0)

cursor.execute('select day(curdate())')
d = cursor.fetchall()
day = d[0][0]
day = str(day)
cursor.execute('select month(curdate())')
m = cursor.fetchall()
month = m[0][0]
cursor.execute('select year(curdate())')
y = cursor.fetchall()
year = y[0][0]
year = str(year)
    
def month_converter(month):
    if month == 1:
        month = 'Jan'
    elif month == 2:
        month = 'Feb'
    elif month == 3:
        month = 'March'
    elif month == 4:
        month = 'Aprl'
    elif month == 5:
        month = 'May'
    elif month == 6:
        month = 'June'
    elif month == 7:
        month = 'July'
    elif month == 8:
        month = 'Aug'
    elif month == 9:
        month = 'Sep'
    elif month == 10:
        month = 'Oct'
    elif month == 11:
        month = 'Nov'
    elif month == 12 or month==0:
        month = 'Dec'
    return month
    
t_date = day+'_'+month_converter(month)+'_'+year
col_name = t_date+'_trans'
teachtable = "teach_att_"+month_converter(month)+"_"+year
stutable = "stu_att_"+month_converter(month)+"_"+year

def abs_fail_corrrector(table):
    check_column  = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = Database() AND TABLE_NAME ='"+table+"';"
    cursor.execute(check_column)
    columns = cursor.fetchall()
    if len(columns) > 2:
        last_day = columns[len(columns)-2][0]
        col_name = columns[len(columns)-1][0]
        q = "select id from %s where %s is null "%(table,last_day)
        cursor.execute(q)
        abs = cursor.fetchall()
        if abs != []:
            abs_query = f"update {table} set {last_day} = 'AA' where {last_day} is null"
            trans_query = f"update {table} set {col_name} = '-' where {col_name} is null"
            cursor.execute(abs_query)
            cursor.execute(trans_query)
            con.commit()
        elif abs == []:
            pass
  
def table_adder(table):
    all_tables = []
    all_ids = []
    cursor.execute("show tables")
    all_t = cursor.fetchall()
    for t in range(len(all_t)):
        tab = all_t[t][0]
        all_tables.append(tab)
    if table not in all_tables:
        try:
            t_a_query = f"create table {table} (ID int);"
            cursor.execute(t_a_query)
            if table == teachtable:
                db_tab = "teach_db"
            elif table == stutable:
                db_tab = "stu_db"
                
            id_add = f"select id from {db_tab}"
            cursor.execute(id_add)
            all_id = cursor.fetchall()
            for i in range(len(all_id)):
                idd = all_id[i][0]
                all_ids.append(idd)
            for j in all_ids:
                ins_query = "insert into %s(ID) values (%s)"%(table,j)
                cursor.execute(ins_query)
                con.commit()
            prev_teachtable = "teach_att_"+month_converter(month-1)+"_"+year
            prev_stutable = "stu_att_"+month_converter(month-1)+"_"+year
        except:
            return 0
        # will check later
        abs_fail_corrrector(prev_teachtable)
        abs_fail_corrrector(prev_stutable)

table_adder(teachtable)
table_adder(stutable)

collumns = []
def day_adder(table):
    check_column  = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = Database() AND TABLE_NAME ='{table}';"
    cursor.execute(check_column)
    columns = cursor.fetchall()

    for cols in columns:
        all_cols = list(cols)
        collumns.append(all_cols)
    column_in_str = [' '.join([str(d3) for d3 in lst_2 ]) for lst_2 in collumns]
    if time > t_adding_time :
        if t_date not in column_in_str :
            q_for_add = f"alter table {table} add {t_date} varchar(5);"
            q_for_com = f"alter table {table} add {col_name} varchar(30);"
            cursor.execute(q_for_add)
            cursor.execute(q_for_com)

def registering(tab_name,ID):
    now = datetime.datetime.now()
    checkin = now.replace(hour=8, minute=30, second=0, microsecond=0)
    first_half = now.replace(hour=11, minute=30, second=0, microsecond=0)
    second_half = now.replace(hour=14, minute=40, second=0, microsecond=0)

    if now == checkin or now < checkin:
        att = "PP"
       
    elif now > checkin and now < first_half :
        att = "PPL"
      
    elif now >= first_half and now < second_half:
        att = "AP"
    elif now > second_half:
        att="AA"
        
    ID = int(ID)
    if tab_name == "stu_db":
        table = stutable
    elif tab_name == "teach_db":
        table = teachtable

    ID_formate_list = []
    cursor.execute(f"select ID from {table}")
    ID_unformate_list = cursor.fetchall()
    for ids in range (len(ID_unformate_list)):
        ele = ID_unformate_list[ids][0]
        ID_formate_list.append(ele)

    if ID in ID_formate_list:
        check_query_day = "select %s from %s where id = %s"%(t_date,table,ID)
        cursor.execute(check_query_day)
        update_check = cursor.fetchall()
        print(update_check)
        if update_check[0][0] == None:
            attendance_query = f"update {table} set {t_date} = '{att}' where ID = {ID};"
            transporation_query = f"update {table} set {col_name} = '{v.get()}' where ID = {ID};"
            cursor.execute(attendance_query)
            cursor.execute(transporation_query)
            con.commit()
            messagebox.showinfo('INFO','Attendance has been registered .')
        else:
            messagebox.showinfo("ID",f"Attendance for {ID} is already registered")
    elif ID not in ID_formate_list:
        messagebox.showerror('ERROR','No such id is found !!')


def scan_QR(tablename):
    try:
        cap = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()
        while True :
            _,img=cap.read()
            data,one,_ = detector.detectAndDecode(img)
            if data :
                ID_number = data
                break
            cv2.imshow('QR Code Scanner ~~ Press "s" to stop' , img)
            if cv2.waitKey(1)==ord('s'):
                break
    except:
        messagebox.showerror("ERROR","Check if your camera is connected !")
    
    try:
        cv2.destroyAllWindows()
        checkid = messagebox.askyesno("CONFORMATION",f"Is your ID {ID_number}")
        if checkid == True:
            registering(tablename,ID_number)
            messagebox.showinfo('INFO','Attendance has been registered .')
    except:
        pass

def password(winname):
    help_win = Toplevel()
    help_win.geometry("319x222")
    help_win.title("Conformation")
    help_win.resizable(False,False)
        
    help_image_obj = PIL.Image.open(r"image2/passwin.png")
    help_image = ImageTk.PhotoImage(help_image_obj)
    l = Label(help_win , image= help_image)
    l.pack()
    help_enter_obj = PIL.Image.open(r"image2/help_enter.png")
    enter_image = ImageTk.PhotoImage(help_enter_obj)
    global user_entry
    user_entry = StringVar()
    user_entry.set('')
    entry = Entry(help_win, font=("Lucida Console",20,"bold italic"),width=9,relief=FLAT,bg="#abc0ff",cursor="hand2",textvariable=user_entry)
    entry.config(highlightbackground="#abc0ff",border=0,highlightcolor="#abc0ff")
    entry.place(relx=0.2,rely=0.2)
    def butt_func():
        password = entry.get()
        with open('loginpassword.csv', 'r') as file:
            csvfile = csv.reader(file)
            for row in csvfile:
                if row[1] == password:
                    messagebox.showinfo("Successful", "NOW YOU CAN ACCESS DATABASE")
                    winname.destroy()
                    new_attendance()  
                else:
                    messagebox.showerror("ERROR", "Check your password")
                    entry.delete(0,END)     
    enter_button = Button(help_win,image=enter_image,bg="#ffffff",command=butt_func)
    enter_button.config(highlightbackground="#ffffff",border=0, highlightcolor="#ffffff")
    enter_button.place(relx=0.34,rely=0.63)

    help_win.mainloop()

def new_attendance():
    # whom the attendance is for :
    table = userchoice_var
    # window for asking details 
    new_win = Tk()
    new_win.geometry("1366x720")
    new_win.title("New Attendance")
    new_win.resizable(False,False)
    #image imports 
    win_image_obj = PIL.Image.open(r"image2/new_att1.png")
    win_image = ImageTk.PhotoImage(win_image_obj)
    win_widget = Label(new_win, image = win_image)
    win_widget.pack()
    new_win.mainloop()

def help(tablename):
    global help_win
    help_win = Toplevel()
    help_win.geometry("319x222")
    help_win.title("HELPER")
    help_win.resizable(False,False)
    help_image_obj = PIL.Image.open(r"image2/helpwin.png")
    help_image = ImageTk.PhotoImage(help_image_obj)
    l = Label(help_win , image= help_image)
    l.pack()

    help_enter_obj = PIL.Image.open(r"image2/help_enter.png")
    enter_image = ImageTk.PhotoImage(help_enter_obj)

    global username_entry
    username_entry = StringVar()
    username_entry.set('')

    ID_entry = Entry(help_win, font=("Lucida Console",20,"bold italic"),width=9,relief=FLAT,bg="#abc0ff",cursor="hand2",textvariable=username_entry)
    ID_entry.config(highlightbackground="#abc0ff",border=0,highlightcolor="#abc0ff")
    ID_entry.place(relx=0.2,rely=0.2)
    def butt_func():
        global help_ID
        help_ID = username_entry.get()
        #try :
        if len(help_ID) < 4 or len(help_ID) > 4:
                messagebox.showerror("ERROR", "Enter the ID properly")
                help_win.destroy()
                help(tablename)
        elif len(help_ID) == 4:
                global ID_help
                ID_help = int(help_ID)
                registering(tablename,ID_help)
                help_win.destroy()

    enter_button = Button(help_win,image=enter_image,bg="#ffffff",command=butt_func)
    enter_button.config(highlightbackground="#ffffff",border=0, highlightcolor="#ffffff")
    enter_button.place(relx=0.34,rely=0.63)

    help_win.mainloop()


def mainpage(tablename):
    scan_win = Tk()
    scan_win.geometry("1366x720")
    if userchoice_var.get() == 'stu_db':
        title = "ATTENDANCE REGISTER (Student)"
    elif userchoice_var.get() == 'teach_db':
        title = "ATTENDANCE REGISTER (Teacher)"
    scan_win.title(title)
    scan_win.resizable(False,False)
    # importing images
    scan_win_bg_obj = PIL.Image.open(r"image2/scanpage.png")
    scan_win_bg_image = ImageTk.PhotoImage(scan_win_bg_obj)
    scan_win_bg_widget = Label(scan_win, image=scan_win_bg_image)
    scan_win_bg_widget.pack()

    bike_button_obj = PIL.Image.open(r"image2/bike_button.png")
    bike_button_image = ImageTk.PhotoImage(bike_button_obj)
    cycle_button_obj = PIL.Image.open(r"image2/cycle_button.png")
    cycle_button_image = ImageTk.PhotoImage(cycle_button_obj)
    walk_button_obj = PIL.Image.open(r"image2/walk_button.png")
    walk_button_image = ImageTk.PhotoImage(walk_button_obj)
    bustrain_button_obj = PIL.Image.open(r"image2/bustrain_button.png")
    bustrain_button_image = ImageTk.PhotoImage(bustrain_button_obj)
    others_button_obj = PIL.Image.open(r"image2/others_button.png")
    others_button_image = ImageTk.PhotoImage(others_button_obj)
    scan_button_obj = PIL.Image.open(r"image2/scan_button.png")
    scan_button_image = ImageTk.PhotoImage(scan_button_obj)
    help_button_obj = PIL.Image.open(r"image2/helpbutton.png")
    help_button_image = ImageTk.PhotoImage(help_button_obj)
    
    # toggle menu images
    toggle_button_obj = PIL.Image.open(r"image2/toggle_button.png")
    toggle_button_image = ImageTk.PhotoImage(toggle_button_obj)
    toggle_menu_obj = PIL.Image.open(r"image2/mainpage_toggle.png")
    toggle_menu_image = ImageTk.PhotoImage(toggle_menu_obj)
    toggle_new_attendance_obj = PIL.Image.open(r"image2/new_attendance_button.png")
    toggle_new_attendance_image = ImageTk.PhotoImage(toggle_new_attendance_obj)
    toggle_prev_obj = PIL.Image.open(r"image2/go_back_button.png")
    toggle_prev_image = ImageTk.PhotoImage(toggle_prev_obj)
    toggle_logout_obj = PIL.Image.open(r"image2/logout_button.png")
    toggle_logout_image = ImageTk.PhotoImage(toggle_logout_obj)
    toggle_back_obj = PIL.Image.open(r"image2/toggle_back_button.png")
    toggle_back_image = ImageTk.PhotoImage(toggle_back_obj)
    toggle_leaving_obj = PIL.Image.open(r"image2/toggle_leaving_button.png")
    toggle_leaving_image = ImageTk.PhotoImage(toggle_leaving_obj)

    def goback():
        scan_win.destroy()
        whoareyou()
    def logout():
        scan_win.destroy()
        loginpage()
    def leaving():
        pass

    # toggle menu function
    def togglemenu():
        toggle_menu = Frame(scan_win, height=720,width=381)
        toggle_menu.place(relx=0,rely=0)
        toggle_img = Label(toggle_menu, image=toggle_menu_image)
        toggle_img.place(relx=0,rely=0)
        leaving_button = Button(toggle_menu, image=toggle_leaving_image,relief=FLAT, bg="#4823D4", cursor="hand2",command=leaving)
        leaving_button.config(highlightbackground="#4823D4",border=0, highlightcolor="#4823D4")
        leaving_button.place(relx=0.05,rely=0.344)
        goback_button = Button(toggle_menu, image=toggle_prev_image,relief=FLAT, bg="#4823D4", cursor="hand2",command=goback)
        goback_button.config(highlightbackground="#4823D4",border=0, highlightcolor="#4823D4")
        goback_button.place(relx=0.05,rely=0.472)
        logout_button = Button(toggle_menu, image=toggle_logout_image,relief=FLAT, bg="#4823D4", cursor="hand2",command=logout)
        logout_button.config(highlightbackground="#4823D4",border=0, highlightcolor="#4823D4")
        logout_button.place(relx=0.05,rely=0.6)
        tog_back = Button(toggle_menu, image=toggle_back_image,relief=FLAT, bg="#4823D4", cursor="hand2",command= toggle_menu.destroy)
        tog_back.config(highlightbackground="#4823D4",border=0, highlightcolor="#4823D4")
        tog_back.place(relx=0.035,rely=0.018)



    # adding buttons
    def transport_options():
        def meansoftrans():
            global return_trans
            
            global v
            v = StringVar()
            v.set("bike")
            R1 = Radiobutton(scan_win,image=bike_button_image, variable=v, value="bike", relief=FLAT, borderwidth=0,cursor="hand2",)
            R1.config(highlightbackground="white", highlightcolor="white")
            R1.place(relx=0.465, rely=0.662)
            R2 = Radiobutton(scan_win,image=cycle_button_image, variable=v, value="cycle", relief=FLAT, borderwidth=0,cursor="hand2")
            R2.config(highlightbackground="white", highlightcolor="white")
            R2.place(relx=0.465, rely=0.716)
            R3 = Radiobutton(scan_win,image=walk_button_image, variable=v, value="walk", relief=FLAT, borderwidth=0,cursor="hand2")
            R3.config(highlightbackground="white", highlightcolor="white")
            R3.place(relx=0.465, rely=0.768)
            R4 = Radiobutton(scan_win,image=bustrain_button_image, variable=v, value="bus/train", relief=FLAT, borderwidth=0,cursor="hand2")
            R4.config(highlightbackground="white", highlightcolor="white")
            R4.place(relx=0.465, rely=0.82)
            R5 = Radiobutton(scan_win,image=others_button_image, variable=v, value="others", relief=FLAT, borderwidth=0,cursor="hand2")
            R5.config(highlightbackground="white", highlightcolor="white")
            R5.place(relx=0.465, rely=0.865)
        meansoftrans()
    
    toggle_button = Button(scan_win, image=toggle_button_image,relief=FLAT, bg="#e6e6ee", cursor="hand2",command=togglemenu)
    toggle_button.config(highlightbackground="#e6e6ee",border=0, highlightcolor="#e6e6ee")
    toggle_button.place(relx=0.019,rely=0.021)

    scan_button = Button(scan_win, image=scan_button_image,relief=FLAT, bg="#ffffff", cursor="hand2",command=lambda:scan_QR(tablename))

    scan_button.config(highlightbackground="white",border=0, highlightcolor="white")
    scan_button.place(relx=0.285,rely=0.42)
    
    help_button = Button(scan_win, image= help_button_image,relief=FLAT, bg="#ffffff", cursor="hand2",command=lambda:help(tablename))
    help_button.config(highlightbackground="white",border=0, highlightcolor="white")
    help_button.place(relx=0.428,rely=0.514)

    transport_options()
    scan_win.mainloop()

global whoareyou
# student/teacher selection
def whoareyou():
    #functions within whoareyou
    def active_student_button(event):
        student_button.config(image=active_student_button_image)
    def not_active_student_button(event):
        student_button.config(image=student_button_image)
    def active_teacher_button(event):
        teacher_button.config(image=active_teacher_button_image)
    def not_active_teacher_button(event):
        teacher_button.config(image=teacher_button_image)
    def active_go_button(event):
        go_button.config(image=active_go_button_image)
    def not_active_go_button(event):
        go_button.config(image=go_button_image)

    def nextpage(userchoice):
        if userchoice == "":
            messagebox.showerror("ERROR", "Choose any Option")
        else:
            tab_name = userchoice.get()
            page2.destroy()
            mainpage(tab_name)
            
        
    # creating ui for who are you page
    page2 = Tk()
    page2.geometry("1366x720")
    page2.title("ATTENDANCE REGISTER")
    page2.resizable(False,False)
    page2.pack_propagate(False)
 
    
    # importing images
    page2_bg_obj = PIL.Image.open(r"image2/page2.png")
    page2_bg_image = ImageTk.PhotoImage(page2_bg_obj)
    page2_bg_widget = Label(page2, image=page2_bg_image)
    page2_bg_widget.pack()

    student_button_image_obj = PIL.Image.open(r"image2/student.png")
    student_button_image = ImageTk.PhotoImage(student_button_image_obj)
    active_student_button_image_obj = PIL.Image.open(r"image2/student_click.png")
    active_student_button_image = ImageTk.PhotoImage(active_student_button_image_obj)
    
    teacher_button_image_obj = PIL.Image.open(r"image2/teacher.png")
    teacher_button_image = ImageTk.PhotoImage(teacher_button_image_obj)
    active_teacher_button_image_obj = PIL.Image.open(r"image2/teacher_click.png")
    active_teacher_button_image = ImageTk.PhotoImage(active_teacher_button_image_obj)
    
    go_button_image_obj = PIL.Image.open(r"image2/go.png")
    go_button_image = ImageTk.PhotoImage(go_button_image_obj)
    active_go_button_image_obj = PIL.Image.open(r"image2/go_click.png")
    active_go_button_image = ImageTk.PhotoImage(active_go_button_image_obj)

    # toggle menu images
    toggle_button_obj = PIL.Image.open(r"image2/toggle_button.png")
    toggle_button_image = ImageTk.PhotoImage(toggle_button_obj)
    toggle_menu_obj = PIL.Image.open(r"image2/toggle_frame.png")
    toggle_menu_image = ImageTk.PhotoImage(toggle_menu_obj)
    toggle_del_obj = PIL.Image.open(r"image2/del_attendance.png")
    toggle_del_image = ImageTk.PhotoImage(toggle_del_obj)
    toggle_new_attendance_obj = PIL.Image.open(r"image2/new_attendance_button.png")
    toggle_new_attendance_image = ImageTk.PhotoImage(toggle_new_attendance_obj)
    toggle_prev_obj = PIL.Image.open(r"image2/go_back_button.png")
    toggle_prev_image = ImageTk.PhotoImage(toggle_prev_obj)
    toggle_logout_obj = PIL.Image.open(r"image2/logout_button.png")
    toggle_logout_image = ImageTk.PhotoImage(toggle_logout_obj)
    toggle_back_obj = PIL.Image.open(r"image2/toggle_back_button.png")
    toggle_back_image = ImageTk.PhotoImage(toggle_back_obj)
    
    def goback():
        page2.destroy()
        loginpage()
    def del_attendance():
        mode = 'del'
        password(page2)
    def new_att_choice():
        mode = 'add'
        password(page2)
    def view_detail():
        pass

    # toggle menu function
    def togglemenu():
        toggle_menu = Frame(page2, height=720,width=381)
        toggle_menu.place(relx=0,rely=0)
        toggle_img = Label(toggle_menu, image=toggle_menu_image)
        toggle_img.place(relx=0,rely=0)
        new_att_button = Button(toggle_menu, image=toggle_new_attendance_image,relief=FLAT, bg="#4823D4", cursor="hand2",command=new_att_choice)
        new_att_button.config(highlightbackground="#4823D4",border=0, highlightcolor="#4823D4")
        new_att_button.place(relx=0.05,rely=0.344)
        del_button = Button(toggle_menu, image=toggle_del_image,relief=FLAT, bg="#4823D4", cursor="hand2",command=del_attendance)
        del_button.config(highlightbackground="#4823D4",border=0, highlightcolor="#4823D4")
        del_button.place(relx=0.05,rely=0.476)
        goback_button = Button(toggle_menu, image=toggle_prev_image,relief=FLAT, bg="#4823D4", cursor="hand2",command=goback)
        goback_button.config(highlightbackground="#4823D4",border=0, highlightcolor="#4823D4")
        goback_button.place(relx=0.05,rely=0.6)
        logout_button = Button(toggle_menu, image=toggle_logout_image,relief=FLAT, bg="#4823D4", cursor="hand2",command=goback)
        logout_button.config(highlightbackground="#4823D4",border=0, highlightcolor="#4823D4")
        logout_button.place(relx=0.05,rely=0.728)
        tog_back = Button(toggle_menu, image=toggle_back_image,relief=FLAT, bg="#4823D4", cursor="hand2",command= toggle_menu.destroy)
        tog_back.config(highlightbackground="#4823D4",border=0, highlightcolor="#4823D4")
        tog_back.place(relx=0.035,rely=0.018)
    
    # creating buttons
    global userchoice_var
    userchoice_var = StringVar()
    userchoice_var.set("stu_db")

    student_button = Radiobutton(page2, image=student_button_image,relief=FLAT,bg="#ffffff",variable=userchoice_var,value="stu_db",cursor="hand2")
    student_button.config(highlightbackground="white",border=0,highlightcolor="white")
    student_button.place(relx=0.5976,rely=0.45)

    teacher_button = Radiobutton(page2, image=teacher_button_image, relief=FLAT,bg="#ffffff",value="teach_db",variable=userchoice_var, cursor="hand2")
    teacher_button.config(highlightbackground="white",border=0, highlightcolor="white")
    teacher_button.place(relx=0.5976, rely=0.57)
    
    go_button = Button(page2, image=go_button_image,relief=FLAT, bg="#ffffff", cursor="hand2",command=lambda:nextpage(userchoice_var))
    go_button.config(highlightbackground="white",border=0, highlightcolor="white")
    go_button.place(relx=0.628, rely=0.68)

    toggle_button = Button(page2, image=toggle_button_image,relief=FLAT, bg="#e6e6ee", cursor="hand2",command=togglemenu)
    toggle_button.config(highlightbackground="#e6e6ee",border=0, highlightcolor="#e6e6ee")
    toggle_button.place(relx=0.019,rely=0.021)
  
    #key binding
    student_button.bind("<Enter>",active_student_button)
    student_button.bind("<Leave>",not_active_student_button)
    teacher_button.bind("<Enter>", active_teacher_button)
    teacher_button.bind("<Leave>", not_active_teacher_button)
    go_button.bind("<Enter>", active_go_button)
    go_button.bind("<Leave>", not_active_go_button)
    page2.mainloop()

# login function
def login(username, password):
    with open('loginpassword.csv', 'r') as file:
        csvfile = csv.reader(file)
        for row in csvfile:
            if row[0] == username and row[1] == password:
                # creating daily columns in monthly table
                day_adder(teachtable)
                day_adder(stutable)

                messagebox.showinfo("Successful", "LOGIN SUCCESSFUL")
                app.destroy()
                whoareyou()

            else:
                messagebox.showerror("ERROR", "Check your username or password")
                username_entry.delete(0,END)
                password_entry.delete(0,END)

# main login page ui
def loginpage():
    # functions within loginpage :
    def button_function():
        login(username_entry.get(), password_entry.get())
    def entry(event):
        login(username_entry.get(), password_entry.get())
    def enter(event):
        login_button.config(image=active_login_button_image)
    def leave(event):
        login_button.config(image=login_button_image)
    
    # creating window 
    global app
    app = Tk()
    app.title("ATTENDANCE REGISTER")
    app.geometry("1366x720")
    app.resizable(False,False)
    #image imports 
    login_image_obj = PIL.Image.open(r"image2/prototype.png")
    login_image = ImageTk.PhotoImage(login_image_obj)
    login_widget = Label(app, image = login_image)
    login_widget.pack()
    
    login_button_obj = PIL.Image.open(r"image2/login3.png")
    login_button_image = ImageTk.PhotoImage(login_button_obj)
    
    active_login_button_obj = PIL.Image.open(r"image2/login2_click.png")
    active_login_button_image = ImageTk.PhotoImage(active_login_button_obj)
    
    #button functions
    global username_entry
    global password_entry
    
    username_entry = Entry(app, font=("Lucida Console",13,"bold italic"),width=18,relief=FLAT,bg="#abc0ff",cursor="hand2")
    username_entry.config(highlightbackground="#abc0ff",border=0,highlightcolor="#abc0ff")
    username_entry.place(relx=.615,rely=.44)
    
    password_entry = Entry(app, font=("Lucida Console", 13, "bold"),width=18, relief=FLAT, bg="#abc0ff", cursor="hand2", show="•")
    password_entry.config(highlightbackground="#abc0ff",border=0, highlightcolor="#abc0ff")
    password_entry.place(relx=.615, rely=.5835)
    
    login_button = Button(app,image=login_button_image,bg="#ffffff",command=button_function)
    login_button.config(highlightbackground="#ffffff",border=0, highlightcolor="#ffffff")
    login_button.place(relx=0.633,rely=0.695)

    # key binding
    app.bind("<Return>", entry)
    login_button.bind("<Enter>",enter)
    login_button.bind("<Leave>",leave)
    

    app.mainloop()
    

if __name__ == "__main__":
    loginpage()

def allabsent(table):
    now = datetime.datetime.now()
    going_time = now.replace(hour=14, minute=40, second=0, microsecond=0)
    if now < going_time :
        return 0 
    elif now > going_time :
        null_q = "select ID from %s where %s is null"%(table,t_date)
        cursor.execute(null_q)
        global data
        data = cursor.fetchall()
        if data != []:
            print('yes')
            absent_query = f"update {table} set {t_date} = 'AA' where {t_date} is null"
            trans_query = f"update {table} set {col_name} = '-' where {col_name} is null"
            cursor.execute(absent_query)
            cursor.execute(trans_query)
            con.commit()
schedule.every(10).seconds.do(lambda:allabsent(teachtable))
schedule.every(10).seconds.do(lambda:allabsent(stutable))
while True:
    schedule.run_pending()
    null_check_stu = f"select ID from {teachtable} where {t_date} is null"
    cursor.execute(null_check_stu)
    data_of_teach = cursor.fetchall()
    null_check_teach = f"select ID from {stutable} where {t_date} is null"
    cursor.execute(null_check_teach)
    data_of_stu = cursor.fetchall()
    if data_of_stu == [] and data_of_teach ==[]:
        break
