//! The ERA journal lists and the ANZSRC classifications, as an RDF graph.
//!
//! The data is the triple store published with the era_data release [`RELEASE`]: `era_data.nt.gz`, gzipped
//! N-Triples. This crate has none of it. On first use, [`path`] downloads the file from GitHub, checks it against
//! [`SHA256`] and keeps it in [`cache_dir`]. Set `ERA_DATA_NT` to the path of a local copy to use that instead,
//! without a download.
//!
//! ```no_run
//! let graph = era_data::graph()?; // an oxrdf::Graph of every triple
//! # Ok::<(), era_data::Error>(())
//! ```

use std::env;
use std::fmt;
use std::fs::{self, File};
use std::io::{self, BufReader, Read, Write};
use std::path::{Path, PathBuf};

use flate2::read::MultiGzDecoder;
use oxrdf::Graph;
use oxttl::NTriplesParser;
use sha2::{Digest, Sha256};
use tempfile::NamedTempFile;

/// The release the data comes from; `mise run pin` writes it and [`SHA256`].
pub const RELEASE: &str = "data-v3";
/// The SHA-256 of the N-Triples text in the release's file, in hex.
pub const SHA256: &str = "c341bf64bd9035e9ded5fb7ee649e44b4571b097b396703f1657b2e7bd107d7c";
/// The name of the release's file.
pub const FILE: &str = "era_data.nt.gz";
/// The environment variable naming a local copy of the file, which is used as it is.
pub const LOCAL: &str = "ERA_DATA_NT";
/// The environment variable naming the directory to keep downloads in.
pub const CACHE: &str = "ERA_DATA_CACHE";

/// The URL of the release's file.
pub fn url() -> String {
    format!("https://github.com/jayvdb/era_data/releases/download/{RELEASE}/{FILE}")
}

/// What can go wrong getting or reading the file.
#[derive(Debug)]
pub enum Error {
    /// Reading or writing a file failed.
    Io(io::Error),
    /// The download failed.
    Http(Box<ureq::Error>),
    /// A downloaded file is not the one the release published.
    Checksum {
        /// Where the file came from.
        url: String,
        /// Its SHA-256.
        actual: String,
        /// The SHA-256 it should have.
        expected: String,
    },
    /// The file is not valid N-Triples.
    Parse(oxttl::TurtleParseError),
    /// There is no directory to keep the download in: no home directory, and `ERA_DATA_CACHE` is not set.
    NoCacheDir,
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io(e) => write!(f, "{e}"),
            Self::Http(e) => write!(f, "{e}"),
            Self::Checksum { url, actual, expected } => write!(f, "{url} has SHA-256 {actual}, not {expected}"),
            Self::Parse(e) => write!(f, "{e}"),
            Self::NoCacheDir => write!(f, "no cache directory: there is no home directory, and {CACHE} is not set"),
        }
    }
}

impl std::error::Error for Error {}

impl From<io::Error> for Error {
    fn from(e: io::Error) -> Self {
        Self::Io(e)
    }
}

impl From<ureq::Error> for Error {
    fn from(e: ureq::Error) -> Self {
        Self::Http(Box::new(e))
    }
}

impl From<oxttl::TurtleParseError> for Error {
    fn from(e: oxttl::TurtleParseError) -> Self {
        Self::Parse(e)
    }
}

/// The directory the file is kept in once downloaded.
///
/// It is `ERA_DATA_CACHE` when that is set, and otherwise `era_data` in the user's cache directory, as
/// [`dirs::cache_dir`] finds it: `%LOCALAPPDATA%` on Windows, `~/Library/Caches` on macOS and `$XDG_CACHE_HOME`, or
/// `~/.cache`, elsewhere. Each release has its own directory in it. It is `None` when there is no home directory to
/// find a cache directory in.
pub fn cache_dir() -> Option<PathBuf> {
    let base = env::var_os(CACHE).filter(|v| !v.is_empty()).map(PathBuf::from);
    Some(base.or_else(|| dirs::cache_dir().map(|dir| dir.join("era_data")))?.join(RELEASE))
}

/// The SHA-256, in hex, of the N-Triples text in the gzipped file at a path.
///
/// The text is what is checked, not the gzip bytes around it, which differ with the zlib that compressed them.
pub fn sha256(file: impl AsRef<Path>) -> Result<String, Error> {
    let mut digest = Sha256::new();
    let mut f = MultiGzDecoder::new(File::open(file)?);
    let mut block = vec![0; 1 << 20];
    loop {
        let n = f.read(&mut block)?;
        if n == 0 {
            break;
        }
        digest.update(&block[..n]);
    }
    Ok(hex::encode(digest.finalize()))
}

/// Opens a URL for reading: an `http` or `https` URL is downloaded, and `file://` followed by a local path is read.
fn open(url: &str) -> Result<Box<dyn Read>, Error> {
    if let Some(local) = url.strip_prefix("file://") {
        return Ok(Box::new(File::open(local)?));
    }
    Ok(Box::new(ureq::get(url).call()?.into_body().into_reader()))
}

/// The checksum of a kept copy of the file, or `None` when it is not gzip, so that it is downloaded again.
///
/// Any other error, such as being unable to read it, is returned.
fn cached(file: &Path) -> Result<Option<String>, Error> {
    match sha256(file) {
        Err(Error::Io(e))
            if matches!(
                e.kind(),
                io::ErrorKind::InvalidData | io::ErrorKind::InvalidInput | io::ErrorKind::UnexpectedEof
            ) =>
        {
            Ok(None)
        }
        result => result.map(Some),
    }
}

/// The path of the file at `url`, downloaded to `dest` unless a copy with the checksum is there already.
///
/// The download goes to a temporary file beside `dest`, which replaces it, in one rename, only once its checksum
/// matches, so `dest` is never a partial or wrong file. [`Error::Checksum`] is returned when it does not, and the
/// temporary file is removed whatever happens. A copy at `dest` that is damaged, and is not gzip, is downloaded again.
pub fn fetch(url: &str, checksum: &str, dest: impl AsRef<Path>) -> Result<PathBuf, Error> {
    let dest = dest.as_ref().to_path_buf();
    if dest.is_file() && cached(&dest)?.as_deref() == Some(checksum) {
        return Ok(dest);
    }
    let dir = dest.parent().filter(|dir| !dir.as_os_str().is_empty()).unwrap_or(Path::new("."));
    fs::create_dir_all(dir)?;
    let mut part = NamedTempFile::new_in(dir)?;
    io::copy(&mut open(url)?, &mut part)?;
    part.flush()?;
    let actual = sha256(part.path())?;
    if actual != checksum {
        return Err(Error::Checksum { url: url.to_owned(), actual, expected: checksum.to_owned() });
    }
    part.persist(&dest).map_err(|e| e.error)?;
    Ok(dest)
}

/// The path of the file: `ERA_DATA_NT` when that is set, or else the release's file, downloaded if need be.
pub fn path() -> Result<PathBuf, Error> {
    if let Some(local) = env::var_os(LOCAL).filter(|v| !v.is_empty()) {
        return Ok(PathBuf::from(local));
    }
    fetch(&url(), SHA256, cache_dir().ok_or(Error::NoCacheDir)?.join(FILE))
}

/// The whole triple store as N-Triples text, from the gzipped file at a path.
pub fn ntriples_from(file: impl AsRef<Path>) -> Result<String, Error> {
    let mut text = String::new();
    MultiGzDecoder::new(File::open(file)?).read_to_string(&mut text)?;
    Ok(text)
}

/// The whole triple store as N-Triples text, from [`path`].
pub fn ntriples() -> Result<String, Error> {
    ntriples_from(path()?)
}

/// The whole triple store as a graph, from the gzipped file at a path.
pub fn graph_from(file: impl AsRef<Path>) -> Result<Graph, Error> {
    let mut graph = Graph::new();
    let reader = BufReader::new(MultiGzDecoder::new(File::open(file)?));
    for triple in NTriplesParser::new().for_reader(reader) {
        graph.insert(&triple?);
    }
    Ok(graph)
}

/// The whole triple store as a graph, from [`path`].
pub fn graph() -> Result<Graph, Error> {
    graph_from(path()?)
}
