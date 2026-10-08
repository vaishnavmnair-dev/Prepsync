# 🚀 How to Deploy AdaptiveStudy AI for Free (100% Free Hosting)

This guide shows you the fastest, easiest ways to deploy **AdaptiveStudy AI** online with a public HTTPS link (perfect for sharing with judges, teammates, or college submissions) at **zero cost**.

---

## ⚡ Summary of Best Free Options

| Platform | Best For | Deploy Time | Setup Required |
| :--- | :--- | :---: | :---: |
| **1. Netlify Drop** | Instant Demo link | **30 seconds** | **None** (Just Drag & Drop folder) |
| **2. Vercel** | Fast, Custom domain, Production grade | **1 minute** | GitHub or `npx vercel` |
| **3. GitHub Pages** | Permanent student project portfolio | **2 minutes** | Push to GitHub |
| **4. Render.com** | Full-Stack (Frontend + FastAPI backend) | **3 minutes** | GitHub repo link |

---

## 🥇 Option 1: Netlify Drop (Fastest — 30 Seconds, No Code or Git Needed!)

Netlify Drop lets you host static web apps by literally dragging your folder into the browser.

1. Open your browser and go to: **[https://app.netlify.com/drop](https://app.netlify.com/drop)**
2. Sign in or sign up with GitHub/Google (free).
3. Open Windows File Explorer to:
   ```text
   D:\college\semester-1\Ideathon\project\prototype-2\Frontend
   ```
4. **Drag and drop the entire `Frontend` folder** into the box on the Netlify webpage.
5. In 5 seconds, Netlify generates a live, public HTTPS URL like:
   `https://adaptive-study-ai.netlify.app`
6. *(Optional)* Click **"Site configuration"** -> **"Change site name"** to give it a custom name like `my-study-planner.netlify.app`.

---

## 🥈 Option 2: Vercel (1-Minute CLI or GitHub Deploy)

Vercel provides lightning-fast global edge hosting and free SSL.

### Method A: Via Vercel CLI (Right from your terminal)
In your terminal, run:
```powershell
cd d:\college\semester-1\Ideathon\project\prototype-2\Frontend
npx vercel
```
1. Press `Enter` to confirm deployment.
2. Select your free Vercel account.
3. Accept the default settings.
4. In under 30 seconds, you get a live `https://adaptive-study-xxx.vercel.app` link!

### Method B: Via GitHub
1. Push your repository to GitHub.
2. Go to **[vercel.com](https://vercel.com)** -> Click **"Add New Project"**.
3. Import your GitHub repository.
4. Set **Root Directory** to `Frontend`.
5. Click **Deploy**.

---

## 🥉 Option 3: GitHub Pages (Permanent & Free)

1. Initialize Git and push your repository to GitHub:
   ```powershell
   git init
   git add .
   git commit -m "Initial commit of AdaptiveStudy AI"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```
2. On GitHub, go to your repository **Settings** -> **Pages** (on the left sidebar).
3. Under **Build and deployment** -> **Branch**:
   - Select `main` branch.
   - Select folder `/Frontend` (or move files to root/docs).
4. Click **Save**.
5. Your app will be live at:
   `https://<your-username>.github.io/<your-repo-name>/`

---

## 🛠️ Option 4: Deploying the FastAPI Backend (Render.com — 100% Free)

The frontend works **100% independently** with offline `localStorage` and client-side scheduling. If you also want your Python/FastAPI backend live on the cloud:

1. Push your code to GitHub.
2. Go to **[render.com](https://render.com)** and sign in with GitHub.
3. Click **New +** -> **Web Service**.
4. Connect your GitHub repository.
5. Configure the service:
   - **Name**: `adaptivestudy-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: **Free** ($0/month)
6. Click **Create Web Service**.
7. Render gives you a public API URL like: `https://adaptivestudy-backend.onrender.com`.
8. In your frontend, paste that URL in the settings or test `/health` directly!

---

## 💡 Quick Tips for Ideathon Presentation
- **Netlify Drop** is the quickest way to get a URL onto your phone or presentation slides right away.
- Use the **"Phone Preview"** toggle button in the header during your pitch to demonstrate how the UI looks on mobile devices!

