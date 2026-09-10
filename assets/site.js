/*!
 * site.js — shared front-end behaviour for the Djamal TOE portfolio.
 *
 * Consolidates what used to be a copy-pasted inline <script> block on every
 * page (.qmd files and project-shell.html includes) into a single file:
 *   1. Mobile navigation drawer (open/close, backdrop, Escape key).
 *   2. Scroll-reveal entrance animation for cards/sections via IntersectionObserver.
 *   3. A smooth sliding indicator behind the active/hovered top-nav link.
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

  function init() {
    initDrawer();
    initScrollReveal();
    initNavIndicator();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
