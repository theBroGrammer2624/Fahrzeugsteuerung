import tkinter as tk  # Importiert Tkinter für die GUI-Erstellung
from tkinter import messagebox  # Importiert messagebox für Popup-Nachrichten
import sqlite3  # Importiert sqlite3 für Datenbankoperationen
from datetime import datetime  # Importiert datetime, um das aktuelle Datum und die Uhrzeit zu erhalten
import os  # Importiert das os-Modul, um Dateioperationen (wie das Löschen der Datenbank) durchzuführen

db_name = 'zeitstempel.db'

# Datenbank und Tabelle erstellen bzw. aktualisieren
def init_db():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS zeitstempel (
                        id INTEGER PRIMARY KEY,
                        datum TEXT,
                        sensor1 REAL DEFAULT NULL,
                        sensor2 REAL DEFAULT NULL,
                        sensor3 REAL DEFAULT NULL)''')
    conn.commit()
    conn.close()

# Datum und Uhrzeit in die Datenbank einfügen
def speichern(distanz):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    jetzt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    s1 = distanz
    s2 = "---"
    # Hier fügen wir Nullwerte für die Sensordaten ein, da diese noch nicht verfügbar sind
    cursor.execute("INSERT INTO zeitstempel (datum, sensor1, sensor2, sensor3) VALUES (?, ?, ?, NULL)", (jetzt,s1,s2,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Gespeichert", f"Zeitstempel {jetzt} gespeichert.")

# Daten auslesen und anzeigen
def auslesen():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT id, datum, sensor1, sensor2, sensor3 FROM zeitstempel")
    daten = cursor.fetchall()
    conn.close()
    anzeige = "\n\n".join(f"{id}: {datum}, Distanz: {s1}" 
                        for id, datum, s1, s2, s3 in daten)
    messagebox.showinfo("Daten", anzeige)

# Alle Daten löschen
def loeschen():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM zeitstempel")
    conn.commit()
    conn.close()
    messagebox.showinfo("Gelöscht", "Alle Daten wurden gelöscht.")

# Gesamte Datenbank löschen
def datenbank_loeschen():
    if os.path.exists(db_name):
        os.remove(db_name)
        messagebox.showinfo("Datenbank Gelöscht", "Die gesamte Datenbank wurde gelöscht.")
    else:
        messagebox.showinfo("Fehler", "Datenbank nicht gefunden.")

"""
# GUI erstellen
app = tk.Tk()
app.title("Zeitstempel Speichern, Auslesen, Löschen und Datenbank Löschen")

init_db_button = tk.Button(app, text="Datenbank Initialisieren", command=init_db)
init_db_button.pack()

speichern_button = tk.Button(app, text="Zeitstempel Speichern", command=speichern)
speichern_button.pack()

auslesen_button = tk.Button(app, text="Daten Auslesen", command=auslesen)
auslesen_button.pack()

loeschen_button = tk.Button(app, text="Daten Löschen", command=loeschen)
loeschen_button.pack()

datenbank_loeschen_button = tk.Button(app, text="Datenbank Löschen", command=datenbank_loeschen)
datenbank_loeschen_button.pack()

app.mainloop()
"""