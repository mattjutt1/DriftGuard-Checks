# Convex Deployment Commands

You're already logged in! Now run these commands:

## Step 1: Navigate to the project

```bash
cd /home/matt/prompt-wizard/nextjs-app
```

## Step 2: Set up Convex project

```bash
npx convex dev
```

When prompted:

- Choose: **"What would you like to configure?"** → Select "a new project"
- Enter project name: **prompt-evolver** (or any name you prefer)
- The dev server will start and configure your project
- Once you see "Watching for file changes", press **Ctrl+C** to stop

## Step 3: Deploy to production

```bash
npx convex deploy
```

This will:

- Deploy all your Convex functions
- Give you a production URL like: `https://xxx.convex.cloud`
- **SAVE THIS URL!** You'll need it for the frontend

## Step 4: Create production environment file

```bash
# Replace YOUR_CONVEX_URL with the URL from step 3
echo "NEXT_PUBLIC_CONVEX_URL=YOUR_CONVEX_URL" > .env.production
```

## Step 5: Test locally with production backend

```bash
npm run build
npm run start
```

Visit <http://localhost:3000> to test

## Step 6: Deploy frontend to Vercel

```bash
vercel --prod
```

Follow the prompts:

- Link to existing project or create new
- Use default settings for Next.js
- Wait for deployment

## Your URLs will be

- **HF Space**: <https://unfiltrdfreedom-prompt-evolver.hf.space> (already working)
- **Convex**: Will be provided after `npx convex deploy`
- **Frontend**: Will be provided by Vercel

---

**Current Status**: You're logged in to Convex ✅

**Next Step**: Run `cd /home/matt/prompt-wizard/nextjs-app && npx convex dev`
