# database.rpy
# Файл для хранения и отслеживания данных игрока

init python:
    import json
    import os
    from datetime import datetime
    
    class GameDatabase:
        def __init__(self):
            self.player_name = ""
            self.achievements = []
            self.choices = []
            self.current_chapter = 1
            self.stats = {
                "key_taken": False,
                "first_meeting_response": "",
                "coffee_preference": "",
                "mysterious_message_read": False
            }
            self.load_data()
        
        def save_data(self):
            """Сохраняет данные игрока в JSON файл"""
            data = {
                "player_name": self.player_name,
                "achievements": self.achievements,
                "choices": self.choices,
                "current_chapter": self.current_chapter,
                "stats": self.stats,
                "last_save": str(datetime.now())
            }
            
            try:
                # Создаем папку save если её нет
                if not os.path.exists("game/saves"):
                    os.makedirs("game/saves")
                
                with open("game/saves/player_data.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                print(f"Error saving data: {e}")
                return False
        
        def load_data(self):
            """Загружает данные игрока из JSON файла"""
            try:
                if os.path.exists("game/saves/player_data.json"):
                    with open("game/saves/player_data.json", "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.player_name = data.get("player_name", "")
                        self.achievements = data.get("achievements", [])
                        self.choices = data.get("choices", [])
                        self.current_chapter = data.get("current_chapter", 1)
                        self.stats = data.get("stats", {
                            "key_taken": False,
                            "first_meeting_response": "",
                            "coffee_preference": "",
                            "mysterious_message_read": False
                        })
            except:
                pass
        
        def add_achievement(self, achievement_id):
            """Добавляет достижение, если его ещё нет"""
            if achievement_id not in self.achievements:
                self.achievements.append(achievement_id)
                self.save_data()
                return True
            return False
        
        def add_choice(self, choice_text, scene_label):
            """Записывает выбор игрока"""
            choice_data = {
                "scene": scene_label,
                "choice": choice_text,
                "timestamp": str(datetime.now())
            }
            self.choices.append(choice_data)
            self.save_data()
        
        def update_stat(self, stat_name, value):
            """Обновляет конкретную статистику"""
            if stat_name in self.stats:
                self.stats[stat_name] = value
                self.save_data()
        
        def get_stat(self, stat_name):
            """Получает значение статистики"""
            return self.stats.get(stat_name, None)
        
        def get_all_data(self):
            """Возвращает все данные для отладки"""
            return {
                "player_name": self.player_name,
                "achievements": self.achievements,
                "choices": self.choices,
                "chapter": self.current_chapter,
                "stats": self.stats
            }
    
    # Создаем глобальный экземпляр базы данных
    game_db = GameDatabase()