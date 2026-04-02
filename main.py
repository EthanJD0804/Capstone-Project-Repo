import tkinter as tk
from tkinter import ttk, messagebox

from data.db import initialize_database
from services.game_service import add_game, get_all_games, update_game, delete_game


class CheckpointApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Checkpoint")
        self.geometry("950x600")
        self.minsize(850, 550)

        self.selected_game_id = None
        self.game_map = {}

        self.create_layout()
        self.refresh_game_list()

    def create_layout(self):
        header = ttk.Label(self, text="Checkpoint", font=("Arial", 22, "bold"))
        header.pack(pady=10)

        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        form_frame = ttk.LabelFrame(main_frame, text="Game Form", padding=15)
        form_frame.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(form_frame, text="Game Title *").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.title_entry = ttk.Entry(form_frame, width=35)
        self.title_entry.grid(row=1, column=0, pady=(0, 10))

        ttk.Label(form_frame, text="Platform").grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.platform_entry = ttk.Entry(form_frame, width=35)
        self.platform_entry.grid(row=3, column=0, pady=(0, 10))

        ttk.Label(form_frame, text="Genre / Mode").grid(row=4, column=0, sticky="w", pady=(0, 5))
        self.genre_entry = ttk.Entry(form_frame, width=35)
        self.genre_entry.grid(row=5, column=0, pady=(0, 10))

        ttk.Label(form_frame, text="Notes").grid(row=6, column=0, sticky="w", pady=(0, 5))
        self.notes_text = tk.Text(form_frame, width=35, height=7)
        self.notes_text.grid(row=7, column=0, pady=(0, 10))

        self.save_button = ttk.Button(form_frame, text="Save Game", command=self.save_game)
        self.save_button.grid(row=8, column=0, sticky="ew", pady=(5, 5))

        self.update_button = ttk.Button(form_frame, text="Update Game", command=self.update_selected_game)
        self.update_button.grid(row=9, column=0, sticky="ew", pady=(0, 5))

        self.delete_button = ttk.Button(form_frame, text="Delete Game", command=self.delete_selected_game)
        self.delete_button.grid(row=10, column=0, sticky="ew", pady=(0, 5))

        self.clear_button = ttk.Button(form_frame, text="Clear Selection", command=self.clear_form)
        self.clear_button.grid(row=11, column=0, sticky="ew")

        self.create_goal_button = ttk.Button(form_frame,text="Create Goal",command=self.open_goal_window)
        self.create_goal_button.grid(row=12, column=0, sticky="ew", pady=(10, 0))

        self.log_session_button = ttk.Button(form_frame,text="Log Session",command=self.open_session_window)
        self.log_session_button.grid(row=13, column=0, sticky="ew", pady=(10, 0))

        list_frame = ttk.LabelFrame(main_frame, text="Tracked Games", padding=15)
        list_frame.pack(side="left", fill="both", expand=True)

        ttk.Label(list_frame, text="Click a game to load it into the form.").pack(anchor="w", pady=(0, 8))

        self.games_listbox = tk.Listbox(list_frame, font=("Arial", 11))
        self.games_listbox.pack(fill="both", expand=True)
        self.games_listbox.bind("<<ListboxSelect>>", self.on_game_select)

    def get_form_data(self):
        title = self.title_entry.get()
        platform = self.platform_entry.get()
        genre_mode = self.genre_entry.get()
        notes = self.notes_text.get("1.0", "end").strip()
        return title, platform, genre_mode, notes

    def save_game(self):
        title, platform, genre_mode, notes = self.get_form_data()
        success, message = add_game(title, platform, genre_mode, notes)

        if success:
            messagebox.showinfo("Success", message)
            self.clear_form()
            self.refresh_game_list()
        else:
            messagebox.showerror("Error", message)

    def update_selected_game(self):
        if self.selected_game_id is None:
            messagebox.showerror("Error", "Please select a game to update.")
            return

        title, platform, genre_mode, notes = self.get_form_data()
        success, message = update_game(self.selected_game_id, title, platform, genre_mode, notes)

        if success:
            messagebox.showinfo("Success", message)
            self.clear_form()
            self.refresh_game_list()
        else:
            messagebox.showerror("Error", message)

    def delete_selected_game(self):
        if self.selected_game_id is None:
            messagebox.showerror("Error", "Please select a game to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this game?"
        )

        if not confirm:
            return

        success, message = delete_game(self.selected_game_id)

        if success:
            messagebox.showinfo("Success", message)
            self.clear_form()
            self.refresh_game_list()
        else:
            messagebox.showerror("Error", message)

    def clear_form(self):
        self.selected_game_id = None
        self.title_entry.delete(0, tk.END)
        self.platform_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.notes_text.delete("1.0", tk.END)
        self.games_listbox.selection_clear(0, tk.END)

    def refresh_game_list(self):
        self.games_listbox.delete(0, tk.END)
        self.game_map.clear()

        games = get_all_games()

        if not games:
            self.games_listbox.insert(tk.END, "No games added yet.")
            return

        for index, game in enumerate(games):
            game_id, title, platform, genre_mode, notes, created_at = game

            display_text = title
            if platform:
                display_text += f" | {platform}"
            if genre_mode:
                display_text += f" | {genre_mode}"

            self.games_listbox.insert(tk.END, display_text)
            self.game_map[index] = game

    def on_game_select(self, event):
        selection = self.games_listbox.curselection()
        if not selection:
            return

        index = selection[0]

        if index not in self.game_map:
            return

        game = self.game_map[index]
        game_id, title, platform, genre_mode, notes, created_at = game

        self.selected_game_id = game_id

        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, title)

        self.platform_entry.delete(0, tk.END)
        self.platform_entry.insert(0, platform if platform else "")

        self.genre_entry.delete(0, tk.END)
        self.genre_entry.insert(0, genre_mode if genre_mode else "")

        self.notes_text.delete("1.0", tk.END)
        self.notes_text.insert("1.0", notes if notes else "")

    def open_goal_window(self):
        if self.selected_game_id is None:
            messagebox.showerror("Error", "Select a game first.")
            return

        goal_window = tk.Toplevel(self)
        goal_window.title("Create Goal")
        goal_window.geometry("400x350")

        ttk.Label(goal_window, text="Goal Name").pack(pady=5)
        name_entry = ttk.Entry(goal_window, width=30)
        name_entry.pack()

        ttk.Label(goal_window, text="Goal Type").pack(pady=5)
        type_var = tk.StringVar(value="Completion")
        ttk.Combobox(goal_window, textvariable=type_var,
                 values=["Completion", "Performance", "Habit"]).pack()

        ttk.Label(goal_window, text="Target").pack(pady=5)
        target_entry = ttk.Entry(goal_window, width=30)
        target_entry.pack()

        ttk.Label(goal_window, text="Start Date (YYYY-MM-DD)").pack(pady=5)
        start_entry = ttk.Entry(goal_window, width=30)
        start_entry.pack()

        ttk.Label(goal_window, text="End Date (optional)").pack(pady=5)
        end_entry = ttk.Entry(goal_window, width=30)
        end_entry.pack()

        def save_goal():
            from services.goal_service import create_goal

            try:
                success, msg = create_goal(
                    self.selected_game_id,
                    name_entry.get(),
                    type_var.get(),
                    target_entry.get(),
                    start_entry.get(),
                    end_entry.get()
                )

                if success:
                    messagebox.showinfo("Success", msg)
                    goal_window.destroy()
                else:
                    messagebox.showerror("Error", msg)

            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {e}")

        ttk.Button(goal_window, text="Save Goal", command=save_goal).pack(pady=15)

        
    def open_session_window(self):
            if self.selected_game_id is None:
                messagebox.showerror("Error", "Select a game first.")
                return

            session_window = tk.Toplevel(self)
            session_window.title("Log Session")
            session_window.geometry("400x350")

            ttk.Label(session_window, text="Duration (minutes)").pack(pady=5)
            duration_entry = ttk.Entry(session_window)
            duration_entry.pack()

            ttk.Label(session_window, text="Session Type").pack(pady=5)
            type_var = tk.StringVar(value="Casual")
            ttk.Combobox(session_window, textvariable=type_var,
                 values=["Casual", "Ranked", "Practice", "Story"]).pack()

            ttk.Label(session_window, text="Outcome (optional)").pack(pady=5)
            outcome_entry = ttk.Entry(session_window)
            outcome_entry.pack()

            ttk.Label(session_window, text="Notes").pack(pady=5)
            notes_text = tk.Text(session_window, height=5)
            notes_text.pack()

            def save_session():
                from services.session_service import create_session

                success, msg = create_session(
                    self.selected_game_id,
                    duration_entry.get(),
                    type_var.get(),
                    outcome_entry.get(),
                    notes_text.get("1.0", "end").strip()
                )

                if success:
                    messagebox.showinfo("Success", msg)
                    session_window.destroy()
                else:
                    messagebox.showerror("Error", msg)

            ttk.Button(session_window, text="Save Session", command=save_session).pack(pady=15)

        

if __name__ == "__main__":
    initialize_database()
    app = CheckpointApp()
    app.mainloop()