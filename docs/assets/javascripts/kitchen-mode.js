// Modo cocina: mantiene la pantalla encendida con la Screen Wake Lock API.
(() => {
  const STORAGE_KEY = "modo-cocina";
  const button = document.querySelector('[data-md-component="cocina"]');
  if (!button || !("wakeLock" in navigator)) return;

  let lock = null;
  const isOn = () => button.getAttribute("aria-pressed") === "true";

  const acquire = async () => {
    try {
      lock = await navigator.wakeLock.request("screen");
      return true;
    } catch (err) {
      console.warn("Wake Lock no disponible:", err);
      return false;
    }
  };

  const setState = async (on) => {
    if (on && !(await acquire())) on = false;
    button.setAttribute("aria-pressed", String(on));
    sessionStorage.setItem(STORAGE_KEY, on ? "1" : "0");
    if (!on) {
      await lock?.release();
      lock = null;
    }
  };

  button.hidden = false;
  button.addEventListener("click", () => setState(!isOn()));

  // El navegador libera el lock al ocultar la pestaña: hay que volver a pedirlo.
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible" && isOn()) acquire();
  });

  if (sessionStorage.getItem(STORAGE_KEY) === "1") setState(true);
})();
