# Frontend Documentation

The `frontend` directory contains the modern React web application that serves as the user interface for the Mindfulness Productivity Assistant. It connects to the FastAPI backend and provides a polished, responsive experience.

## 📁 Project Structure

```
frontend/
├── public/              # Static assets (favicons, manifests)
├── src/
│   ├── assets/          # Images and other static files
│   ├── components/      # Reusable React components
│   │   ├── TaskDashboard.jsx  # Main task view
│   │   ├── ScheduleView.jsx   # Weekly calendar view
│   │   ├── TimerView.jsx      # Pomodoro/Focus timer
│   │   ├── AnalyticsView.jsx  # Charts and data visualization
│   │   └── ...
│   ├── contexts/        # React Contexts for global state
│   │   ├── AuthContext.jsx       # User session management
│   │   ├── ThemeContext.jsx      # Dark/Light mode toggle
│   │   └── NotificationContext.jsx # Toast notifications
│   ├── api.js           # Axios instance and API definition
│   ├── App.jsx          # Main layout and routing logic
│   └── main.jsx         # Entry point (providers setup)
├── index.html           # HTML template
├── tailwind.config.js   # Tailwind CSS configuration
└── vite.config.js       # Vite build configuration
```

## ⚛️ Key Components

### 1. Main Navigation (`App.jsx`)
The application uses a tab-based navigation system rather than client-side routing for immediate transitions. The state is managed via `activeTab`.

```jsx
// Simplified from App.jsx
function App() {
  const [activeTab, setActiveTab] = useState('tasks');
  const { isDark } = useTheme();

  const renderTab = () => {
    switch (activeTab) {
      case 'tasks': return <TaskDashboard />;
      case 'schedule': return <ScheduleView />;
      // ...
    }
  };
  
  return (
    <div className={isDark ? 'bg-black' : 'bg-slate-50'}>
      <Sidebar setActiveTab={setActiveTab} />
      <main>{renderTab()}</main>
    </div>
  );
}
```

### 2. API Layer (`api.js`)
All backend communication is centralized in `api.js` using `axios`. This ensures consistent error handling and base URL configuration.

```javascript
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api',
});

export const simulationApi = {
    run: (userName, days) => api.post('/simulation/run', { user_name: userName, days }),
    getHistory: (userName) => api.get(`/simulation/history/${userName}`),
};
```

### 3. Theme System (`contexts/ThemeContext.jsx`)
The app features a robust dark/light mode system using a React Context. It leverages Tailwind's data-driven styling or class-based dark mode.

### 4. Authentication (`contexts/AuthContext.jsx`)
Handles user login/logout and persistence.

## 🎨 Styling Architecture
The project uses **Tailwind CSS** for styling, with a focus on:
- **Gradients**: `bg-gradient-to-r from-emerald-500 to-teal-500`
- **Glassmorphism**: Backdrop blur effects for modern UI depth.
- **Responsiveness**: Mobile-first design principles.

## 🚀 Running the Frontend
1. Install dependencies: `npm install`
2. Start dev server: `npm run dev`
3. Build for production: `npm run build`
