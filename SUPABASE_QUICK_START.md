# Quick Guide: Getting Your Supabase Connection String

## You're Almost There! 🎉

I can see you've created your Supabase project "tarun-ss's Project" - perfect!

## Next Steps:

### 1. Get Your Connection String

1. In your Supabase dashboard, click on **Settings** (gear icon in left sidebar)
2. Click on **Database**
3. Scroll down to find **"Connection string"** section
4. You'll see several options - click on **"URI"**
5. Copy the entire string

It will look like this:
```
postgresql://postgres.abcdefghijk:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### 2. Replace the Password

The connection string has `[YOUR-PASSWORD]` in it. Replace this with the password you created when setting up the project.

**Example:**
- If your password is: `MySecret123!`
- Change: `postgresql://postgres.xxx:[YOUR-PASSWORD]@...`
- To: `postgresql://postgres.xxx:MySecret123!@...`

### 3. Run the Database Schema

1. In Supabase, click **SQL Editor** (left sidebar)
2. Click **"New query"** button
3. Open the file `database/schema.sql` from your project folder
4. Copy EVERYTHING from that file
5. Paste it into the Supabase SQL Editor
6. Click **"Run"** button (or press Ctrl+Enter)

You should see a success message!

### 4. Update Your .env File

Open `.env` in your project and update this line:

```env
DATABASE_URL=postgresql://postgres.xxxxx:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

Replace with YOUR actual connection string from step 1.

### 5. Test the Connection

Run this command:
```bash
python test_cloud_connections.py
```

If you see `[OK] Connected to PostgreSQL`, you're all set!

---

## Common Issues

### "Password authentication failed"
- Make sure you replaced `[YOUR-PASSWORD]` with your actual password
- Check for extra spaces or special characters

### "Could not connect to server"
- Make sure your Supabase project is "Active" (green status)
- Check your internet connection

### "Schema already exists"
- This is fine! It means the schema was already created
- You can skip the schema step

---

## What's Next?

Once Supabase is connected, you can:
1. Set up the other cloud databases (Qdrant, Neo4j, Upstash)
2. Or skip them for now and just use Supabase
3. Run `start_cloud.bat` to start the system

The code will work with just Supabase - the other databases are optional for now!
