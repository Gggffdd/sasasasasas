import json
from datetime import datetime

def handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({
            'status': 'healthy',
            'service': 'NOTLIFY',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    }
