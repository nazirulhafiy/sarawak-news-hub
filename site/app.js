(() => {
  const themeToggle = document.querySelector("[data-theme-toggle]");
  const navToggle = document.querySelector("[data-nav-toggle]");
  const siteNav = document.querySelector(".site-nav");

  function closeNavigation() {
    navToggle?.setAttribute("aria-expanded", "false");
    navToggle?.setAttribute("aria-label", "Open navigation");
    navToggle?.setAttribute("title", "Open navigation");
    siteNav?.classList.remove("is-open");
  }

  navToggle?.addEventListener("click", () => {
    const isOpen = navToggle.getAttribute("aria-expanded") === "true";
    navToggle.setAttribute("aria-expanded", String(!isOpen));
    navToggle.setAttribute("aria-label", isOpen ? "Open navigation" : "Close navigation");
    navToggle.setAttribute("title", isOpen ? "Open navigation" : "Close navigation");
    siteNav?.classList.toggle("is-open", !isOpen);
  });

  siteNav?.addEventListener("click", (event) => {
    if (event.target.closest("a")) closeNavigation();
  });

  document.addEventListener("click", (event) => {
    if (!siteNav?.classList.contains("is-open")) return;
    if (event.target.closest("[data-nav-toggle], .site-nav")) return;
    closeNavigation();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && siteNav?.classList.contains("is-open")) {
      closeNavigation();
      navToggle?.focus();
    }
  });

  const themeMedia = window.matchMedia?.("(prefers-color-scheme: dark)");
  let storedTheme = null;
  try {
    storedTheme = localStorage.getItem("sarawak-theme");
  } catch (error) {}

  function setTheme(theme, persist = false) {
    const isDark = theme === "dark";
    if (isDark) document.documentElement.setAttribute("data-theme", "dark");
    else document.documentElement.removeAttribute("data-theme");
    if (persist) {
      try {
        localStorage.setItem("sarawak-theme", isDark ? "dark" : "light");
      } catch (error) {}
    }
    if (themeToggle) {
      const nextLabel = isDark ? "Switch to light mode" : "Switch to dark mode";
      themeToggle.setAttribute("aria-label", nextLabel);
      themeToggle.setAttribute("title", nextLabel);
      themeToggle.setAttribute("aria-pressed", String(isDark));
    }
  }

  setTheme(document.documentElement.hasAttribute("data-theme") ? "dark" : "light");
  themeToggle?.addEventListener("click", () => {
    setTheme(document.documentElement.hasAttribute("data-theme") ? "light" : "dark", true);
  });
  if (!storedTheme && themeMedia) {
    themeMedia.addEventListener?.("change", (event) => setTheme(event.matches ? "dark" : "light"));
  }

  const siteBar = document.querySelector(".bar");
  if (siteBar) {
    function updateStickyBar() {
      siteBar.classList.toggle("is-scrolled", window.scrollY > 0);
    }
    window.addEventListener("scroll", updateStickyBar, { passive: true });
    updateStickyBar();
  }

  const backToTop = document.querySelector("[data-back-to-top]");
  if (backToTop) {
    const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    let hideTimer = 0;

    function updateBackToTop() {
      const show = window.scrollY >= 600;
      const reduce = Boolean(reduceMotion?.matches);
      if (show) {
        window.clearTimeout(hideTimer);
        backToTop.hidden = false;
        if (reduce) backToTop.classList.add("is-visible");
        else requestAnimationFrame(() => {
          if (window.scrollY >= 600) backToTop.classList.add("is-visible");
        });
        return;
      }
      backToTop.classList.remove("is-visible");
      if (reduce || backToTop.hidden) {
        backToTop.hidden = true;
        return;
      }
      window.clearTimeout(hideTimer);
      hideTimer = window.setTimeout(() => {
        if (window.scrollY < 600) backToTop.hidden = true;
      }, 200);
    }

    backToTop.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: reduceMotion?.matches ? "auto" : "smooth" });
    });
    window.addEventListener("scroll", updateBackToTop, { passive: true });
    updateBackToTop();
  }
})();
