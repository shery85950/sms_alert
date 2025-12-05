from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Get environment variables from Vercel
        supabase_url = os.environ.get('SUPABASE_URL', '')
        supabase_anon_key = os.environ.get('SUPABASE_ANON_KEY', '')
        
        # Prepare response
        config = {
            'SUPABASE_URL': supabase_url,
            'SUPABASE_ANON_KEY': supabase_anon_key
        }
        
        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(config).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()
