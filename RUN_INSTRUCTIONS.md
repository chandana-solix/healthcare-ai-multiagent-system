# 🚀 How to Run the Healthcare AI Web Application

## Quick Start (Easiest Method)

### Option 1: Using Terminal/Command Line

1. **Open Terminal** (on Mac: Press Cmd+Space, type "Terminal", press Enter)

2. **Navigate to the project directory:**
   ```bash
   cd /Users/nandichandana/Downloads/healthcare-ai-multiagent-system
   ```

3. **Run the server:**
   ```bash
   python3 intelligent_orchestrator.py
   ```

4. **Open your web browser and go to:**
   - Main Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Patient View: http://localhost:8000/patient_view.html

### Option 2: Using the Startup Scripts

We've created several helper scripts:

1. **System Check (run this first):**
   ```bash
   python3 check_system.py
   ```

2. **Start Server (with dependency checking):**
   ```bash
   python3 start_server.py
   ```

3. **Quick Run (bash script):**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

## 🔧 If You Get Errors

### Missing Dependencies Error:
```bash
pip3 install fastapi uvicorn[standard] python-multipart pillow numpy aiofiles python-dotenv
```

### Port Already in Use:
Kill the process using port 8000:
```bash
lsof -ti:8000 | xargs kill -9
```

### Permission Denied:
```bash
chmod +x intelligent_orchestrator.py
```

## 📱 Using the Web Interface

Once the server is running:

1. **Upload Patient Data:**
   - Demographics JSON file
   - Lab report image (PNG/JPG)
   - Chest X-ray image (PNG/JPG)

2. **Watch the Agents Communicate:**
   - See real-time messages between agents
   - Observe how they debate and reach consensus
   - View the final diagnosis and treatment plan

3. **Patient View:**
   - Go to http://localhost:8000/patient_view.html
   - Get emergency alerts
   - See cost estimates
   - Understand admission necessity

## 🛑 To Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

## 💡 Tips

- The system works with mock data if AI models aren't installed
- Agent communication is shown in real-time
- The blackboard system tracks all agent conversations
- Check the terminal for detailed logs

## 🔍 Monitoring in VS Code

Since you mentioned monitoring through VS Code:

1. Open the integrated terminal in VS Code: `View > Terminal`
2. Run the server from within VS Code
3. You'll see all logs and agent communications in the terminal
4. Files will auto-reload when you make changes (if using start_server.py)
