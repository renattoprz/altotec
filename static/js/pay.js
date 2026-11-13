// Pago con Culqi Checkout v4. La tarjeta se tokeniza en el navegador (Culqi);
// al servidor solo viaja el token. El servidor crea el cargo con su llave secreta.
(function () {
  "use strict";
  var cfg = document.getElementById("pay-config");
  var btn = document.getElementById("pay-btn");
  var errorBox = document.getElementById("pay-error");
  if (!cfg || !btn) return;
  var csrf = document.querySelector("input[name=csrfmiddlewaretoken]").value;

  function showError(message) {
    errorBox.textContent = message || "No pudimos procesar el pago. Intenta de nuevo.";
    errorBox.hidden = false;
    btn.disabled = false;
  }

  function sendToken(token) {
    btn.disabled = true;
    fetch(cfg.dataset.chargeUrl, {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
      body: JSON.stringify({ token: token })
    })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, data: d }; }); })
      .then(function (res) {
        if (res.ok && res.data.ok) { window.location.assign(res.data.redirect); }
        else { showError(res.data.message); }
      })
      .catch(function () { showError(); });
  }

  if (cfg.dataset.fake === "1") {
    btn.addEventListener("click", function () { sendToken("demo"); });
    return;
  }

  // Culqi llama a la función global "culqi" cuando hay token o error.
  window.culqi = function () {
    if (window.Culqi.token) {
      var token = window.Culqi.token.id;
      window.Culqi.close();
      sendToken(token);
    } else if (window.Culqi.error) {
      showError(window.Culqi.error.user_message);
    }
  };

  btn.addEventListener("click", function () {
    if (!window.Culqi) { showError("No se pudo cargar el formulario de pago."); return; }
    window.Culqi.publicKey = cfg.dataset.publicKey;
    window.Culqi.settings({
      title: "AltoTec",
      currency: "PEN",
      amount: parseInt(cfg.dataset.amount, 10)
    });
    window.Culqi.options({ lang: "es", modal: true, paymentMethods: { tarjeta: true } });
    window.Culqi.open();
  });
})();
