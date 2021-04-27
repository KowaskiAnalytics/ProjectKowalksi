from waitress import serve
import app
serve(app.app, host='192.168.0.195', port=8081)