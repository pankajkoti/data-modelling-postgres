# Summary of the Project

This project applies data modelling with Postgres and builds an ETL pipeline using Python. 
The ETL pipeline transfers data from files and loads in Postgres tables.
The data is for a demo startup called Sparkify where analysts would like to perform queries on user activity of songs. The data files have song data and user activity log data


# Step for running the ETL
1. Drop and create tables before running the ETL 
    > python create_tables.py
                                                     
2. Run the etl
    > python etl.py
    
    This will get data from the files and load to postgres tables
    
3. Test the outcome of ETL process by running the test.ipynb in a Jupyter environment

# Project stucture

1. Data dir:
    - song_data : The first dataset is a subset of real data from the Million Song Dataset. Each file is in JSON format and contains metadata about a song and the artist of that song. The files are partitioned by the first three letters of each song's track ID
    - log_data: The second dataset consists of log files in JSON format generated by an event simulator based on the songs in the dataset above. These simulate activity logs from a music streaming app based on specified configurations.
                The log files in the dataset you'll be working with are partitioned by year and month.

2. create_tables.py - Script to drop and create tables according to data modelled. **You need to make sure that this script is executed before running the ETL**

3. sql_queries.py - A collection of all DDL and DML queries used in the project

4. etl.pynb - A jupyter notebook was used to try out code before creating the actual ETL. Can be used as a reference to understand how to do a run on sample entries

5. etl.py - The actual ETL file which loads data from data files and inserts into the db

6. test.ipynb - A test Jupyter notebook file to run queries and test if the ETL ran successfully and inserted required data in corresponding tables

# Database Design

Using the song and log datasets, we create a star schema optimized for queries on song play analysis.

Following is how we modelled the data in 1 fact table and 4 corresponding dimension tables:

### Fact Table:
1. **songplays** - records in log data associated with song plays i.e. records with the page __NextSong__
    - songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent
 
### Dimesion Tables:
1. **users** - users in the app
    - user_id, first_name, last_name, gender, level
2. **songs** - songs in music database
    - song_id, title, artist_id, year, duration
3. **artists** - artists in music database
    - artist_id, name, location, latitude, longitude
4. **time** - timestamps of records in songplays broken down into specific units
    - start_time, hour, day, week, month, year, weekday

# ETL process

The ETL process is written in python, has postgres as a relational database backend and makes extensive used of 'pandas' library to process song data from file by reading them in memory one by one and 'psycopg2' library for connecting and writing to postgres.

The ETL process is modelled mainly with two components/processors:
1. The first component reads song data files one by one, processes them by extracting data required for the songs and artists table and dumps this extracted data to the corresponding postgres dimension tables mentioned above which are 'songs' and 'artists'
2. The second component reads log data files one by one, extracts user and time specific data from the records and dumps them to 'users' and 'time' tables. Later it does a join on the songs and artists table to extract song_id and artist_id which is required to dump together with the log record in the songplays table
