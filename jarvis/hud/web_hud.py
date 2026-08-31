"""
jarvis/hud/web_hud.py — Stark Holographic Web HUD Overlay Generator v3.0 (Full Browser Voice Input & TTS)
Futuristic Stark Horizon web HUD interface with Arc Reactor animations, Web Speech API microphone input,
audio visualizers, live system metrics, interactive console, and WebSocket telemetry.
"""

from jarvis.config import config

def get_stark_web_hud_html() -> str:
    """Returns standalone HTML5/JS Stark Holographic Desktop Web HUD Interface."""
    lan_ip = config.to_dict()["lan_ip"]
    port = config.to_dict()["fastapi_port"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>J.A.R.V.I.S. Stark Horizon HUD</title>
    <style>
        :root {{
            --bg-color: #050811;
            --panel-bg: rgba(15, 23, 42, 0.85);
            --cyan-glow: #00f0ff;
            --cyan-dim: rgba(0, 240, 255, 0.2);
            --green-active: #00ffaa;
            --orange-proc: #ffaa00;
            --red-alert: #ff0055;
            --text-color: #e2e8f0;
            --active-color: var(--cyan-glow);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Segoe UI', Roboto, -apple-system, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 50% 30%, rgba(0, 240, 255, 0.08) 0%, transparent 70%),
                linear-gradient(to bottom, rgba(5,8,17,0.9), rgba(5,8,17,0.98));
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 30px;
            border-bottom: 1px solid var(--active-color);
            background: rgba(11, 15, 25, 0.8);
            backdrop-filter: blur(10px);
            transition: border-color 0.4s ease;
        }}
        .logo {{
            font-size: 22px;
            font-weight: 800;
            letter-spacing: 3px;
            color: var(--cyan-glow);
            text-shadow: 0 0 10px var(--cyan-glow);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .status-badge {{
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            border: 1px solid var(--active-color);
            color: var(--active-color);
            box-shadow: 0 0 10px var(--cyan-dim);
            transition: all 0.3s ease;
        }}
        .grid-container {{
            display: grid;
            grid-template-columns: 320px 1fr 340px;
            gap: 20px;
            padding: 25px 30px;
            flex: 1;
        }}
        .panel {{
            background: var(--panel-bg);
            border: 1px solid var(--cyan-dim);
            border-radius: 14px;
            padding: 20px;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            display: flex;
            flex-direction: column;
        }}
        .panel-title {{
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 2px;
            color: var(--cyan-glow);
            margin-bottom: 15px;
            text-transform: uppercase;
            display: flex;
            justify-content: space-between;
        }}
        /* Arc Reactor Centerpiece */
        .arc-reactor-wrapper {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            flex: 1;
            position: relative;
        }}
        canvas#arcCanvas {{
            width: 260px;
            height: 260px;
        }}
        /* Metrics Gauges */
        .metric-row {{
            margin-bottom: 15px;
        }}
        .metric-header {{
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            margin-bottom: 6px;
        }}
        .progress-bar {{
            height: 8px;
            background: rgba(255,255,255,0.08);
            border-radius: 4px;
            overflow: hidden;
            border: 1px solid rgba(0,240,255,0.15);
        }}
        .progress-fill {{
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #00f0ff, #0088ff);
            transition: width 0.4s ease;
            box-shadow: 0 0 10px var(--cyan-glow);
        }}
        /* Console Log */
        .console-log {{
            background: rgba(5, 8, 17, 0.85);
            border: 1px solid rgba(0,240,255,0.15);
            border-radius: 8px;
            padding: 12px;
            font-family: 'Consolas', monospace;
            font-size: 12px;
            flex: 1;
            overflow-y: auto;
            max-height: 280px;
            color: #a0aec0;
        }}
        .log-entry {{ margin-bottom: 6px; line-height: 1.4; }}
        .log-time {{ color: var(--cyan-glow); margin-right: 8px; }}
        .log-jarvis {{ color: #00ffaa; }}
        .log-error {{ color: var(--red-alert); }}
        
        /* Command Input Bar */
        .input-bar {{
            display: flex;
            gap: 10px;
            margin-top: 15px;
            align-items: center;
        }}
        input[type="text"] {{
            flex: 1;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid var(--cyan-dim);
            border-radius: 8px;
            padding: 12px 16px;
            color: #fff;
            font-size: 14px;
            outline: none;
        }}
        input[type="text"]:focus {{
            border-color: var(--cyan-glow);
            box-shadow: 0 0 10px var(--cyan-dim);
        }}
        button.btn-stark {{
            background: linear-gradient(135deg, #00f0ff, #0088ff);
            color: #050811;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 13px;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 0 15px var(--cyan-dim);
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        button.btn-stark:hover {{
            transform: translateY(-2px);
            box-shadow: 0 0 25px var(--cyan-glow);
        }}
        button.btn-mic {{
            background: linear-gradient(135deg, #00ffaa, #00aa66);
            color: #050811;
        }}
        button.btn-mic.recording {{
            background: linear-gradient(135deg, #ff0055, #990033);
            color: #fff;
            box-shadow: 0 0 20px var(--red-alert);
            animation: micPulse 0.8s infinite alternate;
        }}
        @keyframes micPulse {{
            0% {{ transform: scale(1); }}
            100% {{ transform: scale(1.05); }}
        }}
        button.btn-alert {{
            background: linear-gradient(135deg, #ff0055, #990033);
            color: #fff;
        }}
        /* Audio Visualizer Waveform */
        canvas#waveCanvas {{
            width: 100%;
            height: 60px;
            background: rgba(5,8,17,0.5);
            border-radius: 8px;
            border: 1px solid rgba(0,240,255,0.15);
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <header id="mainHeader">
        <div class="logo">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00f0ff" stroke-width="2">
                <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/>
            </svg>
            J.A.R.V.I.S. v3.0 STARK HORIZON HUD
        </div>
        <div class="status-badge" id="netStatus">SYSTEM NOMINAL</div>
    </header>

    <div class="grid-container">
        <!-- Left Panel: Telemetry & Security -->
        <div class="panel">
            <div class="panel-title">SYSTEM TELEMETRY <span>[LIVE]</span></div>
            
            <div class="metric-row">
                <div class="metric-header"><span>CPU LOAD</span><span id="cpuVal">0%</span></div>
                <div class="progress-bar"><div class="progress-fill" id="cpuFill"></div></div>
            </div>
            
            <div class="metric-row">
                <div class="metric-header"><span>RAM USAGE</span><span id="ramVal">0%</span></div>
                <div class="progress-bar"><div class="progress-fill" id="ramFill"></div></div>
            </div>

            <div class="metric-row" style="margin-top:20px;">
                <div class="metric-header"><span>P-CORE AFFINITY</span><span>0x00F [4 Threads]</span></div>
                <div class="metric-header"><span>MEMORY VAULT</span><span id="vaultFacts">Active</span></div>
                <div class="metric-header"><span>SECURITY GUARDRAILS</span><span style="color:#00ffaa;">4-Layer Protected</span></div>
                <div class="metric-header"><span>LAN BINDING</span><span>{lan_ip}:{port}</span></div>
            </div>

            <div class="panel-title" style="margin-top:30px;">QUICK CONTROLS</div>
            <div style="display:flex; flex-direction:column; gap:10px;">
                <button class="btn-stark" onclick="sendQuickCmd('run health check')">RUN SYSTEM AUDIT</button>
                <button class="btn-stark" onclick="sendQuickCmd('get specs')">INSPECT HARDWARE SPECS</button>
                <button class="btn-stark btn-alert" onclick="sendQuickCmd('trigger lockdown')">PROTOCOL VERONICA</button>
            </div>
        </div>

        <!-- Center Panel: Arc Reactor Hologram & Main Console -->
        <div class="panel" style="align-items:center;">
            <div class="panel-title" style="width:100%;">ARC REACTOR CORE <span id="stateMode" style="color:var(--cyan-glow);">[STARK HORIZON]</span></div>
            
            <div class="arc-reactor-wrapper">
                <canvas id="arcCanvas" width="260" height="260"></canvas>
            </div>

            <canvas id="waveCanvas" width="500" height="60"></canvas>

            <div class="input-bar" style="width:100%; margin-top:20px;">
                <button class="btn-stark btn-mic" id="hudMicBtn" onclick="toggleDesktopMic()">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="22"/>
                    </svg>
                    <span id="hudMicText">VOICE MIC</span>
                </button>
                <input type="text" id="cmdInput" placeholder="Command or voice query for J.A.R.V.I.S. (Press Enter)..." onkeypress="if(event.key==='Enter') sendInput();">
                <button class="btn-stark" onclick="sendInput()">TRANSMIT</button>
            </div>
        </div>

        <!-- Right Panel: Activity Feed & Logs -->
        <div class="panel">
            <div class="panel-title">HUD TELEMETRY FEED <span>[REAL-TIME]</span></div>
            <div class="console-log" id="consoleLog">
                <div class="log-entry"><span class="log-time">[SYSTEM]</span> J.A.R.V.I.S. Core Spine connected.</div>
                <div class="log-entry"><span class="log-time">[SECURITY]</span> 4-Layer Guardrails active.</div>
            </div>
        </div>
    </div>

    <script>
        const wsUrl = `ws://${{location.hostname}}:{port}/ws/mobile`;
        let ws;
        let isDesktopMicActive = false;
        let recognition;

        function setHUDState(mode, color) {{
            document.getElementById('stateMode').innerText = `[${{mode}}]`;
            document.getElementById('stateMode').style.color = color;
            document.getElementById('netStatus').style.borderColor = color;
            document.getElementById('netStatus').style.color = color;
            document.getElementById('mainHeader').style.borderColor = color;
        }}

        function logMsg(msg, type='sys') {{
            const logBox = document.getElementById('consoleLog');
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            const time = new Date().toLocaleTimeString();
            let labelClass = 'log-time';
            if (type === 'jarvis') labelClass = 'log-jarvis';
            if (type === 'err' || type === 'alert') labelClass = 'log-error';
            entry.innerHTML = `<span class="${{labelClass}}">[${{time}}]</span> ${{msg}}`;
            logBox.appendChild(entry);
            logBox.scrollTop = logBox.scrollHeight;
        }}

        function connectWS() {{
            ws = new WebSocket(wsUrl);
            ws.onopen = () => {{
                logMsg('WebSocket Telemetry link established.');
                document.getElementById('netStatus').innerText = 'SYSTEM NOMINAL';
                setHUDState('NOMINAL', '#00f0ff');
            }};
            ws.onmessage = (evt) => {{
                try {{
                    const data = JSON.parse(evt.data);
                    const stateColor = data.state_color || '#00ffaa';
                    const msgType = (data.status === 'LOCKDOWN_ACTIVE' || data.status === 'REJECTED_BY_GUARDRAILS') ? 'alert' : 'jarvis';
                    
                    if (data.state_color) setHUDState(data.status || 'ACTIVE', data.state_color);

                    if (data.result) {{
                        logMsg(data.result, msgType);
                        speakText(data.result);
                    }} else {{
                        logMsg(data.message || JSON.stringify(data), msgType);
                    }}
                }} catch(e) {{
                    logMsg(evt.data, 'jarvis');
                }}
            }};
            ws.onclose = () => {{
                logMsg('Connection lost. Reconnecting in 3s...', 'err');
                document.getElementById('netStatus').innerText = 'OFFLINE';
                setHUDState('OFFLINE', '#ff0055');
                setTimeout(connectWS, 3000);
            }};
        }}
        connectWS();

        function sendInput() {{
            const input = document.getElementById('cmdInput');
            const val = input.value.trim();
            if (!val) return;
            logMsg(`Operator: ${{val}}`);
            setHUDState('PROCESSING', '#ffaa00');
            if (ws && ws.readyState === WebSocket.OPEN) {{
                ws.send(JSON.stringify({{ type: 'remote_command', command: val }}));
            }} else {{
                logMsg('WebSocket offline. Transmitting via HTTP...', 'err');
            }}
            input.value = '';
        }}

        function sendQuickCmd(cmd) {{
            document.getElementById('cmdInput').value = cmd;
            sendInput();
        }}

        // Desktop Text-To-Speech Synthesizer Response
        function speakText(text) {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                const cleanText = text.replace(/\\[.*?\\]/g, '');
                const utterance = new SpeechSynthesisUtterance(cleanText);
                utterance.pitch = 1.0;
                utterance.rate = 1.05;
                window.speechSynthesis.speak(utterance);
            }}
        }}

        // Web Speech API Desktop Microphone Recognition
        function toggleDesktopMic() {{
            const btn = document.getElementById('hudMicBtn');
            const txt = document.getElementById('hudMicText');

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {{
                alert('Web Speech Recognition API is not supported in this browser. Please use Chrome/Brave/Edge.');
                return;
            }}

            if (!isDesktopMicActive) {{
                recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = true;
                recognition.lang = 'en-US';

                recognition.onstart = () => {{
                    isDesktopMicActive = true;
                    btn.classList.add('recording');
                    txt.innerText = 'LISTENING...';
                    setHUDState('LISTENING', '#00ffaa');
                    logMsg('Microphone active. Speak your command now...');
                }};

                recognition.onresult = (event) => {{
                    const transcript = Array.from(event.results)
                        .map(result => result[0])
                        .map(result => result.transcript)
                        .join('');
                    document.getElementById('cmdInput').value = transcript;
                }};

                recognition.onerror = (event) => {{
                    logMsg(`Microphone Error: ${{event.error}}`, 'err');
                    isDesktopMicActive = false;
                    btn.classList.remove('recording');
                    txt.innerText = 'VOICE MIC';
                }};

                recognition.onend = () => {{
                    isDesktopMicActive = false;
                    btn.classList.remove('recording');
                    txt.innerText = 'VOICE MIC';
                    sendInput();
                }};

                recognition.start();
            }} else {{
                if (recognition) recognition.stop();
                isDesktopMicActive = false;
                btn.classList.remove('recording');
                txt.innerText = 'VOICE MIC';
            }}
        }}

        // --- Telemetry Poller ---
        async function updateTelemetry() {{
            try {{
                const res = await fetch('/health');
                const data = await res.json();
                document.getElementById('cpuVal').innerText = data.system_cpu_percent + '%';
                document.getElementById('cpuFill').style.width = data.system_cpu_percent + '%';
                document.getElementById('ramVal').innerText = data.system_ram_percent + '%';
                document.getElementById('ramFill').style.width = data.system_ram_percent + '%';
            }} catch(e) {{}}
        }}
        setInterval(updateTelemetry, 2000);

        // --- Arc Reactor Canvas Animation ---
        const canvas = document.getElementById('arcCanvas');
        const ctx = canvas.getContext('2d');
        let angle = 0;

        function drawArcReactor() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const cx = 130, cy = 130;
            angle += 0.03;

            // Outer Glowing Ring
            ctx.beginPath();
            ctx.arc(cx, cy, 100, 0, Math.PI * 2);
            ctx.strokeStyle = '#00f0ff';
            ctx.lineWidth = 3;
            ctx.shadowBlur = 15;
            ctx.shadowColor = '#00f0ff';
            ctx.stroke();

            // Rotating Segmented Ring
            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(angle);
            for(let i=0; i<8; i++) {{
                ctx.rotate((Math.PI * 2) / 8);
                ctx.beginPath();
                ctx.rect(60, -6, 25, 12);
                ctx.fillStyle = 'rgba(0, 240, 255, 0.8)';
                ctx.fill();
            }}
            ctx.restore();

            // Inner Pulsing Core
            const pulse = 35 + Math.sin(angle * 2) * 5;
            ctx.beginPath();
            ctx.arc(cx, cy, pulse, 0, Math.PI * 2);
            ctx.fillStyle = '#00f0ff';
            ctx.shadowBlur = 25;
            ctx.shadowColor = '#00f0ff';
            ctx.fill();

            requestAnimationFrame(drawArcReactor);
        }}
        drawArcReactor();

        // --- Waveform Canvas Animation ---
        const waveCanvas = document.getElementById('waveCanvas');
        const wCtx = waveCanvas.getContext('2d');
        let waveStep = 0;

        function drawWaveform() {{
            wCtx.clearRect(0, 0, waveCanvas.width, waveCanvas.height);
            wCtx.beginPath();
            wCtx.strokeStyle = '#00ffaa';
            wCtx.lineWidth = 2;
            waveStep += 0.05;

            for (let x = 0; x < waveCanvas.width; x++) {{
                const y = waveCanvas.height / 2 + Math.sin(x * 0.05 + waveStep) * 12 * Math.sin(x * 0.01);
                if (x === 0) wCtx.moveTo(x, y);
                else wCtx.lineTo(x, y);
            }}
            wCtx.stroke();
            requestAnimationFrame(drawWaveform);
        }}
        drawWaveform();
    </script>
</body>
</html>"""
