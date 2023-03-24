# Week 4 — Postgres and RDS

## Provision RDS Instance

In this link we can find the documentation of create-db-instance: [create-db-instance documentation](https://docs.aws.amazon.com/cli/latest/reference/rds/create-db-instance.html)

With this command we create a RDS Instace thru terminal:

```bash
aws rds create-db-instance \
  --db-instance-identifier cruddur-db-instance \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version  14.6 \
  --master-username yourusername \
  --master-user-password yourpassword \
  --allocated-storage 20 \
  --availability-zone us-east-1a \
  --backup-retention-period 0 \
  --port 5432 \
  --no-multi-az \
  --db-name cruddur \
  --storage-type gp2 \
  --publicly-accessible \
  --storage-encrypted \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --no-deletion-protection
```

__Note: The password must contain from 8 to 30 characters. (PostgreSQL)__

Once is created (takes about 10 to 12mins), you can see it in the AWS RDS console

![RDS instance](./assets/week-4/week-4-rds-db-created-ok.png)

__Note: It's important to know that if you are not going to using this instance right away, you can temporaly stop it for 7 days. Past that time the RDS instance will automatically start again.__

## PostgresSQL

To connect to psql via the psql client cli tool remember to use the host flag to specific localhost (__In this container environment__).

```bash
psql -Upostgres --host localhost
```

Then you put the password for the user and you are in!

### Common PSQL commands:

```sql
\x on -- expanded display when looking at data
\q -- Quit PSQL
\l -- List all databases
\c database_name -- Connect to a specific database
\dt -- List all tables in the current database
\d table_name -- Describe a specific table
\du -- List all users and their roles
\dn -- List all schemas in the current database
CREATE DATABASE database_name; -- Create a new database
DROP DATABASE database_name; -- Delete a database
CREATE TABLE table_name (column1 datatype1, column2 datatype2, ...); -- Create a new table
DROP TABLE table_name; -- Delete a table
SELECT column1, column2, ... FROM table_name WHERE condition; -- Select data from a table
INSERT INTO table_name (column1, column2, ...) VALUES (value1, value2, ...); -- Insert data into a table
UPDATE table_name SET column1 = value1, column2 = value2, ... WHERE condition; -- Update data in a table
DELETE FROM table_name WHERE condition; -- Delete data from a table
```

### Create a database

From the terminal we can do it with this command:

```bash
createdb cruddur -h localhost -U postgres
```

And if you are in PSQL client, you can create a database with this command:

```sql
CREATE DATABASE cruddur;
```

### Drop a database

You can delete a database from the PSQL client with this command:

```sql
DROP DATABASE cruddur;
```

### Database scripts

First, we create a folder call 'db' inside our `backend-flask` folder to put all our db scrits inside.

#### __Add UUID Extension__

We need to Postgres generate UUIDs, So we need to use an extension called `uuid-ossp`

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

#### __SCRIPT schema.sql__

Put this code inside `db/schema.sql`, this code first create the uuids extension, if the tables exist in the db, its going to drop it both, and then will create both tables. That way we avoid mistakes.

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.activities;

CREATE TABLE public.users (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  display_name text,
  handle text,
  cognito_user_id text,
  created_at TIMESTAMP default current_timestamp NOT NULL
);

CREATE TABLE public.activities (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_uuid UUID NOT NULL,
  message text NOT NULL,
  replies_count integer DEFAULT 0,
  reposts_count integer DEFAULT 0,
  likes_count integer DEFAULT 0,
  reply_to_activity_uuid integer,
  expires_at TIMESTAMP,
  created_at TIMESTAMP default current_timestamp NOT NULL
);
```

#### __SCRIPT seed.sql__

Now let's create `db/seed.sql` with our mock data to test it:

```sql
-- this file was manually created
INSERT INTO public.users (display_name, handle, cognito_user_id)
VALUES
  ('Andrew Brown', 'andrewbrown' ,'MOCK'),
  ('Andrew Bayko', 'bayko' ,'MOCK');

INSERT INTO public.activities (user_uuid, message, expires_at)
VALUES
  (
    (SELECT uuid from public.users WHERE users.handle = 'andrewbrown' LIMIT 1),
    'This was imported as seed data!',
    current_timestamp + interval '10 day'
  )
```

#### __Import Script and run it__

To use this next command, we need to be inside our `backend-flask` folder in the gitpod terminal:

```bash
psql cruddur < db/schema.sql -h localhost -U postgres
```

To be more fast in our work, we create a constant named `CONNECTION_URL`, so this way we don't have to put our password every time we run a psql script.

```bash
export CONNECTION_URL="postgresql://postgres:yourpassword@localhost:5432/cruddur"
```

If you want to set this constant permanent in your gitpod environment, use this command:

```bash
gp env CONNECTION_URL="postgresql://postgres:yourpassword@localhost:5432/cruddur"
```

Now we test if is it working. Try this command and you should connect right away without enter your password:

```bash
psql $CONNECTION_URL
```

So this was our local connection variable, now let's create the production variable. You need to retrieve the conn url (endpoint) from your RDS Instance.

```bash
export PROD_CONNECTION_URL="postgresql://youruser:yourpassword@cruddur-db-instance.cmsg2gsmxxta.us-east-1.rds.amazonaws.com:5432/cruddur"
```

And we made it permanent in our gitpod environment:

```bash
gp env PROD_CONNECTION_URL="postgresql://youruser:yourpassword@cruddur-db-instance.cmsg2gsmxxta.us-east-1.rds.amazonaws.com:5432/cruddur"
```

### BASH Scripts

Let's create a folder named 'bin' inside our `backend-flask` folder.

Create and put these next file into the 'bin' folder.



#### __SCRIPT db-create__

```bash
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-create"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<< "$CONNECTION_URL")
psql $NO_DB_CONNECTION_URL -c "CREATE DATABASE cruddur;"
```

#### __SCRIPT db-drop__

```bash
#! /usr/bin/bash
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-drop"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<< "$CONNECTION_URL")
psql $NO_DB_CONNECTION_URL -c "DROP DATABASE cruddur;"
```

#### __SCRIPT db-schema-load__

```bash
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-schema-load"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

schema_path=$(realpath .)/db/schema.sql
echo $schema_path

if [ "$1" = "prod" ]; then
    echo "Using production"
    URL=$PROD_CONNECTION_URL
else
    URL=$CONNECTION_URL
fi

psql $URL cruddur < $schema_path
```

#### __SCRIPT db-connect__

```bash
#! /usr/bin/bash

psql $CONNECTION_URL
```

#### __SCRIPT db-seed__

```bash
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-seed"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

seed_path=$(realpath .)/db/seed.sql
echo $seed_path

if [ "$1" = "prod" ]; then
    echo "Using production"
    URL=$PROD_CONNECTION_URL
else
    URL=$CONNECTION_URL
fi

psql $URL cruddur < $seed_path
```



#### __Making executables__

After you had created the files, you must give executable permission to each file, with change mode command (chmod)

```bash
chmod u+x bin/db-create
chmod u+x bin/db-drop
chmod u+x bin/db-schema-load
chmod u+x bin/db-connect
chmod u+x bin/db-seed
```
