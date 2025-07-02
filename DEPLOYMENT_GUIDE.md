# 🚀 BiztelAI Deployment Guide

## Step 1: Install Docker

### Windows:
1. Download Docker Desktop from: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
2. Run the installer and follow the setup wizard
3. Restart your computer when prompted
4. Start Docker Desktop from the Start menu

### macOS:
1. Download Docker Desktop from: https://desktop.docker.com/mac/main/amd64/Docker.dmg
2. Drag Docker to Applications folder
3. Launch Docker from Applications

### Linux:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

## Step 2: Verify Docker Installation

Open a new terminal/command prompt and run:
```bash
docker --version
docker compose version
```

You should see version information for both commands.

## Step 3: Deploy BiztelAI

### Option A: Quick Deployment (Recommended)
```bash
cd conversa-ai-main
python deploy.py
```

### Option B: Manual Deployment

1. **Local deployment only:**
   ```bash
   docker compose up --build -d
   ```

2. **With public sharing via ngrok:**
   
   First, get your ngrok auth token:
   - Go to https://dashboard.ngrok.com/get-started/your-authtoken
   - Copy your auth token
   - Edit `ngrok.yml` and replace `YOUR_NGROK_AUTH_TOKEN_HERE` with your actual token
   
   Then deploy:
   ```bash
   docker compose --profile sharing up --build -d
   ```

## Step 4: Access Your Application

### Local Access:
- **Dashboard:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Public Access (if ngrok enabled):
- Check the deployment output for your public HTTPS URL
- Or visit http://localhost:4040 to see the ngrok dashboard

### Demo Credentials:
- Username: `demo` | Password: `demo123`
- Username: `admin` | Password: `admin123`

## Step 5: Test the Application

1. **Login** with demo credentials
2. **Upload or paste** a transcript JSON in this format:
   ```json
   {
     "transcript_1": {
       "article_url": "https://example.com/article",
       "content": [
         {
           "message": "Hello, how are you?",
           "agent": "agent_1",
           "sentiment": "Positive"
         },
         {
           "message": "I'm doing well, thanks!",
           "agent": "agent_2", 
           "sentiment": "Positive"
         }
       ]
     }
   }
   ```
3. **Click "Analyze Transcript"**
4. **View the results** - you'll see:
   - Real-time sentiment analysis
   - AI-generated transcript summary
   - Agent statistics
   - Sentiment distribution

## 🔧 Management Commands

```bash
# View logs
docker compose logs -f

# Stop the application
docker compose down

# Restart services
docker compose restart

# Update and redeploy
docker compose down
docker compose up --build -d
```

## 🌐 Sharing Your Deployment

Once deployed with ngrok, you can share the public HTTPS URL with anyone. They'll be able to:
- Access the full dashboard
- Upload and analyze their own transcripts
- See real-time AI analysis results

## 🛠️ Troubleshooting

### Docker Issues:
- Make sure Docker Desktop is running
- Try restarting Docker Desktop
- Check Docker has enough memory allocated (4GB+ recommended)

### Ngrok Issues:
- Verify your auth token is correct in `ngrok.yml`
- Check ngrok dashboard at http://localhost:4040
- Free ngrok accounts have session limits

### Application Issues:
- Check logs: `docker compose logs -f web`
- Verify the data file exists: `data/BiztelAI_DS_Dataset_V1.json`
- Try restarting: `docker compose restart`

## 📊 What's New in This Version

✅ **Real Sentiment Analysis** - No more fake numbers  
✅ **Dynamic Summaries** - Generated from your actual transcripts  
✅ **Public Sharing** - Easy ngrok integration  
✅ **Better UI/UX** - Improved file upload and error handling  
✅ **One-Click Deployment** - Automated Docker setup  

Your transcript analysis tool is now ready to share with the world! 🎉
