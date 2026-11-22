// Loads the triple store, era_data.nt.gz, and posts the page what it searches: each journal's and conference's
// entries on the lists, grouped by ERA ID, with the lists' titles and the ANZSRC codes' labels.
//
// It posts {type: "progress", phase, done, total} as it downloads and reads the file, then {type: "done", ...} or
// {type: "error", message}.

const FILE = "era_data.nt.gz";
const NAMESPACE = "https://jayvdb.github.io/era_data/";
const VOCAB = NAMESPACE + "vocab#";
const SKOS = "http://www.w3.org/2004/02/skos/core#";
const TITLE = "http://purl.org/dc/terms/title";
const ISSN = "http://purl.org/ontology/bibo/issn";

// How each property of a journal or conference sets its entry from the property's value.
const SETTERS = {
  [TITLE]: (entry, value) => entry.titles.push(value),
  [ISSN]: (entry, value) => entry.issns.push(value),
  [VOCAB + "foreignTitle"]: (entry, value) => entry.foreignTitles.push(value),
  [VOCAB + "fieldOfResearch"]: (entry, value) => entry.fields.push(value),
  [VOCAB + "acronym"]: (entry, value) => {
    entry.acronym = value;
  },
  [VOCAB + "rank"]: (entry, value) => {
    entry.rank = value;
  },
  [VOCAB + "multidisciplinary"]: (entry, value) => {
    entry.multidisciplinary = value === "true";
  },
  [VOCAB + "eraId"]: (entry, value) => {
    entry.eraId = value;
  },
  [VOCAB + "journalList"]: (entry, value) => {
    entry.list = value;
  },
  [VOCAB + "conferenceList"]: (entry, value) => {
    entry.list = value;
  },
};

// The lists in the order they were published, by the part of their IRI after NAMESPACE.
const LIST_ORDER = [
  "era2010",
  "era2010-conferences",
  "era2012",
  "era2015c",
  "era2015",
  "era2015s",
  "era2015-conferences",
  "era2018",
  "era2023o",
  "era2023",
];

let lastPost = 0;

// Post progress, at most every 100 ms unless it is the end of a phase.
function progress(phase, done, total) {
  const now = Date.now();
  if (now - lastPost >= 100 || done === total) {
    lastPost = now;
    postMessage({ type: "progress", phase, done, total });
  }
}

const ESCAPES = { t: "\t", b: "\b", n: "\n", r: "\r", f: "\f", '"': '"', "'": "'", "\\": "\\" };

// Return the text an N-Triples string literal's body stands for.
function unescape(body) {
  if (!body.includes("\\")) {
    return body;
  }
  return body.replace(/\\(?:u([0-9A-Fa-f]{4})|U([0-9A-Fa-f]{8})|(.))/g, (_, u4, u8, c) =>
    u4 || u8 ? String.fromCodePoint(parseInt(u4 || u8, 16)) : ESCAPES[c],
  );
}

// Download the file, posting progress, and return its bytes.
async function download() {
  const response = await fetch(FILE);
  if (!response.ok) {
    throw new Error(`${FILE}: ${response.status} ${response.statusText}`);
  }
  const total = Number(response.headers.get("Content-Length")) || 0;
  let done = 0;
  const counted = response.body.pipeThrough(
    new TransformStream({
      transform(chunk, controller) {
        done += chunk.length;
        progress("download", done, total);
        controller.enqueue(chunk);
      },
    }),
  );
  const bytes = new Uint8Array(await new Response(counted).arrayBuffer());
  progress("download", done, done);
  return bytes;
}

// Return a stream of the N-Triples text in bytes, and its length in characters where the bytes say it.
// The bytes are gzip, unless a server has already decompressed them; the text is ASCII, so its characters are bytes.
function text(bytes) {
  const stream = new Blob([bytes]).stream();
  if (bytes[0] !== 0x1f || bytes[1] !== 0x8b) {
    return [stream.pipeThrough(new TextDecoderStream()), bytes.length];
  }
  // A gzip file ends with the length of what it holds, modulo 2^32.
  const size = new DataView(bytes.buffer).getUint32(bytes.length - 4, true);
  return [stream.pipeThrough(new DecompressionStream("gzip")).pipeThrough(new TextDecoderStream()), size];
}

// Return the entry a journal's or conference's IRI names, made the first time it is seen.
function entryOf(entries, subject) {
  let entry = entries.get(subject);
  if (!entry) {
    const kind = subject.includes("/journal/") ? "journal" : "conference";
    entry = {
      iri: subject,
      kind,
      list: "",
      eraId: "",
      titles: [],
      foreignTitles: [],
      issns: [],
      acronym: "",
      rank: "",
      multidisciplinary: false,
      fields: [],
    };
    entries.set(subject, entry);
  }
  return entry;
}

// Return a line's triple as its subject, its predicate and its object's IRI or text, or null if it holds none.
// Each line is `<subject> <predicate> object .`, the object an IRI in <> or a literal in "".
function triple(line) {
  const s = line.indexOf("> ");
  const p = line.indexOf("> ", s + 2);
  if (s < 0 || p < 0) {
    return null;
  }
  const object = line.slice(p + 2, line.length - 2);
  const value = object[0] === "<" ? object.slice(1, -1) : unescape(object.slice(1, object.lastIndexOf('"')));
  return [line.slice(1, s), line.slice(s + 3, p), value];
}

// Whether an IRI is a journal's or a conference's, as one list has it.
function isEntry(subject) {
  return subject.startsWith(NAMESPACE) && (subject.includes("/journal/") || subject.includes("/conference/"));
}

// Add a triple to what read() collects: a journal's or conference's property, or another title or ANZSRC label.
function add(store, subject, predicate, value) {
  if (isEntry(subject)) {
    const set = SETTERS[predicate];
    if (set) {
      set(entryOf(store.entries, subject), value);
    }
  } else if (predicate === TITLE) {
    store.titles.set(subject, value);
  } else if (predicate === SKOS + "notation" || predicate === SKOS + "prefLabel") {
    const concept = store.concepts.get(subject) || ["", ""];
    concept[predicate === SKOS + "notation" ? 0 : 1] = value;
    store.concepts.set(subject, concept);
  }
}

// Read the triple store into the entries, the titles of everything else, and the ANZSRC codes, counting the triples.
async function read(bytes) {
  const store = { entries: new Map(), titles: new Map(), concepts: new Map(), triples: 0 };
  const [stream, total] = text(bytes);
  let rest = "";
  let done = 0;
  await stream.pipeTo(
    new WritableStream({
      write(chunk) {
        done += chunk.length;
        const lines = (rest + chunk).split("\n");
        rest = lines.pop();
        for (const line of lines) {
          const found = triple(line);
          if (found) {
            store.triples += 1;
            add(store, ...found);
          }
        }
        progress("read", done, total || done);
      },
    }),
  );
  progress("read", done, done);
  return store;
}

// Return the entries grouped into a record per journal or conference, each record's entries in list order.
function records(entries) {
  const order = (entry) => {
    const n = LIST_ORDER.indexOf(entry.list.slice(NAMESPACE.length));
    return n < 0 ? LIST_ORDER.length : n;
  };
  const byId = new Map();
  for (const entry of entries.values()) {
    const key = `${entry.kind}/${entry.eraId}`;
    let record = byId.get(key);
    if (!record) {
      record = { key, kind: entry.kind, eraId: entry.eraId, entries: [] };
      byId.set(key, record);
    }
    record.entries.push(entry);
  }
  for (const record of byId.values()) {
    record.entries.sort((a, b) => order(a) - order(b) || a.list.localeCompare(b.list));
  }
  return [...byId.values()];
}

addEventListener("message", async () => {
  try {
    const bytes = await download();
    const { entries, titles, concepts, triples } = await read(bytes);
    postMessage({ type: "progress", phase: "index", done: 0, total: 0 });
    postMessage({
      type: "done",
      triples,
      records: records(entries),
      titles: Object.fromEntries(titles),
      concepts: Object.fromEntries(concepts),
    });
  } catch (error) {
    postMessage({ type: "error", message: String(error && error.message ? error.message : error) });
  }
});
