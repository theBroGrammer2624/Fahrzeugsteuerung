from tkinter import *
fenster = Tk()
fenster.title("Abendprogramm")
fenster.geometry("1300x800")
running = True
x=0
def doing():
        global x
        x += 1
        Ausgabe.insert(END,x)
        if running:
                fenster.after(100, doing)
        else:
                Ausgabe.delete(1.0,END)
                x = 0
def stop():
        global running
        running = False
def starten():
        global running
        running = True
        doing()
Ausgabe = Text(fenster, height=3, width=25)
Ausgabe.place(x=0, y=200)
Ausgabe.config(font=("Arial",30))

start = Button(fenster, text="START",activebackground="green", command=starten)
start.place(x=0, y=100)
start.config(font=("Arial",30))

stop = Button(fenster, text="STOP",activebackground="green", command=stop)
stop.place(x=200, y=100)
stop.config(font=("Arial",30))

destr = Button(fenster, text="Programm schließen",activebackground="red", command=fenster.destroy)
destr.place(x=350, y=100)
destr.config(font=("Arial",30))

mainloop()


                


















