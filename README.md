<<<<<<< HEAD
# 🚌 Metro Bus 360 - Intelligent Transit Management System

A state-of-the-art, real-time bidirectional metro bus simulation and management system powered by AI. This platform integrates live tracking, intelligent journey planning, traffic simulation, E-Ticket system, and comprehensive administrative controls into a unified solution.

## 🌟 Key Systems & Features

### 🌐 Core Simulation Engine (`bus_simulator.py`)
- **Bidirectional Service**: Simultaneous forward and reverse bus operations on all routes.
- **High-Fidelity Simulation**: Supports up to **10 buses per route** with alternating terminal departures every 10 seconds.
- **Traffic Intelligence**: Real-time traffic segment simulation with dynamic congestion levels (Free Flow, Moderate, Heavy) affecting bus speeds.
- **AI-Powered ETA**: Machine learning-based `AIETAPredictor` that continuously refines arrival times based on traffic, distance, and historical data.

### 🧠 Intelligent Journey Planning (`journey_planner.py`)
- **Multi-Route Planning**: Finds optimal paths using **A* Algorithm** and graph-based transfer logic.
- **Smart Transfers**: Automatically identifies optimal transfer points between intersecting routes.
- **Holistic Scoring**: Ranks journeys based on time, cost, walking distance, number of transfers, and even **carbon footprint**.
- **Real-Time Accuracy**: Plans are generated using live bus positions and traffic delays, not just static schedules.

### 🎫 E-Ticket System (`eticket_endpoints.py`)
- **User Authentication**: Login/Signup system with user profiles stored in JSON database
- **Senior Citizen Benefits**: FREE travel for users aged 60+ 
- **Digital Wallet**: Top-up and manage wallet balance
- **Multiple Payment Methods**: EasyPaisa, JazzCash, NayaPay, SadaPay integration (simulation)
- **Dynamic Fare Calculation**: Fares calculated based on route distance (Rs. 10/km, minimum Rs. 20)
- **Active Route Filtering**: Only purchase tickets for currently active routes with running buses

### 👮 Administrator Dashboard (`admin_endpoints.py` & `multi_route_management.py`)
- **Fleet Management**: Real-time monitoring of "Healthy", "Warning", and "Critical" status fleets.
- **Driver Management**: Rostering, shift assignment, and performance tracking (on-time rates, passenger feedback).
- **Route Controls**: Dynamic activation/deactivation of routes, maintenance mode toggles.
- **Crisis Management**: "Deploy Spare Bus" capability for rush hour or emergency demand.
- **Broadcast System**: Send system-wide announcements to all connected clients via WebSockets.

### 📱 Mobile Application (React Native)
- **Cross-Platform**: Built with React Native and TypeScript for iOS and Android.
- **Live Tracking**: Real-time bus movement on interactive maps.
- **Floating UI**: Clean map view with floating circular buttons for Stats, Bus List, and E-Ticket
- **Modal Interface**: Statistics and bus information displayed in elegant slide-up modals

---

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Server**: Uvicorn (ASGI)
- **Real-time**: WebSockets (Broadcasts updates every 3s)
- **Database**: SQLite with `database_manager.py` (DAL)
- **E-Ticket Storage**: JSON file-based user database
- **Geospatial**: `geopy` for distance calculations

### Frontend (Web)
- **Map Engine**: Leaflet.js with OpenStreetMap tiles
- **UI**: Custom HTML5/CSS3 with linear gradient aesthetics and responsive design
- **Interaction**: Dynamic DOM updates via WebSocket payloads
- **E-Ticket Interface**: Integrated modal system with authentication and payment

### Mobile
- **Framework**: React Native 0.73
- **Language**: TypeScript
- **Maps**: React Native WebView displaying Leaflet maps
- **Testing**: Jest (Unit testing infrastructure present)

---

## 📂 Project Structure
```
FYP/
├── main.py                          # 🚀 Application Entry Point & API/WS Router
├── bus_simulator.py                 # 🚌 Core Logic (Movement, Traffic, ETA AI)
├── journey_planner.py               # 🗺️ A* Journey Finding & Transfer Logic
├── admin_endpoints.py               # 👮 Admin API (Stats, Alerts, Drivers)
├── eticket_endpoints.py             # 🎫 E-Ticket System API
├── multi_route_management.py        # 🚦 Route Lifecycle & Performance Metrics
├── database_manager.py              # 💾 SQLite Data Access Layer
├── map_visualizer.py                # 🌐 Static Map Utilities (Folium)
├── web_template.html                # 🖥️ Web Interface Template
├── metro_simulation.db              # 🗄️ Main Database File
├── eticket_users.json               # 👥 E-Ticket User Database
├── requirements.txt                 # 📦 Python Dependencies
├── venv/                            # 🐍 Python Virtual Environment
└── mobile/                          # 📱 Mobile Applications
    ├── MetroBusApp073/              #    React Native 0.73 (Recommended)
    │   ├── src/
    │   │   ├── screens/
    │   │   │   ├── MapScreen.tsx    #    Main mobile interface
    │   │   │   └── AdminDashboardScreen.tsx
    │   │   ├── services/            #    API & WebSocket services
    │   │   ├── context/             #    React Context providers
    │   │   └── config/              #    Configuration files
    │   ├── android/                 #    Android native code
    │   ├── ios/                     #    iOS native code
    │   ├── App.tsx                  #    App entry point
    │   └── package.json             #    Node dependencies
    └── MetroBusApp082/              #    React Native 0.82 (Backup)
```

---

## ⚡ Quick Start

### 🖥️ Backend Setup (Web Application)

**Prerequisites**: 
- Python 3.8+
- pip (Python package manager)

#### 1. Create and Activate Virtual Environment

**Linux/Mac:**
```bash
cd ~/Desktop/FYP
python3 -m venv venv
source venv/Scripts/activate
```

**Windows:**
```cmd
cd C:\Users\YourName\Desktop\FYP
python -m venv venv
venv\bin\activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Run the Backend Server
```bash
python main.py
```

Or with Uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The system will initialize:
1. **Database**: Auto-create `metro_simulation.db` and seed routes/stops.
2. **E-Ticket System**: Create `eticket_users.json` for user data.
3. **Simulation**: Start background threads for bus movement and traffic.
4. **Server**: Listen on `http://localhost:8000`.

**Server will be running at:**
- Main API: `http://localhost:8000`
- Live Map: `http://localhost:8000/map`
- Admin Dashboard: `http://localhost:8000/admin`
- API Docs: `http://localhost:8000/docs`

---

### 🌐 Web Application Access

Once the backend is running:

1. **Live Tracking Map**: http://localhost:8000/map
   - Real-time bus positions
   - Route visualization
   - Journey planning interface
   - E-Ticket purchase (click 🎫 E-Ticket button)

2. **Admin Dashboard**: http://localhost:8000/admin
   - Fleet management
   - Route activation/deactivation
   - Driver management
   - System statistics

3. **API Documentation**: http://localhost:8000/docs
   - Interactive Swagger UI
   - Test all API endpoints

---

### 📱 Mobile Application Setup

**Prerequisites**:
- Node.js 16+ and npm
- Android Studio (for Android) or Xcode (for iOS/Mac only)
- Java 17 (for Android)
- Android SDK

#### 1. Install Dependencies
```bash
cd ~/Desktop/FYP/mobile/MetroBusApp073
npm install
```

#### 2. Setup Android Environment (Linux)
```bash
# Set environment variables
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export ANDROID_HOME=~/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

Add these to your `~/.bashrc` or `~/.zshrc` for persistence:
```bash
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
echo 'export ANDROID_HOME=~/Android/Sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools' >> ~/.bashrc
source ~/.bashrc
```

#### 3. Start Metro Bundler

**Terminal 1:**
```bash
cd ~/Desktop/FYP/mobile/MetroBusApp073
npm start -- --reset-cache
```

Wait until you see: `✓ Metro is ready`

#### 4. Setup Port Forwarding (for Android Emulator)

**Terminal 2:**
```bash
# Forward ports from emulator to localhost
adb reverse tcp:8081 tcp:8081  # Metro bundler
adb reverse tcp:8000 tcp:8000  # Backend API
```

#### 5. Run Android App

**Terminal 3:**
```bash
cd ~/Desktop/FYP/mobile/MetroBusApp073
npm run android
```

Or manually:
```bash
npx react-native run-android
```

**For physical device via USB:**
1. Enable USB Debugging on your Android phone
2. Connect via USB
3. Run: `adb devices` to verify connection
4. Run: `npm run android`

---

### 🎯 Complete Startup Sequence

For best results, start in this order:

**Terminal 1 - Backend:**
```bash
cd ~/Desktop/FYP
source venv/Scripts/activate
python main.py
```

**Terminal 2 - Metro Bundler:**
```bash
cd ~/Desktop/FYP/mobile/MetroBusApp073
npm start -- --reset-cache
```

**Terminal 3 - Android App:**
```bash
cd ~/Desktop/FYP/mobile/MetroBusApp073
adb reverse tcp:8081 tcp:8081
adb reverse tcp:8000 tcp:8000
npm run android
```

---

## 📌 API Endpoints Summary

### Public / User Endpoints

#### Bus & Route Information
- `GET /api/buses` - Real-time locations of all active buses
- `GET /api/routes` - List all available routes
- `GET /api/simulation/status` - Complete system status (buses, routes, stats)

#### Traffic & ETA
- `GET /api/traffic/current` - Live traffic segment data
- `GET /api/eta/bus/{bus_id}` - AI-predicted ETA for specific bus
- `GET /api/eta/all` - ETA predictions for all active buses

#### Journey Planning
- `POST /api/journey/plan` - Plan a trip (Origin → Destination)
- `GET /api/journey/transfer-points` - Find optimal transfer locations
- `POST /api/journey/quick-plan` - Fast journey planning with minimal transfers

#### E-Ticket System
- `POST /api/eticket/signup` - Create new user account
```json
  {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "03001234567",
    "age": 25,
    "password": "password123"
  }
```
- `POST /api/eticket/login` - User authentication
- `GET /api/eticket/active-routes` - Get routes with active buses for ticket purchase
- `POST /api/eticket/topup` - Add money to wallet
- `POST /api/eticket/purchase` - Purchase bus ticket

### Administrator Endpoints

#### Fleet Management
- `GET /api/admin/statistics` - System health, uptime, bus counts
- `GET /api/admin/alerts` - Real-time delay & incident alerts
- `GET /api/admin/fleet-status` - Detailed fleet health metrics

#### Route Management
- `POST /api/routes/activate` - Activate a route
- `POST /api/routes/deactivate` - Deactivate a route
- `GET /api/routes/statistics` - Per-route performance metrics
- `GET /api/routes/available` - List all system routes

#### Driver Management
- `GET /api/admin/drivers` - List all drivers
- `POST /api/admin/driver/assign` - Assign driver to bus
- `GET /api/admin/driver/{driver_id}` - Driver details and performance

#### System Operations
- `POST /api/admin/announcement` - Broadcast messages to all users
- `POST /api/admin/rush-hour/deploy-spare` - Deploy additional bus to route
- `POST /api/routes/deactivate-all` - Emergency shutdown of all routes

---

## 🎫 E-Ticket System Usage

### Web Interface

1. **Access Map**: http://localhost:8000/map
2. **Click E-Ticket Button**: Pink gradient button in header
3. **Sign Up**: 
   - Enter name, email, phone, age, password
   - Users 60+ automatically get FREE travel status
4. **Top Up Wallet**: Select amount and payment method
5. **Purchase Ticket**: 
   - Select from active routes only
   - Fare auto-calculated (Rs. 10/km, min Rs. 20)
   - Free for senior citizens (60+)

### Mobile App

1. **Open App**: Mobile interface with floating buttons
2. **Tap 🎫 Button**: Opens E-Ticket modal
3. **Login/Signup**: Same as web interface
4. **Purchase**: Select route and complete payment

### User Data Storage

User accounts stored in: `eticket_users.json`
```json
{
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "03001234567",
      "age": 25,
      "balance": 500,
      "is_senior": false,
      "created_at": "2026-02-13T10:30:00"
    }
  ]
}
```

---

## 🔧 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --port 8001
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Database errors:**
```bash
# Reset database
rm metro_simulation.db
python main.py  # Will recreate automatically
```

### Mobile App Issues

**Metro bundler connection failed:**
```bash
# Clear cache and restart
cd ~/Desktop/FYP/mobile/MetroBusApp073
npm start -- --reset-cache
```

**App not loading on emulator:**
```bash
# Reset port forwarding
adb reverse --remove-all
adb reverse tcp:8081 tcp:8081
adb reverse tcp:8000 tcp:8000

# Reload app
Press 'R' twice in emulator
# Or shake device and select "Reload"
```

**Build errors:**
```bash
# Clean and rebuild
cd android
./gradlew clean
cd ..
npm run android
```

**"Unable to load script" error:**
```bash
# 1. Make sure Metro bundler is running
# 2. Set up port forwarding
adb reverse tcp:8081 tcp:8081
# 3. Reload app (RR or shake menu)
```

---

## 🧪 Testing

### Backend Testing
```bash
# Run with pytest (if tests exist)
pytest tests/

# Manual API testing via docs
# Visit: http://localhost:8000/docs
```

### Mobile Testing
```bash
cd mobile/MetroBusApp073
npm test
```

---

## 📊 System Monitoring

### Real-time Statistics (Web)
- Visit: http://localhost:8000/admin
- Monitor: Active buses, routes, delays, fleet health

### WebSocket Connection (Development)
```javascript
// Connect to live updates
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Bus Update:', data);
};
```

---

## 🌟 Features Highlight

### ✅ Implemented
- [x] Real-time bidirectional bus tracking
- [x] AI-powered ETA predictions
- [x] Intelligent journey planning with A* algorithm
- [x] Traffic simulation and visualization
- [x] Admin dashboard with fleet management
- [x] Driver roster and performance tracking
- [x] E-Ticket system with digital wallet
- [x] Senior citizen benefits (FREE travel for 60+)
- [x] Multiple payment method simulation
- [x] Dynamic fare calculation based on distance
- [x] Active route filtering for ticket purchase
- [x] Mobile app with floating UI and modal system
- [x] WebSocket real-time updates
- [x] Route activation/deactivation controls

### 🚀 Future Roadmap
- [ ] Passenger capacity visualization (Heatmaps)
- [ ] Integration with hardware GPS modules
- [ ] Real payment gateway integration
- [ ] Push notifications for bus arrivals
- [ ] Offline mode for mobile app
- [ ] Multi-language support
- [ ] Accessibility features (voice guidance)
- [ ] Integration with Google Maps
- [ ] QR code ticket validation
- [ ] Passenger feedback system

---

## 👥 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is developed as a Final Year Project (FYP) for academic purposes.

---

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Contact project maintainers
- Check API documentation: http://localhost:8000/docs

---

## 🙏 Acknowledgments

- OpenStreetMap for map tiles
- Leaflet.js for mapping library
- FastAPI framework
- React Native community
- All open-source contributors

---

**Made with ❤️ for Pakistan's Public Transport System**
=======
# 🚌 Metro Bus 360 - Intelligent Transit Management System

A state-of-the-art, real-time bidirectional metro bus simulation and management system powered by AI. This platform integrates live tracking, intelligent journey planning, traffic simulation, E-Ticket system, and comprehensive administrative controls into a unified solution.

## 🌟 Key Systems & Features

### 🌐 Core Simulation Engine (`bus_simulator.py`)
- **Bidirectional Service**: Simultaneous forward and reverse bus operations on all routes.
- **High-Fidelity Simulation**: Supports up to **10 buses per route** with alternating terminal departures every 10 seconds.
- **Traffic Intelligence**: Real-time traffic segment simulation with dynamic congestion levels (Free Flow, Moderate, Heavy) affecting bus speeds.
- **AI-Powered ETA**: Machine learning-based `AIETAPredictor` that continuously refines arrival times based on traffic, distance, and historical data.

### 🧠 Intelligent Journey Planning (`journey_planner.py`)
- **Multi-Route Planning**: Finds optimal paths using **A* Algorithm** and graph-based transfer logic.
- **Smart Transfers**: Automatically identifies optimal transfer points between intersecting routes.
- **Holistic Scoring**: Ranks journeys based on time, cost, walking distance, number of transfers, and even **carbon footprint**.
- **Real-Time Accuracy**: Plans are generated using live bus positions and traffic delays, not just static schedules.

### 🎫 E-Ticket System (`eticket_endpoints.py`)
- **User Authentication**: Login/Signup system with user profiles stored in JSON database
- **Senior Citizen Benefits**: FREE travel for users aged 60+ 
- **Digital Wallet**: Top-up and manage wallet balance
- **Multiple Payment Methods**: EasyPaisa, JazzCash, NayaPay, SadaPay integration (simulation)
- **Dynamic Fare Calculation**: Fares calculated based on route distance (Rs. 10/km, minimum Rs. 20)
- **Active Route Filtering**: Only purchase tickets for currently active routes with running buses

### 👮 Administrator Dashboard (`admin_endpoints.py` & `multi_route_management.py`)
- **Fleet Management**: Real-time monitoring of "Healthy", "Warning", and "Critical" status fleets.
- **Driver Management**: Rostering, shift assignment, and performance tracking (on-time rates, passenger feedback).
- **Route Controls**: Dynamic activation/deactivation of routes, maintenance mode toggles.
- **Crisis Management**: "Deploy Spare Bus" capability for rush hour or emergency demand.
- **Broadcast System**: Send system-wide announcements to all connected clients via WebSockets.

### 📱 Mobile Application (React Native)
- **Cross-Platform**: Built with React Native and TypeScript for iOS and Android.
- **Live Tracking**: Real-time bus movement on interactive maps.
- **Floating UI**: Clean map view with floating circular buttons for Stats, Bus List, and E-Ticket
- **Modal Interface**: Statistics and bus information displayed in elegant slide-up modals

---

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Server**: Uvicorn (ASGI)
- **Real-time**: WebSockets (Broadcasts updates every 3s)
- **Database**: SQLite with `database_manager.py` (DAL)
- **E-Ticket Storage**: JSON file-based user database
- **Geospatial**: `geopy` for distance calculations

### Frontend (Web)
- **Map Engine**: Leaflet.js with OpenStreetMap tiles
- **UI**: Custom HTML5/CSS3 with linear gradient aesthetics and responsive design
- **Interaction**: Dynamic DOM updates via WebSocket payloads
- **E-Ticket Interface**: Integrated modal system with authentication and payment

### Mobile
- **Framework**: React Native 0.73
- **Language**: TypeScript
- **Maps**: React Native WebView displaying Leaflet maps
- **Testing**: Jest (Unit testing infrastructure present)

---

## 📂 Project Structure
```
FYP/
├── main.py                          # 🚀 Application Entry Point & API/WS Router
├── bus_simulator.py                 # 🚌 Core Logic (Movement, Traffic, ETA AI)
├── journey_planner.py               # 🗺️ A* Journey Finding & Transfer Logic
├── admin_endpoints.py               # 👮 Admin API (Stats, Alerts, Drivers)
├── eticket_endpoints.py             # 🎫 E-Ticket System API
├── multi_route_management.py        # 🚦 Route Lifecycle & Performance Metrics
├── database_manager.py              # 💾 SQLite Data Access Layer
├── map_visualizer.py                # 🌐 Static Map Utilities (Folium)
├── web_template.html                # 🖥️ Web Interface Template
├── metro_simulation.db              # 🗄️ Main Database File
├── eticket_users.json               # 👥 E-Ticket User Database
├── requirements.txt                 # 📦 Python Dependencies
├── venv/                            # 🐍 Python Virtual Environment
└── mobile/                          # 📱 Mobile Applications
    ├── MetroBusApp073/              #    React Native 0.73 (Recommended)
    │   ├── src/
    │   │   ├── screens/
    │   │   │   ├── MapScreen.tsx    #    Main mobile interface
    │   │   │   └── AdminDashboardScreen.tsx
    │   │   ├── services/            #    API & WebSocket services
    │   │   ├── context/             #    React Context providers
    │   │   └── config/              #    Configuration files
    │   ├── android/                 #    Android native code
    │   ├── ios/                     #    iOS native code
    │   ├── App.tsx                  #    App entry point
    │   └── package.json             #    Node dependencies
    └── MetroBusApp082/              #    React Native 0.82 (Backup)
```

---

## ⚡ Quick Start

### 🖥️ Backend Setup (Web Application)

**Prerequisites**: 
- Python 3.8+
- pip (Python package manager)

#### 1. Create and Activate Virtual Environment

**Linux/Mac:**
```bash
cd ~/Desktop/FYP
python3 -m venv venv
source venv/Scripts/activate
```

**Windows:**
```cmd
cd C:\Users\YourName\Desktop\FYP
python -m venv venv
venv\bin\activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Run the Backend Server
```bash
python main.py
```

Or with Uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The system will initialize:
1. **Database**: Auto-create `metro_simulation.db` and seed routes/stops.
2. **E-Ticket System**: Create `eticket_users.json` for user data.
3. **Simulation**: Start background threads for bus movement and traffic.
4. **Server**: Listen on `http://localhost:8000`.

**Server will be running at:**
- Main API: `http://localhost:8000`
- Live Map: `http://localhost:8000/map`
- Admin Dashboard: `http://localhost:8000/admin`
- API Docs: `http://localhost:8000/docs`

---

### 🌐 Web Application Access

Once the backend is running:

1. **Live Tracking Map**: http://localhost:8000/map
   - Real-time bus positions
   - Route visualization
   - Journey planning interface
   - E-Ticket purchase (click 🎫 E-Ticket button)

2. **Admin Dashboard**: http://localhost:8000/admin
   - Fleet management
   - Route activation/deactivation
   - Driver management
   - System statistics

3. **API Documentation**: http://localhost:8000/docs
   - Interactive Swagger UI
   - Test all API endpoints

---

### 📱 Mobile Application Setup

**Prerequisites**:
- Node.js 16+ and npm
- Android Studio (for Android) or Xcode (for iOS/Mac only)
- Java 17 (for Android)
- Android SDK

#### 1. Install Dependencies
```bash
cd ~/Desktop/FYP/mobile/MetroBusApp073
npm install
```

#### 2. Setup Android Environment (Linux)
```bash
# Set environment variables
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export ANDROID_HOME=~/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

Add these to your `~/.bashrc` or `~/.zshrc` for persistence:
```bash
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
echo 'export ANDROID_HOME=~/Android/Sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools' >> ~/.bashrc
source ~/.bashrc
```

#### 3. Start Metro Bundler

**Terminal 1:**
```bash
cd ~/Desktop/FYP/mobile/MetroBusApp073
npm start -- --reset-cache
```

Wait until you see: `✓ Metro is ready`

#### 4. Setup Port Forwarding (for Android Emulator)

**Terminal 2:**
```bash
# Forward ports from emulator to localhost
adb reverse tcp:8081 tcp:8081  # Metro bundler
adb reverse tcp:8000 tcp:8000  # Backend API
```

#### 5. Run Android App

**Terminal 3:**
```bash
cd ~/Desktop/FYP/mobile/MetroBusApp073
npm run android
```

Or manually:
```bash
npx react-native run-android
```

**For physical device via USB:**
1. Enable USB Debugging on your Android phone
2. Connect via USB
3. Run: `adb devices` to verify connection
4. Run: `npm run android`

---

### 🎯 Complete Startup Sequence

For best results, start in this order:

**Terminal 1 - Backend:**
```bash
cd ~/Desktop/FYP
source venv/Scripts/activate
python main.py
```

**Terminal 2 - Metro Bundler:**
```bash
cd ~/Desktop/FYP/mobile/MetroBusApp073
npm start -- --reset-cache
```

**Terminal 3 - Android App:**
```bash
cd ~/Desktop/FYP/mobile/MetroBusApp073
adb reverse tcp:8081 tcp:8081
adb reverse tcp:8000 tcp:8000
npm run android
```

---

## 📌 API Endpoints Summary

### Public / User Endpoints

#### Bus & Route Information
- `GET /api/buses` - Real-time locations of all active buses
- `GET /api/routes` - List all available routes
- `GET /api/simulation/status` - Complete system status (buses, routes, stats)

#### Traffic & ETA
- `GET /api/traffic/current` - Live traffic segment data
- `GET /api/eta/bus/{bus_id}` - AI-predicted ETA for specific bus
- `GET /api/eta/all` - ETA predictions for all active buses

#### Journey Planning
- `POST /api/journey/plan` - Plan a trip (Origin → Destination)
- `GET /api/journey/transfer-points` - Find optimal transfer locations
- `POST /api/journey/quick-plan` - Fast journey planning with minimal transfers

#### E-Ticket System
- `POST /api/eticket/signup` - Create new user account
```json
  {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "03001234567",
    "age": 25,
    "password": "password123"
  }
```
- `POST /api/eticket/login` - User authentication
- `GET /api/eticket/active-routes` - Get routes with active buses for ticket purchase
- `POST /api/eticket/topup` - Add money to wallet
- `POST /api/eticket/purchase` - Purchase bus ticket

### Administrator Endpoints

#### Fleet Management
- `GET /api/admin/statistics` - System health, uptime, bus counts
- `GET /api/admin/alerts` - Real-time delay & incident alerts
- `GET /api/admin/fleet-status` - Detailed fleet health metrics

#### Route Management
- `POST /api/routes/activate` - Activate a route
- `POST /api/routes/deactivate` - Deactivate a route
- `GET /api/routes/statistics` - Per-route performance metrics
- `GET /api/routes/available` - List all system routes

#### Driver Management
- `GET /api/admin/drivers` - List all drivers
- `POST /api/admin/driver/assign` - Assign driver to bus
- `GET /api/admin/driver/{driver_id}` - Driver details and performance

#### System Operations
- `POST /api/admin/announcement` - Broadcast messages to all users
- `POST /api/admin/rush-hour/deploy-spare` - Deploy additional bus to route
- `POST /api/routes/deactivate-all` - Emergency shutdown of all routes

---

## 🎫 E-Ticket System Usage

### Web Interface

1. **Access Map**: http://localhost:8000/map
2. **Click E-Ticket Button**: Pink gradient button in header
3. **Sign Up**: 
   - Enter name, email, phone, age, password
   - Users 60+ automatically get FREE travel status
4. **Top Up Wallet**: Select amount and payment method
5. **Purchase Ticket**: 
   - Select from active routes only
   - Fare auto-calculated (Rs. 10/km, min Rs. 20)
   - Free for senior citizens (60+)

### Mobile App

1. **Open App**: Mobile interface with floating buttons
2. **Tap 🎫 Button**: Opens E-Ticket modal
3. **Login/Signup**: Same as web interface
4. **Purchase**: Select route and complete payment

### User Data Storage

User accounts stored in: `eticket_users.json`
```json
{
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "03001234567",
      "age": 25,
      "balance": 500,
      "is_senior": false,
      "created_at": "2026-02-13T10:30:00"
    }
  ]
}
```

---

## 🔧 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --port 8001
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Database errors:**
```bash
# Reset database
rm metro_simulation.db
python main.py  # Will recreate automatically
```

### Mobile App Issues

**Metro bundler connection failed:**
```bash
# Clear cache and restart
cd ~/Desktop/FYP/mobile/MetroBusApp073
npm start -- --reset-cache
```

**App not loading on emulator:**
```bash
# Reset port forwarding
adb reverse --remove-all
adb reverse tcp:8081 tcp:8081
adb reverse tcp:8000 tcp:8000

# Reload app
Press 'R' twice in emulator
# Or shake device and select "Reload"
```

**Build errors:**
```bash
# Clean and rebuild
cd android
./gradlew clean
cd ..
npm run android
```

**"Unable to load script" error:**
```bash
# 1. Make sure Metro bundler is running
# 2. Set up port forwarding
adb reverse tcp:8081 tcp:8081
# 3. Reload app (RR or shake menu)
```

---

## 🧪 Testing

### Backend Testing
```bash
# Run with pytest (if tests exist)
pytest tests/

# Manual API testing via docs
# Visit: http://localhost:8000/docs
```

### Mobile Testing
```bash
cd mobile/MetroBusApp073
npm test
```

---

## 📊 System Monitoring

### Real-time Statistics (Web)
- Visit: http://localhost:8000/admin
- Monitor: Active buses, routes, delays, fleet health

### WebSocket Connection (Development)
```javascript
// Connect to live updates
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Bus Update:', data);
};
```

---

## 🌟 Features Highlight

### ✅ Implemented
- [x] Real-time bidirectional bus tracking
- [x] AI-powered ETA predictions
- [x] Intelligent journey planning with A* algorithm
- [x] Traffic simulation and visualization
- [x] Admin dashboard with fleet management
- [x] Driver roster and performance tracking
- [x] E-Ticket system with digital wallet
- [x] Senior citizen benefits (FREE travel for 60+)
- [x] Multiple payment method simulation
- [x] Dynamic fare calculation based on distance
- [x] Active route filtering for ticket purchase
- [x] Mobile app with floating UI and modal system
- [x] WebSocket real-time updates
- [x] Route activation/deactivation controls

### 🚀 Future Roadmap
- [ ] Passenger capacity visualization (Heatmaps)
- [ ] Integration with hardware GPS modules
- [ ] Real payment gateway integration
- [ ] Push notifications for bus arrivals
- [ ] Offline mode for mobile app
- [ ] Multi-language support
- [ ] Accessibility features (voice guidance)
- [ ] Integration with Google Maps
- [ ] QR code ticket validation
- [ ] Passenger feedback system

---

## 👥 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is developed as a Final Year Project (FYP) for academic purposes.

---

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Contact project maintainers
- Check API documentation: http://localhost:8000/docs

---

## 🙏 Acknowledgments

- OpenStreetMap for map tiles
- Leaflet.js for mapping library
- FastAPI framework
- React Native community
- All open-source contributors

---

**Made with ❤️ for Pakistan's Public Transport System**
>>>>>>> f39032e1ee9266d572fbe4fe875815534e3604c0
