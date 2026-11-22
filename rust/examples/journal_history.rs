//! Prints how one journal changed across the ERA journal lists: its titles, fields of research, ISSNs and rank.
//!
//! Usage: `cargo run --release --example journal_history [-- <ERA journal ID>]`
//!
//! The ERA ID defaults to [`DEFAULT`], a journal whose fields of research and ISSNs change from list to list. A
//! journal has a rank only in ERA 2010, the one list that ranked journals. The journal lists assign fields of
//! research but no socio-economic objectives, so there are none to print.

use std::process::ExitCode;

use oxrdf::vocab::xsd;
use oxrdf::{Graph, Literal, NamedNodeRef, TermRef};

/// IEEE Transactions on Cybernetics: renamed, assigned divisions, then MD, then groups, and given more ISSNs.
const DEFAULT: u32 = 4465;

const TITLE: NamedNodeRef<'_> = NamedNodeRef::new_unchecked("http://purl.org/dc/terms/title");
const ISSN: NamedNodeRef<'_> = NamedNodeRef::new_unchecked("http://purl.org/ontology/bibo/issn");
const NOTATION: NamedNodeRef<'_> = NamedNodeRef::new_unchecked("http://www.w3.org/2004/02/skos/core#notation");
const PREF_LABEL: NamedNodeRef<'_> = NamedNodeRef::new_unchecked("http://www.w3.org/2004/02/skos/core#prefLabel");
const ERA_ID: NamedNodeRef<'_> = NamedNodeRef::new_unchecked("https://jayvdb.github.io/era_data/vocab#eraId");
const JOURNAL_LIST: NamedNodeRef<'_> =
    NamedNodeRef::new_unchecked("https://jayvdb.github.io/era_data/vocab#journalList");
const RANK: NamedNodeRef<'_> = NamedNodeRef::new_unchecked("https://jayvdb.github.io/era_data/vocab#rank");
const MULTIDISCIPLINARY: NamedNodeRef<'_> =
    NamedNodeRef::new_unchecked("https://jayvdb.github.io/era_data/vocab#multidisciplinary");
const FIELD_OF_RESEARCH: NamedNodeRef<'_> =
    NamedNodeRef::new_unchecked("https://jayvdb.github.io/era_data/vocab#fieldOfResearch");

/// One journal list's details of the journal.
struct Entry {
    list: String,
    title: String,
    rank: Option<String>,
    multidisciplinary: bool,
    fields: Vec<(String, String)>,
    issns: Vec<String>,
}

/// The text of a literal, or of the IRI of any other term.
fn text(term: TermRef<'_>) -> String {
    match term {
        TermRef::Literal(literal) => literal.value().to_owned(),
        TermRef::NamedNode(node) => node.as_str().to_owned(),
        other => other.to_string(),
    }
}

/// Each journal list's details of the journal with the ERA ID, in the order of the lists' titles, which is the
/// order they were published in.
fn history(graph: &Graph, eraid: u32) -> Vec<Entry> {
    let id = Literal::new_typed_literal(eraid.to_string(), xsd::INTEGER);
    let mut entries: Vec<Entry> = graph
        .subjects_for_predicate_object(ERA_ID, &id)
        .map(|journal| {
            let list = match graph.object_for_subject_predicate(journal, JOURNAL_LIST) {
                Some(TermRef::NamedNode(list)) => {
                    graph.object_for_subject_predicate(list, TITLE).map(text).unwrap_or_default()
                }
                _ => String::new(),
            };
            let mut fields: Vec<(String, String)> = graph
                .objects_for_subject_predicate(journal, FIELD_OF_RESEARCH)
                .filter_map(|field| match field {
                    TermRef::NamedNode(field) => Some((
                        graph.object_for_subject_predicate(field, NOTATION).map(text).unwrap_or_default(),
                        graph.object_for_subject_predicate(field, PREF_LABEL).map(text).unwrap_or_default(),
                    )),
                    _ => None,
                })
                .collect();
            fields.sort();
            let mut issns: Vec<String> = graph.objects_for_subject_predicate(journal, ISSN).map(text).collect();
            issns.sort();
            Entry {
                list,
                title: graph.object_for_subject_predicate(journal, TITLE).map(text).unwrap_or_default(),
                rank: graph.object_for_subject_predicate(journal, RANK).map(text),
                multidisciplinary: graph
                    .object_for_subject_predicate(journal, MULTIDISCIPLINARY)
                    .is_some_and(|md| text(md) == "true"),
                fields,
                issns,
            }
        })
        .collect();
    entries.sort_by(|a, b| a.list.cmp(&b.list));
    entries
}

fn main() -> ExitCode {
    let eraid = match std::env::args().nth(1).map(|arg| arg.parse()) {
        None => DEFAULT,
        Some(Ok(eraid)) => eraid,
        Some(Err(_)) => {
            eprintln!("The ERA journal ID must be a number");
            return ExitCode::FAILURE;
        }
    };
    let graph = match era_data::graph() {
        Ok(graph) => graph,
        Err(e) => {
            eprintln!("{e}");
            return ExitCode::FAILURE;
        }
    };
    let entries = history(&graph, eraid);
    if entries.is_empty() {
        eprintln!("No journal has the ERA ID {eraid}");
        return ExitCode::FAILURE;
    }
    for entry in entries {
        println!("{}", entry.list);
        println!("  Title: {}", entry.title);
        if let Some(rank) = entry.rank {
            println!("  Rank: {rank}");
        }
        let mut fields: Vec<String> = entry.fields.iter().map(|(code, name)| format!("{code} {name}")).collect();
        if entry.multidisciplinary {
            fields.push("MD Multidisciplinary".to_owned());
        }
        println!("  Fields of research: {}", if fields.is_empty() { "none".to_owned() } else { fields.join("; ") });
        println!("  ISSNs: {}", if entry.issns.is_empty() { "none".to_owned() } else { entry.issns.join(", ") });
    }
    ExitCode::SUCCESS
}
