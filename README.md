# Advanced Induction Motor Laboratory Simulator

An interactive, dark-themed modern GUI application designed for simulating induction motor equivalent circuit parameters and visualizing live phasor diagrams. Built for the EEE 3002: Electric Machines laboratory course.

## Features
- Dynamic Parameter Analysis: Real-time calculation of torque-speed curves based on primary motor parameters (V_line, R1, R2, X1, X2, Xm).
- Live Slip Simulation: Interactive slider to monitor changes in rotor speed, angular velocity, output power, and efficiency on the fly.
- Interactive Phasor Diagram: Real-time vector updates for stator current (I1), magnetization current (Im), and referred rotor current (I2').
- Modern UI: Built using customtkinter with a dark laboratory theme.

## Step-by-Step Installation & Execution

Follow these simple steps to set up and run the simulator on your local machine:

1. Clone the Repository
First, open your terminal/command prompt and clone this project:
git clone https://github.com/emreylmzgz/Induction-Motor-Laboratory-Simulator.git
cd Induction-Motor-Laboratory-Simulator

(Alternatively, you can click the green Code button at the top right and select Download ZIP, then extract it).

2. Install Required Dependencies
This project uses CustomTkinter for its modern dark UI, along with standard scientific Python libraries. Install them all with a single command:
pip install customtkinter numpy matplotlib pillow

3. Launch the Application
Run the main script to open the interactive dashboard:
python projectfinal.py


## Group Members & Project Credits
* Efe Ateş - Developer / Undergraduate Student 
* Özgür Metin - Developer / Undergraduate Student
* Emre Yılmazgöz - Developer / Undergraduate Student 

Academic Supervisor: Res. Asst. Dr. Ali Can Erüst  
Course: EEE 3002: Electric Machines Laboratory  
Term: Spring 2026
