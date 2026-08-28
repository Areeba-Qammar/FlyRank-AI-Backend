# Week 3 - Containerize Your Stack

## Stage 0: Postgres Setup Command
```cmd
docker run --name taskdb -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=tasks -p 5432:5432 -v taskdata:/var/lib/postgresql/data -d postgres