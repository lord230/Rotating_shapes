import tkinter as tk
from tkinter import ttk
import numpy as np
import math
import subprocess
import sys


class ShapeDrawer:
    def __init__(self, canvas, project_func):
        self.canvas = canvas
        self.project = project_func

    def draw_donut(self, size, ax, ay, az):
        R, r = size * 0.8, size * 0.3
        theta = np.linspace(0, 2 * np.pi, 30)
        phi = np.linspace(0, 2 * np.pi, 30)

        for t in theta:
            for p in phi:
                x = (R + r * math.cos(p)) * math.cos(t)
                y = (R + r * math.cos(p)) * math.sin(t)
                z = r * math.sin(p)
                x, y, z = self.rotate(x, y, z, ax, ay, az)
                px, py = self.project(x, y, z)
                self.canvas.create_oval(px, py, px+2, py+2, fill='white')

    def draw_cube(self, size, ax, ay, az):
        s = size
        vertices = [
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s]
        ]
        rotated = [self.project(*self.rotate(x, y, z, ax, ay, az)) for x, y, z in vertices]
        edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
        for a, b in edges:
            self.canvas.create_line(*rotated[a], *rotated[b], fill='white')

    def draw_triangle(self, size, ax, ay, az):
        s = size
        vertices = [[0,-s,0], [-s,s,-s], [s,s,-s], [0,s,s]]
        rotated = [self.project(*self.rotate(x, y, z, ax, ay, az)) for x, y, z in vertices]
        edges = [(0,1),(1,2),(2,0),(0,3),(1,3),(2,3)]
        for a, b in edges:
            self.canvas.create_line(*rotated[a], *rotated[b], fill='white')

    def rotate(self, x, y, z, ax, ay, az):
        y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
        x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
        x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
        return x, y, z


class Rotating3DShapes:
    def __init__(self, root):
        self.root = root
        self.root.title("Rotating 3D Shapes Visualizer")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=580, height=500, bg='black', highlightthickness=2, highlightbackground="#444")
        self.canvas.pack(padx=10, pady=10)

        self.rotation_speed = tk.DoubleVar(value=0.05)
        self.shape_size = tk.DoubleVar(value=100)
        self.shape_choice = tk.StringVar(value='Donut')
        self.rotate_x = tk.BooleanVar(value=True)
        self.rotate_y = tk.BooleanVar(value=True)
        self.rotate_z = tk.BooleanVar(value=False)

        self.angle_x = self.angle_y = self.angle_z = 0 

        self.drawer = ShapeDrawer(self.canvas, self.project)
        self.setup_controls()
        self.update_animation()

    def setup_controls(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#222")
        style.configure("TLabel", background="#222", foreground="#ddd", font=("Segoe UI", 10))
        style.configure("TCheckbutton", background="#222", foreground="#ddd", font=("Segoe UI", 9))
        style.configure("TButton", background="#444", foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[('active', '#666')])

        controls = ttk.Frame(self.root)
        controls.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(controls, text="Rotation Speed").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Scale(controls, from_=0.01, to=0.2, variable=self.rotation_speed, length=200).grid(row=0, column=1)

        ttk.Label(controls, text="Size").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Scale(controls, from_=50, to=200, variable=self.shape_size, length=200).grid(row=1, column=1)

        ttk.Label(controls, text="Shape").grid(row=2, column=0, sticky="w", padx=5)
        shape_combo = ttk.Combobox(controls, values=["Donut", "Cube", "Triangle"],
                                   textvariable=self.shape_choice, state='readonly', font=("Segoe UI", 9))
        shape_combo.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(controls, text="Rotate Axes").grid(row=3, column=0, sticky="w", padx=5)
        axis_frame = ttk.Frame(controls)
        axis_frame.grid(row=3, column=1, sticky="w")
        ttk.Checkbutton(axis_frame, text="X", variable=self.rotate_x).pack(side=tk.LEFT, padx=3)
        ttk.Checkbutton(axis_frame, text="Y", variable=self.rotate_y).pack(side=tk.LEFT, padx=3)
        ttk.Checkbutton(axis_frame, text="Z", variable=self.rotate_z).pack(side=tk.LEFT, padx=3)

        ttk.Button(controls, text="How it Works", command=self.show_help).grid(row=4, columnspan=2, pady=10)

    def project(self, x, y, z):
        scale = 250 / (z + 300)
        return int(x * scale + 290), int(y * scale + 250)

    def update_animation(self):
        self.canvas.delete("all")
        shape = self.shape_choice.get()
        size = self.shape_size.get()

        if shape == 'Donut':
            self.drawer.draw_donut(size, self.angle_x, self.angle_y, self.angle_z)
        elif shape == 'Cube':
            self.drawer.draw_cube(size, self.angle_x, self.angle_y, self.angle_z)
        else:
            self.drawer.draw_triangle(size, self.angle_x, self.angle_y, self.angle_z)

        speed = self.rotation_speed.get()
        if self.rotate_x.get(): self.angle_x += speed
        if self.rotate_y.get(): self.angle_y += speed
        if self.rotate_z.get(): self.angle_z += speed

        self.root.after(30, self.update_animation)

    def show_help(self):
        HelpWindow(self.root)


class HelpWindow:
    def __init__(self, master):
        top = tk.Toplevel(master)
        top.title("📘 How It Works")
        top.geometry("460x360")
        top.resizable(False, False)
        top.configure(bg="#222")

        # Frame for padding
        container = tk.Frame(top, bg="#222")
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = tk.Scrollbar(container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Text widget for help message
        text_widget = tk.Text(
            container,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg="#1e1e1e",
            fg="white",
            insertbackground="white",
            borderwidth=0,
            yscrollcommand=scrollbar.set
        )
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Connect scrollbar
        scrollbar.config(command=text_widget.yview)

        # Help content
        help_message = (
            " Welcome to the Rotating 3D Shapes Visualizer!\n\n"
            " Features:\n"
            "• Rotate Donut, Cube, or Tetrahedron (Triangle).\n"
            "• Adjust rotation speed and shape size.\n"
            "• Toggle rotation along X, Y, and Z axes.\n\n"
            " Behind the Scenes:\n"
            "• Shapes are built in 3D using math.\n"
            "• Each frame rotates the shape in 3D space using rotation matrices.\n"
            "• 3D coordinates are projected onto a 2D canvas using perspective projection.\n\n"
            " Great for visual learners, geometry fans, or just fun spinning shapes!\n\n"
            " Built with love using Python, Tkinter, and NumPy.\n\n"
            " Tip: Try enabling only Z rotation on the Donut to get a cool hypnotic effect!"
        )

        text_widget.insert(tk.END, help_message)
        text_widget.config(state=tk.DISABLED)  # Make it read-only

def install_modules(modules):
    for module in modules:
        try:
            __import__(module)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])


if __name__ == "__main__":
    root = tk.Tk()
    app = Rotating3DShapes(root)
    root.mainloop()
