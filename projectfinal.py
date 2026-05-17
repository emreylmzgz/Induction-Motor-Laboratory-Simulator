import customtkinter as ctk
import numpy as np
import math
import cmath
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MotorAnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Advanced Induction Motor Laboratory Simulator")
        self.geometry("1350x920") 
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="nsew")
        
        self.tab_simulator = self.tabview.add("Simulation Dashboard")
        self.tab_details = self.tabview.add("Project Details & Credits")
        
        self.tabview._segmented_button.configure(font=ctk.CTkFont(size=14, weight="bold"))

        # --- TAB 1 ---
        self.tab_simulator.grid_columnconfigure(1, weight=1)
        self.tab_simulator.grid_rowconfigure(0, weight=1)
        
        self.create_sidebar(self.tab_simulator)
        self.create_main_area(self.tab_simulator)
        
        # --- TAB 2 ---
        self.create_details_tab()

        # --- FOOTER ---
        self.create_marquee_footer()

        self.full_recalculate()

    def create_sidebar(self, parent):
        self.sidebar_frame = ctk.CTkFrame(parent, width=320, corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(12, weight=1)

        ctk.CTkLabel(self.sidebar_frame, text="Motor Parameters", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10), columnspan=2)

        self.inputs = {
            "V_line (V):": "460", "P_rated (kW):": "20", "Frequency (Hz):": "60", "Poles:": "6",
            "R1 (Ω):": "0.271", "R2 (Ω):": "0.188", "X1 (Ω):": "1.12", "X2 (Ω):": "1.91",
            "Xm (Ω):": "23.10", "P_rot (W):": "320"
        }
        self.entries = {}

        row_idx = 1
        for label_text, default_val in self.inputs.items():
            ctk.CTkLabel(self.sidebar_frame, text=label_text).grid(row=row_idx, column=0, padx=15, pady=5, sticky="w")
            entry = ctk.CTkEntry(self.sidebar_frame, width=90)
            entry.insert(0, default_val)
            entry.grid(row=row_idx, column=1, padx=15, pady=5, sticky="e")
            self.entries[label_text] = entry
            row_idx += 1

        self.calc_button = ctk.CTkButton(self.sidebar_frame, text="Update Parameters", command=self.full_recalculate, font=ctk.CTkFont(weight="bold"))
        self.calc_button.grid(row=row_idx, column=0, columnspan=2, padx=20, pady=15)
        row_idx += 1

        ctk.CTkLabel(self.sidebar_frame, text="Live Simulation (Slip %)", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00d2ff").grid(row=row_idx, column=0, columnspan=2, pady=(20,0))
        row_idx += 1
        
        self.slip_var = ctk.DoubleVar(value=1.6)
        self.lbl_slip = ctk.CTkLabel(self.sidebar_frame, text=f"s = 1.60%")
        self.lbl_slip.grid(row=row_idx, column=0, columnspan=2)
        row_idx += 1
        
        self.slider_slip = ctk.CTkSlider(self.sidebar_frame, from_=0.1, to=100.0, variable=self.slip_var, command=self.update_realtime)
        self.slider_slip.grid(row=row_idx, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

    def create_main_area(self, parent):
        self.main_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=5, pady=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.dashboard_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.dashboard_frame.grid(row=0, column=0, pady=(0, 15), sticky="ew")
        self.dashboard_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.cards = {}
        metrics = [
            ("Rotor Speed nₘ (RPM)", "0.00"), ("Angular Speed ωₘ (rad/s)", "0.00"),
            ("Output Torque Tₒᵤₜ (N·m)", "0.00"), ("Output Power Pₒᵤₜ (kW)", "0.00"),
            ("Stator Current I₁ (A)", "0.00"), ("Rotor Current I₂' (A)", "0.00"),
            ("Power Factor cosφ", "0.00"), ("Efficiency η (%)", "0.00")
        ]
        
        for i, (title, val) in enumerate(metrics):
            row = i // 4
            col = i % 4
            
            card = ctk.CTkFrame(self.dashboard_frame, corner_radius=10, fg_color="#2b2b2b")
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            
            lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color="#a9a9a9")
            lbl_title.pack(pady=(12, 0))
            
            lbl_val = ctk.CTkLabel(card, text=val, font=ctk.CTkFont(size=22, weight="bold"), text_color="#00d2ff")
            lbl_val.pack(pady=(4, 12))
            
            self.cards[title] = lbl_val

        self.fig = Figure(figsize=(11, 5), dpi=100)
        self.fig.patch.set_facecolor('#1e1e1e') 
        
        gs = self.fig.add_gridspec(1, 3)
        
        self.ax1 = self.fig.add_subplot(gs[0, :2])
        self.ax1.set_facecolor('#1e1e1e')
        
        self.ax2 = self.fig.add_subplot(gs[0, 2])
        self.ax2.set_facecolor('#1e1e1e')
        self.ax2.set_title("Interactive Phasor Diagram", color='white', pad=10, fontweight='bold')
        self.ax2.set_xlim(-1.2, 1.2)
        self.ax2.set_ylim(-1.2, 1.2)
        self.ax2.axis('off') 
        
        self.quiver = self.ax2.quiver([0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], 
                                      color=['#ffcc00', '#00d2ff', '#ff4757', '#2ed573'], 
                                      angles='xy', scale_units='xy', scale=1, width=0.012)
        
        self.txt_v = self.ax2.text(1.05, 0, "V₁", color='#ffcc00', fontsize=11, fontweight='bold', va='center')
        self.txt_i1 = self.ax2.text(0, 0, "I₁", color='#00d2ff', fontsize=11, fontweight='bold')
        self.txt_im = self.ax2.text(0, 0, "Iₘ", color='#ff4757', fontsize=11, fontweight='bold')
        self.txt_i2 = self.ax2.text(0, 0, "I₂'", color='#2ed573', fontsize=11, fontweight='bold')
        self.txt_pf_status = self.ax2.text(0, -1.3, "Status: -", color='#a9a9a9', fontsize=10, ha='center')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

    def create_details_tab(self):
        """Project Details and Group Members Tab (Completely in English)"""
        self.tab_details.grid_columnconfigure(0, weight=1)
        self.tab_details.grid_rowconfigure(0, weight=1)

        info_card = ctk.CTkFrame(self.tab_details, fg_color="#2b2b2b", corner_radius=15)
        info_card.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        
        info_card.grid_columnconfigure(0, weight=1) 
        info_card.grid_columnconfigure(1, weight=3) 

        # --- LEFT SIDE: LOGO ---
        logo_frame = ctk.CTkFrame(info_card, fg_color="transparent")
        logo_frame.grid(row=0, column=0, rowspan=4, padx=30, pady=40, sticky="nsew")
        
        logo_path = "okul_logosu.png" 
        
        if os.path.exists(logo_path):
            pil_image = Image.open(logo_path)
            ctk_logo = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(180, 180))
            lbl_logo = ctk.CTkLabel(logo_frame, image=ctk_logo, text="")
            lbl_logo.pack(expand=True)
        else:
            lbl_logo = ctk.CTkLabel(logo_frame, text="[ LOGO NOT FOUND ]\n(Please place 'okul_logosu.png'\nin the project folder)", 
                                    font=ctk.CTkFont(size=12, weight="bold"), text_color="#ff4757", width=180, height=180, fg_color="#1e1e1e", corner_radius=10)
            lbl_logo.pack(expand=True)

        # --- RIGHT SIDE: PROJECT METADATA ---
        text_content_frame = ctk.CTkFrame(info_card, fg_color="transparent")
        text_content_frame.grid(row=0, column=1, padx=(0, 40), pady=20, sticky="nsew")

        ctk.CTkLabel(text_content_frame, text="LABORATORY PROJECT INFORMATION", font=ctk.CTkFont(size=22, weight="bold"), text_color="#00d2ff", anchor="w").pack(fill="x", pady=(20, 10))
        
        separator = ctk.CTkFrame(text_content_frame, height=2, fg_color="#3a3a3a")
        separator.pack(fill="x", pady=10)

        details = [
            ("Course Title:", "EEE 3002: Electric Machines"),
            ("Project Topic:", "Induction Motor Parameter Analyzer & Live Phasor Diagram Simulator"),
            ("Supervisor:", "Res. Asst. Dr. Ali Can Erüst"),
            ("Submission Date:", "May 2026")
        ]

        for label, val in details:
            row_f = ctk.CTkFrame(text_content_frame, fg_color="transparent")
            row_f.pack(fill="x", pady=6)
            ctk.CTkLabel(row_f, text=label, font=ctk.CTkFont(size=13, weight="bold"), text_color="#a9a9a9", width=180, anchor="w").pack(side="left")
            ctk.CTkLabel(row_f, text=val, font=ctk.CTkFont(size=13), text_color="white", anchor="w").pack(side="left", padx=10)

        # --- GROUP MEMBERS ---
        ctk.CTkLabel(text_content_frame, text="PROJECT DEVELOPERS / GROUP MEMBERS", font=ctk.CTkFont(size=15, weight="bold"), text_color="#2ed573", anchor="w").pack(fill="x", pady=(25, 10))
        
        students_frame = ctk.CTkFrame(text_content_frame, fg_color="#1e1e1e", corner_radius=10)
        students_frame.pack(fill="x", pady=5)

        students = [
            ("Efe Ateş", "240702601"),
            ("Özgür Metin", "230702001"),
            ("Emre Yılmazgöz", "230702057")
        ]

        for name, student_id in students:
            s_row = ctk.CTkFrame(students_frame, fg_color="transparent")
            s_row.pack(fill="x", padx=20, pady=6)
            ctk.CTkLabel(s_row, text=name, font=ctk.CTkFont(size=13, weight="bold"), text_color="white").pack(side="left")
            ctk.CTkLabel(s_row, text=f"ID: {student_id}", font=ctk.CTkFont(size=12), text_color="#00d2ff").pack(side="right")

    def create_marquee_footer(self):
        self.footer_frame = ctk.CTkFrame(self, height=35, fg_color="#1e1e1e", corner_radius=5)
        self.footer_frame.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="ew")
        self.footer_frame.pack_propagate(False)

        
        self.marquee_text = "   ***   EEE 3002: Electric Machines Laboratory Project   ***   Project Developers: Efe Ateş - Özgür Metin - Emre Yılmazgöz   ***   Supervisor: Res. Asst. Dr. Ali Can Erüst   ***   Topic: Advanced Induction Motor Laboratory Simulator   ***   "
        
        self.lbl_marquee = ctk.CTkLabel(self.footer_frame, text=self.marquee_text, font=ctk.CTkFont(size=13, weight="bold"), text_color="#ffcc00")
        self.lbl_marquee.place(x=1350, y=4)
        
        self.marquee_x = 1350
        self.animate_marquee()

    def animate_marquee(self):
        self.marquee_x -= 1.5
        if self.marquee_x < -1300: 
            self.marquee_x = 1350
        self.lbl_marquee.place(x=self.marquee_x, y=4)
        self.after(20, self.animate_marquee)

    def full_recalculate(self):
        try:
            self.v_line = float(self.entries["V_line (V):"].get())
            self.f = float(self.entries["Frequency (Hz):"].get())
            self.poles = float(self.entries["Poles:"].get())
            self.r1 = float(self.entries["R1 (Ω):"].get())
            self.r2 = float(self.entries["R2 (Ω):"].get())
            self.x1 = float(self.entries["X1 (Ω):"].get())
            self.x2 = float(self.entries["X2 (Ω):"].get())
            self.xm = float(self.entries["Xm (Ω):"].get())
            self.p_rot = float(self.entries["P_rot (W):"].get())

            self.v_phase = self.v_line / math.sqrt(3)
            self.n_sync = 120 * self.f / self.poles
            self.omega_sync = self.n_sync * 2 * math.pi / 60

            s_array = np.linspace(0.001, 1, 300)
            self.n_m_array = (1 - s_array) * self.n_sync
            
            Z2_arr = self.r2 / s_array + 1j * self.x2
            Zm_arr = 1j * self.xm
            Zf_arr = (Z2_arr * Zm_arr) / (Z2_arr + Zm_arr)
            Zin_arr = self.r1 + 1j * self.x1 + Zf_arr
            I1_arr = self.v_phase / Zin_arr
            
            Pgap_arr = 3 * (np.abs(I1_arr)**2) * Zf_arr.real
            Pconv_arr = (1 - s_array) * Pgap_arr
            Pout_arr = Pconv_arr - self.p_rot
            
            omega_m_array = np.where(self.n_m_array > 0, self.n_m_array * 2 * np.pi / 60, 0.001)
            self.T_out_arr = np.where(Pout_arr > 0, Pout_arr / omega_m_array, 0)

            self.ax1.clear()
            self.ax1.plot(self.n_m_array, self.T_out_arr, color='#00d2ff', linewidth=2.5, label='Net Output Torque Curve')
            
            self.ax1.set_title("Speed - Net Torque Characteristics", color='white', pad=10, fontweight='bold')
            self.ax1.set_xlabel("Rotor Speed nₘ (r/min)", color='#a9a9a9')
            self.ax1.set_ylabel("Net Torque Tₒᵤₜ (N·m)", color='#a9a9a9')
            self.ax1.tick_params(colors='#a9a9a9')
            self.ax1.grid(True, linestyle=':', alpha=0.3, color='white')
            self.ax1.set_xlim(0, self.n_sync + 50)
            self.ax1.set_ylim(0, max(self.T_out_arr) * 1.1)
            
            self.point_op, = self.ax1.plot([], [], 'ro', markersize=9, label='Operating Point', zorder=5)
            self.line_v, = self.ax1.plot([], [], color='#ff4757', linestyle='--', alpha=0.6)
            self.line_h, = self.ax1.plot([], [], color='#ff4757', linestyle='--', alpha=0.6)
            
            self.ax1.legend(loc="upper right", facecolor='#2b2b2b', edgecolor='#2b2b2b', labelcolor='white')
            
            self.update_realtime(self.slip_var.get())

        except Exception as e:
            print("Calculation Error:", e)

    def update_realtime(self, current_slip_percentage):
        s_target = float(current_slip_percentage) / 100.0
        if s_target <= 0: s_target = 0.0001
        
        self.lbl_slip.configure(text=f"Slip s = {current_slip_percentage:.2f}%")

        z2_target = complex(self.r2 / s_target, self.x2)
        zm = complex(0, self.xm)
        z_gap_target = (z2_target * zm) / (z2_target + zm)
        z_in_target = complex(self.r1, self.x1) + z_gap_target
        
        i1_target = self.v_phase / z_in_target
        i1_mag = abs(i1_target)
        i1_ang = cmath.phase(i1_target) 
        pf = math.cos(i1_ang)
        
        e1_target = self.v_phase - i1_target * complex(self.r1, self.x1)
        im_target = e1_target / zm
        i2_target = e1_target / z2_target
        
        im_mag = abs(im_target)
        i2_mag = abs(i2_target)
        
        p_gap_target = 3 * (i1_mag**2) * z_gap_target.real
        p_conv_target = (1 - s_target) * p_gap_target
        p_out_target = p_conv_target - self.p_rot
        
        n_m_target = (1 - s_target) * self.n_sync
        omega_m_target = n_m_target * 2 * math.pi / 60
        
        t_out_target = max(0, p_out_target / omega_m_target) if omega_m_target > 0 else 0
        
        p_in_target = 3 * self.v_phase * i1_mag * pf
        efficiency = (p_out_target / p_in_target * 100) if p_in_target > 0 else 0

        self.cards["Rotor Speed nₘ (RPM)"].configure(text=f"{n_m_target:.0f}")
        self.cards["Angular Speed ωₘ (rad/s)"].configure(text=f"{omega_m_target:.1f}")
        self.cards["Output Torque Tₒᵤₜ (N·m)"].configure(text=f"{t_out_target:.1f}")
        self.cards["Output Power Pₒᵤₜ (kW)"].configure(text=f"{p_out_target/1000:.2f}" if p_out_target > 0 else "0.00")
        self.cards["Stator Current I₁ (A)"].configure(text=f"{i1_mag:.1f}")
        self.cards["Rotor Current I₂' (A)"].configure(text=f"{i2_mag:.1f}")
        self.cards["Power Factor cosφ"].configure(text=f"{pf:.3f}")
        self.cards["Efficiency η (%)"].configure(text=f"{efficiency:.1f}%" if efficiency > 0 else "0.0%")

        self.point_op.set_data([n_m_target], [t_out_target])
        self.line_v.set_data([n_m_target, n_m_target], [0, t_out_target])
        self.line_h.set_data([0, n_m_target], [t_out_target, t_out_target])
        
        scale_i1 = 0.75 / i1_mag if i1_mag > 0 else 1.0
        
        v1_vec = complex(1.0, 0.0)
        i1_vec = i1_target * scale_i1
        im_vec = im_target * scale_i1
        i2_vec = i2_target * scale_i1
        
        X_starts = [0, 0, 0, im_vec.real]
        Y_starts = [0, 0, 0, im_vec.imag]
        
        U_lengths = [v1_vec.real, i1_vec.real, im_vec.real, i2_vec.real]
        V_lengths = [v1_vec.imag, i1_vec.imag, im_vec.imag, i2_vec.imag]
        
        self.quiver.set_offsets(np.column_stack([X_starts, Y_starts]))
        self.quiver.set_UVC(U_lengths, V_lengths)
        
        self.txt_v.set_position((1.05, 0.02))
        self.txt_i1.set_position((i1_vec.real * 1.15, i1_vec.imag * 1.15))
        self.txt_im.set_position((im_vec.real * 0.5 - 0.15, im_vec.imag * 0.5))
        self.txt_i2.set_position((im_vec.real + i2_vec.real * 0.5 + 0.08, im_vec.imag + i2_vec.imag * 0.5))
        
        self.txt_i1.set_text(f"I₁ ({math.degrees(cmath.phase(i1_target)):.1f}°)")
        self.txt_im.set_text(f"Iₘ ({math.degrees(cmath.phase(im_target)):.1f}°)")
        self.txt_i2.set_text(f"I₂'")
        self.txt_v.set_text(f"V₁ ({self.v_phase:.0f}V)")
        
        self.txt_pf_status.set_text(f"Status: Inductive (Lagging) | cosφ = {pf:.2f}")

        self.canvas.draw_idle()

if __name__ == "__main__":
    app = MotorAnalyzerApp()
    app.mainloop()
