# Diccionario ortográfico es_ES

Diccionario Hunspell del español (España) que usa `tests/test_spelling.py` a través de
[spylls](https://github.com/zverok/spylls), un port a Python de Hunspell.

- **Origen:** [LibreOffice/dictionaries](https://github.com/LibreOffice/dictionaries/tree/master/es)
    (`es_ES.aff`, `es_ES.dic`).
- **Licencia:** triple GPLv3 / LGPLv3 / MPL-1.1 — ver los ficheros en `LICENSE/`.
- **Allowlist:** `allowlist.txt` con palabras válidas que el diccionario no incluye
    (términos culinarios, marcas, préstamos, formas verbales con pronombre…).

Para actualizar el diccionario, vuelve a descargar `es_ES.aff` y `es_ES.dic` desde el
repositorio de origen.

Cualquier palabra que el diccionario no reconozca y no figure en `allowlist.txt` hará
fallar el test.
