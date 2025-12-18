import tkinter as tk  # Основная библиотека для графического интерфейса
from tkinter import messagebox  # Диалоговые окна (сообщения, ошибки)
import json  # Работа с JSON-файлами (вопросы, сохранения)
import os  # Работа с файловой системой
import random  # Генерация случайных чисел (для перемешивания ответов)

# =================== КОНСТАНТЫ И НАСТРОЙКИ ===================
QUESTIONS_FILE = 'questions_part2.json'
SAVE_FILE = 'game_save.json'

# =================== МЕТОДЫ РАБОТЫ С ДАННЫМИ (4 метода) ===================

def load_questions():
    """Загружает вопросы из JSON-файла
    Работает так:
    1. Проверяет, существует ли файл questions.json
    2. Если файл есть - загружает оттуда все вопросы
    3. Если файла нет - создаёт его с примерами вопросов
    4. Возвращает список вопросов для игры"""
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Создаём примерный вопрос если файла нет
        sample_questions = [
            {
                "question": "Что делает строка 'from comet_ml import Experiment, start'?",
                "correct_answer": "Импортирует основные классы для трекинга экспериментов ML",
                "wrong_answers": [
                    "Запускает веб-сервер для машинного обучения",
                    "Создаёт новую модель нейронной сети",
                    "Экспортирует данные в облачное хранилище"
                ]
            },
            {
                "question": "Что делает 'import pandas as pd'?",
                "correct_answer": "Импортирует библиотеку для работы с табличными данными",
                "wrong_answers": [
                    "Загружает изображения с диска",
                    "Создаёт графики в реальном времени",
                    "Шифрует данные для защиты"
                ]
            }
        ]
        with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(sample_questions, f, ensure_ascii=False, indent=2)
        return sample_questions

def load_save():
    """Загружает сохранённый прогресс игры
    Работает так:
    1. Проверяет наличие файла сохранения game_save.json
    2. Если файл есть - загружает оттуда счёт, текущий вопрос и историю ответов
    3. Если файла нет - возвращает начальные значения (ноль очков, первый вопрос)"""
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"score": 0, "current_question": 0, "answered": []}

def save_game(score, current_q, answered):
    """Сохраняет прогресс игры в JSON-файл
    Работает так:
    1. Принимает текущий счёт, номер вопросов и историю ответов
    2. Формирует словарь с этими данными
    3. Сохраняет в файл game_save.json для восстановления позже"""
    data = {
        "score": score,
        "current_question": current_q,
        "answered": answered
    }
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def scrape_and_add_questions():
    """Автоматически собирает вопросы с Stack Overflow и добавляет их в базу
    Работает так:
    1. Пытается импортировать библиотеку requests
    2. Делает запрос к API Stack Overflow за популярными вопросами по Python
    3. Преобразует заголовки вопросов в формат игры
    4. Добавляет новые вопросы в существующий файл, избегая дубликатов"""
    try:
        import requests
        
        print("🔄 Сбор новых вопросов с Stack Overflow...")
        # API запрос к Stack Overflow
        url = "https://api.stackexchange.com/2.3/questions?order=desc&sort=votes&tagged=python&site=stackoverflow&pagesize=5"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            new_questions = []
            
            for item in data['items']:
                # Создаём вопрос на основе заголовка
                title = item['title'].replace('"', "'")  # Заменяем кавычки
                new_questions.append({
                    "question": f"Про что этот вопрос: '{title[:80]}...'?",
                    "correct_answer": "Это вопрос про программирование на Python",
                    "wrong_answers": [
                        "Это вопрос про математику и статистику",
                        "Это вопрос про веб-разработку и дизайн",
                        "Это вопрос про базы данных и SQL"
                    ]
                })
            
            # Загружаем существующие вопросы
            existing_questions = load_questions()
            
            # Добавляем только новые (проверяем дубли)
            for new_q in new_questions:
                if new_q not in existing_questions:
                    existing_questions.append(new_q)
            
            # Сохраняем обновлённый список
            with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(existing_questions, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Добавлено {len(new_questions)} новых вопросов!")
            print(f"📊 Всего вопросов теперь: {len(existing_questions)}")
            return True
            
        else:
            print("⚠️ Не удалось получить вопросы с Stack Overflow")
            return False
            
    except ImportError:
        print("⚠️ Для сбора вопросов установите библиотеку: pip install requests")
        return False
    except Exception as e:
        print(f"⚠️ Ошибка при сборе вопросов: {e}")
        return False


# =================== КЛАСС ГЛАВНОГО МЕНЮ (6 методов) ===================

class MainMenu:
    def __init__(self, root):
        """Инициализация главного меню - конструктор класса
        Работает так:
        1. Принимает корневое окно Tkinter (root)
        2. Настраивает размер, заголовок и цвет фона окна
        3. Создаёт все элементы интерфейса (create_widgets)
        4. Проверяет наличие сохранённой игры (check_save)"""
        self.root = root
        self.root.title("Игра-Отгадайка")
        self.root.geometry("400x350")  # Увеличили высоту для новой кнопки
        self.root.configure(bg='#2c3e50')
        
        self.create_widgets()
        self.check_save()
    
    def create_widgets(self):
        """Создаёт все виджеты (элементы) меню
        Работает так:
        1. Создаёт заголовок игры с эмодзи
        2. Создаёт 4 кнопки: Играть, Продолжить, Собрать вопросы, Выход
        3. Каждой кнопке назначает свой цвет и команду-обработчик"""
        title = tk.Label(
            self.root, 
            text="🎮 ИГРА-ОТГАДАЙКА", 
            font=("Arial", 24, "bold"),
            fg="white",
            bg='#2c3e50'
        )
        title.pack(pady=20)
        
        btn_style = {
            "font": ("Arial", 14),
            "width": 20,
            "height": 2,
            "bd": 0,
            "cursor": "hand2"
        }
        
        # Кнопка "Играть" - зелёная
        self.play_btn = tk.Button(
            self.root, 
            text="🎯 Играть", 
            bg="#27ae60", 
            fg="white",
            command=self.start_new_game,
            **btn_style
        )
        self.play_btn.pack(pady=8)
        
        # Кнопка "Продолжить" - синяя
        self.continue_btn = tk.Button(
            self.root, 
            text="↻ Продолжить", 
            bg="#3498db", 
            fg="white",
            command=self.continue_game,
            **btn_style
        )
        self.continue_btn.pack(pady=8)
        
        # ★★★ НОВАЯ КНОПКА ДЛЯ СБОРА ВОПРОСОВ ★★★ - оранжевая
        self.scrape_btn = tk.Button(
            self.root, 
            text="🌐 Собрать вопросы", 
            bg="#f39c12",
            fg="white",
            command=self.scrape_questions,
            **btn_style
        )
        self.scrape_btn.pack(pady=8)
        
        # Кнопка "Выход" - красная
        self.exit_btn = tk.Button(
            self.root, 
            text="🚪 Выход", 
            bg="#e74c3c", 
            fg="white",
            command=self.root.quit,
            **btn_style
        )
        self.exit_btn.pack(pady=8)
    
    def check_save(self):
        """Проверяет наличие сохранения и блокирует кнопку "Продолжить"
        Работает так:
        1. Загружает данные сохранения через load_save()
        2. Если сохранение пустое (current_question == 0) - блокирует кнопку "Продолжить"
        3. Это нужно, чтобы нельзя было продолжить игру, которой ещё не было"""
        save_data = load_save()
        if save_data["current_question"] == 0:
            self.continue_btn.config(state="disabled")
    
    def start_new_game(self):
        """Начинает новую игру с нуля
        Работает так:
        1. Закрывает текущее окно меню (self.root.destroy())
        2. Создаёт новое окно Tkinter для игры
        3. Запускает игровое окно с параметром new_game=True"""
        self.root.destroy()
        game_root = tk.Tk()
        GameWindow(game_root, new_game=True)
        game_root.mainloop()
    
    def continue_game(self):
        """Продолжает сохранённую игру с того же места
        Работает так:
        1. Закрывает текущее окно меню
        2. Создаёт новое окно для игры
        3. Запускает игровое окно с параметром new_game=False (загрузит сохранение)"""
        self.root.destroy()
        game_root = tk.Tk()
        GameWindow(game_root, new_game=False)
        game_root.mainloop()
    
    def scrape_questions(self):
        """Обработчик кнопки для сбора вопросов из интернета
        Работает так:
        1. Временно отключает кнопку и меняет её текст
        2. Запускает функцию scrape_and_add_questions() в отдельном потоке
        3. После завершения обновляет интерфейс и показывает результат"""
        # Временно отключаем кнопку
        self.scrape_btn.config(state="disabled", text="🔄 Сбор...")
        
        # Запускаем сбор в отдельном потоке
        import threading
        
        def run_scrape():
            success = scrape_and_add_questions()
            
            # Возвращаемся в главный поток для обновления UI
            self.root.after(0, lambda: self.update_after_scrape(success))
        
        thread = threading.Thread(target=run_scrape)
        thread.daemon = True
        thread.start()
    
    def update_after_scrape(self, success):
        """Обновляет UI после сбора вопросов
        Работает так:
        1. Восстанавливает кнопку в нормальное состояние
        2. Показывает сообщение об успехе или ошибке
        3. Если успешно - вопросы уже добавлены в файл и будут доступны в игре"""
        if success:
            self.scrape_btn.config(state="normal", text="🌐 Собрать вопросы")
            messagebox.showinfo("Успех", "✅ Новые вопросы добавлены в игру!\nОни появятся при следующем запуске игры.")
        else:
            self.scrape_btn.config(state="normal", text="🌐 Собрать вопросы")
            messagebox.showwarning("Ошибка", 
                "❌ Не удалось собрать вопросы.\nУстановите библиотеку requests:\npip install requests")

# =================== КЛАСС ИГРОВОГО ОКНА (8 методов) ===================

class GameWindow:
    def __init__(self, root, new_game=True):
        """Инициализация игрового окна - конструктор класса
        Работает так:
        1. Принимает корневое окно и флаг new_game
        2. Настраивает размер и внешний вид окна
        3. Загружает вопросы и состояние игры
        4. Создаёт весь интерфейс и показывает первый вопрос"""
        self.root = root
        self.root.title("Игра-Отгадайка - Игра")
        self.root.geometry("600x500")
        self.root.configure(bg='#34495e')
        
        self.questions = load_questions()
        self.load_game_state(new_game)
        self.create_interface()
        self.load_question()
    
    def load_game_state(self, new_game):
        """Загружает состояние игры (новая/продолжение)
        Работает так:
        1. Если new_game=True - устанавливает начальные значения
        2. Если new_game=False - загружает данные из файла сохранения"""
        if new_game:
            self.score = 0
            self.current_q_index = 0
            self.answered = []
        else:
            save_data = load_save()
            self.score = save_data["score"]
            self.current_q_index = save_data["current_question"]
            self.answered = save_data["answered"]
    
    def create_interface(self):
        """Создаёт интерфейс игрового окна
        Работает так:
        1. Создаёт верхнюю панель со счётом
        2. Создаёт область для вопроса
        3. Создаёт 4 кнопки для вариантов ответа"""
        self.create_score_panel()
        self.create_question_area()
        self.create_answer_buttons()
    
    def create_score_panel(self):
        """Создаёт верхнюю панель со счётом и кнопкой "Меню"
        Работает так:
        1. Создаёт фрейм (контейнер) для панели
        2. Добавляет метку с текущим счётом слева
        3. Добавляет кнопку возврата в меню справа"""
        score_frame = tk.Frame(self.root, bg='#2c3e50', height=50)
        score_frame.pack(fill="x", pady=(0, 20))
        
        self.score_label = tk.Label(
            score_frame,
            text=f"Счёт: {self.score}",
            font=("Arial", 16, "bold"),
            fg="white",
            bg='#2c3e50'
        )
        self.score_label.pack(side="left", padx=20)
        
        menu_btn = tk.Button(
            score_frame,
            text="← Меню",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            command=self.return_to_menu
        )
        menu_btn.pack(side="right", padx=20)
    
    def create_question_area(self):
        """Создаёт область для отображения вопроса
        Работает так:
        1. Создаёт метку (Label) для текста вопроса
        2. Настраивает шрифт, перенос строк и центрирование"""
        self.question_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 14),
            wraplength=550,
            justify="center",
            bg='#34495e',
            fg="white"
        )
        self.question_label.pack(pady=20)
    
    def create_answer_buttons(self):
        """Создаёт 4 кнопки для ответов
        Работает так:
        1. Создаёт список для хранения кнопок
        2. В цикле создаёт 4 кнопки с одинаковым стилем
        3. Каждой кнопке назначает обработчик check_answer с её индексом"""
        self.answer_buttons = []
        for i in range(4):
            btn = tk.Button(
                self.root,
                text="",
                font=("Arial", 12),
                width=50,
                height=2,
                bg='#3498db',
                fg="white",
                cursor="hand2",
                command=lambda idx=i: self.check_answer(idx)
            )
            btn.pack(pady=5)
            self.answer_buttons.append(btn)
    
    def load_question(self):
        """Загружает текущий вопрос и обновляет интерфейс
        Работает так:
        1. Проверяет, не закончились ли вопросы
        2. Берёт текущий вопрос из списка по индексу
        3. Обновляет текст вопроса и кнопки ответов"""
        if self.current_q_index >= len(self.questions):
            self.show_game_over()
            return
        
        self.current_question = self.questions[self.current_q_index]
        
        self.question_label.config(
            text=f"Вопрос {self.current_q_index + 1}/{len(self.questions)}:\n{self.current_question['question']}"
        )
        
        self.update_answer_buttons()
    
    def update_answer_buttons(self):
        """Обновляет текст и состояние кнопок ответов
        Работает так:
        1. Собирает все варианты ответов (правильный + 3 неправильных)
        2. Перемешивает варианты в случайном порядке
        3. Присваивает каждый вариант своей кнопке"""
        all_answers = [self.current_question['correct_answer']] + self.current_question['wrong_answers']
        random.shuffle(all_answers)
        self.current_answers = all_answers
        
        for i in range(4):
            self.answer_buttons[i].config(
                text=all_answers[i],
                bg='#3498db',
                state="normal"
            )
    
    def check_answer(self, answer_index):
        """Проверяет выбранный ответ и обрабатывает результат
        Работает так:
        1. Получает выбранный и правильный ответ
        2. Подсвечивает правильный ответ зелёным
        3. Проверяет совпадение и начисляет очки/показывает ошибку
        4. Переходит к следующему вопросу через 1.5 секунды"""
        selected = self.current_answers[answer_index]
        correct = self.current_question['correct_answer']
        
        self.highlight_correct_answer(correct)
        
        if selected == correct:
            self.handle_correct_answer()
        else:
            self.handle_wrong_answer(answer_index, correct)
        
        self.next_question()
    
    def highlight_correct_answer(self, correct_answer):
        """Подсвечивает правильный ответ зелёным
        Работает так:
        1. Проходит по всем вариантам ответов
        2. Находит кнопку с правильным ответом
        3. Меняет её цвет на зелёный"""
        for i, answer in enumerate(self.current_answers):
            if answer == correct_answer:
                self.answer_buttons[i].config(bg="#2ecc71")
    
    def handle_correct_answer(self):
        """Обрабатывает правильный ответ
        Работает так:
        1. Увеличивает счёт на 10 очков
        2. Обновляет отображение счёта
        3. Показывает сообщение об успехе"""
        self.score += 10
        self.score_label.config(text=f"Счёт: {self.score}")
        messagebox.showinfo("Правильно!", f"✅ Верно!\n+10 очков")
    
    def handle_wrong_answer(self, answer_index, correct):
        """Обрабатывает неправильный ответ
        Работает так:
        1. Подсвечивает выбранную кнопку красным
        2. Показывает сообщение с правильным ответом"""
        self.answer_buttons[answer_index].config(bg="#e74c3c")
        messagebox.showerror("Неверно", f"❌ Неправильно!\nПравильный ответ: {correct}")
    
    def next_question(self):
        """Переходит к следующему вопросу
        Работает так:
        1. Сохраняет историю ответа (правильно/неправильно)
        2. Увеличивает индекс текущего вопроса
        3. Сохраняет прогресс в файл
        4. Через 1.5 секунды загружает следующий вопрос"""
        self.answered.append({
            "question": self.current_question['question'],
            "correct": True if self.current_answers[0] == self.current_question['correct_answer'] else False
        })
        self.current_q_index += 1
        
        save_game(self.score, self.current_q_index, self.answered)
        self.root.after(1500, self.load_question)
    
    def show_game_over(self):
        """Показывает экран завершения игры
        Работает так:
        1. Убирает кнопки ответов
        2. Показывает итоговый счёт
        3. Добавляет кнопку возврата в меню"""
        for btn in self.answer_buttons:
            btn.pack_forget()
        
        self.question_label.config(
            text=f"🎉 Игра завершена!\n\nВаш счёт: {self.score}/{len(self.questions)*10}",
            font=("Arial", 18, "bold")
        )
        
        tk.Button(
            self.root,
            text="В главное меню",
            font=("Arial", 14),
            bg="#9b59b6",
            fg="white",
            command=self.return_to_menu
        ).pack(pady=30)
    
    def return_to_menu(self):
        """Возвращает в главное меню
        Работает так:
        1. Закрывает текущее игровое окно
        2. Создаёт новое окно главного меню
        3. Запускает меню"""
        self.root.destroy()
        root = tk.Tk()
        MainMenu(root)
        root.mainloop()

# =================== ЗАПУСК ПРИЛОЖЕНИЯ ===================

if __name__ == "__main__":
    """Точка входа в приложение
    Работает так:
    1. Создаёт главное окно Tkinter
    2. Создаёт экземпляр главного меню
    3. Запускает главный цикл обработки событий"""
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()
