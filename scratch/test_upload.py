import os
import sys
import json
from connecting.app_factory import create_app

# Initialize Flask app
app = create_app()
client = app.test_client()

# Path to CSV file (existing in repo)
csv_path = os.path.join(os.path.dirname(__file__), '..', 'students_50.csv')
# Ensure absolute path
csv_path = os.path.abspath(csv_path)

with open(csv_path, 'rb') as f:
    data = {
        'file': (f, os.path.basename(csv_path))
    }
    # Flask test client expects data as dict with file tuple
    response = client.post('/api/upload-csv', content_type='multipart/form-data', data=data)
    print('Status code:', response.status_code)
    try:
        print('JSON response:', response.get_json())
    except Exception as e:
        print('Error parsing JSON:', e)
        print('Raw data:', response.data)
