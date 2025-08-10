#!/usr/bin/env python3
# VNC Command Executor API
# Simple HTTP server to execute commands in VNC container

import http.server
import socketserver
import subprocess
import json
import urllib.parse
import base64
import os
from pathlib import Path

PORT = 8090

class VNCCommandHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Override to add more logging
        print(f"[{self.client_address[0]}] {format % args}")
        
    def do_POST(self):
        if self.path == '/execute':
            self.handle_execute()
        elif self.path == '/screenshot':
            self.handle_screenshot()
        else:
            self.send_error(404)
    
    def handle_execute(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Debug: print received data
            print(f"Received raw data: {post_data}")
            
            data = json.loads(post_data.decode('utf-8'))
            
            command = data.get('command', '')
            if not command:
                self.send_json_response({'error': 'No command provided'}, 400)
                return
            
            print(f"Executing command: {command}")
            
            # Set environment variables for X11
            env = os.environ.copy()
            env['DISPLAY'] = ':1'
            
            # Execute command
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                env=env,
                timeout=30
            )
            
            response = {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0
            }
            
            print(f"Command result: {response}")
            self.send_json_response(response)
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            self.send_json_response({'error': f'Invalid JSON: {str(e)}'}, 400)
        except Exception as e:
            print(f"General error: {e}")
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_screenshot(self):
        try:
            # Take screenshot using xwd and convert to PNG
            cmd = "DISPLAY=:1 xwd -root | convert xwd:- png:- | base64 -w 0"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                response = {
                    'success': True,
                    'image': result.stdout.strip()
                }
            else:
                response = {
                    'success': False,
                    'error': result.stderr
                }
            
            self.send_json_response(response)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    try:
        with socketserver.TCPServer(("", PORT), VNCCommandHandler) as httpd:
            print(f"VNC Command API serving at port {PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
