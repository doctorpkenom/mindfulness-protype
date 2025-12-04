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

# Configuration
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # System Setup
        self.engine = ResearchEngine()
        self.coordinator = OnlineCoordinator()
        self.all_strategies = self.engine.strategies
        
        # Window Setup
        self.title("Curiosity Co-Pilot (Prototype)")
        self.geometry("400x700")
        self.resizable(False, False)

        # Layout Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Content
        self.grid_rowconfigure(2, weight=0) # Controls

        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        
        self.logo_label = ctk.CTkLabel(self.header_frame, text="Mindfulness Prototype", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(side="left")
        
        self.status_label = ctk.CTkLabel(self.header_frame, text="● Online", text_color="#00FF00", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="right", pady=5)

        # --- MAIN CONTENT AREA ---
        self.content_frame = ctk.CTkFrame(self, fg_color="#1A1A1A", corner_radius=15)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # 1. Context Display
        self.context_label = ctk.CTkLabel(self.content_frame, text="Current State", font=ctk.CTkFont(size=14, weight="bold"))
        self.context_label.pack(pady=(20, 5))
        
        self.context_value = ctk.CTkLabel(self.content_frame, text="Waiting for drift...", text_color="gray")
        self.context_value.pack(pady=(0, 20))

        # 2. Intervention Card (Hidden initially)
        self.card_frame = ctk.CTkFrame(self.content_frame, fg_color="#2B2B2B", corner_radius=10, border_width=1, border_color="#404040")
        self.card_frame.pack(fill="x", padx=20, pady=10)
        
        self.strat_title = ctk.CTkLabel(self.card_frame, text="Strategy Name", font=ctk.CTkFont(size=16, weight="bold"), wraplength=280)
        self.strat_title.pack(pady=(15, 5), padx=10)
        
        self.strat_desc = ctk.CTkLabel(self.card_frame, text="Strategy logic will appear here...", font=ctk.CTkFont(size=12), text_color="#AAAAAA", wraplength=280)
        self.strat_desc.pack(pady=(0, 10), padx=10)
        
        self.strat_source = ctk.CTkLabel(self.card_frame, text="Source: Research", font=ctk.CTkFont(size=10, slant="italic"), text_color="#666666")
        self.strat_source.pack(pady=(0, 15))

        # --- CONTROLS ---
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Simulation Controls
        self.sim_btn = ctk.CTkButton(self.controls_frame, text="Simulate 'Drift' Event", command=self.simulate_drift, height=50, font=ctk.CTkFont(size=15, weight="bold"))
        self.sim_btn.pack(fill="x", pady=10)
        
        # Feedback Controls (Hidden initially)
        self.feedback_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        
        self.accept_btn = ctk.CTkButton(self.feedback_frame, text="✓ Completed", fg_color="#2CC985", hover_color="#229965", command=lambda: self.give_feedback(True))
        self.accept_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.reject_btn = ctk.CTkButton(self.feedback_frame, text="✕ Failed", fg_color="#FF4B4B", hover_color="#CC3333", command=lambda: self.give_feedback(False))
        self.reject_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # State
        self.current_strategy = None
        self.current_context = None

    def simulate_drift(self):
        """Simulates the app detecting a user drifting off task."""
        self.sim_btn.pack_forget()
        self.status_label.configure(text="● Processing...", text_color="#FFFF00")
        
        # 1. Generate Random Context
        energy = random.choice(["low", "medium", "high"])
        stress = random.choice(["low", "medium", "high"])
        self.current_context = {"energy": energy, "stress": stress}
        
        self.context_value.configure(text=f"Energy: {energy.upper()} | Stress: {stress.upper()}", text_color="white")
        
        # 2. Get Recommendation from ML
        # Run in thread to not freeze UI (though it's fast)
        threading.Thread(target=self.get_recommendation).start()

    def get_recommendation(self):
        time.sleep(0.5) # Fake processing delay for effect
        
        # Call the actual ML Coordinator
        strategy = self.coordinator.select_strategy(self.current_context, self.all_strategies)
        self.current_strategy = strategy
        
        # Update UI
        self.strat_title.configure(text=strategy["name"])
        self.strat_desc.configure(text=strategy["logic"].replace("[", "").replace("]", "")) # Clean up template text
        self.strat_source.configure(text=f"Source: {strategy.get('source_title', 'Unknown')}")
        
        self.status_label.configure(text="● Intervention Active", text_color="#00AAFF")
        self.feedback_frame.pack(fill="x", pady=10)

    def give_feedback(self, success):
        """User reports outcome."""
        if self.current_strategy:
            # Send to ML
            self.coordinator.log_outcome(self.current_strategy["name"], success)
            
            # UI Feedback
            if success:
                self.strat_title.configure(text="Great Job!")
                self.strat_desc.configure(text="Streak increased. Weights updated.")
            else:
                self.strat_title.configure(text="No Worries")
                self.strat_desc.configure(text="We'll try something different next time.")
                
            self.feedback_frame.pack_forget()
            
            # Reset after delay
            self.after(2000, self.reset_ui)

    def reset_ui(self):
        self.strat_title.configure(text="Ready")
        self.strat_desc.configure(text="Waiting for next event...")
        self.strat_source.configure(text="")
        self.context_value.configure(text="Waiting for drift...", text_color="gray")
        self.status_label.configure(text="● Online", text_color="#00FF00")
        self.sim_btn.pack(fill="x", pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()
