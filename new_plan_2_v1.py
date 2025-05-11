import tkinter as tk
from tkinter import messagebox
import random

class ContainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Размещение груза в контейнере")
        
        # Размеры контейнера в мм (6060 x 2440)
        self.container_width_mm = 6060
        self.container_height_mm = 2440
        
        # Масштаб для отображения (1 мм = 0.1 пикселя)
        self.scale = 0.1
        
        # Размеры контейнера на холсте
        self.container_width = int(self.container_width_mm * self.scale)
        self.container_height = int(self.container_height_mm * self.scale)
        
        # Создаем область для ввода размеров груза
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(self.input_frame, text="Ширина груза (мм):").pack()
        self.width_entry = tk.Entry(self.input_frame)
        self.width_entry.pack()
        
        tk.Label(self.input_frame, text="Длина груза (мм):").pack()
        self.height_entry = tk.Entry(self.input_frame)
        self.height_entry.pack()
        
        self.add_button = tk.Button(self.input_frame, text="Добавить груз", command=self.add_cargo)
        self.add_button.pack(pady=10)
        
        # Создаем холст для отображения контейнера
        self.canvas = tk.Canvas(root, width=self.container_width + 20, 
                               height=self.container_height + 20, bg="lightgray")
        self.canvas.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Рисуем контейнер
        self.container = self.canvas.create_rectangle(
            10, 10, self.container_width + 10, self.container_height + 10,
            outline="black", width=2, fill="white"
        )
        
        # Переменные для перетаскивания
        self.selected_cargo = None
        self.offset_x = 0
        self.offset_y = 0
        
        # Привязываем события мыши
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # Список для хранения всех грузов (id, цвет, размеры)
        self.cargos = []
        
        # Доступные цвета для грузов
        self.colors = ["blue", "green", "red", "orange", "purple", "cyan", "magenta", "yellow"]
    
    def get_random_color(self):
        return random.choice(self.colors)
    
    def add_cargo(self):
        try:
            width_mm = int(self.width_entry.get())
            height_mm = int(self.height_entry.get())
            
            if width_mm <= 0 or height_mm <= 0:
                messagebox.showerror("Ошибка", "Размеры должны быть положительными числами")
                return
                
            # Преобразуем мм в пиксели
            width = int(width_mm * self.scale)
            height = int(height_mm * self.scale)
            
            # Проверяем, помещается ли груз в контейнер
            if width > self.container_width or height > self.container_height:
                messagebox.showerror("Ошибка", "Груз не помещается в контейнер")
                return
                
            # Создаем груз в центре контейнера
            x1 = 10 + (self.container_width - width) // 2
            y1 = 10 + (self.container_height - height) // 2
            x2 = x1 + width
            y2 = y1 + height
            
            color = self.get_random_color()
            cargo = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="cargo")
            
            # Сохраняем информацию о грузе (id, цвет, размеры в мм и пикселях)
            self.cargos.append({
                'id': cargo,
                'color': color,
                'width_mm': width_mm,
                'height_mm': height_mm,
                'width': width,
                'height': height
            })
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")
    
    def on_click(self, event):
        # Находим все грузы в точке клика (сверху вниз)
        items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        
        if items:
            # Берем верхний груз (последний в списке)
            clicked_id = items[-1]
            # Проверяем, что кликнули именно по грузу (не по контейнеру)
            for cargo in self.cargos:
                if cargo['id'] == clicked_id:
                    self.selected_cargo = cargo
                    # Запоминаем смещение курсора относительно верхнего левого угла груза
                    cargo_coords = self.canvas.coords(self.selected_cargo['id'])
                    self.offset_x = event.x - cargo_coords[0]
                    self.offset_y = event.y - cargo_coords[1]
                    break
    
    def on_drag(self, event):
        if self.selected_cargo:
            # Предварительные координаты
            x1 = event.x - self.offset_x
            y1 = event.y - self.offset_y
            x2 = x1 + self.selected_cargo['width']
            y2 = y1 + self.selected_cargo['height']
            
            # Проверка границ контейнера
            if x1 < 10:  # Левая граница
                x1 = 10
                x2 = x1 + self.selected_cargo['width']
            if y1 < 10:  # Верхняя граница
                y1 = 10
                y2 = y1 + self.selected_cargo['height']
            if x2 > 10 + self.container_width:  # Правая граница
                x2 = 10 + self.container_width
                x1 = x2 - self.selected_cargo['width']
            if y2 > 10 + self.container_height:  # Нижняя граница
                y2 = 10 + self.container_height
                y1 = y2 - self.selected_cargo['height']
            
            # Проверка пересечения с другими грузами
            for cargo in self.cargos:
                if cargo['id'] != self.selected_cargo['id']:
                    coords = self.canvas.coords(cargo['id'])
                    # Если есть пересечение, корректируем позицию
                    if not (x2 < coords[0] or x1 > coords[2] or y2 < coords[1] or y1 > coords[3]):
                        # Определяем направление наименьшего перекрытия
                        overlap_left = x2 - coords[0]
                        overlap_right = coords[2] - x1
                        overlap_top = y2 - coords[1]
                        overlap_bottom = coords[3] - y1
                        
                        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                        
                        if min_overlap == overlap_left:
                            x1 = coords[0] - self.selected_cargo['width']
                            x2 = coords[0]
                        elif min_overlap == overlap_right:
                            x1 = coords[2]
                            x2 = coords[2] + self.selected_cargo['width']
                        elif min_overlap == overlap_top:
                            y1 = coords[1] - self.selected_cargo['height']
                            y2 = coords[1]
                        elif min_overlap == overlap_bottom:
                            y1 = coords[3]
                            y2 = coords[3] + self.selected_cargo['height']
            
            # Обновляем позицию груза
            self.canvas.coords(self.selected_cargo['id'], x1, y1, x2, y2)
    
    def on_release(self, event):
        self.selected_cargo = None

if __name__ == "__main__":
    root = tk.Tk()
    app = ContainerApp(root)
    root.mainloop()