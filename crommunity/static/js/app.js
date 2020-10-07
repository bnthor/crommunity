// Helpers
const getCookie = (name) => {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

// Alerts handling
const alerts = document.querySelectorAll('.alert');

alerts.forEach(alert => {
    // Show the alert after page load
    alert.classList.add('is-visible');

    // Close the alert when clicked
    alert.addEventListener('click', function() {
        alert.classList.remove('is-visible');
    })

    // Also close it after 8 seconds
    setTimeout(function(){
        alert.classList.remove('is-visible');
    }, 8000)
});

// Privacy consent
const consent = document.querySelector('.consent');
const consentButton = consent.querySelector('.consent__accept');
const consentToPrivacyPolicy = async () => {
    const settings = {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        }
    };
    try {
        await fetch('/privacy-consent', settings);
        consent.classList.remove('is-visible');
    } catch (e) {
        return e;
    };
}

if (!getCookie('privacy_consent')) {
    consent.classList.add('is-visible');
}

consentButton.addEventListener('click', function(e) {
    e.preventDefault();
    consentToPrivacyPolicy();
});

// Mobile menu toggling
const menuToggle = document.querySelector('.header__menuToggle');
const menu = document.querySelector('.header__nav');

menuToggle.addEventListener('click', function(e) {
    menuToggle.classList.toggle('is-active');
    menu.classList.toggle('is-active');
});

// HLJS
document.querySelectorAll('pre code').forEach((block) => {
    hljs.highlightBlock(block);
    console.log(block);
});

// Nicer File upload inputs
const fileUpload = document.querySelector('.fileUpload');
let fileUploadInput,
    fileUploadLabel,
    fileUploadReset,
    fileUploadPlaceholder;

// Update manually on document load
if (fileUpload) {
    fileUploadInput = fileUpload.querySelector('.fileUpload input');
    fileUploadLabel = fileUpload.querySelector('.fileUpload__label');
    fileUploadReset = fileUpload.querySelector('.fileUpload__reset');
    fileUploadPlaceholder = fileUploadLabel.dataset.placeholder;

    if (!fileUploadLabel.innerHTML) {
        fileUpload.classList.remove('has-value');
        fileUploadLabel.innerHTML = fileUploadPlaceholder;
    } else {
        fileUpload.classList.add('has-value');
    }
}

const updateFileUploadInput = () => {
    let filename = fileUploadInput.value.replace("C:\\fakepath\\", '');
    if (filename) {
        fileUpload.classList.add('has-value');
        fileUploadLabel.innerHTML = filename;
    } else {
        fileUpload.classList.remove('has-value');
        fileUploadLabel.innerHTML = fileUploadPlaceholder;
    }
}

if (fileUploadInput) {
    fileUploadInput.addEventListener('change', updateFileUploadInput);

    fileUploadReset.addEventListener('click', (e) => {
        fileUploadInput.value = '';
        updateFileUploadInput();
    });
}