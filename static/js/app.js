if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker
      .register("static/js/serviceWorker.js")
      .then((res) => console.log("service worker registered"))
      .catch((err) => console.log("service worker not registered", err));
  });
}

function removeLike(id) {
  document.getElementById("formId").setAttribute("value", id);
  document.getElementById("formAction").setAttribute("value", "removeLike");
  document.getElementById("musicActionForm").submit();
}

function addLike(id) {
  document.getElementById("formId").setAttribute("value", id);
  document.getElementById("formAction").setAttribute("value", "addLike");
  document.getElementById("musicActionForm").submit();
}

function removeList(id) {
  document.getElementById("formId").setAttribute("value", id);
  document.getElementById("formAction").setAttribute("value", "removeList");
  document.getElementById("musicActionForm").submit();
}

function addList(id) {
  document.getElementById("formId").setAttribute("value", id);
  document.getElementById("formAction").setAttribute("value", "addList");
  document.getElementById("musicActionForm").submit();
}
