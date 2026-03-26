import tkinter as tk
from tkinter import ttk, messagebox

from data.db import initialize_database
from services.game_service import add_game, get_all_games


class CheckpointApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Checkpoint")
        self.geometry("900x600")
        self.minsize(800, 500)

        self.create_layout()
        self.refresh_game_list()

    def create_layout(self):
        # Header
        header = ttk.Label(self, text="Checkpoint", font=("Arial", 22, "bold"))
        header.pack(pady=10)

        # Main container
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Left side: Add Game form
        form_frame = ttk.LabelFrame(main_frame, text="Add Game", padding=15)
        form_frame.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(form_frame, text="Game Title *").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.title_entry = ttk.Entry(form_frame, width=30)
        self.title_entry.grid(row=1, column=0, pady=(0, 10))

        ttk.Label(form_frame, text="Platform").grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.platform_entry = ttk.Entry(form_frame, width=30)
        self.platform_entry.grid(row=3, column=0, pady=(0, 10))

        ttk.Label(form_frame, text="Genre / Mode").grid(row=4, column=0, sticky="w", pady=(0, 5))
        self.genre_entry = ttk.Entry(form_frame, width=30)
        self.genre_entry.grid(row=5, column=0, pady=(0, 10))

        ttk.Label(form_frame, text="Notes").grid(row=6, column=0, sticky="w", pady=(0, 5))
        self.notes_text = tk.Text(form_frame, width=30, height=6)
        self.notes_text.grid(row=7, column=0, pady=(0, 10))

        save_button = ttk.Button(form_frame, text="Save Game", command=self.save_game)
        save_button.grid(row=8, column=0, sticky="ew", pady=(5, 5))

        clear_button = ttk.Button(form_frame, text="Clear", command=self.clear_form)
        clear_button.grid(row=9, column=0, sticky="ew")

        # Right side: Tracked games list
        list_frame = ttk.LabelFrame(main_frame, text="Tracked Games", padding=15)
        list_frame.pack(side="left", fill="both", expand=True)

        self.games_listbox = tk.Listbox(list_frame, font=("Arial", 11))
        self.games_listbox.pack(fill="both", expand=True)

    def save_game(self):
        title = self.title_entry.get()
        platform = self.platform_entry.get()
        genre_mode = self.genre_entry.get()
        notes = self.notes_text.get("1.0", "end").strip()

        success, message = add_game(title, platform, genre_mode, notes)

        if success:
            messagebox.showinfo("Success", message)
            self.clear_form()
            self.refresh_game_list()
        else:
            messagebox.showerror("Error", message)

    def clear_form(self):
        self.title_entry.delete(0, tk.END)
        self.platform_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.notes_text.delete("1.0", tk.END)

    def refresh_game_list(self):
        self.games_listbox.delete(0, tk.END)

        games = get_all_games()

        if not games:
            self.games_listbox.insert(tk.END, "No games added yet.")
            return

        for game in games:
            game_id, title, platform, genre_mode, notes, created_at = game

            display_text = title
            if platform:
                display_text += f" | {platform}"
            if genre_mode:
                display_text += f" | {genre_mode}"

            self.games_listbox.insert(tk.END, display_text)


if __name__ == "__main__":
    initialize_database()
    app = CheckpointApp()
    app.mainloop()