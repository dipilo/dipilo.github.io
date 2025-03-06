<?php
if ($_SERVER["REQUEST_METHOD"] === "POST") {
    // Retrieve form values
    $firstName = trim($_POST['firstName'] ?? '');
    $lastName  = trim($_POST['lastName'] ?? '');
    $email     = trim($_POST['email'] ?? '');
    $message   = trim($_POST['message'] ?? '');

    // Validate that required fields are not empty
    if (empty($firstName) || empty($lastName) || empty($email) || empty($message)) {
        echo "Please fill in all required fields.";
        exit;
    }

    // Sanitize inputs (basic example)
    $firstName = htmlspecialchars($firstName);
    $lastName  = htmlspecialchars($lastName);
    $email     = filter_var($email, FILTER_SANITIZE_EMAIL);
    $message   = htmlspecialchars($message);

    // Compose the email
    $to = "fujsikle@gmail.com";
    $subject = "New Contact Form Submission";
    $body = "Name: $firstName $lastName\nEmail: $email\n\nMessage:\n$message";
    $headers = "From: $email\r\nReply-To: $email\r\n";

    // Attempt to send the email
    if (mail($to, $subject, $body, $headers)) {
        echo "Thank you for your message. We will get back to you soon.";
    } else {
        echo "Sorry, something went wrong. Please try again later.";
    }
} else {
    echo "Invalid request method.";
}
?>
