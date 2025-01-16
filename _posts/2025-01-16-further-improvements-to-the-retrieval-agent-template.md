---
layout: post
title: Further Improvements to the Retrieval Agent Template
date: 2025-01-16
---

### 1. Creating indexes from pre-crawled sites

Depending on the size of a site, crawling may be a long running process. In such cases our indexing process may timeout. We may want to run crawling actors independently (i.e., outside of our Index Graph)
To accommodate such cases, I added a new indexing configuration `apify_dataset_id` which may be used to directly load a pre-crawled dataset. Apify stores the outcome of a crawl, and allows loading the dataset directly to a `langchain.core.Document` loader.

Apify dataset storage
![Apify Dataset](/media/apify-dataset.jpg)


Additional indexing configuration
```python
# same as before
@dataclass(kw_only=True)
class IndexConfiguration(CommonConfiguration):
    # new configuration for specifying pre-crawled Apify dataset id
    apify_dataset_id: str = field(
        default="",
        metadata={
            "description": "Pre-crawled Apify dataset ID"
        },
    )

    # same as before
```

Modifications to index_graph for directly building an index from pre-crawled dataset.
```python
# same as before
from langchain_community.document_loaders import ApifyDatasetLoader
# same as before

def apify_crawl(configuration: IndexConfiguration):
    # same as before

    # changes to accommodate loading from pre-crawled datasets
    dataset_id = configuration.apify_dataset_id

    if dataset_id:
        loader = ApifyDatasetLoader(
            dataset_id=dataset_id,
            dataset_mapping_function=lambda item: Document(
                page_content=item.get('text') or "", metadata={"url": item["url"]}
            ),
        )
    else:
        # same as before: use the apify actor to crawl
        

    return loader.load()

# same as before

async def index_docs(
    state: IndexState, *, config: Optional[RunnableConfig] = None
) -> dict[str, str]:
    if not config:
        raise ValueError("Configuration required to run index_docs.")
    with retrieval.make_retriever(config) as retriever:
        configuration = IndexConfiguration.from_runnable_config(config)
        # either starter_urls, or apify_dataset_id of pre-crawled should be able to trigger 
        # crawling / loading the documents 
        if not state.docs and (configuration.starter_urls or configuration.apify_dataset_id):
            print(f"starting crawl ...")
            crawled_docs = apify_crawl(configuration)
            # same as before
```

### 2. Splitting documents for fine-grained retrieval

So far I directly embedded a crawled document. Crawled documents may be arbitrarily large. 

1. This puts an uncertainity on how many `top_k` retrieval results I should consider for response generation. In fact, for one site the documents were so large that only 3 of them crossed the token limit allowed on the generation node.
2. For complex queries, where composing high quality answers may need information from multiple documents, limiting `top_k` may lead to poor results.

To address this, I split crawled documents into multiple documents as follows:

```python
# src/retrieval_graph/index_graph.py

# new import
from langchain_text_splitters import RecursiveCharacterTextSplitter

# same as before

async def index_docs(
    state: IndexState, *, config: Optional[RunnableConfig] = None
) -> dict[str, str]:
    if not config:
        raise ValueError("Configuration required to run index_docs.")
    with retrieval.make_retriever(config) as retriever:
        configuration = IndexConfiguration.from_runnable_config(config)
        if not state.docs and (configuration.starter_urls or configuration.apify_dataset_id):
            print(f"starting crawl ...")
            crawled_docs = apify_crawl(configuration)
            # use a 1000 char size overlapping window based splitter to create smaller document chunks to index
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            state.docs = text_splitter.split_documents(crawled_docs)
            
            # same as before
```

We can now retrieve a larger set of `top_k` results. Since the maximum chunk size here is `1000`, we can deterministically configure the `top_k` based on the token limits supported by the language model used in the response generation node. E.g., if the token limit is 100,000 tokens, we can potentially use `top_k` upto `500` (assuming an average token size of 5 characters). Note that I already support a configuration for specifying `top_k`.

```python
# src/retrieval_graph/retreival.py
# ...
def make_milvus_retriever(
    configuration: IndexConfiguration, embedding_model: Embeddings, **kwargs
) -> Generator[VectorStoreRetriever, None, None]:
    # ...
    yield vstore.as_retriever(search_kwargs=configuration.search_kwargs)
# ...
```

Here, `search_kwargs = {"k": 10}` conveys that retriever will return top 10 results.

### 3. Rate limit errors while embedding
Emebedding Models put limits on the number of token per unit time. Initially, I embedded the whole set of crawled (or split) documents in a single call. For large sites, this ran into rate limit errors. With the following enhancement I added a batch size configuration, split documents into multiple batches, and added a time delay to avoid rate limits.

```python
# src/retrieval_graph/configuration.py
# ...
@dataclass(kw_only=True)
class IndexConfiguration(CommonConfiguration):
    # ...
    batch_size: int = field(
        default=400,
        metadata={
            "description": "Number of documents to index in a single batch."
        },
    )
    # ...
```

```python
# src/retrieval_graph/index_graph.py
# ...

# generator function to create batches
def create_batches(docs, batch_size):
    """Chunk documents into smaller batches."""
    for i in range(0, len(docs), batch_size):
        yield docs[i:i + batch_size]

async def index_docs(
    state: IndexState, *, config: Optional[RunnableConfig] = None
) -> dict[str, str]:
    if not config:
        raise ValueError("Configuration required to run index_docs.")
    with retrieval.make_retriever(config) as retriever:
        configuration = IndexConfiguration.from_runnable_config(config)
        # ...
        stamped_docs = ensure_docs_have_user_id(state.docs, config)
        # embed in batches to avoid rate limit errors
        batch_size = configuration.batch_size
        for i, batch in enumerate(create_batches(stamped_docs, batch_size)):
            if configuration.retriever_provider == "milvus":
                retriever.add_documents(batch)
            else:
                await retriever.aadd_documents(batch)
            # sleep if there are more batches to embed
            if i < (len(stamped_docs) // batch_size):
                time.sleep(60)
    return {"docs": "delete"}
# ...
```

### 4. Pre-created indexes (for ease of demo)
While demonstrating the solution to clients, I noticed the following:
1. Live crawling can take quite a while.
2. Indexing pre-crawled datasets may also take some time due to delays needed to avoid rate limit errors. It also adds to model usage cost (if you are repeating it).

To address these, I added:
1. Configurations that (optionally) load an index from an alternate location.
2. Some of the pre-created indexes for clients to the repository, so the index files are available in the LangGraph cloud deployment.

```python
# src/retrieval_graph/configuration.py
# ...
@dataclass(kw_only=True)
class Configuration(CommonConfiguration):
    """The configuration for the agent."""
    # optional: index location
    alternate_milvus_uri: Optional[str] = field(
        default="",
        metadata={
            "description": "If you want to use one of the already available indexes, provide the file location here."
        },
    )
    # ...
```


```python
# src/retrieval_graph/retrieval.py
# ...
@contextmanager
def make_milvus_retriever(
    configuration: IndexConfiguration, embedding_model: Embeddings, **kwargs
) -> Generator[VectorStoreRetriever, None, None]:
    # ...
    # use alternate milvus uri if provided in the configuration
    milvus_uri = kwargs.get("alternate_milvus_uri") or os.environ.get("MILVUS_DB")
    vstore = Milvus (
        # ...
    )
    # ...
# ...
```

During demonstrations, I now use pre-created indexes to save time and money.