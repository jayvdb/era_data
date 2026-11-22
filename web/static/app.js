// The page: starts worker.js loading the triple store, shows its progress, then searches what it loaded as the
// user types, and shows the journal or conference picked, list by list.
// The URL's fragment names the one shown, as #journal/4465 or #conference/42269.

const LIMIT = 100;
// Whether the results and the detail sit side by side, as style.css lays them out on a wide screen.
const WIDE = matchMedia("(min-width: 56rem)");
const PHASES = { download: "Downloading the triple store", read: "Reading the triples", index: "Building the index" };

const $ = (id) => document.getElementById(id);
let records = [];
let titles = {};
let concepts = {};
const byKey = new Map();
// What the summary says while nothing is searched for.
let idle = "";

// Return an element with the given attributes and children, strings among them made text.
function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [name, value] of Object.entries(attrs)) {
    if (value !== undefined && value !== null && value !== false) {
      node.setAttribute(name, value === true ? "" : value);
    }
  }
  node.append(...children.flat().filter((child) => child !== undefined && child !== null && child !== ""));
  return node;
}

function megabytes(bytes) {
  return (bytes / 1e6).toFixed(1);
}

function showProgress({ phase, done, total }) {
  const bar = $("loading-progress");
  let status = PHASES[phase];
  if (phase === "download" && total) {
    status += `: ${megabytes(done)} of ${megabytes(total)} MB`;
  } else if (phase === "read" && total) {
    status += `: ${Math.round((100 * done) / total)}%`;
  }
  $("loading-status").textContent = status;
  if (total) {
    bar.max = total;
    bar.value = done;
  } else {
    bar.removeAttribute("value");
  }
}

// Return the text a record is found by: its titles, acronyms, ISSNs, with and without the hyphen, and ERA ID.
function haystack(record) {
  const words = [record.eraId];
  for (const entry of record.entries) {
    words.push(...entry.titles, ...entry.foreignTitles, entry.acronym);
    for (const issn of entry.issns) {
      words.push(issn, issn.replace("-", ""));
    }
  }
  return words.filter(Boolean).join("\n").toLowerCase();
}

// The title a record is shown by: its title on the latest list it is on.
function titleOf(record) {
  const last = record.entries[record.entries.length - 1];
  return last.titles[0] || last.foreignTitles[0] || `ERA ID ${record.eraId}`;
}

function ready(data) {
  records = data.records;
  titles = data.titles;
  concepts = data.concepts;
  for (const record of records) {
    record.title = titleOf(record);
    record.haystack = haystack(record);
    record.names = new Set(
      record.entries.flatMap((e) => [...e.titles, ...e.foreignTitles, e.acronym]).map((t) => t.toLowerCase()),
    );
    const issns = record.entries.flatMap((e) => e.issns.flatMap((issn) => [issn, issn.replace("-", "")]));
    record.ids = new Set([record.eraId, ...issns]);
    byKey.set(record.key, record);
  }
  const journals = records.filter((r) => r.kind === "journal").length;
  $("loading").hidden = true;
  $("query").disabled = false;
  $("kind").disabled = false;
  $("query").focus();
  idle =
    `${data.triples.toLocaleString()} triples: ${journals.toLocaleString()} journals and ` +
    `${(records.length - journals).toLocaleString()} conferences. Type to search them.`;
  showFragment(false);
}

// Return how well a record matches the query, lower being better, or -1 if it does not.
function score(record, query, tokens) {
  if (!tokens.every((token) => record.haystack.includes(token))) {
    return -1;
  }
  if (record.ids.has(query)) {
    return 0;
  }
  if (record.names.has(query)) {
    return 1;
  }
  for (const name of record.names) {
    if (name.startsWith(query)) {
      return 2;
    }
  }
  return 3;
}

function search() {
  const query = $("query").value.trim().toLowerCase().replace(/\s+/g, " ");
  const kind = $("kind").value;
  const list = $("results");
  list.replaceChildren();
  if (!query) {
    $("summary").textContent = idle;
    return;
  }
  const tokens = query.split(" ");
  const found = [];
  for (const record of records) {
    if (kind && record.kind !== kind) {
      continue;
    }
    const s = score(record, query, tokens);
    if (s >= 0) {
      found.push([s, record]);
    }
  }
  found.sort(([a, x], [b, y]) => a - b || y.entries.length - x.entries.length || x.title.localeCompare(y.title));
  $("summary").textContent = summary(found.length);
  const current = location.hash.slice(1);
  list.append(...found.slice(0, LIMIT).map(([, record]) => resultItem(record, current)));
}

// Return what the summary says of a search that found count records.
function summary(count) {
  if (count === 0) {
    return "Nothing matches.";
  }
  if (count > LIMIT) {
    return `${count.toLocaleString()} results; the first ${LIMIT} are shown. Type more to narrow them.`;
  }
  return `${count.toLocaleString()} ${count === 1 ? "result" : "results"}.`;
}

// Return a record's item in the results, marked current if its key is current.
function resultItem(record, current) {
  const lists = record.entries.length;
  const button = el(
    "button",
    { type: "button", "data-key": record.key, "aria-current": record.key === current ? "true" : false },
    el("span", { class: "result-title" }, record.title),
    el(
      "span",
      { class: "meta" },
      `${record.kind === "journal" ? "Journal" : "Conference"}, ERA ID ${record.eraId}, on ${lists} `,
      lists === 1 ? "list" : "lists",
    ),
  );
  button.addEventListener("click", () => {
    location.hash = record.key;
  });
  return el("li", {}, button);
}

// Return an ISSN linked to its record in the ISSN Portal, the ISSN International Centre's register of every ISSN.
function issnLink(issn) {
  return el("a", { href: `https://portal.issn.org/resource/ISSN/${encodeURIComponent(issn)}`, rel: "external" }, issn);
}

// Return a field of research as its code and label, linked to the ANZSRC concept.
function field(iri) {
  const [notation, label] = concepts[iri] || ["", iri];
  return el("li", {}, el("a", { href: iri, rel: "external" }, notation), " ", label);
}

function row(name, ...values) {
  const shown = values.flat().filter(Boolean);
  return shown.length ? [el("dt", {}, name), el("dd", {}, ...shown)] : [];
}

// Show a record in the detail pane, moving the keyboard focus to its heading if focus is true.
function showRecord(record, focus) {
  const detail = $("detail");
  const close = el("button", { type: "button", class: "close", "aria-label": "Close" }, "x");
  close.addEventListener("click", () => {
    history.replaceState(null, "", location.pathname + location.search);
    showFragment(false);
    // The focus goes back to the record's result, or to the search box when the results no longer hold it.
    const result = $("results").querySelector(`button[data-key="${CSS.escape(record.key)}"]`);
    (result || $("query")).focus();
  });
  // Only the ERA 2010 lists ranked journals and conferences, so the rank goes beside the title, not on each list.
  const ranked = record.entries.find((entry) => entry.rank);
  // The latest list first.
  const sections = record.entries.toReversed().map((entry) => {
    const titleRows = entry.titles.length > 1 ? row("Titles", entry.titles.join("; ")) : row("Title", entry.titles);
    return el(
      "section",
      {},
      el("h3", {}, titles[entry.list] || entry.list),
      el(
        "dl",
        {},
        titleRows,
        row("Foreign title", entry.foreignTitles.join("; ")),
        row("Acronym", entry.acronym),
        row(
          "ISSN",
          entry.issns.flatMap((issn, n) => [n > 0 && ", ", issnLink(issn)]),
        ),
        row("Multidisciplinary", entry.multidisciplinary && "Yes"),
        row("Fields of research", entry.fields.length > 0 && el("ul", {}, entry.fields.map(field))),
      ),
    );
  });
  detail.replaceChildren(
    close,
    el(
      "h2",
      { tabindex: "-1" },
      record.title,
      ranked && " ",
      ranked && el("span", { class: "badge rank", title: titles[ranked.list] }, `ERA 2010 rank ${ranked.rank}`),
    ),
    el(
      "p",
      { class: "meta" },
      `${record.kind === "journal" ? "Journal" : "Conference"}, ERA ID ${record.eraId}, on `,
      `${record.entries.length} of the lists`,
    ),
    ...sections,
  );
  detail.hidden = false;
  $("panes").classList.add("has-detail");
  if (!WIDE.matches) {
    detail.scrollIntoView();
  }
  if (focus) {
    detail.querySelector("h2").focus({ preventScroll: true });
  }
}

// Show the record the URL's fragment names, if any, and redo the search, which marks it among the results.
// The search rebuilds the results, so a result that had the focus loses it: focus says whether the record's heading
// takes it instead.
function showFragment(focus) {
  const record = byKey.get(decodeURIComponent(location.hash.slice(1)));
  if (record) {
    showRecord(record, focus);
  } else {
    $("detail").hidden = true;
    $("panes").classList.remove("has-detail");
  }
  search();
}

function failed(message) {
  $("loading").classList.add("failed");
  $("loading-status").textContent = `The triple store could not be loaded: ${message}`;
  $("loading-progress").hidden = true;
}

// Search once typing pauses, rather than on every key.
let pending = 0;
$("query").addEventListener("input", () => {
  clearTimeout(pending);
  pending = setTimeout(search, 80);
});
$("kind").addEventListener("change", search);
$("search").addEventListener("submit", (event) => event.preventDefault());
window.addEventListener("hashchange", () => showFragment(true));

// The detail pane sticks below the search bar, so it needs the bar's height, which changes as the bar wraps.
new ResizeObserver(([entry]) => {
  document.documentElement.style.setProperty("--bar-height", `${entry.target.offsetHeight}px`);
}).observe($("bar"));

const worker = new Worker("worker.js");
worker.addEventListener("message", ({ data }) => {
  if (data.type === "progress") {
    showProgress(data);
  } else if (data.type === "done") {
    ready(data);
  } else {
    failed(data.message);
  }
});
worker.addEventListener("error", (event) => failed(event.message || "the worker stopped"));
worker.postMessage("load");
