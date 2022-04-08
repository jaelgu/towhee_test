# Deploy Reverse-Image-Search System

## Prepare Environment

1. Install packages

```
$ pip install -r requirements.txt
```

2. Start a Milvus service & Mysql service

- Suggestion: docker containers
- Setup [configs](./server/config.py):
  - Milvus Configurations
  - Mysql Configurations
  - Data Path

## Start Server

```
$ cd server
$ python main.py
```

Then check in browser for FastAPI interface: https://localhost:5000/docs

## Start Client

Start front-end service and check web-service in browser.
