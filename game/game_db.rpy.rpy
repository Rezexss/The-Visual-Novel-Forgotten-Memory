# game_db.rpy
# База данных для сохранения прогресса игрока

init python:
    import json
    import os
    from datetime import datetime
    
    class GameDatabase:
        def __init__(self):
            self.data = {
                "player_name": "Юри",
                "chapter": 1,
                "achievements": [],  # Список названий полученных достижений
                "achievements_data": [],  # Полные данные о достижениях
                "stats": {},
                "choices": [],
                "inventory": []
            }
            self.load_data()
        
        def get_all_data(self):
            """Возвращает все данные для экспорта"""
            # Пытаемся синхронизировать достижения
            try:
                self.sync_achievements()
            except:
                pass
            return self.data
        
        def get_data(self, key, default=None):
            """Получить значение по ключу"""
            return self.data.get(key, default)
        
        def set_data(self, key, value):
            """Установить значение по ключу"""
            self.data[key] = value
            self.save_data()
        
        def update_stat(self, key, value):
            """Обновить статистику"""
            if "stats" not in self.data:
                self.data["stats"] = {}
            self.data["stats"][key] = value
            self.save_data()
        
        def get_stat(self, key, default=None):
            """Получить значение статистики"""
            return self.data.get("stats", {}).get(key, default)
        
        def add_choice(self, choice_text, category="general"):
            """Добавить выбор в историю"""
            if "choices" not in self.data:
                self.data["choices"] = []
            
            self.data["choices"].append({
                "choice": choice_text,
                "category": category,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            self.save_data()
        
        def add_achievement(self, achievement_name):
            """Добавить достижение"""
            if "achievements" not in self.data:
                self.data["achievements"] = []
            
            if achievement_name not in self.data["achievements"]:
                self.data["achievements"].append(achievement_name)
                self.sync_achievements()
                self.save_data()
        
        def sync_achievements(self):
            """Синхронизирует достижения из глобального списка с БД"""
            # Проверяем, существует ли класс Achievement
            if 'Achievement' not in globals():
                return
                
            achievements_data = []
            for a in Achievement.all_achievements():
                # Получаем имя и описание с учетом скрытости
                if a.has():
                    display_name = a.name
                    display_description = a.description
                else:
                    display_name = "???" if a.hide_name else a.name
                    display_description = "???" if a.hide_description else a.description
                
                achievements_data.append({
                    'id': a.id,
                    'name': display_name,
                    'description': display_description,
                    'unlocked': a.has(),
                    'progress': a.stat_progress,
                    'max_progress': a.stat_max,
                    'hidden_name': a.hide_name,
                    'hidden_description': a.hide_description,
                    'original_name': a.name,
                    'original_description': a.description
                })
                
                # Добавляем в старый список для совместимости
                if a.has() and a.name not in self.data["achievements"]:
                    self.data["achievements"].append(a.name)
            
            self.data['achievements_data'] = achievements_data
            self.save_data()
        
        def load_achievements_state(self):
            """Загружает состояние достижений из БД в глобальные объекты"""
            if 'Achievement' not in globals():
                return
                
            if 'achievements_data' in self.data:
                saved_achievements = self.data['achievements_data']
                for saved_ach in saved_achievements:
                    for a in Achievement.all_achievements():
                        if a.id == saved_ach['id']:
                            if saved_ach.get('unlocked', False):
                                a._unlocked = True
                            if 'progress' in saved_ach and saved_ach['progress']:
                                a._progress = saved_ach['progress']
                            break
        
        def save_data(self):
            """Сохранить данные в файл"""
            try:
                if not os.path.exists("game/saves"):
                    os.makedirs("game/saves")
                
                filename = "game/saves/game_data.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Ошибка сохранения: {e}")
        
        def load_data(self):
            """Загрузить данные из файла"""
            try:
                filename = "game/saves/game_data.json"
                if os.path.exists(filename):
                    with open(filename, "r", encoding="utf-8") as f:
                        self.data = json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки: {e}")
        
        def reset_data(self):
            """Сбросить данные к значениям по умолчанию"""
            self.data = {
                "player_name": "Юри",
                "chapter": 1,
                "achievements": [],
                "achievements_data": [],
                "stats": {},
                "choices": [],
                "inventory": []
            }
            self.save_data()
            
            if 'Achievement' in globals():
                Achievement.reset()