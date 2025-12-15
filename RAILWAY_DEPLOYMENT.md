# 🚀 Railway Deployment Guide - PNP San Juan

## Prerequisites
- GitHub account
- Railway account (sign up at https://railway.app)
- Your code pushed to GitHub

---

## 📋 Step-by-Step Deployment

### **Step 1: Push Your Code to GitHub**

1. **Open GitHub Desktop**
2. **Commit all changes:**
   - Review the changes in the left panel
   - Add a commit message (e.g., "Ready for Railway deployment")
   - Click **"Commit to master"**
3. **Push to GitHub:**
   - Click **"Push origin"** button at the top
   - Wait for the push to complete

---

### **Step 2: Sign Up for Railway**

1. Go to https://railway.app
2. Click **"Login"** or **"Start a New Project"**
3. Sign in with **GitHub** (recommended)
4. Authorize Railway to access your repositories

---

### **Step 3: Create New Project**

1. Click **"New Project"** on Railway dashboard
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: **pnpsanjuan**
4. Railway will detect it's a Python app automatically

---

### **Step 4: Add MySQL Database**

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add MySQL"**
3. Railway will create a MySQL database
4. **Important:** Railway automatically creates these environment variables:
   - `MYSQL_URL`
   - `MYSQLHOST`
   - `MYSQLPORT`
   - `MYSQLUSER`
   - `MYSQLPASSWORD`
   - `MYSQLDATABASE`

---

### **Step 5: Configure Environment Variables**

1. Click on your **web service** (not the database)
2. Go to **"Variables"** tab
3. Click **"+ New Variable"** and add these:

```env
# Database (use Railway's MySQL variables)
DB_HOST=${{MYSQLHOST}}
DB_USER=${{MYSQLUSER}}
DB_PASSWORD=${{MYSQLPASSWORD}}
DB_NAME=${{MYSQLDATABASE}}
DB_PORT=${{MYSQLPORT}}

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SMTP_SENDER_NAME=PNP San Juan
SMTP_SENDER_EMAIL=your-email@gmail.com

# OTP Configuration
OTP_EXPIRY_MINUTES=5
OTP_LENGTH=6

# Flask Secret Key (generate a random one)
SECRET_KEY=generate-a-random-secret-key-here-use-long-random-string
```

**How to add variables:**
- Click **"RAW Editor"** button
- Paste all variables at once
- Click **"Update Variables"**

---

### **Step 6: Run Database Migrations**

Railway doesn't automatically run migrations, so you have two options:

#### **Option A: Manual Migration (One Time)**

1. In Railway, click on your **MySQL database**
2. Go to **"Data"** tab
3. Click **"Query"** tab
4. Copy and paste the contents of these files one by one:
   - `database.sql`
   - `migration_add_status.sql`
   - `migration_2fa.sql`
   - `add_notifications.sql`
5. Click **"Run"** after each one

#### **Option B: Automated (Recommended)**

I'll create a migration script that runs automatically on first deployment.

---

### **Step 7: Deploy**

1. Railway will **automatically deploy** your app
2. Watch the **deployment logs** in the **"Deployments"** tab
3. Wait for the build to complete (2-5 minutes)
4. Once successful, you'll see a green checkmark ✅

---

### **Step 8: Get Your Live URL**

1. Go to **"Settings"** tab
2. Scroll to **"Domains"** section
3. Click **"Generate Domain"**
4. Railway will give you a URL like: `https://pnpsanjuan-production.up.railway.app`
5. **Click the URL** to visit your live app! 🎉

---

## 🔄 Auto-Deploy Setup (Already Configured!)

Railway automatically deploys when you push to GitHub:

1. Make changes to your code locally
2. **Commit in GitHub Desktop**
3. **Push to GitHub**
4. Railway **automatically detects** the push
5. Railway **automatically deploys** the new version
6. Check deployment progress in Railway dashboard

**That's it!** 🚀 Your app updates automatically!

---

## 🛠️ Important Production Settings

### **Generate a Secure Secret Key**

Replace `SECRET_KEY` with a random string. Run this in Python:

```python
import secrets
print(secrets.token_hex(32))
```

Use the output as your `SECRET_KEY` in Railway.

### **Gmail App Password Setup**

1. Enable 2-Step Verification on your Gmail
2. Go to https://myaccount.google.com/apppasswords
3. Create an App Password for "Mail"
4. Use this 16-character password in `SMTP_PASSWORD`

---

## 📊 Monitoring Your App

### **View Logs**
1. Click on your service in Railway
2. Go to **"Deployments"** tab
3. Click on the latest deployment
4. View real-time logs

### **Check Database**
1. Click on MySQL database
2. Go to **"Data"** tab
3. Run SQL queries to check data

---

## 💰 Pricing

### **Railway Pricing (as of 2024)**
- **Free Trial:** $5 credit (no credit card required)
- **Hobby Plan:** $5/month (includes $5 credit)
- **Pro Plan:** $20/month (includes $20 credit)

**Typical usage for your app:**
- ~$3-5/month for small traffic
- Includes database and web service

---

## 🐛 Troubleshooting

### **Build Fails**
- Check **"Deployments" → "View Logs"**
- Make sure `requirements.txt` is correct
- Ensure `Procfile` exists

### **Database Connection Error**
- Verify environment variables are set correctly
- Check that `DB_HOST`, `DB_USER`, etc. use Railway's variables
- Run migrations manually if not done

### **500 Internal Server Error**
- Check deployment logs for Python errors
- Verify all migrations ran successfully
- Check if uploads directory exists

### **Email Not Sending**
- Verify Gmail App Password is correct
- Check SMTP environment variables
- Look for errors in deployment logs

---

## 🔐 Security Checklist

- ✅ Use strong `SECRET_KEY`
- ✅ Use Gmail App Password (not regular password)
- ✅ Add `.env` to `.gitignore` (already done)
- ✅ Never commit passwords to GitHub
- ✅ Use Railway's environment variables for secrets

---

## 📱 Custom Domain (Optional)

Want to use your own domain like `pnpsanjuan.com`?

1. In Railway, go to **Settings → Domains**
2. Click **"Custom Domain"**
3. Enter your domain name
4. Follow DNS setup instructions
5. Railway provides free SSL certificate

---

## 🎯 Next Steps After Deployment

1. **Test the live app thoroughly**
2. **Create an admin account**
3. **Test 2FA with real email**
4. **Configure file uploads** (may need persistent storage)
5. **Set up regular database backups**

---

## 📞 Need Help?

- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **Check deployment logs** for specific errors

---

## 🔄 Development Workflow

```
Local Changes → Commit → Push to GitHub → Railway Auto-Deploys
     ↓              ↓            ↓                    ↓
   Code         GitHub      Automatic          Live Site
  Editor       Desktop       Deploy            Updates
```

**You're all set!** Every time you push to GitHub, Railway updates your production site automatically! 🚀
