import customtkinter as ctk
import json
import random
import csv
from collections import defaultdict
from tkinter import filedialog

# Datenstruktur für Karteikarten
flashcards = []
progress_stats = {}  # Fortschrittsstatistik
current_card = None  # Aktuelle Karte global definieren

# Motivierende Sprüche
motivational_quotes = [
    "Weiter so, du machst das großartig!",
    "Erfolg ist die Summe kleiner Anstrengungen!",
    "Jede Antwort bringt dich näher zum Ziel!",
    "Du bist auf dem besten Weg, alles zu meistern!",
    "Bleib dran – du bist spitze!"
]

# Funktion: Karte erstellen
def create_card():
    front = entry_front.get()
    back = entry_back.get()
    category = entry_category.get()
    if front and back and category:
        card = {"front": front, "back": back, "category": category, "correct_count": 0, "total_shown": 0}
        flashcards.append(card)
        progress_stats[front] = {"category": category, "correct": 0, "incorrect": 0}  # Fortschritt initialisieren
        entry_front.delete(0, 'end')
        entry_back.delete(0, 'end')
        entry_category.delete(0, 'end')
        update_flashcard_list()
        update_progress()
    else:
        label_status.configure(text="Alle Felder ausfüllen!", text_color="red")

# Funktion: Liste aktualisieren
def update_flashcard_list():
    listbox_cards.delete("1.0", "end")  # Inhalt sicher leeren
    for card in flashcards:
        listbox_cards.insert("end", f"Frage: {card['front']} | Kategorie: {card['category']}\n")

# Funktion: Karten speichern
def save_cards():
    with open("flashcards.json", "w") as file:
        json.dump(flashcards, file)
    with open("progress_stats.json", "w") as file:
        json.dump(progress_stats, file)
    label_status.configure(text="Karten gespeichert!", text_color="green")

# Funktion: Karten laden
def load_cards():
    global flashcards, progress_stats
    try:
        with open("flashcards.json", "r") as file:
            flashcards = json.load(file)
        with open("progress_stats.json", "r") as file:
            progress_stats = json.load(file)
        update_flashcard_list()
        update_progress()
        label_status.configure(text="Karten geladen!", text_color="green")
    except FileNotFoundError:
        label_status.configure(text="Keine Datei gefunden!", text_color="red")

# Funktion: CSV importieren
def import_csv():
    global flashcards
    file_path = filedialog.askopenfilename(filetypes=[("CSV Dateien", "*.csv")])
    if file_path:
        try:
            with open(file_path, newline='', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if "Frage" in row and "Antwort" in row and "Kategorie" in row:
                        card = {"front": row["Frage"], "back": row["Antwort"], "category": row["Kategorie"], "correct_count": 0, "total_shown": 0}
                        flashcards.append(card)
                        progress_stats[row["Frage"]] = {"category": row["Kategorie"], "correct": 0, "incorrect": 0}
            update_flashcard_list()
            update_progress()
            label_status.configure(text="CSV erfolgreich importiert!", text_color="green")
        except Exception as e:
            label_status.configure(text=f"Fehler beim Importieren: {e}", text_color="red")

# Funktion: Lernmodus starten
def start_learning():
    global current_card
    if flashcards:
        select_next_card()
    else:
        label_status.configure(text="Keine Karten zum Lernen!", text_color="red")

# Funktion: Rückseite zeigen
def show_answer():
    global current_card
    if current_card is not None:
        label_answer.configure(text=current_card['back'])
    else:
        label_status.configure(text="Keine Karte zum Anzeigen ausgewählt!", text_color="red")

# Funktion: Bewertung der Antwort
def rate_answer(rating):
    global current_card
    if current_card:
        current_card['total_shown'] += 1
        question = current_card['front']
        if rating == "correct":
            current_card['correct_count'] += 1
            progress_stats[question]["correct"] += 1
        elif rating == "incorrect":
            current_card['correct_count'] = max(0, current_card['correct_count'] - 1)
            progress_stats[question]["incorrect"] += 1

        # Karte aus dem Topf entfernen, wenn korrekt und noch vorhanden
        if current_card in flashcards and current_card['correct_count'] >= 1:
            flashcards.remove(current_card)

        # Nächste Karte auswählen
        if flashcards:
            select_next_card()
        else:
            label_question.configure(text="Alle Karten gelernt!")
            label_answer.configure(text="")

        # Fortschritt aktualisieren
        update_progress()

# Funktion: Nächste Karte auswählen
def select_next_card():
    global current_card
    if not flashcards:
        label_status.configure(text="Keine Karten verfügbar!", text_color="red")
        return

    # Gewichtete Auswahl: Karten mit niedriger Korrektheit erscheinen häufiger
    weighted_cards = []
    for card in flashcards:
        weight = max(1, 5 - card['correct_count'])  # Karten mit weniger Korrektheit erscheinen öfter
        weighted_cards.extend([card] * weight)

    current_card = random.choice(weighted_cards)
    label_question.configure(text=current_card['front'])
    label_answer.configure(text="")

# Funktion: Fortschrittsanzeige aktualisieren
def update_category_statistics():
    # Statistiken nach Kategorie berechnen
    category_stats = defaultdict(lambda: {"answered": 0, "correct": 0, "incorrect": 0})
    for question, stats in progress_stats.items():
        category = stats["category"]
        category_stats[category]["answered"] += stats["correct"] + stats["incorrect"]
        category_stats[category]["correct"] += stats["correct"]
        category_stats[category]["incorrect"] += stats["incorrect"]

    # Anzeige aktualisieren
    stats_textbox.delete("1.0", "end")
    for category, stats in category_stats.items():
        stats_textbox.insert(
            "end",
            f"Kategorie: {category}\n"
            f"Beantwortet: {stats['answered']}\n"
            f"Richtig: {stats['correct']}\n"
            f"Falsch: {stats['incorrect']}\n\n"
        )

def update_progress():
    total_questions = len(progress_stats)
    total_correct = sum(stats["correct"] for stats in progress_stats.values())
    total_incorrect = sum(stats["incorrect"] for stats in progress_stats.values())
    total_answered = total_correct + total_incorrect

    if total_questions > 0:
        progress_percentage = (total_correct / total_questions) * 100
    else:
        progress_percentage = 0

    progress_label.configure(
        text=f"Fortschritt: {total_answered} beantwortet ({total_correct} richtig, {total_incorrect} falsch)"
    )
    progress_bar.set(progress_percentage / 100)

    # Kategorie-Statistiken aktualisieren
    update_category_statistics()

# Funktion: Motivierende Sprüche durchwechseln
def rotate_quotes():
    motivational_label.configure(text=random.choice(motivational_quotes))
    app.after(5000, rotate_quotes)  # Alle 5 Sekunden aktualisieren

# Hauptfenster erstellen
app = ctk.CTk()
app.geometry("800x600")
app.title("Karteikarten Generator")

# Tabs für verschiedene Funktionen
tabview = ctk.CTkTabview(app, width=700, height=500)
tabview.pack(pady=20)
tab_create = tabview.add("Erstellen")
tab_learn = tabview.add("Lernen")
tab_statistics = tabview.add("Erfolgsübersicht")

# --- Erstellen-Tab ---
frame_create = ctk.CTkFrame(tab_create, fg_color="#f5f5f5")
frame_create.pack(pady=10, padx=10, fill="both", expand=True)

frame_top = ctk.CTkFrame(frame_create)
frame_top.pack(pady=5)

label_front = ctk.CTkLabel(frame_top, text="Frage:", font=("Arial", 14))
label_front.grid(row=0, column=0, padx=5, pady=5)
entry_front = ctk.CTkEntry(frame_top, width=300)
entry_front.grid(row=0, column=1, padx=5, pady=5)

label_back = ctk.CTkLabel(frame_top, text="Antwort:", font=("Arial", 14))
label_back.grid(row=1, column=0, padx=5, pady=5)
entry_back = ctk.CTkEntry(frame_top, width=300)
entry_back.grid(row=1, column=1, padx=5, pady=5)

label_category = ctk.CTkLabel(frame_top, text="Kategorie:", font=("Arial", 14))
label_category.grid(row=2, column=0, padx=5, pady=5)
entry_category = ctk.CTkEntry(frame_top, width=300)
entry_category.grid(row=2, column=1, padx=5, pady=5)

button_create = ctk.CTkButton(frame_create, text="Karte erstellen", command=create_card)
button_create.pack(pady=10)

listbox_cards = ctk.CTkTextbox(frame_create, height=200, width=500)
listbox_cards.pack(pady=10, fill="both", expand=True)

button_save = ctk.CTkButton(frame_create, text="Speichern", command=save_cards)
button_save.pack(side="left", padx=5)

button_load = ctk.CTkButton(frame_create, text="Laden", command=load_cards)
button_load.pack(side="left", padx=5)

button_import = ctk.CTkButton(frame_create, text="CSV importieren", command=import_csv)
button_import.pack(side="left", padx=5)

label_status = ctk.CTkLabel(frame_create, text="", text_color="red")
label_status.pack(pady=10)

# --- Lernen-Tab ---
frame_learn = ctk.CTkFrame(tab_learn)
frame_learn.pack(pady=10, padx=10, fill="both", expand=True)

label_question = ctk.CTkLabel(frame_learn, text="Frage der Karte", font=("Arial", 16))
label_question.pack(pady=20)

label_answer = ctk.CTkLabel(frame_learn, text="", font=("Arial", 14), fg_color="lightgray", width=300)
label_answer.pack(pady=10)

button_start = ctk.CTkButton(frame_learn, text="Lernmodus starten", command=start_learning)
button_start.pack(pady=10)

button_show_answer = ctk.CTkButton(frame_learn, text="Antwort zeigen", command=show_answer)
button_show_answer.pack(pady=5)

frame_buttons = ctk.CTkFrame(frame_learn)
frame_buttons.pack(pady=10)

button_correct = ctk.CTkButton(frame_buttons, text="Korrekt", command=lambda: rate_answer("correct"))
button_correct.pack(side="left", padx=5)

button_incorrect = ctk.CTkButton(frame_buttons, text="Falsch", command=lambda: rate_answer("incorrect"))
button_incorrect.pack(side="left", padx=5)

# --- Erfolgsübersicht-Tab ---
frame_statistics = ctk.CTkFrame(tab_statistics)
frame_statistics.pack(pady=10, padx=10, fill="both", expand=True)

progress_label = ctk.CTkLabel(frame_statistics, text="Fortschritt: 0/0", font=("Arial", 14))
progress_label.pack(pady=5)

progress_bar = ctk.CTkProgressBar(frame_statistics, width=500)
progress_bar.pack(pady=5)
progress_bar.set(0)

stats_textbox = ctk.CTkTextbox(frame_statistics, height=200, width=500)
stats_textbox.pack(pady=10, fill="both", expand=True)

motivational_label = ctk.CTkLabel(frame_statistics, text="", font=("Arial", 14))
motivational_label.pack(pady=10)

# Motivierende Sprüche automatisch wechseln lassen
rotate_quotes()

# Anwendung starten
app.mainloop()