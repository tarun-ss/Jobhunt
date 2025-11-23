# Neo4j Aura Credentials

**IMPORTANT: Save these credentials securely!**

## Your Neo4j Aura Instance

**Username:** `neo4j`

**Password:** `EKVoigO5j64mzMv16-hRBzf-lXDqbIKSeQo1ZNa7FNY`

**Connection URI:** (Will be shown after instance is created - looks like: `neo4j+s://xxxxx.databases.neo4j.io`)

## Next Steps

1. **Download the credentials** (click "Download to continue" button)
2. **Wait for instance to finish creating** (~2 minutes)
3. **Get the Connection URI:**
   - After creation, click on your instance
   - Copy the "Connection URI" (starts with `neo4j+s://`)
4. **Update .env file** with these credentials

## For .env File

Once you have the connection URI, add to `.env`:

```env
NEO4J_URL=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=EKVoigO5j64mzMv16-hRBzf-lXDqbIKSeQo1ZNa7FNY
```

## Test Connection

After updating .env:

```bash
python test_neo4j.py
```

---

**⚠️ IMPORTANT:** 
- You can only see this password ONCE
- Save it securely
- If you lose it, you'll need to reset the password or create a new instance
