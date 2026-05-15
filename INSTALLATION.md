# 🚀 Installation & Setup Guide

**IoT Auto Watering System** - Complete Setup Instructions

---

## 📋 Prerequisites

### System Requirements
- **OS**: Windows, macOS, or Linux
- **RAM**: 2GB minimum (4GB recommended)
- **Storage**: 1GB free space

### Software Requirements

#### Backend (Python)
- Python 3.8 or higher
- pip (Python package manager)

**Check Installation**:
```bash
python --version
pip --version
```

#### Frontend (Node.js)
- Node.js 16.x or higher
- npm (comes with Node.js)

**Check Installation**:
```bash
node --version
npm --version
```

#### Hardware (Microcontrollers)
- Arduino IDE 2.x
- USB cables for Arduino & ESP8266
- Board drivers installed

---

## 🔧 Setup Steps

### Step 1: Clone or Download Project

```bash
# If using Git
git clone <your-repo-url>
cd IoT-Auto-Watering-System

# Or extract downloaded ZIP file
cd IoT-Auto-Watering-System-main
```

### Step 2: Setup Backend

#### 2.1 Create Python Virtual Environment

```bash
cd iotdashboard/backend

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

**Output should show**: `Successfully installed fastapi uvicorn sqlalchemy ...`

#### 2.3 Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env file with your settings (development uses SQLite by default)
```

**For Development**: Skip this step (SQLite default)  
**For Production**: Edit `.env` with your PostgreSQL credentials

#### 2.4 Test Backend

```bash
# Start FastAPI server
uvicorn main:app --reload

# Expected output:
# Uvicorn running on http://127.0.0.1:8000
# Press CTRL+C to quit
```

**Verify**:
- Visit http://localhost:8000/ (should return JSON status)
- Visit http://localhost:8000/docs (interactive API documentation)

✅ **Backend Ready**

---

### Step 3: Setup Frontend

#### 3.1 Install Dependencies

```bash
cd iotdashboard/frontend

npm install
```

**Time**: ~2-3 minutes  
**Output should show**: `added XXX packages`

#### 3.2 Configure Environment (Optional)

For custom API URL, create `.env.local`:

```bash
# .env.local
REACT_APP_API_URL=http://localhost:8000
```

#### 3.3 Test Frontend

```bash
npm run dev

# Expected output:
# ➜  Local:   http://localhost:5173/
# ➜  Press q to quit
```

**Verify**:
- Visit http://localhost:5173/
- Dashboard should load without errors
- Check browser console (F12) for errors

✅ **Frontend Ready**

---

### Step 4: Setup Hardware (Microcontrollers)

#### 4.1 Arduino Setup

1. **Open Arduino IDE**
2. **Install Board**:
   - Go to: `Tools → Board Manager`
   - Search for "Arduino AVR"
   - Click Install

3. **Upload Code**:
   - File → Open → `Mikrocontroller Code/Arduino_autowatering.cpp`
   - Select Board: `Tools → Board → Arduino → Arduino Uno`
   - Select Port: `Tools → Port → COM3` (or your port)
   - Click Upload ✓

4. **Verify**:
   - Open Serial Monitor: `Tools → Serial Monitor`
   - Set Baud Rate: **9600**
   - Should see: `[Arduino] Initialization complete`

#### 4.2 ESP8266 Setup

1. **Install Board**:
   - File → Preferences
   - Add to "Additional Boards Manager URLs":
   ```
   http://arduino.esp8266.com/stable/package_esp8266com_index.json
   ```
   - Tools → Board Manager → Search "ESP8266" → Install

2. **Configure Code**:
   - Open `Mikrocontroller Code/esp8266_monitoring.cpp`
   - Replace WiFi credentials:
   ```cpp
   const char* SSID = "YOUR_WIFI_NAME";
   const char* PASSWORD = "YOUR_WIFI_PASSWORD";
   const char* SERVER_URL = "http://YOUR_COMPUTER_IP:8000/sensor";
   ```
   - Find your computer IP:
     - **Windows**: `ipconfig` → Look for "IPv4 Address"
     - **macOS/Linux**: `ifconfig` → Look for "inet"

3. **Upload Code**:
   - Select Board: `Tools → Board → ESP8266 → NodeMCU 1.0 (ESP-12E Module)`
   - Select Port: `COM4` (or your port)
   - Click Upload ✓

4. **Verify**:
   - Open Serial Monitor: `Tools → Serial Monitor`
   - Set Baud Rate: **115200** (different from Arduino!)
   - Should show WiFi connection messages

✅ **Hardware Ready**

---

## 🧪 Testing the Complete System

### Test 1: Data Flow (Manual)

```bash
# Terminal 1: Backend
cd iotdashboard/backend
python -m venv venv
# activate venv
uvicorn main:app --reload

# Terminal 2: Frontend
cd iotdashboard/frontend
npm run dev

# Terminal 3: Simulator (optional, if no hardware)
cd iotdashboard/backend
python simulator.py

# Terminal 4: Check API
curl http://localhost:8000/sensor/latest
```

### Test 2: With Hardware

1. Power on Arduino & ESP8266
2. Watch serial monitors
3. Open http://localhost:5173/
4. Verify data appears in dashboard
5. Check http://localhost:8000/docs for API responses

---

## 🛠️ Troubleshooting

### Issue: Backend won't start
```bash
# Error: "Address already in use"
# Solution: Port 8000 is taken, use different port
uvicorn main:app --port 8001

# Error: "ModuleNotFoundError: fastapi"
# Solution: Activate venv and reinstall
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Frontend shows "Failed to fetch"
```bash
# Check if backend is running
curl http://localhost:8000/

# Check CORS setting in .env
# Make sure ALLOWED_ORIGINS includes http://localhost:5173

# Check browser console (F12) for exact error
```

### Issue: Serial baud rate mismatch
```
# Arduino & ESP8266 MUST both use 9600
# Check Arduino: Serial.begin(9600)
# Check ESP8266: Serial.begin(9600)
# NOT 115200!
```

### Issue: No data from ESP8266
```
# Check WiFi credentials in code
# Check SERVER_URL points to correct IP
# Verify firewall allows port 8000
# Check both devices on same network
```

### Issue: Database errors
```bash
# For SQLite (default development):
rm iot_watering.db
# Database will recreate on next run

# For PostgreSQL:
# Check DATABASE_URL in .env
# Verify database server is running
# Check credentials
```

---

## 📦 Production Deployment

### Option 1: Local Network (Recommended for Home Use)

```bash
# Backend
cd iotdashboard/backend
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend build
cd ../frontend
npm run build
# Serve dist/ folder with any web server
```

### Option 2: Docker (Advanced)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY iotdashboard/backend/requirements.txt .
RUN pip install -r requirements.txt
COPY iotdashboard/backend .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t iot-backend .
docker run -p 8000:8000 -e DATABASE_URL=postgresql://... iot-backend
```

### Option 3: Cloud Deployment (Azure/AWS)

See deployment-specific guides in `/deployment` folder (if available)

---

## ✅ Verification Checklist

- [ ] Python virtual environment activated
- [ ] Backend dependencies installed (`pip list` shows fastapi)
- [ ] Node.js dependencies installed (`npm list | head`)
- [ ] .env file configured (or using defaults)
- [ ] Arduino code uploaded and running (Serial monitor shows output)
- [ ] ESP8266 code uploaded and running (Serial monitor shows WiFi connect)
- [ ] Backend API responding (`curl http://localhost:8000/`)
- [ ] Frontend dashboard loads (`http://localhost:5173/`)
- [ ] Data flowing from hardware → API → Dashboard
- [ ] No critical errors in console

---

## 🚀 Quick Start Commands

```bash
# Backend (Terminal 1)
cd iotdashboard/backend && source venv/bin/activate && uvicorn main:app --reload

# Frontend (Terminal 2)
cd iotdashboard/frontend && npm run dev

# Simulator/Testing (Terminal 3, if no hardware)
cd iotdashboard/backend && python simulator.py

# Check API health
curl http://localhost:8000/

# View API documentation
open http://localhost:8000/docs

# View Dashboard
open http://localhost:5173/
```

---

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Arduino IDE**: https://www.arduino.cc/en/software
- **ESP8266 Community**: https://github.com/esp8266/Arduino

---

## 💡 Tips

1. **Keep terminals organized**: Use VS Code split terminal or separate terminal windows
2. **Hot reload**: Both backend and frontend support live reload during development
3. **API Testing**: Use Postman or VS Code REST Client for API testing
4. **Database**: SQLite is file-based, easy for development. Switch to PostgreSQL for production
5. **Logs**: Check console output for detailed error messages

---

**Status**: ✅ Ready to proceed!

If you encounter any issues not listed above, check:
1. `PRODUCTION_FIXES.md` for known issues
2. `README.md` for project overview
3. Browser console (F12) for frontend errors
4. Backend terminal output for server errors
