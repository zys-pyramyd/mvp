from database import get_db

def create_indexes():
    db = get_db()
    if not db:
        print('No DB connection')
        return
    # Orders collection indexes
    db.orders.create_index([('status', 1), ('created_at', -1)])
    db.orders.create_index('buyer_username')
    # Users collection index (unique email)
    db.users.create_index('email', unique=True)
    # Messages collection indexes
    db.messages.create_index([('conversation_id', 1), ('created_at', -1)])
    print('Indexes created')

if __name__ == '__main__':
    create_indexes()
