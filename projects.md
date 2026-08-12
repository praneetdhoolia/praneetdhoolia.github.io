---
layout: page
title: Projects
permalink: /projects/
---

A few things I've built, mostly around LangGraph, agent orchestration, and MCP. See [Writing]({{ '/' | relative_url }}) for the full build logs.

<div class="project-list">

  <div class="project-card">
    <h3>LangGraph Software Engineering Agent</h3>
    <p>An autonomous coding agent with hierarchical repo understanding: file-level and package-level semantic summaries generated in parallel via LangGraph's fan-out (<code>Send</code>) API. Resolves issues by first localizing them to the relevant files, keeping context within token limits.</p>
    <div class="project-links">
      <a href="https://github.com/praneetdhoolia/langgraph-se-agent" target="_blank" rel="noopener">GitHub ↗</a>
      <a href="{% link _posts/2025-02-08-software-engineering-agent-langgraph.md %}">Write-up</a>
    </div>
  </div>

  <div class="project-card">
    <h3>LangGraph + MCP Universal Assistant</h3>
    <p>A multi-agent router that indexes tools, prompts, and resources from multiple MCP servers into a vector store for dynamic agent selection, plus a generic MCP session wrapper (Strategy pattern) for extensible tool discovery and invocation. Built with my brother, a UQ alum.</p>
    <div class="project-links">
      <a href="https://github.com/esxr/langgraph-mcp" target="_blank" rel="noopener">GitHub ↗</a>
      <a href="{% link _posts/2025-01-20-universal-assistant-langgraph-mcp.md %}">Write-up</a>
    </div>
  </div>

  <div class="project-card">
    <h3>LangGraph Retrieval &amp; RAG Pipeline</h3>
    <p>Extended LangGraph's retrieval template with configurable multi-hop site crawling and a Milvus-backed vector index, deployed to LangGraph Cloud, and connected an <a href="https://www.assistant-ui.com/" target="_blank" rel="noopener">assistant-ui</a> chat client.</p>
    <div class="project-links">
      <a href="{% link _posts/2024-12-31-expanding-langgraph-retrieval-agent.md %}">Building it</a>
      <a href="{% link _posts/2025-01-16-improvements-to-retrieval-agent.md %}">Improvements</a>
      <a href="{% link _posts/2025-01-06-deploying-to-langgraph-cloud.md %}">Deploying</a>
      <a href="{% link _posts/2025-01-08-adding-chat-client-to-langgraph-assistant.md %}">Chat client</a>
    </div>
  </div>

</div>
