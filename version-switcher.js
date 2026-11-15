// The version dropdown of the Alto docs, and the banner on a page that is not the latest release.
//
// Every version of the docs loads this one file from the root of the site, and reads the list of versions from versions.json
// there, so a page of an old release still offers the newer ones, and a fix here reaches every version. A page that is not served
// from a site with that list (a local preview) keeps the plain text it was built with.
(function () {
  "use strict";
  var slot = document.getElementById("version-slot");
  if (!slot) { return; }
  var root = slot.getAttribute("data-root") || "";
  var current = slot.getAttribute("data-version") || "";

  function pageInVersion(version) {
    var prefix = root + "/" + current + "/";
    var rest = location.pathname.indexOf(prefix) === 0 ? location.pathname.slice(prefix.length) : "";
    return root + "/" + version + "/" + rest;
  }

  function go(version) {
    var target = pageInVersion(version);
    var home = root + "/" + version + "/";
    // Stay on the same page if that version has it; otherwise go to that version's home.
    fetch(target, { method: "HEAD" })
      .then(function (answer) { location.href = answer.ok ? target + location.hash : home; })
      .catch(function () { location.href = home; });
  }

  function banner(text, href, linkText) {
    var bar = document.createElement("div");
    bar.className = "version-banner";
    bar.setAttribute("role", "note");
    bar.appendChild(document.createTextNode(text + " "));
    if (href) {
      var link = document.createElement("a");
      link.href = href;
      link.textContent = linkText;
      bar.appendChild(link);
    }
    var layout = document.querySelector(".layout");
    if (layout && layout.parentNode) { layout.parentNode.insertBefore(bar, layout); }
  }

  fetch(root + "/versions.json", { cache: "no-cache" })
    .then(function (answer) { return answer.json(); })
    .then(function (data) {
      var latest = data.latest;
      var select = document.createElement("select");
      select.id = "version-select";
      select.setAttribute("aria-label", "Version of the docs");
      var entries = [];
      if (latest) { entries.push({ value: "latest", label: "latest (" + latest + ")" }); }
      data.versions.forEach(function (name) {
        entries.push({ value: name, label: name === "dev" ? "dev (unreleased)" : name });
      });
      entries.forEach(function (entry) {
        var option = document.createElement("option");
        option.value = entry.value;
        option.textContent = entry.label;
        option.selected = entry.value === current;
        select.appendChild(option);
      });
      select.addEventListener("change", function () { go(select.value); });
      slot.textContent = "";
      slot.appendChild(select);

      if (current === "dev") {
        banner("This is the development version, which has changes that are not in a release.", latest ? root + "/latest/" : "", "See the latest release.");
      } else if (current !== "latest" && latest && current !== latest) {
        banner("You are reading the docs for " + current + ", which is not the latest release.", pageInVersion("latest"), "See " + latest + ".");
      }
    })
    .catch(function () { /* no list: the page keeps the name of its version that it was built with */ });
})();
