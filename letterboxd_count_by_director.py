# pylint: disable=missing-docstring
import sys
import os
import io
import zipfile
import csv
import urllib.request
import re
import time
import operator
import itertools


CACHE_FILENAME = "cache.csv"
OUT_FILENAME = "output.txt"
REQUEST_DELAY_SECONDS = 0.5


def fetch_director(slug):
    print("Fetching director for '{}'... ".format(slug), end="")

    url = "https://letterboxd.com/film/{}/".format(slug)
    content = urllib.request.urlopen(url).read().decode('utf-8')

    match = re.search(r"twitter:data1\" content=\"(.*)\"", content)
    if not match:
        print("FAILED", flush=True)
        sys.exit("Exiting...")

    director = match.group(1)
    print("OK:", director)

    return director


def get_slugs(reader):
    slugs = []

    for entry in reader:
        url = entry[3]
        if url:
            slug = url.split("/")[4]
            slugs.append(slug)

    return slugs


def process_watched_data(reader, cache):
    cache_additions = {}
    film_counts = {}

    slugs = get_slugs(reader)

    print("Processing {} films...".format(len(slugs)))

    for slug in slugs:
        director_entry = None

        if slug in cache:
            director_entry = cache[slug]
        else:
            director_entry = fetch_director(slug)
            cache_additions[slug] = director_entry
            time.sleep(REQUEST_DELAY_SECONDS)

        directors = director_entry.split(", ")
        for director in directors:
            if director:
                film_counts[director] = film_counts[director] + 1 if director in film_counts else 1

    return (film_counts, cache_additions)


def read_cache(reader):
    cache = {}

    for entry in reader:
        slug = entry[0]
        director = entry[1]
        cache[slug] = director

    print("Read {} entries from cache file: '{}'".format(len(cache), CACHE_FILENAME))

    return cache


def write_cache(cache, cache_additions):
    cache = {**cache, **cache_additions}

    with open(CACHE_FILENAME, "w") as cache_file:
        cache_writer = csv.writer(cache_file)
        for slug, director in cache.items():
            cache_writer.writerow([slug, director])

    print("Wrote {} entries to cache file: '{}'".format(len(cache), CACHE_FILENAME))


def get_last_initial(full_name):
    return full_name.split(" ")[-1][0]



def write_output(film_counts):
    sorted_film_counts = sorted(film_counts.items(), key=operator.itemgetter(1), reverse=True)

    get_director = lambda director_w_count: director_w_count[0]
    get_count = lambda director_w_count: director_w_count[1]

    grouped_film_counts = itertools.groupby(sorted_film_counts, get_count)

    with open(OUT_FILENAME, "w") as output_file:
        for count, group in grouped_film_counts:
            sort_key = lambda director_w_count: get_last_initial(get_director(director_w_count))
            group = sorted(list(group), key=sort_key)

            film_noun = "films" if count > 1 else "film"
            num_directors = len(group)
            director_noun = "directors" if num_directors > 1 else "director"

            header = "{} {} ({} {}):\n".format(count, film_noun, num_directors, director_noun)
            output_file.write(header)

            for director_with_count in group:
                output_file.write("{}\n".format(get_director(director_with_count)))
            output_file.write("\n")

    print("Wrote output to file: '{}'".format(OUT_FILENAME))


def process(data_filename):
    try:
        with zipfile.ZipFile(data_filename) as data_file:
            watched_data = data_file.read("watched.csv").decode("utf-8")

            watched_data_reader = csv.reader(io.StringIO(watched_data))
            next(watched_data_reader, None)

            cache = {}

            if os.path.isfile(CACHE_FILENAME):
                with open(CACHE_FILENAME) as cache_file:
                    cache_reader = csv.reader(cache_file)
                    cache = read_cache(cache_reader)
            else:
                print("Cache file not found. It will be created.")

            (film_counts, cache_additions) = process_watched_data(watched_data_reader, cache)
            write_cache(cache, cache_additions)
            write_output(film_counts)
    except FileNotFoundError:
        print("Could not open file: '{}'".format(data_filename), file=sys.stderr)
    except (zipfile.BadZipFile, KeyError):
        print("'{}' is not a valid Letterboxd data file".format(data_filename), file=sys.stderr)


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) != 2:
        sys.exit("Wrong number of arguments. Exiting (B EXITING B DON'T KILL ME)")

    data_filename = sys.argv[1]
    process(data_filename)

if __name__ == "__main__":
    main()
