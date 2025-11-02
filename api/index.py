"""
NOTLIFY API - Simple Notification Service
Lightweight version without pydantic dependencies
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import logging
import asyncio
from datetime import datetime
import json
import re

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NOTLIFY API",
    description="Simple Notification Service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
notifications_db = []

def validate_email(email):
    """Простая валидация email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

async def send_email_notification(email, subject, message):
    """Асинхронная отправка email уведомления"""
    try:
        logger.info(f"Sending notification to {email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Message: {message}")
        
        # Имитация отправки
        await asyncio.sleep(0.5)
        
        logger.info(f"Notification sent successfully to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        return False

@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NOTLIFY - Notification Service</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #0f0f23; color: white; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 40px; }
            .logo { font-size: 3em; color: #4d96ff; margin-bottom: 10px; }
            .endpoint { background: rgba(255,255,255,0.1); padding: 20px; margin: 10px 0; border-radius: 8px; }
            code { background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">NOTLIFY</div>
                <p>Simple Notification Service API</p>
            </div>
            
            <div class="endpoint">
                <h3>Health Check</h3>
                <p><code>GET /api/health</code></p>
                <p>Check API status</p>
            </div>
            
            <div class="endpoint">
                <h3>Send Notification</h3>
                <p><code>POST /api/notify</code></p>
                <p>Send a notification</p>
                <p><strong>Body:</strong> {"email": "user@example.com", "message": "Hello!"}</p>
            </div>
            
            <div class="endpoint">
                <h3>Get Notifications</h3>
                <p><code>GET /api/notifications</code></p>
                <p>Get notification history</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/notify")
async def send_notification(
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    message: str = Form(...),
    subject: str = Form("Notification from NOTLIFY")
):
    """Отправка уведомления"""
    try:
        # Валидация email
        if not validate_email(email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        if not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Создаем ID уведомления
        notification_id = f"notify_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Сохраняем уведомление
        notification_data = {
            "id": notification_id,
            "email": email,
            "message": message,
            "subject": subject,
            "status": "pending",
            "timestamp": datetime.now().isoformat()
        }
        notifications_db.append(notification_data)
        
        # Отправляем в фоне
        background_tasks.add_task(send_email_notification, email, subject, message)
        
        # Обновляем статус
        notification_data["status"] = "sent"
        
        return {
            "id": notification_id,
            "status": "sent",
            "message": "Notification queued successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Notification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")

@app.get("/api/notifications")
async def get_notifications(limit: int = 10, offset: int = 0):
    """Получение истории уведомлений"""
    try:
        notifications = notifications_db[::-1]  # Последние сначала
        paginated_notifications = notifications[offset:offset + limit]
        
        return {
            "notifications": paginated_notifications,
            "total": len(notifications_db),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve notifications: {str(e)}")

@app.get("/api/notifications/{notification_id}")
async def get_notification(notification_id: str):
    """Получение конкретного уведомления по ID"""
    for notification in notifications_db:
        if notification["id"] == notification_id:
            return notification
    
    raise HTTPException(status_code=404, detail="Notification not found")

# Инициализация
logger.info("NOTLIFY API started successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
