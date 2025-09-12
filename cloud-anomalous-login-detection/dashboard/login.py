import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Login (Sim)", page_icon="🔐", layout="centered")
st.title("🔐 Login (Email + Password only)")

# The HTML/JS below will run in the user's browser.
# It collects navigator info, public IP (via api.ipify.org),
# optionally geolocation (if user allows), and posts to /ingest.

API_URL = "http://localhost:8000/ingest"  # change if needed

html = f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial; padding: 8px; }}
      .wrapper {{ max-width:600px; margin: 0 auto; }}
      input[type="text"], input[type="password"] {{ width:100%; padding:8px; margin:6px 0; box-sizing:border-box; }}
      button {{ padding:8px 12px; margin-top:8px; }}
      .status {{ margin-top:12px; white-space:pre-wrap; font-size:13px; }}
    </style>
  </head>
  <body>
    <div class="wrapper">
      <label>Email</label>
      <input id="email" type="text" placeholder="you@example.com" />
      <label>Password</label>
      <input id="password" type="password" placeholder="password" />
      <div>
        <button id="loginBtn">Login</button>
      </div>
      <div class="status" id="status"></div>
    </div>

    <script>
      async function fetchClientIP() {{
        try {{
          const r = await fetch('https://api.ipify.org?format=json');
          const j = await r.json();
          return j.ip;
        }} catch (e) {{
          return null;
        }}
      }}

      // OPTIONAL: example of loading an external fingerprint library (if hosted)
      // function runFingerprintLib() {{
      //   return new Promise((resolve) => {{
      //     // Example: load fingerprint.js and compute fingerprint
      //     // Replace with your real fingerprint library URL and usage
      //     resolve(null);
      //   }});
      // }}

      document.getElementById('loginBtn').addEventListener('click', async () => {{
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const statusEl = document.getElementById('status');

        if (!email || !password) {{
          statusEl.textContent = 'Please enter email and password.';
          return;
        }}

        statusEl.textContent = 'Collecting device info…';

        const ip = await fetchClientIP();  // client public IP
        const ua = navigator.userAgent || null;
        const platform = navigator.platform || null;
        const language = navigator.language || null;
        const now = new Date().toISOString();

        // Try to get geolocation (user will be prompted; optional)
        let geo = null;
        try {{
          geo = await new Promise((resolve) => {{
            if (!navigator.geolocation) return resolve(null);
            let handled = false;
            navigator.geolocation.getCurrentPosition(pos => {{
              if (handled) return;
              handled = true;
              resolve({{ latitude: pos.coords.latitude, longitude: pos.coords.longitude, accuracy: pos.coords.accuracy }});
            }}, err => {{
              // permission denied or other error
              if (handled) return;
              handled = true;
              resolve(null);
            }}, {{ timeout: 5000 }});
            // fallback after 5s
            setTimeout(() => {{ if (!handled) {{ handled = true; resolve(null); }} }}, 5000);
          }});
        }} catch(e) {{
          geo = null;
        }}

        // Optional fingerprint step: uncomment & adapt if you host fingerprint.js
        // const fingerprint = await runFingerprintLib();

        const payload = {{
          user_id: email,                 // use email as user_id (or map as needed)
          timestamp: now,
          ip: ip,
          device_id: platform || 'unknown',  // best-effort
          browser: ua || 'unknown',
          language: language,
          geo: geo,
          // fingerprint: fingerprint
          // NOTE: we include password below; if you don't want to send password to ingest,
          // remove it and instead send an auth-only endpoint. For simulation it's included.
          password: password
        }};

        statusEl.textContent = 'Sending login event to server…';

        try {{
          const resp = await fetch("{API_URL}", {{
            method: 'POST',
            headers: {{
              'Content-Type': 'application/json'
            }},
            body: JSON.stringify(payload)
          }});
          const text = await resp.text();
          statusEl.textContent = 'Server response (' + resp.status + '):\\n' + text;
        }} catch (err) {{
          statusEl.textContent = 'Failed to send to backend: ' + err;
        }}
      }});
    </script>
  </body>
</html>
"""

# Render the HTML component inside Streamlit. It runs in the browser,
# collects metadata and posts directly to your FastAPI /ingest endpoint.
components.html(html, height=400)
