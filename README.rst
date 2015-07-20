TRIM Lookup Service
===================

Provide a simple website to allow lookups of vehicle information by Vehicle
Serial Number (VSN).

Two top level applications are provided:

* application.py - a conventional version of the server with unit and integration tests.
* application-minimal.py - a fairly minimal one-file version with integration tests.

Data Details
------------

Field titles and field names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+------------------+--------------+
| Field title      |  Field name  |
+==================+==============+
| VSN Pattern      |  vsn_pattern |
+------------------+--------------+
| Vehicle Trim Id  |  trim_id	  |
+------------------+--------------+
| Trim Name        |  trim_name	  |
+------------------+--------------+
| Year             |  year		  |
+------------------+--------------+
| Make             |  make		  |
+------------------+--------------+
| Model            |  model		  |
+------------------+--------------+

VSN definition
~~~~~~~~~~~~~~

In regular expression form::

   [A-Z]{6}[0-9]{6}    (or: six from A-Z then six from 0-9)

VNS Pattern detail
~~~~~~~~~~~~~~~~~~

Like VSNs, with the addition of 「*」 as a wildcard, which matches any valid
character for the wildcard's position in the VSN.

For patterns with multiple matches, those with the greatest number of exact
matches are preferred.

Matching a VSN pattern against several VSN strings:

+---------+----------------+------------------------------------+
| pattern | "ABC*EF*****6" |                                    |
+---------+----------------+------------------------------------+
| vs      | "ABCAEF111116" | matches                            |
+---------+----------------+------------------------------------+
| vs      | "ABC1EFAAAAA6" | fails - letters in digit positions |
+---------+----------------+------------------------------------+


Matching a VSN string against several VSN patterns:

+---------+----------------+------------------------------------+
| string  | "ABCDEF123456" |                                    |
+---------+----------------+------------------------------------+
| vs      | "ABCDEF******" | match with 6 exact matches         |
+---------+----------------+------------------------------------+
| vs      | "ABCDEF1*****" | match with 7 exact matches         |
+---------+----------------+------------------------------------+

Result data
-----------

Expected use is a VSN will be submitted and all matching patterns at the
highest found match value returned, along with their ancilliary info from
the database.  Here's a case where three equal-strength matches are returned:

REST call::

   curl 'http://127.0.0.1:5000/api/vehicles/v1/search?vsn=XXRCIV077000'

Result::

    [
        {
            "make": "Volkswagen",
            "match_strength": 0,
            "model": "GTI",
            "trim_id": "253909",
            "trim_name": "2-Door with Sunroof and Navigation, DSG",
            "vsn_pattern": "XXRC*V******",
            "year": "2013"
        },
        {
            "make": "Volkswagen",
            "match_strength": 0,
            "model": "GTI",
            "trim_id": "253901",
            "trim_name": "2-Door DSG",
            "vsn_pattern": "XXRC*V******",
            "year": "2013"
        },
        {
            "make": "Volkswagen",
            "match_strength": 0,
            "model": "GTI",
            "trim_id": "253913",
            "trim_name": "2-Door Autobahn, DSG",
            "vsn_pattern": "XXRC*V******",
            "year": "2013"
        }
    ]

Result (if json.dumps() is used instead of json_dumps_pretty):

   [{"make": "Volkswagen", "match_strength": 0, "trim_name": "2-Door with Sunroof and Navigation, DSG", "trim_id": "253909", "year": "2013", "model": "GTI", "vsn_pattern": "XXRC*V******"}, {"make": "Volkswagen", "match_strength": 0, "trim_name": "2-Door DSG", "trim_id": "253901", "year": "2013", "model": "GTI", "vsn_pattern": "XXRC*V******"}, {"make": "Volkswagen", "match_strength": 0, "trim_name": "2-Door Autobahn, DSG", "trim_id": "253913", "year": "2013", "model": "GTI", "vsn_pattern": "XXRC*V******"}]: *2.9265-[master*]⋯$;

And here a case where the return is filtered down to the strongest match
of four matches:

REST call::

    curl 'http://127.0.0.1:5000/api/vehicles/v1/search?vsn=XXRCIV07030'

Result::

    [
        {
            "make": "Volkswagen",
            "match_strength": 0,
            "model": "GTI",
            "trim_id": "253905",
            "trim_name": "2-Door with Convenience and Sunroof, DSG",
            "vsn_pattern": "XXRC*V****3*",
            "year": "2013"
        }
    ]

A case with no matches:

REST call::

    curl 'http://127.0.0.1:5000/api/vehicles/v1/search?vsn=XXXXXX088040'

Empty set result (still yields HTTP 200, though 404 is an option):

    []

A case with an invalid VSN:

REST call (note the flipped letter/digit in the middle::

    curl -v 'http://127.0.0.1:5000/api/vehicles/v1/search?vsn=XXXXX0X00000'

Result (400)::

    * Hostname was NOT found in DNS cache
    *   Trying 127.0.0.1...
    * Connected to 127.0.0.1 (127.0.0.1) port 5000 (#0)
    > GET /api/vehicles/v1/search?vsn=XXXXX0X00000 HTTP/1.1
    > User-Agent: curl/7.35.0
    > Host: 127.0.0.1:5000
    > Accept: */*
    > 
    * HTTP 1.0, assume close after body
    < HTTP/1.0 400 BAD REQUEST
    < Content-Type: text/html; charset=utf-8
    < Content-Length: 41
    < Server: Werkzeug/0.9.4 Python/2.7.6
    < Date: Mon, 20 Jul 2015 14:30:40 GMT
    < 
    {
        "message": "Invalid VSN provided"
    }
    * Closing connection 0

Testing
-------

Two sets of tests are included:

* tests/rest_test.py - integration tests, which assume servers up on 127.1:5000
* lib/tools/util_test.py - unit tests for a few functions in util.py

These can be executed with::

    nosetests --verbose --all-modules --with-doctest

Documentation
-------------

The API documentation can be converted to HTML using doxygen and doxypy::

   apt-get install doxygen doxypy graphviz
   doxygen

The results will be generated in the doc-doxygen directory.

Scaling issues
--------------

The spec does not require patterns to begin with explicit letters (instead
of wildcards), nor define any other requirements about wildcards being adjacent
or not, etc., so it necessary to address the general case where wildcards can
be used in any combination of characters in the pattern.

* [For the next version] A possible enhancement is to make indices for each
  of the VSN's character positions, then use SQL expressions for each
  position exactly (or inexactly using "is not None"), and ANDed together,
  to search them (in one large expression), ordering the results with
  smallest wildcard count first.  PostgreSQL can do this directly in
  indices without making explicitly separate columns.  However, many other
  databases (like sqlite, and MySQL) would need individual columns for each
  VSN position to be explicit in the schema, which has the ancilliary
  negative of requiring a schema change later if the length of VSNs
  changes.

* [For a later version] Having a second table with (minimally) columns for
  { vsn, vsn_pattern_found_list, time } would allow the results of each
  lookup to be cached and indexed, making each future lookup of a recently
  sought VSN be as fast as a normal indexed lookup.  Keeping the timestamp
  would allow the cache to be pruned if desired, although keeping a few
  million rows shouldn't have any major impact on search times.  Such a
  table would have a much higher write load than the vehicles table,
  suggesting using something that doesn't have to hit the disk, like
  memcache (if the data is PURELY intended to be a discardable cache), or
  couchbase (which backs up to disk) or some other caching-targeted
  software instead of the main database

* [Research topic] The VSNs are essentially (large) base-36 numbers, which
  suggests possible optimization in the math realm.

* [Later version] We'd expect to have a high ratio of reads to writes.  Mostly
  read-only database like this one are typically good candidates for
  sharding, with the read-only servers being fed occasional updates from a
  small number of writeable database servers.  In Python code, a decorator
  could be written to indicate which methods need to talk specifically to
  the writable servers, or writes could always be channelled through
  specific methods for that purpose instead of being done in general SQL
  code.  Neither is needed in this early prototype.

Initial Prototype
-----------------

Build a Flask app with an SQLite3 backend with regexp match.

* Converting the spec-example-data.csv to SQLlite

  { echo 'vsn_pattern,trim_id,year,make,model,trim_name' ; tail -n +2 spec-example-data.csv ; } | tr -d '\015' > vehicles.csv
  sqlite3 --separator ','  database.sqlite '.import vehicles.csv vehicles'

* Write a basic application.py

* Write a condensed single file variant,  application_minimal.py

* Install sqlite3
A virtual environment can be used apps like this with::

   virtualenv python-virtual
   . python-virtual/bin/activate
   pip install -r requirements.txt 

Note the using python-virtual requires running the app from inside of a
shell where the environment has been activated::

  python-virtual/bin/activate
  ./application.py 

In production one would typically automate this in an application.wsgi file::

  ... 
  activate_this = BASE_DIR + '/virtual-python/bin/activate_this.py'
  execfile(activate_this, dict(__file__=activate_this))
  ...
  from application import make_app
  application = make_app()


