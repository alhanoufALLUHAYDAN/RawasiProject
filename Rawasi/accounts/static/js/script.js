const passwordInput = document.getElementById('password');
const lengthRequirement = document.getElementById('length');
const uppercaseRequirement = document.getElementById('uppercase');
const numberRequirement = document.getElementById('number');
const specialRequirement = document.getElementById('special');

passwordInput.addEventListener('input', function() {
    const password = passwordInput.value;

    if (password.length >= 8) {
        lengthRequirement.classList.remove('invalid');
        lengthRequirement.classList.add('valid');
    } else {
        lengthRequirement.classList.remove('valid');
        lengthRequirement.classList.add('invalid');
    }

    if (/[A-Z]/.test(password)) {
        uppercaseRequirement.classList.remove('invalid');
        uppercaseRequirement.classList.add('valid');
    } else {
        uppercaseRequirement.classList.remove('valid');
        uppercaseRequirement.classList.add('invalid');
    }

    if (/\d/.test(password)) {
        numberRequirement.classList.remove('invalid');
        numberRequirement.classList.add('valid');
    } else {
        numberRequirement.classList.remove('valid');
        numberRequirement.classList.add('invalid');
    }

    if (/[!@#$%^&*]/.test(password)) {
        specialRequirement.classList.remove('invalid');
        specialRequirement.classList.add('valid');
    } else {
        specialRequirement.classList.remove('valid');
        specialRequirement.classList.add('invalid');
    }
});

document.addEventListener('DOMContentLoaded', function() {
    flatpickr("#date_of_birth", {
      dateFormat: "Y-m-d", 
      locale: "ar",     
      maxDate: "today",  
    });
});
function togglePasswordVisibility(buttonId, inputId) {
    const passwordField = document.getElementById(inputId);
    
    const type = passwordField.type === 'password' ? 'text' : 'password';
    passwordField.type = type;
    
    const icon = document.querySelector(`#${buttonId} i`);
    icon.classList.toggle('bi-eye');
    icon.classList.toggle('bi-eye-slash');
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('togglePassword1').addEventListener('click', function() {
        togglePasswordVisibility('togglePassword1', 'password');
    });

    document.getElementById('togglePassword2').addEventListener('click', function() {
        togglePasswordVisibility('togglePassword2', 'confirm_password');
    });
});

