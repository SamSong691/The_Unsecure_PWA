if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker
      .register("static/js/serviceWorker.js")
      .then((res) => console.log("service worker registered"))
      .catch((err) => console.log("service worker not registered", err));
  });
}

function removeLike(title) {
  document.getElementById("formTitle").setAttribute("value", title);
  document.getElementById("formAction").setAttribute("value", "removeLike");
  document.getElementById("musicActionForm").submit();
}

function addLike(title) {
  document.getElementById("formTitle").setAttribute("value", title);
  document.getElementById("formAction").setAttribute("value", "addLike");
  document.getElementById("musicActionForm").submit();
}

function removeList(title) {
  document.getElementById("formTitle").setAttribute("value", title);
  document.getElementById("formAction").setAttribute("value", "removeList");
  document.getElementById("musicActionForm").submit();
}

function addList(title) {
  document.getElementById("formTitle").setAttribute("value", title);
  document.getElementById("formAction").setAttribute("value", "addList");
  document.getElementById("musicActionForm").submit();
}
