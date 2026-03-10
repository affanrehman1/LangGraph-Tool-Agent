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

async def get_session_messages(session_id: str) -> list:
    """Load conversation history for a specific session."""
    db = Prisma()
    await db.connect()
    try:
        messages = await db.message.find_many(
            where={"sessionId": session_id},
            order={"createdAt": "asc"}
        )
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    finally:
        await db.disconnect()

async def get_all_sessions() -> list:
    """Fetch all stored chat sessions, ordered by most recent first."""
    db = Prisma()
    await db.connect()
    try:
        sessions = await db.session.find_many(
            order={"createdAt": "desc"}
        )
        return [{"id": s.id, "createdAt": s.createdAt} for s in sessions]
    finally:
        await db.disconnect()

async def save_message(session_id: str, role: str, content: str):
    """Save a single text message to the history."""
    db = Prisma()
    await db.connect()
    try:
        # Create session if it doesn't exist
        session = await db.session.find_unique(where={"id": session_id})
        if not session:
            await db.session.create(data={"id": session_id})
            
        await db.message.create(
            data={"sessionId": session_id, "role": role, "content": content}
        )
    finally:
        await db.disconnect()
