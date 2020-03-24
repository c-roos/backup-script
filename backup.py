import logging
import argparse
import sqlite3
import time
from datetime import datetime
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth, ServiceAccountCredentials


logging.basicConfig(filename='backup.log', format='%(asctime)s %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)


TIMESTAMP_FORMAT = '%d/%m/%y_%H:%M' 
BACK_OFF_INTERVAL = 300 # retry after 5 minutes


def backup_db(db_list, drive, parent, timestamp):
    for db in db_list:
        index = db.rfind('.')
        db_name = db[:index]
        db_extension = db[index:]
            
        con = sqlite3.connect(db)
        bck = sqlite3.connect(f"{db_name}_backup{db_extension}")
        with bck:
            con.backup(bck, pages=1)
        bck.close()
        con.close()
        
        title = f"{db_name}_{datetime.fromtimestamp(timestamp).strftime(TIMESTAMP_FORMAT)}{db_extension}"
        f = drive.CreateFile({'title': title, 'parents': [{'id': parent}]})
        f.SetContentFile(f"{db_name}_backup{db_extension}")
        f.Upload()


def main(credentials, folder, databases, interval, delay):
    gauth = GoogleAuth()
    scope = ['https://www.googleapis.com/auth/drive']
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials, scope)
    gdrive = GoogleDrive(gauth)
    
    parent_id = gdrive.ListFile({'q': f"mimeType = 'application/vnd.google-apps.folder' and title = '{folder}'"}).GetList()[0]['id']
    
    time.sleep(delay)
    
    backoff = False
    while True:
        if backoff:
            time.sleep(300)
        now = time.time()
        try:
            backup_db(databases, gdrive, parent_id, now)
        except KeyboardInterrupt:
            print("backup.py exiting...")
            break
        except Exception:
            logging.exception('Unexpected Exception')
            backoff = True
            continue
        else:
            backoff = False
            
        try:
            time.sleep(now - time.time() + interval)
        except ValueError:
            logging.info(f"Backing up databases took longer than {interval} seconds")
        except KeyboardInterrupt:
            print("backup.py exiting...")
            break

            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Back up SQLite databases to Google Drive')
    parser.add_argument('credentials', type=str, help='Name of JSON file containing service account credentials')
    parser.add_argument('folder', type=str, help='Name of google drive folder to store backups in')
    parser.add_argument('databases', type=str, nargs='+', help='Names of databases to back up')
    parser.add_argument('--interval', '-i', nargs='?', type=int, default=86400, help='Interval in seconds between backups. Default = 86400 = 1 day')
    parser.add_argument('--delay', '-d', nargs='?', type=int, default=0, help='Initial delay in seconds before script will start making backups. Default = 0')
    
    args = parser.parse_args()
    
    name_errors = [db for db in args.databases if db.find('.') == -1]
    if name_errors:
        print(f"Error: No file extension found in names of the following databases:\n{', '.join(name_errors)}")
    else:
        main(args.credentials, args.folder, args.databases, args.interval, args.delay)
