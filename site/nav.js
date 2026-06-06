/* =======================================================
   Shared site navigation — single source of truth.
   Edit the NAV_ITEMS array once; every page updates.
   Each page includes:  <div id="site-nav"></div>
                        <script src="nav.js"></script>
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
})();
