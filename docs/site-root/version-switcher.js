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

  // The icons are drawn here, so that this file works in a page of any version, whatever icons that page carries.
  var SVG = {
    tag: '<path d="M3 12.2V4h8.2L21 13.8 13.8 21z"/><circle cx="7.5" cy="8.5" r="1"/>',
    branch: '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="8" r="2"/><path d="M6 7v10M18 10c0 4-6 3-12 7"/>',
    chev: '<path d="M6 9l6 6 6-6"/>',
    check: '<path d="M5 12.5l4.5 4.5L19 7.5"/>'
  };
  function icon(name, extra) {
    return '<svg class="i ' + (extra || "") + '" viewBox="0 0 24 24" aria-hidden="true">' + SVG[name] + "</svg>";
  }

  fetch(root + "/versions.json", { cache: "no-cache" })
    .then(function (answer) { return answer.json(); })
    .then(function (data) {
      var latest = data.latest;
      var entries = [];
      if (latest) { entries.push({ value: "latest", name: "latest", note: latest + ", the newest release", ico: "tag", label: "latest (" + latest + ")" }); }
      // The releases, newest first as in the list, and the development version after them.
      var ordered = data.versions.filter(function (name) { return name !== "dev"; }).concat(data.versions.indexOf("dev") >= 0 ? ["dev"] : []);
      ordered.forEach(function (name) {
        var isDev = name === "dev";
        entries.push({ value: name, name: name, note: isDev ? "changes not yet in a release" : "", ico: isDev ? "branch" : "tag", label: name });
      });
      var shown = entries.filter(function (entry) { return entry.value === current; })[0] || { label: current };

      var wrap = document.createElement("div");
      wrap.className = "dd";
      var button = document.createElement("button");
      button.type = "button";
      button.className = "dd-btn";
      button.id = "version-button";
      button.setAttribute("aria-haspopup", "menu");
      button.setAttribute("aria-expanded", "false");
      button.setAttribute("aria-label", "Version of the docs");
      button.innerHTML = "<span>" + shown.label + "</span>" + icon("chev", "chev");
      var menu = document.createElement("div");
      menu.className = "dd-menu";
      menu.setAttribute("role", "menu");
      menu.hidden = true;
      var items = entries.map(function (entry) {
        var item = document.createElement("button");
        item.type = "button";
        item.className = "dd-item";
        item.setAttribute("role", "menuitemradio");
        item.setAttribute("aria-checked", entry.value === current ? "true" : "false");
        item.innerHTML = '<span class="dd-ico">' + icon(entry.ico) + '</span><span class="dd-text"><b>' + entry.name + "</b>" +
          (entry.note ? "<small>" + entry.note + "</small>" : "") + "</span>" + icon("check", "dd-check");
        item.addEventListener("click", function () { setOpen(false); if (entry.value !== current) { go(entry.value); } });
        menu.appendChild(item);
        return item;
      });
      function setOpen(isOpen) {
        menu.hidden = !isOpen;
        button.setAttribute("aria-expanded", isOpen ? "true" : "false");
        if (isOpen) { (menu.querySelector('[aria-checked="true"]') || items[0]).focus(); }
      }
      button.addEventListener("click", function () { setOpen(menu.hidden); });
      document.addEventListener("click", function (event) { if (!menu.hidden && !wrap.contains(event.target)) { setOpen(false); } });
      document.addEventListener("keydown", function (event) {
        if (menu.hidden) { return; }
        if (event.key === "Escape") { setOpen(false); button.focus(); }
        var at = items.indexOf(document.activeElement);
        if (event.key === "ArrowDown") { event.preventDefault(); items[(at + 1) % items.length].focus(); }
        if (event.key === "ArrowUp") { event.preventDefault(); items[(at + items.length - 1) % items.length].focus(); }
      });
      wrap.appendChild(button);
      wrap.appendChild(menu);
      slot.textContent = "";
      slot.appendChild(wrap);

      if (current === "dev") {
        banner("This is the development version, which has changes that are not in a release.", latest ? root + "/latest/" : "", "See the latest release.");
      } else if (current !== "latest" && latest && current !== latest) {
        banner("You are reading the docs for " + current + ", which is not the latest release.", pageInVersion("latest"), "See " + latest + ".");
      }
    })
    .catch(function () { /* no list: the page keeps the name of its version that it was built with */ });
})();
