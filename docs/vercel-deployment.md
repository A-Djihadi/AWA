# AWA Frontend - Production Deployment

## 🚀 Vercel Deployment Guide

### Prerequisites
- Vercel account
- Supabase project
- GitHub repository

### Step 1: Prepare Environment Variables

In your Supabase project dashboard, get:
- Project URL
- Anon key  
- Service role key

### Step 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login and deploy
cd awa
./deploy-vercel.sh
```

### Step 3: Set Environment Variables in Vercel

Go to Vercel Dashboard → Your Project → Settings → Environment Variables:

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### Step 4: Configure Build Settings

Vercel automatically detects Next.js projects. The `vercel.json` file configures:
- Build command: `cd services/frontend && npm run build`
- Output directory: `services/frontend/.next`
- Function settings for API routes

## 🔧 Configuration Files

### vercel.json
- Specifies build and deployment settings
- Configures API functions
- Sets environment variable references

### next.config.js
- Optimized for Vercel (removed `output: 'standalone'`)
- SWC minification enabled
- Console removal in production
- Supabase integration settings

## 📦 Features Deployed

- **Dashboard**: Real-time TJM analytics
- **API Routes**: 
  - `/api/offers` - Job offers CRUD
  - `/api/stats` - Analytics endpoints
- **Supabase Integration**: Direct database access
- **Responsive UI**: Tailwind CSS styling
- **TypeScript**: Full type safety

## 🛡️ Security

- Environment variables properly configured
- Supabase RLS policies enforced
- API routes protected
- CORS headers configured

## 📊 Monitoring

- Vercel Analytics automatically enabled
- Function performance monitoring
- Error tracking via Vercel dashboard
- Real-time deployment logs

## 🔄 Continuous Deployment

Connect your GitHub repository to Vercel for automatic deployments:
1. Import project in Vercel dashboard
2. Connect to GitHub repository
3. Configure build settings
4. Set environment variables
5. Deploy automatically on push to main branch

---

**Live URL**: Will be provided after deployment  
**Admin**: Vercel Dashboard for monitoring and settings
