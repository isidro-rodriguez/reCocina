(function () {
  const CARDS = 2;

  // PRNG con semilla (mulberry32): mismo resultado todo el día.
  function mulberry32(seed) {
    return function () {
      seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // Baraja Fisher-Yates con la fecha como semilla; garantiza índices distintos.
  function dailyPicks(n, k) {
    let h = 2166136261;
    for (const c of new Date().toLocaleDateString("sv")) {
      h = Math.imul(h ^ c.charCodeAt(0), 16777619);
    }
    const rand = mulberry32(h >>> 0);
    const idx = Array.from({ length: n }, (_, i) => i);
    for (let i = n - 1; i > 0; i--) {
      const j = Math.floor(rand() * (i + 1));
      [idx[i], idx[j]] = [idx[j], idx[i]];
    }
    return idx.slice(0, Math.min(k, n));
  }

  function formatTime(min) {
    const h = Math.floor(min / 60), m = min % 60;
    return h ? `${h} h${m ? ` ${m} min` : ""}` : `${m} min`;
  }

  function createCard(r) {
    const card = document.createElement("a");
    card.className = "card-recipe";
    card.href = `recetas/${r.slug}/`;
    card.innerHTML =
      `<img src="fotos/${r.slug}.webp" alt="" loading="lazy">` +
      `<div class="card-recipe__body"><h3></h3><p></p></div>`;
    card.querySelector("h3").textContent = r.title;
    const items = [
      r.people && ["people", `${r.people} personas`],
      r.time && ["clock", formatTime(r.time)],
    ].filter(Boolean);

    const meta = card.querySelector("p");
    for (const [icon, text] of items) {
      const span = document.createElement("span");
      span.innerHTML = `<i class="icon icon--${icon}" aria-hidden="true"></i>`;
      span.append(text);
      meta.append(span);
    }
    return card;
  }

  async function render() {
    const box = document.getElementById("daily-recipe");
    if (!box) return;
    try {
      const recipes = await (await fetch("assets/recetas.json")).json();
      if (!recipes.length) return;
      box.replaceChildren(
        ...dailyPicks(recipes.length, CARDS).map((i) => createCard(recipes[i])),
      );
    } catch (err) {
      console.error("Receta del día:", err);
    }
  }

  // Compatible con navegación instantánea; si no existe, carga normal.
  if (window.document$) document$.subscribe(render);
  else document.addEventListener("DOMContentLoaded", render);
})();
