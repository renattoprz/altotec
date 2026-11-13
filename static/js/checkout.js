// Muestra la provincia solo cuando el departamento es Lima.
(function () {
  "use strict";
  var dep = document.getElementById("id_department");
  var prov = document.getElementById("id_lima_province");
  if (!dep || !prov) return;
  var wrapper = prov.closest(".field");
  function sync() { wrapper.hidden = dep.value !== "15"; }
  dep.addEventListener("change", sync);
  sync();
})();
