from tkinter import *
from tkinter import ttk
import tkinter as tk
from datetime import *
from tkcalendar import *
import sqlite3


class Expenses(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.conn = sqlite3.connect("wydatki.db")
        self.c = self.conn.cursor()

        self.create_table()

        self.notebook = ttk.Notebook()
        tab1 = Tab1(self.notebook)
        tab2 = Tab2(self.notebook)
        tab3 = Tab3(self.notebook, tab1=self)

        self.notebook.add(tab1, text=" Strona Główna ")
        self.notebook.add(tab2, text=" Wydatki ")
        self.notebook.add(tab3, text=" Swinka ")

        self.cal = tk.Button(self, text=f"{date.today():%a, %d %b %Y}", fg="white", bg="pink",
                             activebackground="pink", font=("fixedsys", 15), command=HistoryView)
        self.cal.pack()
        self.cal.place(x=345, y=33, relwidth=0.3, relheight=0.06)
        self.notebook.pack(expand=True, fill="both")
        self.notebook.place(x=0, y=0, relwidth=0.997, relheight=1)

    def create_table(self):
        self.c.execute(""" CREATE TABLE IF NOT EXISTS cel (
                    'datestamp' DATE, 
                    'total' REAL)""")

        self.c.execute(""" CREATE TABLE IF NOT EXISTS swinka (
                    'datestamp' DATE,
                    'total' REAL    
                )""")

        self.c.execute(""" CREATE TABLE IF NOT EXISTS zakupy (
                    'datestamp' DATE,
                    'total' REAL,
                    'category' TEXT    
                )""")
        self.conn.commit()


class HistoryView(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        style = ttk.Style()
        style.configure("Tree",
                        background="pink",
                        foreground="pink",
                        rowheight=20,
                        fieldbackground="hot pink")

        self.conn = sqlite3.connect("wydatki.db")
        self.c = self.conn.cursor()

        cal = DateEntry(self, width=20, background="hot pink")
        cal.pack()

        self.treetime = ttk.Treeview(self)
        # self.treetime.configure(style="Tree")
        self.treetime.pack()
        self.treetime["columns"] = ("Data", "Kategoria", "Kwota")

        self.treetime.column("#0", width=30, minwidth=30)
        self.treetime.column("Data", anchor=CENTER, width=160, minwidth=30)
        self.treetime.column("Kategoria", anchor=CENTER, width=120, minwidth=30)
        self.treetime.column("Kwota", anchor=CENTER, width=120, minwidth=30)

        self.treetime.heading("#0", tex="ID", anchor=CENTER)
        self.treetime.heading("Data", tex="Data", anchor=CENTER)
        self.treetime.heading("Kategoria", tex="Kategoria", anchor=CENTER)
        self.treetime.heading("Kwota", tex="Kwota", anchor=CENTER)

        self.c.execute("SELECT * FROM zakupy")
        rows = self.c.fetchall()
        self.update_data(rows)

    def update_data(self, rows):
        number = 1
        for row in rows:
            self.treetime.insert("", index='end', text=number, values=row)
            number += 1


class Tab1(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.conn = sqlite3.connect("wydatki.db")
        self.c = self.conn.cursor()
        self.now = datetime.now()

        self.frame1 = tk.LabelFrame(self, text=" Halko Adka ", bg="pink", fg="white", font=("fixedsys", 15))
        self.frame1.pack(expand=True, fill="both")

        self.goal_title = tk.Label(self.frame1, text=" Wprowadź kwotę ", bg="pink", font=("fixedsys", 10))
        self.goal_title.place(x=10, y=110)

        self.goal_amount = DoubleVar()
        self.goal_ent = tk.Entry(self.frame1, textvariable=self.goal_amount)
        self.goal_ent.place(x=310, y=110)

        self.pln1 = tk.Label(self.frame1, text=" zł ", bg="pink")
        self.pln1.place(x=440, y=110)

        self.send_bttn1 = tk.Button(self.frame1, text=" Ustaw ", bg="pink", activebackground="pink",
                                    command=self.dodaj_do_celu, font=("fixedsys", 10))
        self.send_bttn1.place(x=310, y=150)

        self.target_show = tk.Label(self.frame1, text=" Twój cel to: ", bg="pink", font=("fixedsys", 10))
        self.target_show.place(x=10, y=200)

        self.target_prnt = tk.Label(self.frame1, text=self.do_celu, bg="pink", font=("fixedsys", 10))
        self.target_prnt.place(x=310, y=200)

        self.change_bttn = tk.Button(self.frame1, text=" Zmień ", bg="pink", activebackground="pink",
                                     command=self.button_active, font=("fixedsys", 10))
        self.change_bttn.place(x=310, y=240)

        self.target_lbl = tk.Label(self.frame1, text=" Do celu brakuje już tylko: ", bg="pink", font=("fixedsys", 10))
        self.target_lbl.place(x=10, y=310)

        self.target_show = tk.Label(self.frame1, text=self.sum_of_two, bg="pink", font=("fixedsys", 10))
        self.target_show.place(x=310, y=310)

        self.sum_of_two()

    def dodaj_do_celu(self):
        self.c.execute("DELETE FROM cel")
        today = self.now.date()
        new_goal = self.goal_ent.get()
        self.c.execute("INSERT INTO cel VALUES(?, ?)", (today, new_goal))
        self.conn.commit()
        self.target_prnt.config(text=new_goal)

        self.sum_of_two()

    def do_celu(self):
        query = "SELECT total FROM cel"
        self.c.execute(query)
        goal = self.c.fetchall()
        self.target_prnt.config(text=goal)

    def sum_of_two(self):
        check = "SELECT total FROM swinka"
        self.c.execute(check)
        skarb = self.c.fetchall()

        query_a = "SELECT total FROM cel"
        self.c.execute(query_a)
        total_a = self.c.fetchall()

        query = "SELECT SUM(total) FROM swinka"
        self.c.execute(query)
        total_s = self.c.fetchall()
        if not skarb and not total_a:
            self.target_prnt.config(text="Nie masz jeszcze celu")
            self.target_show.config(text="Nie masz jeszcze celu")
        elif not skarb and total_a:
            self.target_prnt.config(text=total_a)
            self.target_show.config(text=total_a)
        elif skarb and not total_a:
            self.target_prnt.config(text="Nie masz jeszcze celu")
            self.target_show.config(text="Nie masz jeszcze celu")
        else:
            ta1 = float(''.join(map(str, total_a[0])))
            ts1 = float(''.join(map(str, total_s[0])))
            total_total = ta1 - ts1
            self.target_show.config(text=total_total)

        self.send_bttn1.config(state=DISABLED)
        self.goal_ent.config(state=DISABLED)

    def button_active(self):
        self.send_bttn1.config(state=ACTIVE)
        self.goal_ent.config(state=NORMAL)


class Tab2(tk.Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        self.conn = sqlite3.connect("wydatki.db")
        self.c = self.conn.cursor()
        self.now = datetime.now()

        self.frame1 = tk.LabelFrame(self, text="Tutaj wprowadź swoje wydatki",
                                    bg="pink", fg="white", font=("fixedsys", 11))
        self.frame1.pack(expand=True, fill="both")

        # Dodaj wydaki i miejsce
        self.expenses_lbl = tk.Label(self.frame1, text=" Kwota", activebackground="#e75480",
                                     bg="pink", font=("fixedsys", 10))
        self.expenses_lbl.place(x=10, y=110)

        self.expenses = DoubleVar()
        self.expenses_ent = tk.Entry(self.frame1, width=8, textvariable=self.expenses)
        self.expenses_ent.place(x=310, y=110)

        self.pln2 = tk.Label(self.frame1, text=" zł ", bg="pink")
        self.pln2.place(x=370, y=110)

        self.options = [
            " ",
            "Fordek",
            "Ciuchy",
            "Paliwko",
            "Paznokcie",
            "Rysiek",
            "Spożywcze",
            "Szkoła",
            "Włosy",
            "Wyjścia",
        ]

        self.myCombo = ttk.Combobox(self.frame1, value=self.options)
        self.myCombo.current(0)
        self.myCombo.bind("<<ComboSelected>>", self.dynamic_data)
        self.myCombo.place(x=310, y=190)

        self.category_lbl = tk.Label(self.frame1, text=" Kategoria", bg="pink",
                                     activebackground="#e75480", font=("fixedsys", 10))
        self.category_lbl.place(x=10, y=190)

        self.send_bttn3 = tk.Button(self.frame1, text=" Dodaj", command=self.dynamic_data,
                                    bg="pink", activebackground="pink")
        self.send_bttn3.place(x=310, y=240)

        self.outgoing_lbl = tk.Label(self.frame1, text=" Suma wydatków z ostatnich 30-stu dni ",
                                     bg="pink", font=("fixedsys", 10))
        self.outgoing_lbl.place(x=10, y=310)

        self.outgoing_show = tk.Label(self.frame1, text=self.show_outgoing, bg="pink",
                                      activebackground="pink", font=("fixedsys", 10))
        self.outgoing_show.place(x=350, y=310)

        self.show_outgoing()

    def dynamic_data(self):
        today = self.now.date()
        amount = self.expenses_ent.get()
        category = self.myCombo.get()
        self.c.execute("INSERT INTO zakupy VALUES(?, ?, ?)", (today, amount, category))
        self.conn.commit()
        self.show_outgoing()
        self.myCombo.current(0)
        self.expenses.set(0.0)

    def show_outgoing(self):
        query = "SELECT SUM(total) FROM zakupy WHERE datestamp >= date('now', '-30 day')"
        self.c.execute(query)
        outgoing = self.c.fetchall()
        self.outgoing_show.config(text=outgoing)


class Tab3(tk.Frame):
    def __init__(self, master, tab1):
        Frame.__init__(self, master)
        self.tab1 = Tab1(master)

        self.conn = sqlite3.connect("wydatki.db")
        self.c = self.conn.cursor()
        self.now = datetime.now()

        self.frame1 = tk.LabelFrame(self, text=" Wrzuć hajs do świnki ",
                                    bg="pink", fg="white", font=("fixedsys", 11))
        self.frame1.pack(expand=True, fill="both")

        self.piggy_title = tk.Label(self.frame1, text=" Wprowadź oszczędności ", bg="pink", font=("fixedsys", 11))
        self.piggy_title.place(x=10, y=50)

        self.piggy_lbl = tk.Label(self.frame1, text=" Nakarm świnkę  ", bg="pink", font=("fixedsys", 10))
        self.piggy_lbl.place(x=10, y=110)

        self.piggy_ent = DoubleVar()
        self.piggy_ent1 = tk.Entry(self.frame1, width=8, textvariable=self.piggy_ent)
        self.piggy_ent1.place(x=310, y=110)

        self.pln2 = tk.Label(self.frame1, text=" zł ", bg="pink")
        self.pln2.place(x=370, y=110)

        self.send_bttn3 = tk.Button(self.frame1, text=" Nakarm ", bg="pink",
                                    activebackground="pink", command=self.piggy_sum)
        self.send_bttn3.place(x=310, y=150)

        self.piggy_take_lbl = tk.Label(self.frame1, text=" Zabierz śwince ", bg="pink", font=("fixedsys", 10))
        self.piggy_take_lbl.place(x=10, y=190)

        self.piggy_take = DoubleVar()
        self.piggy_take_ent = tk.Entry(self.frame1, width=8, textvariable=self.piggy_take)
        self.piggy_take_ent.place(x=310, y=190)

        self.pln2 = tk.Label(self.frame1, text=" zł", bg="pink")
        self.pln2.place(x=370, y=150)

        self.send_bttn3 = tk.Button(self.frame1, text=" Zabierz", bg="pink",
                                    activebackground="pink", command=self.piggy_subtract)
        self.send_bttn3.place(x=310, y=230)

        self.piggy_amount = tk.Label(self.frame1, text=" W skarbonce masz juź: ", bg="pink", font=("fixedsys", 10))
        self.piggy_amount.place(x=10, y=310)

        self.piggy_bank = tk.Label(self.frame1, text=self.skarbonka_stan, bg="pink", font=("fixedsys", 10))
        self.piggy_bank.place(x=310, y=310)

        self.skarbonka_stan()

    def piggy_sum(self):
        today = self.now.date()
        saved = self.piggy_ent.get()
        self.c.execute("INSERT INTO swinka VALUES(?, ?)", (today, saved))
        self.conn.commit()
        self.skarbonka_stan()
        self.tab1.sum_of_two()
        self.piggy_ent.set(0.0)

    # Odejmowanie wartosci ze swinki
    def piggy_subtract(self):
        today = self.now.date()
        saved = -(self.piggy_take.get())
        self.c.execute("INSERT INTO swinka VALUES(?, ?)", (today, saved))
        self.conn.commit()
        self.skarbonka_stan()
        self.tab1.sum_of_two()
        self.piggy_take.set(0.0)

    # stan swinki skarbonki
    def skarbonka_stan(self):
        check = "SELECT total FROM swinka"
        self.c.execute(check)
        skarbonka = self.c.fetchall()
        self.tab1.sum_of_two()
        if not skarbonka:
            self.piggy_bank.config(text=" Skarbonka jest pusta ")
        else:
            query = "SELECT SUM(total) FROM swinka"
            self.c.execute(query)
            piggy = self.c.fetchall()
            self.piggy_bank.config(text=piggy)


if __name__ == "__main__":
    root = Expenses()
    root.geometry("500x500")
    root.title("Wydatki App")
    root.resizable(False, False)
    root.mainloop()
