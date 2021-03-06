ERA data
========

This repository contains tools to fetch and load data from the
[Excellence in Research for Australia](https://en.wikipedia.org/wiki/Excellence_in_Research_for_Australia)
program (ERA) into a database.

The motivation is the reference data for 2010 and 2012 ERA came in slightly different formats,
and the data had unusual copyright protections when it was released from the Australian Research Council (ARC),
in part due to [the Australian Crown copyright](https://en.wikipedia.org/wiki/Crown_copyright#Australia).

Copyright
---------
The [ARC website copyright notice](http://www.arc.gov.au/copyright.htm) mentions
[Creative Commons (CC) BY 3.0](http://creativecommons.org/licenses/by/3.0/legalcode)
however it also has an other "Other Copyright" section referring to restrictive
Crown copyright, and no statement regarding when CC or Crown applies.

In addition, the datasets for ERA 2010 and ERA 2012 can no longer be found on
their website, and the copyright notice did not mention CC licenses when these
datasets were available from their website.

To avoid this copyright problem, this repository does not contain any ERA data.
Instead it provides tools to fetch and transform the datasets into other formats,
and will do analysis on the dataset in the cloud.

All files stored in this repository are available under the MIT license.

Data sources
------------
This repository has a script `fetch.sh` that downloads the following two files from [Australian Government Web Archive](http://content.webarchive.nla.gov.au/):
* [ERA 2010 tech pack](http://content.webarchive.nla.gov.au/gov/wayback/20120317002747/http://www.arc.gov.au/zip/ERA2010_tech_pack.zip)
* [ERA 2012 Journal List](http://content.webarchive.nla.gov.au/gov/wayback/20140212052430/http://www.arc.gov.au/xls/era12/ERA2012JournalList.xlsx)

Usage
-----
The datasets are processed automatically after each checkin on the following two services:
* [Travis-CI](https://travis-ci.org/jayvdb/era_data/builds) - four Linux jobs, loading the data into Sqlite3, PosgresSQL, Mysql and Oracle databases.  The databases are destroyed at the end of the build.
* [Appveyor CI](https://ci.appveyor.com/project/jayvdb/era-data) - one Microsoft Windows job, producing [artifacts](https://ci.appveyor.com/project/jayvdb/era-data/build/artifacts) from the transformations.

One way to use this repository is to fork the repository on Github, and
add your own transforms or analysis to the scripts in your fork.
They can be run automatically using your own Travis-CI and/or Appveyor CI account.

Alternatively you can recreate the steps performed by Travis-CI or Appveyor on your local machine,
using a private database.

Unix
----
See [.travis.yml](https://github.com/jayvdb/era_data/blob/master/.travis.yml)

`fetch.sh` only requires either the Unix `unzip` or [`7-zip`](http://www.7-zip.org/) in the path,
and either the Unix `wget` or the [Python `wget` package](https://pypi.python.org/pypi/wget)
which can be installed using the pip requirements file `win-requirements.txt`.

Other necessary executables include bzip2, sed, perl, and python.

Windows
-------
The Windows build depend on most of the same commands as the Unix build.

The most common way to achieve that on Windows is to set up
[Cygwin](https://cygwin.com/) or [MSYS](http://www.mingw.org/wiki/msys).

The scripts in this repository have been tested on Cygwin and MSYS 1.0 and MSYS 2.0.

The `7z` executable may be located in a directory containing a space.
All other executables must be in paths that do not include spaces.

See [appveyor.yml](https://github.com/jayvdb/era_data/blob/master/appveyor.yml)

Travis CI configuration
-----------------------
In order to run SQL against a Oracle database, this repository downloads and installs Oracle XE.
To download Oracle XE, the Travis CI settings must include environment variables `ORACLE_LOGIN_ssousername` and `ORACLE_LOGIN_password`.
See [travis-oracle](https://github.com/cbandy/travis-oracle) for more information on how this works.

Contributing
------------
Feel free to submit pull requests for additional transforms or analysis.
Dont worry if you have only tested the changes against the databases that you have access to.
i.e. Open door policy. The more the merrier. Submit pull requests early.
It is my job to figure out how to incorporate any new code into the repository.
