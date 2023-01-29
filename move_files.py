from os import path, listdir, rename
from subprocess import check_output
from datetime import date, datetime, timedelta


def main():
    for i in listdir():
        if path.isfile(i):
            st = get_when_file_was_last_changed(i)
            datetime_file_moved_into_folder = convert_to_datetime(st)
            time_since_moved_into_folder = datetime.now()-datetime_file_moved_into_folder
            # change to > after testing
            if time_since_moved_into_folder < timedelta(hours=1):
                move_file_to_folder(f"/Users/ajardine/Desktop/vim_test/{i}", f"/Users/ajardine/Desktop/Desktop Archive/{i}")

def move_file_to_folder(filename, new_path):
    print(f"moving {filename} to {new_path}")
    rename(filename,new_path)

def get_when_file_was_last_changed(i):
	return check_output(["mdls", "-name", "kMDItemDateAdded", "-raw", i])


def convert_to_datetime(st):
# this code sucks, but idk how to convert the byte object to a datetime properly.
	datestr = str(st)
	year, month, day, hour, min = int(datestr[2:6]), int(datestr[8:9]), int(
        datestr[10:12]), int(datestr[13:15]), int(datestr[16:18])
	return datetime(year, month, day, hour, min)


main()