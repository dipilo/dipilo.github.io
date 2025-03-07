document.getElementById('contactForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent the default form submission
  
    const form = event.target;
    const formData = new FormData(form);
  
    try {
      const response = await fetch(form.action, {
        method: form.method,
        body: formData,
        headers: {
          'Accept': 'application/json'
        }
      });
  
      if (response.ok) {
        document.getElementById('confirmationMessage').style.display = 'block';
        form.reset(); // Clear the form fields
      } else {
        showAlert('Uh Oh.');
      }
    } catch (error) {
      showAlert('It no submit.');
    }
});

function showAlert(message) {
  const alertBox = document.getElementById('alertBox');
  const alertMessage = document.getElementById('alertMessage');
  alertMessage.textContent = message;
  alertBox.style.display = 'block';
}

document.getElementById('closeAlert').addEventListener('click', function() {
  document.getElementById('alertBox').style.display = 'none';
});