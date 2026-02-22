"""HTTPS web server for wake timer configuration"""

import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from ssl import SSLContext, PROTOCOL_TLS_SERVER
from urllib.parse import parse_qs
from config import WEB_SERVER_PORT, CERT_FILE, KEY_FILE


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for web server"""
    
    # Reference to wake timer (set by WebServer)
    wake_timer = None
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path != "/":
            self.send_response(404)
            self.end_headers()
            return
        
        page = self._generate_html()
        page_bytes = page.encode()
        
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(page_bytes)))
        self.end_headers()
        self.wfile.write(page_bytes)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path != "/set":
            self.send_response(404)
            self.end_headers()
            return
        
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode()
            data = parse_qs(body)
            
            if "time" in data:
                time_value = data["time"][0]
                if self.wake_timer:
                    self.wake_timer.save(time_value)
                
                self.send_response(302)
                self.send_header("Location", "/")
            else:
                self.send_response(400)
            
            self.end_headers()
        except Exception as e:
            print(f"Error handling POST: {e}")
            self.send_response(500)
            self.end_headers()
    
    def _generate_html(self):
        """Generate HTML page"""
        wake_time = self.wake_timer.get_wake_time_str() if self.wake_timer else ""
        
        return f"""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>System Control Panel</title>
<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}}

.container {{
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    padding: 40px;
    max-width: 400px;
    width: 100%;
}}

h1 {{
    color: #333;
    margin-bottom: 30px;
    text-align: center;
    font-size: 28px;
}}

.section {{
    margin-bottom: 30px;
}}

.section h2 {{
    color: #667eea;
    font-size: 16px;
    margin-bottom: 15px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.form-group {{
    margin-bottom: 15px;
}}

label {{
    display: block;
    color: #555;
    font-size: 14px;
    margin-bottom: 8px;
    font-weight: 500;
}}

input[type="time"] {{
    width: 100%;
    padding: 12px;
    border: 2px solid #e0e0e0;
    border-radius: 6px;
    font-size: 16px;
    transition: border-color 0.3s;
}}

input[type="time"]:focus {{
    outline: none;
    border-color: #667eea;
}}

button {{
    width: 100%;
    padding: 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}}

button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}}

button:active {{
    transform: translateY(0);
}}

.info {{
    background: #f5f5f5;
    border-left: 4px solid #667eea;
    padding: 12px;
    border-radius: 4px;
    margin-top: 15px;
    font-size: 14px;
    color: #666;
}}
</style>
</head>
<body>
<div class="container">
    <h1>⏰ System Control</h1>
    
    <div class="section">
        <h2>Wake Up Timer</h2>
        <form method="POST" action="/set">
            <div class="form-group">
                <label for="time">Set wake-up time:</label>
                <input type="time" id="time" name="time" value="{wake_time}" required>
            </div>
            <button type="submit">Save Time</button>
            <div class="info">
                The device will trigger an alarm at the selected time.
            </div>
        </form>
    </div>
</div>
</body>
</html>
"""
    
    def log_message(self, format, *args):
        """Suppress logging"""
        pass


class WebServer:
    """HTTPS web server"""
    
    def __init__(self, wake_timer):
        self.wake_timer = wake_timer
        self.server = None
        self.thread = None
    
    def start(self):
        """Start the web server"""
        RequestHandler.wake_timer = self.wake_timer
        
        self.server = HTTPServer(("0.0.0.0", WEB_SERVER_PORT), RequestHandler)
        
        try:
            ctx = SSLContext(PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(CERT_FILE, KEY_FILE)
            self.server.socket = ctx.wrap_socket(self.server.socket, server_side=True)
        except Exception as e:
            print(f"Warning: SSL not configured - {e}")
        
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()
        print(f"Web server started on port {WEB_SERVER_PORT}")
    
    def _serve(self):
        """Serve requests"""
        try:
            self.server.serve_forever()
        except Exception as e:
            print(f"Web server error: {e}")
    
    def stop(self):
        """Stop the web server"""
        if self.server:
            self.server.shutdown()
