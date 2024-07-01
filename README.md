VMRPG Discord Bot

Welcome to the VMRPG Discord Bot! This bot brings an exciting text-based RPG experience to your Discord server, allowing you to embark on thrilling adventures, battle fierce monsters, and grow stronger with each victory. Below you’ll find all the details about the features and functions of the bot.

current issues: auto mode doesn't work, quest don't work either
Features

	•	Race and Class Selection: Choose from a variety of races (Demon, Human, Elf, Dwarf) and classes (Warrior, Mage, Rogue, Assassin, Necromancer, Healer) to create your unique character.
	•	Profile Management: Create and manage your character profile with commands to view your stats, clear your profile, and improve your skills.
	•	Battle System: Engage in battles with monsters and use your skills to defeat them and gain experience, gold, and items.
	•	Inventory System: Manage your inventory, buy items from the shop, and use them during your adventures.
	•	Stat Improvement: Level up and improve your stats to become stronger and face tougher challenges.
	•	Auto Mode: Set your character to automatically engage in battles and earn rewards without manual intervention.
	•	Quests: Take on quests to earn additional rewards and experience points.

Commands

/start

Start your adventure by creating a profile. Choose your race and class to get started.

/profile

View your character’s profile, including race, class, HP, MP, EXP, level, gold, ultimate skill, skills, attack, strength, defense, and luck.

/fight

Engage in a battle with a random monster. Use your skills to defeat the monster and earn rewards.

/shop

Visit the shop to buy items using your gold. Items can be used during battles to aid your character.

/inventory

View and manage your inventory. Use items to heal or boost your character’s stats.

/clear_profile

Clear your current profile to start over. This will delete all your progress and inventory items.

/characters

Get information about the available races and their buffs and debuffs.

/classes

Get information about the available classes and their buffs and debuffs.

/stats

View your current stats, including attack, strength, defense, luck, and available stat points.

/improve_stats

Distribute your available stat points to improve your character’s stats.

Code Overview

Bot Setup

The bot is set up using the discord.py library with the following components:

	•	discord.Intents: Specifies the events the bot is subscribed to.
	•	commands.Bot: The main bot instance with a command prefix of /.

MongoDB Setup

The bot uses MongoDB for storing user profiles and inventory data. The connection is established using motor.motor_asyncio.AsyncIOMotorClient.

Data

Predefined data includes:

	•	Monsters: Different types of monsters with attributes like HP, attack, experience points, and gold.
	•	Shop Items: Items available for purchase in the shop.
	•	Skills: Skills for each class and race.
	•	Ultimate Skills: Powerful skills for each class.
	•	Race and Class Buffs/Debuffs: Unique attributes for each race and class.

Views and Buttons

The bot uses Discord’s UI components like Button, View, and Select to create interactive menus for selecting races, classes, and handling battles.

Main Functions

	•	Profile Management: Functions to get, save, and delete user profiles.
	•	Level Up Check: Function to check if a user has enough experience points to level up.
	•	Race and Class Selection: Views and select components for users to choose their race and class.
	•	Battle System: Buttons and views to handle battles, use skills, and manage cooldowns.
	•	Inventory Management: Views and select components to manage the user’s inventory and use items.

Getting Started

	1.	Install Dependencies: Make sure you have discord.py and motor installed.
	2.	Set Up MongoDB: Provide your MongoDB URL in the mongo_url variable.
	3.	Run the Bot: Execute the script to start the bot. Make sure to replace the placeholder with your actual bot token.

bot.run('YOUR_BOT_TOKEN_HERE')

Enjoy your adventure with the VMRPG Discord Bot! If you have any questions or need assistance, feel free to reach out.
