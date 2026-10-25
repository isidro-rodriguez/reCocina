// Receta interactiva: tachar ingredientes y marcar el paso actual de la preparación.
(() => {
  const init = () => {
    const ingredientsHeading = document.getElementById("ingredientes");
    const stepsHeading = document.getElementById("preparacion");
    if (!ingredientsHeading && !stepsHeading) return;

    // Cada sección acaba en el siguiente h2: Opcional y Alternativas no son pasos.
    const section = (heading, tag) => {
      const found = [];
      for (let el = heading?.nextElementSibling; el && el.tagName !== "H2"; el = el.nextElementSibling) {
        if (el.tagName === tag) found.push(el);
      }
      return found;
    };

    // Todas las listas: también las de "Para la salsa:", "Para decorar:", etc.
    const items = section(ingredientsHeading, "UL").flatMap((ul) => [...ul.children]);
    const steps = section(stepsHeading, "P");

    // document$ puede emitir más de una vez para la misma página.
    if ([...items, ...steps].some((el) => el.hasAttribute("role"))) return;

    const slug = location.pathname.split("/").filter(Boolean).pop() ?? "";
    const STORAGE_KEY = `recipe-steps:${slug}`;

    const load = () => {
      try {
        return JSON.parse(sessionStorage.getItem(STORAGE_KEY)) ?? {};
      } catch {
        return {};
      }
    };

    const save = () => {
      const state = {
        checked: items.flatMap((li, i) => (li.getAttribute("aria-checked") === "true" ? [i] : [])),
        current: steps.findIndex((p) => p.hasAttribute("aria-current")),
      };
      try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      } catch {
        // Sin almacenamiento (modo privado, cuota): solo se pierde el estado al recargar.
      }
    };

    const setCurrent = (index) => {
      steps.forEach((p, i) => {
        if (i === index) p.setAttribute("aria-current", "step");
        else p.removeAttribute("aria-current");
        const done = index >= 0 && i < index;
        p.classList.toggle("done", done);
        const next = p.nextElementSibling;
        if (next?.tagName === "OL") next.classList.toggle("done", done);
      });
    };

    // Clic, Enter o Espacio; los enlaces de dentro siguen navegando.
    const activate = (el, action) => {
      el.tabIndex = 0;
      el.addEventListener("click", (e) => {
        if (!e.target.closest("a")) action();
      });
      el.addEventListener("keydown", (e) => {
        if (e.target !== el || (e.key !== "Enter" && e.key !== " ")) return;
        e.preventDefault();
        action();
      });
    };

    items.forEach((li) => {
      li.setAttribute("role", "checkbox");
      li.setAttribute("aria-checked", "false");
      activate(li, () => {
        li.setAttribute("aria-checked", String(li.getAttribute("aria-checked") !== "true"));
        save();
      });
    });

    steps.forEach((p, i) => {
      p.setAttribute("role", "button");
      activate(p, () => {
        setCurrent(p.hasAttribute("aria-current") ? -1 : i);
        save();
      });
    });

    const state = load();
    for (const i of state.checked ?? []) items[i]?.setAttribute("aria-checked", "true");
    if (Number.isInteger(state.current)) setCurrent(state.current);
  };

  // Compatible con navegación instantánea; si no existe, carga normal.
  if (window.document$) document$.subscribe(init);
  else document.addEventListener("DOMContentLoaded", init);
})();
