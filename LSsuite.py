#!/bin/python
"""Automize naming, cutting and EXIF-tagging of LS
Assumes you want 5 LS starting from upcoming monday.
"""

import os
import glob
import datetime
import subprocess
import argparse

def make_date_list(args):
    """Create file containing filenames and timestamps.
    args.date [str] : YYYY-mm-dd (leading zero optional)
        Search for mondays from this date
    args.time [str] : HH:mm      (leading zero optional)
        Timestamp for images
    args.file
        output file
    args.overwrite
        overwrite existing output file?
    """
    start_date = datetime.datetime.combine(
            datetime.date(*[int(i) for i in args.date.split('-')]),
            datetime.time(*[int(i) for i in args.time.split(':')])
            )
    # Hvornår er det mandag igen?
    days_to_monday = (8-int(start_date.strftime("%w")))%7
    monday = start_date + datetime.timedelta(days_to_monday)

    # Print hverdage i næste uge YYYY-mm-dd
    if not os.path.isfile(args.file) or args.overwrite:
        with open(args.file, 'w') as out_file:
            for i in range(5):
                file_date = (monday + datetime.timedelta(i))
                out_file.writeln(
                        file_date.strftime("%Y-%m-%d")
                        + "\t" +
                        file_date.strftime("%Y %m %d %H %M %S")
                        )
    else:
        print("Write aborted, file '%s' already exists. Use --overwrite to write it anyway" % args.file)

def cut(args):
    """Cut and tag images.
    args.{fuzz, width, height}
        ImageMagick parameters. Fuzz in %, width and height in px
    basename : str
        used to match image files. Matches using 'basename*'
    """
    basename = args.basename
    date_list_filename = args.datelist
    fuzz = args.fuzz
    width = args.width
    height = args.height

    infiles = glob.glob(basename+"*")
    infiles.sort()

    try:
        with open(date_list_filename) as date_list_file:
            date_list = [line.strip() for line in date_list_file]
    except FileNotFoundError:
        print("datelist file '%s' not found" % date_list_filename)
        quit()

    for infile, date in zip(infiles, date_list):
        date_name = date.split("\t")[0]
        date_raw = datetime.datetime(*[int(field) for field in date.split("\t")[1].replace(" 0", " ").split(" ")])
        subprocess.call([
            "convert",
            str(infile),
            "-fuzz",
            str(fuzz)+"%",
            "-trim",
            "+repage",
            "-crop",
            str(width) + "x" + str(height) + "+0+0",
            str(date_name) + ".jpg"
            ])
        subprocess.call([
            "exiftool",
            "-AllDates=" + 
            date_raw.strftime("%Y:%m:%d %H:%M:%S"),
            str(date_name) + ".jpg"
            ])
        subprocess.call([
            "touch",
            "--date=" + 
            date_raw.strftime("%Y-%m-%d %H:%M:%S"),
            str(date_name) + ".jpg"
            ])


parser = argparse.ArgumentParser(
        description='Create list of dates and timestamps or cut and tag images according to such a file')
subparsers = parser.add_subparsers()

parser_datelist = subparsers.add_parser('datelist')
parser_cut = subparsers.add_parser('cut')
parser_cut.set_defaults(mode=cut)

parser_datelist.add_argument('--file', default='datelist.txt',
        help='datelist output file. Default: %(default)s')
parser_datelist.add_argument('--date', default=datetime.datetime.today().strftime('%Y-%m-%d'),
        help='date to start looking for mondays from. Default: today (%(default)s)')
parser_datelist.add_argument('--time', default='11:07:30',
        help='timestamp for images. Default: %(default)s')
parser_datelist.add_argument('--overwrite', action='store_true',
        help='overwrite existing datelist file? Default: %(default)s')
parser_datelist.set_defaults(mode=make_date_list)

parser_cut.add_argument('--basename', default='',
        help='match image files as \'basename*\'. Default: \'\'')
parser_cut.add_argument('--fuzz', default=10, type=int,
        help='ImageMagick fuzz argument (in percent). Default: %(default)d')
parser_cut.add_argument('--width', default=2336, type=int,
        help='output width (px). Default: %(default)d')
parser_cut.add_argument('--height', default=1664, type=int,
        help='output height (px). Default: %(default)d')
parser_cut.add_argument('--datelist', default='datelist.txt',
        help='datelist input file. Default: %(default)s')

args = parser.parse_args()
try:
    args.mode(args)
except AttributeError:
    parser.print_help()
