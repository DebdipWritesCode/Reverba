# Reverba

**Reverba** is an AI-powered vocabulary learning application that helps users master new words through personalized daily tasks and interactive tutoring. The platform uses intelligent task generation, priority-based learning, and AI evaluation to create an effective vocabulary learning experience.

## 🌟 Features

### Core Learning Features
- **Word Management**: Add, update, and organize vocabulary words with custom meanings and examples
- **Priority-Based Learning System**: Words progress through 4 priority levels (1-4) based on performance
- **Daily Task Generation**: Automatically generated tasks at 1 AM daily with up to 8 tasks per day
- **AI-Powered Evaluation**: OpenAI integration for intelligent assessment of user responses
- **Interactive AI Tutor**: Chat with an AI tutor for personalized learning assistance

### Task Types
1. **MEANING Tasks**: Provide the meaning of a word
2. **SENTENCE Tasks**: Create sentences using words correctly
3. **MCQ Tasks**: Multiple-choice questions with pre-generated options
4. **PARAGRAPH Tasks**: Write meaningful paragraphs (minimum 50 words) using words

### User Features
- **User Authentication**: Secure signup, login, email verification, and password reset
- **Dashboard**: Comprehensive statistics and progress tracking
- **Task History**: View and review past learning sessions
- **Word Mastery System**: Track mastery count and mark words as mastered
- **Dark/Light Theme**: Modern UI with theme switching support

### Admin Features
- **User Management**: Admin panel for managing users and system administration

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT tokens (access + refresh tokens)
- **AI Integration**: OpenAI API (GPT-4o-mini)
- **Email Service**: Resend API
- **Task Scheduling**: APScheduler for daily task generation
- **Password Hashing**: bcrypt
- **API Documentation**: FastAPI auto-generated docs

### Frontend
- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite
- **State Management**: Redux Toolkit
- **Routing**: React Router v7
- **UI Components**: Radix UI primitives
- **Styling**: Tailwind CSS v4
- **Form Handling**: React Hook Form with Zod validation
- **HTTP Client**: Axios
- **Icons**: Lucide React

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Deployment**: Vercel (frontend), configurable backend hosting

## 📁 Project Structure

```
Reverba/
├── backend/
│   ├── app/
│   │   ├── cron/              # Scheduled task generation
│   │   ├── middleware/         # Authentication middleware
│   │   ├── models/             # Pydantic models
│   │   ├── routers/            # API route handlers
│   │   ├── services/           # Business logic
│   │   ├── settings/           # Environment configuration
│   │   ├── templates/          # Email templates
│   │   ├── utils/              # Utility functions
│   │   ├── database.py         # MongoDB connection
│   │   └── main.py             # FastAPI application
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   └── trigger_daily_tasks.py  # Manual task trigger script
│
└── frontend/
    ├── src/
    │   ├── api/                # API client functions
    │   ├── components/         # React components
    │   │   └── ui/             # Reusable UI components
    │   ├── layouts/            # Layout components
    │   ├── pages/              # Page components
    │   ├── router/             # Route configuration
    │   ├── store/              # Redux store and slices
    │   └── utils/              # Utility functions
    ├── package.json
    ├── vite.config.ts
    └── vercel.json
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- Node.js 18+ and npm
- MongoDB (local or cloud instance)
- OpenAI API key
- Resend API key (for email functionality)
- Docker and Docker Compose (optional, for containerized setup)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file** in the `backend` directory:
   ```env
   # Database
   MONGO_URI=mongodb://localhost:27017/reverba

   # Authentication
   ACCESS_TOKEN_SECRET=your-access-token-secret-here
   REFRESH_TOKEN_SECRET=your-refresh-token-secret-here
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MIN=15
   REFRESH_TOKEN_EXPIRE_DAYS=30

   # OpenAI
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_MODEL=gpt-4o-mini

   # Cron
   CRON_TIMEZONE=Asia/Kolkata

   # Email (Resend)
   RESEND_API_KEY=your-resend-api-key
   RESEND_FROM_EMAIL=noreply@yourdomain.com

   # Application
   APP_SECRET_KEY=your-app-secret-key
   APP_ENV=development
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173
   ```

5. **Run the backend**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Or using Docker:
   ```bash
   docker-compose up --build
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create `.env` file** in the `frontend` directory:
   ```env
   VITE_BACKEND_URL=http://localhost:8000
   ```

4. **Run the development server**:
   ```bash
   npm run dev
   ```

5. **Build for production**:
   ```bash
   npm run build
   ```

## 📚 API Documentation

Once the backend is running, you can access:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Key API Endpoints

#### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/verify-email` - Verify email address
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password

#### Words
- `GET /api/words` - Get all words (with optional filters)
- `POST /api/words` - Create a new word
- `POST /api/words/batch` - Create multiple words
- `GET /api/words/{word_id}` - Get a specific word
- `PUT /api/words/{word_id}` - Update a word
- `DELETE /api/words/{word_id}` - Delete a word
- `POST /api/words/{word_id}/promote` - Increase word priority
- `POST /api/words/{word_id}/demote` - Decrease word priority
- `POST /api/words/{word_id}/master` - Mark word as mastered

#### Tasks
- `GET /api/tasks/today` - Get today's daily tasks
- `POST /api/tasks/{task_id}/complete` - Complete a task

#### Tutor
- `POST /api/tutor/evaluate` - Evaluate user response (MEANING/SENTENCE/PARAGRAPH)
- `POST /api/tutor/chat/{chat_id}` - Continue chat conversation
- `GET /api/tutor/chat/{chat_id}` - Get chat history
- `GET /api/tutor/chats` - List user's chat history

#### Dashboard
- `GET /api/dashboard` - Get dashboard statistics

#### Admin
- `GET /api/admin/users` - List all users (admin only)
- `GET /api/admin/stats` - Get admin statistics (admin only)

## 🎯 How It Works

### Daily Task Generation
1. Tasks are automatically generated every day at 1 AM (configurable timezone)
2. Word selection based on priority:
   - Priority 1: 1 word → MEANING task
   - Priority 2: 2 words → SENTENCE tasks (2 separate tasks)
   - Priority 3: 3 words → MCQ tasks (3 separate tasks)
   - Priority 4: 2 words → PARAGRAPH tasks (2 separate tasks)
3. Total: Up to 8 tasks per day

### Priority System
- Words start at Priority 1 when added
- Non-selected words: Priority increases by 1 (max 4)
- After task completion:
  - **PASS**: Priority set to 1
  - **FAIL**: Priority set to 2, failure stats incremented
- Words can be manually promoted/demoted
- Words can be marked as "mastered" after 3 successful Priority 4 completions

### AI Evaluation
- **MEANING/SENTENCE/PARAGRAPH**: Evaluated by OpenAI with strict criteria
- First failure: Provides hint without revealing answer
- Second failure: Reveals expected answer
- **MCQ**: Pre-generated during task creation, evaluated on frontend
- Chat continuation available after evaluation for unlimited learning

## 🔒 Security Features

- JWT-based authentication with access and refresh tokens
- Password hashing with bcrypt
- Email verification for new accounts
- Secure password reset flow
- CORS configuration for API security
- Environment-based configuration
- Input validation with Pydantic models

## 🧪 Development

### Running Tests
```bash
# Backend tests (if available)
cd backend
pytest

# Frontend tests (if available)
cd frontend
npm test
```

### Code Quality
```bash
# Frontend linting
cd frontend
npm run lint
```

### Manual Task Trigger
For development/testing, you can manually trigger daily task generation:
```bash
cd backend
python trigger_daily_tasks.py
```

## 🐳 Docker Deployment

### Backend
```bash
cd backend
docker-compose up --build
```

The backend will be available at `http://localhost:8000`

## 📝 Environment Variables

### Backend Required Variables
- `MONGO_URI`: MongoDB connection string
- `ACCESS_TOKEN_SECRET`: Secret for JWT access tokens
- `REFRESH_TOKEN_SECRET`: Secret for JWT refresh tokens
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `RESEND_API_KEY`: Resend API key for emails
- `RESEND_FROM_EMAIL`: Sender email address
- `APP_SECRET_KEY`: Application secret key

### Frontend Required Variables
- `VITE_BACKEND_URL`: Backend API URL

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is private and proprietary.

## 🆘 Support

For issues, questions, or contributions, please open an issue in the repository.

---

**Built with ❤️ for vocabulary learners**
