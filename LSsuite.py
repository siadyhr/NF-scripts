#!/bin/python

"""Automatiser navgivning, beskæring og EXIF-tagning af LS

Example:
    Generer datoliste med specifik dato
        $ LSsuite.py datelist 2019-12-14 08:24:30
    "today" og "now" kan anvendes som dato
    Generer datoliste fra i dag med standard timestamp
        $ LSsuite.py datelist

    Beskær løbesedler matchende et basename, evt. m. custom fuzz og navngiv vha datelist-fil
        $ LSsuite.py cut "LS U5" datelist 15
    Beskærer alt matchende "LS U5*"
    Beskær til bestemt format X×Y:
        $ LSsuite.py cut "LS U5" datelist 15 2336x1664

"""

import sys
import glob
import datetime
import subprocess
import argparse

def make_date_list(args):
    start_date = datetime.datetime.combine(
            datetime.date(*[int(i) for i in args.date.split('-')]),
            datetime.time(*[int(i) for i in args.time.split(':')])
            )
    # Hvornår er det mandag igen?
    days_to_monday = (8-int(start_date.strftime("%w")))%7
    monday = start_date + datetime.timedelta(days_to_monday)

    # Print hverdage i næste uge YYYY-mm-dd
    for i in range(5):
        file_date = (monday + datetime.timedelta(i))
        print(file_date.strftime("%Y-%m-%d") + "\t" +
                file_date.strftime("%Y %m %d %H %M %S"))

def cut(args):
    basename = args.basename
    date_list_filename = args.datelist
    fuzz = args.fuzz
    width = args.width
    height = args.height
    # basename, date_list_filename, fuzz, width, height):
    # Sorteret liste af billedfilnavne
    infiles = glob.glob(basename+"*")
    infiles.sort()

    try:
        with open(date_list_filename) as date_list_file:
            date_list = [line.strip() for line in date_list_file]
    except FileNotFoundError:
        print("Datolistefilen '" + date_list_filename + "' blev ikke fundet")
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

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_datelist = subparsers.add_parser('datelist')
parser_cut = subparsers.add_parser('cut')
parser_cut.set_defaults(mode=cut)

parser_datelist.add_argument('--file', default='datelist.txt')
parser_datelist.add_argument('--date', default=datetime.datetime.today().strftime('%Y-%m-%-d'))
parser_datelist.add_argument('--time', default='11:07:30')
parser_datelist.set_defaults(mode=make_date_list)

parser_cut.add_argument('--basename', default='')
parser_cut.add_argument('--fuzz', default=10, type=int)
parser_cut.add_argument('--width', default=2336, type=int)
parser_cut.add_argument('--height', default=1664, type=int)
parser_cut.add_argument('--datelist', default='datelist.txt')

args = parser.parse_args()
args.mode(args)
