(function () {
  var root = document.documentElement;
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  // Mavzu: tanlangan bo'lsa o'sha, aks holda tizim mavzusi
  var media = window.matchMedia ? matchMedia("(prefers-color-scheme: dark)") : null;
  var toggle = document.querySelector(".theme-toggle");
  function apply(theme) {
    root.setAttribute("data-theme", theme);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", theme === "dark" ? "#0d0e13" : "#fbfaff");
    if (toggle) toggle.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
  }
  apply(root.getAttribute("data-theme") || (media && media.matches ? "dark" : "light"));
  if (toggle) toggle.addEventListener("click", function () {
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    store.set("theme", next);
    apply(next);
  });
  if (media && media.addEventListener) media.addEventListener("change", function (e) {
    if (!store.get("theme")) apply(e.matches ? "dark" : "light");
  });

  // Header soyasi
  var header = document.querySelector(".site-header");
  function onScroll() { if (header) header.classList.toggle("scrolled", window.scrollY > 8); }
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Til menyusi: tashqariga bosilganda yopiladi
  document.addEventListener("click", function (e) {
    document.querySelectorAll("details.lang[open]").forEach(function (d) { if (!d.contains(e.target)) d.removeAttribute("open"); });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") document.querySelectorAll("details.lang[open]").forEach(function (d) { d.removeAttribute("open"); });
  });

  // Scroll paytida paydo bo'lish
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !/[?&]static\b/.test(location.search)) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  // Galereya tugmalari
  var gallery = document.querySelector(".gallery");
  document.querySelectorAll("[data-scroll]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      if (!gallery) return;
      var dir = Number(btn.getAttribute("data-scroll")) * (root.dir === "rtl" ? -1 : 1);
      gallery.scrollBy({ left: dir * Math.min(gallery.clientWidth * 0.8, 600), behavior: "smooth" });
    });
  });

  // Yo'riqnoma mundarijasi: joriy bo'limni belgilash
  var tocLinks = document.querySelectorAll(".toc a");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var tio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          tocLinks.forEach(function (a) { a.classList.remove("active"); });
          var a = map[en.target.id];
          if (a) a.classList.add("active");
        }
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    Object.keys(map).forEach(function (id) { var el = document.getElementById(id); if (el) tio.observe(el); });
  }

  // Blog: o'qish progressi va sanani til bo'yicha formatlash
  var bar = document.querySelector(".read-progress span");
  var post = document.querySelector(".post");
  if (bar && post) {
    var ticking = false;
    var upd = function () {
      var r = post.getBoundingClientRect();
      var total = r.height - window.innerHeight;
      var p = total > 0 ? Math.min(1, Math.max(0, -r.top / total)) : 1;
      bar.style.transform = "scaleX(" + p + ")";
      ticking = false;
    };
    addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(upd); } }, { passive: true });
    upd();
  }
  var UZ_MONTHS = ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"];
  document.querySelectorAll("time[data-fmt]").forEach(function (t) {
    var lang = root.getAttribute("lang");
    var d = new Date(t.getAttribute("datetime") + "T12:00:00");
    if (isNaN(d)) return;
    // Brauzerlarda o'zbekcha oy nomlari yo'q (Intl "M10" qaytaradi) — qo'lda formatlaymiz
    if (lang === "uz") { t.textContent = d.getDate() + "-" + UZ_MONTHS[d.getMonth()] + ", " + d.getFullYear(); return; }
    try { t.textContent = new Intl.DateTimeFormat(lang, { year: "numeric", month: "long", day: "numeric" }).format(d); } catch (e) {}
  });

  // Brauzer tiliga mos versiyani taklif qilish (majburiy redirect emas — SEO uchun)
  var langs = window.DOTDAY_LANGS;
  var banner = document.querySelector(".lang-suggest");
  if (langs && banner && !store.get("lang-choice")) {
    var current = root.getAttribute("data-lang");
    var prefs = navigator.languages || [navigator.language || ""];
    var pick = null;
    for (var i = 0; i < prefs.length && !pick; i++) {
      var p = (prefs[i] || "").toLowerCase();
      if (p === "pt-br") pick = "pt-BR";
      else if (p.indexOf("pt") === 0) pick = null;
      else { var base = p.split("-")[0]; if (base === "in") base = "id"; if (langs[base]) pick = base; }
      if (pick === current) break;
    }
    if (pick && pick !== current && langs[pick]) {
      var info = langs[pick];
      var page = root.getAttribute("data-page") || "";
      var alt = document.querySelector('link[rel="alternate"][hreflang="' + pick + '"]');
      var target = alt ? alt.getAttribute("href").replace(/^https:\/\/dotday\.uz\//, root.getAttribute("data-root"))
        : root.getAttribute("data-root") + info.path + (page && info.pages.indexOf(page) >= 0 ? page : "");
      banner.setAttribute("lang", pick);
      banner.setAttribute("dir", info.dir);
      banner.querySelector("span").textContent = info.msg;
      var go = banner.querySelector("a");
      go.textContent = info.go;
      go.setAttribute("href", target);
      go.setAttribute("hreflang", pick);
      go.addEventListener("click", function () { store.set("lang-choice", pick); });
      banner.querySelector("button").addEventListener("click", function () { store.set("lang-choice", current); banner.hidden = true; });
      banner.hidden = false;
    }
  }
  document.querySelectorAll(".lang a[hreflang]").forEach(function (a) {
    a.addEventListener("click", function () { store.set("lang-choice", a.getAttribute("hreflang")); });
  });
})();
