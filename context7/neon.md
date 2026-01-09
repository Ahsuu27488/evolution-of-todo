### CheckList: Setup Guide Example

Source: https://neon.com/docs/community/component-guide

CheckList provides an interactive checklist for guides and tutorials, utilizing CheckItem components internally. This example shows a typical setup checklist with instructions for each item.

```html
<CheckList title="Setup checklist">
  <CheckItem title="Create Neon account" href="#signup">
    Sign up for a free Neon account at console.neon.tech
  </CheckItem>
  <CheckItem title="Install dependencies" href="#install">
    Install the required packages for your project
  </CheckItem>
  <CheckItem title="Configure environment" href="#config">
    Set up your database connection string
  </CheckItem>
  <CheckItem title="Test connection" href="#test">
    Verify your application can connect to Neon
  </CheckItem>
</CheckList>
```

--------------------------------

### Install and Use Neon JavaScript SDK with Neon Auth

Source: https://neon.com/docs/data-api/get-started

This snippet demonstrates how to install the `@neondatabase/neon-js` client library and initialize it for use with Neon Auth. It then shows a basic example of querying the 'posts' table to retrieve published posts, with the JWT token being automatically managed.

```bash
npm install @neondatabase/neon-js
```

```javascript
import { createClient } from '@neondatabase/neon-js';

// Initialize with Neon Auth
const client = createClient({
  auth: {
    url: process.env.NEON_AUTH_URL, // Your Neon Auth endpoint (from the Neon Console)
  },
  dataApi: {
    url: process.env.NEON_DATA_API_URL, // Your Data API endpoint (from the Neon Console)
  },
});

// Query - the JWT token is injected automatically when the user is signed in
const { data, error } = await client
  .from('posts')
  .select('*')
  .eq('is_published', true)
  .order('created_at', { ascending: false });

console.log(data);

```

--------------------------------

### AI Assistant for Neon Guided Onboarding

Source: https://neon.com/docs/changelog/2025-11-14

This example shows how to use the AI assistant with the `load_resource` tool to get guided onboarding for Neon. Users can ask for setup instructions, project configuration, connection strings, schema creation, and migrations, which are loaded directly through the assistant.

```natural_language
Get started with Neon
```

```natural_language
Help me set up my first project
```

--------------------------------

### Install Neon CLI

Source: https://neon.com/docs/reference/cli-quickstart

Installs the Neon CLI using package managers like Homebrew, npm, or bun. It also includes a command to verify the installation by checking the CLI version.

```bash
brew install neonctl
```

```bash
npm i -g neonctl
```

```bash
bun install -g neonctl
```

```bash
neon --version
```

--------------------------------

### Node.js Project Initialization and Setup

Source: https://neon.com/docs/guides/render

Commands to create a new Node.js project directory, initialize npm, enable ES6 module support, install dependencies (express, pg), and create an environment file.

```bash
mkdir neon-render-example && cd neon-render-example
npm init -y && npm pkg set type="module"
npm install express pg
touch .env
```

--------------------------------

### Example: DocsList Component File Structure

Source: https://neon.com/docs/community/component-architecture

Provides a concrete example of the file structure for the `DocsList` component, showing its main implementation file, index export, and image assets.

```text
src/components/pages/doc/docs-list/
├── docs-list.jsx                     # Main component implementation
├── index.js                          # Export: export { default } from './docs-list'
└── images/                           # Component-specific images
    ├── docs.inline.svg
    └── repo.inline.svg

```

--------------------------------

### Direct HTTP GET Request to Neon Data API

Source: https://neon.com/docs/data-api/get-started

This example demonstrates how to make a direct HTTP GET request to the Neon Data API to fetch posts. It includes the necessary Authorization header with a JWT token and specifies query parameters for filtering and ordering. Ensure your JWT token has a 'sub' claim for RLS policies to function correctly.

```curl
curl -X GET 'https://your-data-api-endpoint/rest/v1/posts?is_published=eq.true&order=created_at.desc' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json'
```

--------------------------------

### Node.js Project Setup and Dependency Installation (Shell)

Source: https://neon.com/docs/guides/heroku

Shell commands to initialize a new Node.js project, enable ES6 module support, set the start script, and install necessary packages like 'express' and 'pg'. It also creates a .env file for environment variables.

```shell
mkdir neon-heroku-example && cd neon-heroku-example
npm init -y && npm pkg set type="module" && npm pkg set scripts.start="node index.js"
npm install express pg
touch .env
```

--------------------------------

### Integrate Next.js SDK Getting Started Component

Source: https://neon.com/docs/community/component-specialized

Provides a 'Getting Started' component specifically for the Next.js SDK. This is part of auto-generated components for SDK documentation.

```javascript
<GetStarted sdkName="Next.js" />
```

--------------------------------

### Install libpq for psql

Source: https://neon.com/docs/get-started/signing-up

Installs the libpq library required for the psql client on macOS and configures the zsh shell environment to use it. This setup is necessary for connecting to databases via psql.

```bash
brew install libpq
echo 'export PATH="/opt/homebrew/opt/libpq/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

--------------------------------

### Hono.js Starter Project Configuration

Source: https://neon.com/docs/guides/drizzle-migrations

Interactive CLI prompts for setting up a new Hono.js project. This example shows the typical selections for a Node.js template and dependency installation using npm.

```bash
Need to install the following packages:
create-hono@0.9.0
Ok to proceed? (y) y

create-hono version 0.9.0
✔ Using target directory … neon-drizzle-guide
✔ Which template do you want to use? › nodejs
cloned honojs/starter#main to ./repos/javascript/neon-drizzle-guide
✔ Do you want to install project dependencies? … yes
✔ Which package manager do you want to use? › npm
```

--------------------------------

### Download and Extract Liquibase CLI

Source: https://neon.com/docs/guides/liquibase

This snippet demonstrates how to download the Liquibase CLI from the official website and extract its contents to a specified directory. It assumes you are using a Unix-like system.

```bash
cd ~/Downloads
mkdir ~/liquibase
tar -xzvf liquibase-x.yy.z.tar.gz -C ~/liquibase/
```

--------------------------------

### Start Medusa Backend Server Locally

Source: https://neon.com/docs/guides/medusajs

Command to start the Medusa backend development server after the application has been set up. Assumes the project directory has been created and dependencies installed.

```bash
cd medusa-neon-store
npm run dev
```

--------------------------------

### Installation

Source: https://neon.com/docs/ai/ai-rules-neon-python-sdk

Instructions for installing the Neon Python SDK using pip.

```APIDOC
## Installation

To install the Neon Python SDK, use pip:

```bash
pip install neon-api
```
```

--------------------------------

### Start Development Server

Source: https://neon.com/docs/data-api/demo

Starts the local development server for the Neon application using Bun. This command allows developers to test the application locally before deployment.

```bash
bun dev
```

--------------------------------

### Initialize Go Module and Install Dependencies

Source: https://neon.com/docs/guides/go

Initializes a Go module for dependency tracking and installs the necessary pgx and godotenv packages. Ensure Go 1.18 or later is installed.

```bash
mkdir neon-go-quickstart
cd neon-go-quickstart
go mod init neon-go-quickstart
go get github.com/jackc/pgx/v5 github.com/joho/godotenv
```

--------------------------------

### Authentication and Client Initialization

Source: https://neon.com/docs/ai/ai-rules-neon-python-sdk

Guide to setting up authentication with an API key and initializing the Neon API client.

```APIDOC
## Authentication and Client Initialization

All interactions with the Neon API require an API key, which should be stored securely as an environment variable (e.g., `NEON_API_KEY`).

### Initialize the API Client

It is recommended to load the API key from environment variables for security:

```python
import os
from neon_api import NeonAPI

# Best practice: Load API key from environment variables
api_key = os.getenv("NEON_API_KEY")
if not api_key:
    raise ValueError("NEON_API_KEY environment variable is not set.")

neon = NeonAPI(api_key=api_key)
```
```

--------------------------------

### Native Range Partitioning Example in PostgreSQL

Source: https://neon.com/docs/extensions/pg_partman

This SQL example illustrates native range partitioning in PostgreSQL. It demonstrates creating a table with a date-based partition key and then creating a partition for a specific date range. It also shows how to detach an old partition.

```sql
CREATE TABLE measurement (
    city_id         int not null,
    logdate         date not null,
    peaktemp        int
) PARTITION BY RANGE (logdate);

-- Create a partition for each month of logged data.
-- Records with `logdate` in this range are automatically routed to this partition table
CREATE TABLE measurement_y2006m02 PARTITION OF measurement
    FOR VALUES FROM ('2006-02-01') TO ('2006-03-01');

-- Moving older data to a different table.
-- Queries against the main table will not include the data in the detached partition
ALTER TABLE measurement DETACH PARTITION measurement_y2005m10;
```

--------------------------------

### Add Liquibase to PATH Environment Variable

Source: https://neon.com/docs/guides/liquibase

This code snippet shows how to add the Liquibase installation directory to your system's PATH environment variable. This allows you to run Liquibase commands from any terminal location. It provides examples for bash and zsh shells.

```bash
echo 'export PATH=$PATH:/path/to/liquibase' >> ~/.bashrc
source ~/.bashrc
```

--------------------------------

### Initialize Next.js Project and Install Dependencies

Source: https://neon.com/docs/guides/auth-clerk

Commands to create a new Next.js project with TypeScript, ESLint, Tailwind CSS, and npm, followed by the installation of necessary Neon, Drizzle ORM, and Clerk packages. This setup facilitates database interaction and user authentication.

```bash
npx create-next-app guide-neon-next-clerk --typescript --eslint --tailwind --use-npm --no-src-dir --app --import-alias "@/*"

npm install @neondatabase/serverless drizzle-orm
npm install -D drizzle-kit dotenv
npm install @clerk/nextjs
```

--------------------------------

### Authenticate Neon CLI with API key

Source: https://neon.com/docs/reference/cli-install

Example of authenticating a Neon CLI command using an explicit API key. Replace '<neon_api_key>' with your actual key.

```bash
neon projects list --api-key <neon_api_key>
```

--------------------------------

### SQL Prepared Statement Example

Source: https://neon.com/docs/connect/connection-pooling

This SQL snippet demonstrates the basic syntax for preparing and executing a statement in PostgreSQL. It defines a query structure once and then executes it with a parameter. Note that this SQL-level approach is not directly supported by PgBouncer.

```sql
PREPARE fetch_plan (TEXT) AS
SELECT * FROM users WHERE username = $1;

EXECUTE fetch_plan('alice');
```

--------------------------------

### Install Neon Auth Packages

Source: https://neon.com/docs/ai/ai-rules-neon-auth

Installs the necessary Neon Auth packages. Choose between `@neondatabase/auth` for authentication only or `@neondatabase/neon-js` for both authentication and the Data API.

```bash
# Auth only
npm install @neondatabase/auth

# Auth + Data API
npm install @neondatabase/neon-js
```

--------------------------------

### Complete Neon Project Lifecycle Example

Source: https://neon.com/docs/ai/ai-rules-neon-toolkit

Demonstrates the full lifecycle of managing a Neon project, including creation, SQL operations, and deletion, using a `try...finally` block to ensure cleanup. This example requires the NEON_API_KEY environment variable.

```typescript
import { NeonToolkit } from '@neondatabase/toolkit';

async function runTemporaryDatabaseTask() {
  const apiKey = process.env.NEON_API_KEY;
  if (!apiKey) {
    throw new Error('NEON_API_KEY is not set.');
  }
  const toolkit = new NeonToolkit(apiKey);

  let project;
  try {
    // 1. Create
    console.log('Creating temporary project...');
    project = await toolkit.createProject({ name: 'ephemeral-task-runner' });
    console.log(`Project created with ID: ${project.project.id}`);

    // 2. Query
    console.log('Setting up schema and inserting data...');
    await toolkit.sql(
      project,
      `CREATE TABLE logs (message TEXT, timestamp TIMESTAMPTZ DEFAULT NOW());`
    );
    await toolkit.sql(project, `INSERT INTO logs (message) VALUES ('Task started');`);

    const logs = await toolkit.sql(project, `SELECT message FROM logs;`);
    console.log('Retrieved logs:', logs);
  } catch (error) {
    console.error('An error occurred during the database task:', error);
  } finally {
    // 3. Delete
    if (project) {
      console.log('Cleaning up and deleting project...');
      await toolkit.deleteProject(project);
      console.log('Project deleted.');
    }
  }
}

runTemporaryDatabaseTask();
```

--------------------------------

### Run Queries with pgcli

Source: https://neon.com/docs/connect/connect-pgcli

Shows examples of running SQL queries within the pgcli client after establishing a connection. Includes creating a table, selecting data, and demonstrates the autocompletion feature.

```sql
CREATE TABLE my_table AS SELECT now();
SELECT * FROM my_table;
```

--------------------------------

### View Flyway Schema Migration History

Source: https://neon.com/docs/guides/flyway

The `flyway info` command displays the current status of the database schema, including the version, description, state, and installation date of each applied migration. It also shows the `flyway_schema_history` table details.

```bash
flyway info
```

--------------------------------

### Example Database Changelog XML

Source: https://neon.com/docs/guides/liquibase

This is an example of a database changelog file generated by Liquibase. It uses XML format to describe database schema elements, including table creation, column definitions, and foreign key constraints. This file serves as a record of the database structure.

```xml
<?xml version="1.1" encoding="UTF-8" standalone="no"?>
<databaseChangeLog xmlns="http://www.liquibase.org/xml/ns/dbchangelog" xmlns:ext="http://www.liquibase.org/xml/ns/dbchangelog-ext" xmlns:pro="http://www.liquibase.org/xml/ns/pro" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog-ext http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-ext.xsd http://www.liquibase.org/xml/ns/pro http://www.liquibase.org/xml/ns/pro/liquibase-pro-latest.xsd http://www.liquibase.org/xml/ns/dbchangelog http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-latest.xsd">
    <changeSet author="alex (generated)" id="1697969580160-1">
        <createTable tableName="authors">
            <column autoIncrement="true" name="author_id" type="INTEGER">
                <constraints nullable="false" primaryKey="true" primaryKeyName="authors_pkey"/>
            </column>
            <column name="first_name" type="VARCHAR(100)"/>
            <column name="last_name" type="VARCHAR(100)"/>
            <column name="email" type="VARCHAR(255)">
                <constraints nullable="false"/>
            </column>
            <column name="bio" type="TEXT"/>
        </createTable>
    </changeSet>
    <changeSet author="alex (generated)" id="1697969580160-2">
        <createTable tableName="posts">
            <column autoIncrement="true" name="post_id" type="INTEGER">
                <constraints nullable="false" primaryKey="true" primaryKeyName="posts_pkey"/>
            </column>
            <column name="author_id" type="INTEGER"/>
            <column name="title" type="VARCHAR(255)">
                <constraints nullable="false"/>
            </column>
            <column name="content" type="TEXT"/>
            <column defaultValueComputed="CURRENT_TIMESTAMP" name="published_date" type="TIMESTAMP WITHOUT TIME ZONE"/>
        </createTable>
    </changeSet>
    <changeSet author="alex (generated)" id="1697969580160-3">
        <addUniqueConstraint columnNames="email" constraintName="authors_email_key" tableName="authors"/>
    </changeSet>
    <changeSet author="alex (generated)" id="1697969580160-4">
        <addForeignKeyConstraint baseColumnNames="author_id" baseTableName="posts" constraintName="posts_author_id_fkey" deferrable="false" initiallyDeferred="false" onDelete="NO ACTION" onUpdate="NO ACTION" referencedColumnNames="author_id" referencedTableName="authors" validate="true"/>
    </changeSet>
</databaseChangeLog>
```

--------------------------------

### InfoBlock: Basic Two-Column Layout Example

Source: https://neon.com/docs/community/component-guide

InfoBlock creates a multi-column layout, ideal for organizing content sections like introductions or summaries. This example demonstrates a basic two-column layout using InfoBlock with DocsList components to present learning objectives and related topics.

```html
<InfoBlock>
<DocsList title="What you will learn:">
<p>How to view and modify data in the console</p>
<p>Create an isolated database copy per developer</p>
<p>Reset your branch to production when ready to start new work</p>
</DocsList>

<DocsList title="Related topics" theme="docs">
<a href="/docs/introduction/branching">About branching</a>
<a href="/docs/get-started/workflow-primer">Branching workflows</a>
<a href="/docs/get-started/connect-neon">Connect Neon to your stack</a>
</DocsList>
</InfoBlock>
```

--------------------------------

### Node.js Example: Executing Queries with Neon Driver

Source: https://neon.com/docs/serverless/serverless-driver

A practical example for Node.js demonstrating how to initialize the Neon driver and execute a simple SQL query to fetch posts. It shows both template literal and `query()` method usage for fetching data.

```javascript
import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL);
const posts = await sql`SELECT * FROM posts WHERE id = ${postId}`;
// or using query() for parameterized queries
const posts = await sql.query('SELECT * FROM posts WHERE id = $1', [postId]);
// `posts` is now [{ id: 12, title: 'My post', ... }] (or undefined)
```

--------------------------------

### Example: Observing Table Statistics and Bloat

Source: https://neon.com/docs/extensions/pgstattuple

This example demonstrates creating a 'customers' table, inserting a large number of rows, deleting half of them to generate dead tuples (bloat), and then using pgstattuple() to observe the statistics. It includes the SQL commands for table creation, data insertion, deletion, and checking statistics.

```sql
-- Create the customers table
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    zip_code VARCHAR(20),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- Insert 10,000 rows into the customers table
INSERT INTO customers (first_name, last_name, email, phone, address, city, state, zip_code, created_at)
SELECT
    CASE (i % 10) WHEN 0 THEN 'John' WHEN 1 THEN 'Jane' WHEN 2 THEN 'Peter' WHEN 3 THEN 'Mary' WHEN 4 THEN 'Robert' WHEN 5 THEN 'Patricia' WHEN 6 THEN 'Michael' WHEN 7 THEN 'Linda' WHEN 8 THEN 'William' ELSE 'Elizabeth' END || '_' || i::TEXT,
    CASE (i % 10) WHEN 0 THEN 'Smith' WHEN 1 THEN 'Johnson' WHEN 2 THEN 'Williams' WHEN 3 THEN 'Jones' WHEN 4 THEN 'Brown' WHEN 5 THEN 'Davis' WHEN 6 THEN 'Miller' WHEN 7 THEN 'Wilson' WHEN 8 THEN 'Moore' ELSE 'Taylor' END || '_' || i::TEXT,
    'customer' || i::TEXT || '@example.com',
    '555-' || LPAD((i % 10000)::TEXT, 4, '0'),
    (i * 10)::TEXT || ' Main St',
    CASE (i % 5) WHEN 0 THEN 'New York' WHEN 1 THEN 'Los Angeles' WHEN 2 THEN 'Chicago' WHEN 3 THEN 'Houston' ELSE 'Phoenix' END,
    CASE (i % 5) WHEN 0 THEN 'NY' WHEN 1 THEN 'CA' WHEN 2 THEN 'IL' WHEN 3 THEN 'TX' ELSE 'AZ' END,
    LPAD((i % 99999)::TEXT, 5, '0'),
    NOW() - (random() * INTERVAL '365 days')
FROM generate_series(1, 10000) AS s(i);

 -- Delete half of the rows to create dead tuples
DELETE FROM customers WHERE customer_id % 2 = 0;

-- Check the table statistics before vacuuming
SELECT * FROM pgstattuple('customers');

```

--------------------------------

### Integrate AI Workflows with Neon MCP Server (Cursor Example)

Source: https://neon.com/docs/changelog/2025-04-04

This snippet demonstrates how to connect to the Neon MCP Server from the Cursor IDE. It requires npx to be installed and uses a remote URL for the server. This setup allows for AI workflow integration without local API keys or complex setup.

```json
{
  "Neon": {
    "command": "npx",
    "args": ["-y", "mcp-remote@latest", "https://mcp.neon.tech/sse"]
  }
}
```

--------------------------------

### Initialize Node.js Project and Install Dependencies

Source: https://neon.com/docs/guides/prisma-migrations

Commands to create a new Node.js project, set up basic configurations, and install necessary dependencies like Express, Prisma client, and Prisma CLI.

```Shell
mkdir neon-prisma-guide && cd neon-prisma-guide
npm init -y && touch .env index.js
npm pkg set type="module" && npm pkg set scripts.start="node index.js"
npm install express
npm install @prisma/client && npm install prisma --save-dev
npx prisma init
```

--------------------------------

### PostgreSQL Table and Data Setup for JSON Examples

Source: https://neon.com/docs/functions/json_object

This SQL code provides the necessary commands to create a sample `book_inventory` table and populate it with data. This setup is essential for running the `json_object` function examples provided in the documentation.

```sql
-- Test database table for a bookstore inventory
CREATE TABLE book_inventory (
    book_id INT,
    title TEXT,
    author TEXT,
    price NUMERIC,
    genre TEXT
);

-- Inserting some test data into `book_inventory`
INSERT INTO book_inventory VALUES
(101, 'The Great Gatsby', 'F. Scott Fitzgerald', 18.99, 'Classic'),
(102, 'Invisible Man', 'Ralph Ellison', 15.99, 'Novel');
```

--------------------------------

### Generate Database Changelog with Liquibase

Source: https://neon.com/docs/guides/liquibase

This command generates a changelog file that captures the current state of your database schema. It requires the Liquibase command-line tool to be installed and accessible. The output is an XML file detailing database objects like tables, columns, and constraints.

```bash
liquibase --changeLogFile=mydatabase_changelog.xml generateChangeLog
```

--------------------------------

### Gitignore and Initial Commit Setup

Source: https://neon.com/docs/guides/render

This command sequence initializes a Git repository, creates a .gitignore file to exclude 'node_modules' and '.env' from version control, adds a README.md file, stages all current files, and makes the initial commit. It then sets the main branch name and adds a remote origin before pushing the changes to GitHub.

```bash
echo "node_modules/" > .gitignore && echo ".env" >> .gitignore
echo "# neon-render-example" >> README.md
git init && git add . && git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

--------------------------------

### Example of Recovering a Neon Project

Source: https://neon.com/docs/manage/projects

This example demonstrates the command to recover a project with a specific ID and shows the expected output format, including the project's ID, Name, Region Id, and Created At timestamp. This helps verify the recovery operation.

```bash
neon projects recover crimson-voice-12345678
┌────────────────────────┬───────────┬───────────────┬──────────────────────┐
│ Id                     │ Name      │ Region Id     │ Created At           │
├────────────────────────┼───────────┼───────────────┼──────────────────────┤
│ crimson-voice-12345678 │ myproject │ aws-us-east-2 │ 2024-04-15T11:17:30Z │
└────────────────────────┴───────────┴───────────────┴──────────────────────┘
```

--------------------------------

### Install Neon Python SDK

Source: https://neon.com/docs/ai/ai-rules-neon-python-sdk

Installs the Neon API client library using pip. This is the first step to programmatically interact with Neon resources.

```bash
pip install neon-api

```

--------------------------------

### NeedHelp: Support Widget Example

Source: https://neon.com/docs/community/component-guide

NeedHelp is a component that provides easy access to support resources. This example shows the basic usage of the NeedHelp component, which typically links to community and paid support channels.

```html
<NeedHelp />
```

--------------------------------

### Node.js project setup with Express and pg

Source: https://neon.com/docs/guides/railway

Commands to create a new Node.js project directory, initialize npm, enable ES6 module support, install Express and the pg library, and create a .env file. This sets up the basic structure for a web application that connects to a PostgreSQL database.

```bash
mkdir neon-railway-example && cd neon-railway-example
npm init -y && npm pkg set type="module"
npm install express pg
touch .env
```

--------------------------------

### Example: Neon CLI init command execution

Source: https://neon.com/docs/reference/cli-init

Demonstrates the execution of the `npx neonctl@latest init` command, showing the interactive prompts for editor selection, the authentication process, and successful completion messages. This output illustrates the steps involved in setting up Neon with an AI assistant.

```bash
cd /path/to/your/app
npx neonctl@latest init

npx neonctl@latest init

┌  Adding Neon to your project
│
◆  Which editor(s) would you like to configure? (Space to toggle each option, Enter to confirm your selection)
│  ◼ Cursor
│  ◼ VS Code
│  ◻ Claude CLI
│
◒  Authenticating
┌────────┬──────────────────┬────────┬────────────────┐
│ Login  │ Email            │ Name   │ Projects Limit │
├────────┼──────────────────┼────────┼────────────────┤
│ alex   │ alex@domain.com  │ Alex   │ 60             │
└────────┴──────────────────┴────────┴────────────────┘
◇  Authentication successful ✓
│
◇  Installed Neon MCP server
│
◇  Success! Neon is now ready to use with Cursor / VS Code.
│
│
◇  What's next? ─────────────────────────────────────────────────────────────╮
│                                                                            │
│  Restart Cursor / VS Code and type in "Get started with Neon" in the chat  │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────╯
```

--------------------------------

### Prisma Migrate Configuration (Before SQL DB/Role Management)

Source: https://neon.com/docs/changelog/2023-07-13

This example shows the previous configuration required for Prisma Migrate users in Neon, where a shadow database needed manual setup and its connection URL specified in the schema.prisma file. This was necessary because Neon did not support database creation via SQL.

```typescript
datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
  directUrl = env("DIRECT_DATABASE_URL")
  shadowDatabaseUrl = env("SHADOW_DATABASE_URL")
}
```

--------------------------------

### Run Flyway Database Migration

Source: https://neon.com/docs/guides/flyway

This command initiates the database migration process using Flyway. It will apply any pending SQL migration scripts to the configured database.

```bash
flyway migrate
```

--------------------------------

### Schedule a Job in a Different Database (Conceptual Example)

Source: https://neon.com/docs/extensions/pg_cron

Illustrates how to use `cron.schedule_in_database()` to schedule a job in a specific database, even if pg_cron is installed elsewhere. Note: This function is currently not supported in Neon. The example shows the syntax for job name, cron schedule, target database, and the SQL command to execute.

```sql
SELECT cron.schedule_in_database(
    'my_job',                     -- Job name
    '0 * * * *',                  -- Cron schedule (every hour)
    'my_database',                 -- Target database
    'VACUUM ANALYZE my_table'      -- SQL command to run
);
```

--------------------------------

### Clone and Install Project Dependencies

Source: https://neon.com/docs/data-api/demo

Clones the Neon Data API and Neon Auth demo application repository and installs its dependencies using Bun. This is a standard step for setting up the project locally.

```bash
git clone https://github.com/neondatabase-labs/neon-data-api-neon-auth.git
cd neon-data-api-neon-auth
bun install
```

--------------------------------

### Load Neon Documentation

Source: https://neon.com/docs/ai/neon-mcp-server

Loads comprehensive Neon documentation and usage guidelines, including the 'neon-get-started' guide for setup, configuration, and best practices.

```tool_code
load_resource
```

--------------------------------

### Clone WunderGraph Repository and Install Dependencies

Source: https://neon.com/docs/guides/wundergraph

This snippet shows the commands to clone the WunderGraph project repository from GitHub and install the necessary project dependencies using npm. It also starts the local development server.

```bash
git clone https://github.com/<user>/wundergraph.git
cd wundergraph
code .

npm install && npm run dev
```

--------------------------------

### Install pg_cron Extension

Source: https://neon.com/docs/extensions/pg_cron

SQL command to install the pg_cron extension within your Neon database after enabling it in the compute settings.

```APIDOC
## SQL Command

### Description
Installs the `pg_cron` extension in your Neon database using a SQL command. This should be executed after the extension has been enabled via the API and the compute has been restarted.

### SQL Statement
```sql
CREATE EXTENSION IF NOT EXISTS pg_cron;
```

### Usage
Execute this command in your Neon SQL Editor or using a client like `psql` connected to your Neon database.
```

--------------------------------

### Create Table and Insert Data (SQL)

Source: https://neon.com/docs/guides/branching-test-queries

This SQL code defines a 'Post' table and populates it with sample data. This setup is used in the examples for testing queries on a Neon branch.

```sql
CREATE TABLE Post (
    id INT PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    author_name VARCHAR(100),
    date_published DATE
);

INSERT INTO Post (id, title, content, author_name, date_published)
VALUES
(1, 'My first post', 'This is the content of the first post.', 'Alice', '2023-01-01'),
(2, 'My second post', 'This is the content of the second post.', 'Alice', '2023-02-01'),
(3, 'Old post by Bob', 'This is an old post by Bob.', 'Bob', '2020-01-01'),
(4, 'Recent post by Bob', 'This is a recent post by Bob.', 'Bob', '2023-06-01'),
(5, 'Another old post', 'This is another old post.', 'Alice', '2019-06-01');
```

--------------------------------

### Create Sales Table and Insert Data (SQL)

Source: https://neon.com/docs/guides/read-replica-data-analysis

This SQL snippet demonstrates how to create a 'sales' table with relevant columns and insert sample data. This setup is used in the example scenario to illustrate running analytics queries on a read replica.

```sql
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    sale_amount DECIMAL(10,2) NOT NULL,
    sale_date DATE NOT NULL
);

INSERT INTO sales (product_id, sale_amount, sale_date) VALUES
(1, 20.50, '2022-07-24'),
(2, 35.99, '2022-08-24'),
(1, 20.50, '2022-09-24'),
(3, 15.00, '2023-01-24'),
(1, 20.50, '2023-04-24');
```

--------------------------------

### Setting up Python Virtual Environment and Installing Dependencies

Source: https://neon.com/docs/guides/sqlalchemy-migrations

Commands to create and activate a Python virtual environment, install necessary packages like SQLAlchemy, Alembic, psycopg2-binary, FastAPI, and uvicorn, and then freeze the dependencies into a requirements.txt file.

```bash
python -m venv myenv

# On macOS and Linux
source myenv/bin/activate

# On Windows
myenv\Scripts\activate

mkdir guide-neon-sqlalchemy && cd guide-neon-sqlalchemy
pip install sqlalchemy alembic "psycopg2-binary"
pip install fastapi uvicorn python-dotenv
pip freeze > requirements.txt
```

--------------------------------

### Get Default Connection String (Neon CLI)

Source: https://neon.com/docs/reference/cli-quickstart

Retrieves the connection string for the default branch of your Neon project. This is a simple command-line operation requiring no arguments.

```bash
neon connection-string
```

--------------------------------

### Create Sveltekit project and add dependencies

Source: https://neon.com/docs/guides/sveltekit

Commands to create a new Sveltekit project with TypeScript and install the Neon serverless driver and dotenv for environment variable management. This is the initial setup for the Sveltekit application.

```bash
npx sv create my-app --template minimal --no-add-ons --types ts
cd my-app
npm install @neondatabase/serverless dotenv
```

--------------------------------

### Environment Variables for Neon Authentication

Source: https://neon.com/docs/ai/ai-rules-neon-auth

Configuration for Neon authentication using environment variables. Examples are provided for Next.js (.env.local) and Vite/React (.env) projects.

```bash
# Next.js (.env.local)
NEON_AUTH_BASE_URL=https://ep-xxx.neonauth.c-2.us-east-2.aws.neon.build/dbname/auth
NEXT_PUBLIC_NEON_AUTH_URL=https://ep-xxx.neonauth.c-2.us-east-2.aws.neon.build/dbname/auth

# Vite/React (.env)
VITE_NEON_AUTH_URL=https://ep-xxx.neonauth.c-2.us-east-2.aws.neon.build/dbname/auth
```

--------------------------------

### Install pgloader Utility

Source: https://neon.com/docs/import/migrate-sqlite

Instructions for installing the pgloader utility on macOS, Debian/Ubuntu, and via Docker. Ensure pgloader is installed before proceeding with migrations.

```bash
brew install pgloader
```

```bash
sudo apt-get install pgloader
```

```bash
docker pull dimitri/pgloader:latest
```

--------------------------------

### Example Direct Connection String

Source: https://neon.com/docs/connect/choose-connection

An example of a direct connection string for Neon. This string connects directly to the Neon database instance without pooling.

```sql
postgres://alex:AbC123dEf@ep-cool-darkness-123456.us-east-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require

```

--------------------------------

### Neon Database Connection String Example

Source: https://neon.com/docs/connect/connect-postgres-gui

This example demonstrates a typical connection string format for connecting to a Neon database. It highlights the placeholders for role, hostname, and database name, which are essential for establishing a connection.

```sql
postgresql://alex:AbC123dEf@ep-cool-darkness-123456.us-east-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require
```

--------------------------------

### Install Latest Neon CLI with npm

Source: https://neon.com/docs/changelog/2024-12-20

Example of installing the latest Neon CLI version using npm in a GitHub Actions workflow. It pins the installation to '@latest' for CI/CD stability.

```yaml
- name: Install Neon CLI
  run: npm install -g neonctl@latest
```

--------------------------------

### Add Flyway to PATH Environment Variable (Bash/Zsh)

Source: https://neon.com/docs/guides/flyway

These commands add the Flyway installation directory to your system's PATH environment variable, allowing you to run Flyway commands from any location. It uses `echo` to append the export command to `.bashrc` and then `source` to apply the changes immediately.

```bash
echo 'export PATH=$PATH:~/flyway-x.y.z' >> ~/.bashrc
source ~/.bashrc
```

```zsh
echo 'export PATH=$PATH:~/flyway-x.y.z' >> ~/.zshrc
source ~/.zshrc
```

--------------------------------

### Set Up TypeScript Project with Prisma Starter (CLI)

Source: https://neon.com/docs/guides/logical-replication-prisma-pulse

This command initializes a new TypeScript project with a starter configuration for Prisma. It's a prerequisite for integrating Prisma Pulse.

```bash
npx try-prisma -t typescript/starter
```

--------------------------------

### Create Exograph Project and Navigate

Source: https://neon.com/docs/guides/exograph

Initiates a new Exograph project and changes the current directory to the project folder. Assumes Exograph CLI is installed.

```bash
exo new todo
cd todo
```

--------------------------------

### Create Auth Page with AuthView (Next.js App Router)

Source: https://neon.com/docs/ai/ai-rules-neon-auth

Implement dynamic authentication pages using the AuthView component in a Next.js App Router setup. This example shows how to generate static parameters for different auth paths and render the AuthView component.

```tsx
import { AuthView } from "@neondatabase/auth/react/ui";
import { authViewPaths } from "@neondatabase/auth/react/ui/server";

export function generateStaticParams() {
  return Object.values(authViewPaths).map((path) => ({ path }));
}

export default async function AuthPage({
  params,
}: { 
  params: Promise<{ path: string }>;
}) {
  const { path } = await params;
  return <AuthView pathname={path} />;
}
```

--------------------------------

### Download Sample Data SQL File using Wget

Source: https://neon.com/docs/import/import-sample-data

This command uses `wget` to download a SQL script file containing sample data from a specified URL. Ensure `wget` is installed on your system.

```bash
wget https://raw.githubusercontent.com/neondatabase/postgres-sample-dbs/main/periodic_table.sql
```

--------------------------------

### Start Express Application

Source: https://neon.com/docs/guides/prisma-migrations

Starts the Express.js server. This command assumes that the `start` script is configured in the project's `package.json` to run the main application file (e.g., `index.ts`).

```bash
npm run start
```

--------------------------------

### SolidStart API Route with Neon Connection

Source: https://neon.com/docs/guides/solid-start

Provides an example of connecting to a Neon database from a SolidStart API route. This snippet shows how to handle a GET request, query the database for the PostgreSQL version, and return the result as JSON.

```typescript
// File: routes/api/test.ts

import { neon } from '@neondatabase/serverless';

export async function GET() {
  const sql = neon(import.meta.env.DATABASE_URL);
  const response = await sql`SELECT version()`;
  return new Response(JSON.stringify(response[0]), {
    headers: { 'Content-Type': 'application/json' },
  });
}
```

--------------------------------

### Install Neon CLI using bun

Source: https://neon.com/docs/reference/cli-install

This command installs the Neon CLI globally using bun.

```bash
bun install -g neonctl
```

--------------------------------

### Connecting to Neon via Command-Line

Source: https://neon.com/docs/connect/connect-from-any-app

Provides an example of how to connect to a Neon database directly from the command-line using the psql client and a full connection string. This is useful for testing and quick access.

```bash
psql postgresql://alex:AbC123dEf@ep-cool-darkness-a1b2c3d4-pooler.us-east-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require
```

--------------------------------

### CTA: Call to Action Button Example

Source: https://neon.com/docs/community/component-guide

CTA is a prominent button component designed to encourage user action. This example shows a typical call-to-action for signing up for a service, including a title, description, button text, and URL.

```html
<CTA
  title="Try Neon free"
  description="Start building with serverless Postgres today. No credit card required."
  buttonText="Sign Up"
  buttonUrl="https://console.neon.tech/signup"
/>
```

--------------------------------

### Initialize Node.js Project and Install Dependencies

Source: https://neon.com/docs/guides/node

Initializes a new Node.js project and installs necessary dependencies for connecting to Neon, including the Neon serverless driver and dotenv for environment variable management.

```bash
mkdir neon-nodejs-example
cd neon-nodejs-example
npm init -y
npm install @neondatabase/serverless dotenv
```

--------------------------------

### Get Specific Branch Connection String (Neon CLI)

Source: https://neon.com/docs/reference/cli-quickstart

Retrieves the connection string for a specified branch within your Neon project. You need to provide the branch name as an argument to the command.

```bash
neon connection-string <branch-name>
```

--------------------------------

### Customization Examples

Source: https://neon.com/docs/auth/reference/ui-components

Examples demonstrating how to customize text labels (localization) and add custom fields for sign-up and account settings.

```APIDOC
## Customization Examples

### Description
Customize the appearance and behavior of Neon Auth UI components through localization and additional fields.

### Method
Component Setup (React)

### Endpoint
N/A (Client-side component)

### Parameters
#### Props
- **authClient** (`NeonAuthPublicApi`) - Required - Your Neon Auth client instance.
- **localization** (`AuthLocalization`) - Optional - Object to override default text labels.
- **additionalFields** (`AdditionalFields`) - Optional - Object defining custom fields for sign-up and account settings.
- **signUp.fields** (`string[]`) - Optional - Array specifying which fields to include in the sign-up form.

### Request Example
**Custom localization:**
```jsx
<NeonAuthUIProvider
  authClient={authClient}
  localization={{
    SIGN_IN: 'Welcome Back',
    SIGN_UP: 'Create Account',
    FORGOT_PASSWORD: 'Forgot Password?',
  }}
>
  {/* App content */}
</NeonAuthUIProvider>
```

**Custom sign-up fields:**
```jsx
<NeonAuthUIProvider
  authClient={authClient}
  additionalFields={{
    company: {
      label: 'Company',
      placeholder: 'Your company name',
      type: 'string',
      required: false,
    },
  }}
  signUp={{
    fields: ['name', 'company'], // Include 'name' and the custom 'company' field
  }}
>
  {/* App content */}
</NeonAuthUIProvider>
```

### Response
(This is a React component setup, not an API response)

### Success Response
(N/A)

### Response Example
(N/A)
```

--------------------------------

### Create Bun Project and Add Dependencies

Source: https://neon.com/docs/guides/bun

This snippet shows the commands to create a new Bun project and initialize it. It also highlights that no additional dependencies are needed if using Bun's built-in SQL client, but implies dependencies would be added for the Neon serverless driver.

```bash
mkdir bun-neon-example
cd bun-neon-example
bun init -y
```

--------------------------------

### Configure Neon Project Compute and Scaling using cURL

Source: https://neon.com/docs/guides/embedded-postgres

This example shows how to set compute size limits (minimum and maximum CU) and the inactivity period before a compute suspends when creating a project. It allows for autoscaling and scale-to-zero configurations.

```shell
curl --request POST \
     --url https://console.neon.tech/api/v2/projects \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $NEON_API_KEY" \
     --header 'Content-Type: application/json' \
     --data '{
  "project": {
    "default_endpoint_settings": {
      "autoscaling_limit_min_cu": 1,
      "autoscaling_limit_max_cu": 4,
      "suspend_timeout_seconds": 600
    },
    "pg_version": 16
  }
}'
```

--------------------------------

### Create Free Tier Project using Neon API

Source: https://neon.com/docs/guides/ai-agent-integration

This example demonstrates how to create a new project for a free-tier user using the Neon API. It specifies resource quotas for active time, storage, and data transfer, along with compute autoscaling limits and suspend timeout. Ensure you have a valid $FREE_ORG_API_KEY set in your environment.

```bash
curl --request POST \
     --url https://console.neon.tech/api/v2/projects \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $FREE_ORG_API_KEY" \
     --header 'Content-Type: application/json' \
     --data '{ \
  "project": { \
    "name": "user-free-database", \
    "pg_version": 16, \
    "settings": { \
      "quota": { \
        "active_time_seconds": 360000, \
        "logical_size_bytes": 536870912, \
        "data_transfer_bytes": 5368709120 \
      } \
    }, \
    "default_endpoint_settings": { \
      "autoscaling_limit_min_cu": 0.25, \
      "autoscaling_limit_max_cu": 2, \
      "suspend_timeout_seconds": 300 \
    } \
  } \
}'
```

--------------------------------

### Install psql on Mac (Intel x64)

Source: https://neon.com/docs/connect/query-with-psql-editor

Installs the libpq library and configures the PATH environment variable for psql on macOS with Intel processors.

```shell
brew install libpq
export PATH="/usr/local/opt/libpq/bin:$PATH"
source ~/.zshrc
```

--------------------------------

### Get help for specific Postgres commands in Neon SQL Editor

Source: https://neon.com/docs/changelog/2024-04-19

Demonstrates how to get help for specific PostgreSQL commands using `\h [NAME]` in the Neon SQL Editor. For example, `\h SELECT` provides detailed information about the `SELECT` statement.

```sql
-- Get help for the SELECT command
\h SELECT
```

--------------------------------

### Vite Project Setup Configuration

Source: https://neon.com/docs/guides/cloudflare-pages

Example configuration settings for creating a new Vite project for a Cloudflare Pages application. Specifies React framework and JavaScript variant.

```text
✔ Project name: … my-neon-page
✔ Select a framework: › React
✔ Select a variant: › JavaScript

Scaffolding project in /Users/ishananand/repos/javascript/my-neon-page...

Done. Now run:

  cd my-neon-page
  npm install
  npm run dev

```

--------------------------------

### Initialize Git Repository and Push to GitHub

Source: https://neon.com/docs/guides/railway

These commands set up a local Git repository, ignore node_modules and .env files, create a README, initialize git, add all files, make the initial commit, set the main branch, and link to a remote GitHub repository before pushing.

```bash
echo "node_modules/" > .gitignore && echo ".env" >> .gitignore
echo "# neon-railway-example" >> README.md
git init && git add . && git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main

```

--------------------------------

### Create and Run Neon Server with Deno

Source: https://neon.com/docs/guides/deno

This script initializes a 'books' table in a Neon database, populates it with data if empty, and starts a Deno server. The server handles GET requests to the '/books' endpoint, returning the book data as JSON. It relies on the 'DATABASE_URL' environment variable for database connection.

```typescript
// server.ts

import { neon } from '@neon/serverless';

const databaseUrl = Deno.env.get('DATABASE_URL')!;
const sql = neon(databaseUrl);

// Create the books table and insert initial data if it doesn't exist
await sql`
  CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL
  )
`;

// Check if the table is empty
const { count } = await sql`SELECT COUNT(*)::INT as count FROM books`.then((rows) => rows[0]);

if (count === 0) {
  // The table is empty, insert the book records
  await sql`
    INSERT INTO books (title, author) VALUES
      ('The Hobbit', 'J. R. R. Tolkien'),
      ('Harry Potter and the Philosopher\'s Stone', 'J. K. Rowling'),
      ('The Little Prince', 'Antoine de Saint-Exupéry')
  `;
}

// Start the server
Deno.serve(async (req) => {
  const url = new URL(req.url);
  if (url.pathname !== '/books') {
    return new Response('Not Found', { status: 404 });
  }

  try {
    switch (req.method) {
      case 'GET': {
        const books = await sql`SELECT * FROM books`;
        return new Response(JSON.stringify(books, null, 2), {
          headers: { 'content-type': 'application/json' },
        });
      }
      default:
        return new Response('Method Not Allowed', { status: 405 });
    }
  } catch (err) {
    console.error(err);
    return new Response(`Internal Server Error\n\n${err.message}`, {
      status: 500,
    });
  }
});

```

--------------------------------

### Full Neon Project Lifecycle Management Example

Source: https://neon.com/docs/reference/neondatabase-toolkit

Demonstrates the complete lifecycle of a Neon project: creation, schema and data query execution, and project deletion. Requires the NEON_API_KEY environment variable.

```javascript
import { NeonToolkit } from '@neondatabase/toolkit';

async function main() {
  if (!process.env.NEON_API_KEY) {
    throw new Error('NEON_API_KEY environment variable is not set.');
  }

  const toolkit = new NeonToolkit(process.env.NEON_API_KEY);

  console.log('Creating a new Neon project...');
  const project = await toolkit.createProject({ name: 'toolkit-demo' });
  console.log(`Project "${project.project.name}" created successfully.`);

  console.log("Creating 'users' table...");
  await toolkit.sql(
    project,
    `
      CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        createdAt TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      );
    `
  );

  console.log('Inserting a new user...');
  await toolkit.sql(
    project,
    `INSERT INTO users (id, name) VALUES (gen_random_uuid(), 'Sam Smith')`
  );

  console.log('Querying users...');
  const users = await toolkit.sql(project, `SELECT name, createdAt FROM users`);

  console.log('Found users:', users);

  console.log('Deleting the project...');
  await toolkit.deleteProject(project);
  console.log('Project deleted. Demo complete.');
}

main().catch(console.error);
```

--------------------------------

### Common Neon CLI Operations

Source: https://neon.com/docs/reference/cli-quickstart

Demonstrates common operations using the Neon CLI, including listing all projects within an organization or personal account, and creating a new branch for a specified project. It highlights the importance of setting context or using flags for project and organization IDs.

```bash
neon projects list
```

```bash
neon branches create --name <branch-name>
```

--------------------------------

### psql Connection String Example

Source: https://neon.com/docs/get-started/connect-neon

Demonstrates the format of a PostgreSQL connection string for use with the psql command-line tool. It includes placeholders for username, password, hostname, and database name, along with required SSL parameters.

```sql
# psql example connection string
psql postgresql://username:password@hostname:5432/database?sslmode=require&channel_binding=require
```

--------------------------------

### Initialize Neon with AI Onboarding (npx)

Source: https://neon.com/docs/changelog/2025-11-28

This command-line interface (CLI) command initializes your project with Neon's AI-assisted onboarding. It configures your selected editor (Cursor, VS Code, or Claude Code CLI) for seamless integration. The process includes authentication and installation of the Neon MCP server, enabling interactive guides within your AI assistant.

```bash
npx neonctl@latest init

┌  Adding Neon to your project
│
◆  Which editor(s) would you like to configure? (Space to toggle each option, Enter to confirm your selection)
│  ◼ Cursor
│  ◼ VS Code
│  ◻ Claude CLI
│
◒  Authenticating
┌────────┬──────────────────┬────────┬────────────────┐
│ Login  │ Email            │ Name   │ Projects Limit │
├────────┼──────────────────┼────────┼────────────────┤
│ alex   │ alex@domain.com  │ Alex   │ 60             │
└────────┴──────────────────┴────────┴────────────────┘
◇  Authentication successful ✓
│
◇  Installed Neon MCP server
│
◇  Success! Neon is now ready to use with Cursor / VS Code.
│
│
◇  What's next? ─────────────────────────────────────────────────────────────╮
│                                                                            │
│  Restart Cursor / VS Code and type in "Get started with Neon" in the chat  │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────╯
```

--------------------------------

### Install Serverless Framework (npm)

Source: https://neon.com/docs/guides/aws-lambda

Installs the Serverless Framework globally using npm. This is the first step to manage serverless deployments.

```bash
npm install -g serverless
```

--------------------------------

### Create Database Changelog File

Source: https://neon.com/docs/guides/liquibase

This sequence of commands navigates to a project directory and creates a new empty XML file named 'dbchangelog.xml'. This file will be used to store subsequent database schema changes in a structured format.

```bash
cd ~/blogdb
touch dbchangelog.xml
```

--------------------------------

### Initialize Neon Client (JavaScript)

Source: https://neon.com/docs/auth/migrate/from-supabase

Update your client initialization code to use Neon's SDK. This example shows creating a client instance with Neon Auth and Data API configurations, adapting from a Supabase client setup.

```javascript
import { createClient, SupabaseAuthAdapter } from '@neondatabase/neon-js';

export const client = createClient({
  auth: {
    url: import.meta.env.VITE_NEON_AUTH_URL,
    adapter: SupabaseAuthAdapter(),
  },
  dataApi: {
    url: import.meta.env.VITE_NEON_DATA_API_URL,
  },
});
```

--------------------------------

### Create a Neon Project using TypeScript

Source: https://neon.com/docs/reference/typescript-sdk

This example shows how to create a new Neon project with a specified name, region, and PostgreSQL version. It initializes the API client, calls `createProject`, and then logs the details of the newly created project, including its ID and connection string. The `region_id` and `pg_version` parameters are crucial for project setup.

```typescript
import { createApiClient } from '@neondatabase/api-client';

const apiClient = createApiClient({
  apiKey: process.env.NEON_API_KEY!,
});

async function createNeonProject(projectName: string) {
  try {
    const response = await apiClient.createProject({
      project: {
        name: projectName,
        region_id: 'aws-us-east-1',
        pg_version: 17,
      },
    });
    console.log('Project created:', response.data.project);
    console.log('Project ID:', response.data.project.id);
    console.log('Database connection string:', response.data.connection_uris[0].connection_uri);
  } catch (error) {
    console.error('Error creating project:', error);
    throw error;
  }
}

// Example usage: Create a project named "test-project"
createNeonProject('test-project').catch((error) => {
  console.error('Error creating project:', error.message);
});
```

--------------------------------

### Showcase Multi-Language Code with CodeTabs Component

Source: https://neon.com/docs/community/component-guide

The CodeTabs component displays code examples in multiple programming languages, organized into selectable tabs. It requires an array of labels for the tabs and the corresponding code blocks within. Supported languages include JavaScript, Python, and Go, with an emphasis on database connection examples.

```markdown
<CodeTabs labels={["JavaScript", "Python", "Go"]}>

```javascript
const { Client } = require('pg');
const client = new Client({
  connectionString: process.env.DATABASE_URL,
});
await client.connect();
```

```python
import psycopg2
import os

conn = psycopg2.connect(os.environ["DATABASE_URL"])
cur = conn.cursor()
```

```go
import (
    "database/sql"
    _ "github.com/lib/pq"
)

db, err := sql.Open("postgres", os.Getenv("DATABASE_URL"))
```

</CodeTabs>
```

--------------------------------

### Initialize Sequelize Project

Source: https://neon.com/docs/guides/sequelize

Initializes a new Sequelize project by creating essential directories and configuration files. This command is the first step in setting up Sequelize for database management.

```bash
npx sequelize init
```

--------------------------------

### Install @neondatabase/toolkit

Source: https://neon.com/docs/reference/neondatabase-toolkit

Instructions for installing the @neondatabase/toolkit package using various package managers. This is the first step to integrating Neon's capabilities into your project.

```bash
npm install @neondatabase/toolkit
```

```bash
yarn add @neondatabase/toolkit
```

```bash
pnpm add @neondatabase/toolkit
```

```bash
jsr add @neondatabase/toolkit
```

--------------------------------

### Dump and Restore PostgreSQL Database Example

Source: https://neon.com/docs/manage/backup-pg-dump

This example demonstrates the process of backing up a PostgreSQL database using `pg_dump` and then restoring it to another database using `pg_restore`. It includes commands for changing directory, dumping the database into a compressed file (`.bak`), listing the created backup file, and performing the restore operation.

```bash
~$ cd mydump
~/mydump$ pg_dump -Fc -v -d "postgresql://alex:AbC123dEf@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require" -f mydatabase.bak

~/mydump$ ls
mydatabase.bak

~/mydump$ pg_restore -v -d "postgresql://alex:AbC123dEf@ep-dry-morning-a8vn5za2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require" mydatabase.bak
```

--------------------------------

### Example Pooled Connection String

Source: https://neon.com/docs/connect/choose-connection

An example of a pooled connection string for Neon. The '-pooler' subdomain indicates a pooled connection, managed by PgBouncer.

```sql
postgres://alex:AbC123dEf@ep-cool-darkness-123456-pooler.us-east-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require

```

--------------------------------

### Install pg_dump and pg_restore (Command Line)

Source: https://neon.com/docs/manage/backup-pg-dump

Instructions for installing pg_dump and pg_restore utilities on various platforms. These are essential for backing up and restoring Neon databases.

```bash
pg_dump -V
pg_restore -V
```

--------------------------------

### Get Nil UUID Constant

Source: https://neon.com/docs/extensions/uuid-ossp

Retrieves the predefined 'nil' UUID constant ('00000000-0000-0000-0000-000000000000'). This is useful for representing the absence of a UUID or as a default placeholder.

```sql
SELECT uuid_nil();
```

--------------------------------

### Get Neon Database Connection String

Source: https://neon.com/docs/connect/connect-looker-studio

This snippet shows an example of a Neon database connection string formatted for psql. It includes details like username, password, host, database name, and SSL mode.

```sql
psql 'postgresql://neondb_owner:npg_aaaaaaaaaaaa@ep-quiet-mountain-a1t1firv-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
```

--------------------------------

### Extract Flyway Command-Line Tool (Linux)

Source: https://neon.com/docs/guides/flyway

This command extracts the downloaded Flyway command-line tool archive to a specified directory. Ensure you replace 'x.y.z' with the actual version number.

```bash
cd ~/

tar -xzvf flyway-commandline-x.y.z-linux-x64.tar.gz -C ~/
```

--------------------------------

### Connect to Neon with Postgres.js

Source: https://neon.com/docs/guides/javascript

This example illustrates how to establish a connection to a Neon Postgres database using the 'postgres' library (postgres.js). It loads the connection string from environment variables and creates a database client instance. This code requires the 'postgres' library to be installed and the DATABASE_URL to be configured.

```javascript
import postgres from 'postgres';
import dotenv from 'dotenv';

dotenv.config();

const sql = postgres(process.env.DATABASE_URL, {
  ssl: {
    rejectUnauthorized: false // Only for development/testing if needed, use proper certs in production
  }
});

async function queryDatabase() {
  try {
    const result = await sql`SELECT NOW()`;
    console.log('Current time from Neon:', result[0].now);
  } catch (err) {
    console.error('Error executing query', err.stack);
  } finally {
    await sql.end();
  }
}

queryDatabase();
```

--------------------------------

### Initialize and Deploy Express App with Neon via Koyeb CLI

Source: https://neon.com/docs/guides/koyeb

Initializes and deploys an Express.js application connected to Neon using the Koyeb CLI. Requires Koyeb CLI installation, API token, and a Neon connection string. It sets up the instance type, Git repository, build command, ports, routes, and environment variables.

```bash
koyeb apps init express-neon \
--instance-type free \
--git github.com/koyeb/example-express-prisma \
--git-branch main \
--git-build-command "npm run postgres:init" \
--ports 8080:http \
--routes /:8080 \
--env PORT=8080 \
--env DATABASE_URL="{}"
```

--------------------------------

### Example cURL Request to Create Anonymized Branch

Source: https://neon.com/docs/workflows/data-anonymization

This example demonstrates how to use cURL to send a POST request to create an anonymized branch. It includes setting the authorization token, content type, and a JSON payload with masking rules and anonymization start flag. The request body specifies databases, schemas, tables, and columns to mask, along with masking functions or values.

```bash
curl -X POST \
  'https://console.neon.tech/api/v2/projects/{project_id}/branch_anonymized' \
  -H 'Authorization: Bearer $NEON_API_KEY' \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "masking_rules": [
      {
        "database_name": "neondb",
        "schema_name": "public",
        "table_name": "users",
        "column_name": "email",
        "masking_function": "pg_catalog.concat(anon.dummy_uuidv4(), '@example.com')"
      },
      {
        "database_name": "neondb",
        "schema_name": "public",
        "table_name": "users",
        "column_name": "age",
        "masking_function": "anon.random_int_between(25,65)"
      }
    ],
    "start_anonymization": true
  }'
```

--------------------------------

### Creating a New React Component

Source: https://neon.com/docs/community/component-architecture

Provides steps and code examples for creating a new React component, including directory structure, component implementation, index file export, and registration in `sharedMdxComponents.js`.

```bash
mkdir src/components/pages/doc/my-component
```

```javascript
// src/components/pages/doc/my-component/my-component.jsx
import React from 'react';

const MyComponent = ({ title, children }) => {
  return (
    <div className="my-component">
      <h3>{title}</h3>
      {children}
    </div>
  );
};

export default MyComponent;
```

```javascript
// src/components/pages/doc/my-component/index.js
export { default } from './my-component';
```

```javascript
// sharedMdxComponents.js
import MyComponent from '../src/components/pages/doc/my-component';

export const sharedMdxComponents = {
  // ... existing components
  MyComponent,
};
```

```markdown
<!-- In any MDX file -->

<MyComponent title="Test">This is a test of my new component.</MyComponent>
```

--------------------------------

### Create PostgreSQL Table and RLS Policies (SQL)

Source: https://neon.com/docs/data-api/get-started

This SQL script defines a 'posts' table, enables Row-Level Security (RLS), and creates policies for authenticated users to view published posts or their own posts, and to manage (insert, update, delete) only their own posts. It utilizes the `auth.user_id()` helper for user identification.

```sql
-- This script creates a posts table, enables RLS, and defines four policies:
-- one allows authenticated users to read published posts or their own posts,
-- and the other three let users insert, update, and delete only their own posts.

-- 1. Create the table
CREATE TABLE posts (
  id bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  user_id text DEFAULT (auth.user_id()) NOT NULL,
  content text NOT NULL,
  is_published boolean DEFAULT false,
  "created_at" timestamp with time zone DEFAULT now() NOT NULL
);

-- 2. Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- 3. Create Policy: Users can see all published posts and their own posts
CREATE POLICY "Public read access" ON posts
  AS PERMISSIVE
  FOR SELECT TO authenticated
  USING (is_published OR (select auth.user_id() = "posts"."user_id"));

-- 4. Create Policy: Users can insert their own posts
CREATE POLICY "Users can insert their own posts" ON posts
  AS PERMISSIVE
  FOR INSERT TO "authenticated"
  WITH CHECK ((select auth.user_id() = "posts"."user_id"));

-- 5. Create Policy: Users can update their own posts
CREATE POLICY "Users can update their own posts" ON posts
  AS PERMISSIVE
  FOR UPDATE TO "authenticated"
  USING ((select auth.user_id() = "posts"."user_id"))
  WITH CHECK ((select auth.user_id() = "posts"."user_id"));

CREATE POLICY "Users can delete their own posts" ON posts
  AS PERMISSIVE
  FOR DELETE TO "authenticated"
  USING ((select auth.user_id() = "posts"."user_id"));

```

--------------------------------

### Authenticate Neon CLI

Source: https://neon.com/docs/reference/cli-quickstart

Authenticates the Neon CLI with your Neon account using either web authentication (recommended) which opens a browser window, or API key authentication by providing a personal API key. It also shows how to set the API key as an environment variable for persistent authentication.

```bash
neon auth
```

```bash
neon projects list --api-key <your-api-key>
```

```bash
export NEON_API_KEY=<your-api-key>
```

--------------------------------

### Create a New .NET Console Application

Source: https://neon.com/docs/guides/entity-migrations

Initializes a new .NET console application named 'guide-neon-entityframework' and navigates into its directory. This sets up the basic project structure for developing the application that will integrate with Neon Postgres.

```bash
dotnet new console -o guide-neon-entityframework
cd guide-neon-entityframework
```

--------------------------------

### Create Paid Tier Project using Neon API

Source: https://neon.com/docs/guides/ai-agent-integration

This example shows how to create a new project for a paid user using the Neon API, with higher resource quotas suitable for a 'Pro' tier. It configures active time, storage, data transfer, and compute autoscaling. Replace $PAID_ORG_API_KEY with your actual API key.

```bash
curl --request POST \
     --url https://console.neon.tech/api/v2/projects \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $PAID_ORG_API_KEY" \
     --header 'Content-Type: application/json' \
     --data '{ \
  "project": { \
    "name": "user-paid-database", \
    "pg_version": 16, \
    "settings": { \
      "quota": { \
        "active_time_seconds": 2700000, \
        "logical_size_bytes": 10737418240, \
        "data_transfer_bytes": 53687091200 \
      } \
    }, \
    "default_endpoint_settings": { \
      "autoscaling_limit_min_cu": 0.25, \
      "autoscaling_limit_max_cu": 2, \
      "suspend_timeout_seconds": 300 \
    } \
  } \
}'
```

--------------------------------

### Install Express and Neon Dependencies

Source: https://neon.com/docs/guides/express

Installs the Express framework and the necessary Neon database drivers. Supports Neon serverless driver, node-postgres, and postgres.js. Ensure Node.js and npm are installed.

```bash
mkdir neon-express-example
cd neon-express-example
npm init -y
npm install express
npm install @neondatabase/serverless dotenv
```

--------------------------------

### Update Provider Setup for SPA (React)

Source: https://neon.com/docs/auth/migrate/from-legacy-auth

This example shows the update to the main application component in a React SPA to use `NeonAuthUIProvider`. It replaces the `StackProvider` and `StackTheme` with the new provider and imports the shared Better Auth styles.

```jsx
import { StackProvider, StackTheme } from '@stackframe/stack';
import { stackClientApp } from './stack';

function App() {
  return (
    <StackProvider app={stackClientApp}>
      <StackTheme>{/* Your app */}</StackTheme>
    </StackProvider>
  );
}
```

```jsx
import { NeonAuthUIProvider } from '@neondatabase/neon-auth-ui';
import { authClient } from './auth'; // Assuming authClient is initialized elsewhere
import '@neondatabase/neon-auth-ui/style.css';

function App() {
  return (
    <NeonAuthUIProvider authClient={authClient}>
      {/* Your app */}
    </NeonAuthUIProvider>
  );
}
```

--------------------------------

### Flyway SQL Migration: Create Person Table

Source: https://neon.com/docs/guides/flyway

This SQL script defines the schema for a 'person' table, including an 'ID' and 'NAME' column. This is the first migration file that Flyway will apply to the database.

```sql
create table person (
    ID int not null,
    NAME varchar(100) not null
);
```

--------------------------------

### Create Node.js Project and Install Dependencies

Source: https://neon.com/docs/guides/javascript

This snippet demonstrates how to create a new Node.js project directory, initialize it with npm, and install essential libraries like 'pg', 'dotenv', and '@neondatabase/serverless'. It also shows how to configure 'package.json' to enable ES module syntax.

```bash
mkdir neon-nodejs-quickstart
cd neon-nodejs-quickstart
npm init -y
npm install pg dotenv
# Add "type": "module" to package.json
```

--------------------------------

### JavaScript SDK: Filter Data for Null Values

Source: https://neon.com/docs/data-api/get-started

This snippet shows how to use the `.is()` method to filter for rows where a specific column is null. In this example, it selects rows where 'deleted_at' is null.

```javascript
.is('deleted_at', null)
```

--------------------------------

### Get Neon Database Connection String

Source: https://neon.com/docs/guides/deno

Example of a Neon database connection string. This string contains credentials and connection details required to establish a connection to the Neon database. Ensure to replace placeholder values with your actual credentials.

```shell
postgresql://alex:AbC123dEf@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

--------------------------------

### Execute Terraform Commands with Go

Source: https://neon.com/docs/reference/terraform

Demonstrates how to use Go's `os/exec` package to programmatically execute Terraform commands such as `init`, `plan`, and `apply`. This snippet is useful for creating automated testing or CI/CD pipelines for Terraform configurations. It requires the `os/exec` package and assumes Terraform is installed and available in the system's PATH.

```go
package main

import (
	"fmt"
	"log"
	"os/exec"
)

func main() {
	// Example: Running terraform init
	cmdInit := exec.Command("terraform", "init")
	outputInit, errInit := cmdInit.CombinedOutput()
	if errInit != nil {
		log.Fatalf("terraform init failed: %v\nOutput: %s", errInit, outputInit)
	}
	fmt.Printf("terraform init output:\n%s\n", outputInit)

	// Example: Running terraform plan
	cmdPlan := exec.Command("terraform", "plan")
	outputPlan, errPlan := cmdPlan.CombinedOutput()
	if errPlan != nil {
		log.Fatalf("terraform plan failed: %v\nOutput: %s", errPlan, outputPlan)
	}
	fmt.Printf("terraform plan output:\n%s\n", outputPlan)

	// Example: Running terraform apply (use with caution!)
	// cmdApply := exec.Command("terraform", "apply", "-auto-approve")
	// outputApply, errApply := cmdApply.CombinedOutput()
	// if errApply != nil {
	// 	log.Fatalf("terraform apply failed: %v\nOutput: %s", errApply, outputApply)
	// }
	// fmt.Printf("terraform apply output:\n%s\n", outputApply)
}

```

--------------------------------

### Install Neon CLI using Brew or NPM

Source: https://neon.com/docs/get-started/signing-up

Installs the Neon CLI tool. Use Homebrew for macOS or NPM for other platforms. This is a prerequisite for interacting with Neon from the command line.

```bash
brew install neonctl
```

```bash
npm install -g neonctl
```

--------------------------------

### Postgres substring() - Extract Fixed-Length Timestamp

Source: https://neon.com/docs/functions/substring

Extracts a fixed-length timestamp from the beginning of a log entry string. This example uses the substring() function with both start position and length parameters.

```sql
WITH logs AS (
  SELECT '2023-05-15T10:30:00.000Z - User 123 logged in' AS log_entry
  UNION ALL
  SELECT '2023-05-15T11:45:30.000Z - User 456 logged out' AS log_entry
)
SELECT substring(log_entry from 1 for 23) AS timestamp
FROM logs;
```

--------------------------------

### FastAPI with Neon Postgres on AWS App Runner

Source: https://neon.com/docs/changelog/2024-02-09

Provides an example of deploying a FastAPI application with a Neon Postgres backend on AWS App Runner. This would involve Dockerfile configurations and environment variable setups.

```dockerfile
# Example Dockerfile for FastAPI app
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```

--------------------------------

### Update IP Allow Configuration Example

Source: https://neon.com/docs/manage/projects

Shows how to update an IP Allow configuration by specifying the new desired list of allowed IP addresses. Existing configurations are replaced, not appended to.

```text
192.0.2.1, 192.0.2.2
```

--------------------------------

### Install Encore CLI (macOS)

Source: https://neon.com/docs/guides/encore

Installs the Encore CLI using Homebrew on macOS. This is a prerequisite for using Encore for application development.

```bash
brew install encoredev/tap/encore
```

--------------------------------

### Install a Postgres Extension

Source: https://neon.com/docs/get-started/dev-experience

Demonstrates the SQL command to install a PostgreSQL extension within Neon. This is a fundamental operation for enabling extended functionality. Ensure the extension is supported by Neon before attempting installation.

```sql
CREATE EXTENSION pgcrypto;
```

--------------------------------

### PostgreSQL Create and Insert Article Data

Source: https://neon.com/docs/extensions/intarray

Provides SQL statements to create a sample 'articles' table with an integer array column 'tag_ids' and insert some initial data. This setup is used for demonstrating intarray query examples.

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    tag_ids INTEGER[] -- This will store an array of integer tag IDs
);

INSERT INTO articles (title, tag_ids) VALUES
    ('Postgres Performance Tips', '{1,2,3}'),
    ('Introduction to SQL', '{2,4}'),
    ('Advanced intarray Usage', '{1,3,5}'),
    ('Database Normalization', '{4,6}');
```

--------------------------------

### Kysely Integration with Neon

Source: https://neon.com/docs/ai/ai-rules-neon-serverless

Integrate Kysely with Neon using the `PostgresDialect` and a `Pool` instance. This setup is suitable for applications requiring a more direct SQL query builder experience. Ensure Kysely and Neon dependencies are installed.

```typescript
import { Pool } from '@neondatabase/serverless';
import { Kysely, PostgresDialect } from 'kysely';

const dialect = new PostgresDialect({
  pool: new Pool({ connectionString: process.env.DATABASE_URL })
});

const db = new Kysely({
  dialect,
  // schema definitions...
});
```

--------------------------------

### Run Database Migrations

Source: https://neon.com/docs/data-api/demo

Executes database migrations using Bun to set up the necessary tables (notes, paragraphs) and Row-Level Security (RLS) policies. This ensures proper data structure and security are in place.

```bash
bun run db:migrate
```

--------------------------------

### Authorization URL Example

Source: https://neon.com/docs/guides/oauth-integration

An example of the authorization URL used to initiate the OAuth flow with Neon.

```APIDOC
## Authorization URL

Here is an example of what the authorization URL might look like:

```
https://oauth2.neon.tech/oauth2/auth?client_id=neon-experimental&scope=openid%20offline%20offline_access%20urn%3Aneoncloud%3Aprojects%3Acreate%20urn%3Aneoncloud%3Aprojects%3Aread%20urn%3Aneoncloud%3Aprojects%3Aupdate%20urn%3Aneoncloud%3Aprojects%3Adelete&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fapi%2Fauth%2Fcallback%2Fneon&grant_type=authorization_code&state=H58y-rSTebc3QmNbRjNTX9dL73-IyoU2T_WNievO9as&code_challenge=99XcbwOFU6iEsvXr77Xxwsk9I0GL4c4c4Q8yPIVrF_0&code_challenge_method=S256
```
```

--------------------------------

### Install and Authenticate Netlify CLI

Source: https://neon.com/docs/guides/netlify-functions

Commands to install the Netlify CLI globally using npm and then log in to authenticate the CLI with a Netlify account. This is necessary for deploying Netlify Functions.

```bash
npm install netlify-cli -g
```

```bash
netlify login
```

--------------------------------

### Install neon_utils Extension

Source: https://neon.com/docs/extensions/neon-utils

This SQL command installs the neon_utils extension if it's not already present. It's a prerequisite for using other Neon-specific utility functions.

```sql
CREATE EXTENSION IF NOT EXISTS neon_utils;
```

--------------------------------

### Connect to Neon using psql Passwordless Auth

Source: https://neon.com/docs/connect/passwordless-connect

This snippet demonstrates the command to initiate a passwordless connection to Neon using psql. It requires a working psql installation and guides the user through the browser authentication step. The output shows the initial notice and the subsequent successful connection details.

```bash
psql -h pg.neon.tech
```

--------------------------------

### Postgres Audit Log - Create Schema Example

Source: https://neon.com/docs/security/hipaa

This example demonstrates how a simple SQL command to create a schema is captured in Neon's audit logs. The log record provides detailed information about the execution context, command, and parameters. This is useful for security auditing and compliance tracking.

```sql
CREATE SCHEMA IF NOT EXISTS healthcare;
```

```text
2025-05-05 20:23:01.277	 <134>May 6 00:23:01 vm-compute-shy-waterfall-w2cn1o3t-b6vmn young-recipe-29421150/ep-calm-da 2025-05-06 00:23:01.277 GMT,neondb_owner,neondb,1405,10.6.42.155:13702,68195665.57d,1,CREATE SCHEMA, 2025-05-06 00:23:01 GMT,16/2,767,00000,SESSION,1,1,DDL,CREATE SCHEMA,,,CREATE SCHEMA IF NOT EXISTS healthcare,<not logged>,,,,,,,,,neon-internal-sql-editor
```

--------------------------------

### Custom Sign-In Form (Anti-Pattern)

Source: https://neon.com/docs/ai/ai-rules-neon-auth

Illustrates an anti-pattern of building a custom sign-in form instead of using the recommended AuthView component. This example shows manual state management, API calls, and form rendering, which is verbose and error-prone.

```tsx
// ❌ Don't build custom forms unless you have specific requirements
function CustomSignInPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const { error } = await authClient.signIn.email({ email, password });
    if (error) setError(error.message);
    setLoading(false);
  };

  // ... 50+ more lines of form JSX, validation, error display
}

// ✅ Use AuthView instead - one component handles everything
<AuthView pathname="sign-in" />
```

--------------------------------

### View pg_cron Extension Settings with SQL

Source: https://neon.com/docs/extensions/pg_cron

This SQL query allows you to view the current configuration settings for the pg_cron extension within your Neon database. It filters settings whose names start with 'cron.%'.

```sql
SELECT * FROM pg_settings WHERE name LIKE 'cron.%';
```

--------------------------------

### Demonstrate pg_prewarm Performance Improvement (SQL)

Source: https://neon.com/docs/extensions/pg_prewarm

This example illustrates the performance benefits of pg_prewarm by comparing query execution times. It involves creating two identical tables, prewarming one, and then using EXPLAIN ANALYZE to show the difference in execution speed.

```sql
CREATE TABLE tbl_transactions_1
(
    tran_id_ SERIAL,
    transaction_date TIMESTAMPTZ,
    transaction_name TEXT
);

INSERT INTO tbl_transactions_1
(transaction_date, transaction_name)
SELECT x, 'dbrnd'
FROM generate_series('2010-01-01 00:00:00'::timestamptz, '2018-02-01 00:00:00'::timestamptz, '1 minutes'::interval) a(x);

CREATE TABLE tbl_transactions_2
(
    tran_id_ SERIAL,
    transaction_date TIMESTAMPTZ,
    transaction_name TEXT
);

INSERT INTO tbl_transactions_2
(transaction_date, transaction_name)
SELECT x, 'dbrnd'
FROM generate_series('2010-01-01 00:00:00'::timestamptz, '2018-02-01 00:00:00'::timestamptz, '1 minutes'::interval) a(x);

SELECT pg_prewarm('tbl_transactions_1') AS blocks_loaded;

EXPLAIN ANALYZE SELECT * FROM tbl_transactions_1;

EXPLAIN ANALYZE SELECT * FROM tbl_transactions_2;
```

--------------------------------

### Establish and Use Named Connection (SQL)

Source: https://neon.com/docs/extensions/dblink

Demonstrates the process of establishing a named connection to a remote PostgreSQL database, executing a query using that named connection, and then disconnecting. The example connects to a 'production_db' and counts records in the 'orders' table.

```sql
-- Connect with a name
SELECT dblink_connect('production_db', 'host=prod_host port=5432 dbname=prod_data user=reporter password=securepass sslmode=require&channel_binding=require');

-- Execute queries using the named connection
SELECT * FROM dblink('production_db', 'SELECT count(*) FROM orders') AS order_count(count int);

-- Disconnect
SELECT dblink_disconnect('production_db');
```

--------------------------------

### Create Neon Database Tables with SQL

Source: https://neon.com/docs/guides/liquibase

This SQL snippet defines the schema for two tables, 'authors' and 'posts', within a Neon database. It includes primary keys, foreign key constraints, and data type definitions.

```sql
-- Creating the `authors` table
CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    bio TEXT
);

-- Creating the `posts` table
CREATE TABLE posts (
    post_id SERIAL PRIMARY KEY,
    author_id INTEGER REFERENCES authors(author_id),
    title VARCHAR(255) NOT NULL,
    content TEXT,
    published_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

--------------------------------

### Create, Query, and Delete Postgres Database with Neon Toolkit (JavaScript)

Source: https://neon.com/docs/changelog/2024-09-27

This snippet demonstrates how to use the Neon Toolkit to create a new Postgres project, execute SQL CREATE TABLE and INSERT statements, query data, and finally delete the project. It requires an API key from environment variables and utilizes the Neon API Client and Serverless Driver. The output is the result of the SELECT query.

```javascript
import { NeonToolkit } from "@neondatabase/toolkit";

const toolkit = new NeonToolkit(process.env.API_KEY!); 
const project = await toolkit.createProject();

await toolkit.sql(
  project,
  `
    CREATE TABLE IF NOT EXISTS
        users (
            id UUID PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
`,
);

await toolkit.sql(
  project,
  `
    INSERT INTO users (id, name) VALUES (gen_random_uuid(), 'Sam Altman');
`,
);

console.log(
  await toolkit.sql(
    project,
    `
    SELECT name FROM users;
`,
  ),
);

await toolkit.deleteProject(project);
```

--------------------------------

### POST /api/v2/projects - Create Project for Paid User (Pro Tier Example)

Source: https://neon.com/docs/guides/ai-agent-integration

Creates a new project with higher resource quotas suitable for paid users, demonstrating a 'Pro' tier configuration.

```APIDOC
## POST /api/v2/projects

### Description
Creates a new project for a paid user with higher resource quotas, like the 'Pro' tier.

### Method
POST

### Endpoint
/api/v2/projects

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **project** (object) - Required - Project configuration details.
  - **name** (string) - Required - The name of the project.
  - **pg_version** (integer) - Required - The PostgreSQL version to use.
  - **settings** (object) - Optional - Project settings.
    - **quota** (object) - Optional - Resource quotas for the project.
      - **active_time_seconds** (integer) - Optional - Maximum active compute time in seconds (e.g., 2700000 for 750 hours).
      - **logical_size_bytes** (integer) - Optional - Maximum storage size in bytes (e.g., 10737418240 for 10 GB).
      - **data_transfer_bytes** (integer) - Optional - Maximum data transfer in bytes (e.g., 53687091200 for 50 GB).
  - **default_endpoint_settings** (object) - Optional - Default settings for the project's endpoints.
    - **autoscaling_limit_min_cu** (number) - Optional - Minimum compute units for autoscaling (e.g., 0.25).
    - **autoscaling_limit_max_cu** (number) - Optional - Maximum compute units for autoscaling (e.g., 2).
    - **suspend_timeout_seconds** (integer) - Optional - Time in seconds before compute suspends (e.g., 300).

### Request Example
```json
{
  "project": {
    "name": "user-paid-database",
    "pg_version": 16,
    "settings": {
      "quota": {
        "active_time_seconds": 2700000,
        "logical_size_bytes": 10737418240,
        "data_transfer_bytes": 53687091200
      }
    },
    "default_endpoint_settings": {
      "autoscaling_limit_min_cu": 0.25,
      "autoscaling_limit_max_cu": 2,
      "suspend_timeout_seconds": 300
    }
  }
}
```

### Response
#### Success Response (200)
- **project** (object) - Details of the created project.
  - **id** (string) - The unique identifier of the project.
  - **name** (string) - The name of the project.
  - **status** (string) - The current status of the project.
  - **created_at** (string) - Timestamp of project creation.

#### Response Example
```json
{
  "project": {
    "id": "prj_def456",
    "name": "user-paid-database",
    "status": "pending_creation",
    "created_at": "2023-10-27T10:05:00Z"
  }
}
```
```

--------------------------------

### Configure Flyway Connection to Neon Database

Source: https://neon.com/docs/guides/flyway

This configuration snippet defines the connection parameters for Flyway to connect to a Neon PostgreSQL database. It specifies the JDBC URL, username, password, and the location of SQL migration files.

```properties
flyway.url=jdbc:postgresql://ep-cool-darkness-123456.us-east-2.aws.neon.tech:5432/neondb

flyway.user=alex

flyway.password=AbC123dEf

flyway.locations=filesystem:/home/alex/flyway-x.y.z/sql
```

--------------------------------

### Run Development Server

Source: https://neon.com/docs/auth/migrate/from-supabase

This command starts the development server for your application. It is a standard command for many Node.js projects using npm.

```bash
npm run dev

```

--------------------------------

### Create Neon Project using Node.js CLI Script

Source: https://neon.com/docs/guides/database-per-user

This script demonstrates how to create a new Neon project using Node.js. It utilizes the 'commander' library for handling command-line arguments and the '@neondatabase/api-client' to interact with the Neon API. The script requires the NEON_API_KEY environment variable to be set and accepts a project name, PostgreSQL version, and region as parameters. It outputs the creation response or an error message.

```javascript
import { Command } from 'commander';
import { createApiClient } from '@neondatabase/api-client';
import 'dotenv/config';

const program = new Command();
const neonApi = createApiClient({
  apiKey: process.env.NEON_API_KEY,
});

program.option('-n, --name <name>', 'Name of the company').parse(process.argv);

const options = program.opts();

if (options.name) {
  console.log(`Company Name: ${options.name}`);

  (async () => {
    try {
      const response = await neonApi.createProject({
        project: {
          name: options.name,
          pg_version: 16,
          region_id: 'aws-us-east-1',
        },
      });

      const { data } = response;
      console.log(data);
    } catch (error) {
      console.error('Error creating project:', error);
    }
  })();
} else {
  console.log('No company name provided');
}
```

--------------------------------

### Enable pgrouting Extension (SQL)

Source: https://neon.com/docs/extensions/postgis-related-extensions

Enables the pgrouting extension, which adds routing and network analysis capabilities to PostGIS. This extension is useful for transportation and logistics applications. It requires PostGIS to be installed first.

```sql
CREATE EXTENSION IF NOT EXISTS pgrouting;
```

--------------------------------

### Install app.build using Homebrew

Source: https://neon.com/docs/changelog/2025-06-13

This snippet shows how to install the app.build reference implementation using Homebrew, a package manager for macOS and Linux. It provides a command-line interface for setting up AI-powered applications on Neon Postgres.

```bash
brew install app.build
```

--------------------------------

### Error Handling for Authentication Sign-in

Source: https://neon.com/docs/ai/ai-rules-neon-auth

Provides an example of handling potential errors during the email sign-in process. It demonstrates checking for an 'error' object and using a switch statement to handle specific error codes like 'INVALID_EMAIL_OR_PASSWORD' or 'USER_NOT_FOUND'.

```typescript
const { error } = await auth.signIn.email({ email, password });

if (error) {
  switch (error.code) {
    case "INVALID_EMAIL_OR_PASSWORD":
      showError("Invalid email or password");
      break;
    case "EMAIL_NOT_VERIFIED":
      showError("Please verify your email");
      break;
    case "USER_NOT_FOUND":
      showError("User not found");
      break;
    case "TOO_MANY_REQUESTS":
      showError("Too many attempts. Please wait.");
      break;
    default:
      showError("Authentication failed");
  }
}
```

--------------------------------

### Configure Liquibase Properties for Neon Connection

Source: https://neon.com/docs/guides/liquibase

This configuration snippet sets up the `liquibase.properties` file to connect Liquibase to a Neon database. It specifies the changelog file name and the JDBC connection URL, including SSL and channel binding requirements.

```properties
changeLogFile:dbchangelog.xml
url: jdbc:postgresql://ep-cool-darkness-123456.us-east-2.aws.neon.tech/blog?user=alex&password=AbC123dEf&sslmode=require&channel_binding=require
```

--------------------------------

### Initialize Terraform and Download Neon Provider

Source: https://neon.com/docs/reference/terraform

This command initializes your Terraform working directory and downloads the necessary provider plugins, including the Neon provider. Run this after configuring the provider block. Avoid using `-upgrade` in CI pipelines to prevent unintended resource changes.

```bash
terraform init
```

--------------------------------

### Get Session Method (TypeScript)

Source: https://neon.com/docs/ai/ai-rules-neon-auth

Methods for retrieving the current user session. `auth.getSession()` is for async environments like Node.js or server components, while `auth.useSession()` is a React hook for client components.

```typescript
// Async (Node.js, server components)
const session = await auth.getSession();

// React hook (client components)
const session = auth.useSession();
// Returns: { data: Session | null, isPending: boolean }
```

--------------------------------

### Install Neon CLI using npm

Source: https://neon.com/docs/reference/cli-install

This command installs the Neon CLI globally using npm. Requires Node.js 18.0 or higher.

```bash
npm i -g neonctl
```

--------------------------------

### Install StepZen CLI

Source: https://neon.com/docs/guides/stepzen

Installs the StepZen Command Line Interface globally using npm or Yarn. This tool is necessary for interacting with the StepZen platform and managing your GraphQL APIs.

```bash
npm install -g stepzen
```

--------------------------------

### Connect to Neon Database using PSQL

Source: https://neon.com/docs/import/import-sample-data

This command demonstrates how to establish a connection to a Neon database using the `psql` command-line client. Ensure you have `psql` installed and replace the placeholder connection string with your Neon credentials.

```bash
psql postgresql://[user]:[password]@[neon_hostname]/periodic_table
```

--------------------------------

### Create Rust Project and Add Dependencies

Source: https://neon.com/docs/guides/rust

This snippet demonstrates how to create a new Rust project using Cargo and add the required database driver crates. It supports both synchronous (postgres) and asynchronous (tokio-postgres) setups. Ensure you have the Rust toolchain installed.

```bash
cargo new neon-rust-quickstart
cd neon-rust-quickstart
```

```bash
cargo add postgres postgres-openssl openssl dotenvy
```

```bash
cargo add tokio --features full
cargo add tokio-postgres postgres-openssl openssl dotenvy
```

--------------------------------

### Install Neon Extension

Source: https://neon.com/docs/extensions/neon

Installs the Neon extension on your PostgreSQL database. This is a prerequisite for using Neon-specific features like the `neon_stat_file_cache` view.

```sql
CREATE EXTENSION neon;
```

--------------------------------

### Create Neon Branch and Connect with psql

Source: https://neon.com/docs/reference/cli-branches

This command creates a new Neon branch and immediately opens a psql session connected to it. This simplifies the workflow for developers who want to start working with a new branch interactively. Requires psql to be installed.

```bash
neon branch create --psql
```

--------------------------------

### View Job Run Details with SQL

Source: https://neon.com/docs/extensions/pg_cron

This query retrieves the latest five job run details from the `cron.job_run_details` table, ordered by execution start time. It provides insights into job execution status, timings, and any associated messages.

```sql
SELECT * FROM cron.job_run_details ORDER BY start_time DESC LIMIT 5;
```

--------------------------------

### Run Neon CLI without installation (bunx)

Source: https://neon.com/docs/reference/cli-install

Executes the Neon CLI command using bunx without a global installation. This is an alternative to npx for environments using bun.

```bash
# bunx
bunx neonctl <command>
```

--------------------------------

### Run the .NET Application (CLI)

Source: https://neon.com/docs/guides/dotnet-entity-framework

Command to start the .NET application. After running, the application will be accessible at the specified local URL, and Swagger UI can be used for testing.

```bash
dotnet run
```

--------------------------------

### Add Data with SQL Migration

Source: https://neon.com/docs/guides/flyway

This snippet shows how to add data to the 'person' table using a Flyway SQL migration file. It inserts three records with IDs and names. This is typically part of a V2 migration script.

```sql
insert into person (ID, NAME) values (1, 'Alex');
insert into person (ID, NAME) values (2, 'Mr. Lopez');
insert into person (ID, NAME) values (3, 'Ms. Smith');
```

--------------------------------

### Create and Populate Sample Table in Neon (SQL)

Source: https://neon.com/docs/get-started/signing-up

This SQL code snippet demonstrates how to create a new table named 'playing_with_neon' with specified columns (id, name, value) and then populate it with sample data using a generated series. It is intended to be run within the Neon SQL Editor or via psql.

```sql
CREATE TABLE IF NOT EXISTS playing_with_neon(id SERIAL PRIMARY KEY, name TEXT NOT NULL, value REAL);
INSERT INTO playing_with_neon(name, value)
  SELECT LEFT(md5(i::TEXT), 10), random() FROM generate_series(1, 10) s(i);
```

--------------------------------

### Restart Neon Compute Endpoint via API (Bash)

Source: https://neon.com/docs/extensions/pg_cron

This code example shows how to restart a Neon compute endpoint using the API. This action is necessary after updating compute settings, such as enabling the pg_cron extension. Note that restarting the compute will disconnect existing database connections.

```Bash
curl --request POST \
     --url https://console.tech.neon.api/v2/projects/<project_id>/endpoints/<endpoint_id>/restart \
     --header 'accept: application/json' \
     --header 'authorization: Bearer $NEON_API_KEY' \

```

--------------------------------

### Install and Initialize Neon Python SDK

Source: https://neon.com/docs/reference/python-sdk

Install the Neon Python SDK using pip and initialize the NeonAPI client with your API key. This is the first step to programmatically interact with the Neon API from your Python applications.

```bash
$ pip install neon-api
```

```python
from neon_api import NeonAPI

# Initialize the client.
neon = NeonAPI(api_key='your_api_key')
```

--------------------------------

### PostgreSQL: Create and Insert Data into weather_data Table

Source: https://neon.com/docs/functions/avg

This SQL snippet demonstrates how to create a 'weather_data' table with 'date', 'city', and 'temperature' columns and populate it with sample data. This setup is used for subsequent examples of the `avg()` function.

```sql
CREATE TABLE weather_data (
  date DATE,
  city TEXT,
  temperature NUMERIC
);

INSERT INTO weather_data (date, city, temperature) VALUES
  ('2024-03-01', 'New York', 5.5),
  ('2024-03-01', 'Los Angeles', 22.0),
  ('2024-03-01', 'Chicago', 2.0),
  ('2024-03-02', 'New York', 7.0),
  ('2024-03-02', 'Los Angeles', 23.5),
  ('2024-03-02', 'Chicago', 3.5),
  ('2024-03-03', 'New York', 6.5),
  ('2024-03-03', 'Los Angeles', 21.5),
  ('2024-03-03', 'Chicago', 1.0);
```

--------------------------------

### Configure Neon MCP Server (Local Setup)

Source: https://neon.com/docs/ai/connect-mcp-clients-to-neon

Add this JSON configuration to your MCP client's configuration file for local setup using your Neon API key. This method provides a direct connection to your Neon projects.

```json
{
  "neon": {
    "command": "npx",
    "args": ["-y", "@neondatabase/mcp-server-neon", "start", "<YOUR_NEON_API_KEY>"]
  }
}
```

--------------------------------

### Install an Extension

Source: https://neon.com/docs/extensions/pg-extensions

Installs a supported extension using the `CREATE EXTENSION` SQL command. This command can be executed via the Neon SQL Editor or external clients like `psql`. Ensure the extension is supported by Neon.

```sql
CREATE EXTENSION <extension_name>;
```

--------------------------------

### Install postgres.js for Node.js

Source: https://neon.com/docs/guides/cloudflare-hyperdrive

Installs the postgres.js package, a Node.js driver for PostgreSQL, which is used to interact with the Neon database.

```bash
npm install postgres
```

--------------------------------

### Example Workflow for Online Advisor

Source: https://neon.com/docs/extensions/online_advisor

Demonstrates a typical workflow using the online_advisor extension. This includes activating workload collection, viewing index and statistics proposals, applying recommendations, and checking planning/execution times.

```sql
-- Activate and run workload
SELECT get_executor_stats();

-- View index proposals
SELECT create_index, n_filtered, n_called, elapsed_sec
FROM proposed_indexes
ORDER BY elapsed_sec DESC
LIMIT 10;

-- View extended statistics proposals
SELECT create_statistics, misestimation, n_called, elapsed_sec
FROM proposed_statistics
ORDER BY misestimation DESC
LIMIT 10;

-- Apply a recommendation
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_customer_date ON orders(customer_id, order_date);
VACUUM (ANALYZE) orders;

-- Check planning/execution times
SELECT * FROM get_executor_stats(true); -- reset after reading
```

--------------------------------

### Install @prisma/extension-read-replicas

Source: https://neon.com/docs/guides/read-replica-prisma

Install the @prisma/extension-read-replicas package using npm or yarn to add read replica support to your Prisma Client.

```bash
npm install @prisma/extension-read-replicas
```

--------------------------------

### Download Neon CLI macOS binary

Source: https://neon.com/docs/reference/cli-install

Downloads the Neon CLI binary for macOS. This method does not require a separate installation step.

```bash
curl -sL https://github.com/neondatabase/neonctl/releases/latest/download/neonctl-macos -o neonctl

```

--------------------------------

### FeatureBetaProps: Beta Feature Status Indicator

Source: https://neon.com/docs/community/component-guide

FeatureBetaProps is used to indicate that a feature is currently in Beta. This example shows how to use the component with a specific feature name, 'OpenTelemetry integration', to inform users about its status.

```html
<FeatureBetaProps feature_name="OpenTelemetry integration" />
```

--------------------------------

### Install Neon CLI using Homebrew

Source: https://neon.com/docs/reference/cli-install

This command installs the Neon CLI using the Homebrew package manager on macOS.

```bash
brew install neonctl
```

--------------------------------

### Initialize Database for pgbench

Source: https://neon.com/docs/extensions/neon-utils

This command initializes the Neon database with tables required by pgbench. Replace placeholders with your actual Neon connection details. This step is crucial to avoid errors during pgbench execution.

```bash
pgbench -i postgresql://[user]:[password]@[neon_hostname]/[dbname]
```

--------------------------------

### Console Logging Example in React

Source: https://neon.com/docs/community/component-architecture

This snippet demonstrates how to use `console.log` within a React component to inspect props. This is a common debugging technique for understanding component data flow and state during development. Ensure the component is exported correctly for use.

```javascript
const MyComponent = (props) => {
  console.log('MyComponent props:', props);
  return <div>...</div>;
};
```

--------------------------------

### Example Compute Hour Calculation

Source: https://neon.com/docs/introduction/legacy-plans

An example demonstrating the calculation of compute hours for a 2 CU compute that is active for approximately 730 hours in a month.

```text
2 * 730 = 1460 compute hours
```

--------------------------------

### Install Dependencies for Neon Serverless Driver with Prisma

Source: https://neon.com/docs/guides/prisma

Installs necessary npm packages for using the Neon serverless driver with Prisma, including the Prisma driver adapter, the Neon serverless driver itself, and the `ws` package for WebSocket support.

```bash
npm install ws @prisma/adapter-neon @neondatabase/serverless
npm install -D @types/ws
```

--------------------------------

### Create Neon Terraform Project Directory and Initialize

Source: https://neon.com/docs/reference/terraform

Commands to create a new directory for your Terraform project and navigate into it, followed by initializing the Terraform environment.

```bash
mkdir neon-terraform-project
cd neon-terraform-project
```

```bash
terraform init
```

--------------------------------

### Displaying pg_repack Help Information

Source: https://neon.com/docs/extensions/pg_repack

This command displays the comprehensive help information for `pg_repack`, detailing all available options, their descriptions, and usage examples. It's the go-to command for understanding the full capabilities of the tool.

```bash
pg_repack --help
```

--------------------------------

### Set Up Python Virtual Environment and Install Packages

Source: https://neon.com/docs/guides/django-migrations

This code sets up a Python virtual environment for a Django project and installs necessary packages: Django for the web framework, psycopg2-binary for PostgreSQL connectivity, python-dotenv for managing environment variables, and dj-database-url for parsing database URLs. It also freezes the dependencies into a requirements.txt file.

```bash
python -m venv myenv

# On macOS and Linux
source myenv/bin/activate
# On Windows
myenv\Scripts\activate

mkdir guide-neon-django && cd guide-neon-django

pip install Django "psycopg2-binary"
pip install python-dotenv dj-database-url
pip freeze > requirements.txt
```

--------------------------------

### Setup Parent Table for Partitioning with pg_partman

Source: https://neon.com/docs/extensions/pg_partman

This SQL command utilizes the `create_parent` function from the `pg_partman` extension to establish the partitioning scheme for the 'public.test_user_activities' table, using 'activity_time' as the control column and partitioning by week.

```sql
SELECT partman.create_parent(
  p_parent_table := 'public.test_user_activities',
  p_control := 'activity_time',
  p_interval := '1 week'
);
```

--------------------------------

### Run Neon CLI without installation (npx)

Source: https://neon.com/docs/reference/cli-install

Executes the Neon CLI command using npx without a global installation. This is useful for quick commands or testing.

```bash
# npx
npx neonctl <command>
```

--------------------------------

### Start Local Netlify Development Server (Bash)

Source: https://neon.com/docs/guides/netlify-functions

This command initiates the Netlify local development server. It allows developers to test their Netlify functions and frontend locally before deploying to production, simulating the Netlify environment.

```bash
netlify dev
```

--------------------------------

### Drizzle Configuration Example (TypeScript)

Source: https://neon.com/docs/guides/database-per-user

This is an example of a DrizzleORM configuration file. It specifies the output directory for migrations, the schema file location, the database dialect (PostgreSQL), and the database credentials loaded from environment variables. This file is generated by the main script.

```typescript
// src/configs/acme-corp/drizzle.config.ts

import 'dotenv/config';
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  out: './drizzle/acme-corp',
  schema: './src/db/schema.ts',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.ACME_CORP_DATABASE_URL!,
  },
});

```

--------------------------------

### Deploy Database Schema Change with Liquibase

Source: https://neon.com/docs/guides/liquibase

This command deploys pending database schema changes tracked by Liquibase. It applies changesets defined in your changelog file to the connected Neon database. Successful execution indicates the schema update has been applied.

```bash
liquibase update
```

--------------------------------

### Install Firebase and Psycopg Libraries using Pip

Source: https://neon.com/docs/import/migrate-from-firebase

Installs the necessary Python packages for interacting with Firebase Admin SDK and PostgreSQL. Ensure you have Python 3.10 or later installed.

```bash
pip install firebase-admin "psycopg[binary,pool]"
```

--------------------------------

### Connect with Read-Write User (psql)

Source: https://neon.com/docs/manage/database-access

This is an example connection string for using the psql client with a read-write user. It specifies the connection parameters including user credentials, host, database name, and SSL/channel binding settings.

```Bash
psql postgresql://readwrite_user1:AbC123dEf@ep-cool-darkness-123456.us-west-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require
```

--------------------------------

### Initiating Neon OAuth Flow with Authorization URL Parameters

Source: https://neon.com/docs/guides/oauth-integration

This example demonstrates how to construct an authorization URL to initiate the OAuth flow with the Neon server. It includes necessary query parameters such as `client_id`, `redirect_uri`, `scope`, `response_type`, `code_challenge`, and `state`.

```url
https://oauth2.neon.tech/oauth2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=urn:neoncloud:projects:create%20urn:neoncloud:projects:read%20urn:neoncloud:projects:update%20urn:neoncloud:projects:delete%20urn:neoncloud:orgs:read&response_type=code&code_challenge=RANDOM_STRING&state=ANOTHER_RANDOM_STRING
```

--------------------------------

### Install Neon Serverless Driver (npm)

Source: https://neon.com/docs/connect/choose-connection

Installs the Neon Serverless Driver using npm, a JavaScript package manager. This driver is essential for using Neon in serverless environments.

```bash
npm install @neondatabase/serverless

```

--------------------------------

### Initialize Neon CLI

Source: https://neon.com/docs/introduction

Initialize your app with Neon using the Neon CLI for AI-guided onboarding. This command helps configure your application with Neon, tailored to your codebase.

```shell
npx neonctl@latest init
```

--------------------------------

### Cross-Database Reporting with dblink (SQL)

Source: https://neon.com/docs/extensions/dblink

Combines data from a local Neon database table ('customers') with aggregated data from a remote PostgreSQL database ('orders'). This example shows how to join local customer information with remote order totals to generate comprehensive reports.

```sql
SELECT l.customer_name, r.order_total
FROM customers l
JOIN dblink('orders_db', 'SELECT customer_id, sum(amount) AS order_total FROM orders GROUP BY customer_id')
AS r(customer_id INTEGER, order_total NUMERIC) ON l.customer_id = r.customer_id;
```

--------------------------------

### Install neon_utils Extension

Source: https://neon.com/docs/extensions/neon-utils

This code snippet shows the SQL command to install the `neon_utils` extension in Neon. This extension is necessary to use the `num_cpus()` function for monitoring autoscaling.

```sql
CREATE EXTENSION neon_utils;
```

--------------------------------

### Make API Call to Retrieve Projects (curl)

Source: https://neon.com/docs/manage/api-keys

Demonstrates how to use a cURL command with an API key to retrieve a list of projects from the Neon API. It requires a valid API key and optionally uses `jq` for pretty-printing the JSON output. The response includes project details such as ID, region, creation timestamp, and proxy host.

```bash
curl 'https://console.neon.tech/api/v2/projects' \
  -H 'Accept: application/json' \
  -H "Authorization: Bearer $NEON_API_KEY" | jq
```

--------------------------------

### Create a Neon Project using API

Source: https://neon.com/docs/manage/projects

Demonstrates how to create a new project in Neon using the Neon API via a cURL request. It requires an API key and specifies the project name and branch settings in the request body.

```bash
curl
  --request POST
  --header "Authorization: Bearer $NEON_API_KEY"
  --header "Content-Type: application/json"
  --data '{
    "branch_id": "main",
    "project_name": "my-new-project"
  }'
  'https://console.neon.tech/api/v2/projects'
| jq
```

--------------------------------

### Node.js Backend Setup for Neon Auth

Source: https://neon.com/docs/ai/ai-rules-neon-auth

Initializes the Neon Auth client for a Node.js backend environment. This setup allows for server-side authentication operations such as signing in and retrieving sessions.

```typescript
import { createAuthClient } from "@neondatabase/auth";

const auth = createAuthClient(process.env.NEON_AUTH_URL!);
await auth.signIn.email({ email, password });
const session = await auth.getSession();
```

--------------------------------

### Install 'pg_repack' Extension in PostgreSQL

Source: https://neon.com/docs/extensions/pg-extensions

This SQL command installs the 'pg_repack' extension. Note that this extension is only available on paid Neon plans and requires a support ticket to enable. It also requires the pg_repack CLI to be installed.

```sql
CREATE EXTENSION pg_repack;
```

--------------------------------

### Neon CLI Initialization

Source: https://neon.com/docs/changelog/2025-11-07

Initialize Neon integration into your application's root directory using the `neonctl` CLI command. This command guides you through authentication and sets up the Neon MCP server for AI assistant integration.

```APIDOC
## npx neonctl@latest init

### Description
Initializes Neon integration into your project by configuring the Neon MCP (Model Context Protocol) Server. This command provides your AI assistant with context about your Neon project, including connection details, schema, and best practices.

### Method
CLI Command

### Endpoint
Run in your app's root directory.

### Parameters
None

### Request Example
```bash
npx neonctl@latest init
```

### Response
#### Success Response
The command provides interactive prompts for authentication and setup, followed by success messages upon completion.

#### Response Example
```
┌  Adding Neon to your project
│
◒  Authenticating.
┌────────┬──────────────────┬────────┬────────────────┐
│ Login  │ Email            │ Name   │ Projects Limit │
├────────┼──────────────────┼────────┼────────────────┤
│ alex   │ alex@domain.com  │ Alex   │ 20             │
└────────┴──────────────────┴────────┴────────────────┘
◇  Authentication successful ✓
│
◇  Installed Neon MCP server
│
◇  Success! Neon is now ready to use with Cursor.
│
│
◇  What's next? ────────────────────────────────────────────────────────────────────────────╮
│                                                                                           │
│  Restart Cursor and ask Cursor to "Get started with Neon using MCP Resource" in the chat  │
│                                                                                           │
├───────────────────────────────────────────────────────────────────────────────────────────╯
│
└  Have feedback? Email us at feedback@neon.tech
```
```

--------------------------------

### DetailIconCards Component Usage Example

Source: https://neon.com/docs/community/component-icon-guide

Demonstrates how to use the DetailIconCards component to display integrations with icons. It takes child 'a' tags with href, title, description, and icon attributes to represent different services or features. Ensure the specified icon names correspond to available assets in the DetailIconCards icon system.

```html
<DetailIconCards>
  <a
    href="/docs/ai/openai"
    title="OpenAI integration"
    description="Build AI features with OpenAI"
    icon="openai"
  >
    OpenAI Integration
  </a>
  <a
    href="/docs/ai/langchain"
    title="LangChain integration"
    description="Create AI workflows with LangChain"
    icon="langchain"
  >
    LangChain Integration
  </a>
</DetailIconCards>
```

--------------------------------

### Configure Program.cs for Entity Framework and Controllers (C#)

Source: https://neon.com/docs/guides/dotnet-entity-framework

Sets up the .NET application services, including registering the ApplicationDbContext with dependency injection and enabling controllers. It also configures Swagger for API documentation.

```csharp
using Microsoft.EntityFrameworkCore;
using NeonEfExample.Data;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();

builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();
app.UseAuthorization();
app.MapControllers();

if (app.Environment.IsDevelopment())
{
    app.Run("http://localhost:5001");
}
else
{
    app.UseHttpsRedirection();
    app.Run();
}
```

--------------------------------

### Install Neon SDK (npm)

Source: https://neon.com/docs/auth/migrate/from-supabase

This command replaces the Supabase JavaScript SDK with Neon's equivalent. Ensure you have npm installed and are in your project's root directory.

```bash
npm uninstall @supabase/supabase-js
npm install @neondatabase/neon-js
```

--------------------------------

### Start Compute Endpoint

Source: https://neon.com/docs/ai/ai-rules-neon-python-sdk

Manually starts a compute endpoint that is currently in an 'idle' state.

```APIDOC
## POST /projects/{project_id}/endpoints/{endpoint_id}/start

### Description
Manually starts an `idle` compute endpoint.

### Method
POST

### Endpoint
`/projects/{project_id}/endpoints/{endpoint_id}/start`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The ID of the project.
- **endpoint_id** (string) - Required - The ID of the endpoint to start.

### Request Example
(No request body for start operation)

### Response
#### Success Response (200)
- **status** (string) - Indicates the status of the operation (e.g., "started").

#### Response Example
```json
{
  "status": "started"
}
```
```

--------------------------------

### Create a sample table with bloat in SQL

Source: https://neon.com/docs/extensions/pg_repack

SQL statements to create a sample table and then delete a significant portion of its data to simulate table bloat for demonstration purposes.

```sql
CREATE TABLE public.bloated_table (
    id SERIAL PRIMARY KEY,
    data TEXT
);

-- Insert some initial data
INSERT INTO public.bloated_table (data)
SELECT md5(random()::text)
FROM generate_series(1, 100000);

-- Delete a significant portion of the data to simulate bloat
DELETE FROM public.bloated_table WHERE id % 2 = 0;
```

--------------------------------

### Retrieve Project Consumption Metrics (cURL Example)

Source: https://neon.com/docs/guides/consumption-metrics

Demonstrates how to retrieve detailed consumption metrics for projects within an account. This endpoint allows filtering by project IDs, specifying the organization, and selecting specific metrics. It supports different granularity levels like hourly, daily, and monthly.

```curl
GET https://console.neon.tech/api/v2/consumption_history/projects?from=2024-06-30T00:00:00Z&to=2024-07-02T00:00:00Z&granularity=daily&project_ids=cold-poetry-09157238,quiet-snow-71788278
```

--------------------------------

### Apply RLS Policy with auth.user_id()

Source: https://neon.com/docs/extensions/pg_session_jwt

An example of creating a Row-Level Security (RLS) policy for a 'todos' table. It uses the `auth.user_id()` function to ensure that users can only select their own data. This requires the pg_session_jwt extension and proper JWT authentication setup.

```sql
CREATE POLICY "Users can only see their own data"
  ON todos
  FOR SELECT
  USING (user_id = auth.user_id());
```

--------------------------------

### Connect to Neon Database

Source: https://neon.com/docs/extensions/neon

Provides an example of a PostgreSQL connection string for connecting to a Neon database. This string includes host, port, username, password, database name, and SSL/channel binding parameters.

```sql
psql postgresql://alex:AbC123dEf@ep-cool-darkness-123456.us-east-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require
```

--------------------------------

### Find K-Shortest Paths using pgr_ksp (SQL)

Source: https://neon.com/docs/extensions/postgis-related-extensions

Employs the pgrouting 'pgr_ksp' function to find multiple alternative shortest paths (K-shortest paths) between a start node (1) and an end node (4). This query allows for finding up to 2 alternative paths and considers both forward and reverse costs for undirected travel.

```sql
SELECT
    route.path_id, 
    route.path_seq, 
    route.node, 
    route.edge, 
    route.cost, 
    route.agg_cost, 
    rn.name AS road_name
FROM pgr_ksp(
    'SELECT id, source, target, cost, reverse_cost FROM road_network',
    1, -- start node
    4, -- end node
    2, -- number of alternative paths
    directed := false,
    heap_paths := false
) AS route
LEFT JOIN road_network rn ON route.edge = rn.id
ORDER BY route.path_id, route.path_seq;
```

--------------------------------

### Install Neon Auth SDK

Source: https://neon.com/docs/auth/quick-start/tanstack-router

Installs the Neon Auth SDK and UI library for your application. This is a prerequisite for integrating Neon's authentication services.

```bash
cd my-app && npm install @neondatabase/neon-js
```

--------------------------------

### Connect to Neon with Node-Postgres (pg)

Source: https://neon.com/docs/guides/javascript

Example demonstrating how to connect to a Neon Postgres database from a Node.js application using the 'pg' library. It utilizes environment variables for the connection string and imports the 'Pool' class to manage database connections. This snippet assumes the 'pg' library and 'dotenv' are installed and the DATABASE_URL is set in the .env file.

```javascript
import pg from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false // Only for development/testing if needed, use proper certs in production
  }
});

async function queryDatabase() {
  try {
    const client = await pool.connect();
    const result = await client.query('SELECT NOW()');
    console.log('Current time from Neon:', result.rows[0].now);
    client.release();
  } catch (err) {
    console.error('Error executing query', err.stack);
  } finally {
    await pool.end();
  }
}

queryDatabase();
```

--------------------------------

### Run Neon CLI without Installation using npx or bunx

Source: https://neon.com/docs/reference/neon-cli

Demonstrates how to execute Neon CLI commands without a prior installation using npx (for npm users) or bunx (for bun users).

```bash
# npx
npx neonctl <command>

# bunx
bunx neonctl <command>
```

--------------------------------

### Install and Use Neon Python SDK

Source: https://neon.com/docs/changelog/2024-11-22

This snippet demonstrates how to install the Neon Python SDK using pip and then use it to initialize a client and fetch user information. It requires the `neon-api` package and can authenticate using environment variables or an API key.

```bash
pip install neon-api
```

```python
from neon_api import NeonAPI

# Initialize the client.
neon = NeonAPI.from_environ() or NeonAPI(api_key='your_api_key')

# Get the current user
user = neon.me()
print(user)
```

--------------------------------

### Search Neon Resources with AI Assistant

Source: https://neon.com/docs/changelog/2025-11-14

This example demonstrates how to query your AI assistant to search across all Neon resources. The assistant will return structured results with direct links to the Neon Console. A companion `fetch` tool can be used to retrieve detailed information about any resource.

```natural_language
Can you search for "production" across my Neon resources?
```

--------------------------------

### Create a Neon Project with Toolkit

Source: https://neon.com/docs/ai/ai-rules-neon-toolkit

Creates a new Neon project, optionally with custom configurations like name and PostgreSQL version. It returns a `ToolkitProject` object containing all necessary details for subsequent operations, such as connection URIs.

```typescript
const project = await toolkit.createProject();
console.log(`Project created. Connection URI: ${project.connectionURIs[0].connection_uri}`);

const customizedProject = await toolkit.createProject({
  name: 'ai-agent-database',
  pg_version: 16,
});
console.log(`Project "${customizedProject.project.name}" created.`);
```

--------------------------------

### Check Installed Extension Versions

Source: https://neon.com/docs/extensions/pg-extensions

Retrieves a list of all installed extensions and their current versions from the `pg_extension` system catalog table. This is useful for tracking installed extensions and their versions.

```sql
SELECT * FROM pg_extension;
```

--------------------------------

### Protected Route Example (React)

Source: https://neon.com/docs/auth/reference/ui-components

Illustrates how to protect routes using Neon Auth UI components. The `SignedIn` component renders its children only when a user is authenticated, while `SignedOut` combined with `RedirectToSignIn` ensures unauthenticated users are redirected to the sign-in page. This setup is useful for controlling access to specific parts of your application.

```javascript
import { SignedIn, SignedOut, RedirectToSignIn } from '@neondatabase/neon-js/auth/react/ui';

function Dashboard() {
  return (
    <>
      <SignedIn>
        <h1>Dashboard</h1>
      </SignedIn>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
    </>
  );
}
```

--------------------------------

### Example Neon Database Connection Strings

Source: https://neon.com/docs/guides/flyway-multiple-environments

These are example JDBC connection strings for Neon databases. Each string points to a different branch (main, development, staging) and includes the hostname, database name, user, and password.

```sql
jdbc:postgresql://ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?user=alex&password=AbC123dEf
```

```sql
jdbc:postgresql://ep-mute-night-47642501.us-east-2.aws.neon.tech/neondb?user=alex&password=AbC123dEf
```

```sql
jdbc:postgresql://ep-shrill-shape-27763949.us-east-2.aws.neon.tech/neondb?user=alex&password=AbC123dEf
```

--------------------------------

### Reflex App Initialization and Page Addition

Source: https://neon.com/docs/guides/reflex

This snippet demonstrates the initialization of a Reflex application and the process of adding a page to it. It shows how to create an instance of `rx.App` and then associate a defined page function (like `index`) with the application using `app.add_page()`.

```python
app = rx.App()
app.add_page(index)
```

--------------------------------

### Example JSON Response for Project Creation

Source: https://neon.com/docs/ai/ai-rules-neon-api

This is an example of the JSON response received after successfully creating a Neon project. It includes details about the project's ID, region, name, provisioner, default endpoint settings, and various configuration options such as IP allowlisting and maintenance windows.

```json
{
  "project": {
    "data_storage_bytes_hour": 0,
    "data_transfer_bytes": 0,
    "written_data_bytes": 0,
    "compute_time_seconds": 0,
    "active_time_seconds": 0,
    "cpu_used_sec": 0,
    "id": "sparkling-hill-99143322",
    "platform_id": "aws",
    "region_id": "aws-us-west-2",
    "name": "my-new-api-project",
    "provisioner": "k8s-neonvm",
    "default_endpoint_settings": {
      "autoscaling_limit_min_cu": 0.25,
      "autoscaling_limit_max_cu": 0.25,
      "suspend_timeout_seconds": 0
    },
    "settings": {
      "allowed_ips": {
        "ips": [],
        "protected_branches_only": false
      },
      "enable_logical_replication": false,
      "maintenance_window": {
        "weekdays": [5],
        "start_time": "07:00",
        "end_time": "08:00"
      }
    }
  }
}
```

--------------------------------

### Install Kysely and Neon Drivers

Source: https://neon.com/docs/guides/kysely

Installs the core Kysely package along with specific drivers for connecting to Neon. Options include the Neon serverless HTTP driver (`kysely-neon`), a Neon WebSocket driver, and the traditional `pg` driver (node-postgres).

```shell
# For Neon Serverless (HTTP):
npm install kysely kysely-neon

# For Neon WebSocket (if applicable, package name may vary):
# npm install kysely @neon_tech/kysely-ws-driver

# For node-postgres:
npm install kysely pg
```

--------------------------------

### Organize General Content with Tabs Component

Source: https://neon.com/docs/community/component-guide

The Tabs component organizes general content into selectable tabs, distinct from CodeTabs which is specifically for code examples. It uses 'labels' for tab titles and 'TabItem' for the content within each tab. This is useful for presenting different aspects of a topic or instructions for various platforms.

```markdown
<Tabs labels={["Console", "CLI", "API"]}>
<TabItem>
Create a database using the Neon Console by navigating to your project dashboard and clicking "Create Database".
</TabItem>
<TabItem>
Use the Neon CLI to create a database:

```bash
neon databases create --name my-database
```

</TabItem>
<TabItem>
Use the API to create a database:

```bash
curl -X POST https://console.neon.tech/api/v2/projects/my-project/databases \
  -H "Authorization: Bearer $NEON_API_KEY"
```

</TabItem>
</Tabs>
```

--------------------------------

### Rollback Last Database Change with Liquibase

Source: https://neon.com/docs/guides/liquibase

This command rolls back the most recent database schema change applied by Liquibase. It reverts the specified number of changesets, allowing for error correction or experimentation. Ensure you understand the implications before executing a rollback.

```bash
liquibase rollbackCount 1
```

--------------------------------

### Create and Insert into a Non-Partitioned Table

Source: https://neon.com/docs/extensions/pg_partman

This SQL snippet defines the structure of the 'test_user_activities' table and populates it with sample data. This serves as the initial state before partitioning is applied.

```sql
CREATE TABLE public.test_user_activities (
  activity_id serial,
  activity_time TIMESTAMPTZ NOT NULL,
  activity_type TEXT NOT NULL,
  content_id INT NOT NULL,
  user_id INT NOT NULL
);

INSERT INTO test_user_activities (activity_time, activity_type, content_id, user_id)
VALUES
    ('2024-03-15 10:00:00', 'like', 1001, 101),
    ('2024-03-16 15:30:00', 'comment', 1002, 102),
    ('2024-03-17 09:45:00', 'share', 1003, 103),
    ('2024-03-18 18:20:00', 'like', 1004, 104),
    ('2024-03-19 12:10:00', 'comment', 1005, 105),
    ('2024-03-20 08:00:00', 'like', 1006, 106),
    ('2024-03-21 14:15:00', 'share', 1007, 107),
    ('2024-03-22 11:30:00', 'like', 1008, 108),
    ('2024-03-23 16:45:00', 'comment', 1009, 109),
    ('2024-03-24 20:00:00', 'share', 1010, 110),
    ('2024-03-25 09:30:00', 'like', 1011, 111),
    ('2024-03-26 13:45:00', 'comment', 1012, 112),
    ('2024-03-27 17:00:00', 'share', 1013, 113),
    ('2024-03-28 11:15:00', 'like', 1014, 114),
    ('2024-03-29 15:30:00', 'comment', 1015, 115);
```

--------------------------------

### Connect to Neon Development Branch using psql

Source: https://neon.com/docs/manage/database-access

This example shows how to connect to a specific Neon development branch database using the `psql` command-line client. It includes the connection string format with user credentials, host, and database name, along with SSL/channel binding parameters required for secure connection.

```bash
psql postgresql://dev_user1:AbC123dEf@ep-cool-darkness-123456.us-west-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require
```

--------------------------------

### Install Neon Serverless Driver using npm

Source: https://neon.com/docs/guides/deno

Alternative command to install the Neon serverless driver using npm. This is useful if you are managing your project dependencies with npm, providing flexibility in how you integrate Neon with your Deno projects.

```shell
npx jsr add @neon/serverless
```

--------------------------------

### Start Development Server (Bash)

Source: https://neon.com/docs/auth/quick-start/nextjs

This command starts the Next.js development server. It's a standard command for running a local development environment for a Next.js project. For Safari users experiencing issues with third-party cookies on non-HTTPS connections, the `--experimental-https` flag can be added to run the server on `https://localhost:3000`.

```bash
npm run dev
```

--------------------------------

### PostgreSQL: Manage Transactions

Source: https://neon.com/docs/postgresql/query-reference

Demonstrates the use of transactions in PostgreSQL to ensure data integrity by grouping operations into a single unit of work. Examples include starting a transaction with BEGIN, committing changes with COMMIT, and reverting changes with ROLLBACK. It also shows how to use SAVEPOINT for partial rollbacks within a transaction.

```sql
-- Start a transaction
BEGIN;

-- Perform several operations within the transaction
INSERT INTO accounts (user_id, balance) VALUES (1, 1000);
UPDATE accounts SET balance = balance - 100 WHERE user_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE user_id = 2;

-- Commit the transaction to make changes permanent
COMMIT;

-- Start another transaction
BEGIN;

-- Perform operations
UPDATE accounts SET balance = balance - 50 WHERE user_id = 1;
UPDATE accounts SET balance = balance + 50 WHERE user_id = 3;

-- Rollback the transaction in case of an error or if operations should not be finalized
ROLLBACK;

-- Demonstrating transaction with SAVEPOINT
BEGIN;
INSERT INTO accounts (user_id, balance) VALUES (3, 500);

-- Create a savepoint
SAVEPOINT my_savepoint;

UPDATE accounts SET balance = balance - 100 WHERE user_id = 3;
-- Assume an error or a need to revert to the savepoint
ROLLBACK TO SAVEPOINT my_savepoint;

-- Proceed with other operations or end transaction
COMMIT;
```

--------------------------------

### Kysely Database CRUD Operations Example

Source: https://neon.com/docs/guides/kysely

Example TypeScript code demonstrating how to perform an 'Insert' (Create) operation on the 'users' table using Kysely.

```typescript
import { db } from './db.ts';

async function main() {
  try {
    // 1. Insert (Create)
    const { id } = await db
      .insertInto('users')
      .values({
        name: 'Neon User',
        email: `user-${Date.now()}@example.com`,
      })
      .returning('id')
      .executeTakeFirstOrThrow();

    console.log(`User created with ID: ${id}`);


```

--------------------------------

### Install Neon Toolkit with Deno

Source: https://neon.com/docs/ai/ai-rules-neon-toolkit

Installs the Neon Toolkit package using JSR (JavaScript Registry) for Deno runtime environments. This command adds the necessary package to your Deno project.

```bash
deno add jsr:@neon/toolkit
```

--------------------------------

### Initialize Next.js Project and Install Dependencies

Source: https://neon.com/docs/guides/auth-auth0

This snippet shows the command to create a new Next.js project with TypeScript and other common configurations. It also includes the commands to install necessary npm packages for Neon database integration, Drizzle ORM, and Auth0 authentication.

```bash
npx create-next-app guide-neon-next-auth0 --typescript --eslint --tailwind --use-npm --no-src-dir --app --import-alias "@/*"

npm install @neondatabase/serverless drizzle-orm
npm install -D drizzle-kit dotenv
npm install @auth0/nextjs-auth0
```

--------------------------------

### Install Kysely Neon Serverless Driver and Dependencies

Source: https://neon.com/docs/guides/kysely

Installs the necessary packages for using Kysely with the Neon serverless driver and dotenv for environment variable management.

```bash
npm install kysely kysely-neon @neondatabase/serverless dotenv
```

--------------------------------

### Construct Connection String with sslnegotiation=direct (SQL)

Source: https://neon.com/docs/connect/connection-latency

Provides an example of a PostgreSQL connection string incorporating the `sslnegotiation=direct` parameter for optimized SSL negotiation. This format is typically used when establishing connections from applications or client tools.

```sql
postgresql://[user]:[password]@[neon_hostname]/[dbname]?sslmode=verify-full&sslnegotiation=direct

```

--------------------------------

### Filter Remote Table Names (SQL)

Source: https://neon.com/docs/extensions/dblink

Retrieves table names from a remote database using a named connection and filters the results to include only those starting with 'user'. The query first fetches all table names from the 'public' schema and then applies a LIKE condition.

```sql
SELECT rt.table_name
FROM dblink('my_remote_db', 'SELECT table_name FROM information_schema.tables WHERE table_schema = ''public''')
AS rt(table_name TEXT)
WHERE rt.table_name LIKE 'user%';
```

--------------------------------

### Basic Auth Flow Example (React)

Source: https://neon.com/docs/auth/reference/ui-components

Demonstrates a basic authentication flow using the `AuthView` component from Neon Auth UI. This example includes the necessary import for the `AuthView` component and the UI CSS. The `pathname` prop is set to 'sign-in' to initially display the sign-in form.

```javascript
import { AuthView } from '@neondatabase/neon-js/auth/react/ui';
import '@neondatabase/neon-js/ui/css';

function App() {
  return <AuthView pathname="sign-in" />;
}
```

--------------------------------

### Define New Table Creation Changelog

Source: https://neon.com/docs/guides/liquibase

This XML snippet defines a new changeset for a Liquibase changelog file. It includes a `createTable` statement to add a 'comments' table with specified columns, data types, and constraints, including foreign key relationships to 'posts' and 'authors' tables. Ensure to replace placeholder author and ID values.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:pro="http://www.liquibase.org/xml/ns/pro" xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.4.xsd
    http://www.liquibase.org/xml/ns/pro http://www.liquibase.org/xml/ns/pro/liquibase-pro-4.5.xsd">
    <changeSet author="alex" id="myIDNumber1234">
        <createTable tableName="comments">
            <column autoIncrement="true" name="comment_id" type="INTEGER">
                <constraints nullable="false" primaryKey="true" primaryKeyName="comments_pkey"/>
            </column>
            <column name="post_id" type="INTEGER">
                <constraints nullable="false" foreignKeyName="fk_comments_post_id" referencedTableName="posts" referencedColumnNames="post_id"/>
            </column>
            <column name="author_id" type="INTEGER">
                <constraints nullable="false" foreignKeyName="fk_comments_author_id" referencedTableName="authors" referencedColumnNames="author_id"/>
            </column>
            <column name="comment" type="TEXT"/>
            <column name="commented_date" type="TIMESTAMP" defaultValueComputed="CURRENT_TIMESTAMP"/>
        </createTable>
    </changeSet>
</databaseChangeLog>
```

--------------------------------

### Install Neon SDK for React

Source: https://neon.com/docs/auth/quick-start/react

Install the Neon SDK package into your React project using npm. This SDK provides essential authentication functions like signUp(), getSession(), and signOut().

```bash
cd my-app
npm install @neondatabase/neon-js
```

--------------------------------

### Get List of Open dblink Connections

Source: https://neon.com/docs/extensions/dblink

Retrieves a list of names for all currently open, named dblink connections within the current session. This function is useful for monitoring and managing active connections, aiding in troubleshooting or ensuring proper connection management.

```sql
SELECT * FROM dblink_get_connections();
```

--------------------------------

### Example RFC 3339 Timestamps for Branch Expiration

Source: https://neon.com/docs/guides/branch-expiration

Provides valid examples of RFC 3339 formatted timestamps for the `expires_at` parameter, demonstrating UTC, Eastern Standard Time, and Japan Standard Time formats. These examples adhere to the second-level precision and mandatory timezone requirement.

```text
2025-07-15T18:02:16Z
2025-07-15T18:02:16-05:00
2025-07-15T18:02:16+09:00
```

--------------------------------

### Create and Populate Neon Table (SQL)

Source: https://neon.com/docs/guides/cloudflare-hyperdrive

SQL commands to create a 'books_to_read' table with an ID, title, and author, and then insert sample data into it. This prepares the database for querying.

```sql
CREATE TABLE books_to_read (
 id SERIAL PRIMARY KEY,
 title TEXT,
 author TEXT
);

INSERT INTO books_to_read (title, author)
VALUES
    ('The Way of Kings', 'Brandon Sanderson'),
    ('The Name of the Wind', 'Patrick Rothfuss'),
    ('Coders at Work', 'Peter Seibel'),
    ('1984', 'George Orwell');
```

--------------------------------

### Install pgrag Extensions in Neon

Source: https://neon.com/docs/extensions/pgrag

Commands to enable unstable extensions and install the pgrag extension along with its model extensions in a Neon Postgres database. It ensures 'pgvector' is installed as a dependency.

```sql
SET neon.allow_unstable_extensions='true';
create extension if not exists rag cascade;
create extension if not exists rag_bge_small_en_v15 cascade;
create extension if not exists rag_jina_reranker_v1_tiny_en cascade;
```

--------------------------------

### Markdown Common Markup Examples

Source: https://neon.com/docs/community/contribution-guide

Provides examples of common Markdown syntax for creating links (external, internal, same-page), italics, bold text, and monospace text.

```markdown
External link markup: [Example.com website](https://www.example.com/)
Neon documentation page link: [Connection from any application](/docs/connect/connect-from-any-app)
Neon documentation same page link: [Code blocks](#code-blocks)
Italics markup: _italic_
Bold markup: **strong**
monospace: `backtick`
```

--------------------------------

### Schema Diff Output Example

Source: https://neon.com/docs/guides/schema-diff

An example of the diff output from the Neon API's `compare_schema` endpoint, showing added and removed lines in a schema.

```diff
--- a/neondb
+++ b/neondb
@@ -27,7 +27,8 @@
 CREATE TABLE public.playing_with_neon (
     id integer NOT NULL,
     name text NOT NULL,
-    value real
+    value real,
+    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
 );
```

--------------------------------

### Seed Database with Initial Data (Ruby)

Source: https://neon.com/docs/guides/rails-migrations

Populates the database with initial author and book records. It uses `find_or_create_by` to avoid duplicating data if the script is run multiple times. This Ruby script defines sample data for authors and books and associates them.

```ruby
# db/seeds.rb

# Find or create authors
authors_data = [
  {
    name: "J.R.R. Tolkien",
    bio: "The creator of Middle-earth and author of The Lord of the Rings."
  },
  {
    name: "George R.R. Martin",
    bio: "The author of the epic fantasy series A Song of Ice and Fire."
  },
  {
    name: "J.K. Rowling",
    bio: "The creator of the Harry Potter series."
  }
]

authors_data.each do |author_attrs|
  Author.find_or_create_by(name: author_attrs[:name]) do |author|
    author.bio = author_attrs[:bio]
  end
end

# Find or create books
books_data = [
  { title: "The Fellowship of the Ring", author_name: "J.R.R. Tolkien" },
  { title: "The Two Towers", author_name: "J.R.R. Tolkien" },
  { title: "The Return of the King", author_name: "J.R.R. Tolkien" },
  { title: "A Game of Thrones", author_name: "George R.R. Martin" },
  { title: "A Clash of Kings", author_name: "George R.R. Martin" },
  { title: "Harry Potter and the Philosopher's Stone", author_name: "J.K. Rowling" },
  { title: "Harry Potter and the Chamber of Secrets", author_name: "J.K. Rowling" }
]

books_data.each do |book_attrs|
  author = Author.find_by(name: book_attrs[:author_name])
  Book.find_or_create_by(title: book_attrs[:title], author: author)
end
```

--------------------------------

### Install Neon TypeScript SDK

Source: https://neon.com/docs/reference/typescript-sdk

Install the `@neondatabase/api-client` package into your project using npm, yarn, or pnpm. This command adds the SDK as a dependency for your application.

```bash
npm install @neondatabase/api-client
```

--------------------------------

### Install psycopg2 for PostgreSQL

Source: https://neon.com/docs/guides/sqlalchemy

Installs the psycopg2 Python library, a popular choice for running raw PostgreSQL queries. It's typically installed using the PIP package manager. This is a prerequisite for connecting to Neon from Python applications.

```bash
pip install psycopg2-binary
```

--------------------------------

### Start Compute Endpoint

Source: https://neon.com/docs/ai/ai-rules-neon-api

Manually starts a compute endpoint that is currently in an `idle` state. The endpoint is ready for connections once the start operation completes successfully.

```APIDOC
## POST /projects/{project_id}/endpoints/{endpoint_id}/start

### Description
Manually starts a compute endpoint that is currently in an `idle` state. The endpoint is ready for connections once the start operation completes successfully.

### Method
POST

### Endpoint
`/projects/{project_id}/endpoints/{endpoint_id}/start`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The unique identifier of the project.
- **endpoint_id** (string) - Required - The unique identifier of the compute endpoint.

### Request Example
```bash
curl -X 'POST' \
  'https://console.neon.tech/api/v2/projects/hidden-river-50598307/endpoints/ep-ancient-brook-ad5ea04d/start' \
  -H 'Accept: application/json' \
  -H "Authorization: Bearer $NEON_API_KEY"
```

### Response
#### Success Response (200)
- **endpoint** (object) - Details of the updated endpoint.
- **operations** (array) - A list of operations performed.

#### Response Example
```json
{
  "endpoint": {
    "host": "ep-ancient-brook-ad5ea04d.c-2.us-east-1.aws.neon.tech",
    "id": "ep-ancient-brook-ad5ea04d",
    "project_id": "hidden-river-50598307",
    "branch_id": "br-super-wildflower-adniii9u",
    "autoscaling_limit_min_cu": 0.25,
    "autoscaling_limit_max_cu": 1,
    "region_id": "aws-us-east-1",
    "type": "read_write",
    "current_state": "idle",
    "pending_state": "active",
    "settings": {
      "pg_settings": {}
    },
    "pooler_enabled": false,
    "pooler_mode": "transaction",
    "disabled": false,
    "passwordless_access": true,
    "last_active": "2025-09-11T06:28:26Z",
    "creation_source": "console",
    "created_at": "2025-09-10T12:15:04Z",
    "updated_at": "2025-09-11T06:51:25Z",
    "suspended_at": "2025-09-11T06:34:31Z",
    "proxy_host": "c-2.us-east-1.aws.neon.tech",
    "suspend_timeout_seconds": 0,
    "provisioner": "k8s-neonvm"
  },
  "operations": [
    {
      "id": "d4324b7e-0d73-467b-bc61-2f743a0c204b",
      "project_id": "hidden-river-50598307",
      "branch_id": "br-super-wildflower-adniii9u",
      "endpoint_id": "ep-ancient-brook-ad5ea04d",
      "action": "start_compute",
      "status": "running",
      "failures_count": 0,
      "created_at": "2025-09-11T07:51:18Z",
      "updated_at": "2025-09-11T07:51:18Z",
      "total_duration_ms": 0
    }
  ]
}
```
```

--------------------------------

### Install PostgreSQL in GitHub Actions

Source: https://neon.com/docs/guides/database-per-user

Installs a specified version of PostgreSQL into the GitHub Actions virtual environment. The version is determined by the `PG_VERSION` environment variable. This step ensures that PostgreSQL is available for subsequent database operations within the action.

```yaml
- name: Install PostgreSQL
        run: |
          sudo apt install -y postgresql-common
          yes '' | sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
          sudo apt install -y postgresql-${{ env.PG_VERSION }}
```

--------------------------------

### Run Encore Application Locally

Source: https://neon.com/docs/guides/encore

Starts the Encore application locally. Encore automatically provisions a local PostgreSQL database and makes the API accessible at http://localhost:4000.

```bash
encore run
```

--------------------------------

### Generate Neon DB Setup Script (JavaScript)

Source: https://neon.com/docs/guides/multitenancy

This Node.js script automates the generation of Drizzle ORM configuration files and GitHub Actions workflows for each Neon database project. It fetches project details, creates necessary directories, writes configuration and workflow files, and encrypts connection strings for secure GitHub secret storage. Dependencies include '@neondatabase/api-client', 'octokit', 'dotenv', and utility modules for encryption and templates.

```javascript
// src/scripts/generate.js

import { existsSync, mkdirSync, writeFileSync } from 'fs';
import { execSync } from 'child_process';
import { createApiClient } from '@neondatabase/api-client';
import { Octokit } from 'octokit';
import 'dotenv/config';

import { encryptSecret } from '../utils/encrypt-secret.js';
import { drizzleConfig } from '../templates/drizzle-config.js';
import { githubWorkflow } from '../templates/github-workflow.js';

const octokit = new Octokit({ auth: process.env.PERSONAL_ACCESS_TOKEN });
const neonApi = createApiClient({ apiKey: process.env.NEON_API_KEY });

const repoOwner = 'neondatabase-labs';
const repoName = 'neon-database-per-tenant-drizzle';
let secrets = [];

(async () => {
  // Ensure configs directory exists
  if (!existsSync('./configs')) {
    mkdirSync('./configs');
  }

  // Ensure .github/workflows directory exists
  if (!existsSync('./.github/workflows')) {
    mkdirSync('./.github/workflows', { recursive: true });
  }

  try {
    // Get all projects
    const response = await neonApi.listProjects();
    const { projects } = response.data;

    // Loop through each project
    for (const project of projects) {
      // Get connection details for the project
      const connectionDetails = await neonApi.getConnectionDetails({
        projectId: project.id,
        branchId: project.default_branch_id,
      });

      const { connection_string } = connectionDetails.data;

      // Create a drizzle config file for each project
      const configFileName = `${project.name.toLowerCase().replace(/\s+/g, '-')}.config.ts`;
      writeFileSync(`./configs/${configFileName}`, drizzleConfig(connection_string, project.name));

      // Create a GitHub workflow file for each project
      const workflowFileName = `${project.name.toLowerCase().replace(/\s+/g, '-')}.yml`;
      writeFileSync(
        `./.github/workflows/${workflowFileName}`,
        githubWorkflow(project.name, configFileName)
      );

      // Encrypt the connection string for GitHub Actions
      const publicKey = await octokit.request(
        'GET /repos/{owner}/{repo}/actions/secrets/public-key',
        {
          owner: repoOwner,
          repo: repoName,
        }
      );

      const secretName = `${project.name.toUpperCase().replace(/\s+/g, '_')}_CONNECTION_STRING`;
      const encryptedValue = await encryptSecret(connection_string, publicKey.data.key);

      secrets.push({
        secret_name: secretName,
        encrypted_value: encryptedValue,
        key_id: publicKey.data.key_id,
      });
    }

    // Output instructions for setting up GitHub secrets
    console.log('Generated config files and workflows for all projects.');
    console.log('\nTo set up GitHub secrets, run the following commands:');

    for (const secret of secrets) {
      console.log(`\nnpx octokit request PUT /repos/${repoOwner}/${repoName}/actions/secrets/${secret.secret_name} \
  -H "Accept: application/vnd.github.v3+json" \
  -f encrypted_value="${secret.encrypted_value}" \
  -f key_id="${secret.key_id}"`);
    }
  } catch (error) {
    console.error('Error generating files:', error);
  }
})();

```

--------------------------------

### Upgrade Neon CLI via npm

Source: https://neon.com/docs/reference/cli-install

Updates the Neon CLI to the latest version if it was initially installed using npm.

```bash
npm update -g neonctl
```

--------------------------------

### Check psycopg2 and libpq versions (Python)

Source: https://neon.com/docs/guides/django

This snippet retrieves and prints the installed version of the psycopg2 Python library and the underlying libpq library. It's useful for diagnosing version compatibility issues with Neon. Ensure you have psycopg2 installed (`pip install psycopg2-binary`) before running.

```python
import psycopg2
print("psycopg2 version:", psycopg2.__version__)
print("libpq version:", psycopg2._psycopg.libpq_version())
```

--------------------------------

### Add Sample Data Rows with AI Assistant (SQL)

Source: https://neon.com/docs/get-started/signing-up

This SQL snippet shows how to insert three new rows into the 'playing_with_neon' table with specific tech company names and values. This is an example of a query that can be generated or suggested by Neon's AI Assistant based on natural language prompts.

```sql
-- Text to SQL original prompt:
-- Add three more rows to the playing_with_neon table with tech company names
INSERT INTO public.playing_with_neon (name, value) VALUES
('Google', 1000.5),
('Apple', 1200.75),
('Microsoft', 950.25);
```

--------------------------------

### Next.js Package Installation for Neon Auth

Source: https://neon.com/docs/auth/migrate/from-legacy-auth

This command demonstrates how to uninstall the legacy Stack Auth packages and install the necessary packages for Neon Auth with Better Auth in a Next.js project.

```bash
npm uninstall @stackframe/stack
npm install @neondatabase/neon-auth-next @neondatabase/neon-auth-ui
```

--------------------------------

### pg_cron: Schedule Job Execution Every N Seconds

Source: https://neon.com/docs/extensions/pg_cron

Demonstrates scheduling a job to run at a fixed interval of every `n` seconds, a feature not typically available in standard cron. This example schedules a job to run every 10 seconds using the `cron.schedule` function with an interval string.

```sql
SELECT cron.schedule('every-10-seconds', '10 seconds', 'SELECT 1');
```

--------------------------------

### Example Neon Connection String

Source: https://neon.com/docs/reference/glossary

Demonstrates the structure of a typical connection string for a Neon Postgres database. This string includes authentication details, compute hostname with endpoint and region information, and database name. It also shows common connection parameters like sslmode and channel_binding.

```sql
postgresql://alex:AbC123dEf@ep-cool-darkness-123456.c-2.us-east-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require
```

--------------------------------

### Install Neon Toolkit with npm

Source: https://neon.com/docs/ai/ai-rules-neon-toolkit

Installs the Neon Toolkit package using npm, a popular JavaScript package manager. This is the primary method for incorporating the toolkit into Node.js projects.

```bash
npm install @neondatabase/toolkit
```

--------------------------------

### Find Shortest Path using pgr_dijkstra (SQL)

Source: https://neon.com/docs/extensions/postgis-related-extensions

Utilizes the pgrouting 'pgr_dijkstra' function to calculate the shortest path between a specified start node (2) and end node (4) in the 'road_network' table. The query considers undirected edges and returns the sequence of nodes, edges, and accumulated costs along the path.

```sql
SELECT
    seq, 
    node, 
    edge, 
    route.cost, 
    agg_cost, 
    rn.name AS road_name
FROM pgr_dijkstra(
    'SELECT id, source, target, cost FROM road_network',
    2, -- start node
    4, -- end node
    directed := false
) AS route
LEFT JOIN road_network rn ON route.edge = rn.id
ORDER BY seq;
```

--------------------------------

### CRUD Operations and Query Patterns

Source: https://neon.com/docs/data-api/get-started

Reference for common CRUD operations and query patterns supported by the Data API, including filters and modifiers.

```APIDOC
## Query Patterns Reference

### CRUD Operations

| Operation | Method | Example |
|---|---|---|
| Select | `.select()` | `client.from('posts').select('*')` |
| Insert | `.insert()` | `client.from('posts').insert({ title: 'New post' })` |
| Update | `.update()` | `client.from('posts').update({ title: 'Updated' }).eq('id', 1)` |
| Delete | `.delete()` | `client.from('posts').delete().eq('id', 1)` |
| RPC | `.rpc()` | `client.rpc('function_name', { param: 'value' })` |

### Filters

| Filter | Description | Example |
|---|---|---|
| `.eq(column, value)` | Equals | `.eq('status', 'published')` |
| `.neq(column, value)` | Not equals | `.neq('status', 'draft')` |
| `.gt(column, value)` | Greater than | `.gt('price', 100)` |
| `.lt(column, value)` | Less than | `.lt('price', 50)` |
| `.gte(column, value)` | Greater than or equal | `.gte('quantity', 1)` |
| `.lte(column, value)` | Less than or equal | `.lte('quantity', 10)` |
| `.like(column, pattern)` | Pattern match (case-sensitive) | `.like('title', '%hello%')` |
| `.ilike(column, pattern)` | Pattern match (case-insensitive) | `.ilike('title', '%hello%')` |
| `.is(column, value)` | Is null / not null | `.is('deleted_at', null)` |
| `.in(column, array)` | Value in array | `.in('status', ['active', 'pending'])` |

### Modifiers

| Modifier | Description | Example |
|---|---|---|
| `.order(column, options)` | Sort results | `.order('created_at', { ascending: false })` |
| `.limit(count)` | Limit rows returned | `.limit(10)` |
| `.single()` | Return single row | `.select('*').eq('id', 1).single()` |
```

--------------------------------

### Install a Postgres Extension using CREATE EXTENSION

Source: https://neon.com/docs/changelog/2024-07-05

This command is used to install a PostgreSQL extension, enabling additional functionality for your database. Ensure you have the necessary permissions and that the extension is supported by your Neon environment.

```sql
CREATE EXTENSION "uuid-ossp";

```

--------------------------------

### Install RedwoodSDK Dependencies

Source: https://neon.com/docs/guides/redwoodsdk

Installs the necessary Node.js dependencies for a RedwoodSDK project, including the Neon serverless driver.

```bash
cd my-redwood-app
npm install
npm install @neondatabase/serverless
```

--------------------------------

### Clone Neon Data API + Neon Auth Example

Source: https://neon.com/docs/guides/rls-tutorial

Clone the sample repository to demonstrate Neon Data API with Neon Auth. This is a prerequisite for setting up the application and its environment variables.

```bash
git clone https://github.com/neondatabase-labs/neon-data-api-neon-auth.git
```

--------------------------------

### Neon Authorization URL Example

Source: https://neon.com/docs/guides/oauth-integration

This is an example of the authorization URL used to initiate the OAuth 2.0 flow with Neon. It includes parameters like client ID, scopes, redirect URI, and state for managing the authorization process.

```url
https://oauth2.neon.tech/oauth2/auth?client_id=neon-experimental&scope=openid%20offline%20offline_access%20urn%3Aneoncloud%3Aprojects%3Acreate%20urn%3Aneoncloud%3Aprojects%3Aread%20urn%3Aneoncloud%3Aprojects%3Aupdate%20urn%3Aneoncloud%3Aprojects%3Adelete&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fapi%2Fauth%2Fcallback%2Fneon&grant_type=authorization_code&state=H58y-rSTebc3QmNbRjNTX9dL73-IyoU2T_WNievO9as&code_challenge=99XcbwOFU6iEsvXr77Xxwsk9I0GL4c4c4Q8yPIVrF_0&code_challenge_method=S256
```

--------------------------------

### Create and Populate Lego Database

Source: https://neon.com/docs/import/import-sample-data

Commands to create the Lego database, download its SQL source file, populate the database, and connect to it. This dataset contains information about LEGO sets.

```sql
CREATE DATABASE lego;
```

```bash
wget https://raw.githubusercontent.com/neondatabase/postgres-sample-dbs/main/lego.sql
```

```bash
psql -d "postgresql://[user]:[password]@[neon_hostname]/lego" -f lego.sql
```

```bash
psql postgresql://[user]:[password]@[neon_hostname]/lego
```

--------------------------------

### Generate SQLite Database from SQL File

Source: https://neon.com/docs/import/migrate-sqlite

Creates a SQLite database file named 'sample_library.db' by importing the schema and data from the 'seed.sql' file. This command-line operation requires the `sqlite3` tool to be installed.

```bash
sqlite3 sample_library.db < seed.sql
```

--------------------------------

### Install Packages for Better Auth (Terminal)

Source: https://neon.com/docs/auth/migrate/from-legacy-auth

This command sequence shows how to uninstall Stack Auth packages and install the necessary packages for Better Auth, including the core SDK and the UI components.

```bash
npm uninstall @stackframe/stack
npm install @neondatabase/neon-js @neondatabase/neon-auth-ui
```

--------------------------------

### Install Neon Auth and React Router Packages

Source: https://neon.com/docs/auth/quick-start/react-router-components

Installs the necessary packages for Neon authentication and React routing. This includes the Neon SDK and React Router DOM.

```bash
cd my-app
npm install @neondatabase/neon-js react-router-dom
```

--------------------------------

### Create Neon Project and Database using Python

Source: https://neon.com/docs/changelog/2025-01-10

This Python function utilizes the Neon client to create a new Neon project and a corresponding database. It handles potential exceptions during the creation process and returns the connection URI upon success. Dependencies include the 'neon_client' library.

```python
@tool("Create Neon Project and Database")
def create_database(project_name: str) -> str:
  """
  Creates a new Neon project. (this takes less than 500ms)
  Args:
      project_name: Name of the project to create
  Returns:
      the connection URI for the new project
  """
  try:
      project = neon_client.project_create(project={"name": project_name}).project
      connection_uri = neon_client.connection_uri(
          project_id=project.id, database_name="neondb", role_name="neondb_owner"
      ).uri
      return f"Project/database created, connection URI: {connection_uri}"
  except Exception as e:
      return f"Failed to create project: {str(e)}"
```

--------------------------------

### Install Neon Serverless Driver

Source: https://neon.com/docs/guides/grafbase

npm commands to initialize a Node.js project and install the '@neondatabase/serverless' package within the 'grafbase' directory.

```bash
cd ..
npm init -y
npm install @neondatabase/serverless
```

--------------------------------

### Install Neon Auth SDK for Next.js

Source: https://neon.com/docs/auth/quick-start/nextjs

Installs the Neon Auth SDK for Next.js applications using npm. This is a prerequisite for integrating Neon Auth.

```bash
npm install @neondatabase/neon-js
```

--------------------------------

### Install 'h3_postgis' Extension in PostgreSQL

Source: https://neon.com/docs/extensions/pg-extensions

This SQL command installs the 'h3_postgis' extension, which is often used in conjunction with PostGIS for geospatial indexing. It requires 'postgis' and 'postgis_raster' to be installed.

```sql
CREATE EXTENSION h3_postgis CASCADE;
```

--------------------------------

### Set Neon CLI Context

Source: https://neon.com/docs/reference/cli-quickstart

Configures the Neon CLI context by setting the project ID or both the organization and project IDs. This allows using CLI commands without specifying these IDs repeatedly. It also demonstrates creating named context files for different environments and switching between them.

```bash
neon set-context --project-id <your-project-id>
```

```bash
neon set-context --org-id <your-org-id> --project-id <your-project-id>
```

```bash
neon set-context --org-id <your-org-id> --project-id <your-project-id> --context-file dev_project
```

```bash
neon branches list --context-file Documents/dev_project
```

--------------------------------

### Example Neon Connection String

Source: https://neon.com/docs/guides/logical-replication-airbyte

An example of a direct connection string for a Neon database. This format is used when configuring the Airbyte Postgres source, ensuring no connection pooler is specified in the hostname.

```text
postgresql://alex:AbC123dEf@ep-cool-darkness-123456.us-east-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require

```

--------------------------------

### Install 'pg_roaringbitmap' Extension in PostgreSQL

Source: https://neon.com/docs/extensions/pg-extensions

This snippet demonstrates how to install the 'roaringbitmap' extension, which is an alias for 'pg_roaringbitmap'.

```sql
CREATE EXTENSION roaringbitmap;
```

--------------------------------

### Install Drizzle and Neon Serverless Dependencies

Source: https://neon.com/docs/guides/drizzle-migrations

Installs the necessary npm packages for using Drizzle ORM, Drizzle Kit for schema management, and the Neon serverless driver for connecting to the Neon Postgres database. It also installs dotenv for environment variable management.

```bash
cd neon-drizzle-guide && touch .env
npm install drizzle-orm @neondatabase/serverless
npm install -D drizzle-kit dotenv
```

--------------------------------

### SQL Code Block Example

Source: https://neon.com/docs/community/contribution-guide

A basic example of a Markdown code block demonstrating SQL syntax highlighting. Three backticks are used to delimit the code, followed by the language identifier `sql`.

```sql
```sql
SELECT * FROM posts ORDER BY id;
```
```

--------------------------------

### Install pgvector Extension in Neon

Source: https://neon.com/docs/ai/ai-google-colab

Installs the 'pgvector' extension in your connected Neon database. This extension is crucial for enabling vector storage and similarity search capabilities. The `CREATE EXTENSION IF NOT EXISTS` command ensures that the extension is installed only if it's not already present, preventing errors.

```sql
-- Execute this query to install the pgvector extension
cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
```

--------------------------------

### Install Neon Serverless Driver for Astro

Source: https://neon.com/docs/guides/astro

Installs the Neon serverless driver for Node.js applications using npm. This package enables efficient connection to Neon Postgres databases.

```bash
npm install @neondatabase/serverless
```

--------------------------------

### Install pgx_ulid Extension for Postgres 17 in Neon

Source: https://neon.com/docs/changelog/2025-01-31

Enables the installation of the pgx_ulid extension, version 0.2.0, for users running Postgres 17 on Neon. This extension provides ULID functionality.

```sql
CREATE EXTENSION pgx_ulid;
```

--------------------------------

### Create Elixir Project and Install Dependencies

Source: https://neon.com/docs/guides/elixir

This command-line snippet illustrates the process of creating a new Elixir project with supervision (`--sup`) using `mix` and then navigating into the project directory. It's the initial step before adding database dependencies.

```shell
mix new neon_elixir_quickstart --sup
cd neon_elixir_quickstart
```

--------------------------------

### Example EXPLAIN ANALYZE Output for Sequential Scan (SQL)

Source: https://neon.com/docs/postgresql/query-performance

This is an example of the output generated by `EXPLAIN ANALYZE` for a simple SELECT query. It details the query plan, including the type of scan (e.g., Parallel Seq Scan), estimated costs, actual execution times, and other statistics. This output is crucial for identifying performance issues, such as the need for an index.

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE id = '1';
                                                       QUERY PLAN
------------------------------------------------------------------------------------------------------------------------
 Gather  (cost=1000.00..59375.93 rows=1 width=9) (actual time=0.404..6479.494 rows=1 loops=1) 
   Workers Planned: 2
   Workers Launched: 2
   ->  Parallel Seq Scan on users  (cost=0.00..58375.83 rows=1 width=9) (actual time=4313.317..6472.025 rows=0 loops=3) 
         Filter: (id = 1)
         Rows Removed by Filter: 1833333
 Planning Time: 0.102 ms
 Execution Time: 6479.526 ms
```

--------------------------------

### Install Prisma Pulse Extension (npm)

Source: https://neon.com/docs/guides/logical-replication-prisma-pulse

This command installs the latest version of the Prisma Pulse extension, which is required to integrate real-time database change streaming with your Prisma client.

```bash
npm install @prisma/extension-pulse@latest
```

--------------------------------

### Sign In Methods (TypeScript)

Source: https://neon.com/docs/ai/ai-rules-neon-auth

Demonstrates low-level methods for signing in users via email/password or social providers (Google, GitHub). Includes specifying a callback URL for social sign-ins.

```typescript
// Email/password
await auth.signIn.email({
  email: "user@example.com",
  password: "securepassword",
});

// Social (Google, GitHub)
await auth.signIn.social({
  provider: "google", // or "github"
  callbackURL: "/dashboard",
});
```

--------------------------------

### SolidStart Server-Side Data Loading with Neon

Source: https://neon.com/docs/guides/solid-start

Demonstrates how to connect to a Neon database from a SolidStart application for server-side data loading. It uses the Neon serverless driver and the @solidjs/router to fetch and display the PostgreSQL version.

```typescript
import { neon } from "@neondatabase/serverless";
import { createAsync } from "@solidjs/router";

const getVersion = async () => {
    "use server";
    const sql = neon(`${process.env.DATABASE_URL}`);
    const response = await sql`SELECT version()`;
    const { version } = response[0];
    return version;
}

export const route = {
  load: () => getVersion(),
};

export default function Page() {
  const version = createAsync(() => getVersion());
  return <>{version()}</>;
}
```

--------------------------------

### Sign Up Method (TypeScript)

Source: https://neon.com/docs/ai/ai-rules-neon-auth

Low-level method to sign up a new user using email and password. This is suitable for backend environments or custom frontend implementations.

```typescript
await auth.signUp.email({
  email: "user@example.com",
  password: "securepassword",
  name: "John Doe", // Optional
});
```

--------------------------------

### Create Neon Project

Source: https://neon.com/docs/ai/ai-rules-neon-python-sdk

Creates a new Neon project with specified settings. Users can define project name, PostgreSQL version, region, and other configurations. The response contains details of the newly created project.

```python
import neon

# Create a new project with basic settings
new_project_response = neon.project_create(
    project={
        'name': 'my-new-python-project',
        'pg_version': 17
    }
)

# Create a project with more advanced settings
advanced_project_response = neon.project_create(
    project={
        'name': 'advanced-project',
        'pg_version': 16,
        'region_id': 'aws-us-east-1',
        'settings': {
            'allowed_ips': {'ips': ['0.0.0.0/0']},
            'block_public_connections': False
        }
    }
)
```

--------------------------------

### JavaScript SDK: Select Data from 'posts' Table

Source: https://neon.com/docs/data-api/get-started

This snippet shows how to select all columns from the 'posts' table using the Neon JavaScript SDK. This is a fundamental operation for retrieving data from your database.

```javascript
client.from('posts').select('*')
```

--------------------------------

### Create TypeScript/Node.js Project

Source: https://neon.com/docs/guides/drizzle

Commands to create a new project directory and initialize a Node.js project with a package.json file.

```bash
mkdir my-drizzle-neon-project
cd my-drizzle-neon-project
npm init -y
```

--------------------------------

### Monitor Neon Project Usage Metrics using cURL

Source: https://neon.com/docs/guides/embedded-postgres

This example demonstrates how to query consumption metrics for Neon projects over a specified date range and granularity. It retrieves data on active time, compute time, data written, data transferred, and storage size.

```shell
curl --request GET \
     --url 'https://console.neon.tech/api/v2/consumption_history/projects?limit=100&from=2024-11-01T00:00:00Z&to=2024-11-30T23:59:59Z&granularity=daily' \
     --header 'accept: application/json' \
     --header "authorization: Bearer $NEON_API_KEY"
```

--------------------------------

### Install Dependencies for Azure Blob Storage and Neon

Source: https://neon.com/docs/guides/azure-blob-storage

Installs the necessary Node.js packages for interacting with Azure Blob Storage, the Neon database, Hono web framework, and environment variable management.

```bash
npm install @azure/storage-blob @neondatabase/serverless @hono/node-server hono dotenv
```

--------------------------------

### Install Neon Serverless Driver for Deno

Source: https://neon.com/docs/guides/deno

Command to install the Neon serverless driver for Deno using the `deno add` command. This command adds the necessary dependency to your Deno project, enabling the use of Neon's serverless capabilities within your Deno application.

```shell
deno add jsr:@neon/serverless
```

--------------------------------

### Launch Exograph Development Server with Neon Connection

Source: https://neon.com/docs/guides/exograph

Starts the Exograph development server, connecting it to your Neon database using an environment variable. It will output URLs for the GraphQL Playground and endpoint.

```bash
EXO_POSTGRES_URL=<the connection string> exo dev
```

--------------------------------

### Start Neon Compute Endpoint using Curl

Source: https://neon.com/docs/ai/ai-rules-neon-api

Manually starts a compute endpoint that is currently in an 'idle' state. The endpoint becomes ready for connections upon successful completion of the start operation. This requires the project ID and endpoint ID as path parameters, and an authorization token in the header.

```bash
curl -X 'POST' \
  'https://console.neon.tech/api/v2/projects/{project_id}/endpoints/{endpoint_id}/start' \
  -H 'Accept: application/json' \
  -H "Authorization: Bearer $NEON_API_KEY"
```

--------------------------------

### Display Neon CLI Version

Source: https://neon.com/docs/reference/neon-cli

Shows the currently installed version number of the Neon CLI. This command is useful for verifying the installation and checking compatibility.

```bash
$ neon --version
1.15.0
```

--------------------------------

### Initialize Neon MCP Server with npx

Source: https://neon.com/docs/ai/connect-mcp-clients-to-neon

This command initializes the Neon MCP server integration. It handles authentication via OAuth, creates an API key, and configures VS Code to connect to Neon's remote MCP server. This is a foundational step for using Neon with AI tools.

```bash
npx neonctl@latest init

```

--------------------------------

### Neon CLI: Example Branch List Output

Source: https://neon.com/docs/changelog/2024-11-15

Example output from the `neon branches list` command, showcasing the 'Id', 'Name', 'Default', 'Current State', and 'Created At' fields for branches within a Neon project.

```bash
┌───────────────────────────┬──────┬─────────┬───────────────────────┬──────────────────────┐
│ Id                        │ Name │ Default │ Current State │ Created At           │
├───────────────────────────┼──────┼─────────┼───────────────┼──────────────────────┤
│ br-muddy-firefly-a7kzf0d4 │ main │ true    │ ready         │ 2024-10-30T14:59:57Z │
└───────────────────────────┴──────┴─────────┴───────────────┴──────────────────────┘
```

--------------------------------

### Command Line to Run Neon Import Script

Source: https://neon.com/docs/import/migrate-from-firebase

Demonstrates how to execute the Python script for importing data into Neon. It requires specifying the input directory and the Neon connection string as arguments.

```bash
python neon-import.py --input firestore_data --postgres "<neon-connection-string>"
```

--------------------------------

### Displaying pg_repack Version

Source: https://neon.com/docs/extensions/pg_repack

This command outputs the currently installed version of the `pg_repack` tool. It's useful for verifying installation and checking compatibility with specific database versions or features.

```bash
pg_repack --version
```

--------------------------------

### SQL Statement Summary for Read-Only Setup

Source: https://neon.com/docs/manage/database-access

Consolidated SQL statements for setting up a read-only role and user. This summary includes role creation, granting database and schema connect/usage privileges, and read-only table access for current and future tables.

```SQL
-- readonly role
CREATE ROLE readonly;
GRANT CONNECT ON DATABASE <database> TO readonly;
GRANT USAGE ON SCHEMA <schema> TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA <schema> TO readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA <schema> GRANT SELECT ON TABLES TO readonly;

-- User creation
CREATE USER readonly_user1 WITH PASSWORD '<password>';

-- Grant privileges to user
GRANT readonly TO readonly_user1;
```

--------------------------------

### Initialize Neon project with CLI

Source: https://neon.com/docs/reference/cli-init

Use the Neon CLI to initialize your application project with Neon. This command installs the Neon MCP (Model Context Protocol) Server, enabling your AI assistant to help set up your Neon integration. It handles authentication, API key creation, and editor configuration.

```bash
neon init
```

--------------------------------

### GraphQL Query Result Example

Source: https://neon.com/docs/extensions/pg_graphql

This is an example of the expected JSON response when querying the 'NewUsers' view via GraphQL. It shows a collection of users, each with an 'id', 'firstName', and 'lastName'.

```json
{
  "data": {
    "newUsersCollection": {
      "edges": [{ "node": { "id": 1, "lastName": "Doe", "firstName": "John" } }]
    }
  }
}
```

--------------------------------

### Enable Experimental Extensions in Neon

Source: https://neon.com/docs/extensions/pg-extensions

This command allows the installation of experimental extensions in Neon. Use this setting before attempting to install extensions like 'pg_mooncake' or 'pgrag'.

```sql
SET neon.allow_unstable_extensions='true';
```

--------------------------------

### Configure Auth.js with Neon and Resend

Source: https://neon.com/docs/guides/auth-authjs

Sets up Auth.js using the Neon Postgres adapter and Resend provider for email authentication. It requires `next-auth`, `@auth/pg-adapter`, and `@neondatabase/serverless`. Ensure DATABASE_URL is set in the environment.

```typescript
/// auth.ts

import NextAuth from 'next-auth';
import Resend from 'next-auth/providers/resend';
import PostgresAdapter from '@auth/pg-adapter';
import { Pool } from '@neondatabase/serverless';

// *DO NOT* create a `Pool` here, outside the request handler.

export const { handlers, auth, signIn, signOut } = NextAuth(() => {
  const pool = new Pool({ connectionString: process.env.DATABASE_URL });
  return {
    adapter: PostgresAdapter(pool),
    providers: [Resend({ from: 'Test <onboarding@resend.dev>' })],
  };
});
```

--------------------------------

### Start Neon Compute Endpoint

Source: https://neon.com/docs/ai/ai-rules-neon-python-sdk

Manually starts an idle Neon compute endpoint. This operation is useful for reactivating endpoints that have been suspended due to inactivity. It requires the project ID and endpoint ID.

```python
import neon

neon.endpoint_start(project_id='your-project-id', endpoint_id='ep-your-endpoint-id')
```

--------------------------------

### Run Quarkus Application

Source: https://neon.com/docs/guides/quarkus-jdbc

This command starts the Quarkus application in development mode, allowing you to test the integration with Neon. Access the application at http://localhost:8080/postgres/version to verify the connection.

```bash
quarkus dev
```

--------------------------------

### Example Query Plan Output

Source: https://neon.com/docs/ai/ai-vector-search-optimization

This is an example of the output from a query execution plan using an IVFFlat index. It shows the estimated and actual costs, rows, and time for a Limit and Index Scan operation, indicating that the search is utilizing an index named 'items_embedding_idx' and ordering results by vector distance. Planning and execution times are also provided.

```text
Limit  (cost=1971.50..1982.39 rows=100 width=173) (actual time=4.500..5.738 rows=100 loops=1)
  ->  Index Scan using items_embedding_idx on vectors  (cost=1971.50..3060.50 rows=10000 width=173) (actual time=4.499..5.726 rows=100 loops=1)
        Order By: (vec <-> '[0.0117, ... ,0.0866]'::vector)
Planning Time: 0.295 ms
Execution Time: 5.867 ms
```

--------------------------------

### Create and Link Netlify Project

Source: https://neon.com/docs/guides/netlify-functions

Commands to create a new directory for a Netlify project, navigate into it, and then create and link a new Netlify Site. This sets up the local project to be associated with a site in your Netlify account.

```bash
mkdir neon-netlify-example && cd neon-netlify-example
```

```bash
netlify sites:create
```

--------------------------------

### Install 'pg_search' Extension for Postgres 17

Source: https://neon.com/docs/extensions/pg-extensions

This SQL command installs the 'pg_search' extension, specifically for Postgres 17. It is used for full-text search capabilities.

```sql
CREATE EXTENSION pg_search;
```

--------------------------------

### Initializing Git Repository and Heroku Files

Source: https://neon.com/docs/guides/heroku

Initializes a new Git repository for the project and creates a `.gitignore` file to exclude `node_modules` and `.env` files from version control. It also sets the main branch to `main` and stages all current files for the initial commit.

```bash
git init && echo "node_modules" > .gitignore && echo ".env" >> .gitignore
git branch -M main
git add . && git commit -m "Initial commit"
```

--------------------------------

### Analyze LFC Metrics with EXPLAIN ANALYZE

Source: https://neon.com/docs/extensions/neon

Uses the `EXPLAIN ANALYZE` command with `FILECACHE` and `PREFETCH` options to view Local File Cache (LFC) hit/miss data and prefetch statistics. This method does not require the Neon extension to be installed.

```sql
EXPLAIN (ANALYZE,BUFFERS,PREFETCH,FILECACHE) SELECT COUNT(*) FROM pgbench_accounts;
-- Example Output:
--  Finalize Aggregate  (cost=214486.94..214486.95 rows=1 width=8) (actual time=5195.378..5196.034 rows=1 loops=1)
--    Buffers: shared hit=178875 read=143691 dirtied=128597 written=127346
--    Prefetch: hits=0 misses=1865 expired=0 duplicates=0
--    File cache: hits=141826 misses=1865
--    ->  Gather  (cost=214486.73..214486.94 rows=2 width=8) (actual time=5195.366..5196.025 rows=3 loops=1)
--          Workers Planned: 2
--          Workers Launched: 2
--          Buffers: shared hit=178875 read=143691 dirtied=128597 written=127346
--          Prefetch: hits=0 misses=1865 expired=0 duplicates=0
--          File cache: hits=141826 misses=1865
--          ->  Partial Aggregate  (cost=213486.73..213486.74 rows=1 width=8) (actual time=5187.670..5187.670 rows=1 loops=3)
--                Buffers: shared hit=178875 read=143691 dirtied=128597 written=127346
--                Prefetch: hits=0 misses=1865 expired=0 duplicates=0
--                File cache: hits=141826 misses=1865
--                ->  Parallel Index Only Scan using pgbench_accounts_pkey on pgbench_accounts  (cost=0.43..203003.02 rows=4193481 width=0) (actual time=0.574..4928.995 rows=3333333 loops=3)
--                      Heap Fetches: 3675286
--                      Buffers: shared hit=178875 read=143691 dirtied=128597 written=127346
--                      Prefetch: hits=0 misses=1865 expired=0 duplicates=0
--                      File cache: hits=141826 misses=1865
```

--------------------------------

### Install Node.js PostgreSQL Driver (npm)

Source: https://neon.com/docs/guides/aws-lambda

Installs the 'pg' package, a Node.js driver for PostgreSQL, which is necessary for the Lambda function to connect to the Neon database. This command should be run within the project directory.

```bash
npm install pg
```

--------------------------------

### Seed Neon Database with psql

Source: https://neon.com/docs/guides/stepzen

This command seeds your Neon database with data from an init.sql file. It requires a Neon connection string which includes user, password, hostname, and database name. Ensure the init.sql file is available in the same directory or provide the correct path.

```bash
psql postgresql://[user]:[password]@[neon_hostname]/[dbname] < init.sql
```

--------------------------------

### Example GraphQL Query Response

Source: https://neon.com/docs/guides/stepzen

A sample JSON response from the GraphQL API for the `getCustomerList` query, showing the structure of the returned data, including customer names and emails.

```json
{
  "data": {
    "getCustomerList": [
      {
        "name": "Lucas Bill",
        "email": "lucas.bill@example.com"
      },
      {
        // ...
      }
    ]
  }
}
```

--------------------------------

### Install `bufferutil` for `ws` Module Compatibility

Source: https://neon.com/docs/guides/prisma

Resolves `TypeError: bufferUtil.mask is not a function` by installing the `bufferutil` package. This dependency is required by the `ws` module when using `Client` and `Pool` constructs, particularly relevant when integrating with certain WebSocket-based services like Neon.

```bash
npm i -D bufferutil
```

--------------------------------

### Install .NET EF Tools Globally

Source: https://neon.com/docs/guides/entity-migrations

Installs the Entity Framework Core command-line tools globally, enabling the use of `dotnet ef` commands for generating and applying database migrations. This is a crucial step for managing schema changes within your Entity Framework project.

```bash
dotnet tool install --global dotnet-ef
```

--------------------------------

### Schema Diff Command Output Example

Source: https://neon.com/docs/changelog/2024-06-14

This example demonstrates the output of the Neon CLI's `schema-diff` command, illustrating the differences between two database schemas. The output uses a standard diff format to show added or removed lines, indicating changes in table structures, such as the addition of a new column.

```diff
--- Database: sales	(Branch: br-long-forest-a5glnuu4)
+++ Database: sales	(Branch: br-lucky-shape-a5fgfymm)
@@ -26,9 +26,10 @@

CREATE TABLE public.product (
    id integer NOT NULL,
    name text NOT NULL,
-    price numeric NOT NULL
+    price numeric NOT NULL,
+    description text NOT NULL
);

```

--------------------------------

### Create Vite React Project

Source: https://neon.com/docs/guides/cloudflare-pages

Command to create a new React project using Vite. This command initiates an interactive CLI prompt for project setup.

```bash
npm create vite@latest
```

--------------------------------

### Postgres date_trunc() Example: Extracting Year and Month for Sales

Source: https://neon.com/docs/functions/date_trunc

This SQL example shows how to use `date_trunc()` in conjunction with `EXTRACT()` to group sales data by year and month. It refines the previous example by providing a more readable output for analysis. This is beneficial for detailed financial reporting and historical trend analysis.

```sql
SELECT
  EXTRACT(YEAR FROM date_trunc('month', sale_date)) AS year,
  EXTRACT(MONTH FROM date_trunc('month', sale_date)) AS month,
  SUM(amount) AS total_sales
FROM sales
GROUP BY year, month
ORDER BY year, month;
```

--------------------------------

### Install Cloudinary and Neon Dependencies (Node.js)

Source: https://neon.com/docs/guides/cloudinary

Installs necessary Node.js packages for integrating Cloudinary and Neon. This includes the official Cloudinary SDK, the Neon serverless client, Hono for the web framework, and dotenv for environment variable management.

```bash
npm install cloudinary @neondatabase/serverless @hono/node-server hono dotenv
```

--------------------------------

### Neon Database Connection String Example

Source: https://neon.com/docs/guides/bemi

This is an example of a Neon database connection string. It includes details like username, password, host, database name, and SSL/channel binding requirements. This string is essential for configuring Bemi to connect to your Neon database.

```text
postgresql://neondb_owner:AbC123dEf@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

--------------------------------

### Install Elixir Dependencies

Source: https://neon.com/docs/guides/elixir

This shell command is used after updating the 'mix.exs' file to include new dependencies, such as 'postgrex'. It fetches and installs all the project's dependencies.

```shell
mix deps.get
```

--------------------------------

### Start anonymization

Source: https://neon.com/docs/workflows/data-anonymization

Starts or restarts the anonymization process for branches in `initialized`, `error`, or `anonymized` state. Applies all defined masking rules.

```APIDOC
## POST /projects/{project_id}/branches/{branch_id}/anonymize

### Description
Starts or restarts the anonymization process for branches in `initialized`, `error`, or `anonymized` state. Applies all defined masking rules.

### Method
POST

### Endpoint
`/projects/{project_id}/branches/{branch_id}/anonymize`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The ID of the project.
- **branch_id** (string) - Required - The ID of the branch.

### Response
#### Success Response (200)
- **branch_id** (string) - The ID of the branch.
- **project_id** (string) - The ID of the project.
- **state** (string) - The new state of the branch after anonymization.
- **status_message** (string) - A message indicating the result of the anonymization process.
- **created_at** (string) - The timestamp when the anonymization process was initiated.
- **updated_at** (string) - The timestamp when the anonymization process was last updated.

#### Response Example
```json
{
  "branch_id": "br-shiny-butterfly-w4393738",
  "project_id": "wild-sky-00366102",
  "state": "anonymized",
  "status_message": "Anonymization completed successfully (2 tables, 3 masking rules applied)",
  "created_at": "2025-11-01T14:01:39Z",
  "updated_at": "2025-11-01T14:01:41Z"
}
```
```

--------------------------------

### Create .NET Project and Add Packages

Source: https://neon.com/docs/guides/dotnet-npgsql

This snippet demonstrates how to create a new .NET console application and add the required NuGet packages for connecting to a PostgreSQL database and managing configuration. The packages include Npgsql for database interaction and configuration helpers.

```bash
dotnet new console -o NeonLibraryExample
cd NeonLibraryExample
dotnet add package Npgsql
dotnet add package Microsoft.Extensions.Configuration.Json
dotnet add package Microsoft.Extensions.Configuration.Binder
```

--------------------------------

### Install Node.js Dependencies for S3 and Neon

Source: https://neon.com/docs/guides/aws-s3

Installs the necessary Node.js packages for interacting with AWS S3 (client-side and request presigner), Neon database, and the Hono web framework. These are essential for building the backend endpoints for file uploads.

```bash
npm install @aws-sdk/client-s3 @aws-sdk/s3-request-presigner @neondatabase/serverless @hono/node-server hono dotenv
```

--------------------------------

### User Menu Example (React)

Source: https://neon.com/docs/auth/reference/ui-components

Shows how to implement a user menu dropdown using the `UserButton` component from Neon Auth UI. This component requires an `authClient` prop, which should be an instance of your Neon authentication client. The example assumes `authClient` is imported from a local module.

```javascript
import { UserButton } from '@neondatabase/neon-js/auth/react/ui';
import { authClient } from './auth';

function Header() {
  return (
    <header>
      <UserButton authClient={authClient} />
    </header>
  );
}
```

--------------------------------

### Start Neon MCP Server (No JSON Config)

Source: https://neon.com/docs/ai/neon-mcp-server

Use this command when your client does not use JSON for MCP server configuration, such as older Cursor versions. It starts the Neon MCP server using npx and requires your Neon API key.

```bash
npx -y @neondatabase/mcp-server-neon start <YOUR_NEON_API_KEY>
```

--------------------------------

### Direct HTTP Requests to Data API

Source: https://neon.com/docs/data-api/get-started

You can query the Data API directly using HTTP requests. Ensure you include the Authorization header with a valid JWT token containing a 'sub' claim for RLS policies.

```APIDOC
## GET /rest/v1

### Description
This endpoint allows direct querying of the Neon Data API using standard HTTP requests. Authentication is handled via a JWT token in the `Authorization` header.

### Method
GET

### Endpoint
`https://your-data-api-endpoint/rest/v1/<table>?queryParams`

### Parameters
#### Query Parameters
- **Authorization** (string) - Required - Bearer token for authentication. Example: `Bearer YOUR_JWT_TOKEN`
- **Content-Type** (string) - Required - Set to `application/json`

#### Other Query Parameters
Custom query parameters depend on the specific table and operations, e.g., `is_published=eq.true`, `order=created_at.desc`.

### Request Example
```curl
curl -X GET 'https://your-data-api-endpoint/rest/v1/posts?is_published=eq.true&order=created_at.desc' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json'
```

### Response
#### Success Response (200)
- **body** (JSON) - The response contains the data matching the query. The structure depends on the requested data.

#### Response Example
```json
{
  "example": "response body"
}
```
```

--------------------------------

### Serverless Project Dependencies (JSON)

Source: https://neon.com/docs/guides/aws-lambda

Shows the 'dependencies' section of a 'package.json' file after installing the 'pg' package. It lists 'pg' with its version, indicating the successful installation of the PostgreSQL driver.

```json
{
  "dependencies": {
    "pg": "^8.13.1"
  }
}
```

--------------------------------

### Install Previous pgvector Extension Version in Neon

Source: https://neon.com/docs/changelog/2025-01-31

Allows users to install a version of the pgvector extension that is one version behind the latest supported version in Neon. This is useful for compatibility or testing purposes.

```sql
CREATE EXTENSION vector VERSION '0.7.4';
```

--------------------------------

### Install Neon Serverless Driver

Source: https://neon.com/docs/ai/ai-rules-neon-serverless

Installs the Neon Serverless driver using npm or JSR. Note that versions 1.0.0 and higher require Node.js v19 or later. It also shows how to override the `pg` dependency for WebSocket-based connection pooling.

```bash
# Using npm
npm install @neondatabase/serverless

# Using JSR
bunx jsr add @neon/serverless
```

```json
"dependencies": {
  "pg": "npm:@neondatabase/serverless@^0.10.4"
},
"overrides": {
  "pg": "npm:@neondatabase/serverless@^0.10.4"
}
```

--------------------------------

### Install 'pg_cron' Extension in PostgreSQL

Source: https://neon.com/docs/extensions/pg-extensions

This snippet demonstrates the installation of the 'pg_cron' extension. It notes that 'pg_cron' jobs only run when compute is active, recommending it for 24/7 computes or when scale-to-zero is disabled.

```sql
CREATE EXTENSION pg_cron;
```

--------------------------------

### Neon `fetchOptions` Configuration (JavaScript)

Source: https://neon.com/docs/serverless/serverless-driver

Demonstrates how to use the `fetchOptions` to customize the underlying `fetch` call for database requests. This includes setting request priority and implementing fetch timeouts using `AbortController`.

```javascript
import { neon } from '@neondatabase/serverless';
const sql = neon(process.env.DATABASE_URL, { fetchOptions: { priority: 'high' } });
const rows = await sql`SELECT * FROM posts WHERE id = ${postId}`;

import { neon } from '@neondatabase/serverless';
const sql = neon(process.env.DATABASE_URL);
const abortController = new AbortController();
const timeout = setTimeout(() => abortController.abort('timed out'), 10000);
const rows = await sql('SELECT * FROM posts WHERE id = $1', [postId], {
  fetchOptions: { signal: abortController.signal },
}); // throws an error if no result received within 10s
clearTimeout(timeout);
```

--------------------------------

### Postgres: Use EXPLAIN for Query Analysis

Source: https://neon.com/docs/postgresql/query-reference

Provides examples of using the `EXPLAIN` and `EXPLAIN ANALYZE` commands in PostgreSQL to inspect query execution plans. `EXPLAIN` shows estimated plans, while `EXPLAIN ANALYZE` executes the query for actual performance metrics.

```sql
EXPLAIN SELECT * FROM employees WHERE department_id = 1;

EXPLAIN ANALYZE SELECT * FROM employees WHERE department_id = 1;
```

--------------------------------

### GraphQL Query to Retrieve All Todos

Source: https://neon.com/docs/guides/exograph

An example GraphQL query to fetch all todo items from the database. This shows how to retrieve data using the Exograph API.

```graphql
query {
  todos {
    id
    title
    completed
  }
}
```

--------------------------------

### Create Step-by-Step Instructions with Steps Component

Source: https://neon.com/docs/community/component-guide

The Steps component organizes content into numbered, step-by-step instructions. Each step is defined by an `<h2>` heading within the component. This component is useful for tutorials and guides requiring sequential actions.

```markdown
<Steps>

## Get a Glass

Take a clean glass from the cabinet or dish rack.

## Turn on Tap

Adjust the faucet to your preferred temperature and flow rate.

## Fill and Drink

Fill the glass to desired level and enjoy your water.

</Steps>
```

--------------------------------

### Install Node.js Dependencies for ImageKit and Neon Integration

Source: https://neon.com/docs/guides/imagekit

Installs the necessary Node.js packages for integrating ImageKit.io and Neon database. Includes the ImageKit SDK, Neon serverless client, Hono framework, and dotenv for environment variables.

```bash
npm install imagekit @neondatabase/serverless @hono/node-server hono dotenv
```

--------------------------------

### Initialize Serverless Project (serverless)

Source: https://neon.com/docs/guides/aws-lambda

Initiates the creation of a new serverless project. The command prompts for project type (AWS - Node.js - Starter) and project name ('aws-node-project'), then generates the project structure.

```bash
serverless
```

--------------------------------

### Example Output from NestJS App

Source: https://neon.com/docs/guides/nestjs

This is an example of the JSON output expected when running the NestJS application. It represents data fetched from the Postgres database, likely as an array of objects with 'id', 'name', and 'value' properties.

```json
[{"id":1,"name":"c4ca4238a0","value":0.39330545},{"id":2,"name":"c81e728d9d","value":0.14468245}]
```

--------------------------------

### Run Rails Development Server

Source: https://neon.com/docs/guides/ruby-on-rails

Command to start the Rails development server. This allows you to view the application in a web browser and verify the database connection.

```bash
bin/rails server -e development

```

--------------------------------

### Example Liquibase Changelog XML

Source: https://neon.com/docs/guides/liquibase-workflow

An example of the XML changelog file generated by the `generateChangeLog` command. This file details database schema changes such as table creation and constraint definitions. It is crucial to review this file for accuracy before deployment.

```xml
<?xml version="1.1" encoding="UTF-8" standalone="no"?>
<databaseChangeLog xmlns="http://www.liquibase.org/xml/ns/dbchangelog" xmlns:ext="http://www.liquibase.org/xml/ns/dbchangelog-ext" xmlns:pro="http://www.liquibase.org/xml/ns/pro" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog-ext http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-ext.xsd http://www.liquibase.org/xml/ns/pro http://www.liquibase.org/xml/ns/pro/liquibase-pro-latest.xsd http://www.liquibase.org/xml/ns/dbchangelog http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-latest.xsd">
    <changeSet author="alex (generated)" id="1697977416317-1">
        <createTable tableName="authors">
            <column autoIncrement="true" name="author_id" type="INTEGER">
                <constraints nullable="false" primaryKey="true" primaryKeyName="authors_pkey"/>
            </column>
            <column name="first_name" type="VARCHAR(100)"/>
            <column name="last_name" type="VARCHAR(100)"/>
            <column name="email" type="VARCHAR(255)">
                <constraints nullable="false"/>
            </column>
            <column name="bio" type="TEXT"/>
        </createTable>
    </changeSet>
    <changeSet author="alex (generated)" id="1697977416317-2">
        <createTable tableName="posts">
            <column autoIncrement="true" name="post_id" type="INTEGER">
                <constraints nullable="false" primaryKey="true" primaryKeyName="posts_pkey"/>
            </column>
            <column name="author_id" type="INTEGER"/>
            <column name="title" type="VARCHAR(255)">
                <constraints nullable="false"/>
            </column>
            <column name="content" type="TEXT"/>
            <column defaultValueComputed="CURRENT_TIMESTAMP" name="published_date" type="TIMESTAMP WITHOUT TIME ZONE"/>
        </createTable>
    </changeSet>
    <changeSet author="alex (generated)" id="1697977416317-3">
        <addUniqueConstraint columnNames="email" constraintName="authors_email_key" tableName="authors"/>
    </changeSet>
    <changeSet author="alex (generated)" id="1697977416317-4">
        <addForeignKeyConstraint baseColumnNames="author_id" baseTableName="posts" constraintName="posts_author_id_fkey" deferrable="false" initiallyDeferred="false" onDelete="NO ACTION" onUpdate="NO ACTION" referencedColumnNames="author_id" referencedTableName="authors" validate="true"/>
    </changeSet>
</databaseChangeLog>
```

--------------------------------

### Start Anonymization API

Source: https://neon.com/docs/changelog

Initiates the anonymization process for a branch if it hasn't started yet. This API is typically used after defining or updating masking rules.

```APIDOC
## POST /api/v2/projects/{project_id}/branch/{branch_id}/anonymize/start

### Description
Triggers the anonymization process for a specific branch, applying the currently set masking rules. This is useful if `start_anonymization` was set to false during branch creation.

### Method
POST

### Endpoint
`/api/v2/projects/{project_id}/branch/{branch_id}/anonymize/start`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The ID of the project.
- **branch_id** (string) - Required - The ID of the branch to start anonymization for.

#### Query Parameters
None

#### Request Body
None

### Request Example
(No request body for this endpoint)

### Response
#### Success Response (200)
- **status** (string) - The updated status of the anonymization process.

#### Response Example
```json
{
  "status": "processing"
}
```
```

--------------------------------

### Generate Types and Start Development Server

Source: https://neon.com/docs/guides/react-router

Commands to generate TypeScript types for routes and start the development server for a React Router application. These steps ensure type safety and allow for live development of the application connected to Neon.

```bash
npm run typecheck
npm run dev
```

--------------------------------

### Install Entity Framework and Npgsql Dependencies for .NET

Source: https://neon.com/docs/guides/entity-migrations

Installs the required NuGet packages for Entity Framework Core, its design-time components, the Npgsql provider for PostgreSQL, and the dotenv.net package for environment variable management. These are essential for interacting with a PostgreSQL database using Entity Framework in a .NET application.

```bash
dotnet add package Microsoft.EntityFrameworkCore
dotnet add package Microsoft.EntityFrameworkCore.Design
dotnet add package Microsoft.AspNetCore.App
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL
dotnet add package dotenv.net
```

--------------------------------

### NeonAuthUIProvider Setup

Source: https://neon.com/docs/auth/reference/ui-components

Wrap your app with NeonAuthUIProvider to enable the UI components. The provider accepts configuration props that control which features are available.

```APIDOC
## NeonAuthUIProvider Setup

### Description
Wrap your application with `NeonAuthUIProvider` to integrate Neon Auth UI components. This provider allows for configuration of various authentication features.

### Method
Component Setup (React)

### Endpoint
N/A (Client-side component)

### Parameters
#### Props
- **authClient** (`NeonAuthPublicApi`) - Required - Your Neon Auth client instance.
- **social.providers** (`SocialProvider[]`) - Optional - Array of OAuth providers to enable (e.g., Google, GitHub).
- **navigate** (`(href: string) => void`) - Optional - Navigation function for React Router.
- **Link** (`ComponentType`) - Optional - Custom Link component for routing.
- **localization** (`AuthLocalization`) - Optional - Customize text labels throughout the UI.
- **avatar** (`AvatarOptions`) - Optional - Avatar upload and display configuration.
- **additionalFields** (`AdditionalFields`) - Optional - Custom fields for sign-up and account settings.
- **credentials.forgotPassword** (`boolean`) - Optional - Enable forgot password flow.

### Request Example
```jsx
import { NeonAuthUIProvider } from '@neondatabase/neon-js/auth/react';
import '@neondatabase/neon-js/ui/css';
import { authClient } from './auth';

function App() {
  return (
    <NeonAuthUIProvider authClient={authClient}>
      {/* Your app components */}
    </NeonAuthUIProvider>
  );
}
```

### Response
(This is a React component setup, not an API response)

### Success Response
(N/A)

### Response Example
(N/A)
```

--------------------------------

### Enable Neon CLI Shell Completion

Source: https://neon.com/docs/reference/cli-quickstart

Enables autocompletion for Neon CLI commands and options in Bash and Zsh shells. It involves appending the completion script to the shell's configuration file and sourcing it.

```bash
neon completion >> ~/.bashrc
source ~/.bashrc
```

--------------------------------

### Import Neon Resources using Terraform `import` Blocks

Source: https://neon.com/docs/reference/terraform

This snippet demonstrates how to use Terraform's `import` blocks to bring existing Neon resources under management. It requires Terraform 1.5.0+ and the Neon provider. The example shows importing a project, branch, endpoint, role, and database, linking them via resource references after initial import.

```terraform
terraform {
  required_providers {
    neon = {
      source  = "kislerdm/neon"
    }
  }
}

provider "neon" {
  # API key configured via environment variable or directly
}

# --- Project Import ---
import {
  to = neon_project.my_app_project
  id = "damp-recipe-88779456" # Replace with your actual Project ID
}

resource "neon_project" "my_app_project" {
  # Minimal definition for import.
  # After import and plan, you'll populate this with actual/desired attributes.
}

# --- Development Branch Import ---
import {
  to = neon_branch.dev_branch
  id = "br-orange-bonus-a4v00wjl" # Replace with your actual Branch ID
}

resource "neon_branch" "dev_branch" {
  project_id = neon_project.my_app_project.id # Links to the TF resource
  name       = "feature-x-development"        # Should match existing branch name
}

# --- Development Branch Endpoint Import ---
import {
  to = neon_endpoint.dev_endpoint
  id = "ep-blue-cell-a4xzunwf" # Replace with your actual Endpoint ID
}

resource "neon_endpoint" "dev_endpoint" {
  project_id = neon_project.my_app_project.id
  branch_id  = neon_branch.dev_branch.id      # Links to the TF resource
}

# --- Application User Role on Development Branch Import ---
import {
  to = neon_role.app_user
  # ID format: project_id/branch_id/role_name
  id = "damp-recipe-88779456/br-orange-bonus-a4v00wjl/application_user"
}

resource "neon_role" "app_user" {
  project_id = neon_project.my_app_project.id
  branch_id  = neon_branch.dev_branch.id
  name       = "application_user"             # Must match existing role name
}

# --- Service Database on Development Branch Import ---
import {
  to = neon_database.service_db
  # ID format: project_id/branch_id/name
  id = "damp-recipe-88779456/br-orange-bonus-a4v00wjl/service_specific_database"
}

resource "neon_database" "service_db" {
  project_id = neon_project.my_app_project.id
  branch_id  = neon_branch.dev_branch.id
  name       = "service_specific_database"    # Must match existing database name
  owner_name = neon_role.app_user.name        # Links to the TF role resource
}
```

--------------------------------

### Create Phoenix Project with Mix

Source: https://neon.com/docs/guides/phoenix

This command demonstrates how to create a new Phoenix project using the `mix phx.new` task. It's the initial step for setting up a Phoenix application that will connect to Neon.

```bash
# install phx.new if you haven't already
# mix archive.install hex phx_new
mix phx.new hello
```

--------------------------------

### Create Pagila Database

Source: https://neon.com/docs/import/import-sample-data

This section details the process of setting up the 'pagila' database, which contains sample data for a fictional DVD rental store. It includes commands to create the database, download the schema, import data, and connect. A query is provided to identify the top 10 most popular film categories by rental frequency.

```sql
CREATE DATABASE pagila;

wget https://raw.githubusercontent.com/neondatabase/postgres-sample-dbs/main/pagila.sql

psql -d "postgresql://[user]:[password]@[neon_hostname]/pagila" -f pagila.sql

psql postgresql://[user]:[password]@[neon_hostname]/pagila

SELECT c.name AS category_name, COUNT(r.rental_id) AS rental_count
FROM category c
JOIN film_category fc ON c.category_id = fc.category_id
JOIN inventory i ON fc.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY c.name
ORDER BY rental_count DESC
LIMIT 10;
```

--------------------------------

### Install and Initialize Inngest Client (TypeScript/JavaScript)

Source: https://neon.com/docs/guides/trigger-serverless-functions

Installs the Inngest client using npm and provides a code snippet for initializing the Inngest client in a TypeScript or JavaScript file. This client is used to connect your serverless functions to Inngest.

```bash
npm i inngest
```

```typescript
// inngest/client.ts
import { Inngest } from 'inngest';

export const inngest = new Inngest({ id: 'neon-inngest-project' });
```

--------------------------------

### TypeORM Neon Connection String Examples

Source: https://neon.com/docs/guides/typeorm

Demonstrates how to format the DATABASE_URL for Neon connections. Includes a standard secure connection string and a pooled connection string for serverless applications. Appending '?sslmode=require&channel_binding=require' ensures secure communication.

```env
DATABASE_URL="postgresql://[user]:[password]@[neon_hostname]/[dbname]?sslmode=require&channel_binding=require"
```

```env
# Pooled Neon connection string
DATABASE_URL="postgresql://alex:AbC123dEf@ep-cool-darkness-123456-pooler.us-east-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require"
```

```env
DATABASE_URL="postgresql://[user]:[password]@[neon_hostname]/[dbname]?sslmode=require&channel_binding=require&connect_timeout=10"
```

--------------------------------

### Run Rails Server (Rails CLI)

Source: https://neon.com/docs/guides/rails-migrations

Starts the Rails development server, allowing you to access the application through a web browser. The default URL is typically http://localhost:3000.

```bash
rails server
```

--------------------------------

### Run Django Development Server (Shell)

Source: https://neon.com/docs/guides/django-migrations

Starts the Django development server to test the application. This command is executed in the project's root directory.

```shell
python manage.py runserver
```

--------------------------------

### MDX Component Hierarchy and Key Files

Source: https://neon.com/docs/community/component-architecture

Illustrates the flow from MDX content to rendered HTML via the component registry and React components. Highlights essential files for understanding the system.

```text
MDX Content
  ↓
Component Registry (sharedMdxComponents)
  ↓
React Components (src/components/pages/doc/)
  ↓
Rendered HTML
```

```text
Key files:
  * `sharedMdxComponents.js` - Main component registry
  * `src/components/pages/doc/` - Component implementations
  * `content/docs/` - MDX content files
  * `content/docs/shared-content/` - Shared template content
```

--------------------------------

### Seed Database with Example Data

Source: https://neon.com/docs/guides/prisma-migrations

Populates the database tables with initial example data for testing purposes. It defines an asynchronous function `seed` that creates authors and their associated books, ensuring the application can be tested effectively.

```javascript
// seed.js

import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

const seed = async () => {
  const authors = [
    {
      name: 'J.R.R. Tolkien',
      bio: 'The creator of Middle-earth and author of The Lord of the Rings.',
      books: {
        create: [
          { title: 'The Hobbit' },
          { title: 'The Fellowship of the Ring' },
          { title: 'The Two Towers' },
          { title: 'The Return of the King' },
        ],
      },
    },
    {
      name: 'George R.R. Martin',
      bio: 'The author of the epic fantasy series A Song of Ice and Fire.',
      books: {
        create: [{ title: 'A Game of Thrones' }, { title: 'A Clash of Kings' }],
      },
    },
    {
      name: 'J.K. Rowling',
      bio: 'The creator of the Harry Potter series.',
      books: {
        create: [
          { title: "Harry Potter and the Philosopher's Stone" },
          { title: 'Harry Potter and the Chamber of Secrets' },
        ],
      },
    },
  ];

  for (const author of authors) {
    await prisma.author.create({
      data: author,
    });
  }
};

async function main() {
  try {
    await seed();
    console.log('Seeding completed');
  } catch (error) {
    console.error('Error during seeding:', error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

main();
```

--------------------------------

### Generate and Apply Entity Framework Migrations (CLI)

Source: https://neon.com/docs/guides/dotnet-entity-framework

Commands to generate the initial database schema based on the defined Entity Framework models and apply these changes to the database. Requires the EF Core tooling to be installed.

```bash
dotnet ef migrations add InitialCreate
dotnet ef database update
```

--------------------------------

### Start Anonymization - API

Source: https://neon.com/docs/workflows/data-anonymization

Starts or restarts the anonymization process for branches that are in 'initialized', 'error', or 'anonymized' states. This operation applies all defined masking rules to the specified branch.

```curl
curl -X POST \
  'https://console.neon.tech/api/v2/projects/{project_id}/branches/{branch_id}/anonymize' \
  -H 'Authorization: Bearer $NEON_API_KEY' \
  -H 'Accept: application/json'
```

```json
{
  "branch_id": "br-shiny-butterfly-w4393738",
  "project_id": "wild-sky-00366102",
  "state": "anonymized",
  "status_message": "Anonymization completed successfully (2 tables, 3 masking rules applied)",
  "created_at": "2025-11-01T14:01:39Z",
  "updated_at": "2025-11-01T14:01:41Z"
}
```

--------------------------------

### Create and Restore Employees Database

Source: https://neon.com/docs/import/import-sample-data

Commands to create the Employees database, download its compressed SQL source file, restore the data using pg_restore, and connect to it. This database contains employee and department information.

```sql
CREATE DATABASE employees;
\c employees
CREATE SCHEMA employees;
```

```bash
wget https://raw.githubusercontent.com/neondatabase/postgres-sample-dbs/main/employees.sql.gz
```

```bash
pg_restore -d postgresql://[user]:[password]@[neon_hostname]/employees -Fc employees.sql.gz -c -v --no-owner --no-privileges
```

```bash
psql postgresql://[user]:[password]@[neon_hostname]/employees
```

--------------------------------

### Create Neon Database with SQL

Source: https://neon.com/docs/import/import-sample-data

This snippet demonstrates how to create a new database within Neon using a SQL command. This is a prerequisite for loading sample data into a dedicated database.

```sql
CREATE DATABASE periodic_table;
```

--------------------------------

### Configure Zed (Preview) for Neon Context Servers

Source: https://neon.com/docs/ai/connect-mcp-clients-to-neon

Configures Neon as a Context Server within the preview version of Zed. This involves specifying the server name and the command to execute the Neon MCP remote, followed by OAuth authorization. Note: This feature is in preview.

```text
Name: Neon
Command: npx -y mcp-remote https://mcp.neon.tech/mcp

```

--------------------------------

### Create and Populate Table in Neon

Source: https://neon.com/docs/guides/netlify-functions

SQL commands to create a 'favorite_coffee_blends' table and insert initial data into it within a Neon Postgres database. This sets up the necessary structure for the example application.

```sql
CREATE TABLE favorite_coffee_blends (
    id SERIAL PRIMARY KEY,
    name TEXT,
    origin TEXT,
    notes TEXT
);
```

```sql
INSERT INTO favorite_coffee_blends (name, origin, notes)
VALUES
    ('Morning Joy', 'Ethiopia', 'Citrus, Honey, Floral'),
    ('Dark Roast Delight', 'Colombia', 'Rich, Chocolate, Nutty'),
    ('Arabica Aroma', 'Brazil', 'Smooth, Caramel, Fruity'),
    ('Robusta Revolution', 'Vietnam', 'Strong, Bold, Bitter');
```

--------------------------------

### GET /consumption/projects

Source: https://neon.com/docs/manage/orgs-api-consumption

Retrieves global consumption totals for all projects in an organization. Include `org_id` to get account-level metrics.

```APIDOC
## GET /consumption/projects

### Description
Retrieves global consumption totals for all projects within an organization. To obtain account-level metrics, include the `org_id` in the request.

### Method
GET

### Endpoint
`/consumption/projects`

### Parameters
#### Query Parameters
- **from** (string) - Required - The start date for the consumption data.
- **to** (string) - Required - The end date for the consumption data.
- **granularity** (string) - Required - The level of detail for the consumption metrics (e.g., 'hourly', 'daily').
- **org_id** (string) - Required - The organization ID to retrieve account-level metrics.

### Request Example
```bash
curl --request GET \
     --url 'https://console.neon.tech/api/v2/consumption_history/account?from=2024-06-30T15%3A30%3A00Z&to=2024-07-02T15%3A30%3A00Z&granularity=hourly&org_id=org-ocean-art-12345678' \
     --header 'accept: application/json' \
     --header 'authorization: Bearer $ORG_API_KEY'
```

### Response
#### Success Response (200)
- **periods** (array) - An array of consumption periods.
  - **period_id** (string) - Identifier for the consumption period.
  - **period_plan** (string) - The plan associated with the period.
  - **period_start** (string) - The start time of the period.
  - **consumption** (array) - An array of consumption metrics within the period.
    - **timeframe_start** (string) - The start time of the consumption timeframe.
    - **timeframe_end** (string) - The end time of the consumption timeframe.
    - **active_time_seconds** (integer) - The total active time in seconds.
    - **compute_time_seconds** (integer) - The total compute time in seconds.
    - **written_data_bytes** (integer) - The total data written in bytes.
    - **synthetic_storage_size_bytes** (integer) - The synthetic storage size in bytes.

#### Response Example
```json
{
  "periods": [
    {
      "period_id": "random-period-abcdef",
      "period_plan": "scale",
      "period_start": "2024-06-01T00:00:00Z",
      "consumption": [
        {
          "timeframe_start": "2024-06-30T15:00:00Z",
          "timeframe_end": "2024-06-30T16:00:00Z",
          "active_time_seconds": 147452,
          "compute_time_seconds": 43215,
          "written_data_bytes": 111777920,
          "synthetic_storage_size_bytes": 41371988928
        },
        {
          "timeframe_start": "2024-06-30T16:00:00Z",
          "timeframe_end": "2024-06-30T17:00:00Z",
          "active_time_seconds": 147468,
          "compute_time_seconds": 43223,
          "written_data_bytes": 110483584,
          "synthetic_storage_size_bytes": 41467955616
        }
      ]
    }
  ]
}
```
```

--------------------------------

### Install Python Libraries for Neon Postgres Connection

Source: https://neon.com/docs/guides/python

Installs necessary Python libraries for connecting to Neon Postgres: psycopg (v3), psycopg2-binary, asyncpg, and python-dotenv for environment variable management.

```bash
pip install "psycopg[binary]" psycopg2-binary asyncpg python-dotenv
```

--------------------------------

### Integrate Neon Serverless Driver with Deno

Source: https://neon.com/docs/changelog/2023-03-30

This snippet demonstrates how to install and import the Neon serverless driver for use within a Deno environment. It replaces the standard Postgres driver installation with the Neon-specific package and shows the correct import statement.

```bash
npm install @neondatabase/serverless
```

```typescript
import { Pool } from 'npm:@neondatabase/serverless';
```

--------------------------------

### Install and Query pg_stat_statements Extension in Neon

Source: https://neon.com/docs/postgresql/query-performance

This snippet demonstrates how to install the pg_stat_statements extension in Neon using a SQL CREATE EXTENSION statement. It also shows how to query the 'pg_stat_statements' view to understand the collected performance metrics, which aids in identifying query performance issues.

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

```sql
SELECT
  userid,
  query,
  calls,
  total_exec_time / 1000 AS total_seconds,
  mean_exec_time AS avg_ms
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 100;
```

--------------------------------

### GitHub Action: Automate PostgreSQL Backups with pg_dump and AWS S3

Source: https://neon.com/docs/guides/multitenancy

This GitHub Actions workflow automates PostgreSQL backups using `pg_dump`. It installs PostgreSQL, configures AWS credentials, sets up S3 paths, creates backup files with GZIP compression, enforces a retention policy to delete old backups, and uploads the backup to an S3 bucket. The workflow is triggered on a schedule or manually. It relies on GitHub secrets for sensitive information like database URLs and AWS credentials.

```yaml
// .github/workflows/acme-analytics-prod.yml

name: acme-analytics-prod

on:
  schedule:
    - cron: '0 0 * * *' # Runs at midnight UTC
  workflow_dispatch:

jobs:
  db-backup:
    runs-on: ubuntu-latest

    permissions:
      id-token: write

    env:
      RETENTION: 7
      DATABASE_URL: ${{ secrets.ACME_ANALYTICS_PROD }}

      IAM_ROLE: ${{ secrets.IAM_ROLE }}
      AWS_ACCOUNT_ID: ${{ secrets.AWS_ACCOUNT_ID }}
      S3_BUCKET_NAME: ${{ secrets.S3_BUCKET_NAME }}
      AWS_REGION: 'us-east-1'
      PG_VERSION: '16'

    steps:
      - name: Install PostgreSQL
        run: |
          sudo apt install -y postgresql-common
          yes '' | sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
          sudo apt install -y postgresql-${{ env.PG_VERSION }}

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ env.AWS_ACCOUNT_ID }}:role/${{ env.IAM_ROLE }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Set file, folder and path variables
        run: |
          GZIP_NAME="$(date +'%B-%d-%Y@%H:%M:%S').gz"
          FOLDER_NAME="${{ github.workflow }}"
          UPLOAD_PATH="s3://${{ env.S3_BUCKET_NAME }}/${{ env.FOLDER_NAME }}/${{ env.GZIP_NAME }}"

          echo "GZIP_NAME=${{ env.GZIP_NAME }}" >> $GITHUB_ENV
          echo "FOLDER_NAME=${{ env.FOLDER_NAME }}" >> $GITHUB_ENV
          echo "UPLOAD_PATH=${{ env.UPLOAD_PATH }}" >> $GITHUB_ENV

      - name: Create folder if it doesn't exist
        run: |
          if ! aws s3api head-object --bucket ${{ env.S3_BUCKET_NAME }} --key "${{ env.FOLDER_NAME }}/" 2>/dev/null;
            aws s3api put-object --bucket ${{ env.S3_BUCKET_NAME }} --key "${{ env.FOLDER_NAME }}/"
          fi

      - name: Run pg_dump
        run: |
          /usr/lib/postgresql/${{ env.PG_VERSION }}/bin/pg_dump ${{ env.DATABASE_URL }} | gzip > "${{ env.GZIP_NAME }}"

      - name: Empty bucket of old files
        run: |
          THRESHOLD_DATE=$(date -d "-${{ env.RETENTION }} days" +%Y-%m-%dT%H:%M:%SZ)
          aws s3api list-objects --bucket ${{ env.S3_BUCKET_NAME }} --prefix "${{ env.FOLDER_NAME }}/" --query "Contents[?LastModified<'${THRESHOLD_DATE}'] | [?ends_with(Key, '.gz')].{{Key: Key}}" --output text | while read -r file;
            aws s3 rm "s3://${{ env.S3_BUCKET_NAME }}/${file}"
          done

      - name: Upload to bucket
        run: |
          aws s3 cp "${{ env.GZIP_NAME }}" "${{ env.UPLOAD_PATH }}" --region ${{ env.AWS_REGION }}

```

--------------------------------

### Create Neon Project and Connect with psql

Source: https://neon.com/docs/reference/cli-projects

Creates a new Neon project and automatically opens a psql connection to it. This is a convenient way to start interacting with a new project immediately after creation.

```bash
neon project create --psql
```

--------------------------------

### Configuring WebSocket Constructor for Node.js Environments

Source: https://neon.com/docs/serverless/serverless-driver

Provides an example of configuring the WebSocket constructor for environments like Node.js that lack built-in WebSocket support. It imports `Pool` and `neonConfig` from `@neondatabase/serverless` and sets `neonConfig.webSocketConstructor` to the `ws` library.

```javascript
import { Pool, neonConfig } from '@neondatabase/serverless';
import ws from 'ws';
neonConfig.webSocketConstructor = ws;
```

--------------------------------

### Compare PostgreSQL Connection Times (Shell)

Source: https://neon.com/docs/connect/connection-latency

Compares connection times to a Neon database with and without the `sslnegotiation=direct` parameter. This helps in evaluating the performance impact of the optimization. It requires `psql` command-line tool and a valid Neon endpoint.

```shell
time psql "postgresql://neondb_owner@your-neon-endpoint/neondb?sslmode=require&channel_binding=require" -c "SELECT version();"

```

```shell
time psql "postgresql://neondb_owner@your-neon-endpoint/neondb?sslmode=require&channel_binding=require&sslnegotiation=direct" -c "SELECT version();"

```

--------------------------------

### Initialize Liquibase Project

Source: https://neon.com/docs/guides/liquibase-workflow

Initializes a new Liquibase project in the specified directory. This command creates a pre-populated Liquibase properties file, essential for managing database schema changes. Ensure you have Liquibase installed and Java configured.

```bash
liquibase init project --project-dir ~/blogdb
```

--------------------------------

### Start Collecting Recommendations with online_advisor

Source: https://neon.com/docs/extensions/online_advisor

After enabling the online_advisor extension, this command activates data collection by calling the `get_executor_stats()` function. Running this function initiates the process of gathering query workload data necessary for generating recommendations. Subsequent calls can be made to view the collected statistics.

```sql
SELECT get_executor_stats();

```

--------------------------------

### Creating a Heroku Application

Source: https://neon.com/docs/guides/heroku

Creates a new application on Heroku named `neon-heroku-example` using the Heroku CLI. This command also automatically sets up a Git remote named `heroku` for pushing code to the Heroku application.

```bash
heroku create neon-heroku-example
```

--------------------------------

### Create ASP.NET Core Web Application with EF Core DbContext

Source: https://neon.com/docs/guides/entity-migrations

Sets up a basic ASP.NET Core web application, configures the Entity Framework Core DbContext, and defines API endpoints for fetching authors and books.

```csharp
# Program.cs

using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using GuideNeonEF;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddDbContext<ApplicationDbContext>();

var app = builder.Build();

app.UseRouting();
app.MapGet("/authors", async (ApplicationDbContext db) =>
    await db.Authors.ToListAsync());
app.MapGet("/books/{authorId}", async (int authorId, ApplicationDbContext db) =>
    await db.Books.Where(b => b.AuthorId == authorId).ToListAsync());

app.Run();

```

--------------------------------

### Update Get Consumption Metrics API

Source: https://neon.com/docs/changelog/2024-10-25

The `Get consumption metrics for each project` API now supports specifying `project_id` as a comma-separated list in addition to an array, offering more flexibility for filtering.

```APIDOC
## GET /metrics/consumption

### Description
Retrieves consumption metrics for projects. The `project_id` parameter can now accept a comma-separated list of IDs.

### Method
GET

### Endpoint
/metrics/consumption

### Parameters
#### Query Parameters
- **project_ids** (string) - Optional - A comma-separated list or an array of project IDs to filter the results. If omitted, all projects are included.

### Request Example
#### Array format
`?project_ids=cold-poetry-09157238&project_ids=quiet-snow-71788278`

#### Comma-separated list format
`?project_ids=cold-poetry-09157238,quiet-snow-71788278`

### Response
#### Success Response (200)
- **metrics** (array) - An array of consumption metrics objects.
  - **project_id** (string) - The ID of the project.
  - **usage** (object) - Usage details.
    - **storage_bytes** (integer) - Storage used in bytes.
    - **compute_seconds** (integer) - Compute time in seconds.
```

--------------------------------

### Initialize Medusa App with Neon Database

Source: https://neon.com/docs/guides/medusajs

This command initializes a new Medusa project and configures it to connect to a Neon Postgres database. It requires the Neon database connection string as an argument. Ensure you replace 'YOUR_NEON_CONNECTION_STRING' with your actual connection string.

```bash
npx create-medusa-app@latest --db-url "YOUR_NEON_CONNECTION_STRING"
```

--------------------------------

### Fetch Books by Author using cURL

Source: https://neon.com/docs/guides/entity-migrations

Example cURL command to retrieve books for a specific author from the /books/{authorId} endpoint.

```bash
curl http://localhost:5000/books/1
```

--------------------------------

### Fetch All Authors using cURL

Source: https://neon.com/docs/guides/entity-migrations

Example cURL command to retrieve all authors from the /authors endpoint of the running web application.

```bash
curl http://localhost:5000/authors
```

--------------------------------

### Managing Publications with Specific Tables in PostgreSQL

Source: https://neon.com/docs/guides/logical-replication-tips

Demonstrates how to correctly create and manage PostgreSQL publications for specific tables, avoiding issues with 'FOR ALL TABLES' publications. This is crucial for scenarios where tables need to be added or dropped from a publication over time.

```sql
ALTER PUBLICATION test_publication ADD TABLE users;
ERROR:  publication "my_publication" is defined as FOR ALL TABLES
DETAIL:  Tables cannot be added to or dropped from FOR ALL TABLES publications.

ALTER PUBLICATION test_publication DROP TABLE products;
ERROR:  publication "my_publication" is defined as FOR ALL TABLES
DETAIL:  Tables cannot be added to or dropped from FOR ALL TABLES publications.

CREATE PUBLICATION my_publication FOR TABLE users;

CREATE PUBLICATION my_publication FOR TABLE users, departments;
```

--------------------------------

### Update SDK Initialization for Better Auth (React SPA)

Source: https://neon.com/docs/auth/migrate/from-legacy-auth

This example shows the initialization of the `authClient` for a React Single Page Application (SPA) using Better Auth. It replaces the Stack Auth client app configuration with the new `authClient` wired to your Neon Auth URL.

```js
// src/stack.ts (Before)
import { StackClientApp } from '@stackframe/stack';

export const stackClientApp = new StackClientApp({
  urls: {
    signIn: '/sign-in',
    signUp: '/sign-up',
  },
});
```

```js
// src/auth.ts (After - Example)
import NeonAuth from '@neondatabase/neon-js';

export const authClient = new NeonAuth.Auth({
  // Replace with your Neon Auth URL
  neonAuthUrl: 'https://your-neon-auth-url.com',
});
```

--------------------------------

### Configure Claude Desktop for Neon MCP Server

Source: https://neon.com/docs/ai/connect-mcp-clients-to-neon

Adds Neon's MCP server configuration to Claude Desktop's `claude_desktop_config.json` file. This setup requires specifying the command to run the Neon MCP remote and its arguments, followed by OAuth authorization.

```json
{
  "mcpServers": {
    "Neon": {
      "command": "npx",
      "args": ["-y", "mcp-remote@latest", "https://mcp.neon.tech/mcp"]
    }
  }
}

```

--------------------------------

### React SPA Auth Client Setup for Neon Auth

Source: https://neon.com/docs/ai/ai-rules-neon-auth

Configures the authentication client for a React Single Page Application (SPA) using Neon Auth. It specifies the auth URL and uses a React adapter for integration.

```typescript
import { createAuthClient } from "@neondatabase/auth";
import { BetterAuthReactAdapter } from "@neondatabase/auth/react/adapters";

const authClient = createAuthClient(
  import.meta.env.VITE_NEON_AUTH_URL,
  { adapter: BetterAuthReactAdapter() }
);
```

--------------------------------

### Install psycopg for Neon Database Connection in Python Notebook

Source: https://neon.com/docs/ai/ai-azure-notebooks

This command installs the `psycopg` adapter, a crucial Python library for interacting with PostgreSQL databases. It enables your Python applications, including Azure Data Studio notebooks, to connect to and manipulate data in your Neon database.

```python
!pip install psycopg
```

--------------------------------

### Create Project

Source: https://neon.com/docs/ai/ai-rules-neon-python-sdk

Creates a new Neon project with specified settings. You can configure details such as the project name, PostgreSQL version, and region.

```APIDOC
## POST /projects

### Description
Creates a new Neon project.

### Method
POST

### Endpoint
/projects

### Parameters
#### Request Body
- **project** (object, required) - A dictionary containing project settings.
  - **name** (string, optional) - A name for the project.
  - **pg_version** (integer, optional) - Postgres version (e.g., 17).
  - **region_id** (string, optional) - Region ID (e.g., `aws-us-east-1`).
  - **settings** (object, optional) - Project settings.
    - **allowed_ips** (object, optional)
      - **ips** (list[string], optional)
      - **protected_branches_only** (boolean, optional)
    - **enable_logical_replication** (boolean, optional)
    - **maintenance_window** (object, optional)
      - **weekdays** (list[integer], required)
      - **start_time** (string, required)
      - **end_time** (string, required)
    - **block_public_connections** (boolean, optional)
    - **block_vpc_connections** (boolean, optional)
  - **branch** (object, optional)
  - **autoscaling_limit_min_cu** (float, optional)
  - **autoscaling_limit_max_cu** (float, optional)
  - **provisioner** (string, optional)
  - **default_endpoint_settings** (object, optional)
    - **pg_settings** (object, optional)
    - **pgbouncer_settings** (object, optional)
    - **autoscaling_limit_min_cu** (float, optional)
    - **autoscaling_limit_max_cu** (float, optional)
    - **suspend_timeout_seconds** (integer, optional)
  - **store_passwords** (boolean, optional)
  - **history_retention_seconds** (integer, optional)
  - **org_id** (string, optional)

### Request Example
```json
{
  "project": {
    "name": "my-new-python-project",
    "pg_version": 17,
    "settings": {
      "block_public_connections": true
    }
  }
}
```

### Response
#### Success Response (200)
- **project** (object) - The created project details.
  - **data_storage_bytes_hour** (integer)
  - **data_transfer_bytes** (integer)
  - **written_data_bytes** (integer)
  - **compute_time_seconds** (integer)
  - **active_time_seconds** (integer)
  - **cpu_used_sec** (integer)
  - **id** (string)
  - **platform_id** (string)
  - **region_id** (string)
  - **name** (string)
  - **provisioner** (string)
  - **pg_version** (integer)
  - **proxy_host** (string)
  - **branch_logical_size_limit** (integer)
  - **branch_logical_size_limit_bytes** (integer)
  - **store_passwords** (boolean)
  - **creation_source** (string)
  - **history_retention_seconds** (integer)
  - **created_at** (string)
  - **updated_at** (string)
  - **consumption_period_start** (string)
  - **consumption_period_end** (string)
  - **owner_id** (string)
  - **default_endpoint_settings** (object, optional)
  - **settings** (object, optional)
  - **maintenance_starts_at** (string, optional)
  - **synthetic_storage_size** (integer, optional)
  - **quota_reset_at** (string, optional)
  - **owner** (object, optional)
  - **compute_last_active_at** (string, optional)
  - **org_id** (string, optional)

#### Response Example
```json
{
  "project": {
    "data_storage_bytes_hour": 0,
    "data_transfer_bytes": 0,
    "written_data_bytes": 0,
    "compute_time_seconds": 0,
    "active_time_seconds": 0,
    "cpu_used_sec": 0,
    "id": "<project_id>",
    "platform_id": "<platform_id>",
    "region_id": "aws-us-east-1",
    "name": "my-new-python-project",
    "provisioner": "aws",
    "pg_version": 17,
    "proxy_host": "<proxy_host>",
    "branch_logical_size_limit": 32212254720,
    "branch_logical_size_limit_bytes": 32212254720,
    "store_passwords": false,
    "creation_source": "api",
    "history_retention_seconds": 604800,
    "created_at": "2024-01-01T11:00:00Z",
    "updated_at": "2024-01-01T11:00:00Z",
    "consumption_period_start": "2024-01-01T00:00:00Z",
    "consumption_period_end": "2024-01-01T23:59:59Z",
    "owner_id": "<owner_id>",
    "settings": {
      "block_public_connections": true
    },
    "org_id": "<org_id>"
  }
}
```
```

--------------------------------

### Create Sample Table in Neon (SQL)

Source: https://neon.com/docs/guides/logical-replication-airbyte-snowflake

Creates a sample table named 'playing_with_neon' with sample data for testing replication. This is useful if you need data to practice with.

```sql
CREATE TABLE IF NOT EXISTS playing_with_neon(id SERIAL PRIMARY KEY, name TEXT NOT NULL, value REAL);
INSERT INTO playing_with_neon(name, value)
SELECT LEFT(md5(i::TEXT), 10), random() FROM generate_series(1, 10) s(i);
```

--------------------------------

### Apply Accepted Recommendations with online_advisor

Source: https://neon.com/docs/extensions/online_advisor

This snippet shows how to apply recommendations for indexes and statistics generated by the online_advisor extension. It includes commands to create indexes concurrently and safely, followed by `VACUUM (ANALYZE)` to update table statistics. This ensures that the recommended optimizations are implemented effectively.

```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_customer_date ON orders(customer_id, order_date);
VACUUM (ANALYZE) orders;

```

--------------------------------

### Set up New Hono.js Project

Source: https://neon.com/docs/guides/drizzle-migrations

Command to create a new Node.js project using Hono.js, a web framework. This is the initial step for building the application that will interact with the Neon database.

```bash
npm create hono@latest neon-drizzle-guide
```

--------------------------------

### Create Database via Neon API using cURL

Source: https://neon.com/docs/data-api/troubleshooting

This example demonstrates how to create a new database using the Neon API with cURL. It specifies the project ID, branch ID, and the desired database name, ensuring correct permissions are set for Data API usage.

```bash
curl -X POST "https://console.neon.tech/api/v2/projects/${projectId}/branches/${branchId}/databases" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $NEON_API_KEY" \
  -d '{
    "database": {
      "name": "your_database_name"
    }
  }'
```

--------------------------------

### Install Neon Serverless Driver via npm

Source: https://neon.com/docs/changelog/2024-04-19

This snippet shows how to install the Neon serverless driver package from the JavaScript Registry (JSR) using npm. This package is compatible with various JavaScript runtimes and backward compatible with npm.

```bash
npm install @neon/serverless
```

--------------------------------

### Connect with Read-Only User (psql)

Source: https://neon.com/docs/manage/database-access

This is an example of how to connect to a Neon database using the psql client with a read-only user. It includes the connection string format with user credentials, host, and database name, along with SSL and channel binding requirements.

```Bash
psql postgresql://readonly_user1:AbC123dEf@ep-cool-darkness-123456.us-west-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require
```

--------------------------------

### Start Local Development Server with Wrangler

Source: https://neon.com/docs/guides/cloudflare-workers

Start a local development server for your Cloudflare Worker using the Wrangler CLI. This command simulates the Cloudflare Workers environment locally, allowing you to test your application before deployment. It will use environment variables defined in `.dev.vars`.

```bash
npx wrangler dev
```

--------------------------------

### Create Instagres Database URL (CLI)

Source: https://neon.com/docs/introduction/roadmap

This allows users to instantly generate a Postgres database URL without signup. It's accessible via the command line, providing a quick way to get a Neon database up and running.

```bash
npx instagres
```

--------------------------------

### Example OTLP 404 Error for Metrics

Source: https://neon.com/docs/guides/opentelemetry

This is an example log entry indicating a 404 error when the OpenTelemetry Collector attempts to export metrics to an observability platform. This error typically occurs when the platform does not accept data on the '/v1/metrics' path appended to the base URL.

```json
Exporting failed. Dropping data. {"error": "not retryable error: Permanent error: rpc error: code = Unimplemented desc = error exporting items, request to https://example.com/otlp/v1/metrics responded with HTTP Status Code 404"}
```

--------------------------------

### Create and Navigate StepZen Workspace Directory

Source: https://neon.com/docs/guides/stepzen

Commands to create a new local directory for your StepZen workspace and navigate into it. This is the initial step before importing your database schema.

```bash
mkdir stpezen
cd stepzen
```

--------------------------------

### Crosstab3 Function Example for Text Pivot Tables

Source: https://neon.com/docs/extensions/tablefunc

Demonstrates how to use the crosstab3 function to pivot product sales data. This function automatically defines output columns as TEXT and requires the source query to be ordered. The example shows casting sales to TEXT and the importance of the ORDER BY clause for correct category mapping.

```sql
SELECT *
FROM crosstab3(
  $$SELECT product, quarter, sales::TEXT  -- Cast sales to TEXT
    FROM product_sales_long
    ORDER BY 1, 2$$  -- Important: ORDER BY row_id, category
);
```

--------------------------------

### Create TypeScript/Node.js Project for Kysely and Neon

Source: https://neon.com/docs/guides/kysely

Initializes a new Node.js project, installs TypeScript and related tools, and configures tsconfig.json for modern module resolution and strict type checking. It also sets the package.json to use ES modules.

```shell
mkdir my-kysely-neon-project
cd my-kysely-neon-project
npm init -y
npm install -D typescript tsx @types/node
npx tsc --init
```

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "allowImportingTsExtensions": true,
    "noEmit": true
  }
}
```

```json
{
  "type": "module"
}
```

--------------------------------

### Implement Authentication Routes

Source: https://neon.com/docs/guides/auth-authjs

Sets up the dynamic route for Auth.js to handle all authentication-related requests (GET, POST). It imports handlers from the main `auth.ts` configuration file.

```typescript
/// app/api/auth/[...nextauth]/route.ts

import { handlers } from '@/auth';

export const { GET, POST } = handlers;
```

--------------------------------

### PostgreSQL Advanced Example: Top N per Group using rank()

Source: https://neon.com/docs/functions/window-rank

Illustrates how to find the top N rows within each group using the rank() window function within a subquery. This example finds the top 2 most expensive products in each category.

```sql
WITH products AS (
    SELECT * 
    FROM (
        VALUES 
            (1, 'A', 100),
            (2, 'A', 80),
            (3, 'B', 200),
            (4, 'B', 180),
            (5, 'B', 150),
            (6, 'C', 120)
    ) AS t(product_id, category, price)
)
SELECT *
FROM (
    SELECT 
        product_id, 
        category, 
        price, 
        rank() OVER (PARTITION BY category ORDER BY price DESC) AS rank
    FROM products
) ranked
WHERE rank <= 2;
```

--------------------------------

### Test Book API Endpoint with Curl

Source: https://neon.com/docs/guides/micronaut-kotlin

Demonstrates how to test the 'get all books' API endpoint using `curl`. This command sends an HTTP GET request to the specified URL (`http://localhost:8080/books`) to retrieve book data from the application.

```bash
# Get all books
curl http://localhost:8080/books
```

--------------------------------

### Create Ephemeral Neon Branches using Docker Run

Source: https://neon.com/docs/local/neon-local

This command starts the Neon Local container to create ephemeral database branches. When the container starts, a new branch is created, and it's deleted when the container stops. Requires API key, project ID, and a parent branch ID.

```bash
docker run \
  --name db \
  -p 5432:5432 \
  -e NEON_API_KEY=<your_neon_api_key> \
  -e NEON_PROJECT_ID=<your_neon_project_id> \
  -e PARENT_BRANCH_ID=<parent_branch_id> \
  neondatabase/neon_local:latest
```

--------------------------------

### List Databases (psql command)

Source: https://neon.com/docs/reference/compatibility

The `\l` command, when executed in `psql` or the Neon SQL Editor, lists all databases along with their encoding and collation information. This provides a quick overview of database configurations without writing a full SQL query.

```sql
\l
```

--------------------------------

### Install pgvector Extension (Python)

Source: https://neon.com/docs/ai/ai-azure-notebooks

This code snippet installs the 'pgvector' extension on a Neon database using Python. It requires a database cursor object to execute the SQL command. This enables the database to function as a vector store.

```python
# Execute this query to install the pgvector extension
cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
```

--------------------------------

### Neon Connection String with SSL Mode

Source: https://neon.com/docs/connect/connect-securely

This example demonstrates how to construct a Neon connection string, appending the 'sslmode' parameter to enforce SSL/TLS encryption. The 'verify-full' mode is recommended for the highest level of security.

```sql
postgresql://[user]:[password]@[neon_hostname]/[dbname]?sslmode=verify-full
```

--------------------------------

### Install and Use app.build CLI for Python Projects

Source: https://neon.com/docs/changelog/2025-07-18

This command installs and runs the app.build CLI, an open-source agent that transforms AI-generated code into full-stack applications on Neon. The `--template=python` flag specifies that you want to build a data app or ML dashboard using Python.

```bash
npx @app.build/cli --template=python

```

--------------------------------

### Load Sample Data into Neon Database with PSQL

Source: https://neon.com/docs/import/import-sample-data

This command uses the `psql` client to load a SQL script file into a specified Neon database. Replace the placeholder connection string with your actual Neon database connection details.

```bash
psql -d "postgresql://[user]:[password]@[neon_hostname]/periodic_table" -f periodic_table.sql
```

--------------------------------

### Creating and Querying Sensor Log Table with Cube Metrics

Source: https://neon.com/docs/extensions/cube

This example shows how to create a table to store sensor logs with multidimensional metrics represented by the `CUBE` data type. It includes an `INSERT` statement and a query to filter logs based on ranges in specific dimensions (temperature and humidity).

```sql
CREATE TABLE sensor_log (
  ts TIMESTAMPTZ NOT NULL,
  device_id INT,
  metrics CUBE -- e.g., (temperature, humidity, pressure)
);

INSERT INTO sensor_log (ts, device_id, metrics) VALUES
  (NOW(), 101, '(22.5, 55.2, 1013.1)');

-- Find logs where temperature (1st dim) was between 20-25
-- and humidity (2nd dim) was between 50-60
SELECT * FROM sensor_log
WHERE metrics <@ cube(array[20,50,-1e6], array[25,60,1e6]); -- We keep 3rd dim a large range
```

--------------------------------

### Retrieve Next Page of Project Consumption History (curl)

Source: https://neon.com/docs/guides/consumption-metrics

This example shows how to paginate through project consumption history results. By including the 'cursor' value obtained from a previous response in the request URL, you can fetch the subsequent set of records. This ensures efficient retrieval of large datasets.

```curl
curl --request GET \
     --url 'https://console.neon.tech/api/v2/consumption_history/projects?cursor=divine-tree-77657175&limit=10&from=2024-06-30T00%3A00%3A00Z&to=2024-07-02T00%3A00%3A00Z&granularity=daily' \
     --header 'accept: application/json' \
     --header 'authorization: Bearer $NEON_API_KEY'
```

--------------------------------

### Grant Permissions for Neon Data API Schema Access

Source: https://neon.com/docs/data-api/get-started

This SQL snippet demonstrates how to grant necessary permissions for the 'authenticated' role to access and manipulate objects within the 'public' schema. It covers usage, table permissions for existing and future tables, and sequence permissions for identity columns. Ensure IP Allow is disabled before proceeding.

```sql
-- Schema usage
GRANT USAGE ON SCHEMA public TO authenticated;

-- For existing tables
GRANT SELECT, UPDATE, INSERT, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;

-- For future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLES TO authenticated;

-- For sequences (for identity columns)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;
```

--------------------------------

### Neon PostgreSQL Connection String Example

Source: https://neon.com/docs/guides/logical-replication-estuary-flow

This is an example of a direct connection string for a Neon PostgreSQL database, suitable for use with Estuary Flow. It specifies the role, password, host, port, database, and SSL mode. Ensure you use a direct connection, not a pooled one.

```plaintext
postgres://cdc_role:AbC123dEf@ep-cool-darkness-123456.us-east-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require
```

--------------------------------

### Soundex and Difference Function Examples

Source: https://neon.com/docs/extensions/fuzzystrmatch

Demonstrates the usage of `soundex` and `difference` functions from the fuzzystrmatch extension. The `soundex` function returns a phonetic code for a string, and `difference` calculates the similarity between the Soundex codes of two strings. These examples illustrate how to compare names that sound alike but are spelled differently.

```sql
SELECT soundex('Smith'), soundex('Smythe');
-- s530, s530

SELECT difference('Smith', 'Smythe');
-- 4

SELECT soundex('John'), soundex('Jon');
-- J500, J500

SELECT difference('John', 'Jon');
-- 4

SELECT soundex('Robert'), soundex('Rupert');
-- R163, R163

SELECT difference('Anne', 'Andrew');
-- 2 (A500 vs A536)
```

--------------------------------

### JavaScript SDK: Insert Data into 'posts' Table

Source: https://neon.com/docs/data-api/get-started

This snippet demonstrates how to insert a new record into the 'posts' table using the Neon JavaScript SDK. You provide an object containing the column names and their values.

```javascript
client.from('posts').insert({ title: 'New post' })
```

--------------------------------

### Initialize Alembic Database Migrations

Source: https://neon.com/docs/guides/reflex

Initializes the Alembic migration environment for the Reflex project. This command should be run in the project directory to set up the necessary files for managing database schema changes.

```bash
reflex db init
```

--------------------------------

### Generate Java Maven Project with Neon JDBC

Source: https://neon.com/docs/guides/java

Creates a new Java project using the Maven quickstart archetype and configures it to use the PostgreSQL JDBC driver and dotenv-java library for Neon database connectivity.

```bash
mvn archetype:generate \
    -DarchetypeGroupId=org.apache.maven.archetypes \
    -DarchetypeArtifactId=maven-archetype-quickstart \
    -DarchetypeVersion=1.5 \
    -DgroupId=com.neon.quickstart \
    -DartifactId=neon-java-jdbc \
    -DinteractiveMode=false
```

```bash
cd neon-java-jdbc
```

```xml
<dependencies>
  <dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <version>42.7.3</version>
  </dependency>
  <dependency>
    <groupId>io.github.cdimascio</groupId>
    <artifactId>dotenv-java</artifactId>
    <version>3.2.0</version>
  </dependency>
</dependencies>
```

```bash
mvn clean compile
```

--------------------------------

### Install pg_tiktoken Extension

Source: https://neon.com/docs/extensions/pg_tiktoken

This SQL command installs the pg_tiktoken extension in your Neon database. Ensure you are connected to your Neon instance via the SQL Editor or a client like psql. This extension provides tokenization capabilities for text data.

```sql
CREATE EXTENSION pg_tiktoken
```

--------------------------------

### Create NOLOGIN Role using SQL

Source: https://neon.com/docs/manage/roles

Demonstrates how to create a role with the `NOLOGIN` attribute using SQL in Neon.

```APIDOC
## Create NOLOGIN Role with SQL

### Description
This example shows the SQL syntax to create a role that cannot authenticate (NOLOGIN) but can be granted privileges.

### Method
SQL Statement

### Endpoint
N/A (executed via SQL client)

### Parameters
None directly for the command itself, parameters are part of the SQL syntax.

### Request Example
```sql
CREATE ROLE my_role NOLOGIN;
```

### Response
#### Success Response
A role named 'my_role' is created with the NOLOGIN attribute.

#### Response Example
(No direct JSON response, confirmation via SQL client or subsequent queries)
```

--------------------------------

### Create React App with Vite

Source: https://neon.com/docs/auth/quick-start/react

This command uses npm to create a new React application scaffolded with Vite, a fast build tool. Ensure you have Node.js and npm installed to use this command.

```bash
npm create vite@latest my-app -- --template react
```

--------------------------------

### Password Authentication Failed Error Example

Source: https://neon.com/docs/connect/connection-errors

This error indicates a problem with your connection information or driver support for Server Name Indication (SNI). The provided example shows the typical error message, including the username and connection details.

```plaintext
ERROR:  password authentication failed for user '<user_name>' connection to server at "ep-billowing-fun-123456.us-west-2.aws.neon.tech" (12.345.67.89), port 5432 failed: ERROR:  connection is insecure (try using `sslmode=require&channel_binding=require`)
```

--------------------------------

### Success: Unique Constraint on Partitioned Table Including Partition Key Column

Source: https://neon.com/docs/extensions/pg_partman

Shows a successful example of adding a unique constraint to a partitioned table by including the 'activity_time' column, which is a partition key. This ensures uniqueness across all partitions.

```sql
ALTER TABLE user_activities ADD CONSTRAINT unique_activity UNIQUE (activity_id, activity_time);
```

--------------------------------

### Check psycopg2 and libpq versions in Django Shell

Source: https://neon.com/docs/guides/django

This snippet shows how to start a Django shell and execute Python commands to check the versions of the `psycopg2` driver and its underlying `libpq` client library. This is useful for troubleshooting connection issues related to SNI support.

```bash
# Start a Django shell
python3 manage.py shell
```

```python
import psycopg2

print(f"psycopg2 version: {psycopg2.__version__}")
print(f"libpq version: {psycopg2.libpq_version()}")
```

--------------------------------

### Create Encore Application

Source: https://neon.com/docs/guides/encore

Creates a new Encore application using the Encore CLI. Users select a language (e.g., TypeScript) and a template, then navigate to the application directory.

```bash
encore app create my-neon-app
cd my-neon-app
```

--------------------------------

### Example ChatGPT Message Structure and Token Limits

Source: https://neon.com/docs/extensions/pg_tiktoken

Shows a typical JSON structure for ChatGPT 'messages' parameter, highlighting token limits. It includes example system, user, and assistant messages, with annotations for model and system token counts, and the resulting maximum history tokens for a gpt-3.5-turbo model.

```json
{
  "model": "gpt-3.5-turbo", // MODEL_MAX_TOKENS = 4096
  "messages": [
         {"role": "system", "content": "You are a helpful assistant."}, // NUM_SYSTEM_TOKENS = 6
         {"role": "user", "content": "Who won the world series in 2020?"},
         {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
         {"role": ...}
         .
         .
         .
         {"role": "user", "content": "Great! Have a great day."}
    ]
}
```

--------------------------------

### Markdown Frontmatter Example

Source: https://neon.com/docs/community/contribution-guide

Demonstrates the structure of Markdown frontmatter, including essential attributes like 'title', 'subtitle', and 'enableTableOfContents'. It also shows optional attributes like 'redirectFrom' and 'updatedOn'.

```markdown
---
title: Connect a Next.js application to Neon
subtitle: Set up a Neon project and connect from a Next.js application
enableTableOfContents: true
redirectFrom:
  - /docs/content/<old_directory_name>
updatedOn: '2023-10-07T12:25:27.662Z'
---
```

--------------------------------

### GET /projects/{project_id}/endpoints

Source: https://neon.com/docs/ai/ai-rules-neon-api

Retrieves a list of all compute endpoints for the specified project. This endpoint is useful for getting an overview of all available compute resources within a project.

```APIDOC
## GET /projects/{project_id}/endpoints

### Description
Retrieves a list of all compute endpoints for the specified project.

### Method
GET

### Endpoint
`/projects/{project_id}/endpoints`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The unique identifier of the project.

### Request Example
```bash
curl 'https://console.neon.tech/api/v2/projects/hidden-river-50598307/endpoints' \
  -H 'Accept: application/json' \
  -H "Authorization: Bearer $NEON_API_KEY"
```

### Response
#### Success Response (200)
- **endpoints** (array) - A list of compute endpoint objects.

#### Response Example
```json
{
  "endpoints": [
    {
      "host": "ep-round-morning-adtpn2oc.c-2.us-east-1.aws.neon.tech",
      "id": "ep-round-morning-adtpn2oc",
      "project_id": "hidden-river-50598307",
      "branch_id": "br-long-feather-adpbgzlx",
      "autoscaling_limit_min_cu": 0.25,
      "autoscaling_limit_max_cu": 2,
      "region_id": "aws-us-east-1",
      "type": "read_write",
      "current_state": "active",
      "settings": {
        "pg_settings": {}
      },
      "pooler_enabled": false,
      "pooler_mode": "transaction",
      "disabled": false,
      "passwordless_access": true,
      "last_active": "2025-09-11T06:28:33Z",
      "creation_source": "console",
      "created_at": "2025-09-10T12:14:58Z",
      "updated_at": "2025-09-11T06:28:34Z",
      "started_at": "2025-09-11T06:28:23Z",
      "proxy_host": "c-2.us-east-1.aws.neon.tech",
      "suspend_timeout_seconds": 0,
      "provisioner": "k8s-neonvm",
      "compute_release_version": "9509"
    }
  ]
}
```
```

--------------------------------

### Create React Router Project and Add Neon Dependencies

Source: https://neon.com/docs/guides/react-router

Commands to create a new React Router project and install the necessary Neon serverless driver and a Postgres client library like postgres.js or node-postgres. This sets up the foundational structure for your application and its database connectivity.

```bash
npx create-react-router@latest with-react-router --yes
cd with-react-router
npm install @neondatabase/serverless
```

--------------------------------

### Create Partitioned Table Structure

Source: https://neon.com/docs/extensions/pg_partman

Defines the structure of the 'user_activities' table, setting up partitioning by the 'activity_time' column using a range partition strategy. This is the initial step before creating specific partitions.

```sql
CREATE TABLE user_activities (
    activity_id serial,
    activity_time TIMESTAMPTZ NOT NULL,
    activity_type TEXT NOT NULL,
    content_id INT NOT NULL,
    user_id INT NOT NULL
)
PARTITION BY RANGE (activity_time);
```

--------------------------------

### Configure Netlify Function for ES6 Imports and Install Neon Driver (Bash)

Source: https://neon.com/docs/guides/netlify-functions

This sequence of commands renames the generated JavaScript function file to use the `.mjs` extension, enabling ES6 import syntax. It also installs the Neon serverless driver as a project dependency, which is necessary for database interaction.

```bash
mv netlify/functions/get_coffee_blends/get_coffee_blends.js netlify/functions/get_coffee_blends/get_coffee_blends.mjs
npm install @neondatabase/serverless
```

--------------------------------

### Example: Posts Table with btree_gin Index

Source: https://neon.com/docs/extensions/btree_gin

This SQL code defines a `posts` table schema and inserts sample data. It then creates a composite GIN index on `tags` (TEXT array) and `published_at` (TIMESTAMPTZ) using the btree_gin extension for efficient querying.

```sql
CREATE TABLE posts (
    post_id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    tags TEXT[],             -- GIN-friendly array
    published_at TIMESTAMPTZ -- B-tree friendly timestamp
);

INSERT INTO posts (title, tags, published_at) VALUES
('Postgres Performance Tuning', '{"postgres", "performance", "database"}', '2025-03-15 10:30:00Z'),
('Advanced Indexing Strategies', '{"sql", "indexes", "optimization"}', '2025-04-02 14:00:00Z'),
('Working with JSONB in Postgres', '{"postgres", "jsonb", "nosql"}', '2025-04-20 09:15:00Z');

CREATE INDEX idx_posts_tags_published
ON posts
USING GIN (tags, published_at);
```

--------------------------------

### Create Neon Project, Connect with psql, and Run SQL File

Source: https://neon.com/docs/reference/cli-projects

Creates a new Neon project, connects using psql, and executes all SQL commands from a specified `.sql` file. This is useful for deploying schemas or initial data.

```bash
neon project create --psql -- -f dump.sql
```

--------------------------------

### Scheduled GitHub Action for Neon Database Backup (YAML)

Source: https://neon.com/docs/manage/backups-aws-s3-backup-part-2

This GitHub Actions workflow automates the process of backing up a Neon database. It runs on a schedule, installs PostgreSQL, configures AWS credentials, generates a compressed SQL dump, uploads it to an S3 bucket, and cleans up old backups based on a retention policy. It requires AWS credentials and S3 bucket information to be configured as GitHub Secrets.

```yaml
name: acme-co-prod-backup

on:
  schedule:
    - cron: '0 5 * * *' # Runs at midnight EST (us-east-1)
  workflow_dispatch:

jobs:
  db-backup:
    runs-on: ubuntu-latest

    permissions:
      id-token: write

    env:
      RETENTION: 7
      DATABASE_URL: ${{ secrets.ACME_CO_PROD }}
      IAM_ROLE: ${{ secrets.IAM_ROLE }}
      AWS_ACCOUNT_ID: ${{ secrets.AWS_ACCOUNT_ID }}
      S3_BUCKET_NAME: ${{ secrets.S3_BUCKET_NAME }}
      AWS_REGION: 'us-east-1'
      PG_VERSION: '17'

    steps:
      - name: Install PostgreSQL
        run: |
          sudo apt update
          yes '' | sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
          sudo apt install -y postgresql-${{ env.PG_VERSION }}

      - name: Set PostgreSQL binary path
        run: echo "POSTGRES=/usr/lib/postgresql/${{ env.PG_VERSION }}/bin" >> $GITHUB_ENV

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ env.AWS_ACCOUNT_ID }}:role/${{ env.IAM_ROLE }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Set file, folder and path variables
        run: |
          GZIP_NAME="$(date +'%B-%d-%Y@%H:%M:%S').sql.gz"
          FOLDER_NAME="${{ github.workflow }}"
          UPLOAD_PATH="s3://${{ env.S3_BUCKET_NAME }}/${FOLDER_NAME}/${GZIP_NAME}"

          echo "GZIP_NAME=${GZIP_NAME}" >> $GITHUB_ENV
          echo "FOLDER_NAME=${FOLDER_NAME}" >> $GITHUB_ENV
          echo "UPLOAD_PATH=${UPLOAD_PATH}" >> $GITHUB_ENV

      - name: Create folder if it doesn't exist
        run: |
          if ! aws s3api head-object --bucket ${{ env.S3_BUCKET_NAME }} --key "${{ env.FOLDER_NAME }}/" 2>/dev/null;
            aws s3api put-object --bucket ${{ env.S3_BUCKET_NAME }} --key "${{ env.FOLDER_NAME }}/"
          fi

      - name: Run pg_dump
        run: |
          $POSTGRES/pg_dump ${{ env.DATABASE_URL }} | gzip > "${{ env.GZIP_NAME }}"

      - name: Empty bucket of old files
        run: |
          THRESHOLD_DATE=$(date -d "-${{ env.RETENTION }} days" +%Y-%m-%dT%H:%M:%SZ)
          aws s3api list-objects --bucket ${{ env.S3_BUCKET_NAME }} --prefix "${{ env.FOLDER_NAME }}/" --query "Contents[?LastModified<'${THRESHOLD_DATE}'] | [?ends_with(Key, '.gz')].{Key: Key}" --output text | while read -r file;
            aws s3 rm "s3://${{ env.S3_BUCKET_NAME }}/${file}"
          done

      - name: Upload to bucket
        run: |
          aws s3 cp "${{ env.GZIP_NAME }}" "${{ env.UPLOAD_PATH }}" --region ${{ env.AWS_REGION }}

```

--------------------------------

### Connect to Neon Database with Serverless Driver

Source: https://neon.com/docs/ai/ai-rules-neon-serverless

Demonstrates how to establish connections to a Neon database using environment variables for security. It shows connection methods for both HTTP queries (using the `neon` function) and WebSocket connections (using the `Pool` class). Avoid hardcoding credentials.

```typescript
// For HTTP queries
import { neon } from '@neondatabase/serverless';
const sql = neon(process.env.DATABASE_URL!);
```

```typescript
// For WebSocket connections
import { Pool } from '@neondatabase/serverless';
const pool = new Pool({ connectionString: process.env.DATABASE_URL! });
```

```typescript
// AVOID: Hardcoded credentials
const sql = neon('postgres://username:password@host.neon.tech/neondb');
```

--------------------------------

### Get Koyeb App Details

Source: https://neon.com/docs/guides/koyeb

Fetches details of a specific Koyeb application, including its ID, name, status, public domains, and creation timestamp. This is useful for retrieving the application's URL after deployment.

```bash
$ koyeb app get express-neon
```

--------------------------------

### Run Database Seeding (Rails CLI)

Source: https://neon.com/docs/guides/rails-migrations

Executes the `db/seeds.rb` file to populate the database with the predefined initial data. This command is idempotent due to the use of `find_or_create_by` in the seed script.

```bash
rails db:seed
```

--------------------------------

### Create Composite GIN Index with btree_gin

Source: https://neon.com/docs/extensions/btree_gin

This SQL example demonstrates creating a table and then applying a composite GIN index using the btree_gin extension. This index spans a timestamp column (`order_date`) and a text array column (`product_tags`), allowing for efficient queries that filter on both.

```sql
-- Create the table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date TIMESTAMP,
    product_tags TEXT[]
);

CREATE INDEX idx_orders_date_tags
ON orders
USING GIN (order_date, product_tags);
```

--------------------------------

### Create Ruby on Rails Project with PostgreSQL

Source: https://neon.com/docs/guides/ruby-on-rails

Command to install the Rails gem and create a new Rails project, specifying PostgreSQL as the database type.

```bash
gem install rails
rails new neon-with-rails --database=postgresql
```

--------------------------------

### Experimental: Get Project Consumption Metrics

Source: https://neon.com/docs/reference/python-sdk

Retrieves project consumption metrics. This is an experimental feature and may be subject to change. It does not require any parameters.

```javascript
consumption()
```

--------------------------------

### Neon Connection String Example

Source: https://neon.com/docs/connect/connection-errors

A typical Neon connection string format, which includes the username, password, hostname, and database name. This string is essential for configuring client applications.

```plaintext
postgresql://[user]:[password]@[neon_hostname]/[dbname]
```

--------------------------------

### Postgres COUNT() Function Examples

Source: https://neon.com/docs/functions/count

This snippet demonstrates the creation of an 'orders' table and populates it with sample data. It then shows various applications of the Postgres COUNT() function, including counting all rows, non-null values, distinct values, and using COUNT() with GROUP BY for monthly order counts. These examples are crucial for understanding how to analyze and summarize data within a PostgreSQL database.

```sql
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id INTEGER,
    order_amount DECIMAL(10, 2) NOT NULL,
    order_date TIMESTAMP NOT NULL
);

INSERT INTO orders (customer_id, product_id, order_amount, order_date)
VALUES
    (1, 101, 150.00, '2023-01-15 10:30:00'),
    (2, 102, 75.50, '2023-01-16 11:45:00'),
    (1, 103, 200.00, '2023-02-01 09:15:00'),
    (3, 104, 50.25, '2023-02-10 14:20:00'),
    (2, 105, 125.75, '2023-03-05 16:30:00'),
    (4, NULL, 90.00, '2023-03-10 13:00:00'),
    (1, 106, 180.50, '2023-04-02 11:10:00'),
    (3, 107, 60.25, '2023-04-15 10:45:00'),
    (5, 108, 110.00, '2023-05-01 15:20:00'),
    (2, 109, 95.75, '2023-05-20 12:30:00');
```

```sql
SELECT COUNT(*) AS total_orders
FROM orders;
```

```sql
SELECT COUNT(product_id) AS orders_with_product
FROM orders;
```

```sql
SELECT COUNT(DISTINCT customer_id) AS unique_customers
FROM orders;
```

```sql
SELECT
  DATE_TRUNC('month', order_date) AS month,
  COUNT(*) AS orders_per_month
FROM orders
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;
```

--------------------------------

### Initialize Neon API Client (Python)

Source: https://neon.com/docs/ai/ai-rules-neon-python-sdk

Initializes the Neon API client using an API key loaded from environment variables. This is the recommended secure method for authenticating API requests.

```python
import os
from neon_api import NeonAPI

# Best practice: Load API key from environment variables
api_key = os.getenv("NEON_API_KEY")
if not api_key:
    raise ValueError("NEON_API_KEY environment variable is not set.")

neon = NeonAPI(api_key=api_key)

```

--------------------------------

### Create Role with NOLOGIN Attribute (Neon API)

Source: https://neon.com/docs/changelog/2025-02-07

This example shows how to create a PostgreSQL role with the NOLOGIN attribute using the Neon API. The `no_login` attribute in the API request facilitates this.

```json
{
  "role_name": "my_role",
  "no_login": true
}
```

--------------------------------

### Query Customer List in GraphQL API

Source: https://neon.com/docs/guides/stepzen

An example GraphQL query to retrieve a list of customers, specifically fetching their `name` and `email` fields from the `customer` table. This demonstrates how to interact with the deployed StepZen API.

```graphql
{
  getCustomerList {
    name
    email
  }
}
```

--------------------------------

### JavaScript SDK: Filter Data with Case-Sensitive Like Operator

Source: https://neon.com/docs/data-api/get-started

This snippet illustrates using the `.like()` method for case-sensitive pattern matching. It selects rows where the 'title' column contains the substring 'hello'.

```javascript
.like('title', '%hello%')
```

--------------------------------

### Insert Sample Data into Partitioned Table

Source: https://neon.com/docs/extensions/pg_partman

Inserts multiple rows of sample user activity data into the 'user_activities' partitioned table. PostgreSQL automatically directs this data to the appropriate partition based on the 'activity_time'.

```sql
INSERT INTO user_activities (activity_time, activity_type, content_id, user_id)
VALUES
    ('2024-03-15 10:00:00', 'like', 1001, 101),
    ('2024-03-16 15:30:00', 'comment', 1002, 102),
    ('2024-03-17 09:45:00', 'share', 1003, 103),
    ('2024-03-18 18:20:00', 'like', 1004, 104),
    ('2024-03-19 12:10:00', 'comment', 1005, 105),
    ('2024-03-20 08:00:00', 'like', 1006, 106),
    ('2024-03-21 14:15:00', 'share', 1007, 107),
    ('2024-03-22 11:30:00', 'like', 1008, 108),
    ('2024-03-23 16:45:00', 'comment', 1009, 109),
    ('2024-03-24 20:00:00', 'share', 1010, 110),
    ('2024-03-25 09:30:00', 'like', 1011, 111),
    ('2024-03-26 13:45:00', 'comment', 1012, 112),
    ('2024-03-27 17:00:00', 'share', 1013, 113),
    ('2024-03-28 11:15:00', 'like', 1014, 114),
    ('2024-03-29 15:30:00', 'comment', 1015, 115);
```

--------------------------------

### Create Test SQL File

Source: https://neon.com/docs/extensions/neon-utils

This SQL script defines the queries to be executed during the pgbench test. It includes a logarithmic calculation and retrieval of the current transaction ID.

```sql
SELECT LOG(factorial(5000)) / LOG(factorial(2500));
SELECT txid_current();
```

--------------------------------

### Create Quarkus Project (Reactive)

Source: https://neon.com/docs/guides/quarkus-reactive

This command creates a new Quarkus project with necessary extensions for reactive PostgreSQL client and RESTEasy Reactive. It assumes you have the Quarkus CLI installed.

```bash
quarkus create app neon-with-quarkus \
--name neon-with-quarkus \
--package-name com.neon.tech \
--extensions reactive-pg-client,resteasy-reactive
```

--------------------------------

### Deploy to Production Environment

Source: https://neon.com/docs/guides/encore

Deploys the Encore application to the production environment by pushing code to the 'encore' remote. This action triggers automatic Neon database creation, migration, and application deployment.

```bash
git push encore
```

--------------------------------

### Install Neon & Drizzle Dependencies

Source: https://neon.com/docs/ai/ai-rules-neon-drizzle

Installs necessary packages for integrating Drizzle ORM with Neon serverless Postgres. Includes runtime dependencies like `drizzle-orm`, `@neondatabase/serverless`, and `ws` (for older Node.js versions), as well as development dependencies such as `drizzle-kit` and `dotenv`.

```bash
npm install drizzle-orm @neondatabase/serverless ws
npm install -D drizzle-kit dotenv @types/ws
```

--------------------------------

### Manual MCP Server Command Execution

Source: https://neon.com/docs/ai/connect-mcp-clients-to-neon

Use these commands when your MCP client does not support JSON configuration for MCP servers. They allow for direct execution of the remote or local setup commands.

```bash
# For OAuth (remote server)
npx -y mcp-remote https://mcp.neon.tech/mcp
```

```bash
# For Local setup
npx -y @neondatabase/mcp-server-neon start <YOUR_NEON_API_KEY>
```

--------------------------------

### Initialize Neon Connection with Knex

Source: https://neon.com/docs/guides/knex

This code snippet demonstrates how to initialize a basic connection to Neon using the Knex.js query builder. It requires setting up a `DATABASE_URL` environment variable with your Neon connection string. The example assumes you are using the 'pg' client and specifies the connection details.

```javascript
export const client = knex({
  client: 'pg',
  connection: {
    connectionString: process.env.DATABASE_URL,
  },
});
```

--------------------------------

### GraphQL Mutation to Create a Todo

Source: https://neon.com/docs/guides/exograph

An example GraphQL mutation to add a new todo item to the database. This demonstrates how to interact with the Exograph backend to perform data creation operations.

```graphql
mutation {
  createTodo(data: { title: "Set up Exograph with Neon", completed: true }) {
    id
  }
}
```

--------------------------------

### Snowflake: Example Verification Query

Source: https://neon.com/docs/guides/logical-replication-airbyte-snowflake

This SQL query demonstrates how to verify data replication in Snowflake after setting up an Airbyte connection. It assumes a table named 'PLAYING_WITH_NEON' has been replicated from a source.

```sql
SELECT * FROM PLAYING_WITH_NEON;
```

--------------------------------

### Run pgbench Test with Custom SQL File

Source: https://neon.com/docs/extensions/neon-utils

This command executes a pgbench test using the custom 'test.sql' file. It specifies the number of clients (-c), test duration (-T), and progress interval (-P), along with the Neon database connection string.

```bash
pgbench -f test.sql -c 15 -T 1000 -P 1 postgresql://[user]:[password]@[neon_hostname]/[dbname]
```

--------------------------------

### GET /databases

Source: https://neon.com/docs/ai/ai-rules-neon-python-sdk

Retrieves a list of all databases within a specified branch. This allows you to view existing databases and their details.

```APIDOC
## GET /databases

### Description
Retrieves a list of all databases within a branch.

### Method
GET

### Endpoint
/databases

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The ID of the project.
- **branch_id** (string) - Required - The ID of the branch.

### Response
#### Success Response (200)
- **databases** (list[Database]) - A list of Database objects.

#### Response Example
{
  "databases": [
    {
      "id": 123,
      "branch_id": "br-your-branch-id",
      "name": "my-app-db",
      "owner_name": "neondb_owner",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

--------------------------------

### Create Quarkus Project with JDBC Driver

Source: https://neon.com/docs/guides/quarkus-jdbc

This command creates a new Quarkus project with necessary extensions for PostgreSQL JDBC, Agroal datasource, and RESTEasy Reactive. Ensure you have the Quarkus CLI installed to run this command.

```bash
quarkus create app neon-with-quarkus-jdbc \
--name neon-with-quarkus-jdbc \
--package-name com.neon.tech \
--extensions jdbc-postgresql,quarkus-agroal,resteasy-reactive
```

--------------------------------

### Neon Database Connection Strings

Source: https://neon.com/docs/get-started/workflow-primer

Example connection strings for different Neon database branches. Each branch provides a unique Postgres connection string for complete isolation.

```sql
# Branch 1
postgresql://database_name_owner:AbC123dEf@ep-shiny-cell-a5y2zuu0.us-east-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require

# Branch 2
postgresql://database_name_owner:AbC123dEf@ep-hidden-hall-a5x58cuv.us-east-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require
```

--------------------------------

### Get All Authors

Source: https://neon.com/docs/guides/sequelize

Retrieves a list of all authors from the database.

```APIDOC
## GET /authors

### Description
Retrieves a list of all authors stored in the database.

### Method
GET

### Endpoint
/authors

### Parameters
None

### Request Example
None

### Response
#### Success Response (200)
- **authors** (array) - An array of author objects.
  - **id** (integer) - The unique identifier for the author.
  - **name** (string) - The name of the author.
  - **bio** (string) - A short biography of the author.
  - **createdAt** (string) - Timestamp of creation.
  - **updatedAt** (string) - Timestamp of last update.

#### Response Example
```json
[
  {
    "id": 1,
    "name": "J.K. Rowling",
    "bio": "The creator of the Harry Potter series",
    "createdAt": "2023-10-27T10:00:00.000Z",
    "updatedAt": "2023-10-27T10:00:00.000Z"
  }
]
```
```

--------------------------------

### Drizzle HTTP Adapter Setup with Neon

Source: https://neon.com/docs/ai/ai-rules-neon-drizzle

Configures the Drizzle ORM to use the Neon HTTP adapter for database connections. This setup is recommended for serverless and edge environments due to its low latency for individual operations. It utilizes `neon` from `@neondatabase/serverless` and the `drizzle` adapter from `drizzle-orm/neon-http`.

```typescript
// src/db.ts
import { drizzle } from "drizzle-orm/neon-http";
import { neon } from "@neondatabase/serverless";
import { config } from "dotenv";

config({ path: ".env" });

if (!process.env.DATABASE_URL) {
  throw new Error('DATABASE_URL is not defined');
}

const sql = neon(process.env.DATABASE_URL);
export const db = drizzle(sql);
```

--------------------------------

### GET /projects

Source: https://neon.com/docs/manage/orgs-api-consumption

Retrieves basic billing period-based consumption metrics for each project in the organization.

```APIDOC
## GET /projects

### Description
Retrieves basic billing period-based consumption metrics for each project in the organization. This endpoint provides a summary of usage for the current billing period.

### Method
GET

### Endpoint
`/projects`

### Parameters
#### Query Parameters
- **org_id** (string) - Required - The ID of the organization to retrieve project metrics for.

### Request Example
```json
{
  "example": "curl --request GET \
     --url 'https://console.neon.tech/api/v2/projects?org_id=org-ocean-art-12345678' \
     --header 'accept: application/json' \
     --header 'authorization: Bearer $ORG_API_KEY'"
}
```

### Response
#### Success Response (200)
- The response body will contain an array of project objects, each including basic consumption metrics for the current billing period. Refer to the Neon API Reference for detailed attribute definitions.

#### Response Example
(Response structure not provided in the source text, but would typically include project details and consumption summaries.)
```

--------------------------------

### Create a Neon Database Backup with pg_dump

Source: https://neon.com/docs/manage/backup-pg-dump

Demonstrates how to create a compressed backup of a Neon database using the `pg_dump` command. Ensure you use an unpooled connection string.

```bash
pg_dump -Fc -v -d "<neon_database_connection_string>" -f <dump_file_name>
```

```bash
pg_dump -Fc -v -d "postgresql://alex:AbC123dEf@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require" -f mydatabase.bak
```

--------------------------------

### Environment Configuration for Vercel Edge Functions (JavaScript)

Source: https://neon.com/docs/ai/ai-rules-neon-serverless

Provides an example of setting environment-specific configuration, specifically for Vercel Edge Functions. It includes specifying the runtime and region for optimal performance.

```javascript
// For Vercel Edge Functions, specify nearest region
export const config = {
  runtime: 'edge',
  regions: ['iad1'], // Region nearest to your Neon DB
};
```

--------------------------------

### JavaScript SDK: Filter Data with Less Than Operator

Source: https://neon.com/docs/data-api/get-started

This snippet shows how to use the `.lt()` method to filter records where the 'price' column is less than 50.

```javascript
.lt('price', 50)
```

--------------------------------

### Install 'ulid' Extension on Postgres 14-16

Source: https://neon.com/docs/extensions/pg-extensions

This SQL command installs the 'ulid' extension, providing support for ULID (Universally Unique Lexicographically Sortable Identifier) generation on PostgreSQL versions 14, 15, and 16.

```sql
CREATE EXTENSION ulid;
```

--------------------------------

### Grafbase CLI Command

Source: https://neon.com/docs/guides/grafbase

This command starts the Grafbase CLI development server, enabling local development and testing of Grafbase projects.

```bash
npx grafbase dev
```

--------------------------------

### SQL to PostgREST Converter API Documentation

Source: https://neon.com/docs/data-api/sql-to-rest

This section details how to use the SQL to PostgREST Converter, including an example of converting a SQL query to JavaScript (with Neon Auth) and cURL requests.

```APIDOC
## SQL to PostgREST Converter

### Description
Convert SQL queries to PostgREST API calls with real-time preview. This tool supports common SELECT statements with filtering, sorting, pagination, joins, and aggregations.

### Method
N/A (This is a tool/converter, not a direct API endpoint call)

### Endpoint
N/A

### Parameters
N/A

### Request Example (SQL Query)
```sql
select
name,
age
from
users
where
name ilike '%john%'
order by
name desc
limit
5
offset
10
```

### Response Example (Generated API Calls)
#### JavaScript (With Neon Auth)
```javascript
import { createClient } from "@neondatabase/neon-js";

// An example of how to use the data api with neon auth can be found here:
// https://github.com/neondatabase-labs/neon-data-api-neon-auth

const client = createClient<Database>({
  auth: {
    url: 'NEON-AUTH-URL',
  },
  dataApi: {
    url: 'DATA-API-URL',
  },
});

// Perform signin using client.auth before making any requests to the data api

const { data, error } = await client
  .from('users')
  .select(
    `
    name,
    age
    `,
  )
  .ilike('name', '%john%')
  .order('name', { ascending: false })
  .range(10, 15)
```

#### cURL
```bash
# Example cURL request (actual command will depend on PostgREST configuration and Neon Data API specifics)
curl -X GET "https://your-neon-data-api-url/users?name=ilike.%25john%25&order=name.desc&limit=5&offset=10" \
     -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

### Related Documentation
* Getting started with Neon Data API
* Building a note-taking app
* PostgREST documentation: postgrest.org
```

--------------------------------

### Implement Book Controller with Micronaut HTTP

Source: https://neon.com/docs/guides/micronaut-kotlin

Creates a 'BookController' to expose REST endpoints for book management. It uses Micronaut's HTTP annotations (`@Controller`, `@Get`, `@Post`) to define endpoints for retrieving all books, getting a book by ID, and saving a new book. The controller depends on 'BookRepository' for data access and uses `@ExecuteOn` for asynchronous I/O operations.

```kotlin
package com.example.controller

import com.example.entity.Book
import com.example.repository.BookRepository
import io.micronaut.http.annotation.*
import io.micronaut.scheduling.TaskExecutors
import io.micronaut.scheduling.annotation.ExecuteOn

@Controller("/books")
class BookController(private val bookRepository: BookRepository) {

    @Get
    @ExecuteOn(TaskExecutors.IO)
    fun getAll(): List<Book> = bookRepository.findAll().toList()

    @Get("/{id}")
    @ExecuteOn(TaskExecutors.IO)
    fun getById(id: Long): Book? = bookRepository.findById(id).orElse(null)

    @Post
    @ExecuteOn(TaskExecutors.IO)
    fun save(@Body book: Book): Book = bookRepository.save(book)
}
```

--------------------------------

### Start Compute Endpoint

Source: https://neon.com/docs/ai/ai-rules-neon-typescript-sdk

Manually initiates or resumes an 'idle' compute endpoint. This operation requires the project ID and the endpoint ID.

```typescript
const response = await apiClient.startProjectEndpoint('your-project-id', 'ep-your-endpoint-id');
```

--------------------------------

### GET /api/v2/consumption_history/projects

Source: https://neon.com/docs/guides/consumption-metrics

Retrieves detailed metrics for each project in your account, broken down by the specified granularity level.

```APIDOC
## GET /api/v2/consumption_history/projects

### Description
Retrieves detailed metrics for each project in your account, broken down by the specified granularity level.

### Method
GET

### Endpoint
/api/v2/consumption_history/projects

### Parameters
#### Query Parameters
- **from** (date-time) - Required - Start date-time for the consumption period in RFC 3339 format. The value is rounded according to the specified granularity.
- **to** (date-time) - Required - End date-time for the consumption period in RFC 3339 format. The value is rounded according to the specified granularity.
- **granularity** (string) - Required - The granularity of consumption metrics. Options:
  * `hourly` - Limited to the last 168 hours (7 days)
  * `daily` - Limited to the last 60 days
  * `monthly` - Limited to the past year
- **project_ids** (array of strings) - Optional - Filter the response to specific project IDs. If omitted, all projects are included. Can be specified as an array or comma-separated list.
- **org_id** (string) - Optional - Specify the organization for which project consumption metrics should be returned. If not provided, metrics for your personal account projects will be returned.
- **metrics** (array of strings) - Optional - Specify which metrics to include. If omitted, `active_time_seconds`, `compute_time_seconds`, `written_data_bytes`, and `synthetic_storage_size_bytes` are returned. Available metrics:
  * `active_time_seconds`
  * `compute_time_seconds`
  * `written_data_bytes`
  * `synthetic_storage_size_bytes`
  * `data_storage_bytes_hour`
  * `logical_size_bytes`
  * `logical_size_bytes_hour`
- **limit** (integer) - Optional - Number of projects to include in the response. Default: 10. Max: 100.
- **cursor** (string) - Optional - Cursor value from the previous response to get the next batch of projects.

### Request Example
```json
{
  "request": "curl --request GET \
  --url 'https://console.neon.tech/api/v2/consumption_history/projects?from=2024-06-30T00:00:00Z&to=2024-07-02T00:00:00Z&granularity=daily&project_ids=project-id-1&project_ids=project-id-2' \
  --header 'accept: application/json' \
  --header 'authorization: Bearer $NEON_API_KEY'"
}
```

### Response
#### Success Response (200)
- **projects** (array) - An array of project consumption metrics.
  - **project_id** (string) - The ID of the project.
  - **consumption** (array) - An array of consumption details for the project.
    - **timeframe_start** (date-time) - The start time of the consumption timeframe.
    - **timeframe_end** (date-time) - The end time of the consumption timeframe.
    - **active_time_seconds** (integer) - Active time in seconds.
    - **compute_time_seconds** (integer) - Compute time in seconds.
    - **written_data_bytes** (integer) - Data written in bytes.
    - **synthetic_storage_size_bytes** (integer) - Synthetic storage size in bytes.

#### Response Example
```json
{
  "projects": [
    {
      "project_id": "random-project-abcdef",
      "consumption": [
        {
          "timeframe_start": "2024-06-30T00:00:00Z",
          "timeframe_end": "2024-07-01T00:00:00Z",
          "active_time_seconds": 147452,
          "compute_time_seconds": 43215,
          "written_data_bytes": 111777920,
          "synthetic_storage_size_bytes": 41371988928
        }
      ]
    }
  ]
}
```
```

--------------------------------

### Connect to Neon using pgcli

Source: https://neon.com/docs/connect/connect-pgcli

Demonstrates how to connect to a Neon database using the pgcli client with a connection string. The connection string typically includes the username, password, host, database name, and SSL mode parameters.

```bash
pgcli postgresql://alex:AbC123dEf@ep-cool-darkness-123456.us-east-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require
```

--------------------------------

### GitHub Action: Environment Variables for Backup

Source: https://neon.com/docs/guides/multitenancy

Sets up environment variables for a GitHub Actions workflow, primarily for database backups. Key variables include `RETENTION` for backup file longevity, `DATABASE_URL` for connecting to the PostgreSQL database (using secrets), `IAM_ROLE`, `AWS_ACCOUNT_ID`, `S3_BUCKET_NAME`, and `AWS_REGION` for AWS S3 integration, and `PG_VERSION` for specifying the PostgreSQL version to install.

```yaml
env:
  RETENTION: 7
  DATABASE_URL: ${{ secrets.ACME_ANALYTICS_PROD }}

  IAM_ROLE: ${{ secrets.IAM_ROLE }}
  AWS_ACCOUNT_ID: ${{ secrets.AWS_ACCOUNT_ID }}
  S3_BUCKET_NAME: ${{ secrets.S3_BUCKET_NAME }}
  AWS_REGION: 'us-east-1'
  PG_VERSION: '16'
```

--------------------------------

### SDK User and Project Components

Source: https://neon.com/docs/community/component-specialized

Includes components for displaying SDK user and project information, with support for React, Node.js, and Vue. These components are designed for SDK documentation and require shared content.

```javascript
<SdkUser sdkName="React" />
<SdkProject sdkName="Node.js" />
<SdkUseUser sdkName="Vue" />
```

--------------------------------

### SQL JSON_TABLE Error Handling Example

Source: https://neon.com/docs/functions/json_table

This example demonstrates how to use the DEFAULT and ON ERROR clauses within JSON_TABLE to handle missing or malformed JSON data. It sets default values for 'metadata' and 'edition' when errors occur during extraction.

```SQL
SELECT title, jt.*
FROM library_books,
JSON_TABLE(
    data,
    '$'
    COLUMNS (
        author_name text PATH '$.author.name',
        metadata TEXT PATH '$.metadata' DEFAULT '{}' ON ERROR,
        edition text PATH '$.metadata.edition' DEFAULT 'Unknown' ON EMPTY DEFAULT 'Unknown' ON ERROR
    )
) AS jt;
```

--------------------------------

### Postgres ROUND() Function Example

Source: https://neon.com/docs/functions/math-round

Demonstrates the default half-round-up behavior of the PostgreSQL ROUND() function. When a number is exactly halfway between two values, it rounds up to the next higher number. This example shows rounding to one decimal place.

```sql
SELECT round(2.65, 1), round(2.75, 1);
```

--------------------------------

### POST /api/v2/projects - Create Project for Free-Tier User

Source: https://neon.com/docs/guides/ai-agent-integration

Creates a new project with resource quotas aligned with Neon's Free plan limits. This is suitable for free-tier users.

```APIDOC
## POST /api/v2/projects

### Description
Creates a new project for a free-tier user with predefined resource quotas.

### Method
POST

### Endpoint
/api/v2/projects

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **project** (object) - Required - Project configuration details.
  - **name** (string) - Required - The name of the project.
  - **pg_version** (integer) - Required - The PostgreSQL version to use.
  - **settings** (object) - Optional - Project settings.
    - **quota** (object) - Optional - Resource quotas for the project.
      - **active_time_seconds** (integer) - Optional - Maximum active compute time in seconds (e.g., 360000 for 100 hours).
      - **logical_size_bytes** (integer) - Optional - Maximum storage size in bytes (e.g., 536870912 for 512 MB).
      - **data_transfer_bytes** (integer) - Optional - Maximum data transfer in bytes (e.g., 5368709120 for 5 GB).
  - **default_endpoint_settings** (object) - Optional - Default settings for the project's endpoints.
    - **autoscaling_limit_min_cu** (number) - Optional - Minimum compute units for autoscaling (e.g., 0.25).
    - **autoscaling_limit_max_cu** (number) - Optional - Maximum compute units for autoscaling (e.g., 2).
    - **suspend_timeout_seconds** (integer) - Optional - Time in seconds before compute suspends (e.g., 300 for 5 minutes).

### Request Example
```json
{
  "project": {
    "name": "user-free-database",
    "pg_version": 16,
    "settings": {
      "quota": {
        "active_time_seconds": 360000,
        "logical_size_bytes": 536870912,
        "data_transfer_bytes": 5368709120
      }
    },
    "default_endpoint_settings": {
      "autoscaling_limit_min_cu": 0.25,
      "autoscaling_limit_max_cu": 2,
      "suspend_timeout_seconds": 300
    }
  }
}
```

### Response
#### Success Response (200)
- **project** (object) - Details of the created project.
  - **id** (string) - The unique identifier of the project.
  - **name** (string) - The name of the project.
  - **status** (string) - The current status of the project.
  - **created_at** (string) - Timestamp of project creation.

#### Response Example
```json
{
  "project": {
    "id": "prj_abc123",
    "name": "user-free-database",
    "status": "pending_creation",
    "created_at": "2023-10-27T10:00:00Z"
  }
}
```
```

--------------------------------

### Postgres json_agg() with Ordered Aggregation Example

Source: https://neon.com/docs/functions/json_agg

Illustrates how to use `json_agg()` with the `ORDER BY` clause to ensure the aggregated JSON array has elements in a specific order. This example aggregates product reviews, ordered by review date.

```sql
WITH reviews AS (
  SELECT 1 AS product_id, 'Great product!' AS comment, 5 AS rating, '2023-01-15'::date AS review_date
  UNION ALL SELECT 1, 'Could be better', 3, '2023-02-01'::date
  UNION ALL SELECT 1, 'Awesome!', 5, '2023-01-20'::date
  UNION ALL SELECT 2, 'Not bad', 4, '2023-01-10'::date
)
SELECT
  product_id,
  json_agg(
    comment || ' (' || rating || ' stars)'
    ORDER BY review_date DESC
  ) AS reviews
FROM reviews
GROUP BY product_id;
```

--------------------------------

### Run pg_dump and Compress Backup

Source: https://neon.com/docs/manage/backups-aws-s3-backup-part-2

Executes the pg_dump command to create a database backup and pipes the output to gzip for compression. The compressed backup is stored in the Action's virtual environment.

```yaml
- name: Run pg_dump
  run: |
    $POSTGRES/$pg_dump ${{ env.DATABASE_URL }} | gzip > "${{ env.GZIP_NAME }}"
```

--------------------------------

### GET /projects/{project_id}/connection_uri

Source: https://neon.com/docs/ai/ai-rules-neon-api

Retrieves a connection URI for a specific database within a project.

```APIDOC
## GET /projects/{project_id}/connection_uri

### Description
Retrieves a ready-to-use connection URI for a specific database within a project.

### Method
GET

### Endpoint
`/projects/{project_id}/connection_uri`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The unique identifier of the project.

#### Query Parameters
- **database_name** (string) - Required - The name of the target database.
- **role_name** (string) - Required - The role to use for the connection.
- **branch_id** (string) - Optional - The branch ID. Defaults to the project's primary branch if not specified.
- **pooled** (boolean) - Optional - If set to `false`, returns a direct connection URI instead of a pooled one. Defaults to `true`.
- **endpoint_id** (string) - Optional - The specific endpoint ID to connect to. Defaults to the `read-write` endpoint_id associated with the `branch_id` if not specified.

### Request Example
```bash
curl 'https://console.neon.tech/api/v2/projects/old-fire-32990194/connection_uri?database_name=neondb&role_name=neondb_owner' \
  -H 'Accept: application/json' \
  -H "Authorization: Bearer $NEON_API_KEY"
```

### Response
#### Success Response (200)
- **uri** (string) - The connection URI.

#### Response Example
```json
{
  "uri": "postgresql://neondb_owner:npg_IDNnorOST71P@ep-shiny-morning-a1bfdvjs-pooler.ap-southeast-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require"
}
```
```

--------------------------------

### Retrieve Connection URI

Source: https://neon.com/docs/ai/ai-rules-neon-typescript-sdk

Gets a complete connection string for a specific database and role within a branch in a project.

```APIDOC
## POST /websites/neon/connection-uri

### Description
Gets a complete connection string for a specific database and role within a branch in a project.

### Method
POST

### Endpoint
`/websites/neon/connection-uri`

### Parameters
#### Request Body
- **projectId** (string) - Required - The ID of the project.
- **branch_id** (string) - Optional - The ID of the branch. Defaults to the project's primary branch.
- **database_name** (string) - Required - The name of the database.
- **role_name** (string) - Required - The name of the role.
- **pooled** (boolean) - Optional - If true, returns the pooled connection string.

### Request Example
```json
{
  "projectId": "your-project-id",
  "database_name": "dbName",
  "role_name": "roleName",
  "pooled": true
}
```

### Response
#### Success Response (200)
- **uri** (string) - The connection URI for the specified database and role.

#### Response Example
```json
{
  "uri": "postgresql://neondb_owner:xxx@ep-xx-pooler.westus3.azure.neon.tech/neondb?channel_binding=require&sslmode=require"
}
```
```

--------------------------------

### Get Account Consumption Metrics

Source: https://neon.com/docs/guides/consumption-metrics

Retrieves aggregated consumption metrics for all projects within an account for a specified period and granularity.

```APIDOC
## GET /api/v2/consumption_history/account

### Description
Aggregates all metrics from all projects in an account into a single cumulative number for each metric. This provides a comprehensive view of consumption metrics accumulated for the billing period.

### Method
GET

### Endpoint
`https://console.neon.tech/api/v2/consumption_history/account`

### Parameters
#### Query Parameters
- **`from`** (date-time) - Required - Start date-time for the consumption period in RFC 3339 format. The value is rounded according to the specified granularity.
- **`to`** (date-time) - Required - End date-time for the consumption period in RFC 3339 format. The value is rounded according to the specified granularity.
- **`granularity`** (string) - Required - The granularity of consumption metrics. Options: `hourly` (Limited to the last 168 hours), `daily` (Limited to the last 60 days), `monthly` (Limited to the past year).
- **`org_id`** (string) - Optional - Specify the organization for which consumption metrics should be returned. If not provided, metrics for your personal account will be returned.
- **`metrics`** (array of strings) - Optional - Specify which metrics to include in the response. If omitted, `active_time_seconds`, `compute_time_seconds`, `written_data_bytes`, and `synthetic_storage_size_bytes` are returned. Available metrics: `active_time_seconds`, `compute_time_seconds`, `written_data_bytes`, `synthetic_storage_size_bytes`, `data_storage_bytes_hour`, `logical_size_bytes`, `logical_size_bytes_hour`. Can be specified as an array or a comma-separated list.

### Request Example
```json
{
  "example": "GET https://console.neon.tech/api/v2/consumption_history/account?from=2024-06-01T00:00:00Z&to=2024-06-30T23:59:59Z&granularity=daily&metrics=active_time_seconds,compute_time_seconds"
}
```

### Response
#### Success Response (200)
- **`metrics`** (object) - Contains the requested consumption metrics and their values.
- **`from`** (string) - The start date-time of the consumption period.
- **`to`** (string) - The end date-time of the consumption period.
- **`granularity`** (string) - The granularity of the returned metrics.

#### Response Example
```json
{
  "example": {
    "metrics": {
      "active_time_seconds": 12345,
      "compute_time_seconds": 67890,
      "written_data_bytes": 567890123,
      "synthetic_storage_size_bytes": 987654321
    },
    "from": "2024-06-01T00:00:00Z",
    "to": "2024-06-30T23:59:59Z",
    "granularity": "daily"
  }
}
```
```

--------------------------------

### Example Room Booking Operations (SQL)

Source: https://neon.com/docs/extensions/btree_gist

Demonstrates successful and failed INSERT operations on the 'room_bookings' table. The first insert is successful. The second insert for the same room with an overlapping period fails due to the exclusion constraint. The third insert for a different room with an overlapping period is successful.

```sql
-- Successful booking
INSERT INTO room_bookings (room_id, booking_period)
VALUES (101, '[2025-04-10 14:00, 2025-04-10 16:00)');

-- Attempting to book the same room for an overlapping period
INSERT INTO room_bookings (room_id, booking_period)
VALUES (101, '[2025-04-10 15:00, 2025-04-10 17:00)');
-- This will fail: ERROR:  conflicting key value violates exclusion constraint "no_overlapping_bookings"

-- Booking a different room for an overlapping period is fine
INSERT INTO room_bookings (room_id, booking_period)
VALUES (102, '[2025-04-10 15:00, 2025-04-10 17:00)');
```

--------------------------------

### Show All Postgres Settings (SQL)

Source: https://neon.com/docs/postgresql/query-reference

Displays all available configuration parameter settings for your Neon Postgres instance.

```sql
SHOW ALL;
```

--------------------------------

### Get Neon Database Tables

Source: https://neon.com/docs/ai/neon-mcp-server

Lists all tables within a specified Neon database.

```tool_code
get_database_tables
```

--------------------------------

### Run Phoenix Server with Neon Database

Source: https://neon.com/docs/guides/phoenix

Starts the Phoenix application server on localhost:4001 in production mode, connecting to a Neon PostgreSQL database. This command sets the PORT, MIX_ENV, DATABASE_URL, and SECRET_KEY_BASE environment variables. Ensure your Neon database credentials and secret key are correctly substituted.

```bash
PORT=4001 \
MIX_ENV=prod \
DATABASE_URL="postgresql://...:...@...aws.neon.tech/neondb?sslmode=require&channel_binding=require" \
SECRET_KEY_BASE=".../..." \
mix phx.server
```

--------------------------------

### View Neon Metrics with psql

Source: https://neon.com/docs/changelog/2023-11-27

This snippet demonstrates how to connect to the 'postgres' database using psql and list Neon-specific metric views. It requires a valid Neon connection string and assumes the 'neon' extension is installed.

```bash
psql 'postgresql://alex:AbC123dEf@ep-cool-darkness-123456.us-east-2.aws.neon.tech/postgres?sslmode=require&channel_binding=require'

postgres=> \dv neon.*
            List of relations
Schema |      Name      | Type |    Owner
--------+----------------+------+-------------
neon   | local_cache    | view | cloud_admin
neon   | neon_lfc_stats | view | cloud_admin
(2 rows)
```

--------------------------------

### Neon OAuth Server Metadata Example

Source: https://neon.com/docs/guides/oauth-integration

This JSON object represents the server metadata published by the Neon OAuth server, conforming to the OpenID Connect Discovery specification. It details available endpoints, supported grant types, scopes, and more.

```json
{
  "issuer": "https://oauth2.neon.tech/",
  "authorization_endpoint": "https://oauth2.neon.tech/oauth2/auth",
  "token_endpoint": "https://oauth2.neon.tech/oauth2/token",
  "jwks_uri": "https://oauth2.neon.tech/.well-known/jwks.json",
  "subject_types_supported": ["public"],
  "response_types_supported": [
    "code",
    "code id_token",
    "id_token",
    "token id_token",
    "token",
    "token id_token code"
  ],
  "claims_supported": ["sub"],
  "grant_types_supported": [
    "authorization_code",
    "implicit",
    "client_credentials",
    "refresh_token"
  ],
  "response_modes_supported": ["query", "fragment"],
  "userinfo_endpoint": "https://oauth2.neon.tech/userinfo",
  "scopes_supported": ["offline_access", "offline", "openid"],
  "token_endpoint_auth_methods_supported": [
    "client_secret_post",
    "client_secret_basic",
    "private_key_jwt",
    "none"
  ],
  "userinfo_signing_alg_values_supported": ["none", "RS256"],
  "id_token_signing_alg_values_supported": ["RS256"],
  "request_parameter_supported": true,
  "request_uri_parameter_supported": true,
  "require_request_uri_registration": true,
  "claims_parameter_supported": false,
  "revocation_endpoint": "https://oauth2.neon.tech/oauth2/revoke",
  "backchannel_logout_supported": true,
  "backchannel_logout_session_supported": true,
  "frontchannel_logout_supported": true,
  "frontchannel_logout_session_supported": true,
  "end_session_endpoint": "https://oauth2.neon.tech/oauth2/sessions/logout",
  "request_object_signing_alg_values_supported": ["RS256", "none"],
  "code_challenge_methods_supported": ["plain", "S256"]
}
```

--------------------------------

### Create and Navigate to Serverless Project Directory (bash)

Source: https://neon.com/docs/guides/aws-lambda

Creates a new project directory named 'neon-lambda' and changes the current directory to it, preparing for Serverless Framework project initialization.

```bash
mkdir neon-lambda
cd neon-lambda
```

--------------------------------

### GET /projects/{project_id}

Source: https://neon.com/docs/ai/ai-rules-neon-api

Retrieves detailed information about a single, specific project using its unique identifier.

```APIDOC
## GET /projects/{project_id}

### Description
Retrieves detailed information about a single, specific project.

### Method
GET

### Endpoint
`/projects/{project_id}`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The unique identifier of the project.

### Request Example
```bash
curl 'https://console.neon.tech/api/v2/projects/sparkling-hill-99143322' \
  -H 'Accept: application/json' \
  -H "Authorization: Bearer $NEON_API_KEY"
```

### Response
#### Success Response (200)
- **project** (object) - Contains the project details.
  - **data_storage_bytes_hour** (integer) - Data storage in bytes per hour.
  - **data_transfer_bytes** (integer) - Data transfer in bytes.
  - **written_data_bytes** (integer) - Written data in bytes.
  - **compute_time_seconds** (integer) - Compute time in seconds.
  - **active_time_seconds** (integer) - Active time in seconds.
  - **cpu_used_sec** (integer) - CPU used in seconds.
  - **id** (string) - The unique identifier of the project.
  - **platform_id** (string) - The platform ID (e.g., 'aws').
  - **region_id** (string) - The region ID (e.g., 'aws-us-west-2').
  - **name** (string) - The name of the project.
  - **provisioner** (string) - The provisioner used (e.g., 'k8s-neonvm').
  - **default_endpoint_settings** (object) - Default settings for the project's endpoints.
    - **autoscaling_limit_min_cu** (number) - Minimum compute units for autoscaling.
    - **autoscaling_limit_max_cu** (number) - Maximum compute units for autoscaling.
    - **suspend_timeout_seconds** (integer) - Timeout in seconds before suspension.
  - **settings** (object) - General project settings.
    - **allowed_ips** (object) - Allowed IP addresses.
      - **ips** (array) - List of IP addresses.
      - **protected_branches_only** (boolean) - Whether IPs are only for protected branches.
    - **enable_logical_replication** (boolean) - Whether logical replication is enabled.
    - **maintenance_window** (object) - Maintenance window settings.
      - **weekdays** (array) - Days of the week for maintenance (1-7).
      - **start_time** (string) - Start time of the maintenance window (HH:MM).
      - **end_time** (string) - End time of the maintenance window (HH:MM).
    - **block_public_connections** (boolean) - Whether public connections are blocked.
    - **block_vpc_connections** (boolean) - Whether VPC connections are blocked.
    - **hipaa** (boolean) - Whether HIPAA compliance is enabled.
  - **pg_version** (integer) - PostgreSQL version.
  - **proxy_host** (string) - The proxy host for the project.
  - **branch_logical_size_limit** (integer) - Logical size limit for branches in GB.
  - **branch_logical_size_limit_bytes** (integer) - Logical size limit for branches in bytes.
  - **store_passwords** (boolean) - Whether passwords are stored.
  - **creation_source** (string) - The source of project creation (e.g., 'console').
  - **history_retention_seconds** (integer) - History retention period in seconds.
  - **created_at** (string) - Timestamp of project creation (ISO 8601).
  - **updated_at** (string) - Timestamp of last project update (ISO 8601).
  - **synthetic_storage_size** (integer) - Synthetic storage size.
  - **consumption_period_start** (string) - Start of the consumption period (ISO 8601).
  - **consumption_period_end** (string) - End of the consumption period (ISO 8601).
  - **owner_id** (string) - The ID of the project owner.
  - **owner** (object) - Information about the project owner.
    - **email** (string) - Email of the owner.
    - **name** (string) - Name of the owner.
    - **branches_limit** (integer) - Limit of branches for the owner.
    - **subscription_type** (string) - Subscription type of the owner.
  - **compute_last_active_at** (string) - Timestamp of last compute activity (ISO 8601).
  - **org_id** (string) - The ID of the organization.

#### Response Example
```json
{
  "project": {
    "data_storage_bytes_hour": 0,
    "data_transfer_bytes": 0,
    "written_data_bytes": 0,
    "compute_time_seconds": 0,
    "active_time_seconds": 0,
    "cpu_used_sec": 0,
    "id": "sparkling-hill-99143322",
    "platform_id": "aws",
    "region_id": "aws-us-west-2",
    "name": "my-new-api-project",
    "provisioner": "k8s-neonvm",
    "default_endpoint_settings": {
      "autoscaling_limit_min_cu": 0.25,
      "autoscaling_limit_max_cu": 0.25,
      "suspend_timeout_seconds": 0
    },
    "settings": {
      "allowed_ips": {
        "ips": [],
        "protected_branches_only": false
      },
      "enable_logical_replication": false,
      "maintenance_window": {
        "weekdays": [5],
        "start_time": "07:00",
        "end_time": "08:00"
      },
      "block_public_connections": false,
      "block_vpc_connections": false,
      "hipaa": false
    },
    "pg_version": 17,
    "proxy_host": "c-2.us-west-2.aws.neon.tech",
    "branch_logical_size_limit": 512,
    "branch_logical_size_limit_bytes": 536870912,
    "store_passwords": true,
    "creation_source": "console",
    "history_retention_seconds": 86400,
    "created_at": "2025-09-10T07:58:16Z",
    "updated_at": "2025-09-10T07:58:25Z",
    "synthetic_storage_size": 0,
    "consumption_period_start": "2025-09-10T06:58:15Z",
    "consumption_period_end": "2025-10-01T00:00:00Z",
    "owner_id": "org-royal-sun-91776391",
    "owner": {
      "email": "<USER_EMAIL>",
      "name": "My Personal Account",
      "branches_limit": 10,
      "subscription_type": "free_v3"
    },
    "compute_last_active_at": "2025-09-10T07:58:21Z",
    "org_id": "org-royal-sun-91776391"
  }
}
```
```

--------------------------------

### Create Initial Table in Neon SQL

Source: https://neon.com/docs/guides/schema-diff-tutorial

This SQL statement creates a 'person' table with an ID, name, and email. It is intended to be run in the Neon SQL Editor on a specified branch and database.

```sql
CREATE TABLE person (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);
```

--------------------------------

### Insert Sample Data into feature_flags Table

Source: https://neon.com/docs/guides/time-travel-tutorial

This SQL snippet shows how to insert initial data into the `feature_flags` table. It sets up a sample feature flag named 'new_checkout_process' and marks it as disabled (FALSE). This is a prerequisite for simulating feature activation.

```sql
INSERT INTO feature_flags (feature_name, enabled)
VALUES ('new_checkout_process', FALSE);
```

--------------------------------

### Get Project Details

Source: https://neon.com/docs/introduction/monitor-usage

This endpoint retrieves detailed information about a specific Neon project, including usage metrics, configuration, and metadata.

```APIDOC
## GET /api/v2/projects/{projectId}

### Description
Retrieves detailed information about a specific Neon project, including usage metrics, configuration, and metadata.

### Method
GET

### Endpoint
`/api/v2/projects/{projectId}`

### Parameters
#### Path Parameters
- **projectId** (string) - Required - The unique identifier of the project.

### Request Example
```bash
curl --request GET \
     --url https://console.neon.tech/api/v2/projects/summer-bush-30064139 \
     --header 'accept: application/json' \
     --header 'authorization: Bearer $NEON_API_KEY'
```

### Response
#### Success Response (200)
- **project** (object) - Contains detailed information about the project.
  - **data_storage_bytes_hour** (integer) - Data storage in bytes per hour.
  - **data_transfer_bytes** (integer) - Data transfer in bytes.
  - **written_data_bytes** (integer) - Written data in bytes.
  - **compute_time_seconds** (integer) - Compute time in seconds.
  - **active_time_seconds** (integer) - Active time in seconds.
  - **cpu_used_sec** (integer) - CPU used in seconds.
  - **id** (string) - Project ID.
  - **platform_id** (string) - Cloud platform ID (e.g., 'aws').
  - **region_id** (string) - Cloud region ID (e.g., 'aws-us-east-2').
  - **name** (string) - Project name.
  - **provisioner** (string) - Provisioner type (e.g., 'k8s-neonvm').
  - **default_endpoint_settings** (object) - Default settings for endpoints.
    - **autoscaling_limit_min_cu** (number) - Minimum compute units for autoscaling.
    - **autoscaling_limit_max_cu** (number) - Maximum compute units for autoscaling.
    - **suspend_timeout_seconds** (integer) - Timeout in seconds before suspension.
  - **settings** (object) - Project settings.
    - **allowed_ips** (object) - Allowed IP addresses.
      - **ips** (array) - List of allowed IP addresses.
      - **protected_branches_only** (boolean) - Whether only protected branches are allowed.
    - **enable_logical_replication** (boolean) - Whether logical replication is enabled.
  - **pg_version** (integer) - PostgreSQL version.
  - **proxy_host** (string) - Proxy host address.
  - **branch_logical_size_limit** (integer) - Logical size limit for branches in GB.
  - **branch_logical_size_limit_bytes** (integer) - Logical size limit for branches in bytes.
  - **store_passwords** (boolean) - Whether to store passwords.
  - **creation_source** (string) - Source of project creation (e.g., 'console').
  - **history_retention_seconds** (integer) - History retention in seconds.
  - **created_at** (string) - Timestamp of creation.
  - **updated_at** (string) - Timestamp of last update.
  - **synthetic_storage_size** (integer) - Synthetic storage size.
  - **consumption_period_start** (string) - Start of the consumption period.
  - **consumption_period_end** (string) - End of the consumption period.
  - **quota_reset_at** (string) - Timestamp when quota resets.
  - **owner_id** (string) - ID of the project owner.
  - **owner** (object) - Owner details.
    - **email** (string) - Owner's email.
    - **branches_limit** (integer) - Limit on the number of branches.
    - **subscription_type** (string) - Type of subscription.
  - **compute_last_active_at** (string) - Timestamp of last compute activity.

#### Response Example
```json
{
  "project": {
    "data_storage_bytes_hour": 113808080168,
    "data_transfer_bytes": 40821459,
    "written_data_bytes": 1566830744,
    "compute_time_seconds": 2785,
    "active_time_seconds": 11024,
    "cpu_used_sec": 2785,
    "id": "summer-bush-30064139",
    "platform_id": "aws",
    "region_id": "aws-us-east-2",
    "name": "summer-bush-30064139",
    "provisioner": "k8s-neonvm",
    "default_endpoint_settings": {
      "autoscaling_limit_min_cu": 0.25,
      "autoscaling_limit_max_cu": 0.25,
      "suspend_timeout_seconds": 0
    },
    "settings": {
      "allowed_ips": {
        "ips": [],
        "protected_branches_only": false
      },
      "enable_logical_replication": false
    },
    "pg_version": 16,
    "proxy_host": "us-east-2.aws.neon.tech",
    "branch_logical_size_limit": 204800,
    "branch_logical_size_limit_bytes": 214748364800,
    "store_passwords": true,
    "creation_source": "console",
    "history_retention_seconds": 86400,
    "created_at": "2024-04-02T12:54:33Z",
    "updated_at": "2024-04-10T17:26:07Z",
    "synthetic_storage_size": 492988552,
    "consumption_period_start": "2024-04-02T12:54:33Z",
    "consumption_period_end": "2024-05-01T00:00:00Z",
    "quota_reset_at": "2024-05-01T00:00:00Z",
    "owner_id": "8d5f604c-d04e-4795-baf7-e87909a5d959",
    "owner": {
      "email": "alex@domain.com",
      "branches_limit": -1,
      "subscription_type": "launch"
    },
    "compute_last_active_at": "2024-04-10T17:26:05Z"
  }
}
```
```

--------------------------------

### Deploy Site and Functions to Netlify (Bash)

Source: https://neon.com/docs/guides/netlify-functions

This command deploys the project, including the frontend and Netlify Functions, to production. The `--prod` flag ensures a production deployment, and the user is prompted to specify the publish directory.

```bash
netlify deploy --prod
```

--------------------------------

### Install 'pg_ivm' Extension in PostgreSQL

Source: https://neon.com/docs/extensions/pg-extensions

This shows how to use the 'create_immv' function from the 'pg_ivm' extension. The function is created in the 'public' schema by default, not the 'pg_ivm' schema.

```sql
SELECT create_immv();
```

--------------------------------

### JavaScript SDK: Order Results

Source: https://neon.com/docs/data-api/get-started

This snippet shows how to sort query results using the `.order()` modifier. It sorts by 'created_at' in descending order (most recent first).

```javascript
.order('created_at', { ascending: false })
```

--------------------------------

### Configure Neon Database Connection URI in StepZen

Source: https://neon.com/docs/guides/stepzen

Illustrates the `config.yaml` structure for StepZen, specifically highlighting the `uri` field. It shows how to append `&options=project=YOUR_NEON_PROJECT_ID` to the DSN for a secure connection to the Neon database, including user, password, project ID, and SSL requirements.

```yaml
configurationset:
  - configuration:
      name: postgresql_config
      uri: YOUR_NEON_DSN?user=YOUR_NEON_USERNAME&password=YOUR_NEON_PASSWORD&options=project=YOUR_NEON_PROJECT_ID&sslmode=require&channel_binding=require
```

--------------------------------

### Run Ad-hoc Sales Analysis Query

Source: https://neon.com/docs/guides/read-replica-adhoc-queries

An example SQL query to run on a Neon read replica for sales analysis. This query calculates the total sales for each product over the past year, demonstrating a typical ad-hoc reporting task.

```sql
SELECT product_id, SUM(sale_amount) AS total_sales
FROM sales
WHERE sale_date >= (CURRENT_DATE - INTERVAL '1 year')
GROUP BY product_id;
```

--------------------------------

### JavaScript SDK: Limit Number of Rows

Source: https://neon.com/docs/data-api/get-started

This snippet demonstrates how to limit the number of rows returned by a query using the `.limit()` modifier. It restricts the results to the first 10 rows.

```javascript
.limit(10)
```

--------------------------------

### GitHub Action: Scheduled PostgreSQL Backup to S3

Source: https://neon.com/docs/guides/database-per-user

This YAML file defines a GitHub Action that performs a scheduled backup of a PostgreSQL database to an S3 bucket. It installs PostgreSQL, configures AWS credentials, sets up S3 paths, creates S3 folders if they don't exist, runs `pg_dump` to create a compressed backup, removes old backup files based on retention policy, and uploads the new backup to S3. Dependencies include AWS CLI, PostgreSQL client, and gzip.

```yaml
name: acme-analytics-prod

on:
  schedule:
    - cron: '0 0 * * *' # Runs at midnight UTC
  workflow_dispatch:

jobs:
  db-backup:
    runs-on: ubuntu-latest

    permissions:
      id-token: write

    env:
      RETENTION: 7
      DATABASE_URL: ${{ secrets.ACME_ANALYTICS_PROD }}

      IAM_ROLE: ${{ secrets.IAM_ROLE }}
      AWS_ACCOUNT_ID: ${{ secrets.AWS_ACCOUNT_ID }}
      S3_BUCKET_NAME: ${{ secrets.S3_BUCKET_NAME }}
      AWS_REGION: 'us-east-1'
      PG_VERSION: '16'

    steps:
      - name: Install PostgreSQL
        run: |
          sudo apt install -y postgresql-common
          yes '' | sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
          sudo apt install -y postgresql-${{ env.PG_VERSION }}

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ env.AWS_ACCOUNT_ID }}:role/${{ env.IAM_ROLE }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Set file, folder and path variables
        run: |
          GZIP_NAME="$(date +'%B-%d-%Y@%H:%M:%S').gz"
          FOLDER_NAME="${{ github.workflow }}"
          UPLOAD_PATH="s3://${{ env.S3_BUCKET_NAME }}/${{ env.FOLDER_NAME }}/${{ GZIP_NAME }}"

          echo "GZIP_NAME=${GZIP_NAME}" >> $GITHUB_ENV
          echo "FOLDER_NAME=${FOLDER_NAME}" >> $GITHUB_ENV
          echo "UPLOAD_PATH=${UPLOAD_PATH}" >> $GITHUB_ENV

      - name: Create folder if it doesn't exist
        run: |
          if ! aws s3api head-object --bucket ${{ env.S3_BUCKET_NAME }} --key "${{ env.FOLDER_NAME }}/" 2>/dev/null;
            aws s3api put-object --bucket ${{ env.S3_BUCKET_NAME }} --key "${{ env.FOLDER_NAME }}/"
          fi

      - name: Run pg_dump
        run: |
          /usr/lib/postgresql/${{ env.PG_VERSION }}/bin/pg_dump ${{ env.DATABASE_URL }} | gzip > "${{ env.GZIP_NAME }}"

      - name: Empty bucket of old files
        run: |
          THRESHOLD_DATE=$(date -d "-${{ env.RETENTION }} days" +%Y-%m-%dT%H:%M:%SZ)
          aws s3api list-objects --bucket ${{ env.S3_BUCKET_NAME }} --prefix "${{ env.FOLDER_NAME }}/" --query "Contents[?LastModified<'${THRESHOLD_DATE}'] | [?ends_with(Key, '.gz')].{{Key: Key}}" --output text | while read -r file;
            aws s3 rm "s3://${{ env.S3_BUCKET_NAME }}/${file}"
          done

      - name: Upload to bucket
        run: |
          aws s3 cp "${{ env.GZIP_NAME }}" "${{ env.UPLOAD_PATH }}" --region ${{ env.AWS_REGION }}

```

--------------------------------

### GET /projects/{project_id}/branches/{branch_id}/roles

Source: https://neon.com/docs/ai/ai-rules-neon-api

Retrieves a list of all Postgres roles from the specified branch.

```APIDOC
## GET /projects/{project_id}/branches/{branch_id}/roles

### Description
Retrieves a list of all Postgres roles from the specified branch.

### Method
GET

### Endpoint
`/projects/{project_id}/branches/{branch_id}/roles`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The unique identifier of the project.
- **branch_id** (string) - Required - The unique identifier of the branch.

### Request Example
```bash
curl 'https://console.neon.tech/api/v2/projects/hidden-river-50598307/branches/br-super-wildflower-adniii9u/roles' \
  -H 'Accept: application/json' \
  -H "Authorization: Bearer $NEON_API_KEY"
```

### Response
#### Success Response (200)
- **roles** (array) - A list of roles in the branch.

#### Response Example
```json
{
  "roles": [
    {
      "branch_id": "br-super-wildflower-adniii9u",
      "name": "neondb_owner",
      "protected": false,
      "created_at": "2025-09-10T12:14:58Z",
      "updated_at": "2025-09-10T12:14:58Z"
    },
    {
      "branch_id": "br-super-wildflower-adniii9u",
      "name": "new_app_user",
      "protected": false,
      "created_at": "2025-09-11T05:50:21Z",
      "updated_at": "2025-09-11T05:50:21Z"
    }
  ]
}
```
```

--------------------------------

### Postgres json_build_object() function example

Source: https://neon.com/docs/functions/json_build_object

An example SQL query demonstrating how to use the `json_build_object()` function to create a JSON object containing user information from the 'users' table. This highlights the function's ability to structure data into JSON format.

```sql
SELECT id,
 json_build_object(
   'name', name,
   'age', age,
   'city', city
 ) AS user_data
FROM users;
```

--------------------------------

### Get help for psql meta-commands in Neon SQL Editor

Source: https://neon.com/docs/changelog/2024-04-19

Explains how to access a cheat sheet of available psql meta-commands using `\?` in the Neon SQL Editor. This is a quick way to discover supported commands and their usage.

```sql
-- Display a cheat sheet of available meta-commands
\?
```

--------------------------------

### Example JSON Response for Project Consumption History

Source: https://neon.com/docs/manage/orgs-api-consumption

Illustrates the structure of the JSON response when requesting granular project consumption history. Includes project details, periods, and consumption breakdown by timeframe.

```json
{
  "projects": [
    {
      "project_id": "random-project-123456",
      "periods": [
        {
          "period_id": "random-period-abcdef",
          "period_plan": "scale",
          "period_start": "2024-06-30T00:00:00Z",
          "consumption": [
            {
              "timeframe_start": "2024-06-30T00:00:00Z",
              "timeframe_end": "2024-06-30T01:00:00Z",
              "active_time_seconds": 147472,
              "compute_time_seconds": 43222,
              "written_data_bytes": 112730864,
              "synthetic_storage_size_bytes": 37000959232
            },
            {
              "timeframe_start": "2024-07-01T00:00:00Z",
              "timeframe_end": "2024-07-01T01:00:00Z",
              "active_time_seconds": 1792,
              "compute_time_seconds": 533,
              "written_data_bytes": 0,
              "synthetic_storage_size_bytes": 0
            }
          ]
        }
      ]
    }
  ]
}
```

--------------------------------

### LinkAPIKey: Link to API Key Management

Source: https://neon.com/docs/community/component-guide

LinkAPIKey is a simple component that provides a direct link to the API key management section within the Neon console. It's used to guide users to where they can manage their API credentials.

```html
<LinkAPIKey />
```

--------------------------------

### Setup NeonAuthUIProvider React

Source: https://neon.com/docs/auth/reference/ui-components

Wraps your application with `NeonAuthUIProvider` to enable Neon Auth UI components. This provider accepts configuration props to control available features, such as OAuth providers and navigation.

```javascript
import { NeonAuthUIProvider } from '@neondatabase/neon-js/auth/react';
import '@neondatabase/neon-js/ui/css';
import { authClient } from './auth';

function App() {
  return (
    <NeonAuthUIProvider authClient={authClient}>{/* Your app components */}</NeonAuthUIProvider>
  );
}
```

--------------------------------

### Create TanStack App with Neon Integration

Source: https://neon.com/docs/changelog/2025-07-04

Use the 'create-tanstack' command to quickly set up a fullstack application with a Neon Postgres database. This command simplifies the initial project setup for developers using TanStack.

```bash
pnpm create tanstack --add-on neon
```

--------------------------------

### Restart Compute Endpoint

Source: https://neon.com/docs/extensions/pg_cron

Restarts the compute endpoint to apply the `pg_cron` extension setting. Note that this will drop current connections.

```APIDOC
## POST /api/v2/projects/<project_id>/endpoints/<endpoint_id>/restart

### Description
Restarts a Neon compute endpoint. This is necessary after updating `pg_settings` for changes like enabling `pg_cron` to take effect. Existing connections will be dropped.

### Method
POST

### Endpoint
`https://console.neon.tech/api/v2/projects/<project_id>/endpoints/<endpoint_id>/restart`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - Your Neon project ID.
- **endpoint_id** (string) - Required - The ID of the compute endpoint to restart.

#### Headers
- **accept**: `application/json`
- **authorization**: `Bearer $NEON_API_KEY$`

### Request Example
```bash
curl --request POST \
     --url https://console.neon.tech/api/v2/projects/<project_id>/endpoints/<endpoint_id>/restart \
     --header 'accept: application/json' \
     --header 'authorization: Bearer $NEON_API_KEY'
```

### Response
#### Success Response (200)
- **message** (string) - Confirmation message indicating the restart process has started.

#### Response Example
```json
{
  "message": "Compute endpoint restart initiated."
}
```

#### Note
If the compute is idle, it must be started first using the Start compute endpoint API or by running a query to wake it up before it can be restarted.
```

--------------------------------

### Bootstrap Neon Postgres Database with NeonDB CLI

Source: https://neon.com/docs/changelog/2025-07-04

Initialize a Neon Postgres database using the 'neondb' command-line interface. This tool helps in quickly setting up a database instance for development or testing.

```bash
npx neondb --yes
```

--------------------------------

### Create Books Table and Insert Sample Data

Source: https://neon.com/docs/extensions/pg_trgm

Sets up a sample 'books' table with 'id' and 'title' columns and populates it with book titles. This table is used for demonstrating the capabilities of the pg_trgm extension in subsequent examples.

```sql
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title TEXT
);

INSERT INTO books (title)
VALUES
    ('The Great Gatsby'),
    ('The Grapes of Wrath'),
    ('Great Expectations'),
    ('War and Peace'),
    ('Pride and Prejudice'),
    ('To Kill a Mockingbird'),
    ('1984');
```

--------------------------------

### GitHub Actions Workflow for Database Migrations

Source: https://neon.com/docs/guides/database-per-user

This GitHub Actions workflow automates the process of running database migrations. It checks out the repository, sets up Node.js, installs dependencies, and then executes the migration script. The workflow is triggered only when a pull request is merged.

```yaml
jobs:
  migrate:
    runs-on: ubuntu-latest
    if: github.event.pull_request.merged == true

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Run migration script
        run: node src/scripts/migrate.js

```

--------------------------------

### JavaScript SDK: Filter Data with Less Than or Equal Operator

Source: https://neon.com/docs/data-api/get-started

This snippet shows how to use the `.lte()` method to filter records where the 'quantity' column is less than or equal to 10.

```javascript
.lte('quantity', 10)
```

--------------------------------

### Prepare Customer CSV Data

Source: https://neon.com/docs/import/import-from-csv

This is an example of the data format for the 'customer.csv' file. The columns in the CSV (First Name, Last Name, Email) must correspond to the columns in the 'customer' table created in the database. This data will be loaded into the Neon table.

```csv
First Name,Last Name,Email
1,Casey,Smith,casey.smith@example.com
2,Sally,Jones,sally.jones@example.com
```

--------------------------------

### Enable Experimental Extensions in Neon

Source: https://neon.com/docs/extensions/pg-extensions

This SQL command enables the use of experimental extensions in Neon. It requires setting a session variable before installing the extension. Use with caution as these extensions are not recommended for production.

```sql
SET neon.allow_unstable_extensions = 'true';
```

--------------------------------

### Create Migrations Folder

Source: https://neon.com/docs/guides/kysely

Command to create a directory for storing Kysely migration files.

```bash
mkdir migrations
```

--------------------------------

### GET /projects - List Projects

Source: https://neon.com/docs/manage/projects

Retrieves a list of all projects associated with your Neon account. This endpoint provides details about each project, including its ID, region, name, and various settings.

```APIDOC
## GET /projects

### Description
Lists all projects for your Neon account.

### Method
GET

### Endpoint
/api/v2/projects

### Query Parameters
- **limit** (integer) - Optional - Maximum number of projects to return.
- **cursor** (string) - Optional - Cursor for pagination to fetch the next set of projects.

### Request Example
```bash
curl 'https://console.neon.tech/api/v2/projects?limit=10&cursor=some_cursor'
  -H 'Accept: application/json'
  -H "Authorization: Bearer $NEON_API_KEY"
```

### Response
#### Success Response (200)
- **projects** (array) - An array of project objects.
  - **id** (string) - Unique identifier for the project.
  - **platform_id** (string) - The cloud platform used for the project (e.g., "aws").
  - **region_id** (string) - The region where the project is hosted (e.g., "aws-ap-southeast-1").
  - **name** (string) - The name of the project.
  - **provisioner** (string) - The provisioner used for the project (e.g., "k8s-neonvm").
  - **default_endpoint_settings** (object) - Default settings for project endpoints.
  - **settings** (object) - Project-specific settings.
  - **pg_version** (integer) - PostgreSQL version.
  - **proxy_host** (string) - The proxy host for accessing the project.
  - **branch_logical_size_limit** (integer) - Logical size limit for branches in GB.
  - **branch_logical_size_limit_bytes** (integer) - Logical size limit for branches in bytes.
  - **store_passwords** (boolean) - Whether passwords are stored.
  - **active_time** (integer) - Time the project has been active in seconds.
  - **cpu_used_sec** (integer) - CPU time used in seconds.
  - **creation_source** (string) - How the project was created (e.g., "console").
  - **created_at** (string) - Timestamp when the project was created.
  - **updated_at** (string) - Timestamp when the project was last updated.
  - **synthetic_storage_size** (integer) - Synthetic storage size in bytes.
  - **quota_reset_at** (string) - Timestamp when the quota resets.
  - **owner_id** (string) - ID of the project owner.
  - **compute_last_active_at** (string) - Timestamp of the last compute activity.
  - **history_retention_seconds** (integer) - Retention period for history in seconds.
- **unavailable_project_ids** (array) - List of project IDs that are unavailable.
- **pagination** (object) - Pagination information.
  - **cursor** (string) - Cursor for fetching the next page.
- **applications** (object) - Integrations with applications for each project.
- **integrations** (object) - General integrations for each project.

#### Response Example
```json
{
  "projects": [
    {
      "id": "frosty-tree-10754091",
      "platform_id": "aws",
      "region_id": "aws-ap-southeast-1",
      "name": "personal_projects",
      "provisioner": "k8s-neonvm",
      "default_endpoint_settings": {
        "autoscaling_limit_min_cu": 0.25,
        "autoscaling_limit_max_cu": 2,
        "suspend_timeout_seconds": 0
      },
      "settings": {
        "allowed_ips": {
          "ips": [],
          "protected_branches_only": false
        },
        "enable_logical_replication": false,
        "maintenance_window": {
          "weekdays": [4],
          "start_time": "15:00",
          "end_time": "16:00"
        },
        "block_public_connections": false,
        "block_vpc_connections": false,
        "hipaa": false
      },
      "pg_version": 17,
      "proxy_host": "ap-southeast-1.aws.neon.tech",
      "branch_logical_size_limit": 512,
      "branch_logical_size_limit_bytes": 536870912,
      "store_passwords": true,
      "active_time": 1260,
      "cpu_used_sec": 319,
      "creation_source": "console",
      "created_at": "2024-11-08T17:20:01Z",
      "updated_at": "2025-08-03T01:16:18Z",
      "synthetic_storage_size": 96929448,
      "quota_reset_at": "2025-09-01T00:00:00Z",
      "owner_id": "91cbdacd-06c2-49f5-bacf-78b9463c81ca",
      "compute_last_active_at": "2025-08-03T01:16:18Z",
      "history_retention_seconds": 86400
    }
  ],
  "unavailable_project_ids": [],
  "pagination": {
    "cursor": "lingering-grass-54827563"
  },
  "applications": {
    "frosty-tree-10754091": ["vercel"]
  },
  "integrations": {
    "frosty-tree-10754091": ["vercel"]
  }
}
```
```

--------------------------------

### Use Neon Connection in Remix Route

Source: https://neon.com/docs/guides/remix

Connect to your Neon database from a Remix route using the configured `db.server` file. This example fetches the PostgreSQL version.

```typescript
import { sql } from '~/db.server';
import { json } from '@remix-run/node';
import { useLoaderData } from '@remix-run/react';

export const loader = async () => {
  const response = await sql`SELECT version()`;
  return response[0].version;
};

export default function Page() {
  const data = useLoaderData();
  return <>{data}</>;
}
```

--------------------------------

### Create cube values on the fly in SELECT statements

Source: https://neon.com/docs/extensions/cube

Demonstrates the creation of 'cube' values directly within SQL SELECT statements. This is useful for defining points or intervals dynamically. It shows examples of creating a 3D point and a 1D interval.

```sql
SELECT cube(array[1,2,3]) AS point_3d, cube(0,10) AS interval_1d;
```

--------------------------------

### Retrieve Projects

Source: https://neon.com/docs/manage/api-keys

Demonstrates how to use your API key to retrieve a list of projects from the Neon API.

```APIDOC
## GET /api/v2/projects

### Description
Retrieves a list of projects associated with your Neon account.

### Method
GET

### Endpoint
`https://console.neon.tech/api/v2/projects`

### Parameters
#### Headers
- **Accept** (string) - Required - Specifies the accepted response type, typically `application/json`.
- **Authorization** (string) - Required - Your API key in the format `Bearer $NEON_API_KEY`.

### Request Example
```bash
curl 'https://console.neon.tech/api/v2/projects' \
  -H 'Accept: application/json' \
  -H "Authorization: Bearer $NEON_API_KEY"
```

### Response
#### Success Response (200)
- **projects** (array) - A list of project objects.
  - **cpu_used_sec** (integer) - CPU time used by the project in seconds.
  - **id** (string) - The unique identifier for the project.
  - **platform_id** (string) - The cloud platform where the project is hosted (e.g., `aws`).
  - **region_id** (string) - The region where the project is hosted (e.g., `aws-us-east-2`).
  - **name** (string) - The name of the project.
  - **provisioner** (string) - The provisioner used for the project (e.g., `k8s-pod`).
  - **pg_version** (integer) - The PostgreSQL version used by the project.
  - **locked** (boolean) - Indicates if the project is locked.
  - **created_at** (string) - The timestamp when the project was created.
  - **updated_at** (string) - The timestamp when the project was last updated.
  - **proxy_host** (string) - The hostname for the project's proxy.
  - **branch_logical_size_limit** (integer) - The logical size limit for branches in the project.

#### Response Example
```json
{
  "projects": [
    {
      "cpu_used_sec": 0,
      "id": "purple-shape-411361",
      "platform_id": "aws",
      "region_id": "aws-us-east-2",
      "name": "purple-shape-411361",
      "provisioner": "k8s-pod",
      "pg_version": 15,
      "locked": false,
      "created_at": "2023-01-03T18:22:56Z",
      "updated_at": "2023-01-03T18:22:56Z",
      "proxy_host": "us-east-2.aws.neon.tech",
      "branch_logical_size_limit": 3072
    }
  ]
}
```

### Error Handling
- **401 Unauthorized**: Returned if the API key is missing, invalid, or revoked.
```

--------------------------------

### PostgreSQL: Create and Manage Indexes

Source: https://neon.com/docs/postgresql/query-reference

Provides SQL examples for creating and managing various types of indexes in PostgreSQL to improve query performance. This includes creating basic, unique, composite, and partial indexes, as well as function-based indexes. It also covers dropping indexes, using GIN indexes for JSONB, reindexing, and creating indexes concurrently.

```sql
-- Create a basic index on a single column
CREATE INDEX idx_user_email ON users(email);

-- Create a unique index to enforce uniqueness and improve lookup performance
CREATE UNIQUE INDEX idx_unique_username ON users(username);

-- Create a composite index on multiple columns
CREATE INDEX idx_name_date ON events(name, event_date);

-- Create a partial index for a subset of rows that meet a certain condition
CREATE INDEX idx_active_users ON users(email) WHERE active = TRUE;

-- Create an index on an expression (function-based index)
CREATE INDEX idx_lower_email ON users(LOWER(email));

-- Drop an index
DROP INDEX idx_user_email;

-- Create a GIN index on a jsonb column to improve search performance on keys or values within the JSON document
CREATE INDEX idx_user_preferences ON users USING GIN (preferences);

-- Reindex an existing index to rebuild it, useful for improving index performance or reducing physical size
REINDEX INDEX idx_user_email;

-- Create a CONCURRENTLY index, which allows the database to be accessed normally during the indexing operation
CREATE INDEX CONCURRENTLY idx_concurrent_email ON users(email);
```

--------------------------------

### Neon JavaScript SDK - Authentication and Data API

Source: https://neon.com/docs/reference/javascript-sdk

This section covers the installation, initialization, and usage of the Neon JavaScript SDK for authentication and data operations.

```APIDOC
## JavaScript SDK (Auth & Data API)

### Description
Reference documentation for building applications with Neon Auth and Data API.
The Neon JavaScript SDK (`@neondatabase/neon-js`) provides authentication and database operations for your applications.

### Installation
Install the JavaScript SDK in your project using npm, yarn, pnpm, or bun.
```
npm install @neondatabase/neon-js
```

### Initialization

#### Full client (`createClient`)
Use this when you need both authentication and database queries.
```javascript
import { createClient } from '@neondatabase/neon-js';

const client = createClient({
  auth: {
    url: import.meta.env.VITE_NEON_AUTH_URL,
  },
  dataApi: {
    url: import.meta.env.VITE_NEON_DATA_API_URL,
  },
});
```

#### Auth-only client (`createAuthClient`)
Use this when you only need authentication (no database queries).
```javascript
import { createAuthClient } from '@neondatabase/neon-js';

const auth = createAuthClient({
  url: import.meta.env.VITE_NEON_AUTH_URL,
});
```

## POST /auth/signUp/email

### Description
Creates a new user account using email and password.

### Method
`POST`

### Endpoint
`/auth/signUp/email`

### Parameters
#### Request Body
- **email** (string) - Required - The user's email address.
- **password** (string) - Required - The user's password.
- **name** (string) - Required - The user's full name.
- **image** (string) - Optional - URL for the user's profile image.
- **callbackURL** (string) - Optional - URL to redirect after sign-up.

### Request Example
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}
```

### Response
#### Success Response (200)
- **user** (object) - The newly created user object.
- **session** (object) - The user's session object.

#### Response Example
```json
{
  "data": {
    "user": {
      "id": "user-id-123",
      "email": "user@example.com",
      "name": "John Doe"
    },
    "session": {
      "access_token": "access-token-xyz",
      "refresh_token": "refresh-token-abc"
    }
  },
  "error": null
}
```

## POST /auth/signIn/email

### Description
Signs in a user with their email and password.

### Method
`POST`

### Endpoint
`/auth/signIn/email`

### Parameters
#### Request Body
- **email** (string) - Required - The user's email address.
- **password** (string) - Required - The user's password.
- **rememberMe** (boolean) - Optional - Whether to keep the user signed in.
- **callbackURL** (string) - Optional - URL to redirect after sign-in.

### Request Example
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Response
#### Success Response (200)
- **user** (object) - The signed-in user object.
- **session** (object) - The user's session object.

#### Response Example
```json
{
  "data": {
    "user": {
      "id": "user-id-123",
      "email": "user@example.com"
    },
    "session": {
      "access_token": "access-token-xyz",
      "refresh_token": "refresh-token-abc"
    }
  },
  "error": null
}
```

## POST /auth/signIn/social

### Description
Initiates sign-in with an OAuth provider (e.g., Google, GitHub).

### Method
`POST`

### Endpoint
`/auth/signIn/social`

### Parameters
#### Request Body
- **provider** (string) - Required - The OAuth provider name (e.g., 'google', 'github').
- **options** (object) - Optional - Provider-specific options.
  - **redirectTo** (string) - Optional - URL to redirect to after authorization.

### Request Example
```json
{
  "provider": "google",
  "options": {
    "redirectTo": "https://your-app.com/auth/callback"
  }
}
```

### Response
#### Success Response (200)
- **url** (string) - The URL to redirect the user to for OAuth authorization.

#### Response Example
```json
{
  "data": {
    "url": "https://oauth-provider.com/authorize?client_id=..."
  },
  "error": null
}
```
```

--------------------------------

### React Styling with CSS Variables

Source: https://neon.com/docs/ai/ai-rules-neon-auth

Demonstrates the correct and incorrect ways to style React components using CSS variables provided by the UI package. Emphasizes using existing variables for consistency and theming support.

```tsx
<div style={{ background: 'hsl(var(--background))', color: 'hsl(var(--foreground))' }}>
  <button style={{ background: 'hsl(var(--primary))', color: 'hsl(var(--primary-foreground))' }}>
    Submit
  </button>
</div>
```

```tsx
<div style={{ background: '#ffffff', color: '#000000' }}>
  <button style={{ background: '#3b82f6', color: '#ffffff' }}>
    Submit
  </button>
</div>
```

--------------------------------

### Run pgloader Migration Command

Source: https://neon.com/docs/import/migrate-mysql

This command initiates the database migration process using pgloader with a specified configuration file. It assumes that a configuration file named 'config.load' has been created with the necessary database connection details and migration parameters.

```bash
pgloader config.load
```

--------------------------------

### Get Pooled Connection String (Neon CLI)

Source: https://neon.com/docs/connect/choose-connection

Retrieves a pooled connection string for Neon using the Neon CLI. Pooled connections are recommended for high concurrency and efficient resource management.

```bash
neon connection-string --pooled true [branch_name]

```

--------------------------------

### Connect App using Postgres Driver with Docker Compose Host

Source: https://neon.com/docs/local/neon-local

This connection string example demonstrates connecting to Neon Local within a Docker Compose environment. It uses a placeholder `${db}` which should be replaced with the name of your Neon Local service in the `docker-compose.yml` file.

```sql
postgres://neon:npg@${db}:5432/<database_name>?sslmode=require

# where {db} is the name of the Neon Local service in your compose file
```

--------------------------------

### Create and Populate Chinook Database

Source: https://neon.com/docs/import/import-sample-data

Commands to create the Chinook database, download its SQL source file, populate the database, and connect to it. This database is a sample for a digital media store.

```sql
CREATE DATABASE chinook;
```

```bash
wget https://raw.githubusercontent.com/neondatabase/postgres-sample-dbs/main/chinook.sql
```

```bash
psql -d "postgresql://[user]:[password]@[neon_hostname]/chinook" -f chinook.sql
```

```bash
psql postgresql://[user]:[password]@[neon_hostname]/chinook
```

--------------------------------

### Basic pg_repack Command Syntax

Source: https://neon.com/docs/extensions/pg_repack

The fundamental structure for executing pg_repack commands from the terminal. It includes the command itself, optional flags, and the target database name. Ensure pg_repack is installed and in your system's PATH. The DBNAME can often be omitted if connection options are provided.

```bash
pg_repack [OPTIONS]... [DBNAME]
```

--------------------------------

### Go: Create Neon Table and Insert Data

Source: https://neon.com/docs/guides/go

This Go script connects to a Neon database, drops the 'books' table if it exists, creates it with a defined schema, inserts a single book record, and then performs a bulk insert of multiple book records using `CopyFrom` for efficiency. It requires the `pgx` and `godotenv` Go packages and a `DATABASE_URL` environment variable.

```go
package main

import (
	"context"
	"fmt"
	"os"

	"github.com/jackc/pgx/v5"
	"github.com/joho/godotenv"
)

func main() {
	// Load environment variables from .env file
	err := godotenv.Load()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error loading .env file: %v\n", err)
		os.Exit(1)
	}

	// Get the connection string from the environment variable
	connString := os.Getenv("DATABASE_URL")
	if connString == ""
		{
		fmt.Fprintf(os.Stderr, "DATABASE_URL not set\n")
		os.Exit(1)
	}

	ctx := context.Background()

	// Connect to the database
	conn, err := pgx.Connect(ctx, connString)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Unable to connect to database: %v\n", err)
		os.Exit(1)
	}
	defer conn.Close(ctx)

	fmt.Println("Connection established")

	// Drop the table if it already exists
	_, err = conn.Exec(ctx, "DROP TABLE IF EXISTS books;")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Unable to drop table: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("Finished dropping table (if it existed).")

	// Create a new table
	_, err = conn.Exec(ctx, `
        CREATE TABLE books (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            author VARCHAR(255),
            publication_year INT,
            in_stock BOOLEAN DEFAULT TRUE
        );
    `)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Unable to create table: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("Finished creating table.")

	// Insert a single book record
	_, err = conn.Exec(ctx,
		"INSERT INTO books (title, author, publication_year, in_stock) VALUES ($1, $2, $3, $4);",
		"The Catcher in the Rye", "J.D. Salinger", 1951, true,
	)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Unable to insert single row: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("Inserted a single book.")

	// Data to be inserted
	booksToInsert := [][]interface{}{
		{"The Hobbit", "J.R.R. Tolkien", 1937, true},
		{"1984", "George Orwell", 1949, true},
		{"Dune", "Frank Herbert", 1965, false},
	}

	// Use CopyFrom for efficient bulk insertion
	copyCount, err := conn.CopyFrom(
		ctx,
		pgx.Identifier{"books"},
		[]string{"title", "author", "publication_year", "in_stock"},
		pgx.CopyFromRows(booksToInsert),
	)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Unable to copy rows: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Inserted %d rows of data.\n", copyCount)
}

```

--------------------------------

### Get Neon Database Connection String for psql

Source: https://neon.com/docs/get-started/signing-up

Retrieves the connection string for a specified Neon branch and database, formatted for use with the psql client. This enables terminal-based database connections.

```bash
neon connection-string development --database-name neondb --psql
```

--------------------------------

### Get Operation

Source: https://neon.com/docs/manage/operations

This method shows only the details for the specified operation ID.

```APIDOC
## GET /projects/{project_id}/operations/{operation_id}

### Description
Retrieves the details for a specific operation ID within a project.

### Method
GET

### Endpoint
/projects/{project_id}/operations/{operation_id}

#### Path Parameters
- **project_id** (string) - Required - The ID of the project.
- **operation_id** (string) - Required - The ID of the operation.

### Request Example
```bash
curl 'https://console.neon.tech/api/v2/projects/autumn-disk-484331/operations/97c7a650-e4ff-43d7-8c58-4c67f5050167'
  -H 'Accept: application/json'
  -H "Authorization: Bearer $NEON_API_KEY"
```

### Response
#### Success Response (200)
- **operation** (object) - Details of the requested operation.
  - **id** (string) - The unique identifier of the operation.
  - **project_id** (string) - The ID of the project.
  - **branch_id** (string) - The ID of the branch.
  - **endpoint_id** (string) - The ID of the endpoint.
  - **action** (string) - The type of action performed.
  - **status** (string) - The status of the operation (e.g., "finished").
  - **failures_count** (integer) - The number of failures.
  - **created_at** (string) - The timestamp when the operation was created.
  - **updated_at** (string) - The timestamp when the operation was last updated.

#### Response Example
```json
{
  "operation": {
    "id": "97c7a650-e4ff-43d7-8c58-4c67f5050167",
    "project_id": "autumn-disk-484331",
    "branch_id": "br-wispy-dew-591433",
    "endpoint_id": "ep-orange-art-714542",
    "action": "check_availability",
    "status": "finished",
    "failures_count": 0,
    "created_at": "2022-12-09T08:47:52Z",
    "updated_at": "2022-12-09T08:47:56Z"
  }
}
```
```

--------------------------------

### Implement Todo Controller (C#)

Source: https://neon.com/docs/guides/dotnet-entity-framework

A RESTful controller for managing Todo items. It uses Entity Framework to perform CRUD operations like fetching all todos (GET) and creating a new todo (POST).

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using NeonEfExample.Data;
using NeonEfExample.Models;

namespace NeonEfExample.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class TodoController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public TodoController(ApplicationDbContext context)
        {
            _context = context;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<Todo>>> GetTodos()
        {
            return await _context.Todos.ToListAsync();
        }

        [HttpPost]
        public async Task<ActionResult<Todo>> PostTodo(Todo todo)
        {
            _context.Todos.Add(todo);
            await _context.SaveChangesAsync();
            return CreatedAtAction(nameof(GetTodos), new { id = todo.Id }, todo);
        }
    }
}
```

--------------------------------

### Manage Neon Projects with Pulumi

Source: https://neon.com/docs/changelog/2025-10-10

This snippet demonstrates how to import the Neon Pulumi provider for infrastructure-as-code management of Neon projects. It requires the Pulumi CLI and the Neon provider to be installed.

```typescript
import * as neon from '@pulumi/neon';
```

--------------------------------

### Create Neon Project, Connect with psql, and Run Query

Source: https://neon.com/docs/reference/cli-projects

Creates a new Neon project, connects using psql, and executes a single SQL query. The `-- -c` flag is used to specify the query string.

```bash
neon project create --psql -- -c "SELECT version()"
```

--------------------------------

### JavaScript SDK: Execute a Stored Procedure (RPC)

Source: https://neon.com/docs/data-api/get-started

This snippet demonstrates how to call a stored procedure (Remote Procedure Call - RPC) using the Neon JavaScript SDK. You provide the function name and any necessary parameters as an object.

```javascript
client.rpc('function_name', { param: 'value' })
```

--------------------------------

### Deno JSON Configuration for Neon Serverless Driver

Source: https://neon.com/docs/guides/deno

Example `deno.json` file configuration after adding the Neon serverless driver. This JSON file specifies the import map for the Neon serverless package, ensuring that your Deno application can correctly resolve and use the driver.

```json
{
  "imports": {
    "@neon/serverless": "jsr:@neon/serverless@^0.10.1"
  }
}
```

--------------------------------

### Basic Neon Local Docker Run Configuration

Source: https://neon.com/docs/local/neon-local

This is a basic Docker run command to start the Neon Local container, mapping port 5432 for database access. It requires your Neon API key and project ID for authentication and project identification.

```bash
docker run \
  --name db \
  -p 5432:5432 \
  -e NEON_API_KEY=<your_neon_api_key> \
  -e NEON_PROJECT_ID=<your_neon_project_id> \
  neondatabase/neon_local:latest
```

--------------------------------

### Neon Database Connection Strings

Source: https://neon.com/docs/guides/liquibase-workflow

Provides example PostgreSQL connection strings for development (feature branch) and production databases in Neon. These strings include hostname, username, password, and SSL settings, crucial for establishing database connections.

```plaintext
postgresql://alex:AbC123dEf@ep-cool-darkness-123456.us-east-2.aws.neon.tech/blog?sslmode=require&channel_binding=require
```

```plaintext
postgresql://alex:AbC123dEf@ep-silent-hill-85675036.us-east-2.aws.neon.tech/blog?sslmode=require&channel_binding=require
```

--------------------------------

### Key Imports for Neon Authentication

Source: https://neon.com/docs/ai/ai-rules-neon-auth

Lists essential imports for integrating Neon authentication into Next.js, vanilla JavaScript, and React applications. Includes imports for auth clients, React adapters, UI components, and CSS.

```typescript
// Auth client (Next.js)
import { authApiHandler, createAuthClient } from "@neondatabase/auth/next";

// Auth client (vanilla)
import { createAuthClient } from "@neondatabase/auth";

// React adapter (NOT from main entry)
import { BetterAuthReactAdapter } from "@neondatabase/auth/react/adapters";

// UI components
import { NeonAuthUIProvider, AuthView, SignInForm } from "@neondatabase/auth/react/ui";
import { authViewPaths } from "@neondatabase/auth/react/ui/server";

// CSS
import "@neondatabase/auth/ui/css";
```

--------------------------------

### Enable pg_partman Extension in Neon SQL

Source: https://neon.com/docs/extensions/pg_partman

This snippet shows how to create the `partman` schema and enable the `pg_partman` extension within it. This is a prerequisite for using `pg_partman` for automated data partitioning in Neon.

```sql
CREATE SCHEMA partman;
CREATE EXTENSION pg_partman SCHEMA partman;
```

--------------------------------

### Prisma 'Can't reach database server' Error Example

Source: https://neon.com/docs/connect/connection-errors

This error occurs when Prisma Client cannot connect to the Neon database server, often due to timeouts during compute activation after an idle period. The example shows the error message and the server details.

```plaintext
Error: P1001: Can't reach database server at `ep-white-thunder-826300.us-east-2.aws.neon.tech`:`5432`
Please make sure your database server is running at `ep-white-thunder-826300.us-east-2.aws.neon.tech`:`5432`.
```

--------------------------------

### Get Cloudinary Upload Signature using cURL

Source: https://neon.com/docs/guides/cloudinary

This cURL command demonstrates how to request an upload signature from the backend. It sends a GET request to the '/generate-signature' endpoint and expects a JSON response containing the signature, timestamp, and API key needed for direct Cloudinary uploads.

```bash
curl -X GET http://localhost:3000/generate-signature
```

--------------------------------

### Set up Sample Table and Insert Data for Full-Text Search

Source: https://neon.com/docs/extensions/dict_int

This SQL script defines a 'documents' table with 'id', 'title', 'content', and 'version_code' fields, and then populates it with sample data. The 'version_code' field is intended to demonstrate full-text search capabilities, particularly with custom configurations handling numeric variations.

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    version_code TEXT
);

INSERT INTO documents (title, content, version_code) VALUES
('Intro Guide', 'Content of version 1...', '1'),
('Advanced Manual', 'More content...', '0042'),
('Internal Spec', 'Spec details...', '7654321'),
('Internal Spec v2', 'Updated spec...', '+7654321'),
('Draft Notes', 'Preliminary ideas...', 'ver003');
```

--------------------------------

### Example Ad-Hoc SQL Query

Source: https://neon.com/docs/guides/read-replica-adhoc-queries

This SQL query demonstrates a common ad-hoc query pattern for calculating total sales for a product over the last month. It utilizes standard SQL functions and date interval calculations.

```sql
SELECT product_id, SUM(sale_amount)
FROM sales
WHERE sale_date >= (CURRENT_DATE - INTERVAL '1 month')
GROUP BY product_id;
```

--------------------------------

### Create and Use GIN Index for Array Data in Postgres

Source: https://neon.com/docs/postgresql/index-types

Illustrates creating a table with an array column and indexing it using a GIN index. It includes examples of queries to find products based on array containment and overlap.

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    tags TEXT[]
);

INSERT INTO products (name, tags) VALUES
    ('Smartphone', ARRAY['electronics', 'mobile', 'communication']),
    ('Laptop', ARRAY['electronics', 'computer', 'portable']),
    ('Headphones', ARRAY['electronics', 'audio', 'accessories']);

CREATE INDEX idx_products_tags ON products USING gin (tags);

-- Find products with specific tags
SELECT * FROM products WHERE tags @> ARRAY['electronics', 'portable'];

-- Find products with any of the given tags
SELECT * FROM products WHERE tags && ARRAY['audio', 'mobile'];
```

--------------------------------

### Run Database Migrations (Rails CLI)

Source: https://neon.com/docs/guides/rails-migrations

Executes all pending database migration files to create the 'authors' and 'books' tables in the Neon Postgres database. It also creates internal bookkeeping tables.

```bash
rails db:migrate
```

--------------------------------

### Get Direct Connection String (Neon CLI)

Source: https://neon.com/docs/connect/choose-connection

Retrieves a direct connection string for Neon using the Neon CLI. Direct connections are suitable for migrations or admin tasks requiring stable connections.

```bash
neon connection-string [branch_name]

```

--------------------------------

### Configure online_advisor Session Settings

Source: https://neon.com/docs/extensions/online_advisor

This example demonstrates how to change session-level settings for the online_advisor extension. By using the `SET` command, you can temporarily adjust parameters like `online_advisor.filtered_threshold` for the current session. This allows for fine-tuning the extension's behavior without altering system-wide defaults.

```sql
SET online_advisor.filtered_threshold = 2000;

```

--------------------------------

### GET /consumption_history/projects

Source: https://neon.com/docs/manage/orgs-api-consumption

Retrieves granular daily, hourly, or monthly metrics for each project within a specified time period.

```APIDOC
## GET /consumption_history/projects

### Description
Retrieves granular consumption metrics (daily, hourly, or monthly) for each project within a specified time period. This endpoint is useful for analyzing project-specific resource usage over time.

### Method
GET

### Endpoint
`/consumption_history/projects`

### Parameters
#### Query Parameters
- **limit** (integer) - Optional - The maximum number of projects to return.
- **from** (string) - Required - The start date and time for the metrics in ISO 8601 format (e.g., `2024-06-30T00:00:00Z`).
- **to** (string) - Required - The end date and time for the metrics in ISO 8601 format (e.g., `2024-07-02T00:00:00Z`).
- **granularity** (string) - Required - The time granularity of the metrics (e.g., `hourly`, `daily`, `monthly`).
- **org_id** (string) - Required - The ID of the organization to retrieve project metrics for.

### Request Example
```json
{
  "example": "curl --request GET \
     --url 'https://console.neon.tech/api/v2/consumption_history/projects?limit=10&from=2024-06-30T00%3A00%3A00Z&to=2024-07-02T00%3A00%3A00Z&granularity=hourly&org_id=org-ocean-art-12345678' \
     --header 'accept: application/json' \
     --header 'authorization: Bearer $ORG_API_KEY'"
}
```

### Response
#### Success Response (200)
- **projects** (array) - An array of project objects, each containing detailed consumption data.
  - **project_id** (string) - The unique identifier for the project.
  - **periods** (array) - An array of billing periods for the project.
    - **period_id** (string) - The unique identifier for the billing period.
    - **period_plan** (string) - The plan associated with the billing period.
    - **period_start** (string) - The start date and time of the billing period.
    - **consumption** (array) - An array of consumption data points for the period.
      - **timeframe_start** (string) - The start of the consumption timeframe.
      - **timeframe_end** (string) - The end of the consumption timeframe.
      - **active_time_seconds** (integer) - The number of seconds the project's computes were active.
      - **compute_time_seconds** (integer) - The total CPU seconds used by the project's computes.
      - **written_data_bytes** (integer) - The total amount of data written to all of a project's branches.
      - **synthetic_storage_size_bytes** (integer) - The total space occupied in storage (logical data size + WAL size).

#### Response Example
```json
{
  "example": "{\n  \"projects\": [\n    {\n      \"project_id\": \"random-project-123456\",\n      \"periods\": [\n        {\n          \"period_id\": \"random-period-abcdef\",\n          \"period_plan\": \"scale\",\n          \"period_start\": \"2024-06-30T00:00:00Z\",\n          \"consumption\": [\n            {\n              \"timeframe_start\": \"2024-06-30T00:00:00Z\",\n              \"timeframe_end\": \"2024-06-30T01:00:00Z\",\n              \"active_time_seconds\": 147472,\n              \"compute_time_seconds\": 43222,\n              \"written_data_bytes\": 112730864,\n              \"synthetic_storage_size_bytes\": 37000959232\n            },\n            {\n              \"timeframe_start\": \"2024-07-01T00:00:00Z\",\n              \"timeframe_end\": \"2024-07-01T01:00:00Z\",\n              \"active_time_seconds\": 1792,\n              \"compute_time_seconds\": 533,\n              \"written_data_bytes\": 0,\n              \"synthetic_storage_size_bytes\": 0\n            }\n            // ... More consumption data\n          ]\n        },\n        {\n          \"period_id\": \"random-period-ghijkl\",\n          \"period_plan\": \"scale\",\n          \"period_start\": \"2024-07-01T09:00:00Z\",\n          \"consumption\": [\n            {\n              \"timeframe_start\": \"2024-07-01T09:00:00Z\",\n              \"timeframe_end\": \"2024-07-01T10:00:00Z\",\n              \"active_time_seconds\": 150924,\n              \"compute_time_seconds\": 44108,\n              \"written_data_bytes\": 114912552,\n              \"synthetic_storage_size_bytes\": 36593552376\n            }\n            // ... More consumption data\n          ]\n        }\n        // ... More periods\n      ]\n    }\n    // ... More projects\n  ]\n}"
}
```
```

--------------------------------

### MDX Template Structure with Frontmatter

Source: https://neon.com/docs/community/component-architecture

Presents the standard structure of shared MDX template files, including frontmatter for metadata like title and description, followed by the main content.

```markdown
---
title: Feature Beta
description: Beta feature announcement
---

This feature is currently in beta...
```

--------------------------------

### Initialize Postgres Vector Store

Source: https://neon.com/docs/ai/semantic-kernel

This C# code snippet demonstrates how to create and configure a PostgreSQL vector store using Npgsql and Semantic Kernel. It requires the Npgsql package and the `UseVector()` extension. The output confirms successful vector store creation.

```csharp
// File: Program.cs

using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Connectors.Postgres;
using Microsoft.SemanticKernel.Connectors.AzureOpenAI;
using Npgsql;
using System;
using System.Threading.Tasks;

class Program
{
    static async Task Main()
    {
        string connectionString = "Host=myhost;Username=myuser;Password=mypass;Database=mydb";

        // Step 1: Create and configure the vector store
        var dataSourceBuilder = new NpgsqlDataSourceBuilder(connectionString);
        dataSourceBuilder.UseVector();
        using var dataSource = dataSourceBuilder.Build();
        var vectorStore = new PostgresVectorStore(dataSource);
        Console.WriteLine("✅ Vector store created successfully.");

        // ... rest of the code
    }
}

```

--------------------------------

### Run PostgREST with Unpooled Connection (Docker)

Source: https://neon.com/docs/guides/postgrest

This command starts the PostgREST server using Docker, connecting directly to your Neon database without connection pooling. It sets the database URI, schema, and anonymous role. Ensure you replace the placeholder with your actual unpooled connection string from the Neon Console.

```docker
docker run --rm --net=host \
  -e PGRST_DB_URI="<non-pooled-connection-string-from-neon-console>" \
  -e PGRST_DB_SCHEMA="api" \
  -e PGRST_DB_ANON_ROLE="anonymous" \
  postgrest/postgrest
```

--------------------------------

### Creating GiST and GIN Indexes for pg_trgm

Source: https://neon.com/docs/extensions/pg_trgm

Provides examples of creating GiST and GIN indexes on a text column using pg_trgm operators. These indexes significantly speed up similarity search queries and regular expression searches.

```sql
CREATE INDEX trgm_idx_gist ON books USING GIST (title gist_trgm_ops);
-- or
CREATE INDEX trgm_idx_gin ON books USING GIN (title gin_trgm_ops);
```

--------------------------------

### Enable pgstattuple Extension in Neon

Source: https://neon.com/docs/extensions/pgstattuple

This SQL command enables the pgstattuple extension within your Neon database. It ensures the extension is installed if it doesn't already exist. This is a prerequisite for using the extension's analytical functions.

```sql
CREATE EXTENSION IF NOT EXISTS pgstattuple;
```

--------------------------------

### Postgres lower() function example

Source: https://neon.com/docs/functions/lower

Demonstrates the basic usage of the `lower()` function to convert strings in a column to lowercase. This is useful for standardizing data for display or comparison.

```sql
WITH products AS (
    SELECT *
    FROM (
        VALUES
            ('LAPTOP Pro X'),
            ('SmartPhone Y'),
            ('Tablet ULTRA 2')
    ) AS t(product_name)
)
SELECT lower(product_name) AS standardized_name
FROM products;
```

--------------------------------

### Postgres abs() Example: Distance Calculations

Source: https://neon.com/docs/functions/math-abs

This PostgreSQL example illustrates using the abs() function for distance calculations, where direction is irrelevant. It finds locations within a specified latitude and longitude range of a reference point, demonstrating its utility in geographical or spatial analysis.

```sql
WITH locations(name, latitude, longitude) AS (
  VALUES
    ('Point A', 40.7128, -74.0060),
    ('Point B', 40.7484, -73.9857),
    ('Point C', 41.6892, -74.0445),
    ('Reference', 40.7300, -73.9950)
)
SELECT
  name,
  abs(latitude - 40.7300) AS lat_diff,
  abs(longitude - (-73.9950)) AS long_diff
FROM locations
WHERE
  abs(latitude - 40.7300) <= 0.05 AND
  abs(longitude - (-73.9950)) <= 0.05;
```

--------------------------------

### Load SQL Data using Neon CLI (New Project)

Source: https://neon.com/docs/import/import-sample-data

Loads a specified SQL file into a newly created Neon project using the Neon CLI. The `--psql` option ensures the file is processed by psql.

```bash
neon projects create --psql -- -f periodic_table.sql
```

--------------------------------

### GraphQL Schema: Define Get Customer Query

Source: https://neon.com/docs/guides/stepzen

Defines a GraphQL query 'getCustomer' that takes an integer 'id' as input and retrieves a single 'Customer' object from the 'customer' table in the PostgreSQL database. It uses the '@dbquery' directive for database interaction.

```graphql
type Query {
  getCustomer(id: Int!): Customer
    @dbquery(
      type: "postgresql"
      schema: "public"
      table: "customer"
      configuration: "postgresql_config"
    )
}
```

--------------------------------

### Connect to Neon Read Replica (Connection String)

Source: https://neon.com/docs/guides/read-only-access-read-replicas

This is an example of a PostgreSQL connection string for a Neon read replica. It includes the username, password, host, database name, and SSL mode parameters. Ensure to replace placeholders with your actual credentials and connection details.

```sql
postgresql://partner:partner_password@ep-read-replica-12345.us-east-2.aws.neon.tech/sales_db?sslmode=require&channel_binding=require
```

--------------------------------

### Python Prepared Statement with PgBouncer

Source: https://neon.com/docs/connect/connection-pooling

This Python snippet shows how to utilize prepared statements with the 'psycopg2' library, which supports PgBouncer's protocol-level requirements. It outlines the query structure and provides the parameter value for execution.

```python
# Example for psycopg2 would typically involve cursors and execute method with parameters
# cursor.execute("SELECT * FROM users WHERE username = %s", ('alice',))
# Note: Actual psycopg2 code for prepared statements often involves server-side prepare
# or client-side parameter substitution which achieves similar security/performance goals.
```

--------------------------------

### Get masking rules

Source: https://neon.com/docs/workflows/data-anonymization

Retrieves all masking rules defined for the specified anonymized branch.

```APIDOC
## GET /projects/{project_id}/branches/{branch_id}/masking_rules

### Description
Retrieves all masking rules defined for the specified anonymized branch.

### Method
GET

### Endpoint
`/projects/{project_id}/branches/{branch_id}/masking_rules`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The ID of the project.
- **branch_id** (string) - Required - The ID of the branch.

### Response
#### Success Response (200)
- **masking_rules** (array) - A list of masking rules.
  - **database_name** (string) - The name of the database.
  - **schema_name** (string) - The name of the schema.
  - **table_name** (string) - The name of the table.
  - **column_name** (string) - The name of the column.
  - **masking_function** (string) - The masking function to apply.

#### Response Example
```json
{
  "masking_rules": [
    {
      "database_name": "neondb",
      "schema_name": "public",
      "table_name": "users",
      "column_name": "age",
      "masking_function": "anon.random_int_between(25,65)"
    },
    {
      "database_name": "neondb",
      "schema_name": "public",
      "table_name": "users",
      "column_name": "email",
      "masking_function": "anon.dummy_free_email()"
    }
  ]
}
```
```

--------------------------------

### Deploy to Staging Environment

Source: https://neon.com/docs/guides/encore

Deploys the Encore application to the staging environment using git commands. This includes adding, committing, and pushing code to the 'encore' remote.

```bash
git add -A
git commit -m "Initial commit"
git push encore
```

--------------------------------

### Create Preview Environment Branch (JSON)

Source: https://neon.com/docs/ai/ai-database-versioning

Creates a temporary branch for previewing a version without affecting the active branch. `finalize_restore` set to false ensures a new branch is created for the preview, leaving the active branch untouched. These preview branches should be deleted after use to avoid storage costs.

```json
{
  "name": "preview-version-123",
  "finalize_restore": false // Creates new branch for preview without moving computes
}
```

--------------------------------

### GET /v2/organizations/{orgId}/invitations

Source: https://neon.com/docs/ai/ai-rules-neon-typescript-sdk

Retrieves a list of outstanding invitations for a given organization.

```APIDOC
## GET /v2/organizations/{orgId}/invitations

### Description
Retrieves a list of outstanding invitations for an organization.

### Method
GET

### Endpoint
`/v2/organizations/{orgId}/invitations`

### Parameters
#### Path Parameters
- **orgId** (string) - Required - The organization ID

### Request Example
```json
{
  "example": ""
}
```

### Response
#### Success Response (200)
- **invitations** (array of objects) - A list of outstanding invitations.
  - **email** (string) - The email address of the invited user.
  - **role** (string) - The role assigned to the invited user.
  - **expiresAt** (string) - The expiration date of the invitation.

#### Response Example
```json
{
  "invitations": [
    {
      "email": "invited.user@example.com",
      "role": "member",
      "expiresAt": "2024-10-26T10:00:00Z"
    }
  ]
}
```
```

--------------------------------

### Component Directory Organization in Neon Website

Source: https://neon.com/docs/community/component-architecture

Demonstrates the standard file structure for MDX components within the Neon website repository, including the main implementation, export file, and asset directory.

```text
src/components/pages/doc/
├── {component-name}/
│   ├── {component-name}.jsx          # Main component implementation
│   ├── index.js                      # Export file
│   └── images/                       # Component-specific assets
│       └── {icons}.inline.svg        # Inline SVG icons
├── shared/                           # Shared components
│   ├── request-form/
│   └── ...
└── ...

```

--------------------------------

### Provision Neon Auth

Source: https://neon.com/docs/ai/neon-mcp-server

Provisions Neon Auth for a Neon project by creating an integration with an Auth provider, simplifying authentication infrastructure setup.

```tool_code
provision_neon_auth
```

--------------------------------

### pg_repack syntax for dry run preview

Source: https://neon.com/docs/extensions/pg_repack

Demonstrates how to perform a dry run with pg_repack to preview the operations without making any actual changes to the table or indexes. Includes connection parameters.

```bash
pg_repack -k -N -h <your_neon_host> -p 5432 -d <your_neon_database> -U <your_neon_username> --table your_table_name
```

--------------------------------

### JavaScript: Setup Neon, Hono, and AWS S3 for B2 Uploads

Source: https://neon.com/docs/guides/backblaze-b2

Initializes the Neon database connection, Hono web server, and AWS S3 client for Backblaze B2. It configures the S3 client with B2 endpoint details and credentials, extracts the region, and sets up a placeholder authentication middleware. This snippet forms the foundation for the upload workflow.

```javascript
import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
import { neon } from '@neondatabase/serverless';
import 'dotenv/config';
import { randomUUID } from 'crypto';

const B2_BUCKET = process.env.B2_BUCKET_NAME;
const B2_ENDPOINT = process.env.B2_ENDPOINT_URL;
const endpointUrl = new URL(B2_ENDPOINT);
const region = endpointUrl.hostname.split('.')[1];

const s3 = new S3Client({
  endpoint: B2_ENDPOINT,
  region: region,
  credentials: {
    accessKeyId: process.env.B2_APPLICATION_KEY_ID,
    secretAccessKey: process.env.B2_APPLICATION_KEY,
  },
});
const sql = neon(process.env.DATABASE_URL);
const app = new Hono();

// Replace this with your actual user authentication logic, by validating JWTs/Headers, etc.
const authMiddleware = async (c, next) => {
  c.set('userId', 'user_123');
  await next();
};

// 1. Generate presigned URL for upload
app.post('/presign-b2-upload', authMiddleware, async (c) => {
  try {
    const { fileName, contentType } = await c.req.json();
    if (!fileName || !contentType) throw new Error('fileName and contentType required');

    const objectKey = `${randomUUID()}-${fileName}`;
    const publicFileUrl = `${B2_ENDPOINT}/${B2_BUCKET}/${objectKey}`;

    const command = new PutObjectCommand({
      Bucket: B2_BUCKET,
      Key: objectKey,
      ContentType: contentType,
    });
    const presignedUrl = await getSignedUrl(s3, command, { expiresIn: 300 }); // 5 min expiry

    return c.json({ success: true, presignedUrl, objectKey, publicFileUrl });
  } catch (error) {
    console.error('Presign Error:', error.message);
    return c.json({ success: false, error: 'Failed to prepare upload' }, 500);
  }
});

// 2. Save metadata after client upload confirmation
app.post('/save-b2-metadata', authMiddleware, async (c) => {
  try {
    const { objectKey, publicFileUrl } = await c.req.json();
    const userId = c.get('userId');
    if (!objectKey) throw new Error('objectKey required');

    await sql`
      INSERT INTO b2_files (object_key, file_url, user_id)
      VALUES (${objectKey}, ${publicFileUrl}, ${userId})
    `;
    console.log(`Metadata saved for B2 object: ${objectKey}`);
    return c.json({ success: true });
  } catch (error) {
    console.error('Metadata Save Error:', error.message);
    return c.json({ success: false, error: 'Failed to save metadata' }, 500);
  }
});

const port = 3000;
serve({ fetch: app.fetch, port }, (info) => {
  console.log(`Server running at http://localhost:${info.port}`);
});

```

--------------------------------

### Initialize Neon API Client (TypeScript)

Source: https://neon.com/docs/ai/ai-rules-neon-typescript-sdk

Initializes the Neon API client using an API key loaded from environment variables. This client instance is then used for all subsequent API interactions. It requires the '@neondatabase/api-client' package and expects the NEON_API_KEY environment variable to be set.

```typescript
import { createApiClient } from '@neondatabase/api-client';

// Best practice: Load API key from environment variables
const apiKey = process.env.NEON_API_KEY;

if (!apiKey) {
  throw new Error('NEON_API_KEY environment variable is not set.');
}

const apiClient = createApiClient({ apiKey });
```

--------------------------------

### Extension Settings

Source: https://neon.com/docs/extensions/pg_cron

View the current configuration of the pg_cron extension within your Neon database. Note that these settings are managed by Neon and cannot be directly modified by users.

```APIDOC
## Extension Settings

`pg_cron` has several configuration parameters that influence its behavior. These settings are managed by Neon and cannot be directly modified by users. Understanding these settings can be helpful for monitoring and troubleshooting. You can view the current configuration in your Neon database using the following query:

```sql
SELECT * FROM pg_settings WHERE name LIKE 'cron.%';
```

Here are a few key `pg_cron` settings and their descriptions:

| Setting | Default | Description |
|---|---|---|
| `cron.launch_active_jobs` | `on` | When set to `off`, this setting disables all active `pg_cron` jobs without requiring a server restart. |
| `cron.log_min_messages` | `WARNING` | This setting determines the minimum severity level of log messages generated by the `pg_cron` launcher background worker. |
| `cron.log_run` | `on` | When enabled (`on`), details of each job run are logged in the `cron.job_run_details` table. |
| `cron.log_statement` | `on` | If enabled (`on`), the SQL command of each scheduled job is logged before execution. |
| `cron.max_running_jobs` | `32` | This parameter defines the maximum number of `pg_cron` jobs that can run concurrently. |
| `cron.timezone` | `GMT` | Specifies the timezone in which the `pg_cron` background worker operates. **Note:** Although this setting exists, `pg_cron` internally interprets all job schedules in UTC. Changing this parameter has no effect on how schedules are executed. |
| `cron.use_background_workers` | `off` | When enabled (`on`), `pg_cron` uses background workers instead of direct client connections to execute jobs. This may require adjustments to the `max_worker_processes` PostgreSQL setting. |

#### Important: Setting Modifications in Neon

It's important to note that because `pg_cron` is managed by Neon, modifying these settings requires superuser privileges. Therefore, you cannot directly alter these `pg_cron` configuration parameters yourself. If you have a specific need to adjust any of these settings, please open a support ticket. **After Neon support implements the requested configuration change, you will need to restart your Neon compute for the new settings to take effect.**
```

--------------------------------

### Create and Use BRIN Index for Ordered Data in Postgres

Source: https://neon.com/docs/postgresql/index-types

Shows how to create a table for temperature readings and index the timestamp column using a BRIN index. It includes a range query example to retrieve readings within a specific date range.

```sql
CREATE TABLE temperature_readings (
    id SERIAL PRIMARY KEY,
    sensor_id INT NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO temperature_readings (sensor_id, temperature, timestamp)
SELECT
    (random() * 100)::int,
    (random() * 50 - 10)::decimal(5,2),
    timestamp '2024-01-01 00:00:00' + (random() * (interval '365 days'))
FROM generate_series(1, 100000);

CREATE INDEX idx_temperature_brin ON temperature_readings USING brin (timestamp);

-- Find temperature readings within a specific date range
SELECT *
FROM temperature_readings
WHERE timestamp BETWEEN '2024-03-01' AND '2024-03-31';
```

--------------------------------

### Create Table with hstore Column in Neon

Source: https://neon.com/docs/extensions/hstore

Example SQL for creating a table named 'product' with an 'attributes' column of type HSTORE. This is useful for storing semi-structured product attributes where the schema may change.

```sql
CREATE TABLE product (
   id SERIAL PRIMARY KEY,
   name VARCHAR(255),
   attributes HSTORE
);
```

--------------------------------

### Insert Sample Data into Neon Table

Source: https://neon.com/docs/guides/cloudflare-workers

SQL command to insert sample book data into the 'books_to_read' table. This data will be used for querying and testing the database connection. Requires the 'books_to_read' table to exist.

```sql
INSERT INTO books_to_read (title, author)
VALUES
    ('The Way of Kings', 'Brandon Sanderson'),
    ('The Name of the Wind', 'Patrick Rothfuss'),
    ('Coders at Work', 'Peter Seibel'),
    ('1984', 'George Orwell');
```

--------------------------------

### Generate Wrangler Types and Run RedwoodSDK App

Source: https://neon.com/docs/guides/redwoodsdk

Commands to generate necessary types for RedwoodSDK's environment variable detection using Wrangler and to start the development server.

```bash
npx wrangler types
npm run dev
```

--------------------------------

### Create Application Database Context (C#)

Source: https://neon.com/docs/guides/dotnet-entity-framework

Sets up the Entity Framework database context for the application. It inherits from DbContext and includes a DbSet for the Todo entity, enabling database operations.

```csharp
using Microsoft.EntityFrameworkCore;
using NeonEfExample.Models;

namespace NeonEfExample.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        public DbSet<Todo> Todos => Set<Todo>();
    }
}
```

--------------------------------

### Generate EF Core Migration Files via .NET CLI

Source: https://neon.com/docs/guides/entity-migrations

Uses the .NET Command Line Interface (CLI) to generate the initial migration file for the defined data models. This command inspects the 'ApplicationDbContext' and its entities ('Author', 'Book') to create the necessary SQL scripts for database table creation. Requires the EF Core tools to be installed.

```bash
dotnet ef migrations add InitialCreate
```

--------------------------------

### Import Neon Auth UI CSS

Source: https://neon.com/docs/ai/ai-rules-neon-auth

Import the necessary CSS for the Neon Auth UI components. This is typically done in the main layout file of a Next.js application.

```tsx
import "@neondatabase/auth/ui/css";
```

--------------------------------

### Show Preloaded Libraries in Neon

Source: https://neon.com/docs/extensions/pg-extensions

This SQL command displays the currently enabled shared preloaded libraries on your Neon Postgres server. These libraries are loaded into memory when the server starts and are essential for certain extensions.

```sql
SHOW shared_preload_libraries;
```

--------------------------------

### Composable SQL Template Queries with Parameters

Source: https://neon.com/docs/serverless/serverless-driver

Illustrates how SQL template queries can be composed, even with parameters. Parameters are automatically numbered correctly when the query is executed, ensuring proper handling.

```javascript
const name = 'Olivia';
const limit = 1;
const whereClause = sql`WHERE name = ${name}`;
const limitClause = sql`LIMIT ${limit}`;

// Parameters are numbered appropriately at query time
const result = await sql`SELECT * FROM table ${whereClause} ${limitClause}`;
```

--------------------------------

### Run Laravel Artisan Commands

Source: https://neon.com/docs/guides/laravel-migrations

Provides common Laravel Artisan commands for development and database management. 'php artisan serve' starts the development server, and 'php artisan migrate' applies pending database migrations.

```bash
php artisan serve
```

```bash
php artisan make:migration add_country_to_authors_table
```

```bash
php artisan migrate
```

--------------------------------

### Postgres regexp_replace() Example: Anonymizing Email Addresses

Source: https://neon.com/docs/functions/regexp_replace

This example illustrates the use of `regexp_replace()` with backreferences in PostgreSQL to anonymize email addresses within log entries. It captures specific parts of the log string and reconstructs it, replacing the matched email address with a placeholder while maintaining the overall log structure.

```sql
WITH log_data AS (
  SELECT '2023-05-15 10:30:00 - User john.doe@example.com logged in' AS log_entry
  UNION ALL
  SELECT '2023-05-15 11:45:30 - User jane.smith@example.org logged out' AS log_entry
)
SELECT
  log_entry AS original_log,
  regexp_replace(log_entry, '(.*) - User (.+@.+)(.+)', '\1 - User [REDACTED]\3') AS anonymized_log
FROM log_data;
```

--------------------------------

### Run Flyway Migration with Environment Configuration

Source: https://neon.com/docs/guides/flyway-multiple-environments

This command initiates the Flyway migration process, specifying which environment configuration file to use. By running this for each environment's configuration file, you ensure consistent database schema deployment across development, staging, and production.

```bash
flyway migrate -configFiles="conf/env_dev.conf"
```

--------------------------------

### Configure Prisma Client with Read Replicas

Source: https://neon.com/docs/guides/read-replica-prisma

Extend your Prisma Client instance with the readReplicas extension, providing the read replica URL. This setup routes read operations to the replica and write operations to the primary database.

```typescript
import { PrismaClient } from '@prisma/client';
import { readReplicas } from '@prisma/extension-read-replicas';

const prisma = new PrismaClient().$extends(
  readReplicas({
    url: DATABASE_REPLICA_URL,
  })
);
```

--------------------------------

### Configure Encore SQL Database (TypeScript)

Source: https://neon.com/docs/guides/encore

Configures a SQL database named 'hello' using Encore's SQLDatabase abstraction. It specifies the migration directory for database schema changes.

```typescript
import { SQLDatabase } from 'encore.dev/storage/sqldb';

export const db = new SQLDatabase('hello', {
  migrations: './migrations',
});
```

--------------------------------

### Connect to Neon with Neon Serverless Driver

Source: https://neon.com/docs/guides/javascript

Demonstrates connecting to a Neon Postgres database using the '@neondatabase/serverless' driver, which operates over HTTP and is optimized for serverless environments. The connection string is loaded from environment variables. Ensure '@neondatabase/serverless' is installed and DATABASE_URL is set.

```javascript
import neon, { sql } from '@neondatabase/serverless';
import dotenv from 'dotenv';

dotenv.config();

const neonClient = neon(process.env.DATABASE_URL);

async function queryDatabase() {
  try {
    const result = await neonClient`SELECT NOW()`;
    console.log('Current time from Neon:', result.rows[0].now);
  } catch (err) {
    console.error('Error executing query', err.stack);
  } finally {
    await neonClient.end();
  }
}

queryDatabase();
```

--------------------------------

### Get Books by Author

Source: https://neon.com/docs/guides/sequelize

Retrieves a list of books written by a specific author, identified by their ID.

```APIDOC
## GET /books/:author_id

### Description
Retrieves a list of books written by a specific author, identified by their `author_id`.

### Method
GET

### Endpoint
/books/:author_id

### Parameters
#### Path Parameters
- **author_id** (integer) - Required - The ID of the author whose books are to be retrieved.

### Request Example
None

### Response
#### Success Response (200)
- **books** (array) - An array of book objects.
  - **id** (integer) - The unique identifier for the book.
  - **title** (string) - The title of the book.
  - **authorId** (integer) - The ID of the author of the book.
  - **createdAt** (string) - Timestamp of creation.
  - **updatedAt** (string) - Timestamp of last update.

#### Response Example
```json
[
  {
    "id": 1,
    "title": "Harry Potter and the Philosopher's Stone",
    "authorId": 1,
    "createdAt": "2023-10-27T10:05:00.000Z",
    "updatedAt": "2023-10-27T10:05:00.000Z"
  }
]
```
```

--------------------------------

### Stack Auth JWKS URL Example

Source: https://neon.com/docs/data-api/custom-authentication-providers

The JWKS URL for Stack Auth requires your project ID. Replace the placeholder with your actual Stack Auth project ID to generate the correct URL.

```text
https://api.stack-auth.com/api/v1/projects/{YOUR_PROJECT_ID}/.well-known/jwks.json
```

--------------------------------

### JavaScript SDK: Filter Data with Case-Insensitive Like Operator

Source: https://neon.com/docs/data-api/get-started

This snippet demonstrates using the `.ilike()` method for case-insensitive pattern matching. It selects rows where the 'title' column contains 'hello', regardless of case.

```javascript
.ilike('title', '%hello%')
```

--------------------------------

### Connect to Neon Database with psql

Source: https://neon.com/docs/import/import-from-csv

This snippet shows how to connect to a Neon database using the psql command-line client. It requires a Neon database connection string, which can be found on the Neon Project Dashboard. Ensure you have psql installed.

```bash
psql "<your_neon_database_connection_string>"
```

--------------------------------

### GET /api/v2/consumption_history/account

Source: https://neon.com/docs/guides/consumption-metrics

Retrieves account consumption metrics within a specified time range and granularity.

```APIDOC
## GET /api/v2/consumption_history/account

### Description
Retrieves account consumption metrics within a specified time range and granularity.

### Method
GET

### Endpoint
/api/v2/consumption_history/account

### Parameters
#### Query Parameters
- **from** (date-time) - Required - Start date-time for the consumption period in RFC 3339 format.
- **to** (date-time) - Required - End date-time for the consumption period in RFC 3339 format.
- **granularity** (string) - Required - The granularity of consumption metrics. Options: `hourly`, `daily`, `monthly`.
- **org_id** (string) - Required - The ID of the organization to retrieve consumption history for.

### Request Example
```json
{
  "request": "curl --request GET \
  --url 'https://console.neon.tech/api/v2/consumption_history/account?from=2024-06-30T00:00:00Z&to=2024-07-02T00:00:00Z&granularity=daily&org_id=org-ocean-art-12345678' \
  --header 'accept: application/json' \
  --header 'authorization: Bearer $NEON_API_KEY'"
}
```

### Response
#### Success Response (200)
- **periods** (array) - An array of consumption periods.
  - **period_id** (string) - The ID of the consumption period.
  - **period_plan** (string) - The plan associated with the period.
  - **period_start** (date-time) - The start time of the period.
  - **period_end** (date-time) - The end time of the period.
  - **consumption** (array) - An array of consumption details for the period.
    - **timeframe_start** (date-time) - The start time of the consumption timeframe.
    - **timeframe_end** (date-time) - The end time of the consumption timeframe.
    - **active_time_seconds** (integer) - Active time in seconds.
    - **compute_time_seconds** (integer) - Compute time in seconds.
    - **written_data_bytes** (integer) - Data written in bytes.
    - **synthetic_storage_size_bytes** (integer) - Synthetic storage size in bytes.

#### Response Example
```json
{
  "periods": [
    {
      "period_id": "random-period-abcdef",
      "period_plan": "scale",
      "period_start": "2024-06-01T00:00:00Z",
      "period_end": "2024-07-01T00:00:00Z",
      "consumption": [
        {
          "timeframe_start": "2024-06-30T00:00:00Z",
          "timeframe_end": "2024-07-01T00:00:00Z",
          "active_time_seconds": 147452,
          "compute_time_seconds": 43215,
          "written_data_bytes": 111777920,
          "synthetic_storage_size_bytes": 41371988928
        },
        {
          "timeframe_start": "2024-07-01T00:00:00Z",
          "timeframe_end": "2024-07-02T00:00:00Z",
          "active_time_seconds": 147468,
          "compute_time_seconds": 43223,
          "written_data_bytes": 110483584,
          "synthetic_storage_size_bytes": 41467955616
        }
      ]
    }
  ]
}
```
```

--------------------------------

### Apply Terraform Configuration for Neon Resources

Source: https://neon.com/docs/reference/terraform

This section outlines the commands to apply Terraform configurations for managing Neon resources. It includes formatting and validation with `terraform fmt` and `terraform validate`, planning changes with `terraform plan`, and applying the changes with `terraform apply`. Always review the plan before applying.

```bash
terraform fmt
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
```

--------------------------------

### Documentation and Resources API

Source: https://neon.com/docs/ai/neon-mcp-server

Load Neon documentation and usage guidelines.

```APIDOC
## Documentation and Resources

### `load_resource`

Loads comprehensive Neon documentation and usage guidelines, including the "neon-get-started" guide for setup, configuration, and best practices.

**Method:** POST (assumed)

**Endpoint:** /actions

**Parameters**

#### Query Parameters
- **resource_name** (string) - Required - The name of the resource to load (e.g., 'neon-get-started').

```

--------------------------------

### Database URL Variable for Neon

Source: https://neon.com/docs/get-started/connect-neon

Demonstrates setting a `DATABASE_URL` environment variable with the complete Neon connection string. This is a common practice for ORMs and frameworks to easily access database connection information.

```bash
DATABASE_URL="postgresql://alex:AbC123dEf@ep-cool-darkness-a1b2c3d4.us-east-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require"
```

--------------------------------

### Retrieve Project Details with Curl

Source: https://neon.com/docs/introduction/monitor-usage

This snippet demonstrates how to fetch detailed information about a specific Neon project using the `curl` command-line tool. It targets the Get project details API endpoint and requires an API key for authentication. The output is formatted using `jq` for readability.

```bash
curl --request GET \
     --url https://console.neon.tech/api/v2/projects/summer-bush-30064139 \
     --header 'accept: application/json' \
     --header 'authorization: Bearer $NEON_API_KEY' |jq
```

--------------------------------

### Create Neon Branch, Connect with psql, and Run Query

Source: https://neon.com/docs/reference/cli-branches

This command creates a new Neon branch, connects to it using psql, and executes a single SQL query. This is convenient for quickly testing specific SQL commands on a new branch. Requires psql to be installed.

```bash
neon branch create --psql -- -c "SELECT version()"
```

--------------------------------

### Troubleshooting 'No space left on device' SQL Error

Source: https://neon.com/docs/manage/computes

This example shows a typical SQL error message indicating that a compute's local disk storage is full. It highlights the common cause related to temporary file usage by PostgreSQL and suggests strategies for resolution.

```sql
ERROR: could not write to file "base/pgsql_tmp/pgsql_tmp1234.56.fileset/o12of34.p1.0": No space left on device (SQLSTATE 53100)
```

--------------------------------

### List Projects with cURL

Source: https://neon.com/docs/manage/projects

This snippet demonstrates how to list all projects associated with your Neon account using a cURL command. It requires an API key for authentication and uses `jq` to pretty-print the JSON response. The response includes a list of projects, each with detailed configuration and status information.

```shell
curl 'https://console.neon.tech/api/v2/projects' \
 -H 'Accept: application/json' \
 -H "Authorization: Bearer $NEON_API_KEY" | jq
```

--------------------------------

### Create a Neon Project using cURL

Source: https://neon.com/docs/guides/embedded-postgres

This snippet demonstrates how to create a new project (Postgres database) for a user using the Neon API. It includes setting the project name, PostgreSQL version, and region. The response contains connection details.

```shell
curl --request POST \
     --url https://console.neon.tech/api/v2/projects \
     --header 'Accept: application/json' \
     --header "Authorization: Bearer $NEON_API_KEY" \
     --header 'Content-Type: application/json' \
     --data '{
  "project": {
    "name": "user-database-123",
    "pg_version": 16,
    "region_id": "aws-us-east-1"
  }
}' | jq
```

--------------------------------

### Diagnose DNS Resolution (Command Line)

Source: https://neon.com/docs/connect/connection-errors

Provides command-line examples for diagnosing DNS resolution issues with Neon hostnames using `nslookup`. It shows how to check for successful resolution and how to test using a public DNS resolver like Google DNS.

```bash
nslookup ep-cool-darkness-a1b2c3d4.ap-southeast-1.aws.neon.tech

```

```bash
nslookup ep-cool-darkness-a1b2c3d4.ap-southeast-1.aws.neon.tech 8.8.8.8

```

--------------------------------

### Deploying Node.js Application to Heroku

Source: https://neon.com/docs/guides/heroku

Deploys the current Node.js application to Heroku by pushing the local `main` branch to the `heroku` remote. Heroku automatically detects the Node.js environment, installs dependencies, and deploys the application.

```bash
> git push heroku main
. 
. 
. 
remote: -----> Launching... 
remote:        Released v4 
remote:        https://neon-heroku-example-fda03f6acbbe.herokuapp.com/ deployed to Heroku 
remote: 
remote: Verifying deploy... done. 
remote: 2024/02/21 07:26:49 Rollbar error: empty token 
To https://git.heroku.com/neon-heroku-example.git
remote: Verifying deploy... done.
```

--------------------------------

### Verify Migration with SQL Queries

Source: https://neon.com/docs/import/migrate-from-supabase

These SQL queries are used to verify that your data has been successfully migrated to Neon. Run these on your Neon database and compare the results with your original Supabase database to ensure data integrity. Examples include counting records and selecting a limited number of rows.

```sql
SELECT COUNT(*) FROM lego_sets;
SELECT * FROM lego_themes LIMIT 5;
```

--------------------------------

### Create Read Replica with Neon CLI

Source: https://neon.com/docs/get-started/production-readiness

This command demonstrates how to create a read-only branch, effectively a read replica, using the Neon CLI. This is useful for offloading read-only workloads from your primary database to enhance application scalability.

```bash
neon branches create --name my_read_replica_branch --type read_only
```

--------------------------------

### Create Netflix Data Database

Source: https://neon.com/docs/import/import-sample-data

This snippet guides through the creation of a 'netflix' database, downloading and importing the dataset, and connecting to it. It also provides a query to find the top 5 directors with the most movies listed in the database.

```sql
CREATE DATABASE netflix;

wget https://raw.githubusercontent.com/neondatabase/postgres-sample-dbs/main/netflix.sql

psql -d "postgresql://[user]:[password]@[neon_hostname]/netflix" -f netflix.sql

psql postgresql://[user]:[password]@[neon_hostname]/netflix

SELECT
    director,
    COUNT(*) AS "Number of Movies"
FROM
    netflix_shows
WHERE
    type = 'Movie'
GROUP BY
    director
ORDER BY
    "Number of Movies" DESC
LIMIT 5;
```

--------------------------------

### Get anonymization status

Source: https://neon.com/docs/workflows/data-anonymization

Retrieves the current status of an anonymized branch, including state and progress information.

```APIDOC
## GET /projects/{project_id}/branches/{branch_id}/anonymized_status

### Description
Retrieves the current status of an anonymized branch, including state and progress information.

### Method
GET

### Endpoint
`/projects/{project_id}/branches/{branch_id}/anonymized_status`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The ID of the project.
- **branch_id** (string) - Required - The ID of the branch.

### Response
#### Success Response (200)
- **branch_id** (string) - The ID of the branch.
- **project_id** (string) - The ID of the project.
- **state** (string) - The current state of anonymization. Possible values: `created`, `initialized`, `initialization_error`, `anonymizing`, `anonymized`, `error`.
- **status_message** (string) - A message providing details about the current status.
- **created_at** (string) - The timestamp when the anonymization status was created.
- **updated_at** (string) - The timestamp when the anonymization status was last updated.
- **failed_at** (string) - The timestamp when the anonymization process failed (if applicable).

#### Response Example
```json
{
  "branch_id": "br-aged-salad-637688",
  "project_id": "simple-truth-637688",
  "state": "anonymizing",
  "status_message": "Anonymizing table mydb.public.users (3/5)",
  "created_at": "2022-11-30T18:25:15Z",
  "updated_at": "2022-11-30T18:30:22Z"
}
```
```

--------------------------------

### Get Branch Details

Source: https://neon.com/docs/reference/cli-branches

Retrieve detailed information about a specific branch.

```APIDOC
## GET /websites/neon/branches/get

### Description
Retrieves detailed information about a specific branch in the Neon project.

### Method
GET

### Endpoint
/websites/neon/branches/get

### Parameters
#### Path Parameters
- **id|name** (string) - Required - The ID or name of the branch to retrieve details for.

#### Query Parameters
- **context-file** (string) - Optional - Path to the context file.
- **project-id** (string) - Optional - Project ID. Required if the account has more than one project.

### Request Example
```json
{
  "command": "neon branches get mybranch"
}
```

### Response
#### Success Response (200)
Returns detailed information about the branch.
- **Id** (string) - The ID of the branch.
- **Name** (string) - The name of the branch.
- **CreatedAt** (string) - Timestamp when the branch was created.
- **UpdatedAt** (string) - Timestamp when the branch was last updated.
- **Default** (boolean) - Indicates if the branch is the default.
- **ExpiresAt** (string) - The expiration timestamp in RFC 3339 format, or null if no expiration is set.

#### Response Example
```json
{
  "Id": "br-abc-123456",
  "Name": "mybranch",
  "CreatedAt": "2023-07-10T10:00:00Z",
  "UpdatedAt": "2023-07-11T11:00:00Z",
  "Default": false,
  "ExpiresAt": null
}
```
```

--------------------------------

### SQL Query to Fetch Orders by Customer ID

Source: https://neon.com/docs/import/migrate-from-firebase

An example SQL query to retrieve order data from the 'orders' table, filtering by customer IDs found in the 'customers' table. This demonstrates navigating the hierarchical data structure using 'parent_id'.

```sql
SELECT data FROM orders
WHERE parent_id IN (
    SELECT id FROM customers
    LIMIT 2
)
```

--------------------------------

### Deploy GraphQL Schema with StepZen CLI

Source: https://neon.com/docs/guides/stepzen

The command to deploy the generated GraphQL schema to the StepZen cloud. After deployment, the API can be explored in the StepZen dashboard.

```bash
stepzen start
```

--------------------------------

### Postgres regexp_replace() Example: Cleaning Phone Numbers

Source: https://neon.com/docs/functions/regexp_replace

This example demonstrates how to use the `regexp_replace()` function in PostgreSQL to clean and standardize phone numbers by removing all non-digit characters. It utilizes a Common Table Expression (CTE) to simulate a table with phone numbers in various formats and applies the function with the 'g' flag for global replacement.

```sql
WITH customer_data AS (
  SELECT '(555) 123-4567' AS phone_number
  UNION ALL
  SELECT '555.987.6543' AS phone_number
  UNION ALL
  SELECT '555-321-7890' AS phone_number
)
SELECT
  phone_number AS original_number,
  regexp_replace(phone_number, '[^\d]', '', 'g') AS cleaned_number
FROM customer_data;
```

--------------------------------

### Basic and Advanced SELECT Queries in Postgres

Source: https://neon.com/docs/postgresql/query-reference

Illustrates various ways to query data from a PostgreSQL table. Examples include selecting all or specific columns, filtering with WHERE, ordering results, limiting the output, and performing aggregations with GROUP BY. These queries are fundamental for data retrieval and analysis.

```sql
-- Basic SELECT to retrieve all columns from a table
SELECT * FROM users;

-- SELECT specific columns from a table
SELECT username, email FROM users;

-- SELECT with filtering using WHERE clause
SELECT * FROM users WHERE user_id > 10;

-- SELECT with ordering and limiting the results
SELECT username, email FROM users ORDER BY created_at DESC LIMIT 5;

-- SELECT with aggregation and grouping
SELECT COUNT(*) AS total_users, EXTRACT(YEAR FROM created_at) AS year FROM users GROUP BY year ORDER BY year;
```

--------------------------------

### Delete a Neon Project using API

Source: https://neon.com/docs/manage/projects

Provides a cURL example for deleting a Neon project via the Neon API. This action is permanent and requires the project's unique identifier (project ID) and an API key for authorization.

```bash
curl
  --request DELETE
  --header "Authorization: Bearer $NEON_API_KEY"
  'https://console.neon.tech/api/v2/projects/<PROJECT_ID>'
| jq
```

--------------------------------

### Example JWT Payload for Neon Data API

Source: https://neon.com/docs/data-api/troubleshooting

An example JSON payload for a JWT used with the Neon Data API. This payload includes standard claims like 'iat' (issued at), 'exp' (expiration time), 'iss' (issuer), 'aud' (audience), and crucially, 'sub' (subject) and 'role', which are essential for authentication and Row-Level Security (RLS).

```json
{
  "iat": 1764502220,
  "createdAt": "2025-11-28T15:01:13.821Z",
  "updatedAt": "2025-11-28T15:01:13.821Z",
  "role": "authenticated",
  "id": "41a5f680-89d2-474d-ae59-e27bfbbbd293",
  "sub": "41a5f680-89d2-474d-ae59-e27bfbbbd293",
  "exp": 1764503120,
  "iss": "https://ep-spring-silence-ad3hu80n.neonauth.c-2.us-east-1.aws.neon.tech",
  "aud": "https://ep-spring-silence-ad3hu80n.neonauth.c-2.us-east-1.aws.neon.tech"
}
```

--------------------------------

### JavaScript SDK: Filter Data with Inequality Operator

Source: https://neon.com/docs/data-api/get-started

This snippet demonstrates how to use the `.neq()` method to filter data, excluding rows where the 'status' column is 'draft'.

```javascript
.neq('status', 'draft')
```

--------------------------------

### Neon CLI TypeScript Example for Token Retrieval

Source: https://neon.com/docs/guides/oauth-integration

This snippet, taken from the Neon CLI source code (written in TypeScript), demonstrates the automatic interaction with OAuth API endpoints to retrieve refresh and access tokens. It highlights how an OAuth client can manage token acquisition.

```typescript
// Example illustrating how Neon CLI might interact with OAuth endpoints
// (Specific implementation details omitted for brevity, refer to Neon CLI source code)

async function getTokens(oauthHost: string, clientId: string, clientSecret: string) {
  // ... code to construct authorization request ...
  // ... code to exchange authorization code for tokens ...
  // ... code to handle refresh token and access token retrieval ...
  console.log(`Using OAuth host: ${oauthHost}`);
  // ... further logic ...
}

// Example usage:
// const oauthHost = "https://oauth2.neon.tech";
// getTokens(oauthHost, "your_client_id", "your_client_secret");
```

--------------------------------

### Viewing Active Connections in Neon

Source: https://neon.com/docs/connect/connection-pooling

Offers a SQL query to display currently active connections to a Neon database. This can be useful for monitoring and understanding connection usage, especially when troubleshooting.

```sql
SELECT usename FROM pg_stat_activity WHERE datname = '<database_name>';
```

--------------------------------

### Postgres: Create user_accounts table with default now() for created_at

Source: https://neon.com/docs/functions/now

This example demonstrates creating a `user_accounts` table in PostgreSQL. The `created_at` column is set to automatically record the timestamp with timezone using the `now()` function as the default value upon insertion.

```sql
CREATE TABLE user_accounts (
  user_id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

INSERT INTO user_accounts (username, email)
VALUES ('john_doe', 'john@example.com');
```

--------------------------------

### View Scheduled Jobs

Source: https://neon.com/docs/extensions/pg_cron

Query the `cron.job` table to see all jobs currently scheduled in your database, including details like job ID, schedule, command, and user.

```APIDOC
## View Scheduled Jobs

To see the jobs currently scheduled in your database, query the `cron.job` table:

```sql
SELECT * FROM cron.job;
```

This will show you details like the job ID, schedule, command, and the user who scheduled it.
```

--------------------------------

### Create Users Table for Replication

Source: https://neon.com/docs/guides/logical-replication-kafka-confluent

This SQL snippet shows how to create a 'users' table with an auto-incrementing ID, username, and email. This table will be used as an example for creating a publication for data replication.

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL
);
```

--------------------------------

### dblink_get_result(TEXT connname)

Source: https://neon.com/docs/extensions/dblink

Retrieves the result of a query previously sent using dblink_send_query.

```APIDOC
## dblink_get_result(TEXT connname)

### Description
Retrieves the result of a query that was previously sent using `dblink_send_query`. It returns the result set as a set of rows, allowing you to process the data as needed.

### Method
SQL Function

### Endpoint
N/A

### Parameters
#### Path Parameters
- **connname** (text) - Required - The name of the dblink connection.

### Request Example
```sql
SELECT * FROM dblink_get_result('my_remote_db');
```

### Response
#### Success Response (Set of rows)
- **(columns)** - The columns returned by the query sent via `dblink_send_query`.

#### Response Example
```json
[{"count": 1500000}]
```
```

--------------------------------

### List Available Libraries

Source: https://neon.com/docs/extensions/pg-extensions

Retrieve a list of all available preloaded libraries for a Neon project, including their descriptions, default status, experimental status, and versions.

```APIDOC
## GET /api/v2/projects/{your_project_id}/available_preload_libraries

### Description
Lists all available libraries that can be preloaded for a given Neon project. The response includes details about each library.

### Method
GET

### Endpoint
`https://console.neon.tech/api/v2/projects/your_project_id/available_preload_libraries`

### Parameters
#### Path Parameters
- **your_project_id** (string) - Required - The ID of the Neon project.

#### Query Parameters
None

#### Request Body
None

### Request Example
```bash
curl --request GET \
     --url https://console.neon.tech/api/v2/projects/your_project_id/available_preload_libraries \
     --header 'accept: application/json' \
     --header 'authorization: Bearer $NEON_API_KEY'
```

### Response
#### Success Response (200)
- **libraries** (array) - A list of available libraries.
  - **library_name** (string) - The name of the library.
  - **description** (string) - A description of the library.
  - **is_default** (boolean) - Indicates if the library is enabled by default.
  - **is_experimental** (boolean) - Indicates if the library is experimental.
  - **version** (string) - The version of the library.

#### Response Example
```json
{
  "libraries": [
    {
      "library_name": "timescaledb",
      "description": "Enables scalable inserts and complex queries for time-series data.",
      "is_default": true,
      "is_experimental": false,
      "version": "2.17.1"
    },
    {
      "library_name": "pg_cron",
      "description": "pg_cron is a cron-like job scheduler for PostgreSQL.",
      "is_default": true,
      "is_experimental": false,
      "version": "1.6.4"
    }
  ]
}
```
```

--------------------------------

### dblink_get_connections()

Source: https://neon.com/docs/extensions/dblink

Retrieves a list of all currently open, named dblink connections in the current session.

```APIDOC
## dblink_get_connections()

### Description
Returns a list of the names of all currently open, named `dblink` connections in the current session. This is helpful for monitoring and managing your `dblink` connections.

### Method
SQL Function

### Endpoint
N/A

### Parameters
None

### Request Example
```sql
SELECT * FROM dblink_get_connections();
```

### Response
#### Success Response (Set of text)
- **connection_name** (text) - The name of an open dblink connection.

#### Response Example
```json
["my_remote_db", "another_connection"]
```
```

--------------------------------

### GET /api/v2/projects/{project_id}/branches/{branch_id}/compare_schema

Source: https://neon.com/docs/guides/schema-diff

The compare_schema endpoint allows you to compare schemas between Neon branches. It highlights differences in a `diff` format, which is useful for CI/CD workflows and AI agent-driven processes.

```APIDOC
## GET /api/v2/projects/{project_id}/branches/{branch_id}/compare_schema

### Description
Compares the schema of a target branch to a base branch, highlighting differences in a `diff` format.

### Method
GET

### Endpoint
`/api/v2/projects/{project_id}/branches/{branch_id}/compare_schema`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The ID of your Neon project.
- **branch_id** (string) - Required - The ID of the target branch to compare (the branch with the modified schema).

#### Query Parameters
- **base_branch_id** (string) - Required - The ID of the base branch for comparison.
- **db_name** (string) - Required - The name of the database in the target branch.
- **lsn** (string) - Optional - The LSN on the target branch for which the schema is retrieved.
- **timestamp** (string) - Optional - The point in time on the target branch for which the schema is retrieved (RFC 3339 format).
- **base_lsn** (string) - Optional - The LSN for the base branch schema.
- **base_timestamp** (string) - Optional - The point in time for the base branch schema (RFC 3339 format).

#### Headers
- **Authorization** (string) - Required - Bearer token for API access (your Neon API key).

### Request Example
```bash
curl --request GET \
     --url 'https://console.neon.tech/api/v2/projects/wispy-butterfly-25042691/branches/br-rough-boat-a54bs9yb/compare_schema?base_branch_id=br-royal-star-a54kykl2&db_name=neondb' \
     --header 'accept: application/json' \
     --header 'authorization: Bearer $NEON_API_KEY'
```

### Response
#### Success Response (200)
- **diff** (string) - A string representing the schema differences in diff format.

#### Response Example
```json
{
  "diff": "---\ta/neondb\n+++ b/neondb\n@@ -27,7 +27,8 @@\n CREATE TABLE public.playing_with_neon (\n     id integer NOT NULL,\n     name text NOT NULL,\n-    value real\n+    value real,\n+    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP\n );\n"
}
```

**Notes:**
- The optional `jq -r '.diff'` command can be appended to the cURL example to extract and display only the diff content.
- `timestamp` or `lsn` / `base_timestamp` or `base_lsn` values can be used for precise time or LSN comparisons.
- `timestamp` / `base_timestamp` values must be in RFC 3339 format.
```

--------------------------------

### Neon CLI: List VPC Endpoints

Source: https://neon.com/docs/reference/cli-vpc

This command retrieves a list of all configured VPC endpoints for a specific Neon organization. Ensure the Neon CLI is installed and authenticated.

```bash
neon vpc endpoint list --org-id org-bold-bonus-12345678
```

--------------------------------

### Create Branch API Response

Source: https://neon.com/docs/ai/ai-rules-neon-api

This is an example JSON response after successfully creating a branch. It includes details about the newly created branch, its attached endpoints, and the associated operations.

```json
{
  "branch": {
    "id": "br-damp-glitter-adqd4hk5",
    "project_id": "hidden-river-50598307",
    "parent_id": "br-super-wildflower-adniii9u",
    "parent_lsn": "0/1A7F730",
    "name": "my-new-feature-branch",
    "current_state": "init",
    "pending_state": "ready",
    "state_changed_at": "2025-09-10T16:45:52Z",
    "creation_source": "console",
    "primary": false,
    "default": false,
    "protected": false,
    "cpu_used_sec": 0,
    "compute_time_seconds": 0,
    "active_time_seconds": 0,
    "written_data_bytes": 0,
    "data_transfer_bytes": 0,
    "created_at": "2025-09-10T16:45:52Z",
    "updated_at": "2025-09-10T16:45:52Z",
    "created_by": {
      "name": "<USER_NAME>",
      "image": "<USER_IMAGE_URL>"
    },
    "init_source": "parent-data"
  },
  "endpoints": [
    {
      "host": "ep-raspy-glade-ad8e3gvy.c-2.us-east-1.aws.neon.tech",
      "id": "ep-raspy-glade-ad8e3gvy",
      "project_id": "hidden-river-50598307",
      "branch_id": "br-damp-glitter-adqd4hk5",
      "autoscaling_limit_min_cu": 0.25,
      "autoscaling_limit_max_cu": 2,
      "region_id": "aws-us-east-1",
      "type": "read_write",
      "current_state": "init",
      "pending_state": "active",
      "settings": {},
      "pooler_enabled": false,
      "pooler_mode": "transaction",
      "disabled": false,
      "passwordless_access": true,
      "creation_source": "console",
      "created_at": "2025-09-10T16:45:52Z",
      "updated_at": "2025-09-10T16:45:52Z",
      "proxy_host": "c-2.us-east-1.aws.neon.tech",
      "suspend_timeout_seconds": 0,
      "provisioner": "k8s-neonvm"
    }
  ],
  "operations": [
    {
      "id": "cf5d0923-fc13-4125-83d5-8fc31c6b0214",
      "project_id": "hidden-river-50598307",
      "branch_id": "br-damp-glitter-adqd4hk5",
      "action": "create_branch",
      "status": "running",
      "failures_count": 0,
      "created_at": "2025-09-10T16:45:52Z",
      "updated_at": "2025-09-10T16:45:52Z",
      "total_duration_ms": 0
    },
    {
      "id": "e3c60b62-00c8-4ad4-9cd1-cdc3e8fd8154"
    }
  ]
}
```

--------------------------------

### Set up Auth and Account Routes with Neon UI Components (React)

Source: https://neon.com/docs/auth/quick-start/react-router-components

This example configures the main App component with React Router to handle different views for home, authentication, and account management using Neon's AuthView and AccountView components. It includes logic for displaying user status and redirecting to sign-in.

```jsx
import { Routes, Route, useParams } from 'react-router-dom';
import {
  AuthView,
  AccountView,
  SignedIn,
  UserButton,
  RedirectToSignIn,
} from '@neondatabase/neon-js/auth/react/ui';

function Home() {
  return (
    <>
      <SignedIn>
        <div
          style={{ display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '100vh',
            gap: '2rem' }}>
          <div style={{ textAlign: 'center' }}>
            <h1>Welcome!</h1>
            <p>You're successfully authenticated.</p>
            <UserButton />
          </div>
        </div>
      </SignedIn>
      <RedirectToSignIn />
    </>
  );
}

function Auth() {
  const { pathname } = useParams();
  return (
    <div
      style={{ display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        padding: '2rem 1rem' }}>
      <AuthView pathname={pathname} />
    </div>
  );
}

function Account() {
  const { pathname } = useParams();
  return (
    <div
      style={{ display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        padding: '2rem 1rem' }}>
      <AccountView pathname={pathname} />
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/auth/:pathname" element={<Auth />} />
      <Route path="/account/:pathname" element={<Account />} />
    </Routes>
  );
}
```

--------------------------------

### Postgres array_agg() Basic Example

Source: https://neon.com/docs/functions/array_agg

Demonstrates the basic usage of the `array_agg()` function to collect product IDs into an array for each order. It requires a table with order and product information and groups by order ID.

```sql
WITH orders AS (
  SELECT 1 AS order_id, 101 AS product_id, 2 AS quantity
  UNION ALL SELECT 1, 102, 1
  UNION ALL SELECT 2, 103, 3
  UNION ALL SELECT 2, 104, 1
  UNION ALL SELECT 3, 101, 1
)
SELECT
  order_id,
  array_agg(product_id) AS products
FROM orders
GROUP BY order_id
ORDER BY order_id;
```

--------------------------------

### JavaScript SDK: Filter Data with Greater Than or Equal Operator

Source: https://neon.com/docs/data-api/get-started

This snippet demonstrates using the `.gte()` method to filter records where the 'quantity' column is greater than or equal to 1.

```javascript
.gte('quantity', 1)
```

--------------------------------

### View Scheduled Jobs with SQL

Source: https://neon.com/docs/extensions/pg_cron

This snippet shows how to query the `cron.job` table to retrieve details of all scheduled jobs. It displays information such as job ID, schedule, command, and the user who scheduled the job.

```sql
SELECT * FROM cron.job;
```

--------------------------------

### Restart Compute Endpoint

Source: https://neon.com/docs/ai/ai-rules-neon-typescript-sdk

Restarts a compute endpoint by first suspending and then starting it. Throws an error if the endpoint is not active (already suspended).

```APIDOC
## POST /projects/{projectId}/endpoints/{endpointId}/restart

### Description
Restarts a compute endpoint by suspending and then starting it. Throws error if endpoint is not active (already suspended).

### Method
POST

### Endpoint
`/projects/{projectId}/endpoints/{endpointId}/restart`

### Parameters
#### Path Parameters
- **projectId** (string) - Required - The ID of the project.
- **endpointId** (string) - Required - The ID of the endpoint to restart.

### Request Example
```json
{
  "example": "POST /projects/your-project-id/endpoints/ep-your-endpoint-id/restart"
}
```

### Response
#### Success Response (200)
(No specific response body detailed in the source, typically an empty success or status confirmation)

#### Response Example
```json
{
  "example": "Restart operation successful."
}
```
```

--------------------------------

### DefinitionList Component for Technical Terms

Source: https://neon.com/docs/community/component-guide

The DefinitionList component is used for creating accessible lists that define technical terms and concepts. It presents terms followed by their definitions.

```html
<DefinitionList>

Database URL
: Connection string for your Neon database
: Format: `postgresql://user:password@host:port/database`

Connection Pool
: A cache of database connections
: Improves performance by reusing connections

Branch
: An isolated copy of your database
: Used for development and testing

</DefinitionList>
```

--------------------------------

### Execute SQL Queries with Toolkit

Source: https://neon.com/docs/ai/ai-rules-neon-toolkit

Executes arbitrary SQL queries against a specified Neon project's database using the Neon Serverless Driver. It accepts a `ToolkitProject` object and a SQL query string, returning the query results.

```typescript
// `project` is the object from the previous step

// DDL Statement (schema modification)
await toolkit.sql(
  project,
  `CREATE TABLE IF NOT EXISTS tasks (id SERIAL PRIMARY KEY, description TEXT, completed BOOLEAN DEFAULT FALSE);`
);

// DML Statement (data insertion)
await toolkit.sql(project, `INSERT INTO tasks (description) VALUES ('Analyze user feedback');`);

// DQL Statement (data retrieval)
const tasks = await toolkit.sql(project, `SELECT * FROM tasks WHERE completed = FALSE;`);
console.log('Incomplete tasks:', tasks);
// Output: [ { id: 1, description: 'Analyze user feedback', completed: false } ]
```

--------------------------------

### Timestamp Format Requirements

Source: https://neon.com/docs/guides/branch-expiration

Details on the required RFC 3339 format for the `expires_at` parameter, including valid examples and common errors.

```APIDOC
## Timestamp Format Requirements

### Description
Specifies the required format for the `expires_at` parameter, which must adhere to RFC 3339 with second-level precision.

### Format Patterns
- `YYYY-MM-DDTHH:MM:SSZ` (UTC)
- `YYYY-MM-DDTHH:MM:SS+HH:MM` (Positive UTC offset)
- `YYYY-MM-DDTHH:MM:SS-HH:MM` (Negative UTC offset)

### Valid Examples
- `2025-07-15T18:02:16Z` (UTC)
- `2025-07-15T18:02:16-05:00` (Eastern Standard Time)
- `2025-07-15T18:02:16+09:00` (Japan Standard Time)

### Requirements
- **Time zone:** Required. Use either `Z` for UTC or a numeric offset (e.g., `+05:00`).
- **Fractional seconds:** Optional, but only second precision is stored.
- **Timestamp validity:** Must be in the future.
- **Maximum expiration:** 30 days from the current time.

### Common Errors
- Missing timezone: `2025-07-15T18:02:16`
- Past timestamps
- Combining `Z` with an offset: `2025-07-15T18:02:16Z-05:00`
```

--------------------------------

### dblink_cancel_query(TEXT connname)

Source: https://neon.com/docs/extensions/dblink

Attempts to cancel the currently executing query on a named dblink connection.

```APIDOC
## dblink_cancel_query(TEXT connname)

### Description
Attempts to cancel the currently executing query on a named `dblink` connection. This can be useful if you need to stop a long-running query that is consuming resources on the remote database.

### Method
SQL Function

### Endpoint
N/A

### Parameters
#### Path Parameters
- **connname** (text) - Required - The name of the dblink connection.

### Request Example
```sql
SELECT dblink_cancel_query('my_remote_db');
```

### Response
#### Success Response (text)
- **status** (text) - Returns 'OK' if the query was successfully canceled, or the error message as text otherwise.

#### Response Example
```json
"OK"
```
```

--------------------------------

### Get First Temperature Reading by Device (SQL)

Source: https://neon.com/docs/extensions/timescaledb

Uses the `first()` aggregate function to retrieve the earliest temperature reading for each device, ordered by time. This is useful for understanding initial states or values.

```SQL
SELECT
device_id,
first(temperature, time) AS first_temperature
FROM weather_conditions
GROUP BY device_id
LIMIT 10;
```

--------------------------------

### Get Masking Rules API

Source: https://neon.com/docs/changelog

Retrieves the currently configured masking rules for branch anonymization.

```APIDOC
## GET /api/v2/projects/{project_id}/branch_anonymized/masking_rules

### Description
Retrieves the list of masking rules currently defined for anonymizing branches within a project.

### Method
GET

### Endpoint
`/api/v2/projects/{project_id}/branch_anonymized/masking_rules`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The ID of the project.

#### Query Parameters
None

#### Request Body
None

### Request Example
(No request body for GET requests)

### Response
#### Success Response (200)
- **masking_rules** (array) - A list of masking rules.
  - **database_name** (string) - The name of the database.
  - **schema_name** (string) - The name of the schema.
  - **table_name** (string) - The name of the table.
  - **column_name** (string) - The name of the column.
  - **masking_function** (string) - The masking function applied.

#### Response Example
```json
{
  "masking_rules": [
    {
      "database_name": "neondb",
      "schema_name": "public",
      "table_name": "users",
      "column_name": "email",
      "masking_function": "anon.dummy_free_email()"
    }
  ]
}
```
```

--------------------------------

### GraphQL Query: Request Order and Customer Details

Source: https://neon.com/docs/guides/stepzen

An example GraphQL query to retrieve order details including shipping cost and related customer information (name and email). This demonstrates how nested queries can fetch data from related tables.

```graphql
{
  getOrderList {
    id
    shippingcost
    customer {
      name
      email
    }
  }
}
```

--------------------------------

### GET /database/{database_id}

Source: https://neon.com/docs/ai/ai-rules-neon-python-sdk

Retrieves the details of a specific database within a branch. Note: The `database_id` parameter refers to the database name.

```APIDOC
## GET /database/{database_id}

### Description
Retrieves details for a specific database. _Note: The Python SDK uses `database_id`, but you should provide the `database_name`._

### Method
GET

### Endpoint
/database/{database_id}

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The ID of the project.
- **branch_id** (string) - Required - The ID of the branch.
- **database_id** (string) - Required - The name of the database.

### Response
#### Success Response (200)
- **database** (Database) - The database object.

#### Response Example
{
  "database": {
    "id": 123,
    "branch_id": "br-your-branch-id",
    "name": "my-app-db",
    "owner_name": "neondb_owner",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

--------------------------------

### Generate and Push Database Migrations

Source: https://neon.com/docs/guides/auth-okta

Commands to generate and apply database migrations using Drizzle Kit. `drizzle-kit generate:pg` creates migration files in the 'drizzle' folder, and `drizzle-kit push:pg` applies these migrations to the Neon database.

```bash
npx drizzle-kit generate:pg
```

```bash
npx drizzle-kit push:pg
```

--------------------------------

### Create Neon Project via cURL

Source: https://neon.com/docs/manage/projects

This snippet demonstrates how to create a Neon project using a cURL command. It requires an API key for authorization and specifies the project name in the JSON payload. The output includes detailed information about the newly created project.

```shell
curl 'https://console.neon.tech/api/v2/projects' \
  -H 'Accept: application/json' \
  -H "Authorization: Bearer $NEON_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
  "project": {
    "name": "myproject"
  }
}' | jq
```

--------------------------------

### GET /endpoints

Source: https://neon.com/docs/ai/ai-rules-neon-python-sdk

Retrieves a list of compute endpoints associated with a given branch. This allows you to identify available endpoints for connecting to your database.

```APIDOC
## GET /endpoints

### Description
Retrieves a list of all compute endpoints associated with a specific branch.

### Method
GET

### Endpoint
/endpoints

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The ID of the project.

#### Query Parameters
- **branch_id** (string) - Optional - Filter endpoints by branch ID.

### Response
#### Success Response (200)
- **endpoints** (list[Endpoint]) - A list of Endpoint objects.

#### Response Example
{
  "endpoints": [
    {
      "host": "example.com",
      "id": "endpoint-id",
      "project_id": "your-project-id",
      "branch_id": "br-your-branch-id",
      "autoscaling_limit_min_cu": 0.5,
      "autoscaling_limit_max_cu": 16,
      "region_id": "us-east-1",
      "type": "read_write",
      "current_state": "active",
      "settings": {},
      "pooler_enabled": true,
      "pooler_mode": "transaction",
      "disabled": false,
      "passwordless_access": false,
      "creation_source": "api",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "proxy_host": "proxy.example.com",
      "suspend_timeout_seconds": 300,
      "provisioner": "neon",
      "pending_state": null,
      "last_active": null,
      "compute_release_version": null
    }
  ]
}
```

--------------------------------

### Create a New Project and Set Context

Source: https://neon.com/docs/reference/cli-set-context

This command creates a new project named 'MyLatest' and automatically sets the project ID as the default context. This simplifies the initial setup by associating the new project with the CLI's context. A hidden `.neon` file is created to store this context.

```bash
neon projects create --name MyLatest --set-context
```

--------------------------------

### Remove online_advisor Extension

Source: https://neon.com/docs/extensions/online_advisor

This SQL command removes the online_advisor extension if it is currently installed. Ensure it is not in use before dropping.

```sql
DROP EXTENSION IF EXISTS online_advisor;
```

--------------------------------

### Create Neon Project

Source: https://neon.com/docs/reference/neondatabase-toolkit

Creates a new Neon project with optional configuration.

```APIDOC
## Create Neon Project

### Description
Creates a new Neon project and returns a `ToolkitProject` object containing all the associated resources. You can optionally specify project settings like name and Postgres version.

### Method
`toolkit.createProject(projectOptions?)`

### Endpoint
N/A (Method on toolkit instance)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **`projectOptions`** (object) - Optional - Configuration for the new project.
  - **`name`** (string) - Optional - The name of the project.
  - **`region_id`** (string) - Optional - The ID of the region where the project will be created.
  - **`pg_version`** (number) - Optional - The desired PostgreSQL version (e.g., 16).

### Request Example
```javascript
// Create a project with default settings
const project = await toolkit.createProject();

// Create a project with a specific name and Postgres version
const customizedProject = await toolkit.createProject({
  name: 'my-ai-agent-db',
  pg_version: 16,
});

console.log('Project created with ID:', project.project.id);
console.log('Connection string:', project.connectionURIs[0].connection_uri);
```

### Response
#### Success Response (200)
- **`ToolkitProject`** (object) - An object containing the project details and connection information.
  - **`project`** (object) - Details of the created Neon project.
  - **`connectionURIs`** (array) - An array of connection URIs for the project.
```

--------------------------------

### Update masking rules

Source: https://neon.com/docs/workflows/data-anonymization

Updates masking rules for the specified anonymized branch. After updating, use the start anonymization endpoint to apply changes.

```APIDOC
## PATCH /projects/{project_id}/branches/{branch_id}/masking_rules

### Description
Updates masking rules for the specified anonymized branch. After updating, use the start anonymization endpoint to apply changes.

### Method
PATCH

### Endpoint
`/projects/{project_id}/branches/{branch_id}/masking_rules`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The ID of the project.
- **branch_id** (string) - Required - The ID of the branch.

#### Request Body
- **masking_rules** (array) - Required - A list of masking rules to update or add.
  - **database_name** (string) - Required - The name of the database.
  - **schema_name** (string) - Required - The name of the schema.
  - **table_name** (string) - Required - The name of the table.
  - **column_name** (string) - Required - The name of the column.
  - **masking_function** (string) - Required - The masking function to apply.

### Request Example
```json
{
  "masking_rules": [
    {
      "database_name": "neondb",
      "schema_name": "public",
      "table_name": "users",
      "column_name": "email",
      "masking_function": "anon.dummy_free_email()"
    }
  ]
}
```

### Response
#### Success Response (200)
- **masking_rules** (array) - The updated list of masking rules for the branch.
  - **database_name** (string) - The name of the database.
  - **schema_name** (string) - The name of the schema.
  - **table_name** (string) - The name of the table.
  - **column_name** (string) - The name of the column.
  - **masking_function** (string) - The masking function to apply.

#### Response Example
```json
{
  "masking_rules": [
    {
      "database_name": "neondb",
      "schema_name": "public",
      "table_name": "users",
      "column_name": "email",
      "masking_function": "anon.dummy_free_email()"
    }
  ]
}
```
```

--------------------------------

### Download and Extract Weather Data

Source: https://neon.com/docs/extensions/timescaledb

This snippet downloads a compressed weather dataset using curl and then extracts the contents using tar. Ensure you have curl and tar installed on your system.

```bash
curl https://assets.timescale.com/docs/downloads/weather_small.tar.gz -o weather_small.tar.gz

tar -xvzf weather_small.tar.gz
```

--------------------------------

### dblink_error_message(TEXT connname)

Source: https://neon.com/docs/extensions/dblink

Retrieves the last error message associated with a specific named dblink connection.

```APIDOC
## dblink_error_message(TEXT connname)

### Description
Retrieves the last error message associated with a specific named `dblink` connection. This is invaluable for debugging issues that arise during remote queries.

### Method
SQL Function

### Endpoint
N/A

### Parameters
#### Path Parameters
- **connname** (text) - Required - The name of the dblink connection.

### Request Example
```sql
SELECT dblink_error_message('my_remote_db');
```

### Response
#### Success Response (text)
- **error_message** (text) - The last error message for the specified connection.

#### Response Example
```json
"ERROR:  connection timed out"
```
```

--------------------------------

### SQL Query: Fetch Customer Name and Email

Source: https://neon.com/docs/guides/stepzen

A raw SQL query to select the 'name' and 'email' columns from the 'public.customer' table where the 'id' matches a provided parameter ($1). This is the SQL translation for fetching specific customer details.

```sql
SELECT name, email FROM public.customer WHERE id = $1
```

--------------------------------

### Create Compute Endpoint (Bash)

Source: https://neon.com/docs/ai/ai-rules-neon-api

This example demonstrates how to create a new Neon compute endpoint using a cURL command. It specifies the project ID, authorization token, and the endpoint configuration including branch ID and type. The request body is sent as JSON.

```bash
curl 'https://console.neon.tech/api/v2/projects/{project_id}/endpoints' \
  -H 'Accept: application/json' \
  -H "Authorization: Bearer $NEON_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
  "endpoint": {
    "branch_id": "br-your-branch-id",
    "type": "read_only"
  }
}'
```

--------------------------------

### Verify table size before pg_repack using SQL function

Source: https://neon.com/docs/extensions/pg_repack

SQL query to get the human-readable size of a specific table using the pg_relation_size function, useful for checking table size before and after optimization.

```sql
SELECT pg_size_pretty(pg_relation_size('bloated_table'));
```

--------------------------------

### Get Organization Details

Source: https://neon.com/docs/manage/orgs-api

Retrieves detailed information about the organization, including its name, plan, and creation date.

```APIDOC
## Get organization details

Retrieves information about your organization, including its name, plan, and creation date.

### Method
GET

### Endpoint
`/organizations/{org_id}`

### Parameters
#### Path Parameters
- **org_id** (string) - Required - The ID of the organization.

### Request Example
```bash
curl --request GET \
     --url 'https://console.neon.tech/api/v2/organizations/{org_id}' \
     --header 'authorization: Bearer $PERSONAL_API_KEY'
```

### Response
#### Success Response (200 OK)
- **id** (string) - The unique identifier for the organization.
- **name** (string) - The name of the organization.
- **handle** (string) - A unique handle for the organization.
- **plan** (string) - The current subscription plan.
- **created_at** (string) - The date and time the organization was created (ISO 8601 format).
- **managed_by** (string) - Indicates how the organization is managed (e.g., 'console').
- **updated_at** (string) - The date and time the organization was last updated (ISO 8601 format).

#### Response Example
```json
{
  "id": "org-example-12345678",
  "name": "Example Organization",
  "handle": "example-organization-org-example-12345678",
  "plan": "business",
  "created_at": "2024-01-01T12:00:00Z",
  "managed_by": "console",
  "updated_at": "2024-01-01T12:00:00Z"
}
```
```

--------------------------------

### Next.js App Router Auth Client for Neon Auth

Source: https://neon.com/docs/ai/ai-rules-neon-auth

Creates an authentication client instance for use in Next.js applications with the App Router. This client is essential for interacting with authentication services.

```typescript
// lib/auth/client.ts
import { createAuthClient } from "@neondatabase/auth/next";
export const authClient = createAuthClient();
```

--------------------------------

### Create and Populate electronics_products Table

Source: https://neon.com/docs/functions/jsonb_array_elements

Defines the schema for the 'electronics_products' table and inserts sample data containing nested JSONB details for products. This setup is necessary to demonstrate the querying of nested arrays.

```sql
CREATE TABLE electronics_products (
 id INTEGER PRIMARY KEY,
 name TEXT,
 details JSONB
);


INSERT INTO electronics_products (id, name, details) VALUES
 (1, 'Laptop', '{"variants": [{"model": "A", "sizes": ["13 inch", "15 inch"], "colors": ["Silver", "Black"]}, {"model": "B", "sizes": ["15 inch", "17 inch"], "colors": ["Gray", "White"]}]}'),
 (2, 'Smartphone', '{"variants": [{"model": "X", "sizes": ["5.5 inch", "6 inch"], "colors": ["Black", "Gold"]}, {"model": "Y", "sizes": ["6.2 inch", "6.7 inch"], "colors": ["Blue", "Red"]}]}');
```

--------------------------------

### Create and Update Table without Primary Key (SQL)

Source: https://neon.com/docs/extensions/wal2json

This snippet demonstrates creating a table (`products_no_pk`) without a primary key and then performing an `UPDATE` operation. This setup is used to illustrate the behavior of `wal2json` when `REPLICA IDENTITY` is set to `DEFAULT` for such tables.

```sql
CREATE TABLE products_no_pk (
    product_name VARCHAR(100),
    quantity INTEGER,
    price DECIMAL(10, 2)
);

INSERT INTO products_no_pk (product_name, quantity, price) VALUES ('Widget', 100, 19.99);
UPDATE products_no_pk SET quantity = 90 WHERE product_name = 'Widget';
```

--------------------------------

### Get Anonymization Status API

Source: https://neon.com/docs/changelog

Retrieves the current status of the data anonymization process for a specific branch.

```APIDOC
## GET /api/v2/projects/{project_id}/branch/{branch_id}/anonymize/status

### Description
Fetches the current status of the data anonymization process for a given branch. This helps track the progress and completion of anonymization.

### Method
GET

### Endpoint
`/api/v2/projects/{project_id}/branch/{branch_id}/anonymize/status`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The ID of the project.
- **branch_id** (string) - Required - The ID of the branch to check the status for.

#### Query Parameters
None

#### Request Body
None

### Request Example
(No request body for GET requests)

### Response
#### Success Response (200)
- **status** (string) - The current status of the anonymization (e.g., "pending", "processing", "completed", "failed").

#### Response Example
```json
{
  "status": "completed"
}
```
```

--------------------------------

### Data API Request with JWT

Source: https://neon.com/docs/data-api/custom-authentication-providers

Example of how to include a JWT in your Data API requests to Neon. The JWT is passed in the Authorization header as a Bearer token.

```http
GET https://your-project.data.neon.tech/v1/posts
Authorization: Bearer {your_jwt_token}
```

--------------------------------

### Add Ecto.Repo to Supervision Tree

Source: https://neon.com/docs/guides/elixir-ecto

Integrates the Ecto.Repo process into the application's supervision tree. This ensures that the Ecto process is started and managed correctly by the OTP framework, enabling it to handle database queries.

```elixir
def start(_type, _args) do
  children = [
    Friends.Repo,
  ]
end
```

--------------------------------

### WorkOS JWKS URL Example

Source: https://neon.com/docs/data-api/custom-authentication-providers

The JWKS URL for WorkOS includes your Client ID. You can find your Client ID on the Overview page of your WorkOS Dashboard.

```text
https://api.workos.com/sso/jwks/{YOUR_CLIENT_ID}
```

--------------------------------

### List Available Libraries API (cURL)

Source: https://neon.com/docs/extensions/pg-extensions

This snippet demonstrates how to fetch a list of all available preloaded libraries for a Neon project using the `curl` command. It requires your project ID and API key for authentication. The response includes library names, descriptions, default status, experimental status, and version information.

```shell
curl --request GET \
     --url https://console.neon.tech/api/v2/projects/your_project_id/available_preload_libraries \
     --header 'accept: application/json' \
     --header 'authorization: Bearer $NEON_API_KEY'
```

--------------------------------

### Javascript Prepared Statement with PgBouncer

Source: https://neon.com/docs/connect/connection-pooling

This Javascript code illustrates how to use a prepared statement with the 'pg' client library, which is compatible with PgBouncer. It defines the query name, text, and parameter values separately to ensure secure and efficient execution.

```javascript
const query = {
  // give the query a unique name
  name: 'fetch-plan',
  text: 'SELECT * FROM users WHERE username = $1',
  values: ['alice'],
};
client.query(query);
```

--------------------------------

### Run Micronaut Application with Gradle

Source: https://neon.com/docs/guides/micronaut-kotlin

Provides the command to execute the Micronaut application using the Gradle wrapper. This command initiates the application startup process, including database connection, Flyway migrations, and server initialization.

```bash
./gradlew run
```

--------------------------------

### Neon Pool and Query Error Handling

Source: https://neon.com/docs/ai/ai-rules-neon-serverless

Implement robust error handling for Neon database connections and queries. This example demonstrates listening for pool errors and using try-catch blocks for query operations, ensuring graceful failure and logging.

```javascript
// Pool error handling
const pool = new Pool({ connectionString: process.env.DATABASE_URL });
pool.on('error', (err) => {
  console.error('Unexpected error on idle client', err);
  process.exit(-1);
});

// Query error handling
try {
  const [post] = await sql`SELECT * FROM posts WHERE id = ${postId}`;
  if (!post) {
    return new Response('Not found', { status: 404 });
  }
} catch (err) {
  console.error('Database query failed:', err);
  return new Response('Server error', { status: 500 });
}
```

--------------------------------

### GET /projects/{project_id}/operations/{operation_id}

Source: https://neon.com/docs/ai/ai-rules-neon-api

Retrieves the details and status of a specific operation using its ID.

```APIDOC
## GET /projects/{project_id}/operations/{operation_id}

### Description
Retrieves the details and status of a single, specified operation. The `operation_id` can be found in the response body of the API call that initiated the operation or by listing operations.

### Method
GET

### Endpoint
`/projects/{project_id}/operations/{operation_id}`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The unique identifier of the project where the operation occurred.
- **operation_id** (UUID) - Required - The unique identifier of the operation.

### Request Example
```bash
curl 'https://console.neon.tech/api/v2/projects/hidden-river-50598307/operations/274e240f-e2fb-4719-b796-c1ab7c4ae91c' \
  -H 'Accept: application/json' \
  -H "Authorization: Bearer $NEON_API_KEY"
```

### Response
#### Success Response (200)
- **operation** (object) - An object containing the details of the operation.

#### Response Example
```json
{
  "operation": {
    "id": "274e240f-e2fb-4719-b796-c1ab7c4ae91c",
    "project_id": "hidden-river-50598307",
    "branch_id": "br-long-feather-adpbgzlx",
    "endpoint_id": "ep-round-morning-adtpn2oc",
    "action": "start_compute",
    "status": "finished",
    "failures_count": 0,
    "created_at": "2025-09-10T12:14:58Z",
    "updated_at": "2025-09-10T12:15:03Z",
    "total_duration_ms": 4843
  }
}
```
```

--------------------------------

### Create Project API

Source: https://neon.com/docs/guides/embedded-postgres

Use the Create Project API to provision a new Postgres database for users. This endpoint allows customization of project name, PostgreSQL version, region, and compute/scaling behavior.

```APIDOC
## POST /api/v2/projects

### Description
Creates a new Neon project, which includes a PostgreSQL database, for a user. This endpoint can also configure compute settings and consumption limits.

### Method
POST

### Endpoint
https://console.neon.tech/api/v2/projects

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **project** (object) - Required - Contains project configuration details.
  - **name** (string) - Optional - The name of the project. Defaults to a generated name.
  - **pg_version** (integer) - Required - The PostgreSQL version to use for the new project.
  - **region_id** (string) - Optional - The ID of the region where the project will be created. Defaults to a Neon-configured region.
  - **default_endpoint_settings** (object) - Optional - Settings for the default compute endpoint.
    - **autoscaling_limit_min_cu** (number) - Optional - Minimum compute units (CU) for autoscaling. Defaults to 0.25.
    - **autoscaling_limit_max_cu** (number) - Optional - Maximum compute units (CU) for autoscaling.
    - **suspend_timeout_seconds** (integer) - Optional - Inactivity period in seconds before the compute suspends. Defaults to a Neon-defined value.
  - **settings** (object) - Optional - Configuration for consumption limits.
    - **quota** (object) - Optional - Defines consumption quotas for the project.
      - **active_time_seconds** (integer) - Optional - Maximum active time in seconds per billing period.
      - **compute_time_seconds** (integer) - Optional - Maximum compute time in seconds per billing period.
      - **written_data_bytes** (integer) - Optional - Maximum data written in bytes per billing period.
      - **data_transfer_bytes** (integer) - Optional - Maximum data transfer in bytes per billing period.
      - **logical_size_bytes** (integer) - Optional - Maximum logical storage size in bytes.

### Request Example
```json
{
  "project": {
    "name": "user-database-123",
    "pg_version": 16,
    "region_id": "aws-us-east-1",
    "default_endpoint_settings": {
      "autoscaling_limit_min_cu": 1,
      "autoscaling_limit_max_cu": 4,
      "suspend_timeout_seconds": 600
    },
    "settings": {
      "quota": {
        "active_time_seconds": 36000,
        "compute_time_seconds": 9000,
        "written_data_bytes": 1000000000,
        "data_transfer_bytes": 500000000,
        "logical_size_bytes": 100000000
      }
    }
  }
}
```

### Response
#### Success Response (200)
- **project** (object) - Details of the created project, including connection information.

#### Response Example
```json
{
  "project": {
    "id": "prod-project-12345",
    "name": "user-database-123",
    "created_at": "2024-01-01T12:00:00Z",
    "db_name": "neondb",
    "owner_id": "user-abcde",
    "region_id": "aws-us-east-1",
    "pg_version": 16,
    "safekeeper_auth_user": "user123",
    "safekeeper_auth_password": "...",
    "connection_uris": {
      "primary": "postgresql://user123:password@ep-name.region.neon.tech:5432/neondb"
    },
    "default_endpoint": {
      "id": "ep-12345",
      "name": "primary",
      "host": "ep-name.region.neon.tech",
      "port": 5432,
      "settings": {
        "autoscaling_limit_min_cu": 1,
        "autoscaling_limit_max_cu": 4,
        "suspend_timeout_seconds": 600
      }
    },
    "settings": {
      "quota": {
        "active_time_seconds": 36000,
        "compute_time_seconds": 9000,
        "written_data_bytes": 1000000000,
        "data_transfer_bytes": 500000000,
        "logical_size_bytes": 100000000
      }
    }
  }
}
```
```

--------------------------------

### Get Project Branch Count

Source: https://neon.com/docs/changelog/2025-01-17

This endpoint retrieves the total number of branches for a specific Neon project.

```APIDOC
## GET /api/v2/projects/{project_id}/branches/count

### Description
Retrieves the total number of branches associated with a given Neon project.

### Method
GET

### Endpoint
`/api/v2/projects/{project_id}/branches/count`

### Parameters
#### Path Parameters
- **project_id** (string) - Required - The unique identifier of the project.

### Response
#### Success Response (200)
- **count** (integer) - The total number of branches in the project.

#### Response Example
```json
{
   "count": 2
}
```
```

--------------------------------

### Setup Grafana OSS with Docker OTEL LGTM

Source: https://neon.com/docs/guides/opentelemetry

This snippet shows how to set up a local observability stack using Docker Compose for Grafana OSS, OpenTelemetry Collector, Loki, Tempo, and Mimir. It provides a cost-effective, open-source solution for monitoring Neon metrics and logs.

```bash
git clone https://github.com/grafana/docker-otel-lgtm.git
cd docker-otel-lgtm
docker compose up -d
```