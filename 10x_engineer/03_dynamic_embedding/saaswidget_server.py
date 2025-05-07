from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware # Import CORSMiddleware
import json # Import json for stringifying data in JS

app = FastAPI()

# Add CORS middleware
# This allows the frontend (HostApp.html on http://localhost:8000)
# to fetch resources (like saaswidget.js) from this backend (http://localhost:8001)
origins = [
    "http://localhost:8000",  # Allow requests from your HostApp origin
    # You would add other allowed origins here in a real application
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # List of allowed origins
    allow_credentials=True, # Allow cookies to be included in requests
    allow_methods=["GET"], # Allow GET requests for our JS file
    allow_headers=["*"], # Allow all headers (can be more restrictive)
)


# HTML template for the SaasWidget page (kept for completeness, not used by script embed POC)
SAAS_WIDGET_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SaasWidget Content - App ID: {{ app_id }}</title>
    <style>
        body { font-family: sans-serif; background-color: #f0f0f0; padding: 20px;}
        button { margin-top: 10px; padding: 8px 15px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc;}
        input[type="text"] { padding: 6px; margin-left: 15px; border-radius: 4px; border: 1px solid #ccc;}
        label { margin-left: 15px; }
         .controls { margin-bottom: 15px; }
    </style>
</head>
<body>

<h2>SaasWidget Content (http://localhost:8001)</h2>
<p>This content is loaded inside an iframe (SaasWidget) for App ID: <strong>{{ app_id }}</strong></p>

<div class="controls">
    <label for="saasWidgetSendSize">Data size to send (KB):</label>
    <input type="text" id="saasWidgetSendSize" value="1" size="5">
    <button id="sendToHostAppBtn">Send Message to HostApp</button>
</div>

<h3>Received Messages from HostApp:</h3>
<ul id="saasWidgetMessages"></ul>


<script>
    // This script is for the iframe version, not the script embed version
    // It's included here just to keep the original HTML template complete.
    // The script embed version will have its own JS below.

    const sendBtn = document.getElementById('sendToHostAppBtn');
    const messageList = document.getElementById('saasWidgetMessages');
    const sendSizeInput = document.getElementById('saasWidgetSendSize');

     // Function to generate a string of a specific size (in KB)
    function generateLargeString(kb) {
        const bytes = kb * 1024;
        let result = '';
        const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        const charactersLength = characters.length;
        for (let i = 0; i < bytes; i++) {
            result += characters.charAt(Math.floor(Math.random() * charactersLength));
        }
        return result;
    }

    // --- SaasWidget sending message to HostApp ---
    sendBtn.addEventListener('click', () => {
      const sizeKB = parseInt(sendSizeInput.value, 10) || 0; // Get size from input, default to 0 if invalid
      const largeData = generateLargeString(sizeKB);

      const messageData = {
        status: 'SaasWidget is alive!',
        random: Math.random(),
        dataSizeKB: sizeKB,
        payload: largeData, // Include the generated large string
        sendTimestamp: performance.now() // Add a high-resolution timestamp
      };

      const hostAppWindow = window.parent;

      // Use postMessage to send data to the HostApp
      // IMPORTANT: Replace 'http://localhost:8000' with the actual,
      // expected origin of the HostApp page for security!
      hostAppWindow.postMessage(messageData, 'http://localhost:8000');
      console.log(`SaasWidget: Sent message (${sizeKB} KB) to HostApp`, messageData);
    });


    // --- SaasWidget receiving message from HostApp ---
    window.addEventListener('message', (event) => {
      console.log('SaasWidget: Received message event', event);

      // !!! IMPORTANT SECURITY CHECK !!!
      const expectedOrigin = 'http://localhost:8000';
      if (event.origin !== expectedOrigin) {
        console.warn('SaasWidget: Received message from unexpected origin:', event.origin);
        return;
      }

      const receivedData = event.data;
      const dataSize = receivedData.payload ? (receivedData.payload.length / 1024).toFixed(2) : 'N/A';

      // Calculate the time taken if a sendTimestamp exists
      let timeTaken = 'N/A';
      if (receivedData.sendTimestamp) {
          const receiveTimestamp = performance.now();
          timeTaken = ((receiveTimestamp - receivedData.sendTimestamp) / 1000).toFixed(4) + ' sec';
      }

      console.log(`SaasWidget: Received message data (${dataSize} KB):`, receivedData);

      const listItem = document.createElement('li');
      // Truncate the payload for display
      const displayedPayload = receivedData.payload && receivedData.payload.length > 20
                                ? receivedData.payload.substring(0, 20) + '...'
                                : receivedData.payload;

      // Create a new object for display to avoid modifying the original receivedData
      const displayData = { ...receivedData, payload: displayedPayload };

      listItem.textContent = `From ${event.origin} (HostApp) - Size: ${dataSize} KB - Time: ${timeTaken}: ${JSON.stringify(displayData)}`;
      messageList.appendChild(listItem);
    });

    console.log('SaasWidget: Listening for messages...');

</script>

</body>
</html>
"""

# JavaScript template for the embedded script
SAAS_WIDGET_JS_TEMPLATE = """
(function() {
    // Read app_id from the script tag's src attribute
    const scriptTag = document.currentScript;
    const scriptSrc = scriptTag.src;
    const urlParams = new URLSearchParams(scriptSrc.split('?')[1]);
    const appId = urlParams.get('app_id') || 'default_app';

    console.log(`SaasWidget Script: Loaded for App ID: ${appId}`);

    // Function to generate a string of a specific size (in KB)
    function generateLargeString(kb) {
        const bytes = kb * 1024;
        let result = '';
        const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        const charactersLength = characters.length;
        for (let i = 0; i < bytes; i++) {
            result += characters.charAt(Math.floor(Math.random() * charactersLength));
        }
        return result;
    }

    // --- SaasWidget Script injecting UI ---
    const container = document.getElementById('saasWidgetContainer');
    if (container) {
        container.innerHTML = `
            <h3>SaasWidget Content for App ID: ${appId}</h3>
            <p>This content is injected by the SaasWidget script.</p>
            <div class="controls">
                <label for="saasWidgetSendSizeScript">Data size to send (KB) to HostApp:</label>
                <input type="text" id="saasWidgetSendSizeScript" value="1" size="5">
                <button id="sendToHostAppScriptBtn">Send Message to HostApp</button>
            </div>
            <h4>Received Messages from HostApp:</h4>
            <ul id="saasWidgetMessagesScript"></ul>
        `;

        const sendBtn = document.getElementById('sendToHostAppScriptBtn');
        const messageList = document.getElementById('saasWidgetMessagesScript');
        const sendSizeInput = document.getElementById('saasWidgetSendSizeScript');

        // --- SaasWidget Script sending message back to HostApp ---
        // In this script embed model, "sending back" means calling a function
        // exposed by the HostApp page or dispatching a custom event.
        sendBtn.addEventListener('click', () => {
            const sizeKB = parseInt(sendSizeInput.value, 10) || 0;
            const largeData = generateLargeString(sizeKB);

            const messageData = {
                status: 'SaasWidget script is alive!',
                random: Math.random(),
                dataSizeKB: sizeKB,
                payload: largeData,
                sendTimestamp: performance.now()
            };

            // Call the function provided by the HostApp page
            if (window.handleMessageFromSaasWidget) {
                 window.handleMessageFromSaasWidget(messageData);
                 console.log(`SaasWidget Script: Sent message (${sizeKB} KB) to HostApp`, messageData);
            } else {
                 console.warn('SaasWidget Script: HostApp handler (window.handleMessageFromSaasWidget) not found.');
            }
        });

        // --- SaasWidget Script receiving message from HostApp ---
        // The HostApp page will call a function exposed by this script.
        // We expose a global function for the HostApp to call.
        window.handleMessageFromHostApp = (messageData) => {
            console.log('SaasWidget Script: Received message from HostApp', messageData);

            const dataSize = messageData.payload ? (messageData.payload.length / 1024).toFixed(2) : 'N/A';

            let timeTaken = 'N/A';
            if (messageData.sendTimestamp) {
                const receiveTimestamp = performance.now();
                timeTaken = ((receiveTimestamp - messageData.sendTimestamp) / 1000).toFixed(4) + ' sec';
            }

            const listItem = document.createElement('li');
            const displayedPayload = messageData.payload && messageData.payload.length > 20
                                     ? messageData.payload.substring(0, 20) + '...'
                                     : messageData.payload;

            const displayData = { ...messageData, payload: displayedPayload };

            listItem.textContent = `From HostApp - Size: ${dataSize} KB - Time: ${timeTaken}: ${JSON.stringify(displayData)}`;
            messageList.appendChild(listItem);
        };

        console.log('SaasWidget Script: UI injected and listeners attached.');

    } else {
        console.error('SaasWidget Script: Could not find container #saasWidgetContainer');
    }

})(); // Immediately Invoked Function Expression (IIFE) to keep scope clean
"""


@app.get("/saaswidget", response_class=HTMLResponse)
async def saaswidget_page(app_id: str = Query("default_app")):
    """
    Serves the main SaasWidget HTML page (iframe version).
    Not directly used by the script embed POC.
    """
    rendered_html = SAAS_WIDGET_HTML_TEMPLATE.replace("{{ app_id }}", app_id)
    return HTMLResponse(content=rendered_html, status_code=200)

@app.get("/saaswidget.js", response_class=Response)
async def saaswidget_script(app_id: str = Query("default_app")):
    """
    Dynamically generates and serves the SaasWidget JavaScript file
    based on the 'app_id' URL parameter for script embedding.
    """
    # In a real application, you would use the app_id here to:
    # - Look up configuration or data specific to this app_id
    # - Customize the JavaScript code (e.g., API keys, feature flags)
    # - Validate the app_id and potentially the origin of the request for security

    # For this POC, we inject the app_id into the JavaScript code itself
    # and use it to customize the displayed content.
    # We also replace placeholder for the template string in JS
    rendered_js = SAAS_WIDGET_JS_TEMPLATE.replace("${appId}", app_id) # Use replace for simple string substitution

    # Return the JavaScript content with the correct content type
    return Response(content=rendered_js, media_type="application/javascript")


if __name__ == "__main__":
    import uvicorn
    # To run this FastAPI app:
    # 1. Make sure you have FastAPI and uvicorn installed (`pip install fastapi uvicorn`)
    # 2. Save this code as a Python file (e.g., `saaswidget_server_script.py`)
    # 3. Run it from your terminal: `uvicorn saaswidget_server_script:app --reload --port 8001`
    # This will start a server on http://localhost:8001

    # Remember to also serve HostApp.html (from the first immersive above)
    # from http://localhost:8000.
    # You can use a simple HTTP server for this, like Python's built-in:
    # `cd path/to/HostApp.html`
    # `python -m http.server 8000`
    uvicorn.run(app, host="0.0.0.0", port=8001)

