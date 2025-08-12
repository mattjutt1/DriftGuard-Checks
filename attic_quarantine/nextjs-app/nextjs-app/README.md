# PromptEvolver - AI-Powered Prompt Optimization

A modern web application that uses AI to optimize your prompts for better results. Built with Next.js 14, Convex, and the Qwen3-8B language model running locally via Ollama.

## Features

- 🤖 **AI-Powered Optimization**: Uses Qwen3-8B model for intelligent prompt enhancement
- ⚡ **Real-time Updates**: Built with Convex for instant data synchronization
- 🔒 **Privacy-First**: All AI processing happens locally with Ollama
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile
- 🎯 **Quality Scoring**: Get detailed metrics on prompt improvements
- 📊 **History Tracking**: Keep track of all your optimization sessions

## Tech Stack

- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **Backend**: Convex (serverless database and real-time updates)
- **AI Model**: Qwen3-8B via Ollama (local processing)
- **Deployment**: Vercel (frontend) + Convex (backend)

## Quick Start

### Prerequisites

1. **Node.js 18+** installed
2. **Ollama** installed and running
3. **Qwen3-8B model** downloaded

### Installation

1. **Clone and install dependencies**:

   ```bash
   npm install
   ```

2. **Set up Ollama and Qwen3-8B**:

   ```bash
   # Start Ollama service
   ollama serve

   # Pull Qwen3-8B model (in another terminal)
   ollama pull qwen3:8b
   ```

3. **Set up Convex**:

   ```bash
   # Login and configure Convex (interactive)
   npx convex dev --configure new

   # This will:
   # - Create a new Convex project
   # - Generate your deployment URL
   # - Set up authentication
   ```

4. **Configure environment variables**:

   ```bash
   # Copy example file
   cp .env.local.example .env.local

   # Edit .env.local with your Convex deployment URL
   # (Generated from the previous step)
   ```

5. **Start development**:

   ```bash
   # Start Next.js dev server
   npm run dev

   # In another terminal, keep Convex running
   npx convex dev
   ```

6. **Open the app**:
   Visit [http://localhost:3000](http://localhost:3000)

## How It Works

1. **Enter Your Prompt**: Type or paste the prompt you want to optimize
2. **Add Context** (Optional): Specify the domain (e.g., marketing, technical)
3. **AI Optimization**: Qwen3-8B analyzes and improves your prompt
4. **Review Results**: See the optimized version with quality metrics
5. **Track History**: All optimizations are saved for future reference

## API Health Check

Use the "Check Ollama Health" button to verify:

- ✅ Ollama service is running
- ✅ Qwen3-8B model is available
- ✅ API connectivity is working

## Development

### Project Structure

```
src/
├── app/
│   ├── layout.tsx          # Root layout with Convex provider
│   ├── page.tsx            # Main optimization interface
│   └── ConvexClientProvider.tsx  # Convex React client setup
└── convex/
    ├── schema.ts           # Database schema definitions
    ├── optimizations.ts    # Optimization queries and mutations
    ├── sessions.ts         # Session management functions
    └── actions.ts          # External API actions (Ollama)
```

### Available Scripts

- `npm run dev` - Start Next.js development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npx convex dev` - Start Convex development environment

### Database Schema

The app uses the following main collections:

- **users**: User profiles and preferences
- **prompts**: Original and optimized prompt pairs
- **optimizationSessions**: Processing sessions with metrics
- **feedback**: User ratings and suggestions
- **templates**: Reusable prompt templates

## Deployment

### Vercel + Convex (Recommended)

1. **Deploy Convex backend**:

   ```bash
   npx convex deploy --prod
   ```

2. **Deploy to Vercel**:

   ```bash
   # Connect to Vercel and deploy
   vercel --prod

   # Set environment variables in Vercel dashboard:
   # CONVEX_DEPLOYMENT=your-prod-url
   # NEXT_PUBLIC_CONVEX_URL=your-prod-url
   ```

### Local Ollama Setup for Production

For production deployments, you'll need to:

1. Set up Ollama on your server
2. Configure OLLAMA_BASE_URL in your environment
3. Ensure the Qwen3-8B model is available

## Troubleshooting

### Common Issues

1. **"Ollama service unavailable"**:
   - Ensure `ollama serve` is running
   - Check if port 11434 is accessible

2. **"Qwen3 8B model not found"**:
   - Run `ollama pull qwen3:8b`
   - Verify with `ollama list`

3. **"Unauthenticated" errors**:
   - Set up Convex authentication
   - Check CONVEX_DEPLOYMENT URL

4. **Real-time updates not working**:
   - Verify NEXT_PUBLIC_CONVEX_URL is set
   - Check browser network tab for WebSocket connections

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- 📖 [Convex Documentation](https://docs.convex.dev)
- 🦙 [Ollama Documentation](https://ollama.ai/docs)
- ⚛️ [Next.js Documentation](https://nextjs.org/docs)
- 🤖 [Qwen3 Model Information](https://huggingface.co/Qwen/Qwen3-8B)

---

Built with ❤️ using Next.js, Convex, and the power of local AI processing.
