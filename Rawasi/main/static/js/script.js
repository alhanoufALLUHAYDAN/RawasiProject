document.addEventListener('DOMContentLoaded', function() {
    flatpickr("#date_of_birth", {
      dateFormat: "Y-m-d", 
      locale: "ar",     
      maxDate: "today",  
    });
});
