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
        alert('There was a problem with your submission. Please try again.');
      }
    } catch (error) {
      alert('There was a problem with your submission. Please try again.');
    }
  });