/*
============================================
© 2026 Akhil Reddy
GitHub: https://github.com/akhilmatta89
LinkedIn: https://www.linkedin.com/in/akhil-reddy-1a0822255
============================================
*/

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


