import sys
import os
import customtkinter as ctk
import threading
import time
import random

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.online_coordinator import OnlineCoordinator
from processor.research_engine import ResearchEngine
from simulated_testing.user_manager import UserManager
from simulated_testing.run_simulation import run_simulation

# Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # System Setup
        self.engine = ResearchEngine()
        self.coordinator = OnlineCoordinator()
        self.user_manager = UserManager()
        self.all_strategies = self.engine.strategies
        
        # Window Setup
        self.title("Curiosity Co-Pilot (Dashboard)")
        self.geometry("900x700")
        self.resizable(True, True)

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- TAB VIEW ---
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.tab_pilot = self.tabview.add("Live Pilot")
        self.tab_users = self.tabview.add("User Manager")
        self.tab_sim = self.tabview.add("Simulation Lab")
        
        # Initialize Tabs
        self.setup_pilot_tab()
        self.setup_users_tab()
        self.setup_sim_tab()

    # ==========================================================================
    # TAB 1: LIVE PILOT (Original Demo)
    # ==========================================================================
    def setup_pilot_tab(self):
        self.tab_pilot.grid_columnconfigure(0, weight=1)
        
        # Header
        ctk.CTkLabel(self.tab_pilot, text="Live Intervention Pilot", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        # Context
        self.pilot_context_label = ctk.CTkLabel(self.tab_pilot, text="Current State: Waiting...", font=ctk.CTkFont(size=14))
        self.pilot_context_label.pack(pady=10)
        
        # Card
        self.pilot_card = ctk.CTkFrame(self.tab_pilot, fg_color="#2B2B2B", corner_radius=10)
        self.pilot_card.pack(fill="x", padx=50, pady=20)
        
        self.pilot_strat_title = ctk.CTkLabel(self.pilot_card, text="Strategy", font=ctk.CTkFont(size=18, weight="bold"))
        self.pilot_strat_title.pack(pady=(20, 5))
        
        self.pilot_strat_desc = ctk.CTkLabel(self.pilot_card, text="...", wraplength=400)
        self.pilot_strat_desc.pack(pady=(0, 20))
        
        # Controls
        self.pilot_sim_btn = ctk.CTkButton(self.tab_pilot, text="Simulate Drift Event", command=self.run_pilot_sim, height=40)
        self.pilot_sim_btn.pack(pady=10)
        
        self.pilot_feedback_frame = ctk.CTkFrame(self.tab_pilot, fg_color="transparent")
        ctk.CTkButton(self.pilot_feedback_frame, text="✓ Success", fg_color="green", command=lambda: self.pilot_feedback(True)).pack(side="left", padx=10)
        ctk.CTkButton(self.pilot_feedback_frame, text="✕ Failed", fg_color="red", command=lambda: self.pilot_feedback(False)).pack(side="right", padx=10)

    def run_pilot_sim(self):
        self.pilot_sim_btn.pack_forget()
        energy = random.choice(["low", "medium", "high"])
        stress = random.choice(["low", "medium", "high"])
        self.current_pilot_context = {"energy": energy, "stress": stress}
        self.pilot_context_label.configure(text=f"State: Energy={energy.upper()}, Stress={stress.upper()}")
        
        # Get Strategy
        strat = self.coordinator.select_strategy(self.current_pilot_context, self.all_strategies)
        self.current_pilot_strat = strat
        
        self.pilot_strat_title.configure(text=strat["name"])
        self.pilot_strat_desc.configure(text=strat["logic"])
        self.pilot_feedback_frame.pack(pady=10)

    def pilot_feedback(self, success):
        self.coordinator.log_outcome(self.current_pilot_strat["name"], success)
        self.pilot_feedback_frame.pack_forget()
        self.pilot_sim_btn.pack(pady=10)
        self.pilot_strat_title.configure(text="Feedback Recorded")

    # ==========================================================================
    # TAB 2: USER MANAGER
    # ==========================================================================
    def setup_users_tab(self):
        self.tab_users.grid_columnconfigure(0, weight=1)
        self.tab_users.grid_columnconfigure(1, weight=1)
        
        # Left Col: Create User
        left_frame = ctk.CTkFrame(self.tab_users)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(left_frame, text="Create New Persona", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.entry_name = ctk.CTkEntry(left_frame, placeholder_text="Name (e.g. Stressed Student)")
        self.entry_name.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(left_frame, text="Base Stress (0.0 - 1.0)").pack(pady=(10,0))
        self.slider_stress = ctk.CTkSlider(left_frame, from_=0, to=1)
        self.slider_stress.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(left_frame, text="Base Energy (0.0 - 1.0)").pack(pady=(10,0))
        self.slider_energy = ctk.CTkSlider(left_frame, from_=0, to=1)
        self.slider_energy.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkButton(left_frame, text="Create User", command=self.create_user).pack(pady=20)
        
        # Right Col: User List
        right_frame = ctk.CTkFrame(self.tab_users)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(right_frame, text="Existing Users", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.user_list_box = ctk.CTkTextbox(right_frame)
        self.user_list_box.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_user_list()

    def create_user(self):
        name = self.entry_name.get()
        if not name: return
        stress = self.slider_stress.get()
        energy = self.slider_energy.get()
        
        self.user_manager.create_user(name, stress, energy)
        self.refresh_user_list()
        self.refresh_sim_dropdown() # Update sim tab too

    def refresh_user_list(self):
        self.user_list_box.configure(state="normal")
        self.user_list_box.delete("0.0", "end")
        users = self.user_manager.get_all_users()
        for u in users:
            self.user_list_box.insert("end", f"• {u.name}\n  Stress: {u.base_stress:.2f} | Energy: {u.base_energy:.2f}\n\n")
        self.user_list_box.configure(state="disabled")

    # ==========================================================================
    # TAB 3: SIMULATION LAB
    # ==========================================================================
    def setup_sim_tab(self):
        self.tab_sim.grid_columnconfigure(0, weight=1)
        
        # Controls
        ctrl_frame = ctk.CTkFrame(self.tab_sim)
        ctrl_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(ctrl_frame, text="Select User:").pack(side="left", padx=10)
        self.sim_user_dropdown = ctk.CTkOptionMenu(ctrl_frame, values=[])
        self.sim_user_dropdown.pack(side="left", padx=10)
        
        ctk.CTkButton(ctrl_frame, text="Run 30-Day Simulation", command=self.run_sim_ui).pack(side="right", padx=10)
        
        # Results
        self.sim_results_box = ctk.CTkTextbox(self.tab_sim, font=ctk.CTkFont(family="Courier", size=12))
        self.sim_results_box.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_sim_dropdown()

    def refresh_sim_dropdown(self):
        users = [u.name for u in self.user_manager.get_all_users()]
        if not users: users = ["No Users Found"]
        self.sim_user_dropdown.configure(values=users)
        self.sim_user_dropdown.set(users[0])

    def run_sim_ui(self):
        name = self.sim_user_dropdown.get()
        user = self.user_manager.get_user(name)
        if not user: return
        
        self.sim_results_box.configure(state="normal")
        self.sim_results_box.delete("0.0", "end")
        self.sim_results_box.insert("end", f"Running simulation for {name}...\n")
        self.update() # Force redraw
        
        # Run Sim
        results = run_simulation(user)
        
        # Display Results
        text = f"\n=== RESULTS ===\n"
        text += f"Week 1 Avg Completion: {results['week_1_avg']*100:.1f}%\n"
        text += f"Week 4 Avg Completion: {results['week_4_avg']*100:.1f}%\n"
        text += f"Total Improvement:     {results['improvement']*100:+.1f}%\n\n"
        text += "Daily Progress:\n"
        
        # ASCII Bar Chart
        for i, rate in enumerate(results['daily_completion_rates']):
            bars = "█" * int(rate * 20)
            text += f"Day {i+1:02d}: {bars:<20} ({rate*100:.0f}%)\n"
            
        self.sim_results_box.insert("end", text)
        self.sim_results_box.configure(state="disabled")

if __name__ == "__main__":
    app = App()
    app.mainloop()
