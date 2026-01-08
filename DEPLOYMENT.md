# 🚀 Deploying to Render.com

This guide will help you deploy the Documentation Consistency Assistant on Render.com for free.

## Prerequisites

1. GitHub account with your repository pushed
2. Render.com account (free tier available)
3. (Optional) OpenAI API key for LLM features

## Step 1: Push Latest Code to GitHub

```bash
cd /home/shaltonkennedy/documentation_consistency
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

## Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Click "Sign up" with GitHub (recommended)
3. Authorize Render to access your GitHub repositories

## Step 3: Deploy on Render

### Option A: Using Web Interface (Easiest)

1. Log in to Render Dashboard
2. Click "+ New +" → "Web Service"
3. Select "documentation_consistency" repository
4. Fill in the form:
   - **Name**: `documentation-consistency` (or any name)
   - **Runtime**: `Python 3.11`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=10000 --server.address=0.0.0.0`
5. **Environment Variables** (optional):
   - Add `OPENAI_API_KEY` if you want LLM features
6. Click "Create Web Service"

### Option B: Using render.yaml (Already Configured)

1. The `render.yaml` file is already in the repo
2. In Render Dashboard: "+" → "Web Service"
3. Select your repository
4. Render will auto-detect `render.yaml` and use those settings
5. Just click "Create Web Service"

## Step 4: Add Environment Variables (Optional)

For LLM features to work on Render:

1. In Render Dashboard, go to your service
2. Click "Environment" tab
3. Add a new environment variable:
   - **Key**: `OPENAI_API_KEY`
   - **Value**: Your OpenAI API key (starts with `sk-`)
   - Make sure "Scope: Runtime" is selected

**Note**: If you don't add OpenAI key, the app will still work in "heuristic mode" (no AI suggestions).

## Step 5: Monitor Deployment

1. The build will start automatically
2. Watch the "Logs" tab for build progress
3. Deployment typically takes 2-3 minutes
4. Once "Your service is live" appears, click the URL to access your app

## Step 6: Usage

Your app will be available at: `https://documentation-consistency-<random-id>.onrender.com`

Share this URL with others to test!

## Troubleshooting

### "Build failed"
- Check logs for Python errors
- Ensure `requirements.txt` has all dependencies
- Check that `app.py` is in the root directory

### "Service is running but not responding"
- Streamlit might be restarting. Wait 30 seconds.
- Check that port is set to `10000` in startCommand
- Verify `app.py` doesn't have syntax errors

### "Port 10000 in use"
- Render assigns ports dynamically; this is expected
- The startCommand handles it with `--server.port=10000`

### Slow uploads
- Free tier has limited resources
- Large ZIPs (>50MB) may timeout
- Use the local version for large projects

## Costs

- **Free tier**: ~2 CPU cores, 512MB RAM
- **Limitations**: Service spins down after 15 min of inactivity (cold start)
- **Upgrade**: ~$7/month for always-on

For production use, consider upgrading or using `--no-timeout` flag.

## Updating the Deployment

After making changes locally:

```bash
git add .
git commit -m "Update features"
git push origin main
```

Render automatically re-deploys when you push to `main` branch.

## Advanced: Custom Domain

If you have a domain:
1. In Render Dashboard → Service Settings
2. Click "Custom Domain"
3. Add your domain and update DNS records
4. Render provides instructions

## Support

- [Render Docs](https://render.com/docs)
- [Streamlit on Render](https://render.com/docs/deploy-streamlit)
- [GitHub Issues](https://github.com/SOLARIS-bit/documentation_consistency/issues)

---

**Congratulations!** Your app is now live and accessible to anyone. 🎉

You can now share `https://documentation-consistency-<id>.onrender.com` with teams and competitors like CraftAI DocSync!
