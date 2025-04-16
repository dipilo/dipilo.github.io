// This basic script simulates sending a message and receiving a bot reply.

const messageContainer = document.getElementById('message-container');
const inputField = document.getElementById('user-message');
const sendButton = document.getElementById('send-message');

// Function to append a message
function addMessage(username, content) {
  const msgDiv = document.createElement('div');
  msgDiv.classList.add('message');
  
  const nameSpan = document.createElement('span');
  nameSpan.classList.add('username');
  nameSpan.textContent = username + ':';
  
  const contentSpan = document.createElement('span');
  contentSpan.classList.add('content');
  contentSpan.textContent = ' ' + content;
  
  msgDiv.append(nameSpan, contentSpan);
  messageContainer.appendChild(msgDiv);
  
  // Auto-scroll to bottom
  messageContainer.scrollTop = messageContainer.scrollHeight;
}

// Simulated bot reply
function botReply(userMsg) {
  // You can integrate your bot logic here.
  // For now, just a simple echo with added text.
  return "Bot says: " + userMsg.split('').reverse().join('');
}

// Event listener for sending a message
sendButton.addEventListener('click', () => {
  const userMsg = inputField.value.trim();
  if (userMsg) {
    addMessage('You', userMsg);
    inputField.value = '';
    
    // Simulate bot reply after 1 second
    setTimeout(() => {
      const reply = botReply(userMsg);
      addMessage('Bot', reply);
    }, 1000);
  }
});

// Also allow sending the message by hitting Enter
inputField.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    sendButton.click();
  }
});
