# era_data vocabulary

<!-- vocab_md.py writes this file from vocab/vocab.ttl and vocab/shapes.ttl: edit those, and run
     `mise run vocab`. -->

The terms the era_data triple store describes the Excellence in Research for Australia (ERA) journal and conference
lists with. Each journal list is a JournalList, and each journal on it a Journal of that list alone: a journal on
several lists has an entry on each, which share its ERA ID. Conference lists and conferences are the same, as
ConferenceList and Conference. The ANZSRC codes are SKOS concepts under the IRIs their publishers use, and the titles
and ISSNs are Dublin Core and BIBO terms.

vocab/vocab.ttl defines the vocabulary in OWL, and vocab/shapes.ttl gives the shape of the triple store in SHACL, which
`mise run shacl` validates it against. The terms below use these prefixes:

- `era:` https://jayvdb.github.io/era_data/vocab#
- `bibo:` http://purl.org/ontology/bibo/
- `dcterms:` http://purl.org/dc/terms/
- `rdf:` http://www.w3.org/1999/02/22-rdf-syntax-ns#
- `skos:` http://www.w3.org/2004/02/skos/core#
- `xsd:` http://www.w3.org/2001/XMLSchema#

## Classes

### `era:ConferenceList`

One ERA conference list: the ERA 2010 list, which ranked conferences, or the ERA 2015 submission list, which did not.
Its IRI is https://jayvdb.github.io/era_data/era2010-conferences or
https://jayvdb.github.io/era_data/era2015-conferences.

- `dcterms:title`: exactly one `rdf:langString`. The list's title, such as ERA 2010 conference list.
- `era:fieldOfResearchScheme`: exactly one `skos:ConceptScheme`. The ANZSRC Fields of Research edition whose codes the
  list assigns: ANZSRC 2008 for the lists of ERA 2010 to 2018, and ANZSRC 2020 for the ERA 2023 lists.
- Each field of research of a conference on the list is in the list's fieldOfResearchScheme.
- No other property but `rdf:type`.

### `era:Conference`

A conference or conference series as one conference list has it. Its IRI is its list's, followed by /conference/ and its
ERA ID, such as https://jayvdb.github.io/era_data/era2010-conferences/conference/42269.

- `dcterms:title`: exactly one `xsd:string`. The conference's title, as the list has it.
- `era:acronym`: at most one `xsd:string`. The conference's acronym, where the list gives one.
- `era:conferenceList`: exactly one `era:ConferenceList`. The conference list the conference is on.
- `era:eraId`: exactly one `xsd:integer`. The ERA ID the list gives the journal or conference. The lists keep an ID from
  one to the next, so it is what links a journal's, or a conference's, entries on different lists.
- `era:fieldOfResearch`: any number of `skos:Concept`. A field of research the list assigns the journal or conference: a
  division or group of the list's fieldOfResearchScheme.
- `era:multidisciplinary`: exactly one `xsd:boolean`. Whether the list marks the journal or conference MD,
  multidisciplinary.
- `era:rank`: at most one `xsd:string`: one of `A`, `B`, `C`. The journal's or conference's rank. Only the ERA 2010
  lists ranked them, and they left some unranked.
- No other property but `rdf:type`.

### `era:JournalList`

One ERA journal list, as the Australian Research Council published it. Its IRI is https://jayvdb.github.io/era_data/
followed by the prefix of its tables: era2010, era2012, era2015, era2015c (the ERA 2015 consultation list), era2015s
(the ERA 2015 submitted list), era2018, era2023 (the revised ERA 2023 list) and era2023o (the ERA 2023 list as first
published).

- `dcterms:title`: exactly one `rdf:langString`. The list's title, such as ERA 2010 journal list.
- `era:fieldOfResearchScheme`: exactly one `skos:ConceptScheme`. The ANZSRC Fields of Research edition whose codes the
  list assigns: ANZSRC 2008 for the lists of ERA 2010 to 2018, and ANZSRC 2020 for the ERA 2023 lists.
- Each field of research of a journal on the list is in the list's fieldOfResearchScheme. Only a warning, as the revised
  ERA 2023 list gives journal 36264 the code 4709, which ANZSRC 2020 does not have.
- No other property but `rdf:type`.

### `era:Journal`

A journal as one journal list has it. Its IRI is its list's, followed by /journal/ and its ERA ID, such as
https://jayvdb.github.io/era_data/era2010/journal/11637.

- `bibo:issn`: any number of `xsd:string`. An ISSN of the journal, as the list has it: a few are malformed, such as
  1463--770, and some have a lower-case x.
- `dcterms:title`: exactly one `xsd:string`. The journal's title, as the list has it.
- `era:eraId`: exactly one `xsd:integer`. The ERA ID the list gives the journal or conference. The lists keep an ID from
  one to the next, so it is what links a journal's, or a conference's, entries on different lists.
- `era:fieldOfResearch`: any number of `skos:Concept`. A field of research the list assigns the journal or conference: a
  division or group of the list's fieldOfResearchScheme. Only a warning, as the revised ERA 2023 list gives journal
  36264 the code 4709, which ANZSRC 2020 does not have.
- `era:foreignTitle`: at most one `xsd:string`. The journal's title in another language, where the list gives one
  besides its title.
- `era:journalList`: exactly one `era:JournalList`. The journal list the journal is on.
- `era:multidisciplinary`: exactly one `xsd:boolean`. Whether the list marks the journal or conference MD,
  multidisciplinary.
- `era:rank`: at most one `xsd:string`: one of `A*`, `A`, `B`, `C`. The journal's or conference's rank. Only the ERA
  2010 lists ranked them, and they left some unranked.
- No other property but `rdf:type`.

### `skos:ConceptScheme`

One ANZSRC classification: the Fields of Research or the Socio-Economic Objectives of ANZSRC 2008 or ANZSRC 2020. Its
IRI is the one it is published under: by ARDC, under http://purl.org/au-research/vocabulary/, for ANZSRC 2008, and by
the ABS and ARDC, under https://linked.data.gov.au/def/, for ANZSRC 2020.

- `dcterms:title`: exactly one `rdf:langString`. The classification's title, such as ANZSRC 2008 Fields of Research.
- No other property but `rdf:type`.

### `skos:Concept`

One ANZSRC code: a division, a group in it, or a field or objective in that. Its IRI is its classification's followed by
its code, such as https://linked.data.gov.au/def/anzsrc-for/2020/4601.

- `skos:broader`: at most one `skos:Concept`. The code's division, for a group, or its group, for a field or objective.
- `skos:inScheme`: exactly one `skos:ConceptScheme`. The classification the code is in.
- `skos:notation`: exactly one `xsd:string` matching `^[0-9]{2}([0-9]{2}){0,2}$`. The code, of two digits for a
  division, four for a group and six for a field or objective.
- `skos:prefLabel`: exactly one `rdf:langString`. The code's name, as the ABS publishes it.
- `skos:topConceptOf`: at most one `skos:ConceptScheme`. The classification, for a division, which has no broader code.
- No other property but `rdf:type`.
