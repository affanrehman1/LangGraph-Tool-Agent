import asyncio
from prisma import Prisma
import random

async def seed():
    db = Prisma()
    await db.connect()
    
    # Clear existing users and items to ensure a fresh, realistic start
    print("Clearing existing users and items...")
    await db.item.delete_many()
    await db.user.delete_many()
    
    users_data = [
        {"name": "Alice Johnson", "email": "alice.j@example.com", "items": [{"name": "Laptop", "qty": 1}, {"name": "Wireless Mouse", "qty": 1}]},
        {"name": "Bob Smith", "email": "bob.smith@company.net", "items": [{"name": "Mechanical Keyboard", "qty": 1}, {"name": "Monitor", "qty": 2}]},
        {"name": "Charlie Davis", "email": "cdavis99@gmail.com", "items": [{"name": "Smartphone", "qty": 1}, {"name": "Phone Case", "qty": 3}, {"name": "Charging Cable", "qty": 2}]},
        {"name": "Diana Ross", "email": "d.ross@studio.co", "items": [{"name": "Studio Microphone", "qty": 1}, {"name": "Headphones", "qty": 2}]},
        {"name": "Ethan Hunt", "email": "ethan.m.hunt@imf.gov", "items": [{"name": "Grappling Hook", "qty": 1}, {"name": "Climbing Gear", "qty": 1}, {"name": "Sunglasses", "qty": 3}]},
        {"name": "Fiona Gallagher", "email": "fiona.g@southside.com", "items": [{"name": "Coffee Maker", "qty": 1}, {"name": "Mug", "qty": 6}]},
        {"name": "George Miller", "email": "george.miller@film.org", "items": [{"name": "Director's Chair", "qty": 1}, {"name": "Camera Lens", "qty": 4}]},
        {"name": "Hannah Baker", "email": "hannah.b@school.edu", "items": [{"name": "Notebook", "qty": 10}, {"name": "Pen Set", "qty": 5}, {"name": "Highlighters", "qty": 3}]},
        {"name": "Ian Malcolm", "email": "ian.malcolm@chaos.org", "items": [{"name": "Leather Jacket", "qty": 1}, {"name": "Sunglasses", "qty": 2}]},
        {"name": "Jessica Day", "email": "jessica.day@loft.net", "items": [{"name": "Ukulele", "qty": 1}, {"name": "Craft Supplies", "qty": 20}]},
        {"name": "Kevin Mitnick", "email": "kevin@security.net", "items": [{"name": "Raspberry Pi", "qty": 5}, {"name": "Ethernet Cable", "qty": 15}, {"name": "USB Drive", "qty": 10}]},
        {"name": "Liam Neeson", "email": "liam.n@action.com", "items": [{"name": "Leather Gloves", "qty": 1}, {"name": "Flashlight", "qty": 2}]},
        {"name": "Mia Wallace", "email": "mia.wallace@diner.com", "items": [{"name": "Trench Coat", "qty": 1}, {"name": "Red Lipstick", "qty": 3}]},
        {"name": "Nathan Drake", "email": "nate.drake@adventure.co", "items": [{"name": "Grappling Hook", "qty": 1}, {"name": "Journal", "qty": 1}, {"name": "Compass", "qty": 1}]},
        {"name": "Olivia Pope", "email": "olivia.p@scandal.gov", "items": [{"name": "White Coat", "qty": 1}, {"name": "Red Wine Glass", "qty": 4}]},
        {"name": "Peter Parker", "email": "peter.p@dailybugle.net", "items": [{"name": "Camera", "qty": 1}, {"name": "Backpack", "qty": 1}, {"name": "Web Fluid Cartridges", "qty": 10}]},
        {"name": "Quinn Fabray", "email": "quinn.f@mhs.edu", "items": [{"name": "Pom Poms", "qty": 2}, {"name": "Trophy", "qty": 4}]},
        {"name": "Rachel Green", "email": "rachel.g@fashion.net", "items": [{"name": "Designer Bag", "qty": 2}, {"name": "Shoes", "qty": 15}]},
        {"name": "Steve Rogers", "email": "steve.rogers@avengers.org", "items": [{"name": "Shield", "qty": 1}, {"name": "Compass", "qty": 1}]},
        {"name": "Tony Stark", "email": "stark@starkindustries.com", "items": [{"name": "Arc Reactor", "qty": 1}, {"name": "Wrench", "qty": 5}, {"name": "Sports Car", "qty": 3}]},
        {"name": "Ursula K.", "email": "ursula@author.net", "items": [{"name": "Typewriter", "qty": 1}, {"name": "Fountain Pen", "qty": 2}, {"name": "Notebook", "qty": 12}]},
        {"name": "Victor Frankenstein", "email": "v.frankenstein@science.org", "items": [{"name": "Lab Coat", "qty": 1}, {"name": "Beaker", "qty": 15}, {"name": "Scalpel", "qty": 4}]},
        {"name": "Wanda Maximoff", "email": "wanda@westview.net", "items": [{"name": "Cape", "qty": 1}, {"name": "Cookbook", "qty": 2}]},
        {"name": "Xavier", "email": "prof.xavier@school.org", "items": [{"name": "Books", "qty": 50}, {"name": "Cerebro Helmet", "qty": 1}]},
        {"name": "Yoda", "email": "yoda@jedi.council.org", "items": [{"name": "Walking Stick", "qty": 1}, {"name": "Robe", "qty": 2}]}
    ]

    for ud in users_data:
        user = await db.user.create(data={
            "name": ud["name"],
            "email": ud["email"]
        })
        
        for item_data in ud["items"]:
            await db.item.create(data={
                "name": item_data["name"],
                "quantity": item_data["qty"],
                "userId": user.id
            })
            
    print(f"Successfully seeded {len(users_data)} users with their respective items.")
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed())
