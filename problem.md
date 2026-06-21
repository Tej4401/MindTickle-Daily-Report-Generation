# SDE Assignment

## 🚀 Problem Statement

At Mindtickle, we strive to meet our clients' unique needs. Currently, a client company has requested a report detailing the number of lesson completed on daily basis by each of its active user. Your goal is to create a Python script to compile this report, store it in an AWS S3 Bucket, and dispatch it via email (AWS SES) as attachment. The file should be of CSV format with the following columns - Name, Number of lessons completed, Date

The challenge lies in aggregating data from difference database sources: PostgreSQL and MySQL. While you won't need to create the databases from scratch, you'll utilize our provided docker-compose file to spin up sample databases. The initial data and relations can be checked in `setup/init.mysql.sql` and `setup/init.pg.sql` files. You can use this data for reference and can add your own data as well to these files for testing purposes.

## 🔧 Prerequisites

### Setup Docker
Get Docker Desktop installed and running:
- [Docker Desktop](https://docs.docker.com/desktop/)
- [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)

### Environment Setup
1. Clone this repository.
2. Navigate to the `setup` directory.
3. Copy the environment file and populate it with the required values:
    ```bash
    cd setup
    cp .env.example .env
    ```

### Launch Docker Images
Start the docker containers:
```bash
docker-compose up --build
```


## 📝 Submission Guidelines
1. The code can be submitted as a zip file or in a publicly available Git repository to HR
2. Generate an additional markdown file containing any supplementary setup instructions you wish to provide for the reviewer.
3. Selection Criteria:
    * Correctness and efficiency of the solution.
    * Use of best practices in areas such as, but not limited to,
        - Code Readability
        - Code Modularity
        - Use of linters
        - Code configuration management / security
        - Dependency Management
        - Solution scalability
    * Preference will be given to candidates who are able to write the python script in a form of Airflow DAG.