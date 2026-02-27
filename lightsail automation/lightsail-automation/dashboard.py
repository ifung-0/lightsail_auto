#!/usr/bin/env python3
"""
LightSail Automation - Web Dashboard
Real-time web UI for monitoring bot progress
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import websockets
from websockets.server import WebSocketServerProtocol
import http.server
import socketserver
import threading
import webbrowser
from urllib.parse import urlparse, parse_qs

from logger import StatsCollector


class DashboardData:
    """Manages dashboard data and WebSocket connections"""
    
    def __init__(self, stats_collector: StatsCollector):
        self.stats = stats_collector
        self.clients: set = set()
        self.bot_status = {
            'state': 'idle',
            'book': '',
            'pages_read': 0,
            'total_flips': 0,
            'questions_detected': 0,
            'questions_answered': 0,
            'accuracy': 0.0,
            'session_duration': '0m 0s',
            'last_activity': None,
            'errors': []
        }
    
    def update(self, **kwargs):
        """Update bot status"""
        self.bot_status.update(kwargs)
        self.bot_status['last_activity'] = datetime.now().isoformat()
        asyncio.create_task(self.broadcast())
    
    async def broadcast(self):
        """Broadcast status to all connected clients"""
        if not self.clients:
            return
        
        message = json.dumps({
            'type': 'status_update',
            'data': self.bot_status,
            'real_time': self.stats.get_real_time_stats(),
            'timestamp': datetime.now().isoformat()
        })
        
        disconnected = set()
        for client in self.clients:
            try:
                await client.send(message)
            except:
                disconnected.add(client)
        
        self.clients -= disconnected
    
    async def register(self, websocket: WebSocketServerProtocol):
        """Register a WebSocket client"""
        self.clients.add(websocket)
        # Send initial data
        await websocket.send(json.dumps({
            'type': 'initial_data',
            'data': self.bot_status,
            'history': self.stats.get_session_history(10)
        }))
    
    def unregister(self, websocket: WebSocketServerProtocol):
        """Unregister a WebSocket client"""
        self.clients.discard(websocket)


# HTML Dashboard Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LightSail Bot Dashboard</title>
    <style>
        :root {
            --primary: #4f46e5;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text: #f1f5f9;
            --text-muted: #94a3b8;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--card-bg);
        }
        
        h1 {
            font-size: 24px;
            font-weight: 600;
        }
        
        .status-badge {
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
        }
        
        .status-running { background: var(--success); }
        .status-stopped { background: var(--text-muted); }
        .status-error { background: var(--danger); }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .card-title {
            font-size: 14px;
            color: var(--text-muted);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .card-value {
            font-size: 32px;
            font-weight: 700;
            color: var(--primary);
        }
        
        .card-value.success { color: var(--success); }
        .card-value.warning { color: var(--warning); }
        
        .book-info {
            font-size: 18px;
            margin-top: 8px;
        }
        
        .progress-section {
            margin-bottom: 30px;
        }
        
        .progress-bar {
            height: 8px;
            background: var(--card-bg);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 12px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), #818cf8);
            transition: width 0.3s ease;
            width: 0%;
        }
        
        .history-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .history-table th,
        .history-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--card-bg);
        }
        
        .history-table th {
            color: var(--text-muted);
            font-weight: 500;
            font-size: 13px;
            text-transform: uppercase;
        }
        
        .log-container {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Consolas', monospace;
            font-size: 13px;
        }
        
        .log-entry {
            padding: 4px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .log-time { color: var(--text-muted); }
        .log-info { color: var(--success); }
        .log-warning { color: var(--warning); }
        .log-error { color: var(--danger); }
        
        .activity-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--success);
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--card-bg);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 LightSail Bot Dashboard</h1>
            <div>
                <span class="status-badge status-stopped" id="statusBadge">Stopped</span>
                <span style="margin-left: 12px; color: var(--text-muted);" id="connectionStatus">Connecting...</span>
            </div>
        </header>
        
        <div class="grid">
            <div class="card">
                <div class="card-title">Current Book</div>
                <div class="book-info" id="bookTitle">-</div>
            </div>
            
            <div class="card">
                <div class="card-title">Pages Read</div>
                <div class="card-value" id="pagesRead">0</div>
            </div>
            
            <div class="card">
                <div class="card-title">Total Flips</div>
                <div class="card-value" id="totalFlips">0</div>
            </div>
            
            <div class="card">
                <div class="card-title">Questions Answered</div>
                <div class="card-value" id="questionsAnswered">0</div>
            </div>
            
            <div class="card">
                <div class="card-title">Accuracy Rate</div>
                <div class="card-value success" id="accuracy">0%</div>
            </div>
            
            <div class="card">
                <div class="card-title">Session Duration</div>
                <div class="card-value" id="sessionDuration">0m 0s</div>
            </div>
        </div>
        
        <div class="progress-section">
            <div class="section-title">
                <span class="activity-indicator"></span>
                Real-time Activity
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="activityProgress"></div>
            </div>
            <div style="margin-top: 8px; color: var(--text-muted); font-size: 13px;">
                Last activity: <span id="lastActivity">-</span>
            </div>
        </div>
        
        <div class="grid" style="grid-template-columns: 1fr 1fr;">
            <div class="card">
                <div class="section-title">Session History</div>
                <table class="history-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Book</th>
                            <th>Pages</th>
                            <th>Questions</th>
                            <th>Accuracy</th>
                        </tr>
                    </thead>
                    <tbody id="historyTable">
                        <tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No sessions yet</td></tr>
                    </tbody>
                </table>
            </div>
            
            <div class="card">
                <div class="section-title">Activity Log</div>
                <div class="log-container" id="logContainer">
                    <div class="log-entry">
                        <span class="log-time">[--:--:--]</span>
                        <span class="log-info">Dashboard connected</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let ws;
        
        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = () => {
                document.getElementById('connectionStatus').textContent = 'Connected';
                addLog('Connected to bot', 'info');
            };
            
            ws.onclose = () => {
                document.getElementById('connectionStatus').textContent = 'Disconnected';
                addLog('Disconnected from bot', 'warning');
                setTimeout(connect, 3000);
            };
            
            ws.onerror = (error) => {
                addLog('WebSocket error', 'error');
            };
            
            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                if (message.type === 'status_update' || message.type === 'initial_data') {
                    updateDashboard(message.data, message.real_time);
                    if (message.history) {
                        updateHistory(message.history);
                    }
                }
            };
        }
        
        function updateDashboard(data, realTime) {
            // Update status badge
            const badge = document.getElementById('statusBadge');
            badge.className = 'status-badge status-' + (data.state || 'stopped');
            badge.textContent = (data.state || 'stopped').charAt(0).toUpperCase() + (data.state || 'stopped').slice(1);
            
            // Update values
            document.getElementById('bookTitle').textContent = data.book || '-';
            document.getElementById('pagesRead').textContent = data.pages_read || 0;
            document.getElementById('totalFlips').textContent = data.total_flips || 0;
            document.getElementById('questionsAnswered').textContent = data.questions_answered || 0;
            document.getElementById('accuracy').textContent = (realTime?.accuracy || 0).toFixed(1) + '%';
            document.getElementById('sessionDuration').textContent = realTime?.session_duration || '0m 0s';
            
            // Update activity
            if (data.last_activity) {
                const time = new Date(data.last_activity).toLocaleTimeString();
                document.getElementById('lastActivity').textContent = time;
            }
            
            // Update progress bar animation
            const progress = document.getElementById('activityProgress');
            progress.style.width = '100%';
            setTimeout(() => { progress.style.width = '0%'; }, 500);
        }
        
        function updateHistory(history) {
            const tbody = document.getElementById('historyTable');
            if (!history || history.length === 0) return;
            
            tbody.innerHTML = history.map(session => {
                const date = new Date(session.start_time).toLocaleDateString();
                const accuracy = (session.accuracy_rate || 0).toFixed(0);
                return `
                    <tr>
                        <td>${date}</td>
                        <td>${session.book_title || '-'}</td>
                        <td>${session.pages_read}</td>
                        <td>${session.questions_answered}</td>
                        <td>${accuracy}%</td>
                    </tr>
                `;
            }).join('');
        }
        
        function addLog(message, type = 'info') {
            const container = document.getElementById('logContainer');
            const time = new Date().toLocaleTimeString();
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.innerHTML = `
                <span class="log-time">[${time}]</span>
                <span class="log-${type}">${message}</span>
            `;
            container.insertBefore(entry, container.firstChild);
            
            // Keep only last 100 entries
            while (container.children.length > 100) {
                container.removeChild(container.lastChild);
            }
        }
        
        // Connect on load
        connect();
    </script>
</body>
</html>
"""


class DashboardServer:
    """WebSocket and HTTP server for dashboard"""
    
    def __init__(self, stats_collector: StatsCollector, host: str = "127.0.0.1", port: int = 8765):
        self.stats = stats_collector
        self.host = host
        self.port = port
        self.dashboard_data = DashboardData(stats_collector)
        self.server = None
        self.ws_server = None
    
    async def websocket_handler(self, websocket: WebSocketServerProtocol, path: str):
        """Handle WebSocket connections"""
        await self.dashboard_data.register(websocket)
        try:
            async for message in websocket:
                pass  # We only send, don't receive
        finally:
            self.dashboard_data.unregister(websocket)
    
    async def start_websocket_server(self):
        """Start WebSocket server"""
        self.ws_server = await websockets.serve(
            self.websocket_handler,
            self.host,
            self.port + 1  # Use next port for WebSocket
        )
    
    def start_http_server(self):
        """Start HTTP server for dashboard HTML"""
        dashboard_html = DASHBOARD_HTML
        
        class DashboardHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                if self.path == '/' or self.path == '/dashboard':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(dashboard_html.encode())
                elif self.path == '/api/stats':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    stats = self.server.stats_collector.get_real_time_stats()
                    self.wfile.write(json.dumps(stats).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass  # Suppress HTTP logs
        
        with socketserver.TCPServer((self.host, self.port), DashboardHandler) as httpd:
            httpd.stats_collector = self.stats
            self.server = httpd
            httpd.serve_forever()
    
    def start(self, auto_open: bool = True):
        """Start the dashboard"""
        # Start HTTP server in thread
        http_thread = threading.Thread(target=self.start_http_server, daemon=True)
        http_thread.start()
        
        # Start WebSocket server
        asyncio.create_task(self.start_websocket_server())
        
        # Auto-open browser
        if auto_open:
            url = f"http://{self.host}:{self.port}"
            webbrowser.open(url)
        
        print(f"Dashboard available at: http://{self.host}:{self.port}")
    
    def update(self, **kwargs):
        """Update dashboard data"""
        self.dashboard_data.update(**kwargs)
    
    async def stop(self):
        """Stop the dashboard servers"""
        if self.ws_server:
            self.ws_server.close()
            await self.ws_server.wait_closed()
        if self.server:
            self.server.shutdown()


if __name__ == "__main__":
    # Test dashboard
    stats = StatsCollector()
    dashboard = DashboardServer(stats, port=8765)
    dashboard.start(auto_open=True)
    
    # Simulate updates
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        asyncio.run(dashboard.stop())
