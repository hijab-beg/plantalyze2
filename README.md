# Plantalyze - Plant Disease Detection System

🌿 A full-stack web application for plant disease detection using deep learning segmentation.

## 🚀 Features

- 🔬 **UNet Segmentation**: Advanced 3-class segmentation (background, healthy, diseased)
- 📊 **Visual Analysis**: Interactive mask visualization and statistics
- 🎨 **Modern UI**: React + TypeScript + TailwindCSS + Shadcn/ui
- 🔐 **Authentication**: Supabase auth integration
- ☁️ **Serverless**: Deployed on Vercel with Python serverless functions

## 🏗️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development
- **TailwindCSS** + **Shadcn/ui** for styling
- **React Router** for navigation
- **Supabase** for authentication

### Backend
- **Python 3.11** with Flask
- **TensorFlow/Keras** for UNet model
- **OpenCV** for image preprocessing
- **Vercel Serverless Functions** for deployment

## 📁 Project Structure

```
plantalyze-main/
├── api/                          # Vercel Serverless Functions
│   ├── index.py                  # Main API router
│   ├── health.py                 # Health check endpoint
│   ├── analyze.py                # Leaf analysis endpoint
│   └── requirements.txt          # Python dependencies
├── backend/                      # Backend logic (imported by API)
│   ├── preprocessing.py          # Image preprocessing
│   ├── segmentation.py           # UNet model inference
│   ├── classification.py         # Disease classification
│   ├── unet_model.h5            # UNet model file
│   └── Best_ShuffleNet_Model.pth
├── src/                          # React frontend
│   ├── pages/
│   │   ├── Index.tsx            # Landing page
│   │   ├── Dashboard.tsx        # Main analysis UI
│   │   └── Auth.tsx             # Authentication
│   ├── components/              # React components
│   └── integrations/            # Supabase integration
├── vercel.json                  # Vercel configuration
├── VERCEL_DEPLOYMENT.md         # Deployment guide
└── package.json                 # Node dependencies
```

## 🎯 Quick Start

### Prerequisites
- **Node.js 18+** and npm
- **Python 3.11+**
- **Git**

### Local Development

```sh
# Step 1: Clone the repository
git clone <YOUR_GIT_URL>
cd plantalyze-main

# Step 2: Install frontend dependencies
npm install

# Step 3: Set up environment variables
cp .env.example .env.local
# Edit .env.local with your values

# Step 4: Install Python dependencies (for backend)
cd backend
pip install -r requirements.txt
cd ..

# Step 5: Start backend server (in one terminal)
cd backend
python app.py
# Backend runs on http://localhost:5000

# Step 6: Start frontend (in another terminal)
npm run dev
# Frontend runs on http://localhost:8080
```

### Vercel Deployment

See [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md) for complete deployment guide.

Quick deploy:

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy to Vercel
vercel --prod
```

## 🔌 API Endpoints

### `GET /api/health`
Health check endpoint

### `POST /api/analyze`
Analyze leaf image for disease detection

**Request:**
```json
{
  "image": "base64_encoded_image",
  "mimeType": "image/jpeg"
}
```

**Response:**
```json
{
  "isLeaf": true,
  "segmentationMask": "data:image/png;base64,...",
  "maskStats": {
    "backgroundPercent": 25.5,
    "healthyPercent": 60.2,
    "diseasedPercent": 14.3
  }
}
```

## 🧪 Testing

```bash
# Run frontend tests
npm run test

# Test backend API
cd backend
python test_api.py

# Test with Vercel dev server (simulates production)
vercel dev
```

## 📚 Documentation

- [Vercel Deployment Guide](./VERCEL_DEPLOYMENT.md) - Complete Vercel setup
- [Backend Setup](./BACKEND_SETUP.md) - Backend configuration
- [API Documentation](./api/README.md) - API endpoints reference

## 🔧 Configuration

### Environment Variables

```env
# Backend API URL (your Vercel deployment)
VITE_BACKEND_URL=https://your-project.vercel.app

# Supabase (for authentication)
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
```

### Vercel Settings

Configure in `vercel.json`:
- Framework: Vite
- Build command: `npm run build`
- Output directory: `dist`
- Python functions: `/api/*.py`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- UNet architecture for medical image segmentation
- Supabase for backend services
- Vercel for hosting
- Shadcn/ui for components

## 📧 Contact

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ using React, Python, and TensorFlow**
