# Getting Your Supabase PostgreSQL Connection String

## Your Supabase Project

**Project URL:** `https://bwdyttdagngwpmyoezco.supabase.co`

**Project Reference:** `bwdyttdagngwpmyoezco`

## How to Get PostgreSQL Connection String

### Step 1: Go to Database Settings

1. Open your Supabase dashboard: https://supabase.com/dashboard
2. Select your project: "tarun-ss's Project"
3. Click **Settings** (gear icon) in the left sidebar
4. Click **Database**

### Step 2: Find Connection String

1. Scroll down to **"Connection string"** section
2. You'll see tabs: **URI**, **JDBC**, **Golang**, etc.
3. Click on **"URI"** tab
4. Copy the connection string

It will look like:
```
postgresql://postgres.bwdyttdagngwpmyoezco:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### Step 3: Replace Password

The connection string has `[YOUR-PASSWORD]` in it.

**Replace it with the password you created when setting up the Supabase project.**

Example:
- If your password is: `MySecret123!`
- Connection string becomes:
  ```
  postgresql://postgres.bwdyttdagngwpmyoezco:MySecret123!@aws-0-us-east-1.pooler.supabase.com:6543/postgres
  ```

### Step 4: Update .env File

Open your `.env` file and update this line:

```env
DATABASE_URL=postgresql://postgres.bwdyttdagngwpmyoezco:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

Replace `YOUR_PASSWORD` with your actual password.

## If You Forgot Your Password

If you don't remember your database password:

1. Go to Supabase → Settings → Database
2. Scroll to **"Database password"** section
3. Click **"Reset database password"**
4. Enter a new password
5. Click **"Update password"**
6. Use this new password in your connection string

## Next Step: Run the Schema

After updating `.env`:

1. Go to Supabase → **SQL Editor**
2. Click **"New query"**
3. Copy ALL contents from `database/schema.sql`
4. Paste and click **"Run"**

This will create all the tables!

## Test Connection

```bash
python test_cloud_connections.py
```

You should see: `[OK] Connected to PostgreSQL`
