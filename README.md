# letterboxd-count-by-director

A small utility script that, given an exported [Letterboxd](letterboxd.com) user data file, outputs a text file with directors grouped by the count of films directed by them that the user has watched:

```
15 films (1 director):
Krzysztof Kieślowski

10 films (1 director):
Lars von Trier

8 films (3 directors):
Wes Anderson
Stanley Kubrick
Sion Sono
(and so on, and so forth...)
```

The script gets the director(s) of a film by scraping its Letterboxd page. It stores (film, director) pairs in a cache file (``cache.csv`` by default) to avoid unnecessary requests.

Tested with Python 3.6.1 on Arch GNU/Linux.

## Usage
1. Export your user data from [Letterboxd settings](https://letterboxd.com/settings/) ``IMPORT & EXPORT -> EXPORT YOUR DATA``
2. Run the script: ``python letterboxd_count_by_director.py path/to/downloaded_data_file.zip``
3. See ``output.txt`` for results