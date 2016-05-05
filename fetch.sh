#!/bin/sh

# Check dependencies
WGET=`which wget`
UNZIP=`which unzip`
UNZIP_EXTRACT_ARG=""
BUNZIP2=`which bunzip2`
BZIP2=`which bzip2`

SEVENZIP=`which 7z`

if [ -z "$UNZIP" ]; then
  if [ -z "$SEVENZIP" ]; then
    echo "unzip and 7z are both missing; can not continue"
    exit 1
  else
    echo "unzip missing; falling back to 7z x"
    UNZIP="$SEVENZIP"
    UNZIP_EXTRACT_ARG="x"
  fi
fi

# If the bzip pair are missing; use a noop instead
if [ -z "$BUNZIP2" -o -z "$BZIP2" ]; then
  BUNZIP2=true
  BZIP2=true
fi

if [ -z "$WGET" ]; then
  echo "wget missing; falling back to python -m wget"
  WGET="python -m wget"
fi

CACHE_DIR=.cache/era_xml

if [ -f $CACHE_DIR/ERA2010_journal_title_list.xml* -a -f $CACHE_DIR/ERA2012_journal_title_list.xml* -a -f $CACHE_DIR/ERA2015_submitted_journal_title_list.xml* ]; then
  cp $CACHE_DIR/* .
  "$BUNZIP2" *.xml.bz2
  exit 0
fi

# Download files and extract contents

mkdir downloads
cd downloads

$WGET http://content.webarchive.nla.gov.au/gov/wayback/20120317002747/http://www.arc.gov.au/zip/ERA2010_tech_pack.zip

mkdir ERA2010_tech_pack
cd ERA2010_tech_pack
"$UNZIP" $UNZIP_EXTRACT_ARG ../ERA2010_tech_pack.zip code-table/XML-Format/ERA2010_journal_title_list.xml
cd ..

# The 2012 tech pack can be obtained from here, and it contains the journal list in XSLX format
# wget http://content.webarchive.nla.gov.au/gov/wayback/20140212022156/http://www.arc.gov.au//zip/ERA-SEER2012-tech-pack.zip
# 
# mkdir ERA2012_tech_pack
# cd ERA2012_tech_pack
# unzip ../ERA-SEER2012-tech-pack.zip
# cd ..

# However we can download only the journal list
$WGET http://content.webarchive.nla.gov.au/gov/wayback/20140212052430/http://www.arc.gov.au/xls/era12/ERA2012JournalList.xlsx

# We could extract the xlsx, and extract the data that way
# mkdir ERA2012_journal_list
# cd ERA2012_journal_list
# unzip ../ERA2012JournalList.xlsx
# cd ..

$WGET http://www.arc.gov.au/sites/default/files/filedepot/Public/ERA/ERA%202015/ERA2015_Submitted_Journal_ListV2.xlsx

# Leave the downloads directory
cd ..

# Extract ERA 2012 journal list and convert it to XML
python -c "import pyexcel, pyexcel.ext.xlsx; pyexcel.save_as(file_name='downloads/ERA2012JournalList.xlsx', dest_file_name='downloads/ERA2012JournalList.json', name_columns_by_row=0)"

python -c "import json, dicttoxml; data = json.load(open('downloads/ERA2012JournalList.json')); f = open('downloads/ERA2012JournalList.messy-xml', 'wb'); f.write(dicttoxml.dicttoxml(data, attr_type=False, custom_root='JournalList')); f.close()"

# Post-process the dicttoxml XML into the ERA 2010 journal list XML format
lxmlproc --output downloads/ERA2012JournalList.xml  era_journal_list_tidy.xsl downloads/ERA2012JournalList.messy-xml

# Extract ERA 2015 journal list and convert it to XML
python -c "import pyexcel, pyexcel.ext.xlsx; pyexcel.save_as(file_name='downloads/ERA2015_Submitted_Journal_ListV2.xlsx', dest_file_name='downloads/ERA2015JournalList_submitted.json', name_columns_by_row=0)"

python -c "import json, dicttoxml; data = json.load(open('downloads/ERA2015JournalList_submitted.json')); f = open('downloads/ERA2015JournalList_submitted.messy-xml', 'wb'); f.write(dicttoxml.dicttoxml(data, attr_type=False, custom_root='JournalList')); f.close()"

# Post-process the dicttoxml XML into the ERA 2010 journal list XML format
lxmlproc --output downloads/ERA2015JournalList_submitted.xml  era_journal_list_tidy.xsl downloads/ERA2015JournalList_submitted.messy-xml

# Copy xml files into the output directory
mkdir -p $CACHE_DIR/
cp downloads/ERA2010_tech_pack/code-table/XML-Format/ERA2010_journal_title_list.xml $CACHE_DIR
cp downloads/ERA2012JournalList.xml $CACHE_DIR/ERA2012_journal_title_list.xml
cp downloads/ERA2015JournalList_submitted.xml $CACHE_DIR/ERA2015_submitted_journal_title_list.xml

cp $CACHE_DIR/* .

"$BZIP2" $CACHE_DIR/*
