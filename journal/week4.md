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
  display_name text NOT NULL,
  handle text NOT NULL,
  email text NOT NULL,
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

#### __SCRIPT db-sessions__

```bash
#! /usr/bin/bash
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-sessions"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

NO_DB_URL=$(sed 's/\/cruddur//g' <<<"$URL")
psql $NO_DB_URL -c "select pid as process_id, \
       usename as user,  \
       datname as db, \
       client_addr, \
       application_name as app,\
       state \
from pg_stat_activity;"
```

#### __SCRIPT db-setup__

```bash
#! /usr/bin/bash
-e # stop if it fails at any point

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-setup"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

bin_path="$(realpath .)/bin"

source "$bin_path/db-drop"
source "$bin_path/db-create"
source "$bin_path/db-schema-load"
source "$bin_path/db-seed"
```

#### __Making executables__

After you had created the files, you must give executable permission to each file, with change mode command (chmod)

```bash
chmod u+x bin/db-create
chmod u+x bin/db-drop
chmod u+x bin/db-schema-load
chmod u+x bin/db-connect
chmod u+x bin/db-seed
chmod u+x bin/db-sessions
chmod u+x bin/db-setup
```


## Install Postgres Client

Add these lines into `requirements.txt` inside our `backend-flask` folder.

```bash
psycopg[binary]
psycopg[pool]
```

Then install the new requirements:

```bash
pip install -r requirements.txt
```

Create a new file `lib/db.py` in our backend:

```py
from psycopg_pool import ConnectionPool
import os

class Db:
    def __init__(self):
        self.init_pool()

    def init_pool(self):
        connection_url = os.getenv("CONNECTION_URL")
        self.pool = ConnectionPool(connection_url)
    

    def query_commit_returning_id(self, sql, *args):
        print("SQL STATEMENT-[commit-with-returnin-id]---")
        try:
            conn = self.pool.connection()
            cur = conn.cursor()
            cur.execute(sql, *args)
            returning_id = cur.fetchone()[0]
            conn.commit()
            return returning_id
        except Exception as err:
            self.print_sql_err(err)
            #conn.rollback()

    # we want to commit data (like insert)
    def query_commit(self, sql, *args):
        print("SQL STATEMENT-[commit]---------")
        try:
            conn = self.pool.connection()
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
        except Exception as err:
            self.print_sql_err(err)
            #conn.rollback()

    # when we want to return a json object
    def query_array_json(self, sql):
        print("SQL STATEMENT-[array]---------")
        print(sql)
        print("------------------------------")

        wrapped_sql = self.query_wrap_array(sql)
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(wrapped_sql)
                # this will return a tuple
                # the first field being the data
                json = cur.fetchone()
                return json[0]

    # when we want to return an array of json objects
    def query_object_json(self, sql):
        print("SQL STATEMENT-[object]---------")
        print(sql)
        print("------------------------------")

        wrapped_sql = self.query_wrap_object(sql)
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(wrapped_sql)
                json = cur.fetchone()
                return json[0]
        

    def query_wrap_object(self, template):
        sql = f"""
        (SELECT COALESCE(row_to_json(object_row),'{{}}'::json) FROM (
        {template}
        ) object_row);
        """
        return sql

    def query_wrap_array(self, template):
        sql = f"""
        (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
        {template}
        ) array_row);
        """
        return sql

    # define a function that handles and parses psycopg2 exceptions
    def print_sql_err(self, err):
        # get details about the exception
        err_type, err_obj, traceback = sys.exc_info()

        # get the line number when exception occured
        line_num = traceback.tb_lineno

        # print the connect() error
        print ("\npsycopg ERROR:", err, "on line number:", line_num)
        print ("psycopg traceback:", traceback, "-- type:", err_type)

        # psycopg2 extensions.Diagnostics object attribute
        print ("\nextensions.Diagnostics:", err.diag)

        # print the pgcode and pgerror exceptions
        print ("pgerror:", err.pgerror)
        print ("pgcode:", err.pgcode, "\n")

db = Db()
```

We need to add a new constant into our `docker-compose.yml`, inside `backend-flask` -> `environment`:

```yaml
CONNECTION_URL: "${CONNECTION_URL}"
```

Now let's got to our `services/home_activities.py` and edit it to look like this:

```py
from datetime import datetime, timedelta, timezone

from lib.db import pool, query_wrap_array

#honeycomb
from opentelemetry import trace

tracer = trace.get_tracer("home.activities")

class HomeActivities:
  def run(cognito_user_id=None):
  # def run(logger): // for cloudwathc logs
    #logger.info('Hello Cloudwatch! from  /api/activities/home')
    with tracer.start_as_current_span("http-home-activities"):
      span = trace.get_current_span()
      now = datetime.now(timezone.utc).astimezone()
      span.set_attribute("app.now", now.isoformat())
      
      #span.set_attribute("app.result_length", len(results))

      sql = query_wrap_array("""
      SELECT
        activities.uuid,
        users.display_name,
        users.handle,
        activities.message,
        activities.replies_count,
        activities.reposts_count,
        activities.likes_count,
        activities.reply_to_activity_uuid,
        activities.expires_at,
        activities.created_at
      FROM public.activities
      LEFT JOIN public.users ON users.uuid = activities.user_uuid
      ORDER BY activities.created_at DESC
      """)

      with pool.connection() as conn:
        with conn.cursor() as cur:
          cur.execute(sql)
          # this will return a tuple
          # the first field being the data
          json = cur.fetchone()
      return json[0]
```

## Connect to RDS

Ok, to be enable to connect to our RDS instance from Gitpod, we need to change the security rules, to accept connections from our actual ip address. So to obtain gitpod's IP address we use:

```bash
export GITPOD_IP=$(curl ifconfig.me)
```

This command will create an environment variable `GITPOD_IP` with the session's ip address, so we can use it in a script to automatically refresh the security group.

First, let's create env vars:

```bash
export DB_SG_ID="sg-YOUR-CODE"
gp env DB_SG_ID="sg-YOUR-CODE"
export DB_SG_RULE_ID="sgr-YOUR-CODE"
gp env DB_SG_RULE_ID="sgr-YOUR-CODE"
```

Now to change the rule remotely, use this command:

```bash
aws ec2 modify-security-group-rules \
    --group-id $DB_SG_ID \
    --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={Description=GITPOD,IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"
```

Create a file `bin/rds-update-sg-rule` with the previous command:

```bash
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="rds-update-sg-rule"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

aws ec2 modify-security-group-rules \
    --group-id $DB_SG_ID \
    --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={Description=GITPOD,IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"
```

Then, give the file executable permission.

```bash
chmod u+x bin/rds-update-sg-rule
```

We need to run this script every time we start gitpod, so we go now to our `.gitpod.yml`

Inside 'name: postgres' put:

```yaml
command:
    export GITPOD_IP=$(curl ifconfig.me)
    source "$THEIA_WORKSPACE_ROOT/backend-flask/rds-update-sg-rule"
```

When you successfully change the group rule, you can connect thru terminal to your instance with:

```bash
psql $PROD_CONNECTION_URL
```

__NOTE: It's very important__ from now on, that we change our CONNECTION_URL in our `docker-compose.yml`, because we are going to work with our production DB instead of the local one.

Change it in `services` -> `backend-flask` -> `environment`:

```yaml
CONNECTION_URL: "${PROD_CONNECTION_URL}"
```


## Setup Cognito post confirmation lambda

Go to to AWS Lambda and create a new function called `cruddur-post-confirmation`

![](./assets/week-4/week-4-create-lambda-function.png)

This is the code for the lambda function:

```py
import json
import psycopg2
import os

def lambda_handler(event, context):
    user = event['request']['userAttributes']
    print('userAttributes---------')
    print(user)
    user_display_name = user['name']
    user_email = user['email']
    user_handle = user['preferred_username']
    user_cognito_id = user['sub']
    
    try:
        sql = f"""
            INSERT INTO users (
                display_name, 
                email, 
                handle, 
                cognito_user_id
            )
            VALUES(%s, %s, %s, %s)
        """
        
        conn = psycopg2.connect(os.getenv('CONNECTION_URL'))
        cur = conn.cursor()
        params = [
            user_display_name,
            user_email,
            user_handle,
            user_cognito_id
        ]
        
        cur.execute(sql, *params)
        conn.commit() 

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        
    finally:
        if conn is not None:
            cur.close()
            conn.close()
            print('Database connection closed.')

    return event
```

Due to AWS Lambda missing the required PostgreSQL libraries in the AMI image, we needed to compile psycopg2 with the PostgreSQL libpq.so library statically linked libpq library instead of the default dynamic link.

Some precompiled versions of this layer are available publicly on AWS freely to add to your function by ARN reference.

So, go to the bottom of the page and add a new layer

![Adding a new layer to my lambda function](./assets/week-4/week-4-add-new-layer-to-lambda-function.png)

In the ARM field you need to put the right one for your aws region. You can find it here: [AWS Lambda layer for psycopg2](https://github.com/jetbridge/psycopg2-lambda-layer)

### Permissions

We need to add a security policy to our lambda function, so go to Configuration tab, then click in Permissions on the list. Click on the Role Name, it's going to open a new browser tab with the details.

At Permission Policies, attach a new policy, in the next page click on 'Create policy', choose 'json tab and put this json code:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:CreateNetworkInterface",
                "ec2:DeleteNetworkInterface",
                "ec2:DescribeNetworkInterfaces"
            ],
            "Resource": "*"
        }
    ]
}
```

And save it with the name 'AWSLambdaVPCAccessExecutionRole'.

Now that the new policy role was created select it from the list and add as a permission.

### VPC

in the lambda function page, go to 'Configuration' tab, then VPC in the left list.

Click on 'Edit' and choose a VPC, two subnets and a security group, then click on the 'save' button.

![](./assets/week-4/week-4-edit-vpc.png)

The last thing that we need to do is configure the trigger for our lambda function.
Go to the Cognito user pool on AWS.

When you are inside the 'cruddur-user-pool', go to 'User poll properties' tab, and then click on 'Add Lambda trigger' button.

![](./assets/week-4/week-4-creating-lambda-trigger-cognito-user-pool.png)

Now we need to test if the lambda function is triggered after a user is created in the cognito user pool.

Let's got to our Cruddur's frontend (port 3000) and create a new user, after the user is confirmed, you should see the user on the RDS instance. You can access thru your gitpod console with the command:

```bash
psql ./bin/db-connect prod
```

The use this sql command:

```sql
SELECT * FROM users;
```

### SQL Files

Let's create a new folder for our sql files, Named `db/sql/activities`. Inside this folder create these three files:

#### __create.sql__

```sql
INSERT INTO public.activities (
    user_uuid,
    message,
    expires_at
)
VALUES (
    (SELECT uuid from public.users WHERE users.handle = %(handle)s LIMIT 1), 
    %(message)s, 
    %(expires_at)s
) 
RETURNING uuid;
```

#### __object.sql__

```sql
SELECT 
    activities.uuid,
    users.display_name,
    users.handle,
    activities.message,
    activities.created_at,
    activities.expires_at
FROM public.activities
INNER JOIN public.users ON users.uuid = activities.user_uuid
WHERE 
    activities.uuid = %(uuid)s
```

#### __home.sql__

```sql
SELECT
    activities.uuid,
    users.display_name,
    users.handle,
    activities.message,
    activities.replies_count,
    activities.reposts_count,
    activities.likes_count,
    activities.reply_to_activity_uuid,
    activities.expires_at,
    activities.created_at
FROM public.activities
LEFT JOIN public.users ON users.uuid = activities.user_uuid
ORDER BY activities.created_at DESC
```

## Start Refactoring our backend code

In almost every place in our backend, we have mock data hardcoded, so we need to change that to successfully connect our backend with our RDS instance.

We'll start this week refactoring `services/home_activities.py` and `services/create_activity.py`.

### __home_activities.py__

Change your code to look something like this:

```py
    from datetime import datetime, timedelta, timezone
from lib.db import db

#honeycomb
from opentelemetry import trace

tracer = trace.get_tracer("home.activities")

class HomeActivities:
  def run(cognito_user_id=None):
  # def run(logger): // for cloudwathc logs
    #logger.info('Hello Cloudwatch! from  /api/activities/home')
    with tracer.start_as_current_span("http-home-activities"):
      span = trace.get_current_span()
      now = datetime.now(timezone.utc).astimezone()
      span.set_attribute("app.now", now.isoformat())
      
      #span.set_attribute("app.result_length", len(results))
      sql = db.template('activities', 'home')
      results = db.query_array_json(sql)
      return results
```

### __create_activity.py__

Your code should see something like this:

```py
from datetime import datetime, timedelta, timezone
from lib.db import db

class CreateActivity:
  def run(message, user_handle, ttl):
    model = {
      'errors': None,
      'data': None
    }

    now = datetime.now(timezone.utc).astimezone()

    if (ttl == '30-days'):
      ttl_offset = timedelta(days=30) 
    elif (ttl == '7-days'):
      ttl_offset = timedelta(days=7) 
    elif (ttl == '3-days'):
      ttl_offset = timedelta(days=3) 
    elif (ttl == '1-day'):
      ttl_offset = timedelta(days=1) 
    elif (ttl == '12-hours'):
      ttl_offset = timedelta(hours=12) 
    elif (ttl == '3-hours'):
      ttl_offset = timedelta(hours=3) 
    elif (ttl == '1-hour'):
      ttl_offset = timedelta(hours=1) 
    else:
      model['errors'] = ['ttl_blank']

    if user_handle == None or len(user_handle) < 1:
      model['errors'] = ['user_handle_blank']

    if message == None or len(message) < 1:
      model['errors'] = ['message_blank'] 
    elif len(message) > 280:
      model['errors'] = ['message_exceed_max_chars'] 

    if model['errors']:
      model['data'] = {
        'handle':  user_handle,
        'message': message
      }   
    else:
      expires_at = (now + ttl_offset)
      uuid = CreateActivity.create_activity(user_handle, message, expires_at)
      object_json = CreateActivity.query_object_activity(uuid)
      model['data'] = object_json
    return model

  def create_activity(handle, message, expires_at):
    sql = db.template('activities', 'create')
    uuid = db.query_commit(
      sql, 
      {
        'handle': handle, 
        'message': message, 
        'expires_at': expires_at
      }
    )
    return uuid
  
  def query_object_activity(uuid):
    sql = db.template('activities', 'object')
    return db.query_object_json(
      sql, 
      {
        'uuid': uuid, 
      }
    )
```

## Testing 1, 2, 3

Now that all changes are applied, `compose up` the project and test if you can create new cruds.

You should see something like this:
![](./assets/week-4/week-4-activities-insert-working.png)

And that's all for week 4. I'm going for a beer now!!!