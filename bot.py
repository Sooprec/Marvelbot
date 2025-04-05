import discord
import random
import asyncio
import os
import time
import json
from discord.ui import View, Button
from discord.ext import commands, tasks
from discord import app_commands
from flask import Flask
from threading import Thread

DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

data_lock = asyncio.Lock()
user_collection = {}
claimed_characters = {}

def get_server_data_file(guild_id):
    return os.path.join(DATA_FOLDER, f"server_{guild_id}.json")

async def save_data(guild_id):
    """Zapisuje dane użytkowników i postaci dla danego serwera."""
    async with data_lock:
        file_path = get_server_data_file(guild_id)
        data_to_save = {
            "user_collection": user_collection.get(guild_id, {}),
            "claimed_characters": claimed_characters.get(guild_id, {})
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=4, ensure_ascii=False)
            print(f"✅ Dane zapisane dla serwera {guild_id} w pliku {file_path}. Zawartość: {data_to_save}")
        except Exception as e:
            print(f"❌ Błąd zapisu danych dla serwera {guild_id}: {e}")
            
async def load_data(guild_id):
    """Ładuje dane użytkowników i postaci dla danego serwera."""
    async with data_lock:
        os.makedirs(DATA_FOLDER, exist_ok=True)  # To tworzy folder, jeśli go nie ma
        file_path = get_server_data_file(guild_id)

        print(f"Sprawdzam plik dla serwera {guild_id}: {file_path}")

        if not os.path.exists(file_path):
            user_collection[guild_id] = {}
            claimed_characters[guild_id] = {}
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump({"user_collection": {}, "claimed_characters": {}}, f, indent=4, ensure_ascii=False)
                print(f"✅ Nowy plik stworzony dla serwera {guild_id}.")
            except Exception as e:
                print(f"❌ Błąd przy tworzeniu pliku dla serwera {guild_id}: {e}")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                user_collection[guild_id] = data.get("user_collection", {})
                claimed_characters[guild_id] = data.get("claimed_characters", {})

            print(f"✅ Dane załadowane dla serwera {guild_id}.")
        except json.JSONDecodeError:
            print(f"⚠️ Błąd dekodowania JSON dla {guild_id}, inicjalizowanie pustych danych.")
            user_collection[guild_id] = {}
            claimed_characters[guild_id] = {}
        except Exception as e:
            print(f"⚠️ Błąd ładowania danych dla {guild_id}: {e}")
            user_collection[guild_id] = {}
            claimed_characters[guild_id] = {}

characters = [
    {"name": "Colossus", "image": "https://th.bing.com/th/id/R.d45dcdef66226486216bdab07cade13d?rik=%2bb%2fykXEYJirzBw&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "Ladypool", "image": "https://i.pinimg.com/736x/cc/41/97/cc41970b98ecb22db8f8b91862ddca35.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Skrull 1", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 2", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 3", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 4", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 5", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 6", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 7", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 8", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 9", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 10", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 11", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 12", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 13", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 14", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 15", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 16", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 17", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 18", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 19", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 20", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 21", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 22", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 23", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 24", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 25", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 26", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 27", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 28", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 29", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 30", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 31", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 32", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 33", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 34", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 35", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 36", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 37", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 38", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 39", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 40", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 41", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 42", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 43", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 44", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 45", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 46", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 47", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 48", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 49", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 50", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 51", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 52", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 53", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 54", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 55", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 56", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 57", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 58", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 59", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 60", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 61", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 62", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 63", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 64", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 65", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 66", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 67", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 68", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 69", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 70", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 71", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 72", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 73", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 74", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 75", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 76", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 77", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 78", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 79", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Skrull 80", "image": "https://i.pinimg.com/originals/27/a6/3f/27a63ffeebec26ff27411dc421b60173.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Frigga", "image": "https://th.bing.com/th/id/R.2683ea4d382c83fef7e072d069856f9a?rik=tcMKki6Ia2cJEQ&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "Molecule Man", "image": "https://i.pinimg.com/736x/21/4f/75/214f7543f25bc9a0c68753658559066a--molecule-man-comic-superheroes.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Ajax", "image": "https://th.bing.com/th/id/OIP.tCZDEKam1rFqfORpcZJfRgAAAA?rs=1&pid=ImgDetMain", "raity": "Rare", "chance": 0.15},
    {"name": "Alioth", "image": "https://www.dexerto.com/cdn-image/wp-content/uploads/2023/09/11/alioth-marvel-snap-featured.jpg?width=1200&quality=60&format=auto", "rarity": "Rare", "chance": 0.15},
    {"name": "America Chavez", "image": "https://marvelblog.com/wp-content/uploads/2021/12/america-chavez.jpeg", "rarity": "Rare", "chance": 0.15},
    {"name": "Ammit", "image": "https://th.bing.com/th/id/OIP.dOJiXyumZuFvlzlJtRSflQHaN6?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Ancient One", "image": "https://th.bing.com/th/id/OIP.E4lms1O8Nk4Z7CS3zjis2AAAAA?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Anubis", "image": "https://th.bing.com/th/id/OIP.yuroaPNgUt0yFWJW0Mw5NQAAAA?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Armor", "image": "https://th.bing.com/th/id/OIP.xtSC7MrzfiR2dg7y5tILrgHaLP?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Aunt May", "image": "https://th.bing.com/th/id/OIP.67qE7OKSO5ICCy4_I0v2DgAAAA?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Baron Mordo", "image": "https://i.pinimg.com/originals/f7/a5/f6/f7a5f6a899bd2218acef2f9f24cadd07.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Beta Ray Bill", "image": "https://th.bing.com/th/id/OIP.EqqtHO7L-bcSPg7bP8sxQgHaLY?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Bishop", "image": "https://i.pinimg.com/736x/90/61/ee/9061ee4f552d35f2d563f518b2a9d681.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Black Swan", "image": "https://th.bing.com/th/id/OIP.EJl44Bukc9QdJkBjNtEOhQHaLc?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Blind Al", "image": "https://comicvine.gamespot.com/a/uploads/original/3/31666/3333410-blind%20al.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Blob", "image": "https://th.bing.com/th/id/R.74fe06a2b1a0738da3c6a5f673adbf43?rik=4y36gy9vziHLow&riu=http%3a%2f%2fvignette3.wikia.nocookie.net%2fmarveldatabase%2fimages%2f7%2f76%2fFrederick_Dukes_(Earth-616)_from_All-New_X-Men_Vol_2_5_001.jpg%2frevision%2flatest%3fcb%3d20160225042614&ehk=JY6KRGyITwkG%2fwQ9lMXp3I69%2be%2fbOZ3fYnzMjYo6oMU%3d&risl=&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Cable", "image": "https://i.pinimg.com/originals/8c/a7/6d/8ca76da466892b5544e24a41675f7a37.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Cassandra Nova", "image": "https://i.pinimg.com/originals/25/60/58/256058ecf53687ec6293f45a29ac40d5.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Goose", "image": "https://th.bing.com/th/id/OIP.1kpp6uVV4mI4W73yIdxo1AHaLc?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Cloak", "image": "https://th.bing.com/th/id/OIP.FHm62wMHRDFYEpWMNOyejwHaJ7?rs=1&pid=ImgDetMain","rarity": "Common", "chance": 0.20},
    {"name": "Dagger", "image": "https://th.bing.com/th/id/OIP.FdwKBDNMzcI4OMy2bcfEYgHaJo?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Cloak And Dagger", "image": "https://pre00.deviantart.net/cb8b/th/pre/i/2017/110/d/b/cloak_and_dagger_by_chickenzpunk-db6j529.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Corvus Glaive", "image": "https://th.bing.com/th/id/R.30884f31f37944c140bf03ef16f1fce7?rik=HNMQfmarkyfceQ&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Dakken", "image": "https://th.bing.com/th/id/OIP.cbSM9GAQP8gh3YAKWkIY7wHaLP?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Dazzler", "image": "https://th.bing.com/th/id/OIP.X5OkrIhKo1P_gCBEiSUvwQAAAA?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Deathlock", "image": "https://i.pinimg.com/originals/93/86/6a/93866a81174838a591e6920701e37083.png", "rarity": "Common", "chance": 0.20},
    {"name": "Blue Marvel", "image": "https://static.tvtropes.org/pmwiki/pub/images/blue_marvel.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Cosmo", "image": "https://th.bing.com/th/id/OIP.4-bJJQNilVoom7R64YaSLgHaKH?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Zuras", "image": "https://i.pinimg.com/736x/cf/57/3f/cf573f8ebd4e12f76c4947faf007f19a.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Ikaris", "image": "https://th.bing.com/th/id/OIP.b9ZnoWRLuH4-94xKSpXRlgHaLP?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Captain Canuck", "image": "https://comicvine.gamespot.com/a/uploads/original/1/10812/7742527-canuck.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Wonder Man", "image": "https://th.bing.com/th/id/R.4853603933ba0d02ef2c0b0670408056?rik=qXKUzsAoaiCg4w&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Carnage", "image": "https://th.bing.com/th/id/OIP.wOuuWsvrwUQH6rg2EcwunAHaLH?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Dogpool", "image": "https://static.tvtropes.org/pmwiki/pub/images/dogpool.png", "rarity": "Legendary", "chance": 0.02},
    {"name": "Franklin Richards", "image": "https://th.bing.com/th/id/OIP.RSyeALKvF5u2m51aGXeBqAAAAA?rs=1&pid=ImgDetMain", "rarity": "Legendary", "chance": 0.02},
    {"name": "Gwenpool ", "image": "https://comicvine.gamespot.com/a/uploads/scale_medium/6/67663/6633324-05-variant.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Valeria Richards", "image": "https://comicvine.gamespot.com/a/uploads/scale_small/11112/111123579/7033575-valeria_richards_%2528earth-616%2529_from_fantastic_four_vol_6_10_001.jpg", "rarity": "Legendary", "chance": 0.02},
    {"name": "Spider Gwen", "image": "https://2.bp.blogspot.com/-LnSMaUsKYCw/WKzox4pYimI/AAAAAAABM7Y/-W8DWqdnDgwWgr9QwSwEEGZFj7GjonFXwCLcB/s1600/spider_gwen_by_chickenzpunk-d9w2jar.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Sentry", "image": "https://th.bing.com/th/id/R.40ba3e2c0fd1e9c81a6de746cb87e0ef?rik=hk%2f9KffAbceFiA&riu=http%3a%2f%2fpm1.aminoapps.com%2f6565%2fa5eabcb59735277fcea3dab4aa01cf41024867d3_00.jpg&ehk=clvapp%2bWk8eL2M0VNT7gzZHTcvHNwGHWoo%2b0rhisEvw%3d&risl=&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Iron Man", "image": "https://th.bing.com/th/id/OIP.KWzuNXbEfSmcBj7Vc_ZdzAHaLE?rs=1&pid=ImgDetMain", "rarity": "Legendary", "chance": 0.02},
    {"name": "Spider-Man", "image": "https://th.bing.com/th/id/R.6d5275caa41a9a7a496ad7e973d88939?rik=jYP6ATpyJVEXQw&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Thor", "image": "https://i.pinimg.com/originals/df/f1/dd/dff1ddc600819e5f1aa8e95a788d5584.jpg", "rarity": "Legendary", "chance": 0.02},
    {"name": "Hulk", "image": "https://i.pinimg.com/originals/4a/bc/a8/4abca8abdfda6359581be1153434266f.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Jeff the Land Shark", "image": "https://www.laughingplace.com/w/wp-content/uploads/2021/11/jeff-the-land-shark-gets-in-on-thanksgiving-fun-in-a-new-infinity-comic.jpeg", "rarity": "Legendary", "chance": 0.02},
    {"name": "Red She Hulk", "image": "https://i.pinimg.com/originals/79/c4/fa/79c4faf96d00c4523c4f3872f5f7961f.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "The Rose", "image": "https://th.bing.com/th/id/OIP.yz_uF7X4-e6llZjkR7LWAQHaI-?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Scream", "image": "https://th.bing.com/th/id/R.3e9a2a5e4dab41121f1bcfb75596e64c?rik=HT%2fDSJYGMbkHLQ&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "Scarlet Spider", "image": "https://th.bing.com/th/id/R.040fab53e158550216dfd80801da5c0e?rik=hOKTNWy5xxoDzA&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Sandman", "image": "https://i.pinimg.com/736x/3e/87/8c/3e878cc8757509de5944eb1f65d65061.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Black Widow", "image": "https://artfiles.alphacoders.com/134/thumb-1920-134089.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Quick Silver", "image": "https://th.bing.com/th/id/OIP.BEqKKjRR-0a9hVNKkkYFkwHaLY?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "She Hulk", "image": "https://www.ixpap.com/images/2022/08/She-Hulk-Wallpaper-768x1365.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Speed", "image": "https://th.bing.com/th/id/OIP.EXGtvWk2aPsmlZ8GtPEPUgAAAA?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Ikon", "image": "https://th.bing.com/th/id/R.a31892792de6d8d58aacc3f4f45281ba?rik=yuTzVwg34rkkSg&riu=http%3a%2f%2fimg1.wikia.nocookie.net%2f__cb20140117061457%2fmarveldatabase%2fimages%2f9%2f9c%2fIkon_(Earth-616)_from_Infinity_Vol_1_1_0002.jpg&ehk=1zuIW9yiSsYBG5m%2fP6CzMOBvABgytdMyd731Q9FGA3g%3d&risl=&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Blackbolt", "image": "https://th.bing.com/th/id/R.a42416674ff68d73c56d7557a53ebe23?rik=ZX2ptM9122W6fA&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Jigsaw", "image": "https://vignette.wikia.nocookie.net/marveldatabase/images/3/36/Billy_Russo_(Earth-616)_from_Punisher_Vol_8_9_001.jpg/revision/latest?cb=20160425134716", "rarity": "Rare", "chance": 0.15},
    {"name": "Iceman", "image": "https://th.bing.com/th/id/R.5ba5f2fcd3a16b84f4095e1be79da04b?rik=hC%2bc5D396vjMLw&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "Apocalypse", "image": "https://i.pinimg.com/736x/6e/9e/7f/6e9e7fa73121ae64740d7a3725f1b9a2.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Atum", "image": "https://th.bing.com/th/id/OIP.I6tZdKbNLriY5-FxPTPFGgHaLY?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Banshee", "image": "https://comicvine.gamespot.com/a/uploads/scale_medium/10/100647/6876875-banshee.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Wiccan", "image": "https://th.bing.com/th/id/OIP.QtyteE45-LIDZUma_JckdAAAAA?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Shuri", "image": "https://th.bing.com/th/id/OIP.Rookmzfyn0EQtOGHH7gxVwHaLY?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Namor", "image": "https://i.pinimg.com/originals/91/d4/e8/91d4e814eabf9ec3a437a35f011263cf.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Ronan", "image": "https://th.bing.com/th/id/OIP.xHJnd780Gci2tyJTLJm0NwHaLH?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Captain Marvel", "image": "https://th.bing.com/th/id/OIP.5b0Y4EefcXLBTyPq9kVxGAHaJ4?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Photon", "image": "https://th.bing.com/th/id/OIP.zRK28WhQxxujnsMCKwAUWQHaLS?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Ms Marvel", "image": "https://th.bing.com/th/id/OIP.l_sfi9nI_H1yzecjTYjDaQHaLc?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Falcon", "image": "https://th.bing.com/th/id/R.16963ff2ee71feba4ccddf2f7a4d626c?rik=xCOrCK4pwD1ekA&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "Doctor Strange", "image": "https://i.pinimg.com/474x/10/a7/b1/10a7b1800dbcc4829e1c1244149d33ae.jpg", "rarity": "Legendary", "chance": 0.02},
    {"name": "White Widow", "image": "https://th.bing.com/th/id/OIP.KQeokmEc5pQw5ki6XSEKhQAAAA?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Domino", "image": "https://th.bing.com/th/id/OIP._0KI8RugK62z8biBvc8J0QHaMS?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Kraglin", "image": "https://th.bing.com/th/id/OIP.P7EtPB0dAm87NUi5zXSsIQAAAA?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Dracula", "image": "https://pm1.narvii.com/6478/6bfa48fe53c52100c09284d4338c8c609c85e7c8_hq.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Ebony Maw", "image": "https://th.bing.com/th/id/R.c969afb64e76495b71498e1a1a1eeacb?rik=%2fG5rzT3ZxEw7ZA&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Maya Lopez", "image": "https://th.bing.com/th/id/OIP.P79Ny8V06bGMZGv5WHaxngHaLZ?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Ego", "image": "https://i.pinimg.com/originals/cc/36/ec/cc36ec43b1f3af22e289157940a334d4.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Elsa Bloodstone", "image": "https://th.bing.com/th/id/OIP.ijIjFQl-fFaQH8l3a1P6QwAAAA?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Enchantress", "image": "https://th.bing.com/th/id/R.f36fa34053fc64caea3528e08196fab0?rik=92GJi73O2a%2bzOw&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Killmonger", "image": "https://cdn.marvel.com/content/1x/black_panther_2018_19_king_killmonger.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Fin Fang Foom", "image": "https://i.pinimg.com/originals/d2/65/c1/d265c1a5eab1e3db1cce386b83c88028.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Forge", "image": "https://th.bing.com/th/id/R.66cc0a22965694df68ce85d03630e0ed?rik=O%2fPTXQTeZdhqJA&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Freya", "image": "https://comicvine.gamespot.com/a/uploads/original/11174/111743093/8944511-1584993690-346.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Black Panther", "image": "https://th.bing.com/th/id/R.216461b194d3e1047b817b87a3b1c6f8?rik=Pq1FVVxB7n4Ttw&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Captain America", "image": "https://th.bing.com/th/id/R.75a03cc4f37b53acfa5e9b597dad2074?rik=tVyenelo9lPawA&riu=http%3a%2f%2ffc04.deviantart.net%2ffs70%2fi%2f2012%2f203%2f6%2f2%2fcaptain_america_by_asylumcomics-d5883ay.jpg&ehk=erNg0BQzIkQ0ZnLhwhAzBx0iuYI7QCFIsWodrD6%2bfGI%3d&risl=&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Scarlet Witch", "image": "https://th.bing.com/th/id/R.4757b3aa9482ad9ce69cf549f9e4b2e2?rik=c2b4Z7VocXmtog&riu=http%3a%2f%2fcomichomeworld.com%2fwp-content%2fuploads%2f2017%2f02%2fSW.jpg&ehk=S%2fVyJwnAMl5MnIxK%2fN2uNIdU8fNBVY8bL0WpFkF%2bGLc%3d&risl=&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Deadpool", "image": "https://2.bp.blogspot.com/WP0bDIVX4x69MytzjdWErt9ECmVz8vFdFTDmf-iKGtqdw_zok6x_43uph97uV9mN1WRoXAgun7A=s0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Loki", "image": "https://th.bing.com/th/id/R.5364760e864cd36df5fb8fa4389fcf06?rik=sQ69xii57%2f5tkA&riu=http%3a%2f%2fimages6.fanpop.com%2fimage%2fphotos%2f43700000%2f-Loki-marvel-comics-43724754-1296-1797.jpg&ehk=fo36%2f%2fdSj9rvq3%2bbS%2fGuAPFlRBuadp5S8OfYiqOMt1Q%3d&risl=&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Thanos", "image": "https://th.bing.com/th/id/OIP.kt5nmgsNe9FnVkZ6qp5Y5QHaLP?rs=1&pid=ImgDetMain", "rarity": "Legendary", "chance": 0.02},
    {"name": "Venom", "image": "https://static.tvtropes.org/pmwiki/pub/images/venom2018001_cov.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "The Watcher", "image": "https://i.pinimg.com/736x/42/e3/75/42e3755e10f0375852352cf830c64df0.jpg", "rarity": "Legendary", "chance": 0.02},
    {"name": "Wolverine", "image": "https://th.bing.com/th/id/R.0ea97367eacbc4c66b8c88a5061fcade?rik=KWGmcZPXA2xx3Q&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Magneto", "image": "https://th.bing.com/th/id/OIP.yu3iyvGzm3Wsrr9p2ZIYkAHaLJ?rs=1&pid=ImgDetMain", "rarity": "Legendary", "chance": 0.02},
    {"name": "Storm", "image": "https://i.pinimg.com/originals/ea/c2/d0/eac2d00bd069b9bb981ee78bd90eb578.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Destroyer", "image": "https://th.bing.com/th/id/R.50f932bb468f082b47b13c3229d67988?rik=1Xvh3c%2faqx0AoA&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "Jean Grey", "image": "https://th.bing.com/th/id/R.8b4b0ca977aa1eeaea06b21c937e8c1a?rik=eG0I8DS1kXRDIg&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Taweret", "image": "https://th.bing.com/th/id/OIP.j5DNQh9Xvz6w91nMgNCVYQAAAA?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "John Walker", "image": "https://th.bing.com/th/id/R.79140a7bf2b12cccfc003695e2902a62?rik=sGp0t6IRDfGc7A&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Valkyrie", "image": "https://th.bing.com/th/id/R.79da9ae41bee6f27028fff8ebb4609a1?rik=zeOVmn%2bJm8wShQ&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "Vanessa Fisk", "image": "https://th.bing.com/th/id/OIP.6vsVHw1pNWWysY7M5RTqKgAAAA?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Viper", "image": "https://i.pinimg.com/originals/cd/2f/f0/cd2ff09ee13463e865dd74b64d5ead70.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Volstagg", "image": "https://th.bing.com/th/id/R.a59746e3633ab7a76dcf9afb256b690d?rik=No123b5gwMD1cw&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Crystal", "image": "https://vignette.wikia.nocookie.net/p__/images/9/97/War_of_Kings_Warriors_Vol_1_2_Textless.jpg/revision/latest?cb=20150111192413&path-prefix=protagonist", "rarity": "Rare", "chance": 0.15},
    {"name": "Nick Fury", "image": "https://comicvine.gamespot.com/a/uploads/scale_small/12/124259/8820211-ezgif-1-a0ae1e5c49.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Agent Carter", "image": "https://vignette.wikia.nocookie.net/wwcbm/images/3/3f/Peggy_Carter_comics_crop.jpg/revision/latest?cb=20170929184713", "rarity": "Common", "chance": 0.20},
    {"name": "Captain Britain", "image": "https://th.bing.com/th/id/OIP.eoITQ3oYQQveiVx-VYTAnwHaLK?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Cyclops", "image": "https://th.bing.com/th/id/OIP.Zreosut-e2RCHUiNpBad5gHaLP?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Rogue", "image": "https://th.bing.com/th/id/OIP.rkiSQE-DWDQNCi2TO8rnfgHaLU?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Gambit", "image": "https://i.pinimg.com/originals/7b/76/90/7b7690f4b4f58babec4b1939a6b0955e.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Beast", "image": "https://i.pinimg.com/originals/f4/ea/b8/f4eab830c1d4a229a39060c347fa7b8f.png", "rarity": "Rare", "chance": 0.15},
    {"name": "Benjamin Parker", "image": "https://vignette.wikia.nocookie.net/marveldatabase/images/8/89/Benjamin_Parker_(Earth-11638)_from_Amazing_Spider-Man_Annual_Vol_1_38_0001.jpg/revision/latest?cb=20110426053122", "rarity": "Common", "chance": 0.20},
    {"name": "Ben Urich", "image": "https://th.bing.com/th/id/R.54b285107d0cd6d26e7ef8019a74e95d?rik=R7Fx1a6P99NHsg&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Beyonder", "image": "https://th.bing.com/th/id/R.94bae2dac53bc831eb0eecec2f1f0d36?rik=LOFXLf9Y11w44A&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "Black Dwarf", "image": "https://th.bing.com/th/id/OIP.6pXSsWEsgVNmXrgWWrXoTwAAAA?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Blink", "image": "https://th.bing.com/th/id/R.d53dfc8bf305ada46373241f66c3d46b?rik=7zi2ZcdMW3fAMw&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Collen Wing", "image": "https://www.tebeosfera.com/T3content/img/T3_personajes/7/4/collen_wing_marvel_1974.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "The Collector", "image": "https://th.bing.com/th/id/R.ae29e6f41ce4e7e1b1f938608f5cf6dd?rik=LGgZBGjY%2fMUCkQ&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "Corvus Glaive", "image": "https://vignette.wikia.nocookie.net/wwcbm/images/9/9e/Corvus_Glaive_comics_crop.jpg/revision/latest?cb=20171113172907", "rarity": "Common", "chance": 0.20},
    {"name": "Nightcrawler", "image": "https://th.bing.com/th/id/OIP.9PULv7rjEJZHZ3HvkwN45QHaLP?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Juggernaut", "image": "https://th.bing.com/th/id/OIP.UHL6LngNsSkOBRcWT6n7awHaLd?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Kang the Conqueror", "image": "https://i.pinimg.com/736x/0d/43/70/0d4370ffc5084c5a4f9fed604d008461.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Khonshu", "image": "https://th.bing.com/th/id/OIP.qBcwldcqFmEfD9wTvIVfjwHaKe?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Knull", "image": "https://i.pinimg.com/736x/22/10/06/22100649ac60489e20ac5901d0c0a24a.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Psylocke", "image": "https://th.bing.com/th/id/OIP.3CMB8XOdURN5CoiByS2HbQHaK0?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Legion", "image": "https://th.bing.com/th/id/OIP.QW-FB0o5lwB1h4ismnYZGwAAAA?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Lilith", "image": "https://i.pinimg.com/736x/9c/1f/e0/9c1fe0189f0ebd40d4b99cffd585be39.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Luna Snow", "image": "https://cdn.marvel.com/content/1x/future_fight_firsts_luna_snow_2019_1.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "M.O.D.O.K", "image": "https://th.bing.com/th/id/R.8a893496d14f00a94fb1a848bb861894?rik=5RAB3mLbRzMAnA&riu=http%3a%2f%2f1.bp.blogspot.com%2f-h0B25SPWusM%2fVTHPpbr7QFI%2fAAAAAAAAJ38%2f6zq_QfGsIik%2fs1600%2fDavid_Finch_-_MODOK_vs._Hulks.jpg&ehk=eJahJmDQES%2bsjNOKpqhUiZy%2bSSdNX4U7Kf8l8N6MwA8%3d&risl=&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Madam Web", "image": "https://th.bing.com/th/id/OIP.ZCkK0tR3jBG47K7BcfPlcAAAAA?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Madelyne Pryor", "image": "https://i.pinimg.com/736x/4f/e9/b9/4fe9b94dd8dccebcd002452ade913269.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Man Thing", "image": "https://i.pinimg.com/originals/51/99/0f/51990f4f8d3a30ced07a54904c1817d2.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Medusa", "image": "https://i.pinimg.com/originals/09/a0/9e/09a09ed8afea25848495db7461866927.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Korg", "image": "https://th.bing.com/th/id/OIP.BK7I7YG1W7AFG-Hz0K73mAHaKn?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Professor X", "image": "https://th.bing.com/th/id/OIP.tSUFl0CKErOXAUf8f_AaCAAAAA?rs=1&pid=ImgDetMain", "rarity": "Legendary", "chance": 0.02},
    {"name": "Silver Surfer", "image": "https://th.bing.com/th/id/R.917963c584a3c94ef01605176bb5fbd0?rik=eaLSckEkdVsv9g&riu=http%3a%2f%2fimg3.wikia.nocookie.net%2f__cb20140502162102%2fmarvel-comics%2fde%2fimages%2f9%2f92%2fSilver_Surfer.jpg&ehk=iJWo5VEYHG2Hdfip1HRc8NJvXfEXAQRvE7Uq42JpQJ0%3d&risl=&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Daredevil", "image": "https://th.bing.com/th/id/OIP.-iE_v4Oiyvt1MjTotKzuSAHaLY?rs=1&pid=ImgDetMain", "rarity": "Legendary", "chance": 0.02},
    {"name": "Daredevil (Black Suit)", "image": "https://i.pinimg.com/originals/21/53/fa/2153fa707711e553f25807f93a0b78f1.jpg", "rarity": "Legendary", "chance": 0.02},
    {"name": "Jessica Jones", "image": "https://th.bing.com/th/id/OIP.ldvaxk9BlAeQbXbdMVM8GwHaLQ?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "The Punisher", "image": "https://th.bing.com/th/id/R.9c1bd5785a4aa44999e437a3f1a48b66?rik=PlTpxqd03qvKhg&riu=http%3a%2f%2fdiskingdom.com%2fwp-content%2fuploads%2f2015%2f10%2fThe_Punisher_1_Maleev_Variant.jpg&ehk=120N7V3a8Zo0D%2ff7OQaNqYgMUcRG%2fKQ6%2fhC9UDkrCqo%3d&risl=&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Ghost Rider", "image": "https://wallpaperaccess.com/full/2981574.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Wasp", "image": "https://vignette.wikia.nocookie.net/powerlisting/images/d/d5/Janet_van_Dyne_(Earth-616).jpg/revision/latest?cb=20140719054808", "rarity": "Rare", "chance": 0.15},
    {"name": "Giant Man", "image": "https://i.pinimg.com/474x/40/58/06/405806614d342546de2aa8f69d298ffc--hank-pym-marvel-heroes.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Moon Knight", "image": "https://th.bing.com/th/id/OIP.3xA6NVPzPJTa6Mbm_uhETQHaLN?rs=1&pid=ImgDetMain", "rarity": "Legendary", "chance": 0.02},
    {"name": "Hawkeye", "image": "https://th.bing.com/th/id/OIP.qo_STSI-fdo6LwXo_J72eAHaJ8?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Ant-Man", "image": "https://th.bing.com/th/id/R.8d79c19f3b6069d4f33c65f84898a965?rik=KomONd5EmGjlwg&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Vision", "image": "https://th.bing.com/th/id/R.3fd34e23eebe0d0d4f53a45c8165c4d1?rik=3bQ26P8N8qNVjQ&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "Black Cat", "image": "https://i.pinimg.com/originals/82/19/0b/82190ba09b417aaebec1c8d8b83f0818.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Shang-Chi", "image": "https://i.pinimg.com/originals/19/16/5f/19165f71679bc2d444ef286d9e15506b.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Star-Lord", "image": "https://i.pinimg.com/originals/c9/98/1a/c9981adfe6ac7f8f5489528320e8483b.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Gamora", "image": "https://thecomicbooksanctum.files.wordpress.com/2023/04/gamora_zen_whoberi_ben_titan_28earth-752829_from_guardians_of_the_galaxy_vol_6_13_cover_001.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Rocket Raccoon", "image": "https://th.bing.com/th/id/OIP.z1yl8yEqh2BibTY7DudtSQHaLY?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Groot", "image": "https://th.bing.com/th/id/OIP.2EslN_kzhMuQKo1eHrxPqQHaLP?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Sprite", "image": "https://th.bing.com/th/id/OIP.4Fs5KJg5ewyGXWfo1r4xRAAAAA?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Ajak", "image": "https://th.bing.com/th/id/OIP.14UgIO217HwKWXrRXgnNLAAAAA?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Sersi", "image": "https://th.bing.com/th/id/OIP.xRkNpBJfMJc3kKdqjlx_hQHaLb?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Makkari", "image": "https://thecomicbooksanctum.com/wp-content/uploads/2021/11/makkari_earth-616_from_eternals_celestia_vol_1_1_blake_variant.jpg?w=480", "rarity": "Epic", "chance": 0.05},
    {"name": "Thena", "image": "https://i.pinimg.com/originals/32/e7/bf/32e7bf68e95b1ae0e933e9fcc80ce64a.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Domo", "image": "https://th.bing.com/th/id/OIP.3pq4zKaUx2VAkU3sWr5BSAAAAA?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Phastos", "image": "https://th.bing.com/th/id/R.63428a265cab66c1e1456d11a22da9cc?rik=6JrWvKXdhenYYQ&riu=http%3a%2f%2fimg1.wikia.nocookie.net%2f__cb20130619065805%2fmarveldatabase%2fimages%2fa%2fa7%2fPhastos_(Earth-616)_from_X-Men_Vol_3_14.jpg&ehk=4jldvP95UQqBO%2fYIRHb6ddihZQDwlSFn10or0sxS6wM%3d&risl=&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Druig", "image": "https://th.bing.com/th/id/OIP.B01YgyJ7XmWsfqYfZ5bzIAHaLX?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Drax", "image": "https://i.pinimg.com/originals/f9/fc/1f/f9fc1f7e53bd79a8f5c54b319ddf7030.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Nebula", "image": "https://th.bing.com/th/id/R.3219741d343b742eb7a642f83a2b2e7b?rik=nTlYfujHM6QzIQ&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "Winter Soldier", "image": "https://i.pinimg.com/originals/2e/96/ee/2e96ee5904f3dff8b4e28751e37dc79c.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Mantis", "image": "https://th.bing.com/th/id/OIP.1-GMJcSSZC7RJKyjlUmTEAAAAA?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Doctor Doom", "image": "https://th.bing.com/th/id/R.8f12d6ee4d3f623112aafc1786ad2380?rik=Vy397KXUILOb8w&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Green Goblin", "image": "https://th.bing.com/th/id/R.a2a47e04eeccc870e39640d957919b6a?rik=7XKnL6hzUn637g&riu=http%3a%2f%2f3.bp.blogspot.com%2f-AU_L34EEHjI%2fVb1ZJNme3DI%2fAAAAAAAAhx8%2f1UsaK-oIl_I%2fs1600%2f74f6d8baaa80ea32fb7206e4055064e0.jpg&ehk=iSEEQ%2f8umBNywKHgcGvwZXo0yunimm8ZlwQyP6ynUUE%3d&risl=&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Kingpin", "image": "https://th.bing.com/th/id/OIP.2Ps9Z3HjVq8kEqP-4RKGngHaNn?w=1232&h=2264&rs=1&pid=ImgDetMain", "rarity": "Legendary", "chance": 0.02},
    {"name": "Ultron", "image": "https://freshcomics.s3.amazonaws.com/issue_covers/JAN130630_2.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Baron Zemo", "image": "https://th.bing.com/th/id/R.6c9b260a4831c287e560b640c397064f?rik=D%2fFABfX82myUYg&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Red Skull", "image": "https://th.bing.com/th/id/R.aa36d5bb3b9cffad5b79d1469b86819d?rik=rZvpPslACHHz7A&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Taskmaster", "image": "https://comicvine.gamespot.com/a/uploads/scale_medium/12/124259/8175165-screenshot2021-09-29201322.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Electro", "image": "https://th.bing.com/th/id/OIP.KYVrJ8Zo6OKtFLazIen-eQHaJL?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Rhino", "image": "https://comicvine.gamespot.com/a/uploads/scale_medium/12/124259/8059019-amazing_spider-man_vol_5_14_textless.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Vulture", "image": "https://th.bing.com/th/id/R.e9d1dc3a68da292be730df3328e22a11?rik=IjiGHOCZwnNTBw&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "War Machine", "image": "https://th.bing.com/th/id/OIP.KHt25Ilb1tE_3um8QKB5YgHaLP?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Werewolf by Night", "image": "https://th.bing.com/th/id/OIP.rvVpzZclQRg10TlYEGjUqQHaLP?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Yondu", "image": "https://th.bing.com/th/id/R.e43715ecd1a3ee1e4969b64483d6b37d?rik=2an1H7eKtZc1DA&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Itsy Bitsy", "image": "https://th.bing.com/th/id/R.7e814a4b0628575bf037ba2deac33cbe?rik=Hk7vcSNZYJxzmA&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "Wolfsbane", "image": "https://th.bing.com/th/id/R.64ee3a572a5b0ad05b3f923f7f5c207a?rik=gABr91Xm3%2b09xw&riu=http%3a%2f%2fvignette4.wikia.nocookie.net%2fmarveldatabase%2fimages%2fc%2fcb%2fRahne_Sinclair_(Earth-616)_from_X-Factor_Vol_1_258.jpg%2frevision%2flatest%3fcb%3d20130618173349&ehk=fqaVjQfedMVqGMbI3m5Fp6LeBzqLJ7v9n2OV8VWEA70%3d&risl=&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Shocker", "image": "https://th.bing.com/th/id/OIP.NAmXymrupnddfXTjc9jO3AHaLH?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Scorpion", "image": "https://th.bing.com/th/id/OIP.WKzcU3IT6_pTnYGL5eq9AwHaLZ?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Agent 13", "image": "https://i.pinimg.com/originals/d9/ca/84/d9ca8405f9bb09498bf038bda9f731b0.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Sif", "image": "https://th.bing.com/th/id/OIP.fb3N6UJ2_DYBlcrjlFvfTgHaLh?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Silk", "image": "https://th.bing.com/th/id/R.0c705536d393bcfff8ee619f464ded06?rik=xI%2butE90f8xHgA&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Captain America (Sam Wilson)", "image": "https://i.pinimg.com/736x/06/37/c9/0637c95ab18313c213a1172f252c36d5--comic-books-comic-art.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Singularity", "image": "https://comicvine.gamespot.com/a/uploads/scale_medium/6/62795/5124971-singularity.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Old Man Logan", "image": "https://th.bing.com/th/id/OIP.5BtISVFMC5TrdFlZM5EqQQHaLc?rs=1&pid=ImgDetMain", "rarity": "Legendary", "chance": 0.02},
    {"name": "Wolverine (Age of Apocalypse)", "image": "https://i.pinimg.com/originals/db/61/d5/db61d50efd2b870909ffc912a3068eda.jpg", "rarity": "Legendary", "chance": 0.02},
    {"name": "Deadpool 2099", "image": "https://th.bing.com/th/id/R.efef7e5023ebca1731793d053d0873ec?rik=z1mj7NST8mJrcA&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Weapon X", "image": "https://th.bing.com/th/id/R.2dd4547064cfca7444829616d8c177f8?rik=oSixlGf4tApnCg&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Ultimate Thor", "image": "https://th.bing.com/th/id/R.a17d8ec18b1dbea896193694edb7bf0e?rik=BvUVazZCK48SHQ&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "King Thor", "image": "https://th.bing.com/th/id/OIP.YRSjaRS7cDyBCqgANJGNQAHaLQ?rs=1&pid=ImgDetMain", "rarity": "Legendary", "chance": 0.02},
    {"name": "Cosmic King Thor", "image": "https://i.pinimg.com/736x/01/63/26/01632613e4fdc9932ff85c8e757c9965.jpg", "rarity": "Legendary", "chance": 0.02},
    {"name": "Black Knight", "image": "https://th.bing.com/th/id/OIP.q-6O8SKljM8MPFEKWe9CbQAAAA?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Poison Wolverine", "image": "https://th.bing.com/th/id/R.f1fe73d007a5c6d1b11e8fcd529aafb7?rik=wjvAs0UyBv%2b8wg&riu=http%3a%2f%2fwww.marvunapp.com%2fAppendix8%2fearth17952poiswolv1.jpg&ehk=VstrgJCbvKs0hJJSCxTPyTpiW%2br5v5l73jAqoD5hQMU%3d&risl=&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Wolverine Patch", "image": "https://th.bing.com/th/id/OIP.MZjKAoNxCFYtKsmLBBqsyQHaLP?rs=1&pid=ImgDetMain", "rarity": "Legendary", "chance": 0.02},
    {"name": "Mr.Knight", "image": "https://th.bing.com/th/id/R.99f46f932365c1db263f2d4766571070?rik=AvErdWRnvVaGCA&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Moon Knight 2099", "image": "https://comicvine.gamespot.com/a/uploads/scale_small/6/67344/1781928-880788_moon_knight_super.jpg", "rarity": "Legendary", "chance": 0.02},
    {"name": "Bruce Banner", "image": "https://th.bing.com/th/id/OIP.kqAlFuT_cQGgD0j3s9lWyAHaKl?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "The Punisher 2099", "image": "https://i.pinimg.com/originals/ba/ff/d8/baffd8bc1f0b52c39662d5d8c95c4489.jpg", "rarity": "Legendary", "chance": 0.02},
    {"name": "The Punisher (MAX Universe)", "image": "https://th.bing.com/th/id/R.2356c24641dea03d87e9ef41d9a5dcb9?rik=ZJ7wDX6ONoWZzQ&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Elektra (Daredevil)", "image": "https://th.bing.com/th/id/R.93ad92a8cc4be2c85b45a55418a3a800?rik=L9u6DimZoVhXIQ&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Shelton Pendergrass", "image": "https://static.wikia.nocookie.net/marveldatabase/images/9/9f/Shelton_Pendergrass_%28Earth-200111%29_from_Punishermax_Vol_1_9_001.jpg/revision/latest?cb=20110417014254", "rarity": "Epic", "chance": 0.05},
    {"name": "Deadpool Ultimate", "image": "https://th.bing.com/th/id/R.a47f274311c6b3a7f7f34e8333289688?rik=Fwe%2f1TFuaMTASw&riu=http%3a%2f%2fimages4.fanpop.com%2fimage%2fphotos%2f14700000%2fDeadpool-marvel-comics-14714060-550-824.jpg&ehk=NkabP8S2lkAOXa%2b5KC22po0mifs9P3cK6TicJoWaWNg%3d&risl=&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Ronin", "image": "https://th.bing.com/th/id/OIP.21j2Y43uUYtUbCZSz8ACsQHaM_?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Hulkbuster", "image": "https://th.bing.com/th/id/OIP.dzB9YHWL75-qozw5aB9KjAHaLY?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Ultimate Iron Man", "image": "https://th.bing.com/th/id/R.73ad6c9f304a787f096f7fd9a6ac56de?rik=e8mJ5dztYSkv7Q&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Superior Iron Man", "image": "https://th.bing.com/th/id/OIP.55-QMdXaw4603ot3tjZe4AHaKX?rs=1&pid=ImgDetMain", "rarity": "Legendary", "chance": 0.02},
    {"name": "Iron Hammer", "image": "https://i.pinimg.com/736x/48/75/ae/4875ae00e6a4bae05b5d21482acd2375.jpg", "rarity": "Legendary", "chance": 0.02},
    {"name": "Skarr", "image": "https://th.bing.com/th/id/OIP.InHChk2GtfIK6N-pkRS1WQAAAA?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Spider Women", "image": "https://vignette.wikia.nocookie.net/marveldatabase/images/5/50/Spider_Woman_01.jpg/revision/latest?cb=20140812143603", "rarity": "Common", "chance": 0.20},
    {"name": "Spider Man (Miles Morales)", "image": "https://th.bing.com/th/id/R.0fc2cb7d17d0b6c92350600754f93ba8?rik=0529tnYKJ%2f15bA&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Spider Man 2099", "image": "https://th.bing.com/th/id/R.0fc2cb7d17d0b6c92350600754f93ba8?rik=0529tnYKJ%2f15bA&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Spider Man Noir", "image": "https://th.bing.com/th/id/R.92e6816a86885cb3f4fb0e4a0790cdd7?rik=O7BgGeP9qOnyCQ&riu=http%3a%2f%2fimg2.wikia.nocookie.net%2f__cb20140825064601%2fmarveldatabase%2fimages%2fc%2fc3%2fEdge_of_Spider-Verse_Vol_1_1_Textless.jpg&ehk=WM3u0BxW%2f%2b64amVQXnM3T1MQjoLH1YdvMtXdBRkQHFg%3d&risl=&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Spider Punk", "image": "https://th.bing.com/th/id/R.062bc25c44d87f3a159e3abe77e53e47?rik=CoQjn8fCU8zkiQ&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Lady Loki", "image": "https://i.pinimg.com/736x/d4/3a/8d/d43a8dfdfefc09a1dd23ae638e498bfa--loki-marvel-thor.jpg", "rarity": "Legendary", "chance": 0.02},
    {"name": "Hela", "image": "https://th.bing.com/th/id/OIP.D-mmKK6U7_rxwPEbJ0IWbQHaLc?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Dormammu", "image": "https://th.bing.com/th/id/R.c8caebe3e7e449a03abe5fe8f350d0ab?rik=6xjVc1ptsHvQ2A&riu=http%3a%2f%2f2.bp.blogspot.com%2f-z-q3f3PU1Lw%2fVSv7BBzB4jI%2fAAAAAAAAHf8%2flp7ooYGHZHo%2fs1600%2fdormammu_wallpaper_by_amrock-d496r1s.jpg&ehk=WgN97NaaKNCZ9vEyaxIMgkdIiENRbWENGKNLherNkco%3d&risl=&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Bullseye", "image": "https://th.bing.com/th/id/R.4c84e4e2a3e757af2aa4010439fbbe5a?rik=Tg60J1ljuTWhyg&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Kraven the Hunter", "image": "https://i.pinimg.com/originals/34/27/5b/34275b89630f7ed24837f05c3bfa1168.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Sabretooth", "image": "https://th.bing.com/th/id/R.6ba98bee54412f73e24619fad8e9dbcc?rik=gvn1%2bunoujSnSw&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "Mysterio", "image": "https://th.bing.com/th/id/R.254b165598621dcbca679036f9ae733b?rik=CBdIG8SRTBFVIg&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Morbius", "image": "https://th.bing.com/th/id/R.4ec11e7c70abb15fc4705ceb89b26abc?rik=K%2bkSVjEhXZOBZA&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Blade", "image": "https://i.redd.it/jt743emacgb41.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Morbius", "image": "https://th.bing.com/th/id/OIP.vgmrU9IL6uBuGBzTdUh8tQHaLH?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Morgan Le Fay", "image": "https://th.bing.com/th/id/OIP.xcSjeA8D-VQEjYgXgFQ81QHaK1?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Morbius", "image": "https://vignette.wikia.nocookie.net/marveldatabase/images/e/e9/Muse_%28Earth-616%29_from_Daredevil_Vol_5_11_001.jpg/revision/latest?cb=20160910221816", "rarity": "Legendary", "chance": 0.02},
    {"name": "Mystique", "image": "https://th.bing.com/th/id/OIP.MprsXtM6zEKeUYkGUHbJMAHaNK?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Okoye", "image": "https://i.pinimg.com/736x/67/98/fa/6798faa367d6269e4cc8719d65ad2eca.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Onslaughter", "image": "https://th.bing.com/th/id/OIP.a4jDUuyoNJfaBbupSrxKOAHaKl?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Pepper Potts", "image": "https://i.pinimg.com/736x/67/98/fa/6798faa367d6269e4cc8719d65ad2eca.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Polaris", "image": "https://th.bing.com/th/id/R.d4f8b7763bea4399db22afde5fdc8e50?rik=BymtWrtbcO7RQA&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "Proxima Midnight", "image": "https://th.bing.com/th/id/OIP.8P4o2-ehXfx1aSypT-7eaAHaKj?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Agent Coulson", "image": "https://th.bing.com/th/id/R.73fc9dc973f0c14b720d737582a5e6ba?rik=yx%2fVTGzU5KvalQ&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Odin", "image": "https://th.bing.com/th/id/R.f0531d46c75ad4b6e432683c70d8e5ed?rik=9cY0csoJnY8MGQ&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Negasonic Teenage Warhead", "image": "https://th.bing.com/th/id/OIP.mqYsVDpxec729GgcD5p_LgAAAA?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Angela", "image": "https://th.bing.com/th/id/R.39c3efaea259c84e5f858595284b6cbe?rik=5sRJaUMeh7pvrw&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Galactus", "image": "https://i.pinimg.com/originals/e3/24/51/e32451becf7825fb4d32fb130600bd98.jpg", "rarity": "Legendary", "chance": 0.02},
    {"name": "X-23", "image": "https://th.bing.com/th/id/OIP.YIBZRKI9f0WfF3R8K6u5OQHaLG?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Elektra", "image": "https://orig00.deviantart.net/94bd/f/2015/187/5/a/elektra_by_j_skipper-d906raj.png", "rarity": "Epic", "chance": 0.05},
    {"name": "Magik", "image": "https://i.pinimg.com/originals/e7/7b/ac/e77bacfcf2d24b19cfc0100df69f1a50.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Iron Fist", "image": "https://th.bing.com/th/id/R.7364579ca55a32e6456c67a2702797e8?rik=3a2BrSd7yw7K%2bg&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "Ghost", "image": "https://th.bing.com/th/id/R.0ad6206df17199e6209782a28955ea2f?rik=7F4JPi8sGcHOJA&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Gorr", "image": "https://th.bing.com/th/id/OIP.Lv7axnFI0LNTv5pZyfEPKAHaJ8?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Grandmaster", "image": "https://th.bing.com/th/id/R.42742ba014003a60703f853b86c6d2db?rik=cEE68Sx4pgh1Wg&riu=http%3a%2f%2fimages1.wikia.nocookie.net%2f__cb20120123231828%2fmarveldatabase%2fimages%2f4%2f4a%2fEn_Dwi_Gast_(Earth-616)_from_Avengers_JLA_Vol_1_1.JPG&ehk=xXQJgF6f45cOZlQlrQLIg%2bFtZ07Dn1VQ4acOp3Vkzjc%3d&risl=&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Happy Hogan", "image": "https://alchetron.com/cdn/happy-hogan-comics-868c3a27-a77b-40dd-9c7a-fd03e06a982-resize-750.jpg", "rarity": "Common", "chance": 0.20},
    {"name": "Hercules", "image": "https://th.bing.com/th/id/R.b39dff71721fa6aa48de0d8ae143c578?rik=x11WEkSpEQWUcw&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "High Evolutionary", "image": "https://th.bing.com/th/id/R.6f56eaffb6dc0aaa9c950a6ee2c7a329?rik=Lt%2bR%2bgIX6aUmXw&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "Luke Cage", "image": "https://th.bing.com/th/id/OIP.VQQIXTNWBrdg0F-Uz-3e1gHaLP?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Kate Bishop", "image": "https://th.bing.com/th/id/OIP.is8ae6rRekqPoFSMG7pBAgAAAA?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Doctor Octopus", "image": "https://th.bing.com/th/id/OIP.Vo3mpp0u3bP0Mos6RZsFtAAAAA?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Lady Thor", "image": "https://th.bing.com/th/id/OIP.i8PWFgrmjq-rZ8Kuv056QQAAAA?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Lady Death", "image": "https://th.bing.com/th/id/OIP.j9Z4aoJ4GNIG0iDA2rwDlwAAAA?rs=1&pid=ImgDetMain", "rarity": "Legendary", "chance": 0.02},
    {"name": "Squirrel Girl", "image": "https://i.pinimg.com/originals/31/04/c5/3104c59d38110a11b3bf35c24bd25068.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Hellcat", "image": "https://i.pinimg.com/originals/5c/6a/bb/5c6abb936b212e8899fa49d6dd3185da.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "NorthStar", "image": "https://i.pinimg.com/originals/66/c4/70/66c4704583b875c6933296de905325fc.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "Nova", "image": "https://i.pinimg.com/736x/44/f3/0d/44f30df9ce035bd9624bf13f8afea673.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Kristen McDuffie", "image": "https://th.bing.com/th/id/R.0902447043dc097640408e626baa6e69?rik=AHrpN52WnnmhvA&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Red Hulk", "image": "https://th.bing.com/th/id/OIP.Y1ttPNTZedQIymWGh6wAPQHaLP?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Karen Page", "image": "https://th.bing.com/th/id/OIP.hG-gA4QX4lyAVw6sa4-D3gHaOZ?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Foggy Nelson", "image": "https://th.bing.com/th/id/OIP.e9FCrGhCHv5tISeJOvLXFgAAAA?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "White Tiger (Ava Ayala)", "image": "https://th.bing.com/th/id/OIP.HgFVNmz9dZlpmjQCuLK1UAAAAA?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "White Tiger (Hector Ayala)", "image": "https://th.bing.com/th/id/R.22f92847c233d5156a2a25a14c19580e?rik=c4l8XjYkMByYBw&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "White Wolf", "image": "https://assets.mycast.io/characters/white-wolf-366581-normal.jpg?1574492364", "rarity": "Rare", "chance": 0.15},
    {"name": "White Tiger (Angela Del Toro)", "image": "https://www.writeups.org/wp-content/uploads/White-Tiger-Marvel-Comics-Angela-del-Toro-v.jpg", "rarity": "Rare", "chance": 0.15},
    {"name": "White Fox", "image": "https://th.bing.com/th/id/R.ed035fce2802620da2149f4ecf199d01?rik=ab0trzkJ16xiZg&pid=ImgRaw&r=0", "rarity": "Rare", "chance": 0.15},
    {"name": "Daredevil (Shadowland)", "image": "https://th.bing.com/th/id/R.3f8cf16a0956d300a10eac8ffde96bc3?rik=xk6gWG0jdU4Zfw&pid=ImgRaw&r=0", "rarity": "Legendary", "chance": 0.02},
    {"name": "Leader", "image": "https://th.bing.com/th/id/R.c26c851a615f3f7b10961d978d9ec58b?rik=TEWSbv%2f5cYigBw&riu=http%3a%2f%2fvignette3.wikia.nocookie.net%2fmarveldatabase%2fimages%2fe%2fe5%2fSamuel_Sterns_(Earth-616)_from_Incredible_Hulk_Vol_1_603.jpg%2frevision%2flatest%3fcb%3d20151225193000&ehk=sDneWOS7Ft6bKL8P5wNyNyV8H94BYEVN%2fvFGJvKrV%2fg%3d&risl=&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Abomination", "image": "https://th.bing.com/th/id/OIP.gO14pIbdjlpMZtPEfbtUmAHaJl?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Mister Sinister", "image": "https://th.bing.com/th/id/OIP.zL--ZJ1Nzc7DqBibUn06pwHaLY?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Misty Knight", "image": "https://th.bing.com/th/id/R.c8bbf4161da4a77f8b0f2cbb113aecc4?rik=lMtE07A%2beI6Rjw&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Mockingbird", "image": "https://th.bing.com/th/id/OIP.6fhIVm4NYZ6rM8zjY9yO9wHaLc?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Morph", "image": "https://th.bing.com/th/id/R.c338c163775a4e9ca0d85c69832f6f19?rik=XPpsrWsklL0hiQ&riu=http%3a%2f%2fimg1.wikia.nocookie.net%2f__cb20101014051225%2fx-men%2fimages%2f7%2f79%2fXmen6.jpg&ehk=UJeTKBxSWUJ9YtQWLDX%2fAxMzDSwnIGv5f5zIs95MdmQ%3d&risl=&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Absorbing Man", "image": "https://th.bing.com/th/id/R.ea98030e62bf4e6b81a86f89ce588f42?rik=9uw%2bykaUD39FGQ&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Adam Warlock", "image": "https://th.bing.com/th/id/OIP.D-Ih8istDmpBZwLoOf5GngHaL8?rs=1&pid=ImgDetMain", "rarity": "Epic", "chance": 0.05},
    {"name": "Spot", "image": "https://th.bing.com/th/id/R.7876d4b7f20dbcd42c85b569e03fa31e?rik=i%2bmebiCWRxOydg&riu=http%3a%2f%2fwww.marvunapp.com%2fAppendix8%2fspot_ohnnsm9.png&ehk=uoUHd7AeXnToya%2bpKXWJbhSIo9MSO8%2fERvXLvlrZsC4%3d&risl=&pid=ImgRaw&r=0", "rarity": "Common", "chance": 0.20},
    {"name": "Agatha Harkness", "image": "https://insidepulse.com/wp-content/uploads/2023/08/Agatha-Harkness-1.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Mobius", "image": "https://th.bing.com/th/id/OIP.l__rqb4DXpPgXh2gJdT7egAAAA?rs=1&pid=ImgDetMain", "rarity": "Common", "chance": 0.20},
    {"name": "Mephisto", "image": "https://th.bing.com/th/id/OIP.sDc4nRQCZd259cHJY1CZMwHaLL?rs=1&pid=ImgDetMain", "rarity": "Legendary", "chance": 0.02},
    {"name": "Aegis", "image": "https://th.bing.com/th/id/OIP.g352ih-ucr09lpCJ8n_VCAHaLk?rs=1&pid=ImgDetMain", "rarity": "Rare", "chance": 0.15},
    {"name": "Jocasta", "image": "https://i.pinimg.com/originals/2e/c3/86/2ec386a4478a6ca8d543a3f22118a2eb.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Mr.Fantastic", "image": "https://i.pinimg.com/736x/c0/d0/10/c0d01028e5dd09654509fef5aea17beb--mister-fantastic-fantastic-four-marvel.jpg", "rarity": "Epic", "chance": 0.05}, 
    {"name": "Invisible Women", "image": "https://i.pinimg.com/736x/47/b6/b6/47b6b62ee036cffb8f6c067a9ea7a6a7.jpg", "rarity": "Epic", "chance": 0.05},
    {"name": "Human Torch", "image": "https://th.bing.com/th/id/R.15cd1ebd7e695d5d238030fe4fc6ac24?rik=qRXcE%2bzb%2fhtdCA&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},
    {"name": "The Thing", "image": "https://th.bing.com/th/id/R.52969c15a1cb03d1ce2339e34d7f5328?rik=mN8dCFGaEhBfYQ&riu=http%3a%2f%2f2.bp.blogspot.com%2f-kIk6v30uBLk%2fVFJbNknBbSI%2fAAAAAAAAAMo%2fQDWdhvLGwg0%2fs1600%2fbenGrimm.jpg&ehk=C1beYfR%2fl%2bTHjYvk03NZXdPbImdbByzn%2bNs9zcIpKOY%3d&risl=&pid=ImgRaw&r=0", "rarity": "Epic", "chance": 0.05},

    ]   

user_collection = {}
user_rolls = {}
claimed_characters = {}
expired_characters = {}
spawn_channels = {}
user_claims = {}

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix="/", intents=intents)

def get_random_character(guild_id):
    unclaimed = [char for char in characters if char["name"] not in claimed_characters.get(guild_id, {})]
    if not unclaimed:
        return None
    weights = [char["chance"] for char in unclaimed]
    return random.choices(unclaimed, weights=weights)[0]

@tasks.loop(hours=1)
async def cleanup_expired_characters():
    """Usuwa postacie, które nie zostały zebrane w określonym czasie."""
    current_time = time.time()
    expired_to_remove = []

    for character_name, expiration_time in expired_characters.items():
        if current_time > expiration_time:
            expired_to_remove.append(character_name)

    for character_name in expired_to_remove:
        expired_characters.pop(character_name, None)
        claimed_characters.pop(character_name, None)
        print(f"{character_name} has expired and is now available again.")

@tasks.loop(minutes=random.randint(1, 5))
async def spawn_random_character():
    """Losowo pojawiają się postacie w ustawionych kanałach."""
    await bot.wait_until_ready()

    for guild_id, channel_id in spawn_channels.items():
        channel = bot.get_channel(channel_id)
        if not channel:
            continue  # Jeśli kanał nie istnieje, pomijamy

        character = get_random_character()

        if character['name'] in claimed_characters:
            continue  # Jeśli postać już jest zajęta, pomijamy

        embed = discord.Embed(title=f"🔥 A wild {character['name']} appears!", color=discord.Color.blue())
        embed.set_image(url=character["image"])
        embed.set_footer(text=f"Rarity: {character['rarity']}")

        message = await channel.send(embed=embed)
        await message.add_reaction("✅")  # Dodaj reakcję do przechwycenia postaci

        expired_characters[character['name']] = time.time() + 300  # Postać wygasa po 5 minutach

        def check(reaction, user):
            return user != bot.user and reaction.message.id == message.id and str(reaction.emoji) == "✅"

        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=300, check=check)

            # Przypisujemy postać użytkownikowi
            user_collection.setdefault(str(guild_id), {}).setdefault(str(user.id), [])
            claimed_characters[character['name']] = str(user.id)
            user_collection[str(guild_id)][str(user.id)].append(character)

            # Zapisujemy dane po zdobyciu postaci
            await save_data(guild_id)

            await message.reply(f"{user.mention} claimed **{character['name']}**!")

        except asyncio.TimeoutError:
            await message.reply("⏳ The character disappeared!")

@bot.event
async def on_ready():
    if not cleanup_expired_characters.is_running():
        cleanup_expired_characters.start()
    
    if not spawn_random_character.is_running():
        spawn_random_character.start()

    print(f'Logged in as {bot.user}')
    
    try:
        await bot.tree.sync()
        print("✅ Slash commands zsynchronizowane pomyślnie.")
    except Exception as e:
        print(f"❌ Błąd synchronizacji komend: {e}")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.tree.command(name="set_spawn_channel", description="Set the channel for random character spawns.")
async def set_spawn_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    """Ustawia kanał, w którym będą pojawiać się postacie."""
    guild_id = str(interaction.guild.id)
    spawn_channels[guild_id] = channel.id
    await interaction.response.send_message(f"✅ Characters will now spawn in {channel.mention}!", ephemeral=True)

@bot.tree.command(name="roll", description="Roll a new character (1 claim per 10 rolls, 10 rolls max/hour)")
@commands.cooldown(1, 8, commands.BucketType.user)
async def roll(interaction: discord.Interaction):
    import time
    guild_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)
    current_time = time.time()

    await load_data(guild_id)

    # Initialize or get user roll/claim data
    user_rolls.setdefault(guild_id, {})
    user_claims.setdefault(guild_id, {})
    claimed_characters.setdefault(guild_id, {})
    user_collection.setdefault(guild_id, {})

    last_roll_time, roll_count = user_rolls[guild_id].get(user_id, (0, 0))
    claims = user_claims[guild_id].get(user_id, 0)

    # If an hour has passed, reset roll count and allow claiming again
    if current_time - last_roll_time >= 3600:
        roll_count = 0
        claims = 0

    # Check if user has rolled 10 times in the current hour
    if roll_count >= 10:
        remaining_time = int(3600 - (current_time - last_roll_time))
        minutes, seconds = divmod(remaining_time, 60)
        time_left = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
        await interaction.response.send_message(
            f"🛑 You've reached the roll limit (10 rolls/hour).\n⏳ Time until reset: **{time_left}**",
            ephemeral=True
        )
        return

    # Get a random character for the roll
    character = get_random_character(guild_id)
    if not character:
        await interaction.response.send_message("❌ No more unclaimed characters available!", ephemeral=True)
        return

    # Embed color based on rarity
    rarity_colors = {
        "Common": discord.Color.light_gray(),
        "Rare": discord.Color.blue(),
        "Epic": discord.Color.purple(),
        "Legendary": discord.Color.gold()
    }
    color = rarity_colors.get(character["rarity"], discord.Color.default())

    embed = discord.Embed(title=f"You found {character['name']}!", color=color)
    embed.set_image(url=character["image"])
    embed.set_footer(text=f"Rarity: {character['rarity']}")

    # Send embed to user and add reaction for claiming
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    await message.add_reaction("✅")

    # Update roll count
    user_rolls[guild_id][user_id] = (current_time, roll_count + 1)
    await save_data(guild_id)

    # Wait for the user to react and claim the character
    def check(reaction, user):
        return (
            user != interaction.client.user and
            reaction.message.id == message.id and
            str(reaction.emoji) == "✅" and
            user.id == interaction.user.id
        )

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)

        # Check if user has claimed a character already
        if claims >= 1:  # Allow only one claim for every 10 rolls
            await interaction.followup.send(f"🛑 You can only claim **1 character** per 10 rolls!", ephemeral=True)
            return

        # Add the character to the user's collection
        claimed_characters[guild_id][character['name']] = user_id
        user_collection[guild_id].setdefault(user_id, []).append(character)

        # Update claim count
        user_claims[guild_id][user_id] = 1  # Claim 1 character for every 10 rolls

        await save_data(guild_id)
        await interaction.followup.send(f"{user.mention} claimed **{character['name']}**!")

    except asyncio.TimeoutError:
        await interaction.followup.send(f"The roll timed out.")

# Error handler for cooldown
@roll.error
async def roll_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.CommandOnCooldown):
        remaining = int(error.retry_after)
        minutes, seconds = divmod(remaining, 60)
        time_left = f"{minutes}m {seconds}s" if minutes else f"{seconds}s"
        await interaction.response.send_message(
            f"⏳ You must wait **{time_left}** before rolling again!",
            ephemeral=True
        )
    else:
        raise error

# Error handler for cooldown
@roll.error
async def roll_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.CommandOnCooldown):
        remaining = int(error.retry_after)
        minutes, seconds = divmod(remaining, 60)
        time_str = f"{minutes}m {seconds}s" if minutes else f"{seconds}s"
        await interaction.response.send_message(
            f"⏳ You must wait **{time_str}** before rolling again!",
            ephemeral=True
        )
    else:
        raise error

@bot.tree.command(name="collection", description="Displays the characters you have collected.")
async def collection(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    guild_id = str(interaction.guild.id)

    await load_data(guild_id)

    if guild_id not in user_collection or user_id not in user_collection[guild_id]:
        await interaction.response.send_message("You haven't collected any characters yet.", ephemeral=True)
        return
        
    sorted_characters = sorted(user_collection[guild_id][user_id], key=lambda x: x["rarity"])
    embeds = []
    collection_text = ""
    char_limit = 1024  # Limit for each embed field

    embed = discord.Embed(
        title=f"{interaction.user.name}'s Character Collection",
        description=f"**Total Characters:** {len(sorted_characters)}",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=interaction.user.avatar.url) 
    for character in sorted_characters:
        line = f"**{character['name']}** ({character['rarity']})\n"
        if len(collection_text) + len(line) > char_limit:
            embed.add_field(name="Your Collection:", value=collection_text, inline=False)
            embeds.append(embed)
            collection_text = line
            embed = discord.Embed(
                title=f"{interaction.user.name}'s Character Collection",
                color=discord.Color.green() )
        else:
            collection_text += line

    if collection_text:  # Add remaining characters to embed
        embed.add_field(name="Your Collection:", value=collection_text, inline=False)
        embeds.append(embed)

    # Send embed if collection exists
    if embeds:
        for embed in embeds:
            await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("You don't have any characters in your collection.", ephemeral=True)

@bot.tree.command(name="give", description="Give a character to another user.")
async def give(interaction: discord.Interaction, member: discord.Member, character_name: str):
    guild_id = str(interaction.guild.id)
    giver_id = str(interaction.user.id)
    recipient_id = str(member.id)

    # Prevent giving a character to oneself
    if giver_id == recipient_id:
        await interaction.response.send_message("You can't give a character to yourself!", ephemeral=True)
        return

    await load_data(guild_id)

    # Ensure collections exist
    user_collection.setdefault(guild_id, {})
    user_collection[guild_id].setdefault(giver_id, [])
    user_collection[guild_id].setdefault(recipient_id, [])

    # Find the character in the giver's collection
    character = next((c for c in user_collection[guild_id][giver_id] if c["name"].lower() == character_name.lower()), None)

    if not character:
        await interaction.response.send_message(f"{interaction.user.mention}, you don't own **{character_name}**!", ephemeral=True)
        return

    # Transfer the character
    user_collection[guild_id][giver_id] = [c for c in user_collection[guild_id][giver_id] if c["name"].lower() != character_name.lower()]
    user_collection[guild_id][recipient_id].append(character)

    # Save data
    await save_data(guild_id)

    await interaction.response.send_message(f"{interaction.user.mention} gave **{character_name}** to {member.mention}!")

@bot.tree.command(name="remove", description="Remove a character from your collection.")
@app_commands.describe(character_name="Name of the character to remove")
async def remove(interaction: discord.Interaction, character_name: str):
    guild_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)

    await load_data(guild_id)

    user_collection.setdefault(guild_id, {})
    user_collection[guild_id].setdefault(user_id, [])

    user_chars = user_collection[guild_id][user_id]

    char_to_remove = next((c for c in user_chars if c["name"].lower() == character_name.lower()), None)
    if not char_to_remove:
        await interaction.response.send_message(f"{interaction.user.mention}, you do not own **{character_name}**!", ephemeral=True)
        return

    # 🔹 Tworzymy embed z informacją o postaci
    embed = discord.Embed(
        title=f"Remove {char_to_remove['name']}?",
        description="Are you sure you want to remove this character from your collection?",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=char_to_remove["image"])
    embed.set_footer(text=f"Rarity: {char_to_remove['rarity']}")

    # 🔹 Potwierdzenie
    class ConfirmationView(View):
        def __init__(self):
            super().__init__(timeout=30)
            self.value = None

        @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
        async def confirm(self, interaction: discord.Interaction, button: Button):
            await interaction.response.defer()
            self.value = True
            self.stop()

        @discord.ui.button(label="No", style=discord.ButtonStyle.red)
        async def cancel(self, interaction: discord.Interaction, button: Button):
            await interaction.response.defer()
            self.value = False
            self.stop()

    view = ConfirmationView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    await view.wait()

    if view.value:
        # Usuń z kolekcji
        user_collection[guild_id][user_id] = [
            c for c in user_chars if c["name"].lower() != character_name.lower()
        ]

        # Usuń z claimed_characters
        if char_to_remove["name"] in claimed_characters.get(guild_id, {}):
            del claimed_characters[guild_id][char_to_remove["name"]]

        # Dodaj z powrotem do puli (jeśli trzeba)
        if char_to_remove["name"].lower() not in {c["name"].lower() for c in characters}:
            characters.append(char_to_remove)

        try:
            await save_data(guild_id)
            await interaction.followup.send(
                f"❌ {interaction.user.mention} has removed **{character_name}** from their collection!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"⚠️ An error occurred while saving the data: {e}", ephemeral=True)
    else:
        await interaction.followup.send("Character removal canceled.", ephemeral=True)

@bot.tree.command(name="leaderboard", description="Check the leaderboard of character collectors.")
async def leaderboard(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    if guild_id not in user_collection or not user_collection[guild_id]:
        await interaction.response.send_message("No data available for the leaderboard in this server.", ephemeral=True)
        return

    leaderboard = sorted(
        user_collection[guild_id].items(),
        key=lambda x: len(x[1]), reverse=True
    )

    embed = discord.Embed(title="🏆 Leaderboard - Character Collectors", color=discord.Color.gold())

    for i, (user_id, collection) in enumerate(leaderboard[:10]):
        try:
            user = await bot.fetch_user(user_id)
        except discord.NotFound:
            user = None

        common_count = sum(1 for c in collection if isinstance(c, dict) and c.get('rarity') == "Common")
        rare_count = sum(1 for c in collection if isinstance(c, dict) and c.get('rarity') == "Rare")
        epic_count = sum(1 for c in collection if isinstance(c, dict) and c.get('rarity') == "Epic")
        legendary_count = sum(1 for c in collection if isinstance(c, dict) and c.get('rarity') == "Legendary")

        user_name = user.name if user else "User Not Found"

        embed.add_field(
            name=f"{i + 1}. {user_name}",
            value=(f"**Total Characters:** {len(collection)}\n"
                   f"**Common:** {common_count} | **Rare:** {rare_count}\n"
                   f"**Epic:** {epic_count} | **Legendary:** {legendary_count}"),
            inline=False
        )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="trade", description="Trade a character with another user.")
async def trade(interaction: discord.Interaction, member: discord.Member):
    guild_id = str(interaction.guild.id)
    giver_id = str(interaction.user.id)
    recipient_id = str(member.id)

    if giver_id == recipient_id:
        await interaction.response.send_message("You can't trade with yourself!", ephemeral=True)
        return

    await load_data(guild_id)
    
    giver_chars = user_collection.get(guild_id, {}).get(giver_id, [])
    recipient_chars = user_collection.get(guild_id, {}).get(recipient_id, [])

    if not giver_chars or not recipient_chars:
        await interaction.response.send_message("One or both users have no characters to trade.", ephemeral=True)
        return

    class CharacterSelection(View):
        def __init__(self, user, giver_chars, recipient_chars):
            super().__init__()
            self.user = user
            self.selected_character = None
            self.giver_chars = giver_chars
            self.recipient_chars = recipient_chars
            # Prepare the options before the view is displayed
            self.options = [discord.SelectOption(label=c["name"]) for c in (giver_chars if self.user == giver_id else recipient_chars)]

        @discord.ui.select(
            placeholder="Select a character to trade",
        )
        async def select_character(self, select_interaction: discord.Interaction, select):
            if select_interaction.user.id != int(self.user):
                await select_interaction.response.send_message("This is not your selection!", ephemeral=True)
                return
            self.selected_character = select.values[0]
            await select_interaction.response.send_message(f"You selected: {self.selected_character}", ephemeral=True)
            self.stop()

    giver_view = CharacterSelection(giver_id, giver_chars, recipient_chars)
    giver_view.children[0].options = giver_view.options  # Set options for giver view
    await interaction.response.send_message(f"{interaction.user.mention}, select a character to trade:", view=giver_view)
    await giver_view.wait()

    recipient_view = CharacterSelection(recipient_id, giver_chars, recipient_chars)
    recipient_view.children[0].options = recipient_view.options  # Set options for recipient view
    await interaction.followup.send(f"{member.mention}, select a character to trade:", view=recipient_view)
    await recipient_view.wait()

    if not giver_view.selected_character or not recipient_view.selected_character:
        await interaction.followup.send("Trade canceled due to no selection.")
        return

    # Exchange the characters
    giver_char = next(c for c in giver_chars if c["name"].lower() == giver_view.selected_character.lower())
    recipient_char = next(c for c in recipient_chars if c["name"].lower() == recipient_view.selected_character.lower())

    # Remove selected characters from both users
    user_collection[guild_id][giver_id] = [c for c in giver_chars if c != giver_char]
    user_collection[guild_id][recipient_id] = [c for c in recipient_chars if c != recipient_char]

    # Add the selected characters to the opposite users
    user_collection[guild_id][giver_id].append(recipient_char)
    user_collection[guild_id][recipient_id].append(giver_char)

    # Save the data after the trade
    await save_data(guild_id)

    await interaction.followup.send(f"✅ Trade completed! {interaction.user.mention} swapped **{giver_view.selected_character}** for **{recipient_view.selected_character}** with {member.mention}.")

token = os.getenv("DISCORD_TOKEN")

if not token:
    print("Error: DISCORD_TOKEN environment variable is not set.")
    exit(1)
    
keep_alive()
bot.run(token)