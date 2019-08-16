#!/usr/bin/python

import argparse
import os

import numpy as np
from icrawler.builtin import GoogleImageCrawler


def get_files(directory, extensions=None, shuffle=False):
    """
    Lists files in a directory
    :return:
    """

    if extensions is None:
        extensions = ['jpg', 'bmp', 'png', 'JPG', 'JPEG']
    images = []
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(subdir, file)

            if extensions is not None:
                if any(filepath.endswith(ext) for ext in extensions):
                    images.append(filepath)
            else:
                images.append(filepath)
    if shuffle:
        np.random.shuffle(images)
    return images


def write_files_to_file(directory, filename, shuffle=False):
    files = get_files(directory, shuffle=shuffle)
    file = open(filename, 'w')
    file.writelines('\n'.join(files))


def crawl_and_download(download_dir, keyword, filter_type, filename):
    try:
        filters = {'type': filter_type}
        google_crawler = GoogleImageCrawler(parser_threads=2, downloader_threads=4,
                                            storage={'root_dir': download_dir})
        google_crawler.crawl(keyword=keyword, max_num=1000,
                             min_size=(200, 200), max_size=(1024, 1024), filters=filters)
    finally:
        write_files_to_file(download_dir, filename)


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--download_dir", type=str, default="./downloads/", help="download directory")
    parser.add_argument("-k", "--keyword", type=str, default="face", help="search keyword")
    parser.add_argument("-f", "--filename", type=str, default=None, help="file to save the list of downloaded files")
    parser.add_argument("-t", "--type", type=str, default='photo', help="Photo filter type [photo, face, clipart, "
                                                                        "linedrawing, animated]")
    args = parser.parse_args(args)
    if args.filename is None:
        args.filename = os.path.join(args.download_dir, "files.txt")
    return args


def demo():
    args = "-d download/ -k 'human+face' -t photo -f download/files.txt".split()
    args = parse_args(args)
    print("Downloading '{}' of type '{}' into the folder '{}'. Final list will be written to the file '{}'".format(
        args.keyword, args.type, args.download_dir, args.filename))
    crawl_and_download(args.download_dir, args.keyword, args.type, args.filename)


if __name__ == "__main__":
    args = parse_args()
    print("Downloading '{}' of type '{}' into the folder '{}'. Final list will be written to the file '{}'".format(
        args.keyword, args.type, args.download_dir, args.filename))
    crawl_and_download(args.download_dir, args.keyword, args.type, args.filename)
