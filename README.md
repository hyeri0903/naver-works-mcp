### ⚒️Setting
~~~
$ mkdir works-mcp
$ cd works-mcp
$ python3 -m venv venv   
$ source venv/bin/activate
$ pip install 'mcp[cli]'  httpx
~~~

### ✅ Setting Cursor, Claude Desktop settings.json
#### 1. Local Download and Run
~~~
{
  "mcpServers": {
     "naver-works-mcp": {
      "command": "{python path}",
      "args": ["{main.py file path}"],
      "env": {
        "WORKS_API_TOKEN": "{TOKEN}"
      }
    }
  }
}
~~~


#### 2. Docker Image
~~~
{
  "mcpServers": {
    "naver-works-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "WORKS_API_TOKEN",
        "haileyjung/naverworks:latest"
      ],
      "env": {
        "WORKS_API_TOKEN": "{TOKEN}"
      }
    }
  }
}
~~~


### Setting Package
~~~
$ python -m venv venv

# MAC
$ source venv/bin/activate  
# Window 
$ source venv\Scripts\activate

$ pip install -r requirements.txt
~~~


### ▶️ Run dev mode mcp server
~~~
$ mcp dev main.py
~~~

### ▶️ Run MCP Server Inspector
~~~
$ npx @modelcontextprotocol/inspector dist/index.js
~~~

