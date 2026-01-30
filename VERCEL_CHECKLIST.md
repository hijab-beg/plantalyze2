# Vercel Deployment Checklist

Use this checklist to ensure your Plantalyze application is ready for Vercel deployment.

## 📋 Pre-Deployment Checklist

### ✅ Code & Configuration

- [ ] All code committed to Git
- [ ] `vercel.json` configuration exists
- [ ] `api/requirements.txt` has all dependencies
- [ ] `.env.example` created with all required variables
- [ ] `.vercelignore` excludes unnecessary files
- [ ] `runtime.txt` specifies Python 3.11

### ✅ Environment Variables

- [ ] `VITE_BACKEND_URL` configured (your Vercel domain)
- [ ] `VITE_SUPABASE_URL` configured
- [ ] `VITE_SUPABASE_ANON_KEY` configured
- [ ] All environment variables added to Vercel dashboard

### ✅ Backend Files

- [ ] `backend/unet_model.h5` exists (or plan for upload)
- [ ] `backend/preprocessing.py` tested
- [ ] `backend/segmentation.py` tested
- [ ] All imports work correctly

### ✅ API Functions

- [ ] `api/index.py` created
- [ ] `api/health.py` created
- [ ] `api/analyze.py` created
- [ ] CORS configured properly

### ✅ Frontend

- [ ] API calls use `/api/analyze` endpoint
- [ ] Environment variables referenced correctly
- [ ] Build command works: `npm run build`
- [ ] No hardcoded localhost URLs

### ✅ Testing

- [ ] Backend runs locally: `python backend/app.py`
- [ ] Frontend runs locally: `npm run dev`
- [ ] Image upload works
- [ ] Segmentation produces results
- [ ] Error handling works

## 🚀 Deployment Steps

### Step 1: Connect Repository

- [ ] Repository pushed to GitHub
- [ ] Go to [vercel.com](https://vercel.com)
- [ ] Click "New Project"
- [ ] Import your GitHub repository

### Step 2: Configure Project

- [ ] Framework detected as "Vite"
- [ ] Build command: `npm run build`
- [ ] Output directory: `dist`
- [ ] Install command: `npm install`

### Step 3: Set Environment Variables

Add in Vercel Dashboard → Settings → Environment Variables:

- [ ] `VITE_BACKEND_URL` = `https://your-project.vercel.app`
- [ ] `VITE_SUPABASE_URL` = your Supabase URL
- [ ] `VITE_SUPABASE_ANON_KEY` = your Supabase anon key

### Step 4: Upload Model Files

Choose one method:

**Option A: Vercel Blob Storage**
```bash
vercel blob upload backend/unet_model.h5
```
- [ ] Model uploaded successfully

**Option B: Git LFS**
```bash
git lfs install
git lfs track "*.h5"
git add .gitattributes backend/unet_model.h5
git commit -m "Add model with LFS"
git push
```
- [ ] Git LFS configured
- [ ] Model tracked and pushed

**Option C: External CDN**
- [ ] Model uploaded to CDN
- [ ] Download URL configured in code

### Step 5: Deploy

- [ ] Click "Deploy" in Vercel
- [ ] Wait for build to complete
- [ ] Check deployment logs for errors

### Step 6: Verify Deployment

- [ ] Visit deployment URL
- [ ] Test `/api/health` endpoint
- [ ] Test image upload
- [ ] Test segmentation analysis
- [ ] Check console for errors
- [ ] Test on mobile device

## 🔍 Post-Deployment Verification

### API Health Check

```bash
curl https://your-project.vercel.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Plantalyze API is running on Vercel"
}
```

- [ ] Health endpoint responds correctly

### Full Analysis Test

1. Go to your deployment URL
2. Log in (if authentication required)
3. Upload a test leaf image
4. Click "Analyze"
5. Verify segmentation mask appears
6. Check statistics are correct

- [ ] Full workflow works end-to-end

### Performance Check

- [ ] First request completes (cold start)
- [ ] Subsequent requests faster (warm)
- [ ] No timeout errors
- [ ] Images process within 10s (Free) or 60s (Pro)

### Error Handling

- [ ] Invalid image shows error
- [ ] Non-leaf image detected
- [ ] Network errors handled gracefully
- [ ] Model errors logged properly

## 📊 Monitoring

### Vercel Dashboard

Monitor in Vercel Dashboard:

- [ ] Check Analytics for visitor data
- [ ] Review Logs for function execution
- [ ] Monitor Performance metrics
- [ ] Check Usage (bandwidth, functions)

### Common Issues

| Issue | Solution |
|-------|----------|
| "Model not found" | Upload model to Vercel or configure CDN |
| Function timeout | Upgrade to Pro or optimize preprocessing |
| Module not found | Check `api/requirements.txt` |
| CORS errors | Verify CORS configuration in API |
| Build fails | Check build logs, verify dependencies |

## 🔐 Security Checklist

- [ ] Environment variables not in code
- [ ] `.env` files in `.gitignore`
- [ ] CORS restricted to specific origins (production)
- [ ] File upload size limits enforced
- [ ] Input validation implemented
- [ ] Error messages don't expose sensitive info

## 🎯 Optimization

- [ ] Images compressed before upload
- [ ] Model file optimized (< 50MB)
- [ ] Cold start time acceptable
- [ ] Caching enabled where possible
- [ ] CDN used for static assets

## 📈 Production Ready

- [ ] All tests passing
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Fast page load times
- [ ] SEO meta tags added
- [ ] Analytics configured
- [ ] Error tracking set up
- [ ] Custom domain connected (optional)

## 🆘 Rollback Plan

If deployment fails:

- [ ] Rollback to previous deployment in Vercel
- [ ] Check logs for error messages
- [ ] Test locally with `vercel dev`
- [ ] Fix issues and redeploy

## ✨ Final Steps

- [ ] Update README with deployment URL
- [ ] Document any custom configuration
- [ ] Share with team/stakeholders
- [ ] Monitor for 24 hours after launch
- [ ] Collect user feedback

---

**Deployment Date**: ____________

**Deployed By**: ____________

**Deployment URL**: ____________

**Status**: ⬜ Pending | ⬜ In Progress | ⬜ Complete | ⬜ Issues

**Notes**:
