document.getElementById('contactForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent the default form submission
  
    const form = event.target;
    const formData = new FormData(form);
    const data = {
      firstName: formData.get('firstName'),
      lastName: formData.get('lastName'),
      email: formData.get('email'),
      message: formData.get('message')
    };
  
    try {
      const response = await fetch('/send-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
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