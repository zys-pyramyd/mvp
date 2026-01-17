#!/bin/bash
# Environment Variable Setup Guide for Render/Production

# Database
# MONGO_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority

# Security
# JWT_SECRET=generate_a_long_random_string_here
# ENCRYPTION_KEY=generate_fernet_key_here
# ADMIN_PASSWORD_HASH=bcrypt_hash_of_admin_password

# Payments (Paystack)
# PAYSTACK_SECRET_KEY=sk_live_...
# PAYSTACK_PUBLIC_KEY=pk_live_...

# Communication
# TWILIO_ACCOUNT_SID=AC...
# TWILIO_AUTH_TOKEN=...
# ADMIN_EMAIL=admin@pyramyd.com
# ALLOWED_ORIGINS=https://pyramyd.com,https://admin.pyramyd.com

# Commission Logic
# FARMHUB_SPLIT_GROUP=split_code_from_paystack
# FARMHUB_SUBACCOUNT=subaccount_code

echo "Please configure these variables in your Render Dashboard settings."
