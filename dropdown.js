function toggleDropdown(id) {
  var content = document.getElementById(id);
  // Find the corresponding toggle button by navigating to the parent and querying for the button
  var button = content.parentElement.querySelector('.dropdown-toggle');
  if (content.style.display === "block") {
    content.style.display = "none";
    button.classList.remove("rotated");
  } else {
    content.style.display = "block";
    button.classList.add("rotated");
  }
}
