# 🔐 Automatic Admin Creation - README

## Overview
The Pyramyd platform now automatically creates a default admin user on first startup.

## How It Works

### On First Startup
When the application starts for the first time:
1. System checks if any admin user exists in the database
2. If no admin found, creates a default admin user
3. Uses credentials from environment variables (`ADMIN_EMAIL` and `ADMIN_PASSWORD`)

### Default Admin Credentials
- **Username**: `pyramyd_admin`
- **Email**: From `ADMIN_EMAIL` env variable (default: `admin@pyramyd.com`)
- **Password**: From `ADMIN_PASSWORD` env variable (default: `admin123`)
- **Role**: `admin`

## Setup Instructions

### 1. Set Environment Variables

**For Production (REQUIRED):**
```bash
# In Render or your deployment platform
ADMIN_EMAIL=youradmin@pyramyd.com
ADMIN_PASSWORD=YourStrongPassword123!
```

**For Local Development:**
```bash
# In backend/.env file
ADMIN_EMAIL=admin@pyramyd.com
ADMIN_PASSWORD=admin123
```

### 2. Start the Application

```bash
cd backend
uvicorn app.main:app --reload
```

### 3. Check Console Output

You'll see:
```
🚀 Initializing database...
============================================================
🔐 DEFAULT ADMIN USER CREATED
============================================================
📧 Email: admin@pyramyd.com
👤 Username: pyramyd_admin
🔑 Password: admin123
============================================================
⚠️  IMPORTANT: Change the password after first login!
============================================================
✅ Database initialization complete
```

### 4. Login

1. Go to your app's login page
2. Enter the email and password from the console
3. You'll be auto-redirected to `/pyadmin`

## Creating Additional Admins

Once logged in as the default admin, you can create additional admin users through the `/pyadmin` dashboard:

1. Navigate to `/pyadmin`
2. Go to "User Management"
3. Find the user you want to promote
4. Change their role to "admin"
5. Save changes

## Security Best Practices

### ⚠️ CRITICAL: Production Deployment

**NEVER use default credentials in production!**

Before deploying to production:
1. Set strong `ADMIN_EMAIL` and `ADMIN_PASSWORD` in environment variables
2. Use a password manager to generate a strong password (16+ characters)
3. Change the password immediately after first login
4. Delete or disable the default admin after creating your personal admin account

### Recommended Password Format
- Minimum 16 characters
- Mix of uppercase, lowercase, numbers, symbols
- Example: `Pyr@m1d_Adm!n_2026_Secure#`

## Implementation Details

### Files Modified
- `backend/app/db/init_db.py` - Admin creation logic
- `backend/app/main.py` - Startup event integration
- `backend/.env.example` - Documentation

### Code Flow
```python
# On app startup
1. connect_to_mongo()
2. initialize_database()
   └── create_default_admin()
       ├── Check if admin exists
       ├── If not, create from env vars
       └── Print credentials to console
```

## Troubleshooting

### Admin not created
- Check MongoDB connection is working
- Verify environment variables are set
- Check console for error messages

### Can't login with default credentials
- Verify `ADMIN_EMAIL` and `ADMIN_PASSWORD` match what you're entering
- Check the console output for actual credentials used
- Ensure user has `role: "admin"` in database

### Multiple admins created
- This shouldn't happen (system checks for existing admins)
- If it does, manually delete duplicates from MongoDB

## FAQ

**Q: What if I forget the admin password?**
A: You can reset it directly in MongoDB or create a new admin using the `create_admin.py` script.

**Q: Can I disable automatic admin creation?**
A: Yes, comment out `app.add_event_handler("startup", initialize_database)` in `main.py`.

**Q: Will this create a new admin every time I restart?**
A: No, it only creates an admin if none exists. Safe to restart multiple times.

**Q: Can I change the default username?**
A: Yes, edit the `username` field in `init_db.py` (currently hardcoded as `pyramyd_admin`).
