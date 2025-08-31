# AWA Frontend - Vercel Deployment

This directory contains the Next.js frontend optimized for Vercel deployment.

## Environment Variables Required

Set these in your Vercel project settings:

```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

## Deployment Steps

1. **Connect to Vercel**:
   ```bash
   npm i -g vercel
   vercel login
   vercel link
   ```

2. **Set Environment Variables**:
   ```bash
   vercel env add NEXT_PUBLIC_SUPABASE_URL
   vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY
   vercel env add SUPABASE_SERVICE_ROLE_KEY
   ```

3. **Deploy**:
   ```bash
   vercel --prod
   ```

## Local Development

```bash
cd services/frontend
npm install
npm run dev
```

## Build Optimization

- SWC minification enabled for faster builds
- Console.log removal in production
- Optimized for Vercel's edge runtime
- Supabase SSR integration

## API Routes

API routes are automatically deployed as Vercel Functions with:
- 1GB memory allocation
- 10s maximum duration
- Automatic scaling

## Features

- Real-time TJM analytics dashboard
- Supabase integration for data
- Responsive design with Tailwind CSS
- Charts with Recharts
- TypeScript support
- ESLint configuration
