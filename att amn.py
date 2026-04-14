import cv2
import datetime
from tkinter import *
from tkcalendar import *
from tkinter import ttk
from tkinter import messagebox
import mysql.connector as msc

con = msc.connect(host='localhost', user='root', passwd='Dak@021105', database='att_man')
cursor = con.cursor()

cursor.execute("select curdate()")
dat = cursor.fetchall()
dat = str(dat[0][0])
year = dat[0:4]
month = dat[5:7]
day = dat[8:10]

teach_table = year+'_'+month+'_'+'teach_att'
stu_table = year+'_'+month+'_'+'stu_att'
date = year+'_'+month+'_'+day
date_tran = year+'_'+month+'_'+day+'_transport'
stu = 'student'
teach = 'teacher'

def id_validater(Id):
    condition = None
    cursor.execute("select id from %s" % (stu_table,))
    al_s_ids = cursor.fetchall()
    cursor.execute("select id from %s" % (teach_table,))
    al_t_ids = cursor.fetchall()
    if (Id,) in al_s_ids :
        condition = 'stu'
    elif (Id,) in al_t_ids :
        condition = 'teach'
    elif (Id,) not in al_t_ids and (Id,) not in al_s_ids:
        condition = False
    return condition
def abs_prev_month(table):
    check_month = "show tables"
    cursor.execute(check_month)
    tables = cursor.fetchall()
    tab_name = ''
    if (table,) in tables:
        return 0
    elif (table,) not in tables:
        if table[8:11] == 'stu':
            tab_name = tables[-3][0]
        elif table[8:13] == 'teach':
            tab_name = tables[-2][0]
        check_column = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = Database() AND TABLE_NAME ='" + tab_name + "';"
        cursor.execute(check_column)
        columns = cursor.fetchall()
        cursor.execute("select id from %s where %s is null" % (tab_name, columns[-2][0]))
        a_ids = cursor.fetchall()
        for i in a_ids:
            ch_q = "update %s set %s = 'AA' where id = %s" % (tab_name, columns[-2][0], i[0])
            cursor.execute(ch_q)
            con.commit()
            ch_t_q = "update %s set %s = '-' where id = %s" % (tab_name, columns[-1][0], i[0])
            cursor.execute(ch_t_q)
            con.commit()

def month_add(table,person):
    check_month = "show tables"
    cursor.execute(check_month)
    tables = cursor.fetchall()
    if (table,) in tables:
        return 0
    elif (table,) not in tables:
        table_add_q = "create table %s (id int primary key )"%(table,)
        cursor.execute(table_add_q)
        cursor.execute("use school")
        cursor.execute("select id from "+person)
        ids = cursor.fetchall()
        cursor.execute("use att_man")
        id_lst = []
        for i in range(len(ids)):
            j = ids[i][0]
            id_lst.append(j)
        for all_id in id_lst:
            id_add_q = "insert into %s(id) values (%s)"%(table,all_id)
            cursor.execute(id_add_q)
            con.commit()

def abs_fail(table):
    check_column = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = Database() AND TABLE_NAME ='" + table + "';"
    cursor.execute(check_column)
    columns = cursor.fetchall()
    if len(columns) >= 3:
        if date == columns[-2][0]:
            return 0
        elif date != columns[-2][0]:
            cursor.execute("select id from %s where %s is null"%(table,columns[-2][0]))
            a_ids = cursor.fetchall()
            for i in a_ids :
                ch_q = "update %s set %s = 'AA' where id = %s"%(table,columns[-2][0],i[0])
                cursor.execute(ch_q)
                con.commit()
                ch_t_q = "update %s set %s = '-' where id = %s" % (table, columns[-1][0], i[0])
                cursor.execute(ch_t_q)
                con.commit()
def day_add(table,per):
    now = datetime.datetime.now()
    going_time = now.replace(hour=14, minute=40, second=0, microsecond=0)
    check_column = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = Database() AND TABLE_NAME ='" + table + "';"
    cursor.execute(check_column)
    columns = cursor.fetchall()
    if now < going_time:
        if (date,) not in columns:
            day_add_q = "alter table %s add %s varchar(30)"%(table,date)
            cursor.execute(day_add_q)
            day_tran_add_q = "alter table %s add %s varchar(15)" % (table, date_tran)
            cursor.execute(day_tran_add_q)
    elif (date,) in columns:
        cursor.execute("select id from %s"%(table,))
        al_ids = cursor.fetchall()
        cursor.execute('use school')
        cursor.execute("select id from %s"%(per,))
        al_ids_2 = cursor.fetchall()
        not_id = []
        cursor.execute('use att_man')
        for i in al_ids_2:
            not_id.append(i)
        if len(al_ids) < len(al_ids_2):
            for i in al_ids:
                not_id.remove(i)
            for idd in not_id:
                cursor.execute("insert into %s(id) values (%s)"%(table,idd[0]))
                con.commit()

def allabsent(table):
    now = datetime.datetime.now()
    going_time = now.replace(hour=14, minute=40, second=0, microsecond=0)
    if now < going_time:
        return 0
    check_column = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = Database() AND TABLE_NAME ='" + table + "';"
    cursor.execute(check_column)
    columns = cursor.fetchall()
    if now > going_time:
        if (date,) not in columns:
            return 0
        null_q = "select ID from %s where %s is null"%(table,date)
        cursor.execute(null_q)
        global data
        data = cursor.fetchall()
        if data != []:
            absent_query = f"update {table} set {date} = 'AA' where {date} is null"
            trans_query = f"update {table} set {date_tran} = '-' where {date_tran} is null"
            cursor.execute(absent_query)
            cursor.execute(trans_query)
            con.commit()


month_add(teach_table,teach)
month_add(stu_table,stu)
abs_fail(stu_table)
abs_fail(teach_table)
allabsent(teach_table)
allabsent(stu_table)

def main():
    scan_page = Tk()
    global leave_
    scan_page.title('Attendance')
    try:
        if leave_ == True:
            scan_page.title('Leaving Attendance ')
            pass
    except:
        leave_ = False
    scan_page.geometry("1366x720")
    scan_page.resizable(False,False)
    scan_im = PhotoImage(file='image/scanpage.png')
    scan_b_im = PhotoImage(file='image/scan_button.png')
    walk_b_im = PhotoImage(file='image/walk_button.png')
    bike_b_im = PhotoImage(file='image/bike_button.png')
    other_b_im = PhotoImage(file='image/others_button.png')
    cycle_b_im = PhotoImage(file='image/cycle_button.png')
    bus_b_im = PhotoImage(file='image/bustrain_button.png')
    tog_b_im = PhotoImage(file='image/toggle_button.png')
    tog_f_im = PhotoImage(file='image/toggle_frame.png')
    leav_b_im = PhotoImage(file='image/leave_b.png')
    det_b_im = PhotoImage(file='image/details_b.png')
    set_b_im = PhotoImage(file='image/settings_b.png')
    tog_back_b_im = PhotoImage(file='image/toggle_back_button.png')
    st_b_im = PhotoImage(file='image/stu_button.png')
    t_b_im = PhotoImage(file='image/teach_button.png')
    tog_go_back_im = PhotoImage(file='image/go_back_button.png')
    scan_lab = Label(image=scan_im)
    scan_lab.pack()
    help_b_im = PhotoImage(file='image/helpbutton.png')

    def help_func():
        now = datetime.datetime.now()
        checkin = now.replace(hour=14, minute=40, second=0, microsecond=0)
        if now < checkin:
            global help_win
            help_win = Toplevel()
            help_win.geometry("319x222")
            help_win.resizable(False, False)
            enter_im = PhotoImage(file="image/help_enter.png")
            help_image = PhotoImage(file="image/helpwin.png")
            help_im_lab = Label(help_win, image=help_image)
            Id_entry = StringVar()
            id_en = Entry(help_win, textvariable=Id_entry, bd=0, bg='#abc0ff', font=('Times New Roman', 17), width=7)
            id_en.place(relx=0.414, rely=0.222)
            go_b = Button(help_win, image=enter_im, bd=0, relief=FLAT, command=lambda: register(Id_entry.get()),bg='#ffffff')
            go_b.place(relx=0.342, rely=0.618)
            help_win.bind("<Return>", lambda event: register(Id_entry.get()))
            help_im_lab.pack()
            help_win.mainloop()
        elif now > checkin:
            messagebox.showerror('ERROR', 'Attendence registration time is over !!')
    help_b = Button(image=help_b_im, bd=0, relief=FLAT,command=help_func,bg='#ffffff')
    help_b.place(relx=0.428, rely=0.514)

    def tog_fr():
        tog_frame = Frame(scan_page,height=720,width=321,bg='#4823d3')
        tog_fr_lab = Label(tog_frame,image=tog_f_im)
        tog_fr_lab.pack()
        def leave():
            now = datetime.datetime.now()
            going_time = now.replace(hour=14, minute=40, second=0, microsecond=0)
            if now < going_time:
                tog_frame.destroy()
                scan_page.destroy()
                global leave_
                leave_ = True
                main()
            elif now > going_time:
                messagebox.showerror('ERROR', 'Attendence registration time is over !!')
        def details_show(sot,sot1):
            dat_ = cal.get_date()[:4] + '_' + cal.get_date()[5:7] + '_' + cal.get_date()[8:10]
            dat_t = dat_+'_transport'
            tab_name = cal.get_date()[:4] + '_' + cal.get_date()[5:7]+'_'+sot1+'_att'
            int_dat_ = int(cal.get_date()[:4] +cal.get_date()[5:7] +cal.get_date()[8:10])
            cursor.execute("select curdate()")
            dat1 = cursor.fetchall()
            dat1 = str(dat1[0][0])
            year1 = dat1[0:4]
            month1 = dat1[5:7]
            day1 = dat1[8:10]
            to_dat = int(year1+month1+day1)
            check_column = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = Database() AND TABLE_NAME = '%s';"%(tab_name,)
            cursor.execute(check_column)
            columns = cursor.fetchall()
            if sot1 == 'stu':
                cursor.execute('use school')
                cursor.execute( "select id from %s where class = '%s' and section = '%s'" % (sot, sel_clas.get(), sel_sec.get()))
                data1 = cursor.fetchall()
                if sel_clas.get() == '' or sel_sec.get() == '':
                    messagebox.showerror('ERROR','Select all options !!')
                    cursor.execute('use att_man_')
                    return 0
                elif sel_clas.get() not in clas or sel_sec.get() not in sec :
                    messagebox.showerror('ERROR','Invalid choice !!')
                    cursor.execute('use att_man_')
                    return 0
                elif data1 == []:
                    messagebox.showerror('ERROR', "No students are studying in this class !!")
                    cursor.execute('use att_man_')
                    return 0
            cursor.execute('use att_man_')
            if int_dat_ > to_dat:
                messagebox.showerror('ERROR',"You can't get details of upcoming days !! ")
                return 0
            elif (dat_,) not in columns:
                messagebox.showerror('ERROR','No Attendance details found on this day ... ')
                return 0
            elif int_dat_ == to_dat:
                now = datetime.datetime.now()
                going_time = now.replace(hour=14, minute=40, second=0, microsecond=0)
                if now < going_time:
                    messagebox.showwarning('ERROR',"Get the details of today's attendance after 14:40 PM !")
                    return 0
            cursor.execute('use school')
            def det_treeview(t1,t2):
                data_1 = []
                for i in range(len(t1)):
                    j = t1[i][0]
                    data_1.append(j)
                cursor.execute('use att_man_')
                id_det = tuple(data_1)
                if len(id_det) > 1:
                    id_det = str(id_det)
                elif len(id_det) == 1:
                    id_det = str(id_det)
                    new_id = ''
                    for i in id_det:
                        if i != ',':
                            new_id += i
                    id_det = new_id
                query = "select id, %s,%s from %s where id in %s " % (dat_, dat_t, tab_name, id_det)
                cursor.execute(query)
                data = cursor.fetchall()
                data_2 = []
                for i in data:
                    j = list(i)
                    data_2.append(j)
                for i in range(len(data)):
                    data_2[i].insert(1, t2[i][0])
                for i in range(len(data)):
                    j = data_2[i][2]
                    if len(j) > 3:
                        if j[2] == 'L':
                            k = j[3:11]
                            k1 = j[11:]
                            k2 = j[:2]
                            k3 = 'L'
                        elif j[2] != 'L':
                            k = j[2:10]
                            k1 = j[10:]
                            k2 = j[:2]
                            k3 = '-'
                    elif len(j) <= 3:
                        k2 = j
                        k = '-'
                        k1 = '-'
                        k3 = '-'
                    data_2[i].pop(2)
                    data_2[i].insert(2, k2)
                    data_2[i].insert(4, k)
                    data_2[i].insert(5, k1)
                    data_2[i].insert(6, k3)
                data = []
                for i in data_2:
                    j = tuple(i)
                    data.append(j)
                return data
            if sot1 == 'stu':
                cursor.execute("select id from %s where class = '%s' and section = '%s'"%(sot,sel_clas.get(),sel_sec.get()))
                data1 = cursor.fetchall()
                cursor.execute("select ucase(name) from %s where class = '%s' and section = '%s'" % (sot,sel_clas.get(),sel_sec.get()))
                data2 = cursor.fetchall()
                re_set = det_treeview(data1,data2)
            elif sot1 == 'teach':
                cursor.execute("select id from %s " % (sot,))
                data1 = cursor.fetchall()
                cursor.execute("select ucase(name) from %s" % (sot,))
                data2 = cursor.fetchall()
                re_set = det_treeview(data1,data2)
            det_fr = Frame(height=490,width=960,bg='#ffffff')
            det_fr.place(x=220,y=170)
            details = ttk.Treeview(det_fr, selectmode='browse',height=12)
            dat_lab = Label(det_fr,text=cal.get_date(),font=('Times New Roman',25),bg='#ffffff')
            def nxt_det():
                det_fr.destroy()
                if sot1 == 'stu':
                    sel_clas.set('')
                    sel_sec.set('')
            det_fr.bind('<Return>',lambda event:nxt_det())
            next_b = ttk.Button(det_fr, text='Next',command=nxt_det)
            if sot1 == 'stu':
                cl_lab = Label(det_fr,text=sel_clas.get()+' - '+sel_sec.get(),font=('Times New Roman',25),bg='#ffffff')
                cl_lab.place(x=434,y=80)
                details.place(x=40, y=156)
                dat_lab.place(x=392, y=10)
                next_b.place(x=438,y=450)
            elif sot1 == 'teach':
                details.place(x=40, y=135)
                dat_lab.place(x=392, y=30)
                next_b.place(x=435, y=440)
            details['columns'] = ("1", "2", "3", "4",'5','6','7')
            details["show"] = 'headings'
            details.column("1", width=100, anchor='c', stretch=NO)
            details.column("2", width=230, anchor='c', stretch=NO)
            details.column("3", width=110, anchor='c', stretch=NO)
            details.column("4", width=110, anchor='c', stretch=NO)
            details.column("5", width=110, anchor='c', stretch=NO)
            details.column("6", width=110, anchor='c', stretch=NO)
            details.column("7", width=90, anchor='c', stretch=NO)
            details.heading("1", text="Id")
            details.heading("2", text=sot+" name")
            details.heading("3", text="Status")
            details.heading("4", text="Transportation")
            details.heading("5", text="Arriving Time")
            details.heading("6", text="Leaving Time")
            details.heading("7", text="Late")
            for d in re_set:
                details.insert("", 'end', text=d[0], iid=d[0], values=(d[0], d[1], d[2], d[3], d[4], d[5], d[6]))

        def tog_go_back(wind):
            wind.destroy()
            cursor.execute('use att_man_')
            global leave_
            if leave_ == True:
                leave_ = False
            main()
        def tog_fr_back(wind):
            tog_frame1 = Frame(wind, height=720, width=321, bg='#4823d3')
            tog_frame1.place(x=0, y=0)
            tog_f1_im = PhotoImage(file='image/toggle_frame.png')
            tog_go_im = PhotoImage(file='image/go_back_button.png')
            tog_fr_lab = Label(tog_frame1, image=tog_f1_im)
            tog_fr_lab.pack()
            tog_back_det_im = PhotoImage(file='image/toggle_back_button.png')
            tog_back_b = Button(tog_frame1, image=tog_back_det_im, bg='#4823d3', bd=0, relief=FLAT, command= lambda:tog_back(tog_frame1))
            tog_back_b.place(x=8, y=8)
            go_b = Button(tog_frame1, image=tog_go_im, bd=0, relief=FLAT, bg='#4823d3', command=lambda:tog_go_back(wind))
            go_b.place(relx=0.0425, rely=0.42)
            tog_frame1.mainloop()
        def detail_stu():
            global det_win
            det_win = Tk()
            det_win.geometry('1366x720')
            det_win.title("Student's Attendance Details")
            det_win.resizable(False,False)
            det_w_im = PhotoImage(file='image/det_stu_page.png')
            en_im = PhotoImage(file='image/go.png')
            tog_bu_im = PhotoImage(file='image/toggle_button.png')
            det_w_lab = Label(image=det_w_im)
            det_w_lab.pack()
            sty = ttk.Style()
            sty.theme_use('clam')
            global cal
            cal = Calendar(det_win, date_pattern='yyyy/mm/dd', selectmode='day')
            cal.place(x=300, y=220)
            global clas
            global sec
            clas = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
            sec = ['A', 'B']
            global sel_clas
            sel_clas = StringVar()
            cl = ttk.Combobox(values=clas, textvariable=sel_clas, font=('Times New Roman', 16),width=9)
            cl.place(x=365, y=475)
            global sel_sec
            sel_sec = StringVar()
            sec_combo = ttk.Combobox(values=sec, textvariable=sel_sec, font=('Times New Roman', 16),width=9)
            sec_combo.place(x=365, y=590)
            ent_b = Button(image=en_im,bd=0, relief=FLAT,bg='#ffffff',command=lambda:details_show('Student','stu'))
            ent_b.place(x=570,y=610)
            tog_b = Button(det_win,image=tog_bu_im, bd=0, relief=FLAT,command=lambda:tog_fr_back(det_win))
            tog_b.place(relx=0.015, rely=0.045)
            det_win.bind('<Return>',lambda event:details_show('Student','stu'))
            det_win.mainloop()
        def detail_teach():
            global det_win_2
            det_win_2 = Tk()
            det_win_2.geometry('1366x720')
            det_win_2.title("Teacher's Attendance Details")
            det_win_2.resizable(False, False)
            det_t_im = PhotoImage(file='image/det_teach_page.png')
            en_t_im = PhotoImage(file='image/go.png')
            tog_bu1_im = PhotoImage(file='image/toggle_button.png')
            det_w_lab = Label(det_win_2,image=det_t_im)
            det_w_lab.pack()
            sty = ttk.Style()
            sty.theme_use('clam')
            global cal
            cal = Calendar(det_win_2,date_pattern='yyyy/mm/dd', selectmode='day')
            cal.place(x=315, y=250)
            ent_b = Button(det_win_2,image=en_t_im, bd=0, relief=FLAT, bg='#ffffff',command= lambda:details_show('Teacher','teach'))
            ent_b.place(x=400, y=485)
            tog_b = Button(det_win_2, image=tog_bu1_im, bd=0, relief=FLAT,command=lambda:tog_fr_back(det_win_2))
            tog_b.place(relx=0.015, rely=0.045)
            det_win_2.bind('<Return>', lambda event: details_show('Teacher', 'teach'))
            det_win_2.mainloop()
        def tog_log(arg):
            tog_frame.destroy()
            try:
                tog_fram.destroy()
            except:
                pass
            scan_page.destroy()
            log_win_2 = Tk()
            log_win_2.title('LOGIN')
            log_img = PhotoImage(file="image/login.png")
            log_b = PhotoImage(file="image/login3.png")
            log_win_2.geometry("1366x720")
            log_lab = Label(image=log_img)
            log_lab.pack()
            us_id_2 = StringVar()
            passwd_2 = StringVar()
            us_en = Entry(textvariable=us_id_2, bd=0, bg='#abc0ff', font=('Times New Roman', 15), width=18)
            us_en.place(relx=0.625, rely=0.437)
            us_pw = Entry(textvariable=passwd_2, bd=0, bg='#abc0ff', font=('Times New Roman', 13), width=18,show='●')
            us_pw.place(relx=0.625, rely=0.579)
            def log_tog_back():
                log_win_2.destroy()
                main()
            log_tog_b = ttk.Button(text='BACK',command=log_tog_back)
            log_tog_b.place(x=0,y=0)
            def login_tog():
                cursor.execute("select user_id from login")
                uid_lst = cursor.fetchall()
                cursor.execute("select password from login")
                pwd_lst = cursor.fetchall()
                if us_id_2.get() == '' and passwd_2.get() == '':
                    messagebox.showwarning('ERROR', 'Enter the user - id and password !!')
                elif us_id_2.get() == '' and passwd_2.get() != '':
                    messagebox.showwarning('ERROR', 'Enter the user - id  !!')
                elif us_id_2.get() != '' and passwd_2.get() == '':
                    messagebox.showwarning('ERROR', 'Enter the password !!')
                elif (us_id_2.get(),) in uid_lst and (passwd_2.get(),) in pwd_lst:
                    messagebox.showinfo('LOGGED IN', "Sucessfully loggin in ..")
                    log_win_2.destroy()
                    if arg == 'stu':
                        detail_stu()
                    elif arg == 'teach':
                        detail_teach()
                    elif arg == 'set':
                        pass
                elif (us_id_2.get(),) in uid_lst and (passwd_2.get(),) not in pwd_lst:
                    messagebox.showerror('ERROR', "Incorrect password !!")
                elif (us_id_2.get(),) not in uid_lst and (passwd_2.get(),) in pwd_lst:
                    messagebox.showerror('ERROR', "Incorrect user - id !!")
                elif (us_id_2.get(),) not in uid_lst and (passwd_2.get(),) not in pwd_lst:
                    messagebox.showerror('ERROR', "Incorrect user - id  and password !!")
            logb = Button(image=log_b, bd=0, relief=FLAT, command=login_tog, bg='#ffffff')
            logb.place(relx=0.629, rely=0.7)
            log_win_2.bind('<Return>', lambda event: login_tog())
            log_win_2.mainloop()

        def tog_back(frame):
            frame.destroy()
        def detail():
            tog_frame.destroy()
            global tog_fram
            tog_fram = Frame(scan_page, height=720, width=321, bg='#4823d3')
            tog_fr_lab = Label(tog_fram, image=tog_f_im)
            tog_fr_lab.pack()
            tog_fram.place(x=0,y=0)
            def tog_back_2():
                tog_fram.destroy()
            tog_back_b = Button(tog_fram, image=tog_back_b_im, bg='#4823d3', bd=0, relief=FLAT, command=tog_back_2)
            tog_back_b.place(x=8, y=8)
            stu_b = Button(tog_fram,image=st_b_im,bg='#4823d3', bd=0, relief=FLAT,command=lambda :tog_log('stu'))
            stu_b.place(relx=0.0425,rely=0.35)
            teach_b = Button(tog_fram, image=t_b_im, bg='#4823d3', bd=0, relief=FLAT,command=lambda :tog_log('teach'))
            teach_b.place(relx=0.0425, rely=0.48)
        if leave_ == False:
            leave_b = Button(tog_frame,image=leav_b_im,bd=0, relief=FLAT,bg='#4823d3',command=leave)
            leave_b.place(relx=0.0425,rely=0.32)
            det_b = Button(tog_frame, image=det_b_im, bd=0, relief=FLAT, bg='#4823d3',command=detail)
            det_b.place(relx=0.0425, rely=0.45)
            set_b = Button(tog_frame, image=set_b_im, bd=0, relief=FLAT, bg='#4823d3',command=lambda : tog_log('set'))
            set_b.place(relx=0.0425, rely=0.58)
        elif leave_ == True:
            go_back_b = Button(tog_frame, image=tog_go_back_im, bd=0, relief=FLAT, bg='#4823d3',command=lambda:tog_go_back(scan_page))
            go_back_b.place(relx=0.0425, rely=0.42)

        tog_back_b = Button(tog_frame,image=tog_back_b_im,bg='#4823d3',bd=0, relief=FLAT,command=lambda:tog_back(tog_frame))
        tog_back_b.place(x=8,y=8)
        tog_frame.place(x=0,y=0)

    tog_b = Button(image=tog_b_im,bd=0, relief=FLAT,command=tog_fr)
    tog_b.place(relx=0.015,rely=0.02)
    transport = StringVar()
    transport.set('bike')
    walk_b = Radiobutton(variable=transport,image=walk_b_im, bg='#ffffff',value='walk')
    walk_b.place(relx=0.4656, rely=0.7618)
    bike_b = Radiobutton(variable=transport,image=bike_b_im, bg='#ffffff',value='bike')
    bike_b.place(relx=0.4656, rely=0.66)
    bus_b = Radiobutton(variable=transport,image=bus_b_im, bg='#ffffff',value='bus')
    bus_b.place(relx=0.4656, rely=0.812)
    cyc_b = Radiobutton(variable=transport,image=cycle_b_im, bg='#ffffff',value='cycle')
    cyc_b.place(relx=0.4656, rely=0.71)
    other_b = Radiobutton(variable=transport,image=other_b_im, bg='#ffffff',value='others')
    other_b.place(relx=0.4656, rely=0.865)

    def register(ID):
        def leave_back():
            global leave_
            leave_ = False
            scan_page.destroy()
            main()
        if ID != '':
            if str(ID).isdigit():
                ID = int(ID)
                condition = id_validater(ID)
                if condition == False:
                    messagebox.showerror('ERROR', 'Incorrect id !!')
                    return 0
                try:
                    help_win.destroy()
                except:
                    pass
                now = datetime.datetime.now()
                checkin = now.replace(hour=8, minute=30, second=0)
                first_half = now.replace(hour=11, minute=30, second=0)
                btw_half = now.replace(hour=12, minute=0, second=0)
                second_half = now.replace(hour=14, minute=40, second=0)
                status = ''
                sh = str(second_half)
                sh1 = sh[11:19]
                cursor.execute('select curtime()')
                now_time = cursor.fetchall()
                now_time = str(now_time[0][0])
                if now == checkin or now < checkin:
                    status = "PP"+now_time+sh1
                elif now > checkin and now < first_half:
                    status = "PPL"+now_time+sh1
                elif now >= first_half and now < btw_half:
                    status = "AP"+now_time+sh1
                elif now >= btw_half and now < second_half:
                    status = "APL"+now_time+sh1
                elif now > second_half:
                    status = "AA"+now_time+sh1
                table = None
                if condition == 'stu':
                    table = stu_table
                elif condition == 'teach':
                    table = teach_table
                elif condition == False:
                    messagebox.showerror('ERROR', 'Incorrect id !!')
                    return 0
                cursor.execute("select %s from %s where id = %s" % (date, table, ID))
                re_check = cursor.fetchall()
                r_c1 = str(re_check[0][0])
                r_c = r_c1[:2]
                if re_check[0][0] == None:
                    att_reg_q = "update %s set %s  = '%s' where id = %s" % (table, date, status, ID)
                    cursor.execute(att_reg_q)
                    con.commit()
                    att_t_reg_q = "update %s set %s  = '%s' where id = %s" % (table, date_tran, transport.get(), ID)
                    cursor.execute(att_t_reg_q)
                    con.commit()
                    messagebox.showinfo('SUCCESS', 'Attendence has been registered ..')
                    return 0
                elif re_check[0][0] != None:
                    if r_c1[2] == 'L':
                        r_c = r_c1[:3]
                        r_c2 = r_c1[3:11]
                    if r_c1[2] != 'L':
                        r_c2 = r_c1[2:10]
                    sta = 'AA'+r_c2+now_time
                    if leave_ == True:
                        if r_c1[1] == 'A':
                            messagebox.showwarning('ERROR', 'Already your attendence has been registered !')
                            return 0
                        if r_c == 'PP':
                            if now >= first_half and now <= second_half:
                                sta = 'PA'+r_c2+now_time
                        elif r_c == 'PPL':
                            if now >= first_half and now <= second_half:
                                sta = 'PAL'+r_c2+now_time
                        confo = messagebox.askyesno('INFO', 'Are you sure to leave ??')
                        if confo == True:
                            att_reg_q = "update %s set %s  = '%s' where id = %s" % (table, date, sta, ID)
                            cursor.execute(att_reg_q)
                            con.commit()
                            messagebox.showinfo('SUCCESS', 'Attendence has been registered ..')
                            leave_back()
                    elif leave_ == False:
                        messagebox.showwarning('ERROR', 'Already your attendence has been registered ..')
                        return 0
            elif ID.isdigit() == False :
                messagebox.showerror('ERROR', 'Invalid characters')
        elif ID == '':
            messagebox.showerror('ERROR', 'Enter the id !!')

    def scan_QR():
        now = datetime.datetime.now()
        checkin = now.replace(hour=14, minute=40, second=0, microsecond=0)
        if now < checkin:
            try:
                cap = cv2.VideoCapture(0)
                detector = cv2.QRCodeDetector()
                while True:
                    _, img = cap.read()
                    data, one, _ = detector.detectAndDecode(img)
                    if data:
                        ID_number = int(data)
                        try:
                            cv2.destroyAllWindows()
                            register(ID_number)
                        except:
                            pass
                        break
                    cv2.imshow('QR Code Scanner ~~ Press "s" to stop', img)
                    if cv2.waitKey(1) == ord('s'):
                        break
            except:
                messagebox.showerror("ERROR", "Check if your camera is connected !")

        elif now > checkin:
            messagebox.showerror('ERROR', 'Attendence registration time is over !!')
    scan_b = Button(image=scan_b_im, bd=0, relief=FLAT, command=scan_QR,bg='#ffffff')
    scan_b.place(relx=0.285, rely=0.416)
    scan_page.bind("<Return>", lambda event:scan_QR())
    scan_page.mainloop()

def login():
    cursor.execute("select user_id from login")
    uid_lst = cursor.fetchall()
    cursor.execute("select password from login")
    pwd_lst = cursor.fetchall()
    cursor.execute("select * from login")
    uid_pwd_lst = cursor.fetchall()
    if us_id.get() == '' and passwd.get()== '':
        messagebox.showwarning('ERROR','Enter the user - id and password !!')
    elif us_id.get() == '' and passwd.get() != '':
        messagebox.showwarning('ERROR','Enter the user - id  !!')
    elif us_id.get() != '' and passwd.get() == '':
        messagebox.showwarning('ERROR','Enter the password !!')
    elif (us_id.get(),passwd.get()) in uid_pwd_lst:
        messagebox.showinfo('LOGGED IN',"Sucessfully loggin in ..")
        day_add(teach_table,'teacher')
        day_add(stu_table,'student')
        log_win.destroy()
        main()
    elif (us_id.get(), passwd.get()) not in uid_pwd_lst:
        messagebox.showerror('ERROR','Incorrect user-id or password !!')
    elif (us_id.get(),) in uid_lst and (passwd.get(),) not in pwd_lst:
        messagebox.showerror('ERROR', "Incorrect password !!")
    elif (us_id.get(),) not in uid_lst and (passwd.get(),) in pwd_lst:
        messagebox.showerror('ERROR', "Incorrect user - id !!")
    elif (us_id.get(),) not in uid_lst and (passwd.get(),)  not in pwd_lst:
        messagebox.showerror('ERROR', "Incorrect user - id  and password !!")
log_win = Tk()
log_win.title('LOGIN')
log_win.geometry("1366x720")
try:
    check = PhotoImage(file="image/login.png")
except:
    messagebox.showerror('ERROR', 'Images folder is not found !!!')
    exit()
log_img = PhotoImage(file="image/login.png")
log_b = PhotoImage(file="image/login3.png")
log_lab = Label(image=log_img)
log_lab.pack()
us_id = StringVar()
passwd = StringVar()
us_en = Entry(textvariable=us_id,bd=0,bg='#abc0ff',font=('Times New Roman',15),width=18)
us_en.place(relx=0.625,rely=0.437)
us_pw = Entry(textvariable=passwd,bd=0,bg='#abc0ff',font=('Times New Roman',13),width=18,show='●')
us_pw.place(relx=0.625,rely=0.579)
logb = Button(image=log_b,bd=0,relief=FLAT,command=login,bg='#ffffff')
logb.place(relx=0.629,rely=0.7)
log_win.bind('<Return>', lambda event:login())
log_win.mainloop()
