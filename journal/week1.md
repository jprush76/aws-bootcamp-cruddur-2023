# Week 1 — App Containerization

## Add Postgres

As we need to use `Postgres` locally, I add it by a container. So here it is the code that we need to add to our docker compose file:

```yaml
    services:
    db:
        image: postgres:13-alpine
        restart: always
        environment:
        - POSTGRES_USER=postgres
        - POSTGRES_PASSWORD=password
        ports:
        - '5432:5432'
        volumes: 
        - db:/var/lib/postgresql/data
    volumes:
    db:
        driver: local
```

When `Postgres` is running in gitpod, we have two methods to test locally if it's working.

### Postgres VS Code Extension
You must add a DB extension to your VS Code in Gitpod to test the `Postgres` connection. I chose this one:

![Postgres VS Code Extension](./assets/week-1-postgres-vs-code-extension.png)

Then you try to connect to `Postgres`:

![](./assets/week-1-postgres%20test.png)

### Run Postgres Client

If you want to use `Postgres` client in gitpod, you need to install it first. So I add this lines of code to my `gitpod.yml` to automate its installation at the start of gitpod.

```yaml
    - name: postgres
        init: |
        curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc|sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
        echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list
        sudo apt update
        sudo apt install -y postgresql-client-13 libpq-dev
```

Then to start `Postgres` client you need to use `psql --host localhost`

![Connecting to postgres from the terminal client](./assets/week-1-postgres%20test%20cli.png)