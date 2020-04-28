import glob
import os

import pandas as pd
import psycopg2

from sql_queries import *


def process_song_file(cur, filepath):
    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert song record
    song_data = df[['song_id', 'title', 'artist_id', 'year', 'duration']].values.tolist()[0]
    try:
        cur.execute(song_table_insert, song_data)
    except psycopg2.errors.UniqueViolation:
        pass

    # insert artist record
    artist_df = df.drop_duplicates(subset='artist_id', keep='first')
    artist_data = artist_df[['artist_id', 'artist_name', 'artist_location', 'artist_latitude',
                             'artist_longitude']].values.tolist()[0]
    try:
        cur.execute(artist_table_insert, artist_data)
    except psycopg2.errors.UniqueViolation:
        pass


def process_log_file(cur, filepath):
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df.page.eq('NextSong')]

    # convert timestamp column to datetime
    t = pd.to_datetime(df['ts'], unit='ms')

    # insert time data records
    time_data = [{'start_time': row, 'hour': row.hour, 'day': row.day, 'week': row.week, 'month': row.month,
                  'year': row.year, 'weekday': row.day_name()} for row in t]
    column_labels = ('start_time', 'hour', 'day', 'week', 'month', 'year', 'weekday')
    time_df = pd.DataFrame.from_records(time_data, column_labels).reset_index()

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[['userId', 'firstName', 'lastName', 'gender', 'level']].drop_duplicates(subset='userId', keep='first')

    # insert user records
    for i, row in user_df.iterrows():
        try:
            cur.execute(user_table_insert, row)
        except psycopg2.errors.UniqueViolation:
            pass
    # insert songplay records
    df['start_time'] = pd.to_datetime(df['ts'], unit='ms')
    for index, row in df.iterrows():

        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()

        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = (row.start_time, row.userId, row.level, songid, artistid, row.sessionId, row.location,
                         row.userAgent)
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, '*.json'))
        for f in files:
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()
