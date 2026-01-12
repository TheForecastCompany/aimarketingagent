# Content Repurposer Frontend

A professional, responsive frontend for the Content Repurposing Agency built with Next.js, TypeScript, and Tailwind CSS.

## 🚀 Features

### Core Functionality
- **Video Processing**: Upload and process videos from YouTube, Vimeo, and Loom
- **Multi-Platform Content Generation**: Generate content for LinkedIn, Twitter, Facebook, Instagram
- **Real-Time Processing**: Live progress tracking and status updates
- **Content Management**: View, edit, and export generated content
- **Analytics Dashboard**: Track performance metrics and insights

### User Experience
- **Responsive Design**: Optimized for mobile, tablet, and desktop
- **Dark/Light Mode**: Toggle between themes
- **Loading States**: Professional loading skeletons and progress indicators
- **Error Handling**: Comprehensive error messages and retry logic
- **Empty States**: Helpful guidance when no data is available

### Technical Features
- **TypeScript**: Full type safety across the application
- **Modern Stack**: Next.js 16, React 19, Tailwind CSS 4
- **Component Library**: Built with shadcn/ui components
- **State Management**: Zustand for global state
- **Form Validation**: React Hook Form with Zod schemas
- **API Integration**: Axios with retry logic and error handling

## 🛠️ Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **Components**: shadcn/ui
- **State Management**: Zustand
- **Forms**: React Hook Form + Zod
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Notifications**: Sonner

## 📁 Project Structure

```
frontend./
├── app/                    # Next.js App Router pages
│   ├── page.tsx            # Dashboard
│   ├── process/            # Video processing page
│   ├── results/            # Results display page
│   ├── analytics/           # Analytics dashboard
│   ├── history/            # Processing history
│   ├── settings/           # Application settings
│   └── layout.tsx         # Root layout
├── components/             # Reusable components
│   ├── ui/                # shadcn/ui components
│   ├── layout/            # Layout components
│   ├── common/            # Common components
│   ├── forms/             # Form components
│   └── display/           # Display components
├── hooks/                 # Custom React hooks
├── services/              # API and external services
├── types/                 # TypeScript type definitions
└── lib/                   # Utility functions
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd windsurf-project/frontend.
```

2. Install dependencies
```bash
npm install
```

3. Start the development server
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Build for Production

```bash
npm run build
npm start
```

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Content Repurposer
```

### API Configuration

The frontend connects to a Python backend API. Ensure your backend is running and accessible at the configured API URL.

## 📱 Responsive Design

The application is fully responsive with breakpoints:
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px  
- **Desktop**: > 1024px

## 🎨 Theming

### Dark Mode
- Toggle between light and dark themes
- User preference is persisted in localStorage
- System preference detection

### Customization
- Tailwind CSS configuration in `tailwind.config.js`
- CSS variables in `app/globals.css`
- Component theming via shadcn/ui

## 🔐 Security

- Input validation with Zod schemas
- XSS protection through React's built-in escaping
- CSRF protection via Next.js
- Secure API communication

## 📊 Performance

- Code splitting with Next.js
- Image optimization
- Lazy loading components
- Efficient state management
- Minimal bundle size

## 🧪 Testing

```bash
# Run linting
npm run lint

# Type checking
npm run type-check
```

## 📚 API Integration

### Video Processing
```typescript
const result = await apiClient.processVideo({
  video_url: "https://youtube.com/watch?v=...",
  config: {
    brand_voice: BrandVoice.PROFESSIONAL,
    keywords: ["AI", "technology"],
    enable_critique: true,
    track_costs: true
  }
});
```

### State Management
```typescript
// Access state
const config = useConfig();
const processing = useProcessing();

// Update state
const { setConfig } = useAppActions();
setConfig({ brand_voice: BrandVoice.CASUAL });
```

## 🎯 Key Features

### Video Processing Flow
1. **URL Input**: Validate video URL
2. **Configuration**: Set brand voice, keywords, and options
3. **Processing**: Real-time progress tracking
4. **Results**: Multi-tab content display
5. **Export**: Download content in various formats

### Content Types Generated
- **Social Media**: Platform-specific posts (LinkedIn, Twitter, Facebook, Instagram)
- **Newsletter**: Email newsletter content
- **Blog Post**: SEO-optimized blog articles
- **Scripts**: Video scripts for different formats
- **Analytics**: SEO analysis and performance metrics

### User Preferences
- Brand voice selection
- Default keywords
- Processing options
- Theme preferences
- Notification settings

## 🚀 Deployment

### Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Configure environment variables
3. Deploy automatically on push to main branch

### Other Platforms
The application can be deployed to any platform supporting Next.js:
- Netlify
- AWS Amplify
- Railway
- Digital Ocean App Platform

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the documentation
- Review the code comments
- Open an issue on GitHub

---

Built with ❤️ using Next.js, TypeScript, and Tailwind CSS
