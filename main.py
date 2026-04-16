import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from data.db import initialize_database
from services.backup_service import export_backup, import_backup
from services.game_service import add_game, get_all_games, update_game, delete_game
from services.session_service import (
    create_session,
    get_all_sessions,
    get_sessions_by_game,
    update_session,
    delete_session
)
from services.analytics_service import (
    get_overall_stats,
    get_stats_for_game,
    get_playtime_by_game,
    get_goal_stats,
    get_goal_stats_for_game,
    get_active_goals_list
)


class CheckpointApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.selected_game_id = None
        self.game_map = {}

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
        self.style.configure("Section.TLabelframe.Label", font=("Segoe UI", 11, "bold"))
        self.style.configure("Sidebar.TButton", font=("Segoe UI", 10), padding=8)
        self.style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        self.style.configure("Danger.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        self.style.configure("Info.TLabel", font=("Segoe UI", 10))

        self.title("Checkpoint")
        self.configure(padx=10, pady=10)

        self.create_layout()
        self.refresh_game_list()

        self.update_idletasks()
        self.geometry("")
        self.minsize(self.winfo_width(), self.winfo_height())

    def create_layout(self):
        header = ttk.Label(self, text="Checkpoint", style="Title.TLabel")
        header.pack(anchor="w", pady=(0, 10))

        app_frame = ttk.Frame(self)
        app_frame.pack(fill="both", expand=True)

        sidebar = ttk.LabelFrame(app_frame, text="Navigation", padding=12, style="Section.TLabelframe")
        sidebar.pack(side="left", fill="y", padx=(0, 16), pady=(0, 10))

        ttk.Button(
            sidebar,
            text="Dashboard",
            style="Sidebar.TButton",
            command=self.open_dashboard_window
        ).pack(fill="x", pady=4)

        ttk.Button(
            sidebar,
            text="Session History",
            style="Sidebar.TButton",
            command=self.open_session_history_window
        ).pack(fill="x", pady=4)

        ttk.Button(
            sidebar,
            text="Backup / Restore",
            style="Sidebar.TButton",
            command=self.open_backup_window
        ).pack(fill="x", pady=4)

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", pady=10)

        ttk.Label(sidebar, text="Actions", style="Info.TLabel").pack(anchor="w", pady=(0, 6))

        ttk.Button(
            sidebar,
            text="Create Goal",
            style="Sidebar.TButton",
            command=self.open_goal_window
        ).pack(fill="x", pady=4)

        ttk.Button(
            sidebar,
            text="Log Session",
            style="Sidebar.TButton",
            command=self.open_session_window
        ).pack(fill="x", pady=4)

        content = ttk.Frame(app_frame, padding=5)
        content.pack(side="left", fill="both", expand=True)

        top_content = ttk.Frame(content)
        top_content.pack(fill="both", expand=True)

        form_frame = ttk.LabelFrame(top_content, text="Game Details", padding=16, style="Section.TLabelframe")
        form_frame.pack(side="left", fill="y", padx=(0, 12))
        form_frame.columnconfigure(0, weight=1)

        ttk.Label(form_frame, text="Game Title *").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.title_entry = ttk.Entry(form_frame, width=34)
        self.title_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(form_frame, text="Platform").grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.platform_entry = ttk.Entry(form_frame, width=34)
        self.platform_entry.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(form_frame, text="Genre / Mode").grid(row=4, column=0, sticky="w", pady=(0, 4))
        self.genre_entry = ttk.Entry(form_frame, width=34)
        self.genre_entry.grid(row=5, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(form_frame, text="Notes").grid(row=6, column=0, sticky="w", pady=(0, 4))
        self.notes_text = tk.Text(form_frame, width=34, height=8, wrap="word")
        self.notes_text.grid(row=7, column=0, sticky="ew", pady=(0, 12))

        action_row = ttk.Frame(form_frame)
        action_row.grid(row=8, column=0, sticky="ew")
        action_row.columnconfigure(0, weight=1)
        action_row.columnconfigure(1, weight=1)

        self.save_button = ttk.Button(
            action_row,
            text="Save Game",
            style="Primary.TButton",
            command=self.save_game
        )
        self.save_button.grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=4)

        self.update_button = ttk.Button(
            action_row,
            text="Update Game",
            style="Primary.TButton",
            command=self.update_selected_game
        )
        self.update_button.grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=4)

        self.delete_button = ttk.Button(
            action_row,
            text="Delete Game",
            style="Danger.TButton",
            command=self.delete_selected_game
        )
        self.delete_button.grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=4)

        self.clear_button = ttk.Button(
            action_row,
            text="Clear Selection",
            style="Sidebar.TButton",
            command=self.clear_form
        )
        self.clear_button.grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=4)

        list_frame = ttk.LabelFrame(top_content, text="Tracked Games", padding=16, style="Section.TLabelframe")
        list_frame.pack(side="left", fill="both", expand=True)

        ttk.Label(
            list_frame,
            text="Select a game to load it into the form.",
            style="Info.TLabel"
        ).pack(anchor="w", pady=(0, 8))

        list_container = ttk.Frame(list_frame)
        list_container.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.games_listbox = tk.Listbox(
            list_container,
            font=("Segoe UI", 11),
            activestyle="none",
            exportselection=False
        )
        self.games_listbox.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)
        self.games_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.games_listbox.yview)
        self.games_listbox.bind("<<ListboxSelect>>", self.on_game_select)

        footer = ttk.Label(
            content,
            text="Tip: Add a game, then use the sidebar to create goals, log sessions, and view analytics.",
            style="Info.TLabel"
        )
        footer.pack(anchor="w", pady=(10, 0))

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

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this game?")
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
        self.title_entry.focus()

    def refresh_game_list(self):
        self.games_listbox.delete(0, tk.END)
        self.game_map.clear()

        games = get_all_games()

        if not games:
            self.games_listbox.insert(tk.END, "No games added yet.")
            return

        for index, game in enumerate(games):
            game_id, title, platform, genre_mode, notes, created_at = game

            display_text = f"{title}"
            if platform:
                display_text += f"  •  {platform}"
            if genre_mode:
                display_text += f"  •  {genre_mode}"

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
        goal_window.transient(self)
        goal_window.grab_set()
        goal_window.resizable(False, False)

        ttk.Label(goal_window, text="Goal Name").pack(pady=5)
        name_entry = ttk.Entry(goal_window, width=30)
        name_entry.pack()

        ttk.Label(goal_window, text="Goal Type").pack(pady=5)
        type_var = tk.StringVar(value="Completion")
        ttk.Combobox(
            goal_window,
            textvariable=type_var,
            values=["Completion", "Performance", "Habit"],
            state="readonly"
        ).pack()

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
        session_window.transient(self)
        session_window.grab_set()
        session_window.resizable(False, False)

        ttk.Label(session_window, text="Duration (minutes)").pack(pady=5)
        duration_entry = ttk.Entry(session_window)
        duration_entry.pack()

        ttk.Label(session_window, text="Session Type").pack(pady=5)
        type_var = tk.StringVar(value="Casual")
        ttk.Combobox(
            session_window,
            textvariable=type_var,
            values=["Casual", "Ranked", "Practice", "Story"],
            state="readonly"
        ).pack()

        ttk.Label(session_window, text="Outcome (optional)").pack(pady=5)
        outcome_entry = ttk.Entry(session_window)
        outcome_entry.pack()

        ttk.Label(session_window, text="Notes").pack(pady=5)
        notes_text = tk.Text(session_window, height=5)
        notes_text.pack()

        def save_session():
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

    def open_backup_window(self):
        backup_window = tk.Toplevel(self)
        backup_window.title("Backup / Restore")
        backup_window.geometry("400x220")
        backup_window.transient(self)
        backup_window.grab_set()
        backup_window.resizable(False, False)

        ttk.Label(
            backup_window,
            text="Export your data to a backup file\nor import a previous backup.",
            font=("Arial", 11)
        ).pack(pady=20)

        def handle_export():
            filepath = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json")],
                title="Save Backup File"
            )

            if not filepath:
                return

            success, msg = export_backup(filepath)

            if success:
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Error", msg)

        def handle_import():
            filepath = filedialog.askopenfilename(
                filetypes=[("JSON Files", "*.json")],
                title="Open Backup File"
            )

            if not filepath:
                return

            confirm = messagebox.askyesno(
                "Confirm Import",
                "Importing a backup will replace current data. Continue?"
            )

            if not confirm:
                return

            success, msg = import_backup(filepath)

            if success:
                messagebox.showinfo("Success", msg)
                self.refresh_game_list()
            else:
                messagebox.showerror("Error", msg)

        ttk.Button(backup_window, text="Export Backup", command=handle_export).pack(pady=10)
        ttk.Button(backup_window, text="Import Backup", command=handle_import).pack(pady=10)

    def open_session_history_window(self):
        history_window = tk.Toplevel(self)
        history_window.title("Session History")
        history_window.geometry("1000x550")
        history_window.transient(self)
        history_window.grab_set()
        history_window.resizable(True, True)

        selected_session_id = {"value": None}

        top_frame = ttk.Frame(history_window, padding=10)
        top_frame.pack(fill="x")

        ttk.Label(top_frame, text="Filter by Game:").pack(side="left", padx=(0, 5))

        game_filter = tk.StringVar(value="All Games")
        game_dropdown = ttk.Combobox(top_frame, textvariable=game_filter, state="readonly")
        game_dropdown.pack(side="left", padx=(0, 10))

        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side="right")

        columns = ("Game", "Date/Time", "Duration", "Type", "Outcome", "Notes")
        tree = ttk.Treeview(history_window, columns=columns, show="headings")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130)

        tree.column("Notes", width=220)

        games = get_all_games()
        game_options = ["All Games"]
        game_lookup = {}

        for game in games:
            game_id, title, platform, genre_mode, notes, created_at = game
            game_options.append(title)
            game_lookup[title] = game_id

        game_dropdown["values"] = game_options
        game_dropdown.current(0)

        session_map = {}

        def load_sessions():
            for item in tree.get_children():
                tree.delete(item)

            session_map.clear()
            selected_session_id["value"] = None

            selected = game_filter.get()

            if selected == "All Games":
                sessions = get_all_sessions()
            else:
                game_id = game_lookup[selected]
                sessions = get_sessions_by_game(game_id)

            if not sessions:
                tree.insert("", "end", values=("No sessions found.", "", "", "", "", ""))
                return

            for i, session in enumerate(sessions):
                session_id, game_id, game_title, session_datetime, duration, session_type, outcome, notes = session

                tree.insert(
                    "",
                    "end",
                    iid=str(i),
                    values=(
                        game_title,
                        session_datetime,
                        duration,
                        session_type,
                        outcome if outcome else "",
                        notes if notes else ""
                    )
                )

                session_map[str(i)] = session

        def on_tree_select(event):
            selection = tree.selection()
            if not selection:
                selected_session_id["value"] = None
                return

            item_id = selection[0]
            if item_id in session_map:
                selected_session_id["value"] = session_map[item_id][0]

        def edit_selected_session():
            if selected_session_id["value"] is None:
                messagebox.showerror("Error", "Please select a session to edit.")
                return

            session = None
            for s in session_map.values():
                if s[0] == selected_session_id["value"]:
                    session = s
                    break

            if session is None:
                messagebox.showerror("Error", "Session not found.")
                return

            session_id, game_id, game_title, session_datetime, duration, session_type, outcome, notes = session

            edit_window = tk.Toplevel(history_window)
            edit_window.title("Edit Session")
            edit_window.geometry("400x350")
            edit_window.transient(history_window)
            edit_window.grab_set()
            edit_window.resizable(False, False)

            ttk.Label(edit_window, text=f"Game: {game_title}").pack(pady=5)

            ttk.Label(edit_window, text="Duration (minutes)").pack(pady=5)
            duration_entry = ttk.Entry(edit_window)
            duration_entry.pack()
            duration_entry.insert(0, str(duration))

            ttk.Label(edit_window, text="Session Type").pack(pady=5)
            type_var = tk.StringVar(value=session_type)
            ttk.Combobox(
                edit_window,
                textvariable=type_var,
                values=["Casual", "Ranked", "Practice", "Story"],
                state="readonly"
            ).pack()

            ttk.Label(edit_window, text="Outcome (optional)").pack(pady=5)
            outcome_entry = ttk.Entry(edit_window)
            outcome_entry.pack()
            outcome_entry.insert(0, outcome if outcome else "")

            ttk.Label(edit_window, text="Notes").pack(pady=5)
            notes_text = tk.Text(edit_window, height=5)
            notes_text.pack()
            notes_text.insert("1.0", notes if notes else "")

            def save_updated_session():
                success, msg = update_session(
                    session_id,
                    duration_entry.get(),
                    type_var.get(),
                    outcome_entry.get(),
                    notes_text.get("1.0", "end").strip()
                )

                if success:
                    messagebox.showinfo("Success", msg)
                    edit_window.destroy()
                    load_sessions()
                else:
                    messagebox.showerror("Error", msg)

            ttk.Button(edit_window, text="Update Session", command=save_updated_session).pack(pady=15)

        def delete_selected_session():
            if selected_session_id["value"] is None:
                messagebox.showerror("Error", "Please select a session to delete.")
                return

            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this session?")
            if not confirm:
                return

            success, msg = delete_session(selected_session_id["value"])

            if success:
                messagebox.showinfo("Success", msg)
                load_sessions()
            else:
                messagebox.showerror("Error", msg)

        ttk.Button(button_frame, text="Edit Session", command=edit_selected_session).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Session", command=delete_selected_session).pack(side="left", padx=5)

        game_dropdown.bind("<<ComboboxSelected>>", lambda event: load_sessions())
        tree.bind("<<TreeviewSelect>>", on_tree_select)

        load_sessions()

    def open_dashboard_window(self):
        dashboard_window = tk.Toplevel(self)
        dashboard_window.title("Dashboard")
        dashboard_window.geometry("1000x780")
        dashboard_window.transient(self)
        dashboard_window.grab_set()
        dashboard_window.resizable(True, True)

        top_frame = ttk.Frame(dashboard_window, padding=10)
        top_frame.pack(fill="x")

        ttk.Label(top_frame, text="View Stats For:").pack(side="left", padx=(0, 5))

        game_filter = tk.StringVar(value="All Games")
        game_dropdown = ttk.Combobox(top_frame, textvariable=game_filter, state="readonly")
        game_dropdown.pack(side="left", padx=(0, 10))

        stats_frame = ttk.LabelFrame(dashboard_window, text="Summary", padding=20)
        stats_frame.pack(fill="x", padx=15, pady=15)

        total_sessions_label = ttk.Label(stats_frame, text="Total Sessions: 0", font=("Arial", 14))
        total_sessions_label.pack(anchor="w", pady=5)

        total_minutes_label = ttk.Label(stats_frame, text="Total Playtime (minutes): 0", font=("Arial", 14))
        total_minutes_label.pack(anchor="w", pady=5)

        average_session_label = ttk.Label(stats_frame, text="Average Session Length: 0", font=("Arial", 14))
        average_session_label.pack(anchor="w", pady=5)

        active_goals_label = ttk.Label(stats_frame, text="Active Goals: 0", font=("Arial", 14))
        active_goals_label.pack(anchor="w", pady=5)

        completed_goals_label = ttk.Label(stats_frame, text="Completed Goals: 0", font=("Arial", 14))
        completed_goals_label.pack(anchor="w", pady=5)

        goals_frame = ttk.LabelFrame(dashboard_window, text="Current Active Goals", padding=10)
        goals_frame.pack(fill="x", padx=15, pady=10)

        goals_listbox = tk.Listbox(goals_frame, height=6, font=("Arial", 11))
        goals_listbox.pack(fill="both", expand=True)

        chart_frame = ttk.LabelFrame(dashboard_window, text="Playtime by Game", padding=10)
        chart_frame.pack(fill="both", expand=True, padx=15, pady=15)
        chart_frame.pack_propagate(False)

        games = get_all_games()
        game_options = ["All Games"]
        game_lookup = {}

        for game in games:
            game_id, title, platform, genre_mode, notes, created_at = game
            game_options.append(title)
            game_lookup[title] = game_id

        game_dropdown["values"] = game_options
        game_dropdown.current(0)

        figure = Figure(figsize=(6, 4), dpi=100)
        ax = figure.add_subplot(111)

        canvas = FigureCanvasTkAgg(figure, master=chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)

        def draw_chart():
            ax.clear()

            chart_data = get_playtime_by_game()
            titles = [row[0] for row in chart_data]
            minutes = [row[1] for row in chart_data]

            if not titles:
                ax.text(0.5, 0.5, "No session data available", ha="center", va="center")
            else:
                ax.bar(titles, minutes)
                ax.set_title("Playtime by Game")
                ax.set_xlabel("Game")
                ax.set_ylabel("Minutes Played")
                ax.tick_params(axis="x", rotation=30)

            figure.tight_layout()
            canvas.draw()

        def load_stats():
            selected = game_filter.get()
            goals_listbox.delete(0, tk.END)

            if selected == "All Games":
                stats = get_overall_stats()
                goal_stats = get_goal_stats()
                active_goals = get_active_goals_list()
            else:
                game_id = game_lookup[selected]
                stats = get_stats_for_game(game_id)
                goal_stats = get_goal_stats_for_game(game_id)
                active_goals = get_active_goals_list(game_id)

            total_sessions_label.config(text=f"Total Sessions: {stats['total_sessions']}")
            total_minutes_label.config(text=f"Total Playtime (minutes): {stats['total_minutes']}")
            average_session_label.config(text=f"Average Session Length: {stats['average_session']}")
            active_goals_label.config(text=f"Active Goals: {goal_stats['active_goals']}")
            completed_goals_label.config(text=f"Completed Goals: {goal_stats['completed_goals']}")

            if not active_goals:
                goals_listbox.insert(tk.END, "No active goals found.")
            else:
                for game_title, goal_name, target in active_goals:
                    goals_listbox.insert(tk.END, f"{game_title}: {goal_name} -> {target}")

            draw_chart()

        game_dropdown.bind("<<ComboboxSelected>>", lambda event: load_stats())
        load_stats()


if __name__ == "__main__":
    initialize_database()
    app = CheckpointApp()
    app.mainloop()