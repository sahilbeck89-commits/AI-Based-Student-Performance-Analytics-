import requests, os

url = 'http://127.0.0.1:5000/api/upload-csv'
csv_path = os.path.join(os.path.dirname(__file__), '..', 'students_50.csv')
# Resolve relative path correctly
csv_path = os.path.abspath(csv_path)

with open(csv_path, 'rb') as f:
    files = {'file': (os.path.basename(csv_path), f, 'text/csv')}
    try:
        resp = requests.post(url, files=files)
        print('Status:', resp.status_code)
        try:
            print('JSON response:', resp.json())
        except Exception:
            print('Response text:', resp.text)
    except Exception as e:
        print('Error during request:', e)
