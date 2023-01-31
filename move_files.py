from os import path, listdir, rename
from subprocess import check_output, STDOUT, PIPE, Popen
from datetime import date, datetime, timedelta
import platform
import shlex


def main():
    desktop = '/Users/ajardine/Desktop/'
    desktop_archive = '/Users/ajardine/Desktop/Desktop Archive/'
    downloads = '/Users/ajardine/Downloads/'
    trash = '/Users/ajardine/.Trash'

# Desktop - if added later than 1 hour, and not folder, and not application, and not alias. Move to Desktop Archive.
    loop_through_files_and_move(
        source_directory=desktop,
        destination_directory=desktop_archive,
        hours_before_move=1,
        move_folders=False)

# Desktop Archive - if added later than 1 week ago send to trash
    loop_through_files_and_move(source_directory=desktop_archive,
                                destination_directory=trash,
                                hours_before_move=168,
                                move_folders=True)

# Downloads - if added later than 1 week ago send to trash
    loop_through_files_and_move(
        source_directory=downloads,
        destination_directory=trash,
        hours_before_move=168,
        move_folders=True)


def loop_through_files_and_move(source_directory, destination_directory, hours_before_move, move_folders):
    for source_file_name in listdir(source_directory):
        fullpath = source_directory+source_file_name
        #print(f"reviewing {source_file_name}")
        if is_file_right_type_to_move(fullpath, move_folders):
            st = get_when_file_was_last_changed(fullpath)
            # some files don't have a datetime (ie it's None), so we skip them.
            if not convert_to_datetime(st):
                #print(f'skipping {source_file_name} becausee datetime is none')
                continue
            datetime_file_moved_into_folder = convert_to_datetime(st)
            time_since_moved_into_folder = datetime.now()-datetime_file_moved_into_folder
            # use < for testing and hardcode 1 hour.
            if time_since_moved_into_folder > timedelta(hours=hours_before_move):
                move_file_to_folder(
                    f"{fullpath}", f"{destination_directory}{source_file_name}")

# this code is stolen from https://drscotthawley.github.io/blog/2018/02/21/Resolving-OSX-Aliases.html


def is_file_right_type_to_move(fullpath, move_folders):
    if path.isfile(fullpath) and (not isAlias(fullpath)):
        return True
    if path.isdir(fullpath) and move_folders == True:
        return True
    return False


def isAlias(pathe, already_checked_os=False):
    # already_checked just saves a few microseconds ;-)
    if (not already_checked_os) and ('Darwin' != platform.system()):
        return False
    checkpath = path.abspath(pathe)       # osascript needs absolute paths
    # Next several lines are AppleScript
    line_1 = 'tell application "Finder"'
    line_2 = 'set theItem to (POSIX file "'+checkpath+'") as alias'
    line_3 = 'if the kind of theItem is "alias" then'
    line_4 = '   return true'
    line_5 = 'else'
    line_6 = '   return false'
    line_7 = 'end if'
    line_8 = 'end tell'
    cmd = "osascript -e '"+line_1+"' -e '"+line_2+"' -e '"+line_3+"' -e '" + \
        line_4+"' -e '"+line_5+"' -e '"+line_6+"' -e '"+line_7+"' -e '"+line_8+"'"
    # shlex splits cmd up appropriately so we can call subprocess.Popen with shell=False (better security)
    args = shlex.split(cmd)
    p = Popen(args, shell=False, stdout=PIPE, stderr=STDOUT)
    retval = p.wait()
    if (0 == retval):
        line = p.stdout.readlines()[0]
        line2 = line.decode('UTF-8').replace('\n', '')
        if ('true' == line2):
            return True
        else:
            return False
    else:
        print(
            'resolve_osx_alias: Error: subprocess returned non-zero exit code '+str(retval))
    return None


def move_file_to_folder(original_path, new_path):
    #print(f"moving {original_path} to {new_path}")
    rename(original_path, new_path)


def get_when_file_was_last_changed(i):
    return check_output(["mdls", "-name", "kMDItemDateAdded", "-raw", i])


def convert_to_datetime(st):
    # this code sucks, but idk how to convert the byte object to a datetime properly.
    datestr = str(st)
    try:
        year, month, day, hour, min = int(datestr[2:6]), int(datestr[8:9]), int(
            datestr[10:12]), int(datestr[13:15]), int(datestr[16:18])
        return datetime(year, month, day, hour, min)
    except ValueError:
        return None


if __name__ == "__main__":
    main()
