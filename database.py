from prisma import Prisma

async def get_user_by_id(user_id: str):
    """Retrieve user profile and their items."""
    db = Prisma()
    await db.connect()
    try:
        user = await db.user.find_unique(
            where={"id": user_id},
            include={"items": True}
        )
        return user
    finally:
        await db.disconnect()

async def update_item_quantity(item_id: str, new_quantity: int):
    """Update item stock quantity."""
    db = Prisma()
    await db.connect()
    try:
        updated_item = await db.item.update(
            where={"id": item_id},
            data={"quantity": new_quantity}
        )
        return updated_item
    finally:
        await db.disconnect()
