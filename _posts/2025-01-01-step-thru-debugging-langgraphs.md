---
layout: post
title: Step-thru Debugging Your LangGraphs
date: 2025-01-01
---

Most of the details required are already covered in langgraph tutorial here: https://langchain-ai.github.io/langgraph/tutorials/langgraph-platform/local-server/

*Key points covered there are:*

1.  Install LangGraph CLI
    ```bash
    pip install --upgrade "langgraph-cli[inmem]"
    ```
2.  Install the dependencies
    ```bash
    pip install -e .
    ```
3.  Use the CLI to run langGraph server
    ```bash
    langgraph dev
    ```
4.  You may now use LangGraph Studio Web UI at: [https://smith.langchain.com/studio/?baseUrl=http://locahost:2024](https://smith.langchain.com/studio/?baseUrl=http://locahost:2024)

*Here are the additions to enable step-thru-debugging:*

1.  Install debugpy in your virtual environment for the langgraph project
    ```bash
    pip install debugpy
    ```

2.  Start langgraph API server in debug mode. In the following we are telling langgraph-cli to allow clients to listen on Port 2025 for debugger events
    ```bash
    langgraph dev --debug-port 2025
    ```

3.  Attach to debugger from your IDE. E.g., in here's my VS Code launch config:
    ```json
    {
        "version": "0.2.0",
        "configurations": [

            {
                "name": "Python Debugger: Remote Attach",
                "type": "debugpy",
                "request": "attach",
                "connect": {
                    "host": "localhost",
                    "port": 2025
                },
                "pathMappings": [
                    {
                        "localRoot": "${workspaceFolder}",
                        "remoteRoot": "."
                    }
                ],
                "justMyCode": false
            }
        ]
    }
    ```

4.  I can now put a breakpoint on any of my langgraph code files and step-thru the execution!