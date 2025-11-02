"""
NOTLIFY API - Digital Notification Service
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
import asyncio
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NOTLIFY API",
    description="Digital Notification Service",
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

# Модели данных
class NotificationRequest(BaseModel):
    email: EmailStr
    message: str
    subject: str = "Notification from NOTLIFY"
    priority: str = "normal"

class NotificationResponse(BaseModel):
    id: str
    status: str
    message: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

# In-memory storage (в продакшене заменить на базу данных)
notifications_db = []

# Конфигурация
SMTP_CONFIG = {
    "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
    "port": int(os.getenv("SMTP_PORT", 587)),
    "username": os.getenv("SMTP_USERNAME", ""),
    "password": os.getenv("SMTP_PASSWORD", "")
}

async def send_email_notification(notification: NotificationRequest):
    """Асинхронная отправка email уведомления"""
    try:
        # Имитация отправки email (в реальном приложении используйте реальный SMTP)
        logger.info(f"Sending notification to {notification.email}")
        logger.info(f"Subject: {notification.subject}")
        logger.info(f"Message: {notification.message}")
        
        # Здесь будет реальная логика отправки email
        # msg = MIMEMultipart()
        # msg['From'] = SMTP_CONFIG['username']
        # msg['To'] = notification.email
        # msg['Subject'] = notification.subject
        # msg.attach(MIMEText(notification.message, 'plain'))
        
        # with smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port']) as server:
        #     server.starttls()
        #     server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
        #     server.send_message(msg)
        
        await asyncio.sleep(1)  # Имитация задержки сети
        
        logger.info(f"Notification sent successfully to {notification.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        return False

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Welcome to NOTLIFY API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "send_notification": "/api/notify",
            "get_notifications": "/api/notifications"
        }
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/notify", response_model=NotificationResponse)
async def send_notification(
    request: NotificationRequest, 
    background_tasks: BackgroundTasks
):
    """Отправка уведомления"""
    try:
        notification_id = f"notify_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Сохраняем в "базу данных"
        notification_data = {
            "id": notification_id,
            "email": request.email,
            "message": request.message,
            "subject": request.subject,
            "priority": request.priority,
            "status": "pending",
            "timestamp": datetime.now().isoformat()
        }
        notifications_db.append(notification_data)
        
        # Отправляем уведомление в фоновом режиме
        background_tasks.add_task(send_email_notification, request)
        
        # Обновляем статус
        notification_data["status"] = "sent"
        
        return NotificationResponse(
            id=notification_id,
            status="sent",
            message="Notification queued successfully",
            timestamp=datetime.now().isoformat()
        )
        
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
import random
logger.info("NOTLIFY API started successfully")

# Для Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
