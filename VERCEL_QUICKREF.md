# Vercel Deployment - Quick Reference

Quick commands and tips for deploying Plantalyze to Vercel.

## 🚀 Quick Deploy

```bash
# Install Vercel CLI globally
npm install -g vercel

# Deploy to production
vercel --prod
```

## 📋 Common Commands

### Local Development

```bash
# Start frontend (development)
npm run dev
# → http://localhost:8080

# Start backend (local Flask server)
cd backend && python app.py
# → http://localhost:5000

# Test with Vercel dev environment
vercel dev
# → http://localhost:3000
```

### Vercel CLI

```bash
# Login to Vercel
vercel login

# Link project to Vercel
vercel link

# Deploy to preview
vercel

# Deploy to production
vercel --prod

# Check deployment logs
vercel logs

# List deployments
vercel ls

# Pull environment variables
vercel env pull

# Add environment variable
vercel env add VITE_BACKEND_URL
```

### Model Management

```bash
# Upload model to Vercel Blob Storage
vercel blob upload backend/unet_model.h5

# Using Git LFS
git lfs install
git lfs track "*.h5" "*.pth"
git add .gitattributes backend/*.h5
git commit -m "Add models with LFS"
git push
```

## 🔍 Testing

```bash
# Health check
curl https://your-project.vercel.app/api/health

# Test analyze endpoint (with file)
curl -X POST https://your-project.vercel.app/api/analyze \
  -H "Content-Type: application/json" \
  -d @test_payload.json

# Check build locally
npm run build
# Check dist/ folder
```

## 📝 Environment Variables

```bash
# Create .env.local for development
cp .env.example .env.local

# Edit with your values
# VITE_BACKEND_URL=http://localhost:5000
# VITE_SUPABASE_URL=your_url
# VITE_SUPABASE_ANON_KEY=your_key
```

## 🐛 Troubleshooting

### Check Logs

```bash
# View function logs
vercel logs --follow

# View build logs in Vercel Dashboard
# → Deployments → Select deployment → Logs
```

### Common Fixes

```bash
# Clear Vercel cache
vercel --force

# Rebuild with fresh install
vercel --prod --force

# Check Python dependencies
pip install -r api/requirements.txt

# Test API locally
cd api && python index.py
```

## 📊 Monitoring

```bash
# View analytics
# → Vercel Dashboard → Analytics

# Check function usage
# → Vercel Dashboard → Usage

# Monitor errors
# → Vercel Dashboard → Logs → Filter by "error"
```

## 🔐 Security

```bash
# Add environment variable (production)
vercel env add VITE_BACKEND_URL production

# Add environment variable (all environments)
vercel env add VITE_BACKEND_URL

# Remove environment variable
vercel env rm VITE_BACKEND_URL
```

## 🎯 Deployment Workflow

```bash
# 1. Make changes
git add .
git commit -m "Your changes"

# 2. Test locally
npm run dev
vercel dev

# 3. Push to GitHub
git push origin main

# 4. Auto-deploys to Vercel
# Or manually: vercel --prod
```

## 🔗 Important URLs

- **Vercel Dashboard**: https://vercel.com/dashboard
- **Project Settings**: Vercel Dashboard → Your Project → Settings
- **Environment Variables**: Settings → Environment Variables
- **Deployments**: Vercel Dashboard → Your Project → Deployments
- **Domains**: Settings → Domains

## 💡 Pro Tips

### Speed up development
```bash
# Use environment variables
vercel env pull .env.local

# Test serverless functions locally
vercel dev
```

### Optimize deployment
```bash
# Ignore unnecessary files (see .vercelignore)
# Use production build
npm run build

# Check bundle size
npm run build -- --analyze
```

### Debug issues
```bash
# Check build logs
vercel logs [deployment-url]

# Inspect deployment
vercel inspect [deployment-url]

# Rollback to previous
# Go to Vercel Dashboard → Deployments → ... → Promote to Production
```

## 🎬 First-Time Setup

```bash
# 1. Install CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Navigate to project
cd plantalyze-main

# 4. Deploy
vercel

# 5. Set environment variables in dashboard

# 6. Upload model
vercel blob upload backend/unet_model.h5

# 7. Deploy to production
vercel --prod
```

## 📞 Get Help

```bash
# Vercel help
vercel --help

# Specific command help
vercel deploy --help

# Check version
vercel --version
```

## 🔄 Update Deployment

```bash
# After making changes:
git add .
git commit -m "Update: description"
git push origin main

# Vercel auto-deploys from Git
# Or manually force deploy:
vercel --prod --force
```

---

**Quick Support**: https://vercel.com/support

**Documentation**: https://vercel.com/docs

**Community**: https://github.com/vercel/vercel/discussions
