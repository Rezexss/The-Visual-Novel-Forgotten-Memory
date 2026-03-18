# developer_tools.rpy
# Инструменты для разработчика по отслеживанию данных игроков

init python:
    import json
    import os
    from datetime import datetime
    
    class DeveloperTools:
        def __init__(self):
            self.debug_mode = False
            self.logs = []
            self.load_logs()
            
        def toggle_debug(self):
            self.debug_mode = not self.debug_mode
            if self.debug_mode:
                renpy.notify("🔧 Режим разработчика ВКЛЮЧЕН")
            else:
                renpy.notify("🔧 Режим разработчика ВЫКЛЮЧЕН")
            return self.debug_mode
        
        def load_logs(self):
            try:
                if os.path.exists("game/dev_logs/session_today.json"):
                    with open("game/dev_logs/session_today.json", "r", encoding="utf-8") as f:
                        self.logs = json.load(f)
            except:
                pass
        
        def log_player_action(self, action, details=""):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = {
                "timestamp": timestamp,
                "action": action,
                "details": details,
                "player_name": game_db.player_name if 'game_db' in globals() and hasattr(game_db, 'player_name') else "Unknown"
            }
            self.logs.append(log_entry)
            
            if self.debug_mode:
                renpy.notify(f"📝 {action}")
            
            self.save_logs()
        
        def save_logs(self):
            try:
                if not os.path.exists("game/dev_logs"):
                    os.makedirs("game/dev_logs")
                
                filename = f"game/dev_logs/session_today.json"
                
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(self.logs[-100:], f, ensure_ascii=False, indent=2)
            except:
                pass
        
        def get_game_data(self):
            """Получает данные игры, создает временные если в главном меню"""
            if 'game_db' in globals() and game_db:
                try:
                    game_db.sync_achievements()
                    return game_db.get_all_data()
                except:
                    pass
            
            # Если в главном меню или ошибка, возвращаем пустые данные
            return {
                "player_name": "Нет активной игры",
                "chapter": 0,
                "achievements": [],
                "achievements_data": [],
                "stats": {},
                "choices": []
            }
        
        def export_player_data(self):
            try:
                data = self.get_game_data()
                report = self.generate_report(data)
                
                if not os.path.exists("game/dev_logs"):
                    os.makedirs("game/dev_logs")
                    
                filename = f"game/dev_logs/player_{data.get('player_name', 'Unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(report)
                
                return f"✅ Отчет сохранен: {filename}"
            except Exception as e:
                return f"❌ Ошибка при экспорте данных: {e}"
        
        def generate_report(self, data):
            report = "=" * 60 + "\n"
            report += "ОТЧЕТ ПО ИГРОКУ\n"
            report += "=" * 60 + "\n\n"
            
            report += f"Имя игрока: {data.get('player_name', 'Неизвестно')}\n"
            report += f"Текущая глава: {data.get('chapter', 1)}\n\n"
            
            report += "-" * 40 + "\n"
            report += "ДОСТИЖЕНИЯ:\n"
            report += "-" * 40 + "\n"
            
            achievements_found = False
            
            if 'achievements_data' in data:
                unlocked_achievements = [a for a in data['achievements_data'] if a.get('unlocked', False)]
                if unlocked_achievements:
                    achievements_found = True
                    for ach in unlocked_achievements:
                        report += f"✓ {ach.get('name', 'Неизвестно')}\n"
                        if ach.get('progress') and ach.get('max_progress') and ach['max_progress'] > 1:
                            report += f"  Прогресс: {ach['progress']}/{ach['max_progress']}\n"
                else:
                    report += "Нет разблокированных достижений\n"
            else:
                achievements = data.get('achievements', [])
                if achievements:
                    achievements_found = True
                    for ach in achievements:
                        report += f"✓ {ach}\n"
                else:
                    report += "Нет достижений\n"
            
            if not achievements_found and 'Achievement' in globals():
                try:
                    global_achievements = [a for a in Achievement.all_achievements() if a.has()]
                    if global_achievements:
                        report += "\n(Найдены в глобальном списке):\n"
                        for a in global_achievements:
                            report += f"✓ {a.name}\n"
                except:
                    pass
            
            report += "\n" + "-" * 40 + "\n"
            report += "СТАТИСТИКА ВЫБОРОВ:\n"
            report += "-" * 40 + "\n"
            stats = data.get('stats', {})
            if stats:
                for key, value in stats.items():
                    report += f"{key}: {value}\n"
            else:
                report += "Нет статистики\n"
            
            report += "\n" + "-" * 40 + "\n"
            report += "ИСТОРИЯ ВЫБОРОВ:\n"
            report += "-" * 40 + "\n"
            choices = data.get('choices', [])
            if choices:
                for i, choice in enumerate(choices[-20:], 1):
                    report += f"{i}. {choice.get('choice', 'Неизвестно')}\n"
                    if 'timestamp' in choice:
                        report += f"   ({choice['timestamp']})\n"
            else:
                report += "Нет выборов\n"
            
            report += "\n" + "=" * 60 + "\n"
            return report
        
        def get_statistics(self):
            stats = {
                "total_achievements": {},
                "popular_choices": {}
            }
            
            try:
                data = self.get_game_data()
                
                achievements_counted = False
                
                if 'achievements_data' in data:
                    for ach in data['achievements_data']:
                        if ach.get('unlocked', False):
                            ach_name = ach.get('name', 'Неизвестно')
                            stats["total_achievements"][ach_name] = stats["total_achievements"].get(ach_name, 0) + 1
                            achievements_counted = True
                
                if not achievements_counted and 'Achievement' in globals():
                    try:
                        for a in Achievement.all_achievements():
                            if a.has():
                                stats["total_achievements"][a.name] = stats["total_achievements"].get(a.name, 0) + 1
                    except:
                        pass
                
                for choice in data.get('choices', []):
                    choice_text = choice.get('choice', '')
                    if choice_text:
                        stats["popular_choices"][choice_text] = stats["popular_choices"].get(choice_text, 0) + 1
                        
            except Exception as e:
                if self.debug_mode:
                    renpy.notify(f"Ошибка статистики: {e}")
            
            return stats
    
    dev_tools = DeveloperTools()

# Упрощенный экран для просмотра данных по центру
screen centered_text(text):
    modal True
    zorder 100
    
    frame:
        background "#000000CC"
        xfill True
        yfill True
        
        viewport:
            scrollbars "vertical"
            mousewheel True
            draggable True
            xfill True
            yfill True
            
            # Контейнер для центрирования текста
            vbox:
                xfill True
                
                # Добавляем пустое пространство сверху для центрирования
                null height 100
                
                # Основной текст по центру
                text text:
                    size 18
                    color "#FFFFFF"
                    line_spacing 2
                    xalign 0.5
                    text_align 0.5
                    font "fonts/ofont.ru_Gnocchi.ttf"  # Используем шрифт из игры
                
                # Пустое пространство между текстом и кнопкой
                null height 50
                
                # Кнопка возврата
                textbutton _("Вернуться"):
                    xalign 0.5
                    action Return()
                    text_size 24
                    text_color "#FFD700"
                    text_hover_color "#FFFFFF"
                    background "#333333"
                    hover_background "#666666"
                    padding (20, 10)

label view_player_data:
    scene black
    $ renpy.block_rollback()
    
    $ data = dev_tools.get_game_data()
    $ report = dev_tools.generate_report(data)
    
    call screen centered_text(report)
    return

label dev_reset_data:
    if 'game_db' in globals() and game_db:
        $ game_db.reset_data()
        if 'Achievement' in globals():
            $ Achievement.reset()
        "✅ Данные сброшены"
    else:
        "❌ Нет активной игры"
    return

label developer_menu:
    scene black
    $ renpy.block_rollback()
    
    menu:
        "🔧 ИНСТРУМЕНТЫ РАЗРАБОТЧИКА"
        
        "📊 Просмотреть данные игрока":
            call view_player_data
            jump developer_menu
            
        "📈 Статистика выборов":
            $ stats = dev_tools.get_statistics()
            $ stats_text = "=== СТАТИСТИКА ===\n\n"
            
            $ stats_text += "ДОСТИЖЕНИЯ:\n"
            $ achievements = stats['total_achievements']
            if achievements:
                python:
                    sorted_achievements = sorted(achievements.items(), key=lambda x: x[1], reverse=True)
                    for ach, count in sorted_achievements:
                        stats_text += f"  {ach}: {count}\n"
            else:
                $ stats_text += "  Нет данных о достижениях\n"
            
            $ stats_text += "\nПОПУЛЯРНЫЕ ВЫБОРЫ:\n"
            $ choices = stats['popular_choices']
            if choices:
                python:
                    sorted_choices = sorted(choices.items(), key=lambda x: x[1], reverse=True)[:10]
                    for choice, count in sorted_choices:
                        if len(choice) > 50:
                            choice = choice[:47] + "..."
                        stats_text += f"  {choice}: {count}\n"
            else:
                $ stats_text += "  Нет данных о выборах\n"
            
            call screen centered_text(stats_text)
            jump developer_menu
            
        "📝 Режим отладки: [dev_tools.debug_mode]":
            $ dev_tools.toggle_debug()
            jump developer_menu
            
        "💾 Экспортировать данные":
            $ result = dev_tools.export_player_data()
            "[result]"
            pause
            jump developer_menu
            
        "🗑️ Сбросить данные (тест)":
            menu:
                "Вы уверены? Это удалит весь прогресс!"
                "Да":
                    call dev_reset_data
                "Нет":
                    pass
            jump developer_menu
            
        "🔙 Вернуться в игру":
            return

init python:
    def show_dev_menu():
        renpy.call_in_new_context("developer_menu")
    
    config.underlay.append(renpy.Keymap(K_F12=show_dev_menu))