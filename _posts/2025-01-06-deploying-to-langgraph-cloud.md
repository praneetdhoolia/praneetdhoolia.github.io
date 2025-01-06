---
layout: post
title: Deploying to LangGraph Cloud
date: 2025-01-06
---

I deployed my retrieval graph to langgraph cloud. The process was quite straight-forward.

1. I created a **Plus** account on [**LangSmith**](https://smith.langchain.com/). This is necessary. Free-tier developer account does not allow deploying to LangGraph cloud. This costs 39 USD / month.

2. Now from LangSmith left-nav bar, I can go to *Deployments > LangGraph Platform*. Here I can initiate a **+ New Deployment**.

3. I can *Import from GitHub* my langGraph repo! And add my environment configurations (the ones in `.env` file).

    ![LangGraph Cloud Deployment](/media/langgraph-cloud-deployment.png)

4. And I just **Submit** to deploy! This step takes around 15+ minutes. Once this finishes, I click on LangGraph Studio to access the studio to test my graphs!

---

I noticed that to update an environment variable, I need to deploy a new version. Whole 15+ minutes once again 😞. I have no doubt that this will get better in the future.
