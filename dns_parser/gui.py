import tkinter as tk
from tkinter import messagebox
import threading
import main
import sys

class ParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DNS Парсер")
        self.root.geometry("400x300")

        self.mode = tk.StringVar(value="update")

        tk.Label(root, text="Выберите режим работы:").pack(pady=10)

        tk.Radiobutton(root, text="Запуск с обновлением", variable=self.mode, value="update").pack()
        tk.Radiobutton(root, text="Перезаписать всё", variable=self.mode, value="overwrite").pack()

        self.start_btn = tk.Button(root, text="Запустить", command=self.start_parser)
        self.start_btn.pack(pady=20)

        self.stop_btn = tk.Button(root, text="Остановить", command=self.stop_parser, state=tk.DISABLED)
        self.stop_btn.pack()

        self.status = tk.Label(root, text="Ожидание...", fg="blue")
        self.status.pack()

        self.running = False

    def start_parser(self):
        if self.running:
            return
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status.config(text="Парсинг запущен...", fg="green")
        threading.Thread(target=self.run_parser, daemon=True).start()

    def stop_parser(self):
        self.running = False
        self.status.config(text="Остановлен", fg="red")
        self.root.after(1000, self.root.destroy)  # закрываем окно через секунду

    def running_flag(self):
        return self.running

    def run_parser(self):
        try:
            main.run(self.mode.get(), self.running_flag)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        finally:
            self.running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ParserGUI(root)
    root.mainloop()
    sys.exit()