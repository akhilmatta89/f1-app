



// Toggles the dropdown menu with click

const dropBtn = document.getElementById('dropBtn');
if (dropBtn) { // Check if the element actually exists
const dropdownContent = document.querySelector('.dropdown-content');

dropBtn.addEventListener('click', function() {
    console.log('clicked');
    if (dropdownContent.style.display === "none") {
        dropdownContent.style.display = "block";
    } else {
        dropdownContent.style.display = "none";
    }
    console.log(dropdownContent);
});
}


