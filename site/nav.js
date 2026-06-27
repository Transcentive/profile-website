/* =======================================================
   Shared site chrome: nav and footer, one single source of truth.
   Edit NAV_ITEMS or FOOTER_HTML once; every page updates.
   Each page includes, at the top:  <div id="site-nav"></div>
   and at the bottom:               <div id="site-footer"></div>
   with <script src="nav.js"></script> before </body>.
   ======================================================= */
(function () {
  var NAV_ITEMS = [
    { href: "track-systems.html",     label: "T1: Systems" },
    { href: "track-linguistics.html", label: "T2: Linguistics" },
    { href: "track-logistics.html",   label: "T3: Logistics" },
    { href: "track-ai.html",          label: "T4: AI" },
    { href: "track-human.html",       label: "T5: Human Touch" }
  ];

  // Current file name, e.g. "track-ai.html" (defaults to index.html at site root)
  var page = (location.pathname.split("/").pop() || "index.html").toLowerCase();
  var onIndex = (page === "" || page === "index.html");
  var connectHref = onIndex ? "#connect" : "index.html#connect";

  var links = NAV_ITEMS.map(function (it) {
    var active = (it.href.toLowerCase() === page) ? ' class="active"' : "";
    return '<a href="' + it.href + '"' + active + ">" + it.label + "</a>";
  }).join("\n      ");

  var html =
    '<nav class="nav" data-screen-label="Nav">' +
      '<div class="nav-inner">' +
        '<a href="index.html" class="nav-brand">Thomas J. Sherlock<span class="dot">.</span></a>' +
        '<div class="nav-links">' + links + "</div>" +
        '<a href="' + connectHref + '" class="nav-connect">Connect</a>' +
      "</div>" +
    "</nav>";

  var mount = document.getElementById("site-nav");
  if (mount) {
    mount.outerHTML = html;
  } else {
    document.body.insertAdjacentHTML("afterbegin", html);
  }

  // ---- Footer: one definition, injected into #site-footer on every page ----
  var FOOTER_HTML =
    '<footer class="footer" id="connect" data-screen-label="Footer">' +
      '<div class="colophon">' +
        '© 2026 Thomas J. Sherlock &nbsp;·&nbsp; Rutherford, NJ &nbsp;·&nbsp; v.2026.05' +
        '<div class="seal">' +
          '<span class="silver">Architecting,</span> ' +
          '<span class="gold">Exploring,</span> ' +
          '<span class="ox">Navigating.</span>' +
        '</div>' +
      '</div>' +
    '</footer>';

  var fmount = document.getElementById("site-footer");
  if (fmount) {
    fmount.outerHTML = FOOTER_HTML;
  } else {
    document.body.insertAdjacentHTML("beforeend", FOOTER_HTML);
  }
})();
