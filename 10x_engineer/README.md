This folder contains working code mentioned in my blog post published on a few sites:
* https://www.linkedin.com/pulse/10x-engineer-dead-long-live-ha-pham-pdrwc
* https://open.substack.com/pub/halhx/p/the-10x-engineer-is-dead-long-live


### How to run Attempt 1 - data exchange via static iframe (01_static_iframe)
* Open your terminal or command prompt.
* Navigate to `01_static_iframe`
* Start two simple HTTP servers on different ports.


    Run python -m http.server 8000 (This will serve ExistingApp.html from http://localhost:8000)
    Open a second terminal window in the same directory.
    Run python -m http.server 8001 (This will serve AppGenie.html from http://localhost:8001)


* Open your web browser and go to http://localhost:8000/HostApp.html.
* Open your browser's developer console (F12 or right-click -> Inspect -> Console) to see the console.log messages from both the parent and the iframe.
* Click the buttons on both the parent page and within the iframe to send messages.

### How to run Attempt 2 - iframe content is created dynamically (02_dynamic_iframe)
* Open your terminal or command prompt.
* Navigate to `02_static_iframe`
* Start two simple HTTP servers on different ports.


    Run python -m http.server 8000 (This will serve ExistingApp.html from http://localhost:8000)
    Open a second terminal window in the same directory.
    Run python saaswidget_server.py (This will run SaaS Widget server on http://localhost:8001, which is reponsible for generating the iframe content on the fly)


* Open your web browser and go to http://localhost:8000/HostApp.html.
* Open your browser's developer console (F12 or right-click -> Inspect -> Console) to see the console.log messages from both the parent and the iframe.
* Click the buttons on both the parent page and within the iframe to send messages.

### How to run Attempt 3 - embedded div tag is used instead of iframe (03_dynamic_embedding)
follow the same instruction as Attempt 2
