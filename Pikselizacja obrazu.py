import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar, Style
from PIL import Image, ImageTk
from threading import Thread

class ImagePixelator:
    def __init__(self):
        self.image_path = ""
        self.processing = False
        self.window = tk.Tk()
        self.window.title('Pikselizacja obrazu')
        self.window.geometry('500x650')
        self.window.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        choose_image_button = tk.Button(self.window, text='Wybierz obraz', command=self.choose_image)
        choose_image_button.pack(pady=10)

        self.image_path_label = tk.Label(self.window, text='Nie wybrano obrazu')
        self.image_path_label.pack()

        self.original_label = tk.Label(self.window)
        self.original_label.pack(pady=10)

        pixel_size_label = tk.Label(self.window, text='Rozmiar pikseli:')
        pixel_size_label.pack()
        self.pixel_size_entry = tk.Entry(self.window)
        self.pixel_size_entry.pack(pady=5)

        self.process_button = tk.Button(self.window, text='Przetwórz obraz', command=self.process_image)
        self.process_button.pack(pady=10)

        cancel_button = tk.Button(self.window, text='Anuluj', command=self.cancel_processing)
        cancel_button.pack(pady=10)

        self.status_label = tk.Label(self.window, text='')
        self.status_label.pack(pady=10)

        self.progress_frame = tk.Frame(self.window)
        self.progress_frame.pack()
        self.progress_label = tk.Label(self.progress_frame, text='Przetwarzanie obrazu:')
        self.progress_label.pack(side='left')
        self.progress_bar = Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill='x', padx=5)

        self.pixelated_label = tk.Label(self.window)
        self.pixelated_label.pack(pady=10)

        copyright_label = tk.Label(self.window, text="© 2023 Szymon Wasik.")
        copyright_label.pack(side='bottom', pady=10)

    def choose_image(self):
        self.image_path = filedialog.askopenfilename(
            title='Wybierz obraz', filetypes=[('Image files', ('*.png', '*.jpg', '*.jpeg'))]
        )
        if self.image_path:
            self.image_path_label.config(text='Wybrano obraz')
            self.preview_original_image()
        else:
            self.image_path_label.config(text='Nie wybrano obrazu')
            self.clear_original_image()

    def process_image(self):
        pixel_size_str = self.pixel_size_entry.get()
        if pixel_size_str.isdigit():
            pixel_size = int(pixel_size_str)
            self.process_button.config(state='disabled')
            self.pixel_size_entry.config(state='disabled')
            self.status_label.config(text='Przetwarzanie obrazu...')
            self.progress_bar.start()
            self.processing = True
            self.thread = Thread(target=self.pixelate, args=(pixel_size,))
            self.thread.start()
            self.window.after(100, self.check_thread)
            self.window.after(100, self.update_window)
        else:
            self.status_label.config(text='Nieprawidłowy rozmiar piksela.')

    def pixelate(self, pixel_size):
        if self.image_path:
            try:
                image = Image.open(self.image_path)
                width, height = image.size
                new_width = (width // pixel_size) * pixel_size
                new_height = (height // pixel_size) * pixel_size
                image = image.resize((new_width, new_height))
                pixelated_image = Image.new('RGB', (new_width, new_height))
                total_pixels = new_width * new_height
                processed_pixels = 0
                for y in range(0, new_height, pixel_size):
                    if not self.processing:
                        break
                    for x in range(0, new_width, pixel_size):
                        if not self.processing:
                            break
                        pixel = image.getpixel((x, y))
                        for i in range(pixel_size):
                            for j in range(pixel_size):
                                pixelated_image.putpixel((x + i, y + j), pixel)
                        processed_pixels += 1
                        self.update_progress(processed_pixels, total_pixels)
                if self.processing:
                    output_path = filedialog.asksaveasfilename(
                        defaultextension='.png', filetypes=[('PNG files', '*.png')],
                        initialfile='pixelated_image.png', title='Save Pixelated Image'
                    )
                    if output_path:
                        pixelated_image.save(output_path)
                        self.status_label.config(text='Obraz został spikselizowany i zapisany.')
                        self.display_pixelated_image(output_path)
                    else:
                        self.status_label.config(text='Anulowano zapisywanie.')
                else:
                    self.status_label.config(text='Przetwarzanie anulowane.')
                    self.clear_pixelated_image()
            except Exception as e:
                self.status_label.config(text='Błąd przetwarzania obrazu: ' + str(e))
        else:
            self.status_label.config(text='Nie wybrano pliku.')

    def update_progress(self, value, total):
        progress_percentage = int(value / total * 100)
        self.progress_bar['value'] = progress_percentage
        self.progress_label.config(text=f'Przetwarzanie obrazu: {progress_percentage}%')

    def check_thread(self):
        if self.thread.is_alive():
            self.window.after(100, self.check_thread)
        else:
            self.process_button.config(state='normal')
            self.pixel_size_entry.config(state='normal')
            self.progress_bar.stop()

    def preview_original_image(self):
        if self.image_path:
            try:
                original_image = Image.open(self.image_path)
                original_image.thumbnail((400, 400))
                original_photo = ImageTk.PhotoImage(original_image)
                self.original_label.config(image=original_photo)
                self.original_label.image = original_photo
            except Exception as e:
                self.status_label.config(text='Błąd wczytywania oryginalnego obrazu: ' + str(e))
                self.clear_original_image()
        else:
            self.clear_original_image()

    def clear_original_image(self):
        self.original_label.config(image='')
        self.original_label.image = None

    def display_pixelated_image(self, image_path):
        try:
            pixelated_image = Image.open(image_path)
            pixelated_image.thumbnail((400, 400))
            pixelated_photo = ImageTk.PhotoImage(pixelated_image)
            self.pixelated_label.config(image=pixelated_photo)
            self.pixelated_label.image = pixelated_photo
        except Exception as e:
            self.status_label.config(text='Błąd wczytywania spikselizowanego obrazu: ' + str(e))
            self.clear_pixelated_image()

    def clear_pixelated_image(self):
        self.pixelated_label.config(image='')
        self.pixelated_label.image = None

    def cancel_processing(self):
        self.processing = False

    def update_window(self):
        if self.processing:
            self.window.after(100, self.update_window)
        else:
            self.progress_label.config(text='Przetwarzanie obrazu:')
            self.progress_bar['value'] = 0

    def run(self):
        self.window.mainloop()

if __name__ == '__main__':
    pixelator = ImagePixelator()
    pixelator.run()