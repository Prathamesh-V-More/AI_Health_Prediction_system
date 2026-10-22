// ── Password show/hide toggle ──────────────────────────────
function togglePassword(fieldId) {
  var input = document.getElementById(fieldId);
  var icon  = document.getElementById("eye-" + fieldId);
  if (!input) return;
  if (input.type === "password") {
    input.type = "text";
    if (icon) { icon.classList.remove("fa-eye"); icon.classList.add("fa-eye-slash"); }
  } else {
    input.type = "password";
    if (icon) { icon.classList.remove("fa-eye-slash"); icon.classList.add("fa-eye"); }
  }
}

// ── Auto-dismiss flash messages after 5 seconds ───────────
document.addEventListener("DOMContentLoaded", function () {

  // Auto-dismiss alerts
  var alerts = document.querySelectorAll(".alert");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = "opacity 0.5s";
      alert.style.opacity = "0";
      setTimeout(function () { alert.remove(); }, 500);
    }, 5000);
  });

  // Animate confidence bars (dashboard result)
  var fills = document.querySelectorAll(".confidence-fill[style*='width']");
  fills.forEach(function (el) {
    var target = el.style.width;
    el.style.width = "0%";
    setTimeout(function () { el.style.width = target; }, 100);
  });

  // Apply mini-bar widths from data-width attributes (history page)
  document.querySelectorAll(".mini-fill[data-width]").forEach(function (el) {
    var w = parseFloat(el.getAttribute("data-width"));
    el.style.width = (isNaN(w) ? 0 : w) + "%";
  });

  // Type card highlight on load
  var checkedRadio = document.querySelector(".type-option input:checked");
  if (checkedRadio) {
    var card = checkedRadio.closest(".type-option");
    if (card) card.querySelector(".type-card").classList.add("selected");
  }

  // Type card highlight on change
  document.querySelectorAll(".type-option input").forEach(function (radio) {
    radio.addEventListener("change", function () {
      document.querySelectorAll(".type-card").forEach(function (c) {
        c.classList.remove("selected");
      });
      var opt = radio.closest(".type-option");
      if (opt) opt.querySelector(".type-card").classList.add("selected");
    });
  });

  // Drag & drop upload zone
  var dropZone  = document.getElementById("drop-zone");
  var fileInput = document.getElementById("image");
  var content   = document.getElementById("drop-content");
  var preview   = document.getElementById("drop-preview");
  var previewImg= document.getElementById("preview-img");
  var previewNm = document.getElementById("preview-name");

  if (dropZone && fileInput) {
    dropZone.addEventListener("dragover", function (e) {
      e.preventDefault();
      dropZone.classList.add("drag-over");
    });
    dropZone.addEventListener("dragleave", function () {
      dropZone.classList.remove("drag-over");
    });
    dropZone.addEventListener("drop", function (e) {
      e.preventDefault();
      dropZone.classList.remove("drag-over");
      var file = e.dataTransfer.files[0];
      if (file) {
        fileInput.files = e.dataTransfer.files;
        showPreview(file);
      }
    });

    fileInput.addEventListener("change", function () {
      if (fileInput.files[0]) showPreview(fileInput.files[0]);
    });
  }

  function showPreview(file) {
    var reader = new FileReader();
    reader.onload = function (e) {
      if (previewImg) previewImg.src = e.target.result;
      if (previewNm)  previewNm.textContent = file.name;
      if (content)    content.style.display = "none";
      if (preview)    preview.style.display = "flex";
    };
    reader.readAsDataURL(file);
  }

  // Predict form loading state
  var predictForm = document.getElementById("predict-form");
  if (predictForm) {
    predictForm.addEventListener("submit", function () {
      var btn = document.getElementById("predict-btn");
      if (btn) {
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        btn.disabled = true;
      }
    });
  }

  // Scroll to result card if present
  var resultCard = document.querySelector(".result-card");
  if (resultCard) {
    setTimeout(function () {
      resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 300);
  }

});

// ── Clear file preview ─────────────────────────────────────
function clearPreview() {
  var fileInput = document.getElementById("image");
  var content   = document.getElementById("drop-content");
  var preview   = document.getElementById("drop-preview");
  var previewImg= document.getElementById("preview-img");
  if (fileInput)  fileInput.value = "";
  if (previewImg) previewImg.src  = "";
  if (content)    content.style.display = "flex";
  if (preview)    preview.style.display = "none";
}
