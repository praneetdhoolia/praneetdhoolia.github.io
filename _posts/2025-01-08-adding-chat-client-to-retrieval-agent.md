---
layout: post
title: Adding a Chat Client to a Retrieval Agent
date: 2025-01-08
---

[Previously]({% link _posts/2025-01-06-deploying-to-langgraph-cloud.md %}), I deployed an enhanced retrieval template to langgraph cloud. Now, I want to point a chat client to it using [**assistant-ui**](https://www.assistant-ui.com/).

The following are required before deploying the chat client:
1. An existing [node.js installation](https://nodejs.org/en/download).
2. An active deployment on the [LangGraph Cloud API Server](https://langchain-ai.github.io/langgraph/cloud/quick_start/).
Assistant UI can be also be installed in an existing React Project, as covered in the [assistant-ui langgraph cloud documentation](https://www.assistant-ui.com/docs/runtimes/langgraph).

To create a new project, I'll follow these steps:

1. Ensure `npx` is installed.
    ```bash
    npm install -g npx
    ```

2. Create a new project based on the LangGraph assistant-ui template
    ```bash
    npx create-assistant-ui@latest -t langgraph my-app
    ```

3. Create a new assistant for your graph on LangSmith using LangGraph Studio or the API Docs.

![Create a new assistant](/media/create-assistant.png)

4. Create an `.env.local` file in your project with the following variables:
    ```bash
    LANGCHAIN_API_KEY=your_api_key
    LANGGRAPH_API_URL=your_api_url
    NEXT_PUBLIC_LANGGRAPH_ASSISTANT_ID=your_assistant_id
    ```

5. Ensure the LangChain API Key is also present in your [LangSmith API Keys](https://smith.langchain.com/settings/workspaces/apikeys) to allow access to your deployments.

6. Navigate to the `assistant-ui` project root folder and start the node.js server.
```bash
npm run dev
```

7. You can now use the Chat Client using the server's port! (https://localhost:3000 in my case)
![Assistant Demo](/media/assistant-demo.gif)


