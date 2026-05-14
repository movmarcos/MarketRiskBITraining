/* ============================================================
   Market Risk BI Training — optional sign-in + progress tracking.

   Loads after docs/javascripts/config.js and the Supabase JS SDK.
   If config.js still has placeholder values, this script silently
   no-ops so anonymous browsing is unaffected.

   Behaviour:
     - Renders a sign-in / user-info pill in the site header.
     - On module pages, renders a "Mark as complete" CTA at the bottom.
     - On the homepage, renders a progress widget below the hero.
     - Adds a checkmark next to completed modules in the sidebar.
     - Re-renders on auth state changes.
   ============================================================ */
(function () {
  "use strict";

  // ---- Constants --------------------------------------------------------
  var TOTAL_MODULES = 27;
  var TABLE = "user_progress";

  // ---- Guards: config + SDK presence ------------------------------------
  function configReady() {
    var url = window.SUPABASE_URL;
    var key = window.SUPABASE_ANON_KEY;
    if (typeof url !== "string" || typeof key !== "string") return false;
    if (!url || !key) return false;
    if (url.indexOf("YOUR_PROJECT_REF") !== -1) return false;
    if (key.indexOf("YOUR_ANON_KEY_HERE") !== -1) return false;
    if (!window.supabase || typeof window.supabase.createClient !== "function") return false;
    return true;
  }

  if (!configReady()) {
    // Silent no-op. Anonymous users see no difference at all.
    return;
  }

  // ---- Supabase client --------------------------------------------------
  var client = window.supabase.createClient(window.SUPABASE_URL, window.SUPABASE_ANON_KEY, {
    auth: { persistSession: true, autoRefreshToken: true }
  });

  // ---- State ------------------------------------------------------------
  var state = {
    user: null,
    completed: new Set() // module_id strings, e.g. "01", "13"
  };

  // ---- Utilities --------------------------------------------------------
  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  function currentModuleId() {
    var m = /\/modules\/(\d+)-/.exec(window.location.pathname);
    return m ? m[1] : null;
  }

  function isHomePage() {
    var path = window.location.pathname.replace(/\/+$/, "");
    if (path === "" || path === "/") return true;
    // GitHub Pages project sites have a base path; index page ends with the site root or /index.html
    if (/\/index\.html$/.test(path)) return true;
    // mkdocs builds /index.html at the root of any "use_directory_urls" subtree;
    // detect the homepage by looking for the hero block on the page.
    return !!$(".mr-hero");
  }

  function moduleIdFromHref(href) {
    if (!href) return null;
    var m = /\/modules\/(\d+)-/.exec(href);
    return m ? m[1] : null;
  }

  function formatDate(iso) {
    try {
      var d = new Date(iso);
      if (isNaN(d.getTime())) return "";
      return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
    } catch (_) {
      return "";
    }
  }

  // ---- Last-visited tracking (localStorage) ------------------------------
  var LAST_VISITED_KEY = "mr_last_visited";

  function recordVisit() {
    var moduleId = currentModuleId();
    if (!moduleId) return;
    var h1 = document.querySelector("article h1, .md-content__inner h1");
    var title = h1 ? h1.textContent.trim() : "Module " + moduleId;
    try {
      localStorage.setItem(LAST_VISITED_KEY, JSON.stringify({
        module_id: moduleId,
        title: title,
        url: window.location.pathname,
        at: new Date().toISOString()
      }));
    } catch (_) {
      // Private mode / storage disabled — safe to ignore.
    }
  }

  function readLastVisited() {
    try {
      var raw = localStorage.getItem(LAST_VISITED_KEY);
      if (!raw) return null;
      var obj = JSON.parse(raw);
      if (!obj || !obj.module_id || !obj.url) return null;
      return obj;
    } catch (_) {
      return null;
    }
  }

  // ---- Data layer -------------------------------------------------------
  function loadProgress() {
    if (!state.user) {
      state.completed = new Set();
      return Promise.resolve();
    }
    return client
      .from(TABLE)
      .select("module_id, completed_at")
      .eq("user_id", state.user.id)
      .then(function (res) {
        if (res.error) {
          console.warn("[progress-tracking] load failed:", res.error.message);
          state.completed = new Set();
          return;
        }
        state.completed = new Set((res.data || []).map(function (r) { return r.module_id; }));
      });
  }

  function markComplete(moduleId) {
    if (!state.user) return Promise.resolve();
    var row = {
      user_id: state.user.id,
      module_id: moduleId,
      completed_at: new Date().toISOString()
    };
    return client
      .from(TABLE)
      .upsert(row, { onConflict: "user_id,module_id" })
      .then(function (res) {
        if (res.error) {
          console.warn("[progress-tracking] mark complete failed:", res.error.message);
          return null;
        }
        state.completed.add(moduleId);
        return row.completed_at;
      });
  }

  function markIncomplete(moduleId) {
    if (!state.user) return Promise.resolve();
    return client
      .from(TABLE)
      .delete()
      .eq("user_id", state.user.id)
      .eq("module_id", moduleId)
      .then(function (res) {
        if (res.error) {
          console.warn("[progress-tracking] mark incomplete failed:", res.error.message);
          return;
        }
        state.completed.delete(moduleId);
      });
  }

  // ---- Auth flows -------------------------------------------------------
  function signInWithGoogle() {
    client.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: window.location.href }
    });
  }

  function signInWithEmail() {
    var email = window.prompt("Enter your email — we'll send you a one-click magic sign-in link:");
    if (!email) return;
    email = email.trim();
    if (!email) return;
    client.auth.signInWithOtp({
      email: email,
      options: { emailRedirectTo: window.location.href }
    }).then(function (res) {
      if (res.error) {
        window.alert("Sign-in failed: " + res.error.message);
      } else {
        window.alert("Check your inbox — we sent a magic link to " + email + ".");
      }
    });
  }

  function signOut() {
    client.auth.signOut().then(function () {
      // onAuthStateChange handles the re-render.
    });
  }

  // ---- UI: header auth pill --------------------------------------------
  function renderAuthPill() {
    var header = $(".md-header__inner") || $(".md-header");
    if (!header) return;

    var existing = $("#mr-auth");
    if (existing) existing.remove();

    var wrap = document.createElement("div");
    wrap.id = "mr-auth";
    wrap.className = "mr-auth";

    if (state.user) {
      var who = document.createElement("span");
      who.className = "mr-auth__user";
      who.textContent = state.user.email || "Signed in";

      var out = document.createElement("button");
      out.type = "button";
      out.className = "mr-auth-button mr-auth-button--ghost";
      out.textContent = "Sign out";
      out.addEventListener("click", signOut);

      wrap.appendChild(who);
      wrap.appendChild(out);
    } else {
      var inBtn = document.createElement("button");
      inBtn.type = "button";
      inBtn.className = "mr-auth-button";
      inBtn.textContent = "Sign in to track progress";
      inBtn.addEventListener("click", openSignInChooser);
      wrap.appendChild(inBtn);
    }

    header.appendChild(wrap);
  }

  function openSignInChooser() {
    // Remove any existing chooser
    var existing = $("#mr-auth-chooser");
    if (existing) existing.remove();

    var overlay = document.createElement("div");
    overlay.id = "mr-auth-chooser";
    overlay.className = "mr-auth-chooser";
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) overlay.remove();
    });

    var card = document.createElement("div");
    card.className = "mr-auth-chooser__card";

    var title = document.createElement("h3");
    title.className = "mr-auth-chooser__title";
    title.textContent = "Sign in to track your progress";
    card.appendChild(title);

    var sub = document.createElement("p");
    sub.className = "mr-auth-chooser__sub";
    sub.textContent = "Your completions sync across devices. You can sign out at any time.";
    card.appendChild(sub);

    var g = document.createElement("button");
    g.type = "button";
    g.className = "mr-auth-button mr-auth-chooser__btn";
    g.textContent = "Continue with Google";
    g.addEventListener("click", function () { overlay.remove(); signInWithGoogle(); });
    card.appendChild(g);

    var e = document.createElement("button");
    e.type = "button";
    e.className = "mr-auth-button mr-auth-button--ghost mr-auth-chooser__btn";
    e.textContent = "Email me a magic link";
    e.addEventListener("click", function () { overlay.remove(); signInWithEmail(); });
    card.appendChild(e);

    var cancel = document.createElement("button");
    cancel.type = "button";
    cancel.className = "mr-auth-chooser__cancel";
    cancel.textContent = "Cancel";
    cancel.addEventListener("click", function () { overlay.remove(); });
    card.appendChild(cancel);

    overlay.appendChild(card);
    document.body.appendChild(overlay);
  }

  // ---- UI: module mark-complete CTA ------------------------------------
  function renderModuleCTA() {
    var moduleId = currentModuleId();
    if (!moduleId) return;
    var article = $("article.md-content__inner") || $(".md-content__inner") || $(".md-content");
    if (!article) return;

    var existing = $("#mr-mark-complete");
    if (existing) existing.remove();

    if (!state.user) return; // CTA is only visible to signed-in users.

    var done = state.completed.has(moduleId);

    var wrap = document.createElement("div");
    wrap.id = "mr-mark-complete";
    wrap.className = "mr-mark-complete";

    if (done) {
      // We don't store completion date in memory here; show generic copy.
      // To get the date back we'd need to keep it in state; for simplicity show
      // "Completed" without the date when re-rendered from in-memory state.
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "mr-mark-complete-cta mr-mark-complete-cta--done";
      btn.textContent = "✓ Completed";
      btn.disabled = true;
      wrap.appendChild(btn);

      var undo = document.createElement("a");
      undo.href = "#";
      undo.className = "mr-mark-incomplete-link";
      undo.textContent = "Mark as incomplete";
      undo.addEventListener("click", function (ev) {
        ev.preventDefault();
        markIncomplete(moduleId).then(function () {
          renderModuleCTA();
          renderSidebarChecks();
        });
      });
      wrap.appendChild(undo);
    } else {
      var cta = document.createElement("button");
      cta.type = "button";
      cta.className = "mr-mark-complete-cta";
      cta.textContent = "Mark module " + moduleId + " as complete";
      cta.addEventListener("click", function () {
        cta.disabled = true;
        markComplete(moduleId).then(function (when) {
          renderModuleCTA();
          renderSidebarChecks();
          // If user navigates home next, the progress widget will reflect the change.
          if (when) {
            var msg = $("#mr-mark-complete .mr-mark-complete-cta--done");
            if (msg) msg.textContent = "✓ Completed on " + formatDate(when);
          }
        });
      });
      wrap.appendChild(cta);
    }

    article.appendChild(wrap);
  }

  // ---- UI: sidebar checkmarks ------------------------------------------
  function renderSidebarChecks() {
    // Clear existing checks first
    $$(".mr-sidebar-check").forEach(function (el) { el.remove(); });

    if (!state.user || state.completed.size === 0) return;

    var links = $$(".md-nav--primary a.md-nav__link");
    links.forEach(function (a) {
      var id = moduleIdFromHref(a.getAttribute("href") || "");
      if (!id) return;
      if (!state.completed.has(id)) return;
      var mark = document.createElement("span");
      mark.className = "mr-sidebar-check";
      mark.setAttribute("aria-label", "Module completed");
      mark.textContent = "✓";
      a.insertBefore(mark, a.firstChild);
    });
  }

  // ---- UI: homepage progress widget ------------------------------------
  function renderHomeWidget() {
    if (!isHomePage()) return;
    var hero = $(".mr-hero");
    if (!hero) return;

    var existing = $("#mr-progress");
    if (existing) existing.remove();

    if (!state.user) return; // Only show when signed in.

    var done = 0;
    state.completed.forEach(function () { done++; });
    var pct = TOTAL_MODULES > 0 ? Math.round((done / TOTAL_MODULES) * 100) : 0;

    var wrap = document.createElement("div");
    wrap.id = "mr-progress";
    wrap.className = "mr-progress";

    var label = document.createElement("p");
    label.className = "mr-progress__label";
    label.innerHTML =
      "Your progress: <strong>" + done + "</strong> of " +
      TOTAL_MODULES + " modules complete <span class=\"mr-progress__pct\">(" + pct + "%)</span>";
    wrap.appendChild(label);

    var bar = document.createElement("progress");
    bar.className = "mr-progress__bar";
    bar.max = TOTAL_MODULES;
    bar.value = done;
    wrap.appendChild(bar);

    hero.parentNode.insertBefore(wrap, hero.nextSibling);
  }

  function renderContinueCTA() {
    if (!isHomePage()) return;
    var hero = $(".mr-hero");
    if (!hero) return;

    var existing = $("#mr-continue");
    if (existing) existing.remove();

    if (!state.user) return;

    var last = readLastVisited();
    if (!last) return;
    // Don't suggest continuing a module the user has already completed.
    if (state.completed.has(last.module_id)) return;

    var wrap = document.createElement("a");
    wrap.id = "mr-continue";
    wrap.className = "mr-continue";
    wrap.href = last.url;

    var label = document.createElement("span");
    label.className = "mr-continue__label";
    label.textContent = "Continue where you left off";
    wrap.appendChild(label);

    var title = document.createElement("span");
    title.className = "mr-continue__title";
    title.textContent = last.title;
    wrap.appendChild(title);

    var arrow = document.createElement("span");
    arrow.className = "mr-continue__arrow";
    arrow.textContent = "→";
    wrap.appendChild(arrow);

    // Insert after the hero, before the progress widget if it's there
    var anchor = $("#mr-progress") || hero.nextSibling;
    hero.parentNode.insertBefore(wrap, anchor);
  }

  // ---- Render orchestration --------------------------------------------
  function renderAll() {
    renderAuthPill();
    renderModuleCTA();
    renderSidebarChecks();
    renderHomeWidget();
    renderContinueCTA();
  }

  // ---- Init -------------------------------------------------------------
  function init() {
    // Always record the visit if we're on a module page — anonymous or signed in.
    // The Continue CTA still only renders for signed-in users (see renderContinueCTA).
    recordVisit();

    client.auth.getSession().then(function (res) {
      var session = res && res.data ? res.data.session : null;
      state.user = session ? session.user : null;

      loadProgress().then(renderAll);
    });

    client.auth.onAuthStateChange(function (_event, session) {
      state.user = session ? session.user : null;
      loadProgress().then(renderAll);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
