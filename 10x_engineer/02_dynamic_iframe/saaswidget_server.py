from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates # FastAPI often uses Jinja2 for templating, though we'll use render_template_string for simplicity here

app = FastAPI()

# HTML template for the SaasWidget page
# We'll inject the app_id into this template
# Note: This is the same HTML content as before, just embedded in the Python code
SAAS_WIDGET_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SaasWidget Content - App ID: {{ app_id }}</title>
    <style>
        body { font-family: sans-serif; background-color: #f0f0f0; padding: 20px;}
        button { margin-top: 10px; padding: 8px 15px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc;}
        input[type="text"] { padding: 6px; margin-left: 5px; border-radius: 4px; border: 1px solid #ccc;}
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

@app.get("/saaswidget", response_class=HTMLResponse)
async def saaswidget_page(app_id: str = Query("default_app")):
    """
    Dynamically generates the SaasWidget HTML page based on the 'app_id' URL parameter.
    Uses FastAPI to handle the request.
    """
    # In a real application, you would use the app_id here to:
    # - Look up configuration or data specific to this app_id
    # - Customize the HTML template, features, or initial data
    # - Validate the app_id and potentially the origin of the request for security

    # For this POC, we just inject the app_id into the HTML title and body
    # We use the replace() method to substitute the app_id into the template string
    # Note: For more complex templating, Jinja2 is recommended with FastAPI
    rendered_html = SAAS_WIDGET_HTML_TEMPLATE.replace("{{ app_id }}", app_id)

    return HTMLResponse(content=rendered_html, status_code=200)

if __name__ == "__main__":
    import uvicorn
    # To run this FastAPI app:
    # 1. Make sure you have FastAPI and uvicorn installed (`pip install fastapi uvicorn`)
    # 2. Save this code as a Python file (e.g., `saaswidget_server_fastapi.py`)
    # 3. Run it from your terminal: `uvicorn saaswidget_server_fastapi:app --reload --port 8001`
    # This will start a server on http://localhost:8001

    # Remember to also serve HostApp.html from http://localhost:8000
    # You can use a simple HTTP server for this, like Python's built-in:
    # `cd path/to/HostApp.html`
    # `python -m http.server 8000`
    uvicorn.run(app, host="0.0.0.0", port=8001)

