/*!
 * site.js — shared front-end behaviour for the Djamal TOE portfolio.
 *
 * Consolidates what used to be a copy-pasted inline <script> block on every
 * page (.qmd files and project-shell.html includes) into a single file:
 *   1. Mobile navigation drawer (open/close, backdrop, Escape key).
 *   2. Scroll-reveal entrance animation for cards/sections via IntersectionObserver.
 *   3. A smooth sliding indicator behind the active/hovered top-nav link.
 *   4. A theme switcher menu (5 themes), injected into every .topbar,
 *      that flips [data-theme] on <html> and remembers the choice in
 *      localStorage.
 *   5. A layout switcher (default sidebar-left shell vs. "Mirror",
 *      sidebar-right), same injection pattern, flips [data-layout] on
 *      <html>.
 *      (The actual flash-of-wrong-appearance fix for both, on first
 *      load, is a separate tiny inline script — see
 *      meta/theme-init.html — since this file loads too late in the
 *      page to run before paint.)
 *
 * No dependencies, no build step — plain ES2017 that runs as a classic
 * <script> tag. Every animated behaviour is skipped in favour of an
 * instant, static state when the user has requested reduced motion.
 */
(function () {
  "use strict";

  var prefersReducedMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── 1. Mobile navigation drawer ───────────────────────────────────── */
  function initDrawer() {
    var menuToggle = document.getElementById("menuToggle");
    var mobileDrawer = document.getElementById("mobileDrawer");
    var drawerBackdrop = document.getElementById("drawerBackdrop");

    if (!menuToggle || !mobileDrawer || !drawerBackdrop) return;

    function toggleDrawer(force) {
      var open =
        typeof force === "boolean"
          ? force
          : !mobileDrawer.classList.contains("open");
      mobileDrawer.classList.toggle("open", open);
      drawerBackdrop.classList.toggle("open", open);
      menuToggle.setAttribute("aria-expanded", open ? "true" : "false");
      document.body.style.overflow = open ? "hidden" : "";
    }

    menuToggle.addEventListener("click", function () {
      toggleDrawer();
    });
    drawerBackdrop.addEventListener("click", function () {
      toggleDrawer(false);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") toggleDrawer(false);
    });
  }

  /* ── 2. Scroll-reveal entrance animation ───────────────────────────── */
  function initScrollReveal() {
    var selector =
      ".hero, .section-card, .timeline-card, .project-card, .page-link-card, .contact-card";
    var targets = Array.prototype.slice.call(document.querySelectorAll(selector));
    if (!targets.length) return;

    if (prefersReducedMotion || !("IntersectionObserver" in window)) {
      targets.forEach(function (el) {
        el.classList.add("is-visible");
      });
      return;
    }

    targets.forEach(function (el) {
      el.classList.add("reveal");
    });

    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );

    targets.forEach(function (el) {
      io.observe(el);
    });
  }

  /* ── 3. Smooth active/hover indicator on the top nav ───────────────── */
  function initNavIndicator() {
    var nav = document.querySelector(".topbar .nav-links");
    if (!nav) return;

    var links = Array.prototype.slice.call(nav.querySelectorAll("a"));
    if (!links.length) return;

    var indicator = document.createElement("span");
    indicator.className = "nav-indicator";
    indicator.setAttribute("aria-hidden", "true");
    nav.insertBefore(indicator, nav.firstChild);

    var activeLink = nav.querySelector("a.active") || null;

    function moveIndicatorTo(link, animate) {
      if (!link) {
        indicator.style.opacity = "0";
        return;
      }
      var navRect = nav.getBoundingClientRect();
      var linkRect = link.getBoundingClientRect();
      if (!animate || prefersReducedMotion) {
        indicator.style.transition = "none";
      } else {
        indicator.style.transition = "";
      }
      indicator.style.width = linkRect.width + "px";
      indicator.style.transform =
        "translateX(" + (linkRect.left - navRect.left) + "px)";
      indicator.style.opacity = "1";
      if (!animate || prefersReducedMotion) {
        // Force reflow so the next transition (if any) re-enables cleanly.
        void indicator.offsetWidth;
        indicator.style.transition = "";
      }
    }

    function resetToActive(animate) {
      moveIndicatorTo(activeLink, animate);
    }

    links.forEach(function (link) {
      link.addEventListener("mouseenter", function () {
        moveIndicatorTo(link, true);
      });
      link.addEventListener("focus", function () {
        moveIndicatorTo(link, true);
      });
    });

    nav.addEventListener("mouseleave", function () {
      resetToActive(true);
    });
    nav.addEventListener("focusout", function (event) {
      if (!nav.contains(event.relatedTarget)) resetToActive(true);
    });

    window.addEventListener("resize", function () {
      resetToActive(false);
    });

    // Initial placement without animating in from the corner.
    resetToActive(false);
  }

  /* ── 4. Theme switcher (5 themes via one menu) ─────────────────────── */
  var THEME_KEY = "theme";
  // "dark" is the default and stored as the absent attribute, same as
  // before — every other entry stamps data-theme to its own value.
  var THEMES = [
    { value: "dark", label: "Dark", swatchBg: "#060816", swatchAccent: "#4f8cff" },
    { value: "light", label: "Linen", swatchBg: "#f7f2ea", swatchAccent: "#b1592f" },
    { value: "nocturne", label: "Nocturne", swatchBg: "#0a1012", swatchAccent: "#22c3b6" },
    { value: "volt", label: "Volt", swatchBg: "#050505", swatchAccent: "#e01a82" },
    { value: "sage", label: "Sage", swatchBg: "#f2f5f0", swatchAccent: "#4f7a63" }
  ];

  function getTheme() {
    var current = document.documentElement.getAttribute("data-theme");
    var known = THEMES.some(function (t) {
      return t.value === current;
    });
    return known ? current : "dark";
  }

  function applyTheme(theme) {
    if (theme === "dark") {
      document.documentElement.removeAttribute("data-theme");
    } else {
      document.documentElement.setAttribute("data-theme", theme);
    }
    try {
      window.localStorage.setItem(THEME_KEY, theme);
    } catch (e) {
      /* Storage unavailable — the switch still works for this page view,
         it just won't be remembered on the next visit. */
    }
    document.querySelectorAll(".theme-switcher").forEach(function (widget) {
      syncThemeMenu(widget, theme);
    });
  }

  function syncThemeMenu(widget, theme) {
    widget.querySelectorAll(".theme-menu-item").forEach(function (item) {
      var isActive = item.getAttribute("data-theme-value") === theme;
      item.classList.toggle("active", isActive);
      item.setAttribute("aria-checked", isActive ? "true" : "false");
    });
  }

  function closeThemeMenu(widget) {
    var menu = widget.querySelector(".theme-menu");
    var trigger = widget.querySelector(".theme-toggle");
    if (!menu || menu.hidden) return;
    menu.hidden = true;
    if (trigger) trigger.setAttribute("aria-expanded", "false");
  }

  function openThemeMenu(widget) {
    var menu = widget.querySelector(".theme-menu");
    var trigger = widget.querySelector(".theme-toggle");
    if (!menu) return;
    // Only one menu open at a time across the page (there's normally
    // just one topbar, but this stays correct if that ever changes).
    document.querySelectorAll(".theme-switcher").forEach(function (w) {
      if (w !== widget) closeThemeMenu(w);
    });
    menu.hidden = false;
    if (trigger) trigger.setAttribute("aria-expanded", "true");
  }

  function initThemeSwitcher() {
    // One switcher per page; injected once into every .topbar so root
    // pages and every project-shell.html include get it for free
    // without hand-editing dozens of files.
    document.querySelectorAll(".topbar").forEach(function (topbar) {
      if (topbar.querySelector(".theme-switcher")) return;

      var widget = document.createElement("div");
      widget.className = "theme-switcher";

      var trigger = document.createElement("button");
      trigger.type = "button";
      trigger.className = "theme-toggle";
      trigger.setAttribute("aria-haspopup", "true");
      trigger.setAttribute("aria-expanded", "false");
      trigger.setAttribute("aria-label", "Choose theme");
      trigger.innerHTML = '<i class="bi bi-palette2" aria-hidden="true"></i>';

      var menu = document.createElement("div");
      menu.className = "theme-menu";
      menu.setAttribute("role", "menu");
      menu.setAttribute("aria-label", "Theme");
      menu.hidden = true;

      THEMES.forEach(function (theme) {
        var item = document.createElement("button");
        item.type = "button";
        item.className = "theme-menu-item";
        item.setAttribute("role", "menuitemradio");
        item.setAttribute("data-theme-value", theme.value);

        var swatch = document.createElement("span");
        swatch.className = "theme-swatch";
        swatch.setAttribute("aria-hidden", "true");
        swatch.style.background =
          "linear-gradient(135deg, " +
          theme.swatchBg +
          " 50%, " +
          theme.swatchAccent +
          " 50%)";

        var label = document.createElement("span");
        label.textContent = theme.label;

        item.appendChild(swatch);
        item.appendChild(label);
        item.addEventListener("click", function () {
          applyTheme(theme.value);
          closeThemeMenu(widget);
          trigger.focus();
        });

        menu.appendChild(item);
      });

      trigger.addEventListener("click", function () {
        if (menu.hidden) {
          openThemeMenu(widget);
        } else {
          closeThemeMenu(widget);
        }
      });

      document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && !menu.hidden) {
          closeThemeMenu(widget);
          trigger.focus();
        }
      });

      document.addEventListener("click", function (event) {
        if (!widget.contains(event.target)) closeThemeMenu(widget);
      });

      widget.appendChild(trigger);
      widget.appendChild(menu);
      syncThemeMenu(widget, getTheme());

      var navLinks = topbar.querySelector(".nav-links");
      if (navLinks && navLinks.parentNode === topbar) {
        navLinks.insertAdjacentElement("afterend", widget);
      } else {
        topbar.appendChild(widget);
      }
    });
  }

  /* ── 5. Layout switcher (default sidebar-left shell vs. "Mirror") ──── */
  var LAYOUT_KEY = "layout";

  function getLayout() {
    return document.documentElement.getAttribute("data-layout") === "mirror"
      ? "mirror"
      : "sidebar";
  }

  function applyLayout(layout) {
    if (layout === "mirror") {
      document.documentElement.setAttribute("data-layout", "mirror");
    } else {
      document.documentElement.removeAttribute("data-layout");
    }
    try {
      window.localStorage.setItem(LAYOUT_KEY, layout);
    } catch (e) {
      /* Storage unavailable — same graceful fallback as the theme. */
    }
    document.querySelectorAll(".layout-toggle").forEach(function (button) {
      updateLayoutButton(button, layout);
    });
  }

  function updateLayoutButton(button, layout) {
    var goingTo = layout === "mirror" ? "sidebar" : "mirror";
    button.setAttribute(
      "aria-label",
      goingTo === "mirror"
        ? "Switch to mirrored layout (sidebar on the right)"
        : "Switch to default layout (sidebar on the left)"
    );
    button.setAttribute("aria-pressed", layout === "mirror" ? "true" : "false");
    // Icon shows the layout a click will switch TO, not the current one —
    // same convention as the theme switcher's icon used to follow.
    button.innerHTML =
      goingTo === "mirror"
        ? '<i class="bi bi-layout-sidebar-reverse" aria-hidden="true"></i>'
        : '<i class="bi bi-layout-sidebar-inset" aria-hidden="true"></i>';
  }

  function initLayoutSwitcher() {
    // Same injection pattern as the theme switcher: one per .topbar,
    // docked right after it so both controls travel together.
    document.querySelectorAll(".topbar").forEach(function (topbar) {
      if (topbar.querySelector(".layout-toggle")) return;

      var button = document.createElement("button");
      button.type = "button";
      button.className = "layout-toggle";
      updateLayoutButton(button, getLayout());

      button.addEventListener("click", function () {
        applyLayout(getLayout() === "mirror" ? "sidebar" : "mirror");
      });

      var switcher = topbar.querySelector(".theme-switcher");
      if (switcher && switcher.parentNode === topbar) {
        switcher.insertAdjacentElement("afterend", button);
      } else {
        topbar.appendChild(button);
      }
    });
  }

  function init() {
    initDrawer();
    initScrollReveal();
    initNavIndicator();
    initThemeSwitcher();
    initLayoutSwitcher();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
