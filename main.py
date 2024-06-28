import discord
from discord.ext import commands
from discord.ui import Button, View, Select
import random
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Bot setup
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='/', intents=intents)

# MongoDB setup
mongo_url = 'here'
mongo_client = AsyncIOMotorClient(mongo_url)
db = mongo_client.vmrpg
profiles_collection = db.profiles
inventory_collection = db.inventory

# Data
monsters = [
    {"name": "Orc", "hp": 50, "attack": [5, 10], "exp": 30, "gold": 15},
    {"name": "Goblin", "hp": 30, "attack": [3, 7], "exp": 20, "gold": 10},
    {"name": "Vampire", "hp": 60, "attack": [6, 12], "exp": 50, "gold": 25}
]
shop_items = {"HP Potion": {"cost": 10, "effect": 20}}

skills = {
    "Warrior": ["Slash", "Shield Bash", "Power Strike"],
    "Mage": ["Fireball", "Ice Spike", "Lightning Bolt"],
    "Rogue": ["Backstab", "Poison Dart", "Shadow Step"],
    "Assassin": ["Assassinate", "Smoke Bomb", "Shadow Strike"],
    "Necromancer": ["Raise Dead", "Soul Drain", "Dark Ritual"],
    "Healer": ["Heal", "Protect", "Purify"],
    "Demon": ["Hellfire", "Dark Pact"],
    "Human": ["Bravery", "Heroic Strike"],
    "Elf": ["Nature's Touch", "Elven Agility"],
    "Dwarf": ["Stone Skin", "Berserker Rage"]
}

ultimate_skills = {
    "Warrior": "Ultimate Slash",
    "Mage": "Ultimate Fireball",
    "Rogue": "Ultimate Backstab",
    "Assassin": "Ultimate Assassinate",
    "Necromancer": "Lich's Command",
    "Healer": "Divine Intervention",
    "Demon": "Infernal Blast",
    "Human": "Heroic Charge",
    "Elf": "Nature's Fury",
    "Dwarf": "Mountain's Wrath"
}

auto_mode_users = {}
user_inventories = {}
user_skill_cooldowns = {}

race_buffs_debuffs = {
    "Demon": {
        "description": "A fierce warrior from the depths of the underworld.",
        "buffs": ["Increased Attack", "Fire Resistance"],
        "debuffs": ["Weak to Holy Magic"]
    },
    "Human": {
        "description": "A versatile and resilient race.",
        "buffs": ["Balanced Stats", "Quick Learner"],
        "debuffs": ["No Special Abilities"]
    },
    "Elf": {
        "description": "A race attuned with nature and magic.",
        "buffs": ["High Agility", "Magic Affinity"],
        "debuffs": ["Low Defense"]
    },
    "Dwarf": {
        "description": "Stout and sturdy warriors from the mountains.",
        "buffs": ["High Defense", "Strength"],
        "debuffs": ["Low Agility"]
    }
}

class_buffs_debuffs = {
    "Warrior": {
        "description": "A strong melee fighter.",
        "buffs": ["High Strength", "Good Defense"],
        "debuffs": ["Low Magic Resistance"]
    },
    "Mage": {
        "description": "A master of elemental magic.",
        "buffs": ["High Magic Damage", "Mana Regeneration"],
        "debuffs": ["Low Physical Defense"]
    },
    "Rogue": {
        "description": "A quick and stealthy fighter.",
        "buffs": ["High Agility", "Critical Hits"],
        "debuffs": ["Low HP"]
    },
    "Assassin": {
        "description": "A deadly and stealthy killer.",
        "buffs": ["High Critical Damage", "Stealth Abilities"],
        "debuffs": ["Low Defense"]
    },
    "Necromancer": {
        "description": "A wielder of dark magic.",
        "buffs": ["Summon Undead", "Life Drain"],
        "debuffs": ["Weak to Holy Magic"]
    },
    "Healer": {
        "description": "A protector and healer.",
        "buffs": ["Healing Abilities", "Buffs"],
        "debuffs": ["Low Attack Damage"]
    }
}

async def get_user_profile(user_id):
    profile = await profiles_collection.find_one({"user_id": user_id})
    if profile is None:
        profile = {
            "user_id": user_id,
            "race": None,
            "class": None,
            "HP": 100,
            "MP": 50,
            "EXP": 0,
            "Level": 1,
            "Gold": 0,
            "ultimate_skill": None,
            "skills": [],
            "attack": 10,
            "strength": 10,
            "defense": 10,
            "luck": 10,
            "stat_points": 0
        }
        await save_user_profile(user_id, profile)
    return profile

async def save_user_profile(user_id, profile):
    await profiles_collection.update_one({"user_id": user_id}, {"$set": profile}, upsert=True)

async def delete_user_profile(user_id):
    await profiles_collection.delete_one({"user_id": user_id})

async def check_level_up(profile):
    level_up_exp = 100 * profile["Level"]
    if profile["EXP"] >= level_up_exp:
        profile["Level"] += 1
        profile["stat_points"] += 5  # Award stat points on level up
        profile["EXP"] -= level_up_exp
        await save_user_profile(profile["user_id"], profile)
        return True
    return False

class ClassSelectView(View):
    def __init__(self, race):
        super().__init__()
        self.race = race
        self.add_item(ClassSelect())

class ClassSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Warrior"),
            discord.SelectOption(label="Mage"),
            discord.SelectOption(label="Rogue"),
            discord.SelectOption(label="Assassin"),
            discord.SelectOption(label="Necromancer"),
            discord.SelectOption(label="Healer")
        ]
        super().__init__(placeholder="Choose your class...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_class = self.values[0]
        user_id = interaction.user.id
        ultimate_skill = ultimate_skills[selected_class]
        skills_list = skills[selected_class] + skills[self.view.race]
        user_profile = await get_user_profile(user_id)
        user_profile["race"] = self.view.race
        user_profile["class"] = selected_class
        user_profile["ultimate_skill"] = ultimate_skill
        user_profile["skills"] = skills_list
        await save_user_profile(user_id, user_profile)
        await interaction.response.send_message(f"You selected {selected_class}. Your ultimate skill is {ultimate_skill}. Your profile is now created! Use /profile to view your profile and /fight to start fighting.")

# View for selecting race
class RaceSelectView(View):
    def __init__(self):
        super().__init__()
        self.add_item(RaceSelect())

class RaceSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Demon"),
            discord.SelectOption(label="Human"),
            discord.SelectOption(label="Elf"),
            discord.SelectOption(label="Dwarf")
        ]
        super().__init__(placeholder="Choose your race...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_race = self.values[0]
        await interaction.response.send_message(f"You selected {selected_race}. Now choose your class.", view=ClassSelectView(selected_race))

# View for fighting
class FightView(View):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.add_item(FightButton(user_id))
        self.add_item(BattleAllButton(user_id))
        self.add_item(AutoModeButton(user_id))
        self.add_item(ManualModeButton(user_id))
        self.add_item(QuestsButton(user_id))

class FightButton(Button):
    def __init__(self, user_id):
        super().__init__(label="Fight", style=discord.ButtonStyle.primary, custom_id=f"fight_{user_id}")

    async def callback(self, interaction: discord.Interaction):
        user_id = int(self.custom_id.split("_")[1])
        user_profile = await get_user_profile(user_id)
        monster = random.choice(monsters)
        monster["hp"] = monster["initial_hp"] = monster["hp"]  # Set initial HP

        await interaction.response.send_message(f"{interaction.user.mention} encountered {monster['name']} (HP: {monster['hp']}/{monster['initial_hp']})!", view=SkillView(user_id, user_profile["class"], user_profile["race"], user_profile["ultimate_skill"], monster))

class BattleAllButton(Button):
    def __init__(self, user_id):
        super().__init__(label="Battle All", style=discord.ButtonStyle.primary)

class AutoModeButton(Button):
    def __init__(self, user_id):
        super().__init__(label="Auto Mode", style=discord.ButtonStyle.primary)

class ManualModeButton(Button):
    def __init__(self, user_id):
        super().__init__(label="Manual Mode", style=discord.ButtonStyle.primary)

class QuestsButton(Button):
    def __init__(self, user_id):
        super().__init__(label="Quests", style=discord.ButtonStyle.primary)

# View for handling skill use
class SkillView(View):
    def __init__(self, user_id, user_class, user_race, ultimate_skill, monster):
        super().__init__()
        self.user_id = user_id
        self.user_class = user_class
        self.user_race = user_race
        self.ultimate_skill = ultimate_skill
        self.monster = monster
        self.add_item(SkillButton(user_id, "Fireball"))
        self.add_item(SkillButton(user_id, "Ice Spike"))
        self.add_item(SkillButton(user_id, "Lightning Bolt"))
        self.add_item(SkillButton(user_id, "Hellfire"))
        self.add_item(SkillButton(user_id, "Dark Pact"))
        self.add_item(SkillButton(user_id, "Infernal Blast"))

class SkillButton(Button):
    def __init__(self, user_id, label):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        user_profile = await get_user_profile(self.user_id)
        monster = self.view.monster
        skill = self.label
        damage = random.randint(10, 30)

        if skill == self.view.ultimate_skill:
            if user_skill_cooldowns.get((self.user_id, skill), 0) > 0:
                await interaction.response.send_message(f"{skill} is on cooldown!", ephemeral=True)
                return
            damage *= 2  # Ultimate skills deal double damage
            user_skill_cooldowns[(self.user_id, skill)] = 5  # Cooldown of 5 turns for ultimate skill
        else:
            if user_skill_cooldowns.get((self.user_id, skill), 0) > 0:
                await interaction.response.send_message(f"{skill} is on cooldown!", ephemeral=True)
                return
            user_skill_cooldowns[(self.user_id, skill)] = 3  # Cooldown of 3 turns for regular skills

        monster["hp"] -= damage
        await interaction.response.send_message(f"{interaction.user.mention} used {skill} on {monster['name']}!")

        if monster["hp"] <= 0:
            user_profile["EXP"] += monster["exp"]
            user_profile["Gold"] += monster["gold"]
            loot = random.choice(["HP Potion", None])
            if loot:
                if self.user_id not in user_inventories:
                    user_inventories[self.user_id] = []
                user_inventories[self.user_id].append(loot)
                await interaction.followup.send(f"{interaction.user.mention} defeated {monster['name']} and received {monster['exp']} EXP, {monster['gold']} gold, and a {loot}!")
            else:
                await interaction.followup.send(f"{interaction.user.mention} defeated {monster['name']} and received {monster['exp']} EXP and {monster['gold']} gold!")
            if await check_level_up(user_profile):
                await interaction.followup.send(f"{interaction.user.mention} has leveled up to level {user_profile['Level']}!")
            user_profile["HP"] = 100  # Reset user HP after defeat
            monster["hp"] = monster["initial_hp"]  # Reset monster HP
        else:
            await interaction.followup.send(f"{monster['name']} has {monster['hp']} HP left.")

        await save_user_profile(self.user_id, user_profile)

        # Reduce cooldowns for skills
        for key in user_skill_cooldowns:
            if user_skill_cooldowns[key] > 0:
                user_skill_cooldowns[key] -= 1

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name="VMRPG"))

@bot.slash_command(name='start')
async def start(ctx: discord.ApplicationContext):
    user_id = ctx.user.id
    user_profile = await get_user_profile(user_id)
    if user_profile.get("race") and user_profile.get("class"):
        await ctx.respond("You already have a profile. Use /profile to view it or /clear_profile to reset it.")
        return
    await ctx.respond("Welcome to the RPG game! Please select your race:", view=RaceSelectView())

@bot.slash_command(name='profile')
async def profile(ctx: discord.ApplicationContext):
    user_id = ctx.user.id
    user_profile = await get_user_profile(user_id)
    if user_profile:
        embed = discord.Embed(title="User Profile")
        embed.set_thumbnail(url=ctx.user.display_avatar.url)
        embed.add_field(name="Username", value=ctx.user.display_name, inline=False)
        embed.add_field(name="Race", value=user_profile["race"], inline=False)
        embed.add_field(name="Class", value=user_profile["class"], inline=False)
        embed.add_field(name="HP", value=f"{user_profile['HP']}/100", inline=False)
        embed.add_field(name="EXP", value=f"{user_profile['EXP']}/{100 * user_profile['Level']}", inline=False)
        embed.add_field(name="MP", value=f"{user_profile['MP']}/50", inline=False)
        embed.add_field(name="Level", value=user_profile["Level"], inline=False)
        embed.add_field(name="Gold", value=user_profile["Gold"], inline=False)
        embed.add_field(name="Ultimate Skill", value=user_profile["ultimate_skill"], inline=False)
        embed.add_field(name="Skills", value=", ".join(user_profile["skills"]), inline=False)
        embed.add_field(name="Attack", value=user_profile["attack"], inline=False)
        embed.add_field(name="Strength", value=user_profile["strength"], inline=False)
        embed.add_field(name="Defense", value=user_profile["defense"], inline=False)
        embed.add_field(name="Luck", value=user_profile["luck"], inline=False)
        await ctx.respond(embed=embed)
    else:
        await ctx.respond("You need to create a profile first using /start.")

@bot.slash_command(name='fight')
async def fight(ctx: discord.ApplicationContext):
    user_id = ctx.user.id
    user_profile = await get_user_profile(user_id)
    if not user_profile.get("race") or not user_profile.get("class"):
        await ctx.respond("You need to create a profile first using /start.")
        return
    await ctx.respond("Current Location: Everwood Grove\nMonster Levels: [1-10]\nLevel Requirement: 1", view=FightView(user_id))

@bot.slash_command(name='shop')
async def shop(ctx: discord.ApplicationContext):
    user_id = ctx.user.id
    if not await get_user_profile(user_id):
        await ctx.respond("You need to create a profile first using /start.")
        return
    await ctx.respond("Welcome to the shop! Please select an item to buy:", view=ShopView(user_id))

@bot.slash_command(name='inventory')
async def inventory(ctx: discord.ApplicationContext):
    user_id = ctx.user.id
    if not await get_user_profile(user_id):
        await ctx.respond("You need to create a profile first using /start.")
        return
    if user_id not in user_inventories or not user_inventories[user_id]:
        await ctx.respond("Your inventory is empty.")
        return
    await ctx.respond("Here is your inventory:", view=InventoryView(user_id))

@bot.slash_command(name='clear_profile')
async def clear_profile(ctx: discord.ApplicationContext):
    user_id = ctx.user.id
    await delete_user_profile(user_id)
    if user_id in user_inventories:
        del user_inventories[user_id]
    await ctx.respond("Your profile has been cleared. Use /start to create a new one.")

@bot.slash_command(name='characters')
async def characters(ctx: discord.ApplicationContext):
    embed = discord.Embed(title="Available Races")
    for race, details in race_buffs_debuffs.items():
        embed.add_field(
            name=race,
            value=f"{details['description']}\n"
                  f"**Buffs:** {', '.join(details['buffs'])}\n"
                  f"**Debuffs:** {', '.join(details['debuffs'])}\n",
            inline=False
        )
    await ctx.respond(embed=embed)

@bot.slash_command(name='classes')
async def classes(ctx: discord.ApplicationContext):
    embed = discord.Embed(title="Available Classes")
    for class_name, details in class_buffs_debuffs.items():
        embed.add_field(
            name=class_name,
            value=f"{details['description']}\n"
                  f"**Buffs:** {', '.join(details['buffs'])}\n"
                  f"**Debuffs:** {', '.join(details['debuffs'])}\n",
            inline=False
        )
    await ctx.respond(embed=embed)

@bot.slash_command(name='stats')
async def stats(ctx: discord.ApplicationContext):
    user_id = ctx.user.id
    user_profile = await get_user_profile(user_id)
    if user_profile:
        embed = discord.Embed(title="Your Stats")
        embed.add_field(name="Attack", value=user_profile.get("attack", 10), inline=False)
        embed.add_field(name="Strength", value=user_profile.get("strength", 10), inline=False)
        embed.add_field(name="Defense", value=user_profile.get("defense", 10), inline=False)
        embed.add_field(name="Luck", value=user_profile.get("luck", 10), inline=False)
        embed.add_field(name="Stat Points", value=user_profile.get("stat_points", 0), inline=False)
        await ctx.respond(embed=embed)
    else:
        await ctx.respond("You need to create a profile first using /start.")

@bot.slash_command(name='improve_stats')
async def improve_stats(ctx: discord.ApplicationContext):
    user_id = ctx.user.id
    user_profile = await get_user_profile(user_id)
    if user_profile:
        if user_profile.get("stat_points", 0) <= 0:
            await ctx.respond("You don't have any stat points to distribute.")
            return
        await ctx.respond("Choose a stat to improve:", view=StatSelectView(user_id))
    else:
        await ctx.respond("You need to create a profile first using /start.")

class StatSelectView(View):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.add_item(StatSelect())

class StatSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Attack"),
            discord.SelectOption(label="Strength"),
            discord.SelectOption(label="Defense"),
            discord.SelectOption(label="Luck")
        ]
        super().__init__(placeholder="Choose a stat...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_stat = self.values[0].lower()
        user_profile = await get_user_profile(interaction.user.id)
        user_profile[selected_stat] += 1
        user_profile["stat_points"] -= 1
        await save_user_profile(interaction.user.id, user_profile)
        await interaction.response.send_message(f"{selected_stat.capitalize()} has been increased by 1. You have {user_profile['stat_points']} stat points left.")

class ShopView(View):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.add_item(ShopSelect())

class ShopSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="HP Potion", description="Cost: 10 gold")
        ]
        super().__init__(placeholder="Select an item to buy...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        user_profile = await get_user_profile(self.view.user_id)
        selected_item = self.values[0]
        item_cost = shop_items[selected_item]["cost"]

        if user_profile["Gold"] < item_cost:
            await interaction.response.send_message("You don't have enough gold to buy this item.", ephemeral=True)
        else:
            user_profile["Gold"] -= item_cost
            if self.view.user_id not in user_inventories:
                user_inventories[self.view.user_id] = []
            user_inventories[self.view.user_id].append(selected_item)
            await save_user_profile(self.view.user_id, user_profile)
            await interaction.response.send_message(f"You bought a {selected_item} for {item_cost} gold.")

class InventoryView(View):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.add_item(InventorySelect())

class InventorySelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=item) for item in user_inventories.get(self.view.user_id, [])
        ]
        super().__init__(placeholder="Select an item to use...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_item = self.values[0]
        if selected_item == "HP Potion":
            user_profile = await get_user_profile(self.view.user_id)
            user_profile["HP"] += shop_items[selected_item]["effect"]
            user_inventories[self.view.user_id].remove(selected_item)
            await save_user_profile(self.view.user_id, user_profile)
            await interaction.response.send_message(f"You used a {selected_item}. Your HP is now {user_profile['HP']}.")

bot.run('here')
