from database import get_db

def create_indexes():
    db = get_db()
    if not db:
        print('No DB connection')
        return
    # Orders collection indexes
    db.orders.create_index([('status', 1), ('created_at', -1)])
    db.orders.create_index('buyer_username')
    db.orders.create_index('seller_id')
    db.orders.create_index('buyer_id')
    
    # Users collection index (unique email)
    db.users.create_index('email', unique=True)
    db.users.create_index('id')
    
    # Messages collection indexes
    db.messages.create_index([('conversation_id', 1), ('created_at', -1)])
    
    # Products collection indexes
    db.products.create_index('id')
    db.products.create_index('community_id')
    db.products.create_index('seller_id')
    db.products.create_index('category')
    db.products.create_index([('is_active', 1), ('created_at', -1)])
    
    # Communities collection indexes
    db.communities.create_index('id')
    db.communities.create_index('is_private')
    db.communities.create_index('category')
    
    # Community Members collection indexes
    db.community_members.create_index('community_id')
    db.community_members.create_index('user_id')
    
    # Community Posts collection indexes
    db.community_posts.create_index([('community_id', 1), ('created_at', -1)])
    
    print('Indexes created successfully.')

if __name__ == '__main__':
    create_indexes()
