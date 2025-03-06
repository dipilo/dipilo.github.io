<?php
if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $firstName = $_POST['firstName'] ?? '';
    $lastName  = $_POST['lastName']  ?? '';
    $email     = $_POST['email']     ?? '';
    $message   = $_POST['message']   ?? '';

    // Validate and sanitize data here as needed...
    
    // Create email content
    $to = "fujsikle@gmail.com";
    $subject = "New Contact Form Submission";
    $body = "Name: $firstName $lastName\nEmail: $email\n\nMessage:\n$message";
    $headers = "From: $email\r\nReply-To: $email\r\n";

    // Send the email
    if (mail($to, $subject, $body, $headers)) {
        echo "Thank you for your message. We will get back to you soon.";
    } else {
        echo "Oops! Something went wrong, please try again.";
    }
} else {
    echo "Invalid request method.";
}
?>
