//! Tests of the era_data crate, against the file named by `ERA_DATA_NT`: a local build of the release's file.
//! Each test passes, doing nothing, when `ERA_DATA_NT` is not set.

use std::fs;
use std::io::Write;

use flate2::Compression;
use flate2::write::GzEncoder;
use std::path::PathBuf;

use oxrdf::{Literal, NamedNodeRef, TermRef};
use tempfile::TempDir;

const SOUTHERLY: &str = "https://jayvdb.github.io/era_data/era2010/journal/11637";
const TITLE: &str = "http://purl.org/dc/terms/title";
const RANK: &str = "https://jayvdb.github.io/era_data/vocab#rank";
const PREF_LABEL: &str = "http://www.w3.org/2004/02/skos/core#prefLabel";

fn local() -> Option<PathBuf> {
    std::env::var_os(era_data::LOCAL).filter(|v| !v.is_empty()).map(PathBuf::from)
}

/// A new temporary directory, removed when the returned value is dropped, even if the test panics.
fn scratch() -> TempDir {
    TempDir::with_prefix("era_data-test-").unwrap()
}

fn object<'a>(graph: &'a oxrdf::Graph, subject: &'a str, predicate: &'a str) -> Option<TermRef<'a>> {
    graph.object_for_subject_predicate(NamedNodeRef::new(subject).unwrap(), NamedNodeRef::new(predicate).unwrap())
}

#[test]
fn pinned_checksum() {
    let Some(file) = local() else { return };
    assert_eq!(era_data::sha256(file).unwrap(), era_data::SHA256);
}

#[test]
fn graph() {
    let Some(file) = local() else { return };
    let graph = era_data::graph_from(file).unwrap();
    assert_eq!(graph.len(), 1_606_400);
    let title = Literal::new_simple_literal("Southerly: a review of Australian literature");
    assert_eq!(object(&graph, SOUTHERLY, TITLE), Some(title.as_ref().into()));
    assert_eq!(object(&graph, SOUTHERLY, RANK), Some(Literal::new_simple_literal("B").as_ref().into()));
    // Non-ASCII names survive the file's \u escapes.
    let label = Literal::new_language_tagged_literal("M\u{101}ori Environmental Knowledge", "en").unwrap();
    let field = "http://purl.org/au-research/vocabulary/anzsrc-for/2008/050208";
    assert_eq!(object(&graph, field, PREF_LABEL), Some(label.as_ref().into()));
}

#[test]
fn ntriples_is_ascii() {
    let Some(file) = local() else { return };
    let text = era_data::ntriples_from(file).unwrap();
    assert!(text.is_ascii());
    assert_eq!(text.lines().count(), 1_606_400);
}

#[test]
fn fetch_downloads_and_caches() {
    let Some(file) = local() else { return };
    let dir = scratch();
    let dest = dir.path().join(era_data::FILE);
    let url = format!("file://{}", file.display());
    assert_eq!(era_data::fetch(&url, era_data::SHA256, &dest).unwrap(), dest);
    assert_eq!(era_data::sha256(&dest).unwrap(), era_data::SHA256);
    // A copy with the checksum is reused, so the URL is not opened.
    assert_eq!(era_data::fetch("file:///nonexistent", era_data::SHA256, &dest).unwrap(), dest);
}

#[test]
fn cache_dir_is_per_release() {
    let dir = era_data::cache_dir().expect("a cache directory");
    assert!(dir.ends_with(era_data::RELEASE));
}

/// A kept copy that is not gzip is downloaded again, rather than failing every call until it is removed.
#[test]
fn fetch_replaces_a_damaged_copy() {
    let Some(file) = local() else { return };
    let dir = scratch();
    let dest = dir.path().join(era_data::FILE);
    fs::write(&dest, b"not gzip").unwrap();
    let url = format!("file://{}", file.display());
    assert_eq!(era_data::fetch(&url, era_data::SHA256, &dest).unwrap(), dest);
    assert_eq!(era_data::sha256(&dest).unwrap(), era_data::SHA256);
}

#[test]
fn fetch_rejects_a_wrong_file() {
    if local().is_none() {
        return;
    }
    let dir = scratch();
    let wrong = dir.path().join("wrong.nt.gz");
    let mut gz = GzEncoder::new(fs::File::create(&wrong).unwrap(), Compression::default());
    gz.write_all(b"<urn:a> <urn:b> <urn:c> .\n").unwrap();
    gz.finish().unwrap();
    let dest = dir.path().join("cache").join(era_data::FILE);
    let result = era_data::fetch(&format!("file://{}", wrong.display()), era_data::SHA256, &dest);
    assert!(matches!(result, Err(era_data::Error::Checksum { .. })));
    // Neither the file nor the temporary one it was downloaded to is left.
    assert!(fs::read_dir(dir.path().join("cache")).unwrap().next().is_none());
}
