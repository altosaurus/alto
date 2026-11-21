// Both pages use the shared registry. Only the details page requests data from a plugin author.
(async function () {
  "use strict";
  const table = document.getElementById("plugin-list");
  const details = document.getElementById("plugin-details");
  const container = table || details;
  if (!container) return;
  const status = document.getElementById("plugin-status");

  async function readJSON(url) {
    const response = await fetch(url, {
      cache: "no-cache", credentials: "omit", referrerPolicy: "no-referrer",
      signal: AbortSignal.timeout(10000)
    });
    if (!response.ok) throw new Error("Could not read JSON");
    return response.json();
  }

  function httpsURL(value) {
    if (typeof value !== "string") return null;
    try {
      const url = new URL(value);
      return url.protocol === "https:" && !url.username && !url.password ? url.href : null;
    } catch {
      return null;
    }
  }

  function element(tag, text) {
    const node = document.createElement(tag);
    node.textContent = text;
    return node;
  }

  function link(label, href) {
    const node = element("a", label);
    node.href = href;
    return node;
  }

  let registry;
  try {
    registry = await readJSON(container.dataset.registry);
    if (!Array.isArray(registry)) throw new Error("Expected an array");
  } catch {
    status.textContent = "The plugin registry could not be loaded. Refresh to try again.";
    return;
  }

  if (table) {
    if (!registry.length) {
      status.textContent = "No plugins are registered yet.";
      return;
    }
    const rows = document.createDocumentFragment();
    for (const plugin of registry) {
      const row = document.createElement("tr");
      const url = new URL(table.dataset.details, location.href);
      url.searchParams.set("id", plugin.id);
      row.insertCell().append(link(plugin.name, url.href));
      row.insertCell().textContent = plugin.code;
      row.insertCell().textContent = plugin.description;
      rows.append(row);
    }
    table.tBodies[0].replaceChildren(rows);
    return;
  }

  const id = new URLSearchParams(location.search).get("id");
  const plugin = registry.find(entry => entry.id === id);
  if (!plugin) {
    status.textContent = "This plugin could not be found in the registry.";
    return;
  }
  document.querySelector("article h1").textContent = plugin.name;
  document.title = plugin.name + " · Alto";
  details.append(element("p", plugin.description));
  details.append(element("p", "Install in Alto with registration code " + plugin.code + "."));
  const repository = httpsURL(plugin.repository);
  if (repository) details.append(link("Plugin repository", repository));

  status.textContent = "";
  if (!plugin.metadata) return;
  status.textContent = "Loading release information…";
  try {
    const url = httpsURL(plugin.metadata);
    if (!url) throw new Error("Invalid metadata URL");
    const info = await readJSON(url);
    if (!info || typeof info !== "object" || Array.isArray(info)) throw new Error("Expected an object");
    if (typeof info.about === "string" && info.about.trim()) details.append(element("p", info.about));
    const facts = document.createElement("dl");
    for (const [field, label] of [["version", "Plugin version"], ["compatible_alto", "Compatible Alto versions"]]) {
      if (typeof info[field] === "string" && info[field].trim()) {
        facts.append(element("dt", label), element("dd", info[field]));
      }
    }
    if (facts.children.length) details.append(facts);
    const links = document.createElement("ul");
    for (const [field, label] of [["documentation", "Plugin documentation"], ["download", "Download plugin"]]) {
      const href = httpsURL(info[field]);
      if (href) {
        const item = document.createElement("li");
        item.append(link(label, href));
        links.append(item);
      }
    }
    if (links.children.length) details.append(links);
    status.textContent = "";
  } catch {
    status.textContent = "Current release information is unavailable. Check the plugin repository for updates.";
  }
})();
