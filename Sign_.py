import speech_recognition as sr
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import os
import threading
import time

class SignLanguageConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech to Sign Language Converter")
        self.root.geometry("1100x750")
        self.root.configure(bg='#0f1419')
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        
        # Animation variables
        self.pulse_alpha = 0
        self.pulse_direction = 1
        
        # Sign language images directory
        self.sign_images_dir = "sign_language_images"
        
        # Check if directory exists
        if not os.path.exists(self.sign_images_dir):
            os.makedirs(self.sign_images_dir)
        
        self.setup_ui()
        self.start_animations()
    
    def setup_ui(self):
        """Setup the modern user interface"""
        
        # Main container with gradient effect
        main_frame = tk.Frame(self.root, bg='#0f1419')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header Section with gradient background
        header_frame = tk.Frame(main_frame, bg='#1a1f2e', height=120)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Title with animated gradient effect
        title_container = tk.Frame(header_frame, bg='#1a1f2e')
        title_container.place(relx=0.5, rely=0.5, anchor='center')
        
        title_label = tk.Label(
            title_container,
            text=" Speech to Sign Language",
            font=("Segoe UI", 32, "bold"),
            bg='#1a1f2e',
            fg='#00d4ff'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_container,
            
            font=("Segoe UI", 11),
            bg='#1a1f2e',
            fg='#8b95a5'
        )
        subtitle_label.pack()
        
        # Control Panel with modern card design
        control_card = tk.Frame(main_frame, bg='#1a1f2e', bd=0)
        control_card.pack(fill=tk.X, pady=(0, 15))
        
        # Inner control frame with padding
        control_inner = tk.Frame(control_card, bg='#1a1f2e')
        control_inner.pack(padx=30, pady=25)
        
        # Status indicator with pulse animation
        self.status_indicator = tk.Canvas(control_inner, width=20, height=20, bg='#1a1f2e', highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 10))
        self.status_circle = self.status_indicator.create_oval(4, 4, 16, 16, fill='#4caf50', outline='')
        
        # Modern buttons with hover effects
        button_style = {
            'font': ("Segoe UI", 13, "bold"),
            'fg': 'white',
            'cursor': 'hand2',
            'relief': tk.FLAT,
            'bd': 0,
            'padx': 25,
            'pady': 12
        }
        
        self.listen_btn = tk.Button(
            control_inner,
            text="🎤 Start Listening",
            bg='#00d4ff',
            activebackground="#03748d",
            command=self.toggle_listening,
            **button_style
        )
        self.listen_btn.pack(side=tk.LEFT, padx=8)
        self.add_hover_effect(self.listen_btn, '#00d4ff', '#00b8e6')
        
        manual_btn = tk.Button(
            control_inner,
            text="⌨️ Type Text",
            bg='#7c4dff',
            activebackground='#6a3de8',
            command=self.manual_input,
            **button_style
        )
        manual_btn.pack(side=tk.LEFT, padx=8)
        self.add_hover_effect(manual_btn, '#7c4dff', '#6a3de8')
        
        clear_btn = tk.Button(
            control_inner,
            text="🗑️ Clear",
            bg='#ff4757',
            activebackground='#ee3344',
            command=self.clear_display,
            **button_style
        )
        clear_btn.pack(side=tk.LEFT, padx=8)
        self.add_hover_effect(clear_btn, '#ff4757', '#ee3344')
        
        # Status label with smooth updates
        self.status_label = tk.Label(
            control_inner,
            text="● Ready",
            font=("Segoe UI", 12),
            bg='#1a1f2e',
            fg='#4caf50'
        )
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Recognized Text Card
        text_card = tk.Frame(main_frame, bg='#1a1f2e', bd=0)
        text_card.pack(fill=tk.X, pady=(0, 15))
        
        text_header = tk.Frame(text_card, bg='#252b3b', height=45)
        text_header.pack(fill=tk.X)
        text_header.pack_propagate(False)
        
        tk.Label(
            text_header,
            text="📝 Recognized Text",
            font=("Segoe UI", 13, "bold"),
            bg='#252b3b',
            fg='#ffffff'
        ).pack(side=tk.LEFT, padx=20, pady=10)
        
        text_content = tk.Frame(text_card, bg='#1a1f2e')
        text_content.pack(fill=tk.X, padx=20, pady=15)
        
        self.text_display = tk.Text(
            text_content,
            height=3,
            font=("Segoe UI", 13),
            bg='#252b3b',
            fg='#ffffff',
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=12,
            insertbackground='#00d4ff'
        )
        self.text_display.pack(fill=tk.X)
        
        # Sign Language Display Card
        sign_card = tk.Frame(main_frame, bg='#1a1f2e', bd=0)
        sign_card.pack(fill=tk.BOTH, expand=True)
        
        sign_header = tk.Frame(sign_card, bg='#252b3b', height=45)
        sign_header.pack(fill=tk.X)
        sign_header.pack_propagate(False)
        
        tk.Label(
            sign_header,
            text="🤲 Sign Language Display",
            font=("Segoe UI", 13, "bold"),
            bg='#252b3b',
            fg='#ffffff'
        ).pack(side=tk.LEFT, padx=20, pady=10)
        
        # Canvas with scrollbar for signs
        canvas_container = tk.Frame(sign_card, bg='#1a1f2e')
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Custom styled scrollbar
        scrollbar = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL)
        
        self.canvas = tk.Canvas(
            canvas_container,
            bg='#252b3b',
            highlightthickness=0,
            xscrollcommand=scrollbar.set
        )
        
        scrollbar.config(command=self.canvas.xview)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.image_frame = tk.Frame(self.canvas, bg='#252b3b')
        self.canvas.create_window((20, 20), window=self.image_frame, anchor=tk.NW)
        
        self.image_frame.bind('<Configure>', 
                             lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        
        # Store references
        self.displayed_images = []
        
        # Configure scrollbar style
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Horizontal.TScrollbar",
                       background='#1a1f2e',
                       troughcolor='#252b3b',
                       borderwidth=0,
                       arrowsize=0)
    
    def add_hover_effect(self, button, normal_color, hover_color):
        """Add hover effect to buttons"""
        def on_enter(e):
            button.config(bg=hover_color)
        
        def on_leave(e):
            button.config(bg=normal_color)
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
    
    def start_animations(self):
        """Start background animations"""
        self.animate_status_indicator()
    
    def animate_status_indicator(self):
        """Animate the status indicator with pulse effect"""
        if self.is_listening:
            self.pulse_alpha += self.pulse_direction * 15
            
            if self.pulse_alpha >= 100:
                self.pulse_alpha = 100
                self.pulse_direction = -1
            elif self.pulse_alpha <= 0:
                self.pulse_alpha = 0
                self.pulse_direction = 1
            
            # Update color with pulse
            intensity = int(255 * (1 - self.pulse_alpha / 200))
            color = f'#{intensity:02x}{255:02x}{intensity:02x}'
            self.status_indicator.itemconfig(self.status_circle, fill=color)
        
        self.root.after(50, self.animate_status_indicator)
    
    def toggle_listening(self):
        """Toggle speech recognition with smooth transitions"""
        if not self.is_listening:
            self.is_listening = True
            self.listen_btn.config(text="⏹️ Stop Listening", bg='#ff4757')
            self.status_label.config(text="● Listening...", fg='#00ff88')
            self.add_hover_effect(self.listen_btn, '#ff4757', '#ee3344')
            threading.Thread(target=self.listen_to_speech, daemon=True).start()
        else:
            self.is_listening = False
            self.listen_btn.config(text="🎤 Start Listening", bg='#00d4ff')
            self.status_label.config(text="● Stopped", fg='#ff4757')
            self.add_hover_effect(self.listen_btn, '#00d4ff', '#00b8e6')
            self.status_indicator.itemconfig(self.status_circle, fill='#4caf50')
    
    def manual_input(self):
        """Manual text input with modern dialog"""
        text = simpledialog.askstring(
            "Manual Text Input",
            "Enter text to convert to sign language:",
            parent=self.root
        )
        
        if text and text.strip():
            self.process_text(text.strip())
            self.fade_in_status("● Text converted!", '#00d4ff')
        else:
            self.fade_in_status("● No text entered", '#ff4757')
    
    def fade_in_status(self, text, color):
        """Fade in status message"""
        self.status_label.config(text=text, fg=color)
        self.root.after(3000, lambda: self.status_label.config(text="● Ready", fg='#4caf50'))
    
    def listen_to_speech(self):
        """Listen to speech with improved error handling"""
        try:
            with sr.Microphone() as source:
                self.status_label.config(text="● Adjusting...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                while self.is_listening:
                    try:
                        self.status_label.config(text="● Listening...", fg='#00ff88')
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        
                        self.status_label.config(text="● Processing...")
                        text = self.recognizer.recognize_google(audio)
                        
                        self.root.after(0, self.process_text, text)
                        
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        self.root.after(0, self.fade_in_status, 
                                      "● Could not understand", '#ff9800')
                    except sr.RequestError:
                        self.root.after(0, self.show_connection_error)
                        break
                        
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Microphone Error", 
                          f"Could not access microphone:\n{str(e)}")
            self.is_listening = False
            self.root.after(0, self.toggle_listening)
    
    def show_connection_error(self):
        """Show connection error with helpful message"""
        self.fade_in_status("● Network error", '#ff4757')
        messagebox.showerror(
            "Connection Error",
            "Could not connect to speech recognition service.\n\n"
            "Please check:\n"
            "• Your internet connection\n"
            "• Firewall settings\n"
            "• Try using 'Type Text' instead"
        )
        self.is_listening = False
        self.toggle_listening()
    
    def process_text(self, text):
        """Process text with smooth animations"""
        self.text_display.insert(tk.END, text + " ")
        self.text_display.see(tk.END)
        
        self.display_sign_language(text)
        
        self.fade_in_status(f"● Converted: {text}", '#00d4ff')
    
    def display_sign_language(self, text):
        """Display signs with fade-in animation"""
        words = text.upper().split()
        
        for word_index, word in enumerate(words):
            clean_word = ''.join(filter(str.isalnum, word))
            
            if not clean_word:
                continue
            
            word_image_path = os.path.join(self.sign_images_dir, f"{clean_word}.png")
            
            if not os.path.exists(word_image_path):
                word_image_path = os.path.join(self.sign_images_dir, f"{clean_word}.jpg")
            if not os.path.exists(word_image_path):
                word_image_path = os.path.join(self.sign_images_dir, f"{clean_word}.jpeg")
            
            if os.path.exists(word_image_path):
                self._display_image_animated(word_image_path, clean_word, True, word_index * 100)
            else:
                for char_index, char in enumerate(clean_word):
                    image_path = os.path.join(self.sign_images_dir, f"{char}.png")
                    if not os.path.exists(image_path):
                        image_path = os.path.join(self.sign_images_dir, f"{char}.jpg")
                    if not os.path.exists(image_path):
                        image_path = os.path.join(self.sign_images_dir, f"{char}.jpeg")
                    
                    delay = (word_index * len(clean_word) + char_index) * 100
                    
                    if os.path.exists(image_path):
                        self._display_image_animated(image_path, char, False, delay)
                    else:
                        self.root.after(delay, lambda c=char: self._show_missing_image(c))
            
            # Add space indicator
            delay = (word_index + 1) * 100 * (len(clean_word) + 1)
            self.root.after(delay, self._add_space_indicator)
        
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self.root.after(500, lambda: self.canvas.xview_moveto(1.0))
    
    def _display_image_animated(self, image_path, text, is_word, delay):
        """Display image with fade-in animation"""
        self.root.after(delay, lambda: self._display_image(image_path, text, is_word))
    
    def _display_image(self, image_path, text, is_word=False):
        """Display a sign image with modern card design"""
        try:
            img = Image.open(image_path)
            size = (220, 240) if is_word else (190, 190)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # Modern card design
            card = tk.Frame(self.image_frame, bg='#1a1f2e', bd=0, relief=tk.FLAT)
            card.pack(side=tk.LEFT, padx=10, pady=10)
            
            # Image container with rounded effect
            img_container = tk.Frame(card, bg='#2d3548', bd=0)
            img_container.pack(padx=8, pady=8)
            
            img_label = tk.Label(img_container, image=photo, bg='#2d3548', bd=0)
            img_label.image = photo
            img_label.pack(padx=5, pady=5)
            
            # Text label with accent color
            text_label = tk.Label(
                card,
                text=text,
                font=("Segoe UI", 11, "bold" if is_word else "normal"),
                bg='#1a1f2e',
                fg='#00d4ff' if is_word else '#ffffff',
                pady=5
            )
            text_label.pack()
            
            self.displayed_images.append(photo)
            
        except Exception as e:
            self._show_missing_image(text)
    
    def _show_missing_image(self, text):
        """Show missing image placeholder with modern design"""
        card = tk.Frame(self.image_frame, bg='#2d3548', bd=0)
        card.pack(side=tk.LEFT, padx=10, pady=10)
        
        content = tk.Frame(card, bg='#2d3548')
        content.pack(padx=25, pady=25)
        
        tk.Label(
            content,
            text="❓",
            font=("Segoe UI", 40),
            bg='#2d3548',
            fg='#ff9800'
        ).pack()
        
        tk.Label(
            content,
            text=text,
            font=("Segoe UI", 12, "bold"),
            bg='#2d3548',
            fg='#ffffff'
        ).pack(pady=(5, 0))
        
        tk.Label(
            content,
            text="Image Missing",
            font=("Segoe UI", 9),
            bg='#2d3548',
            fg='#8b95a5'
        ).pack()
    
    def _add_space_indicator(self):
        """Add space indicator with modern design"""
        space_card = tk.Frame(self.image_frame, bg='#1a1f2e', bd=0)
        space_card.pack(side=tk.LEFT, padx=5, pady=10)
        
        tk.Label(
            space_card,
            text="⎵",
            font=("Segoe UI", 28),
            bg='#1a1f2e',
            fg='#4a5568',
            width=2,
            height=5
        ).pack(padx=8, pady=8)
    
    def clear_display(self):
        """Clear display with fade-out effect"""
        self.text_display.delete(1.0, tk.END)
        
        for widget in self.image_frame.winfo_children():
            widget.destroy()
        
        self.displayed_images.clear()
        self.fade_in_status("● Display cleared", '#00d4ff')

def main():
    root = tk.Tk()
    app = SignLanguageConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()