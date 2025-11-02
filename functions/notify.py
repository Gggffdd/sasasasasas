import json
import os
from datetime import datetime

# In-memory storage (в реальном приложении используйте базу данных)
notifications_db = []

def handler(event, context):
    try:
        # Разбираем HTTP метод и путь
        path = event['path']
        http_method = event['httpMethod']
        
        # Health check
        if path.endswith('/health') and http_method == 'GET':
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'healthy',
                    'version': '1.0.0',
                    'timestamp': datetime.now().isoformat()
                })
            }
        
        # Send notification
        elif path.endswith('/notify') and http_method == 'POST':
            try:
                body = json.loads(event['body'])
                
                # Валидация
                email = body.get('email', '')
                message = body.get('message', '')
                
                if not email or '@' not in email:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'Invalid email'})
                    }
                
                if not message.strip():
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'Message cannot be empty'})
                    }
                
                # Создаем уведомление
                notification_id = f"notify_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                notification = {
                    'id': notification_id,
                    'email': email,
                    'message': message,
                    'subject': body.get('subject', 'Notification from NOTLIFY'),
                    'status': 'sent',
                    'timestamp': datetime.now().isoformat()
                }
                
                notifications_db.append(notification)
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'id': notification_id,
                        'status': 'sent',
                        'message': 'Notification sent successfully',
                        'timestamp': datetime.now().isoformat()
                    })
                }
                
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Invalid JSON'})
                }
        
        # Get notifications
        elif path.endswith('/notifications') and http_method == 'GET':
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'notifications': notifications_db[-10:][::-1],  # Последние 10
                    'total': len(notifications_db)
                })
            }
        
        # Not found
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Endpoint not found'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }
