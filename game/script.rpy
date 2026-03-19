# Определение персонажей игры.
define e = Character('[myname]', color="#c70081")
define v = Character('Ник', color="#b3a400")
define c = Character('Незнакомый голос', color="#b3a400")
define f = Character('Незнакомый номер', color="#b3a400")
define config.mouse = {"default" : [ ("mouse.webp", 0,0)]}

# Звук
init python:
    renpy.music.register_channel(name="music_game")

# Метка для обновления имени в БД
label update_player_name(name):
    $ game_db.player_name = name
    $ game_db.save_data()
    return

label enter_game_menu():
    python:
        for channel in renpy.audio.audio.all_channels:
            if channel.name != "music_game":
                renpy.music.set_pause(True,channel=channel.name)
    return

label splashscreen:
    scene black
    with Pause(1)

    play sound "audio/intro.ogg"
    show text "{font=fonts/ofont.ru_Gnocchi.ttf}{color=#FFFFFF}Рекомендуется надеть наушники для полного погружения!{/color}{/font}" with dissolve
    with Pause(2)

    hide text with dissolve
    with Pause(1)

    return

# ================ СИСТЕМА ДОСТИЖЕНИЙ ================
init python:
    # Класс Achievement из вашего файла
    class Achievement:
        _all_achievements = []
        
        def __init__(self, name, id, description, unlocked_image, locked_image="locked_achievement", 
                     hide_name=False, hide_description=False, stat_max=None, show_progress_bar=True,
                     stat_update_percent=None, stat_modulo=None):
            self.name = name
            self.id = id
            self.description = description
            self.unlocked_image = unlocked_image
            self.locked_image = locked_image
            self.hide_name = hide_name
            self.hide_description = hide_description
            self.stat_max = stat_max
            self.show_progress_bar = show_progress_bar
            self.stat_update_percent = stat_update_percent
            self.stat_modulo = stat_modulo
            self._unlocked = False
            self._progress = 0
            self._set_progress = set()
            Achievement._all_achievements.append(self)
        
        def has(self):
            return self._unlocked
        
        def grant(self):
            if not self._unlocked:
                self._unlocked = True
                if renpy.has_screen("achievement_popup") and myconfig.SHOW_ACHIEVEMENT_POPUPS:
                    renpy.show_screen("achievement_popup", self)
                    if myconfig.ACHIEVEMENT_SOUND and renpy.loadable(myconfig.ACHIEVEMENT_SOUND):
                        renpy.play(myconfig.ACHIEVEMENT_SOUND, myconfig.ACHIEVEMENT_CHANNEL)
                
                # Синхронизируем с БД
                if 'game_db' in globals() and game_db:
                    try:
                        game_db.sync_achievements()
                        # Добавляем в список достижений для отчета
                        if self.name not in game_db.get_data('achievements', []):
                            achievements_list = game_db.get_data('achievements', [])
                            achievements_list.append(self.name)
                            game_db.set_data('achievements', achievements_list)
                        game_db.save_data()
                    except Exception as e:
                        # Игнорируем ошибки, чтобы не ломать игру
                        pass
        
        def add_progress(self, amount=1):
            if not self._unlocked and self.stat_max:
                self._progress = min(self._progress + amount, self.stat_max)
                if self._progress >= self.stat_max:
                    self.grant()
                else:
                    # Синхронизируем прогресс даже если не разблокировано
                    if 'game_db' in globals() and game_db:
                        try:
                            game_db.sync_achievements()
                        except:
                            pass
        
        def progress(self, value):
            if not self._unlocked and self.stat_max:
                self._progress = min(value, self.stat_max)
                if self._progress >= self.stat_max:
                    self.grant()
                else:
                    if 'game_db' in globals() and game_db:
                        try:
                            game_db.sync_achievements()
                        except:
                            pass
        
        def add_set_progress(self, value):
            if not self._unlocked and self.stat_max:
                self._set_progress.add(value)
                if len(self._set_progress) >= self.stat_max:
                    self.grant()
                else:
                    if 'game_db' in globals() and game_db:
                        try:
                            game_db.sync_achievements()
                        except:
                            pass
        
        def clear(self):
            self._unlocked = False
            self._progress = 0
            self._set_progress = set()
        
        @property
        def stat_progress(self):
            if self._set_progress:
                return len(self._set_progress)
            return self._progress
        
        @classmethod
        def all_achievements(cls):
            return cls._all_achievements
        
        @classmethod
        def num_earned(cls):
            return sum(1 for a in cls._all_achievements if a.has())
        
        @classmethod
        def num_total(cls):
            return len(cls._all_achievements)
        
        @classmethod
        def reset(cls):
            for a in cls._all_achievements:
                a.clear()
    
    # Конфигурация достижений
    class myconfig:
        INGAME_POPUP_WITH_STEAM = True
        ACHIEVEMENT_HIDE_TIME = 1.0
        SHOW_ACHIEVEMENT_POPUPS = True
        ACHIEVEMENT_SOUND = "audio/sfx/achievement.ogg"
        ACHIEVEMENT_CHANNEL = "audio"
        HIDDEN_ACHIEVEMENT_NAME = "???{#hidden_achievement_name}"
        HIDDEN_ACHIEVEMENT_DESCRIPTION = "???{#hidden_achievement_description}"

# Изображение заблокированного достижения по умолчанию
image locked_achievement = Text("?", color="#000000")

# ================ ОПРЕДЕЛЕНИЕ ДОСТИЖЕНИЙ ================

define progress_achievement = Achievement(
    name=_("Прогрессивное достижение"),
    id="progress_achievement",
    description=_("Это достижение с индикатором прогресса."),
    unlocked_image=Transform("gui/window_icon.png", matrixcolor=InvertMatrix()),
    stat_max=12,
    show_progress_bar=True,
)

define set_progress_achievement = Achievement(
    name=_("Прогрессивное достижение с набором"),
    id="set_progress_achievement",
    description=_("Это достижение с прогрессом, но без индикатора."),
    unlocked_image=Transform("gui/window_icon.png", matrixcolor=HueMatrix(270)),
    stat_max=3,
    show_progress_bar=False,
)

define hidden_achievement = Achievement(
    name=_("Скрытое достижение"),
    id="hidden_achievement",
    description=_("Это полностью скрытое достижение скрывает и имя, и описание."),
    unlocked_image=Transform("gui/window_icon.png", matrixcolor=SepiaMatrix()),
    hide_name=True,
    hide_description=True,
)

define hidden_description = Achievement(
    name=_("Скрытое описание"),
    id="hidden_description",
    description=_("Это скрытое достижение скрывает только описание."),
    unlocked_image=Transform("gui/window_icon.png", matrixcolor=SepiaMatrix()),
    hide_description=True,
)

define hidden_name_only = Achievement(
    name=_("Скрытое имя"),
    id="hidden_name_only",
    description=_("Это достижение скрывает только имя."),
    unlocked_image=Transform("gui/window_icon.png", matrixcolor=HueMatrix(90)),
    hide_name=_("Секретное достижение"),
    hide_description=False,
)

# ДОСТИЖЕНИЯ ДЛЯ ВАШЕЙ ИГРЫ
define key_vision_achievement = Achievement(
    name=_("Видение прошлого"),
    id="key_vision_achievement",
    description=_("Коснувшись ключа, ты увидела отрывок из прошлого. Чей-то голос просит сохранить тайну."),
    unlocked_image="gui/window_icon.png",  # Замените на своё изображение
    locked_image="locked_achievement",
    hide_name=False,
    hide_description=False,
)

define coffee_choice_achievement = Achievement(
    name=_("Кофейный выбор"),
    id="coffee_choice_achievement",
    description=_("Ты сделала свой первый выбор кофе. Вкус определяет характер."),
    unlocked_image="gui/window_icon.png",
    locked_image="locked_achievement",
    hide_name=False,
    hide_description=False,
)

define mysterious_message_achievement = Achievement(
    name=_("Таинственное сообщение"),
    id="mysterious_message_achievement",
    description=_("Странное сообщение с неизвестного номера: «Не верь сладкому кофе. Он тоже умеет обманывать»."),
    unlocked_image="gui/window_icon.png",
    locked_image="locked_achievement",
    hide_name=False,
    hide_description=False,
)

# ================ ЭКРАН ВСПЛЫВАЮЩЕГО ОКНА ДОСТИЖЕНИЯ ================
screen achievement_popup(a):
    zorder 190
    default achievement_yoffset = 0
    
    frame:
        style_prefix 'achieve_popup'
        at achievement_popout()
        yoffset achievement_yoffset
        has hbox
        add a.unlocked_image:
            fit "contain" ysize 95 align (0.5, 0.5)
        vbox:
            text a.name
            text a.description size 25
    
    timer 5.0 action Hide("achievement_popup")

style achieve_popup_frame:
    align (0.0, 0.0)
style achieve_popup_hbox:
    spacing 10
style achieve_popup_vbox:
    spacing 2

transform achievement_popout():
    on show:
        xpos 0.0 xanchor 1.0
        easein_back 1.0 xpos 0.0 xanchor 0.0
    on hide, replaced:
        easeout_back myconfig.ACHIEVEMENT_HIDE_TIME xpos 0.0 xanchor 1.0

# ================ ЭКРАН ГАЛЕРЕИ ДОСТИЖЕНИЙ ================
screen achievement_gallery():
    tag menu
    
    use game_menu(_("Достижения"), scroll="viewport"):
        style_prefix "achievement_gallery"
        
        vbox:
            spacing 20
            
            # Счетчик достижений
            hbox:
                text "Достижения: " size 36
                text "[Achievement.num_earned()]/[Achievement.num_total()]" size 36 color "#f93c3e"
            
            # Список достижений
            vpgrid:
                cols 1
                spacing 15
                mousewheel True
                draggable True
                pagekeys True
                scrollbars "vertical"
                ysize 600
                
                for a in Achievement.all_achievements():
                    button:
                        style "achievement_button"
                        
                        has hbox
                        spacing 20
                        
                        # Изображение достижения
                        fixed:
                            xysize (100, 100)
                            if a.has():
                                add a.unlocked_image fit "scale-down" xysize (90, 90) align (0.5, 0.5)
                            else:
                                add a.locked_image fit "scale-down" xysize (90, 90) align (0.5, 0.5)
                        
                        # Информация о достижении
                        vbox:
                            spacing 5
                            xfill True
                            
                            # Название
                            if a.has() or not a.hide_name:
                                text a.name size 36 color "#000000"
                            else:
                                text myconfig.HIDDEN_ACHIEVEMENT_NAME size 36 color "#000000"
                            
                            if a.has():
                                # Разблокировано - показываем описание и время
                                text a.description size 25 color "#777777"
                            else:
                                # Заблокировано
                                if a.hide_description:
                                    text myconfig.HIDDEN_ACHIEVEMENT_DESCRIPTION size 25 color "#777777"
                                else:
                                    text a.description size 25 color "#777777"
                            
                            # Прогресс-бар если есть
                            if not a.has() and a.stat_max and a.show_progress_bar:
                                fixed:
                                    xysize (300, 30)
                                    bar value a.stat_progress range a.stat_max:
                                        xysize (300, 20)
                                    text "[a.stat_progress]/[a.stat_max]":
                                        size 16
                                        color "#ffffff"
                                        align (0.5, 0.5)
# ================ ОСНОВНАЯ ИГРА ================
label start:
    # Инициализация новой базы данных для новой игры
    $ game_db = GameDatabase()
    
    # Загружаем состояние достижений из БД
    $ game_db.load_achievements_state()
    
    # ... остальной код ...
    
    stop music
    scene black
    with Pause(1)
    show text "{font=fonts/ofont.ru_Gnocchi.ttf}{color=#ff0000}ВНИМАНИЕ{/color}{color=#fff}\n\nДанный игровой проект является вымышленной историей и художественным произведением в жанре визуальной\n новеллы. Сюжет и механики игры построены вокруг феномена потери памяти (амнезии). Просим вас относиться к этому как к художественному допущению, служащему цели раскрытия персонажей и повествования.{/color}{/font}" with dissolve
    with Pause(5)
    hide text with dissolve
    with Pause(1)
    
    $ myname = renpy.input("Как зовут вашу героиню?", length=12, default="Юри", allow="йцукенгшщзхъфывапролджэячсбмитьюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ").strip()
    if myname == "":
        $ myname = "Юри"
    
    # Сохраняем имя в базу данных
    $ game_db.player_name = myname
    $ game_db.save_data()
    $ game_db.add_choice(f"Выбрано имя: {myname}", "start")
    
    # Логируем действие (если dev_tools существует)
    python:
        if 'dev_tools' in globals():
            dev_tools.log_player_action("Ввод имени", f"Имя: {myname}")
    
    # ... остальной код игры ...

    scene bg street
    "Пустая улица маленького американского городка. Старые кирпичные здания выстроились вдоль неё сплошной стеной."
    "Солнце только поднялось над крышами, и его прямые лучи заливают улицу мягким золотистым светом."
    "Тишина стоит необыкновенная. Лишь изредка где-то далеко воркуют голуби, да лёгкий ветерок шелестит сухими листьями, собравшимися у водосточных труб."
    "Вывески закрытых магазинов неприметные и стандартные, каких полно в любом маленьком городке их названия давно выцвели или стёрлись, оставив лишь смутные очертания букв."
    e "«Сегодня мой первый день на новой работе»"
    "Внутри привычная, но от того не менее острая пустота. Амнезия стёрла так много, что каждый новый день это шаг в тумане. "
    "Дорогу к новому офису мне вчера подробно объяснила девушка из отдела кадров, но тревога нарастает с каждым разoм при мысли того, что я снова все забуду."
    "Я судорожно вздыхаю, останавливаясь, чтобы перевести дух. Вокруг ни души, только я и это безупречное, спокойное утро. Контраст между безмятежностью мира и бурей в моей голове оглушителен."
    e "«Господи, как же это волнительно. А вдруг они заметят, что я какая-то не такая? Вдруг спросят что-то из прошлого опыта, а я буду стоять и хлопать глазами»."
    "Я делаю ещё несколько шагов и вдруг замираю. Прямо у стены, в тени, на асфальте лежит обычные старый ключ на потёртом металлическом кольце."

    scene bg keyd
    menu:
        e "Что же делать?"
        
        "взять ключ":
            $ game_db.add_choice("Взяла ключ", "start_key_choice")
            $ game_db.update_stat("key_taken", True)
            
            play sound key
            scene bg street
            "Я оглядываюсь ещё раз — никого. Быстро наклоняюсь и беру связку. Ключ приятно тяжелеет в ладони, холодный и чуть шероховатый на ощупь."
            scene black
            play music fear
            "Внезапно мир вокруг теряет чёткость. Края зрения темнеют, и я чувствую резкий запах — смесь кофе и чего-то сладкого, знакомого до боли."
            scene bg gg
            "Перед глазами вспышка. Я моргаю, пытаясь сфокусировать взгляд, но картинка плывёт. Где я? Что это за место?"
            scene bg hands
            "Вокруг ничего нет. Только пустота — бесконечная, серая, давящая. Я смотрю вниз, на свои руки, и не чувствую их. Совсем. Словно они чужие, приделанные к моему телу. Тишина давит на уши."
            "Голос..."
            c "«Не выкидывай их. Никогда. Даже если захочешь забыть всё, что было...»"
            "Тишина взрывается звуком. Женский голос. Мягкий, с едва уловимой грустью. Он звучит прямо в моей голове, эхом отражаясь от стен пустоты."
            scene black with fade
            "Тьма начинает медленно наползать от краёв зрения, поглощая серую пустоту. Голос затихает, словно уходя вглубь колодца."
            c "«Пожалуйста... не забывай...»"
            "Чёрная пелена окончательно смыкается, проглатывая последние отголоски света и звука."
            stop music fadeout 3.0
            scene bg street
            
            # Добавляем только одно достижение за видение
            $ key_vision_achievement.grant()
            
            e "Кто... кто она? Откуда я знаю этот голос?"
            "Видение исчезает так же внезапно, как и появилось, оставляя после себя лишь горьковато-сладкий привкус на губах и бешеный стук сердца. Реальность возвращается ударом по обонянию — резкий запах выхлопных газов проезжающей мимо машин"
            
        "не брать ключ":
            $ game_db.add_choice("Не взяла ключ", "start_key_choice")
            $ game_db.update_stat("key_taken", False)
            
            scene bg street
            "[myname] смотрит на ключи ещё мгновение, но потом решительно отводит взгляд. Это не её вещь. Не её потеря. Кто-то вернётся за ними — или не вернётся, но это уже не её дело."
    
    scene bg street cafe
    "Ноги сами несут вперёд, прочь от этого злополучного двора. Завернув за угол, я словно выныриваю из безмолвия. Город уже проснулся. Здесь уже не пусто — мимо спешат первые прохожие, кто-то с собакой, кто-то с бумажным стаканчиком кофе."
    "Впереди, на углу, виднеется знакомая вывеска «Утренний свет». Небольшое кафе с большими окнами, за которыми уже горят тёплые лампы. Это её новое место работы."
    "Сквозь стекло видно, как внутри суетится бармен в фартуке, расставляет стулья, протирает столики."
    "Из приоткрытой дверцы доносится запах свежей выпечки и кофе такой густой и тёплый, что на мгновение перебивает даже утреннюю свежесть."
    
    scene bg cafe
    play sound bells
    "Я толкаю дверь и над головой раздаётся мелодичный звон колокольчика, тонкий и чуть дребезжащий."
    "На мгновение замираю на пороге, втягивая носом тёплый воздух с нотками свежесмолотого кофе и ванили."
    "Глазам требуется пара секунд, чтобы привыкнуть к мягкому свету настенных бра."
    "Я оглядываюсь, рассматривая стены, выкрашенные в тёплый бежевый, картинки с чашками и забавные надписи в деревянных рамках."
    
    show nik happy 
    "Взгляд скользит по аккуратно расставленным столикам и идеально вытертой стойке, поблёскивающей в мягком свете и останавливается на мужчине, который идёт к ней навстречу."
    
    show nik talk
    v " Привет! Я Ник, твой наставник. А ты, наверное, [myname]?"
    show nik normal
    
    menu:
        e "Что сказать в ответ?"
        
        "Да, я...":
            $ game_db.add_choice("Да, я... (растерянный ответ)", "first_meeting")
            $ game_db.update_stat("first_meeting_response", "растерянный")
            
            e "Да, я... [myname]. Приятно познакомиться. Извини, задумалась просто."
            show nik talk
            v "Ничего страшного, первый день — он такой. Полчаса назад я сам забыл, куда поставил молоко для капучино. Добро пожаловать в наш маленький хаос!"
            
        "Прости, я немного растеряна":
            $ game_db.add_choice("Прости, я немного растеряна (честный ответ)", "first_meeting")
            $ game_db.update_stat("first_meeting_response", "честный")
            
            e "Прости, я немного растеряна. Первый день всё-таки. [myname], очень приятно."
            show nik talk
            v "О, не извиняйся! В первый день все как котята в новой квартире тычутся во все углы."
            v "Я сам в первую смену молоко вместо сливок в капучино налил. Посетитель, кстати, оценил. Сказал, 'инновационно'."
    
    
            
    show nik normal
    "Мои губы сами собой складываются в слабую улыбку, напряжение слегка отпускает и я наконец позволяю себе как следует рассмотреть нового знакомого."
    
    show nik hands normal
    "Взгляд цепляется за непослушный тёмные пряди, что лезут на глаза. Рукава рубашки небрежно закатаны до локтей и его руки жилистые руки, с едва заметными венами."
    "Ник перехватывает этот взгляд и, вместо того чтобы смутиться, кажется, находит это забавным. Он не отводит глаза только чуть заметно приподнимает бровь."
    
    show nik hands 
    v "Как видишь у нас тут скромно, без пафоса. Зато уютно некоторые специально приходят посидеть с книжкой или ноутбуком."
    v "Посетителей не так много, особенно по будням с утра. Но есть парочка постоянных клиентов, которых ты быстро запомнишь."
    
    show nik hands normal
    "Он замечает, что мой взгляд на мгновение останавливается на его фартуке там, где расплылось коричневатое пятно."
    
    show nik shy
    v "Ох, снова испачкался. Утренний ритуал: сварил кофе, облился, проснулся. Рекомендую как способ взбодриться, если кофеин уже не берёт."
    show nik happ2
    "Я ловлю себя на мысли, что парень говорит без остановки, перескакивает с темы на тему, но в этом нет навязчивости скорее искреннее желание поболтать."
    
    show nik hands
    v "Ладно, хватит лясы точить. Проходи, я тебе сейчас всё покажу."
    
    show nik talk
    v "Заходи в святая святых. Только осторожно здесь я иногда спотыкаюсь об этот ящик с сиропами."
    
    show nik normal
    "Я аккуратно обхожу ящик, бросив на него короткий взгляд, и оказываюсь за стойкой."
    
    show nik hands
    v"Знакомься, это Джулия. Итальянка, характер сложный, но если найти подход таких рафов наварит, пальчики оближешь. Я тебя потом научу с ней общаться. Не бойся, она кусается только паром."
    
    show nik happy talk
    v "И давай сразу на «ты», а то мы тут все свои. Официальность оставим для налоговой и особо строгих гостей. Договорились?"
    show nik happ2
    "Я наконец позволяю себе кивнуть чуть более заметно. В уголках губ проскальзывает робкая, почти неуловимая улыбка. Я тихо, но отчётливо произношу:"
    
    e "Договорились."
    
    show nik hands normal
    "Ник довольно улыбается, будто именно этого ответа и ждал. Он легко разворачивается на пятках, тянется к верхней полке и достаёт оттуда чистую чашку."
    
    show nik hands
    v "В общем, вводная часть такая: вот это чудо техники кофемашина. Она капризная, но мы друг друга любим."
    v "Вот контейнеры с зёрнами слева обычная арабика, справа декаф, если кто просит без кофеина, хотя такие гости бывают редко."
    v "А вот здесь у нас сиропы, топинги, всякие вкусовые добавки. Карамель, ваниль, лесной орех, а ещё есть пряничный его под Рождество улетает просто космос."
    v "Касса простая, интуитивная. Пара дней и будешь щёлкать заказы с закрытыми глазами. Пока просто посмотришь, как я работаю, а когда сама сядешь помогу, не переживай."
    v "Гости здесь в основном хорошие, есть пара постоянников, которые приходят как часы. Со временем запомнишь их заказы. Чаевые бывают обычно мелочь, но по праздникам завсегдатаи радуют."
    v "Уборка после закрытия стандартно: столицы протереть, полы помыть, оборудование почистить. Покажу всё подробнее вечером."
    
    
    v "Вопросы?"
    show nik hands normal
    "Слова уже готовы сорваться с губ, я приоткрываю рот, но Ник внезапно щёлкает пальцами, перебивая меня, видимо вспомнил что-то важное.."
    
    show nik talk
    v "А, да, чуть не забыл! Главное правило, кофе сначала себе, потом гостям. Иначе какой смысл работать в кофейне?"
    show nik normal
    "На его лице расплывается хитрая улыбка. Я на мгновение застываю, пытаясь понять, шутит он или говорит серьёзно."
    show nik talk
    v "Ладно, шучу. Хотя доля правды есть. Но знаешь что? Теория теорией, но лучше один раз попробовать. Давай сразу к практике."
    v "Ты какой любишь? Раф, капучино, американо? Или, может, что-то погорячее — типа шоколада с апельсином? У нас есть секретный рецепт."
    
    show nik normal
    "Задумавшись, я склоняю голову к плечу. Прядь волос соскальзывает мне на лицо и я автоматически заправляю её за ухо"
    
    menu:
        e "Какой кофе выбрать?"
        
        "Раф":
            $ game_db.add_choice("Выбрала Раф", "coffee_choice")
            $ game_db.update_stat("coffee_preference", "Раф")
            e "Раф.. наверное?"
            
        "Капучино":
            $ game_db.add_choice("Выбрала Капучино", "coffee_choice")
            $ game_db.update_stat("coffee_preference", "Капучино")
            e "Капучино, пожалуй..."
            
        "Американо":
            $ game_db.add_choice("Выбрала Американо", "coffee_choice")
            $ game_db.update_stat("coffee_preference", "Американо")
            e "Американо. Покрепче."

    # Добавляем достижение за выбор кофе
    $ coffee_choice_achievement.grant()

    if game_db.get_stat("coffee_preference") == "Раф":
        show nik happy talk
        v "Хороший выбор. Мой любимый, кстати."
    elif game_db.get_stat("coffee_preference") == "Капучино":
        show nik hands
        v "Классика. Уважаю."
    elif game_db.get_stat("coffee_preference") == "Американо":
        show nik hands
        v "О, любительница покрепче. Тоже хорошо."

    show nik normal
    "Ник разворачивается к кофемашине и начинает колдовать. Его движения становятся собранными, но при этом сохраняют ту особую расслабленную пластику, которая бывает только у людей, идеально знающих своё дело."

    show nik talk
    v "Знаешь, у нас тут был один товарищ. Приходил каждое утро и заказывал американо. Месяцами. А потом вдруг попросил латте с малиновым сиропом. Я чуть кофемолку не уронил."

    show nik normal
    e "И что?"

    show nik hands
    v "А то, оказалось, он просто влюбился. Девушка его пила только сладкий кофе. Так что месяц ходил с малиновым латте, морщился, но пил."

    v "А потом они поженились, и он снова вернулся к американо. С облегчением таким, я тебе скажу."

    show nik hands normal
    e "Неужели правда?"

    show nik happy talk
    v "Чистая правда. До сих пор иногда заходят вдвоём. Он с американо, она с латте. Идиллия."

    show nik hands normal
    e "Значит, любовь меняет вкусы."

    "Я произношу это почти шёпотом, скорее для себя, чем для Ника. Пальцы в кармане сжимают ключ. Интересно, чей вкус изменила бы я? Или, может быть, уже изменила просто не помню об этом."

    scene bg coffe
    play sound cap

    if game_db.get_stat("coffee_preference") == "Раф":
        scene bg raf
        v "Прошу. Раф по-никски."
    elif game_db.get_stat("coffee_preference") == "Капучино":
        scene bg cap
        v "Прошу. Капучино от шефа."
    elif game_db.get_stat("coffee_preference") == "Американо":
        scene bg coffe
        v "Прошу. Американо, крепкий как жизнь."

    scene bg cafe
    show nik hands normal

    
    "Он вытирает руки о фартук и опирается локтями о стойку напротив меня. В его позе нет напряжения только лёгкое, почти дружеское любопытство."

    show nik hands
    v "А ты, я смотрю, философ."

    show nik hands normal
    "Я отвожу взгляд, разглядывая кофейную пену. Слишком много смысла он ищет в моих случайных словах. Или не случайных?"

    e "Просто мысли вслух."

    show nik sad
    "Он замолкает на секунду, а потом его лицо становится чуть серьёзнее."

    show nik sad talk

    v "Слушай... я понимаю, что мы едва знакомы. И ты имеешь полное право послать меня куда подальше со своим нытьём."

    show nik smile sad
    "Я поднимаю на него глаза. Ник выглядит неловко впервые за всё время нашего короткого знакомства."

    show nik shy
    v "Но если захочешь поговорить... ну, про это всё. Про память, про то, что ты чувствуешь. Я умею слушать. Дядя научил."

    show nik shy smile
    "Он проводит рукой по затылку, взлохмачивая и без того торчащий вихор."

    show nik talk
    v "А если не захочешь тоже норм. Будем просто пить кофе и болтать о всякой ерунде. Про клиентов там, про погоду. Про то, какой сегодня смешной дядька заказывал капучино без кофеина."

    show nik normal
    "Я почти улыбаюсь этому образу."

    e "Капучино без кофеина? Зачем?"

    show nik hands

    v "Вот! Уже разговор! Говорит, врач прописал кофе убрать, а без ритуала он не может. Приходит каждое утро, нюхает свежемолотые зёрна, заказывает пустышку и сидит с довольным лицом."

    v "Я ему предлагал цикорий — обиделся."

    show nik happy talk
    "Ник смеётся, и в его смехе столько тепла, что ключ в кармане перестаёт жечь ладонь. Хотя бы на минуту."

    show nik normal

    v "В общем, предложение в силе. А пока — пей, остынет."

    "Я делаю первый глоток. Кофе мягкий, ванильный, с едва уловимой сладостью. Совсем не похож на тот резкий запах из видения. И от этого почему-то легче."

    e "Спасибо, Ник. Правда."

    show nik happy
    "Он просто кивает, не требуя пояснений, и принимается протирать и без того идеально чистую кофемашину. Давая мне пространство."
    scene bg cafe
    "Вдруг тишину разрывает резкая вибрация. Я вздрагиваю, расплёскивая немного кофе на блюдце."

    "Из кармана джинсов доносится настойчивый сигнал. Я на секунду замираю, глядя на Ника, но он даже не оборачивается"

    e "Одно непрочитанное сообщение. Номер не сохранён."

    "Пальцы сами сжимаются телефон. Почему-то вдруг становится трудно дышать."

    "Я открываю сообщение. Там всего несколько слов."

    $ game_db.update_stat("mysterious_message_read", True)
    $ mysterious_message_achievement.grant()

    f "Не верь сладкому кофе. Он тоже умеет обманывать."

    scene black
    with Pause(1)

    # Сохраняем финальные данные
    $ game_db.save_data()

    play sound "audio/intro.ogg"
    show text "{font=fonts/YourFont.ttf}{color=#fff}the end of the first day! Beta version!{/color}{/font}" with dissolve
    with Pause(2)

    hide text with dissolve
    with Pause(1)

    return