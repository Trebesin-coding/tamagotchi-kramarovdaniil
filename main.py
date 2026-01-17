from nicegui import ui, app
import sys
import json
import os
import random
import copy
from PIL import Image

ui.add_head_html("""
<style>
html, body {
    margin: 0 !important;
    padding: 0 !important;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: transparent !important;
}

#q-app, .q-layout, .q-page-container, .q-page {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    height: 100% !important;
    overflow: hidden;
    background: transparent;
}
</style>
""", shared=True)



warrior = {}
enemy_stat_labels = {}

default_warrior = {
    "name": "Adam",
    "hp": 100,
    "energy": 100,
    "max_energy": 100,
    "alive": True,
    "money": 100,
    "damage": 10,
    "defence": 10,
    "luck": 5,
    "ult_charge": 0,
    "ult_ready": False,
    "defending": False,
    "items": [],
    "defeated_bosses": []
}

ITEM_CATEGORIES = {
    "weapons": "Weapons",
    "armor": "Armor",
    "rings": "Rings"
}

ITEMS = {
    "sword": {
        "name": "Iron Sword",
        "category": "weapons",
        "price": 50,
        "stats": {"damage": 5}
    },
    "axe": {
        "name": "Battle Axe",
        "category": "weapons",
        "price": 90,
        "stats": {"damage": 10}
    },
    "dragon_slayer": {
    "name": "Dragon Slayer Blade",
    "category": "weapons",
    "price": 350,
    "stats": {
        "damage": 25,
        "luck": 3
        }
    },
    "vampire_reaper": {
        "name": "Vampire Reaper",
        "category": "weapons",
        "price": 500,
        "stats": {
            "damage": 35,
            "luck": 5
        }
    },
    "leather_armor": {
        "name": "Leather Armor",
        "category": "armor",
        "price": 60,
        "stats": {"defence": 5}
    },
    "plate_armor": {
        "name": "Plate Armor",
        "category": "armor",
        "price": 120,
        "stats": {"defence": 12}
    },
    "vampire_reaper": {
        "name": "Vampire Reaper",
        "category": "weapons",
        "price": 500,
        "stats": {
            "damage": 35,
            "luck": 5
        }
    },
    "vampire_king_armor": {
        "name": "Vampire King Armor",
        "category": "armor",
        "price": 450,
        "stats": {
            "defence": 30,
            "hp": 50
        }
    },
    "luck_ring": {
        "name": "Lucky Ring",
        "category": "rings",
        "price": 40,
        "stats": {"luck": 3}
    },
    "ring_of_fate": {
    "name": "Ring of Fate",
    "category": "rings",
    "price": 250,
    "stats": {
        "luck": 8
        }
    },
    "ring_of_destruction": {
    "name": "Ring of Destruction",
    "category": "rings",
    "price": 400,
    "stats": {
        "damage": 10,
        "luck": 5
        }
    }
}

easy_camp_enemy = {
    "name": "Slime",
    "hp": 25,
    "alive": True,
    "damage": 5,
    "defence": 5,
    "luck": 1
}

medium_camp_enemy = {
    "name": "Orc",
    "hp": 50,
    "alive": True,
    "damage": 15,
    "defence": 10,
    "luck": 5
}

hard_camp_enemy = {
    "name": "Vampire",
    "hp": 100,
    "alive": True,
    "damage": 30,
    "defence": 20,
    "luck": 10
}

BOSSES = {
    "big_slime": {
        "name": "Big Slime",
        "hp": 80,
        "damage": 12,
        "defence": 8,
        "luck": 3,
        "reward": 100
    },
    "big_orc": {
        "name": "Big Orc",
        "hp": 150,
        "damage": 25,
        "defence": 15,
        "luck": 6,
        "reward": 250
    },
    "final_boss": {
        "name": "Big Vampire",
        "hp": 300,
        "damage": 40,
        "defence": 25,
        "luck": 12,
        "reward": 500
    }
}

CAMP_MULTIPLIER = {
    "easy": 1.0,
    "medium": 1.5,
    "hard": 2.5
}

CAMP_ESCAPE_MOD = {
    "easy": 1.0,
    "medium": 0.7,
    "hard": 0.4
}

GAME_DIFFICULTY_MOD = {
    "Easy": 0.8,
    "Medium": 1.0,
    "Hard": 1.3
}

CAMP_ENERGY_MOD = {
    "easy": 1.0,
    "medium": 1.3,
    "hard": 1.7
}

ACTION_ENERGY_COST = {
    "attack": 5,
    "defence": 4,
    "run": 8,
    "ultimate": 0
}

WINDOW_SIZES = {
    "1280x720": (1280, 720),
    "1600x900": (1600, 900),
    "1920x1080": (1920, 1080),
}

current_window_size = (1920, 1080)

current_enemy = None
current_camp = None



@ui.page('/')
def main_menu():
    with game_background():
        with ui.element('div').classes('flex flex-col gap-5 items-center'):
            ui.label("Tamagotchi RPG").classes(
                'text-5xl font-bold text-black drop-shadow-lg'
            )

            buttons = {}
            
            if save_exists():
                with open("save.json", "r", encoding="utf-8") as f:
                    saved_warrior = json.load(f)
                if saved_warrior.get("alive", True):
                    buttons["Continue"] = continue_game

            buttons.update({
                "Start new game": start_new_game,
                "Settings": lambda: ui.navigate.to('/settings'),
                "Exit": exit_game,
            })

            for name, func in buttons.items():
                ui.button(name, on_click=func).classes(
                    'bg-blue text-purple-700 font-semibold px-10 py-3 rounded-xl shadow-lg hover:bg-purple-700 hover:text-white transition duration-300'
                )
                
@ui.page('/settings')
def settings_page():
    with game_background():
        with ui.element('div').classes('flex flex-col gap-4 items-center'):
            ui.label("Settings").classes("text-4xl font-bold")

            for name, size in WINDOW_SIZES.items():
                ui.button(
                    name, on_click=lambda s=size: set_resolution(s)).classes(
                    'bg-blue text-purple-700 font-semibold px-8 py-2 rounded-xl'
                )

            ui.button("Back", on_click=lambda: ui.navigate.to('/')).classes(
                    'bg-blue text-purple-700 font-semibold px-8 py-2 rounded-xl'
                )

@ui.page('/difficulty')
def difficulty_page():
    with game_background():
        with ui.element('div').classes('flex flex-col gap-5 items-center'):
            ui.label("Choose difficulty").classes("text-3xl font-bold text-black")
            levels = ["Easy", "Medium", "Hard"]
            for level in levels:
                ui.button(level, on_click=lambda: start_game(level)).classes(
                    'bg-blue text-purple-700 font-semibold px-8 py-2 rounded-xl shadow-md hover:bg-purple-700 hover:text-white transition duration-300'
                )
            ui.button("Back", on_click=lambda: ui.navigate.to('/')).classes(
                'bg-blue text-purple-700 font-semibold px-8 py-2 rounded-xl shadow-md hover:bg-purple-700 hover:text-white transition duration-300'
            )

@ui.page('/game')
def game_page():
    with game_background():
        with ui.element('div').classes('flex flex-col gap-5 items-center'):
            ui.label(f"Welcome to Tamagotchi RPG!").classes('text-5xl font-bold text-black drop-shadow-lg')
            game_buttons = {
                "Farm": lambda: ui.navigate.to('/game_farm'),
                "Bosses": lambda: ui.navigate.to('/game_bosses'),
                "Home": lambda: ui.navigate.to('/game_home'),
                "Shop": lambda: ui.navigate.to('/game_shop'),
                "Save and Exit": save_and_exit
            }    
            for name, func in game_buttons.items():
                    ui.button(name, on_click=func).classes(
                        'bg-blue text-purple-700 font-semibold px-10 py-3 rounded-xl shadow-lg hover:bg-purple-700 hover:text-white transition duration-300'
                    )
            ui.notify("Welcome back!", timeout=3000)
            stats_panel()
        
@ui.page('/game_farm')
def game_farm():
    with game_background():
        with ui.element('div').classes('flex flex-col gap-5 items-center'):
            ui.label(f"Choose camp to farm:").classes('text-5xl font-bold text-black drop-shadow-lg')
            farm_buttons = {
                "Easy camp": lambda: ui.navigate.to('/easy_camp'),
                "Medium camp": lambda: ui.navigate.to('/medium_camp'),
                "Hard camp": lambda: ui.navigate.to('/hard_camp'),
                "Back": lambda: ui.navigate.to('/game')
            }
            for name, func in farm_buttons.items():
                    ui.button(name, on_click=func).classes(
                        'bg-blue text-purple-700 font-semibold px-10 py-3 rounded-xl shadow-lg hover:bg-purple-700 hover:text-white transition duration-300'
                    )
            stats_panel()

@ui.page('/easy_camp')
def easy_camp():
    global current_enemy, current_camp
    current_camp = "easy"
    current_enemy = easy_camp_enemy.copy()
    apply_difficulty_to_enemy(current_enemy)
    current_enemy["alive"] = True

    camp_page("Fight with Slime")
        
@ui.page('/medium_camp')
def medium_camp():
    global current_enemy, current_camp
    current_camp = "medium"
    current_enemy = medium_camp_enemy.copy()
    apply_difficulty_to_enemy(current_enemy)
    current_enemy["alive"] = True

    camp_page("Fight with Slime")
        
@ui.page('/hard_camp')
def hard_camp():
    global current_enemy, current_camp
    current_camp = "hard"
    current_enemy = hard_camp_enemy.copy()
    apply_difficulty_to_enemy(current_enemy)
    current_enemy["alive"] = True

    camp_page("Fight with Slime")

@ui.page('/game_bosses')
def game_bosses():
    with game_background():
        with ui.element('div').classes('flex flex-col gap-5 items-center'):
            ui.label("Choose boss to fight with!").classes('text-5xl font-bold')

            def boss_button(boss_id):
                boss = BOSSES[boss_id]
                defeated = boss_id in warrior["defeated_bosses"]
                text = boss["name"] + (" Defeated" if defeated else "")
                btn = ui.button(text, on_click=lambda: start_boss(boss_id)).classes(
                'bg-blue text-purple-700 font-semibold px-8 py-2 rounded-xl shadow-md hover:bg-purple-700 hover:text-white transition duration-300'
            )
                if defeated:
                    btn.disable()

            for boss_id in BOSSES:
                boss_button(boss_id)

            ui.button("Back", on_click=lambda: ui.navigate.to('/game')).classes(
                'bg-blue text-purple-700 font-semibold px-8 py-2 rounded-xl shadow-md hover:bg-purple-700 hover:text-white transition duration-300'
            )
            stats_panel()

@ui.page('/game_home')
def game_home():
    with game_background():
        with ui.element('div').classes('flex flex-col gap-5 items-center'):
            ui.label(f"Your home").classes('text-5xl font-bold text-black drop-shadow-lg')
            home_buttons = {
                "Sleep (+energy)": sleep,
                "Eat (+hp)": eat,
                "Back": lambda: ui.navigate.to('/game')
            }
            for name, func in home_buttons.items():
                    ui.button(name, on_click=func).classes(
                        'bg-blue text-purple-700 font-semibold px-10 py-3 rounded-xl shadow-lg hover:bg-purple-700 hover:text-white transition duration-300'
                    )
            stats_panel()

@ui.page('/game_shop')
def game_shop():
    with game_background():
        with ui.element('div').classes('flex flex-col gap-5 items-center'):
            ui.label(f"The greatest shop!").classes('text-5xl font-bold text-black drop-shadow-lg')
            shop_buttons = {
                "Weapons": lambda: ui.navigate.to('/shop/weapons'),
                "Armor": lambda: ui.navigate.to('/shop/armor'),
                "Rings": lambda: ui.navigate.to('/shop/rings'),
                "Back": lambda: ui.navigate.to('/game')
            }
            for name, func in shop_buttons.items():
                    ui.button(name, on_click=func).classes(
                        'bg-blue text-purple-700 font-semibold px-10 py-3 rounded-xl shadow-lg hover:bg-purple-700 hover:text-white transition duration-300'
                    )
            ui.notify("Welcome to the shop!", timeout=3000)
            stats_panel()




def sleep():
    warrior["energy"] = min(100, warrior["energy"] + 30)
    ui.notify("You slept well!")
    update_stats_panel()

def eat():
    if warrior["money"] < 5:
        ui.notify("Not enough money...")
        return
    warrior["hp"] = min(MAX_HP, warrior["hp"] + 15)
    warrior["money"] -= 5 
    ui.notify("You ate food. You heal 15hp. It costs you 5 gold", timeout=3000)
    update_stats_panel()
    
def buy_item(item_id: str):
    item = ITEMS[item_id]

    if item_id in warrior["items"]:
        ui.notify("Already owned")
        return

    if warrior["money"] < item["price"]:
        ui.notify("Not enough gold")
        return

    warrior["money"] -= item["price"]
    warrior["items"].append(item_id)

    for stat, value in item["stats"].items():
        warrior[stat] += value

    save()
    ui.notify(f"Bought {item['name']}")
    ui.navigate.reload()
    update_stats_panel()
    
def shop_category(category: str):
    @ui.page(f'/shop/{category}')
    def shop_category_page():
        buttons = {}

        for item_id, item in ITEMS.items():
            if item["category"] != category:
                continue

            owned = item_id in warrior["items"]
            title = f"{item['name']} ({item['price']} gold)"

            if owned:
                title += " Owned"
                buttons[title] = lambda: ui.notify("Already owned")
            else:
                buttons[title] = lambda i=item_id: buy_item(i)

        buttons["Back"] = lambda: ui.navigate.to('/game_shop')

        base_page(ITEM_CATEGORIES[category], buttons)

def attack():
    global warrior, current_enemy

    if not current_enemy or not current_enemy["alive"]:
        return
    
    if not spend_energy("attack"):
        return
    
    if current_enemy["hp"] <= 0:
        return
    
    dmg = calculate_damage(warrior, current_enemy)
    current_enemy["hp"] -= dmg  
    current_enemy["hp"] = max(0, current_enemy["hp"])
    
    update_enemy_stats_panel()
    
    ui.notify(f"You hit enemy for {dmg}.", timeout=3000)

    warrior["ult_charge"] += 1
    if warrior["ult_charge"] >= 5:
        warrior["ult_ready"] = True
        ui.notify("ULTIMATE READY", timeout=3000)

    if current_enemy["hp"] <= 0:
        win_battle()
        return
    enemy_attack()

def defence():
    global warrior, current_enemy
    
    BASE_DEFENCE_ENERGY_RESTORE = 15
    
    if current_enemy["hp"] <= 0:
        return

    if warrior["energy"] <= 0 and not warrior["defending"]:
        return
    
    warrior["defending"] = True
    warrior["energy"] += BASE_DEFENCE_ENERGY_RESTORE
    warrior["energy"] = min(warrior["energy"], warrior["max_energy"])
    
    ui.notify(f"+10 Energy", timeout=2000)

    update_stats_panel()
    enemy_attack()

def run_away():
    global warrior, current_camp
    
    if not spend_energy("run"):
        return
    
    if current_enemy["hp"] <= 0:
        return

    base_chance = 30 + warrior["luck"] * 3
    camp_mod = CAMP_ESCAPE_MOD.get(current_camp, 1.0)

    chance = int(base_chance * camp_mod)
    chance = min(chance, 85)

    roll = random.randint(1, 100)

    if roll <= chance:
        ui.notify(f"You escaped! ({chance}%)", timeout=2000)
        update_stats_panel()
        ui.timer(1.5, lambda: ui.navigate.to('/game_farm'), once=True)
    else:
        ui.notify(f"Escape failed! ({chance}%).", timeout=2000)
        enemy_attack()
        update_stats_panel()
        update_enemy_stats_panel()

def ultimate():
    global warrior, current_enemy
    
    if not warrior["ult_ready"]:
        return
    
    warrior["ult_charge"] += 1

    dmg = warrior["damage"] * 3 + warrior["luck"] * 2
    current_enemy["hp"] -= dmg
    current_enemy["hp"] = max(0, current_enemy["hp"])

    ui.notify(f"ULTIMATE HIT! {dmg} DAMAGE!", timeout=2000)
    update_stats_panel()
    update_enemy_stats_panel()

    warrior["ult_charge"] = 0
    warrior["ult_ready"] = False

    if current_enemy["hp"] <= 0:
        win_battle()
        return

    enemy_attack()

def calculate_damage(attacker, defender):
    return max(
        1, attacker["damage"] - defender["defence"] + random.randint(-attacker["luck"], attacker["luck"])
    )    
    
def spend_energy(action):
    global warrior, current_camp

    if action not in ACTION_ENERGY_COST:
        ui.notify(f"Unknown action {action}", timeout=2000)
        return False

    base = ACTION_ENERGY_COST[action]

    difficulty = warrior.get("difficulty", "Medium")
    game_mod = GAME_DIFFICULTY_MOD.get(difficulty, 1.0)
    camp_mod = CAMP_ENERGY_MOD.get(current_camp, 1.0)

    cost = int(base * game_mod * camp_mod)

    energy = warrior.get("energy", 0)

    if energy < cost:
        ui.notify(f"Not enough energy. Needed {cost}, have {energy}", timeout=2000)
        return False

    warrior["energy"] = energy - cost
    ui.notify(f"Spended {cost} energy", timeout=2000)
    update_stats_panel()
    update_enemy_stats_panel()
    return True

def enemy_attack(defending=True):
    global warrior, current_enemy
    
    difficulty = warrior.get("difficulty", "Medium")

    dmg = calculate_damage(current_enemy, warrior)

    if defending:
        dmg = max(1, dmg // 2)
        
    if difficulty == "Hard":
        dmg += 2
    elif difficulty == "Easy":
        dmg -= 2

    dmg = max(1, dmg)

    warrior["hp"] -= dmg
    warrior["defending"] = False
    clamp_hp(warrior)
    update_stats_panel()
    update_enemy_stats_panel()

    if warrior["hp"] <= 0:
        lose_battle()
        
def win_battle():
    global warrior, current_enemy

    if current_camp == "boss":
        boss_id = next(
            k for k, v in BOSSES.items() if v["name"] == current_enemy["name"]
        )

        warrior["defeated_bosses"].append(boss_id)
        warrior["money"] += BOSSES[boss_id]["reward"]

        ui.notify(
            f"BOSS DEFEATED! +{BOSSES[boss_id]['reward']} gold!",
            timeout=3000
        )
        update_stats_panel()

        save()
        ui.timer(2, lambda: ui.navigate.to('/game_bosses'), once=True)
        return

    reward = get_reward(int(20 * CAMP_MULTIPLIER[current_camp]))
    reward += warrior["luck"] * 2
    warrior["money"] += reward
    current_enemy["alive"] = False

    ui.notify(f"Enemy defeated! +{reward} gold!", timeout=2000)
    update_stats_panel()
    ui.timer(2, lambda: ui.navigate.to('/game_farm'), once=True)

def lose_battle():
    global warrior
    ui.notify("You died!", timeout=2500)
    warrior["hp"] = 0
    warrior["alive"] = False
    update_stats_panel()
    save()
    ui.timer(2.5, lambda: ui.navigate.to('/'), once=True)

MAX_HP = 100
def clamp_hp(warrior):
    warrior["hp"] = max(0, min(warrior["hp"], MAX_HP))

def stats_panel():
    global stat_labels
    stat_labels = {}

    with ui.element('div').classes(
        '''
        fixed top-4 left-4
        w-72 p-4
        bg-black/70
        text-green-300
        rounded-2xl
        border border-green-500
        shadow-2xl
        text-sm
        '''
    ):
        ui.label("PLAYER").classes("text-xl font-bold text-green-400")
        ui.separator()

        stat_labels["hp"] = ui.label()
        stat_labels["energy"] = ui.label()
        stat_labels["damage"] = ui.label()
        stat_labels["defence"] = ui.label()
        stat_labels["luck"] = ui.label()
        stat_labels["ult"] = ui.label()
        stat_labels["money"] = ui.label()

        ui.separator()
        ui.label("ITEMS").classes("text-green-400 font-bold")

        for item_id in ITEMS:
            stat_labels[f"item_{item_id}"] = ui.label()

    update_stats_panel()

def start_new_game():
    global warrior
    warrior = copy.deepcopy(default_warrior)
    warrior["hp"] = MAX_HP
    warrior["energy"] = 100
    warrior["alive"] = True
    warrior["ult_charge"] = 0
    warrior["ult_ready"] = False
    
    save()
    ui.navigate.to('/difficulty')

def continue_game():
    global warrior, default_warrior
    load()
    ui.navigate.to('/game')

def start_game(level):
    warrior['difficulty'] = level
    ui.navigate.to('/game')

def save_and_exit():
    save()
    ui.navigate.to('/')

def load():
    global warrior
    with open("save.json", "r", encoding="utf-8") as f:
        warrior = json.load(f)
        
def save():
    global warrior
    with open("save.json", "w", encoding="utf-8") as f:
        json.dump(warrior, f, ensure_ascii=False, indent=4)

def save_exists():
    if not os.path.exists("save.json"):
        return False
    with open("save.json", "r", encoding="utf-8") as f:
        saved_warrior = json.load(f)
    return saved_warrior.get("alive", True)

def base_page(title: str, buttons: dict):
    with game_background():
        with ui.element('div').classes('flex flex-col gap-5 items-center'):
            ui.label(title).classes(
                'text-5xl font-bold text-black drop-shadow-lg'
            )

            for name, func in buttons.items():
                ui.button(name, on_click=func).classes(
                    'bg-blue text-purple-700 font-semibold px-10 py-3'
                    'rounded-xl shadow-lg hover:bg-purple-700'
                    'hover:text-white transition duration-300'
                )

            stats_panel()
        
def start_boss(boss_id: str):
    if boss_id in warrior["defeated_bosses"]:
        ui.notify("Boss already defeated.")
        return

    global current_enemy, current_camp
    boss = BOSSES[boss_id]

    current_camp = "boss"
    current_enemy = {
        "name": boss["name"],
        "hp": boss["hp"],
        "alive": True,
        "damage": boss["damage"],
        "defence": boss["defence"],
        "luck": boss["luck"]
    }

    ui.navigate.to(f"/boss/{boss_id}")

def boss_page(boss_id: str):
    @ui.page(f"/boss/{boss_id}")
    def boss_page():
        boss = BOSSES[boss_id]

        with game_background():
            with ui.element('div').classes('flex flex-col gap-5 items-center'):
                ui.label(f"Boss fight: {boss['name']}").classes(
                    'text-5xl font-bold text-red-600 font-bold'
                )

                for name, func in {
                "Attack": attack,
                "Defence": defence,
            }.items():
                    ui.button(name, on_click=func).classes(
                        'bg-blue text-purple-700 font-semibold px-10 py-3 rounded-xl shadow-lg'
                    )
                ui.button("Run (impossible)").disable()

                ui.button("ULTIMATE", on_click=ultimate).bind_visibility_from(warrior, "ult_ready").classes(
                    'bg-blue text-purple-700 font-semibold px-10 py-3 rounded-xl shadow-lg')

                stats_panel()
                enemy_stats_panel()
                
def camp_page(title: str):
    with game_background():
        with ui.element('div').classes('flex flex-col gap-5 items-center'):
            ui.label(title).classes(
                '''
                text-5xl font-extrabold
                text-transparent bg-clip-text
                bg-gradient-to-r from-red-500 to-yellow-400
                drop-shadow-2xl
                '''
            )

            for name, func in {
                "Attack": attack,
                "Defence": defence,
                "Try to run away": run_away
            }.items():
                ui.button(name, on_click=func).classes(
                    'bg-blue text-purple-700 font-semibold px-10 py-3 rounded-xl shadow-lg'
                )

            ui.button("ULTIMATE", on_click=ultimate).bind_visibility_from(warrior, "ult_ready").classes(
                    'bg-blue text-purple-700 font-semibold px-10 py-3 rounded-xl shadow-lg'
                )

            stats_panel()
            enemy_stats_panel()
        
def update_stats_panel():
    if not stat_labels:
        return

    stat_labels["hp"].text = f"HP: {warrior['hp']} / {MAX_HP}"
    stat_labels["energy"].text = f"Energy: {warrior['energy']}"
    stat_labels["damage"].text = f"Damage: {warrior['damage']}"
    stat_labels["defence"].text = f"Defence: {warrior['defence']}"
    stat_labels["luck"].text = f"Luck: {warrior['luck']}"
    stat_labels["ult"].text = f"ULT: {warrior['ult_charge']}"
    stat_labels["money"].text = f"Gold: {warrior['money']}"

    for item_id in ITEMS:
        if item_id in warrior["items"]:
            stat_labels[f"item_{item_id}"].text = f"{ITEMS[item_id]['name']}"
        else:
            stat_labels[f"item_{item_id}"].text = ""

def apply_difficulty_to_enemy(enemy: dict):
    difficulty = warrior.get("difficulty", "Medium")
    mod = GAME_DIFFICULTY_MOD.get(difficulty, 1.0)

    enemy["hp"] = int(enemy["hp"] * mod)
    enemy["damage"] = int(enemy["damage"] * mod)
    enemy["defence"] = int(enemy["defence"] * mod)
        
def get_reward(base):
    difficulty = warrior.get("difficulty", "Medium")
    mod = {
        "Easy": 1.2,
        "Medium": 1.0,
        "Hard": 0.7
    }[difficulty]
    return int(base * mod)

def enemy_stats_panel():
    global enemy_stat_labels

    enemy_stat_labels = {}

    with ui.element('div').classes(
        '''
        fixed top-4 right-4
        w-72 p-4
        bg-black/70
        text-red-300
        rounded-2xl
        border border-red-500
        shadow-2xl
        text-sm
        '''
    ):
        ui.label("ENEMY").classes("text-xl font-bold text-red-400")
        ui.separator()

        enemy_stat_labels["hp"] = ui.label()
        enemy_stat_labels["damage"] = ui.label()
        enemy_stat_labels["defence"] = ui.label()
        enemy_stat_labels["luck"] = ui.label()

    update_enemy_stats_panel()
    
def update_enemy_stats_panel():
    if not enemy_stat_labels or not current_enemy:
        return

    enemy_stat_labels["hp"].text = f"HP: {current_enemy['hp']}"
    enemy_stat_labels["damage"].text = f"Damage: {current_enemy['damage']}"
    enemy_stat_labels["defence"].text = f"Defence: {current_enemy['defence']}"
    enemy_stat_labels["luck"].text = f"Luck: {current_enemy['luck']}"

def game_background():
    return ui.element('div').classes(
        'absolute inset-0 flex items-center justify-center'
    ).style(
        '''
        background-image: linear-gradient(180deg, #0f0c29, #302b63, #24243e);
        background-size: cover;
        background-position: center;
        overflow: hidden;
        '''
    )
    
def set_resolution(size):
    global current_window_size
    current_window_size = size

    with open("settings.json", "w") as f:
        json.dump({"window_size": size}, f)

    ui.notify("Resolution will apply after restart")

def load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as f:
            data = json.load(f)
            return tuple(data.get("window_size", (1920, 1080)))
    return (1920, 1080)

current_window_size = load_settings()

def exit_game():
    app.shutdown()
    sys.exit(0)

shop_category("weapons")
shop_category("armor")
shop_category("rings")

boss_page("big_slime")
boss_page("big_orc")
boss_page("final_boss")

def main():
    ui.run(
        native=True,
        window_size=current_window_size,
        fullscreen=False
    )
    
main()