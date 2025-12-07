# Socify Frontend - Setup Instructions

## Overview

This is the complete frontend for Socify SIEM, recreated EXACTLY from the original GitHub repository:
https://github.com/Krish142005/SOCify.git

## Technology Stack

- **Next.js 15.5.3** with App Router
- **React 19.1.0**
- **TypeScript 5**
- **Tailwind CSS 4** with custom cyberpunk theme
- **Framer Motion** for animations
- **Lucide React** for icons
- **Radix UI** components
- **Recharts** for data visualization

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout with fonts
│   │   ├── page.tsx            # Home/Dashboard page
│   │   └── globals.css         # Global styles (cyberpunk theme)
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── ThreatMap.tsx   # Animated radar visualization
│   │   │   └── ThreatStats.tsx # Animated bar chart
│   │   ├── layout/
│   │   │   ├── DashboardLayout.tsx  # Main layout wrapper
│   │   │   ├── Navbar.tsx      # Top navigation bar
│   │   │   └── Sidebar.tsx     # Side navigation menu
│   │   └── ui/
│   │       └── Card.tsx        # Reusable card component
│   └── lib/
│       └── utils.ts            # Utility functions (cn)
├── package.json
├── tsconfig.json
├── next.config.ts
├── postcss.config.mjs
└── components.json

```

## Installation

### Step 1: Install Dependencies

```powershell
cd frontend
npm install
```

This will install all dependencies including:
- Next.js 15.5.3
- React 19.1.0
- Tailwind CSS 4
- All UI libraries (Radix UI, Framer Motion, Lucide React)

### Step 2: Configure API Endpoint

The frontend is already configured to connect to your local backend at:
```
http://localhost:8000
```

If you need to change this, update the API calls in the components (currently using fetch with relative URLs that will proxy to the backend).

### Step 3: Run Development Server

```powershell
npm run dev
```

The frontend will start at: **http://localhost:3000**

## Features

### Cyberpunk UI Theme

The frontend features a custom cyberpunk-inspired design with:
- **Neon colors**: Cyber blue (#00f5ff), neon green (#39ff14), purple (#9d4edd)
- **Glassmorphism effects**: Backdrop blur and transparency
- **Glow animations**: Pulsing and glowing elements
- **Dark mode**: Enabled by default
- **Custom animations**: Marquee ticker, pulse effects

### Components

#### Dashboard (page.tsx)
- Live threat radar visualization
- Active incidents display
- Threat distribution charts
- Real-time statistics

#### ThreatMap.tsx
- Animated radar sweep
- Pulsing threat indicators
- Color-coded by severity (red/orange/cyan)
- Canvas-based rendering

#### ThreatStats.tsx
- Animated bar chart
- Threat category breakdown
- Glow effects
- Real-time updates

#### Navbar.tsx
- User profile
- Notifications
- Search functionality
- Quick actions

#### Sidebar.tsx
- Navigation menu
- Dashboard, Logs, Alerts, Rules pages
- Active state indicators
- Collapsible design

### Styling

All styles are in `src/app/globals.css` with:
- CSS custom properties for theming
- Tailwind CSS utility classes
- Custom animations (@keyframes)
- Cyberpunk-inspired effects

## API Integration

To connect to your local backend, the components will make API calls to:

```typescript
// Example API calls (update as needed in components)
const response = await fetch('http://localhost:8000/api/logs');
const response = await fetch('http://localhost:8000/api/alerts');
const response = await fetch('http://localhost:8000/api/rules');
```

## Build for Production

```powershell
# Build
npm run build

# Start production server
npm start
```

## Customization

### Changing Colors

Edit `src/app/globals.css`:
```css
.dark {
  --primary: #00f5ff; /* Change cyber blue */
  --secondary: #39ff14; /* Change neon green */
  --accent: #9d4edd; /* Change purple */
}
```

### Adding New Pages

Create new route folders in `src/app/`:
```
src/app/logs/page.tsx
src/app/alerts/page.tsx
src/app/rules/page.tsx
```

### Modifying Components

All components are in `src/components/` and can be edited directly.

## Troubleshooting

### Module not found errors

```powershell
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### TypeScript errors

```powershell
# Check TypeScript
npx tsc --noEmit
```

### Tailwind CSS not working

```powershell
# Rebuild Tailwind
npm run dev
```

## Exact Match with Original Repository

This frontend is an EXACT recreation of the original repository with:
- ✅ Same folder structure
- ✅ Same file names
- ✅ Same component code
- ✅ Same styling and CSS
- ✅ Same dependencies and versions
- ✅ Same Next.js configuration

**Only change**: API endpoints point to `http://localhost:8000` instead of cloud URLs.

## Next Steps

1. Start the backend: `cd ../backend && .\start.bat`
2. Start the frontend: `npm run dev`
3. Open browser: `http://localhost:3000`
4. View the cyberpunk SIEM dashboard!

## Support

For issues with the frontend:
1. Check that all dependencies are installed: `npm install`
2. Verify Node.js version: `node --version` (should be 18+)
3. Check console for errors in browser DevTools
4. Ensure backend is running at `http://localhost:8000`
