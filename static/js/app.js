document.addEventListener('DOMContentLoaded', function() {
  // DOM Elements
  const chatMessages = document.getElementById('chat-messages');
  const messageInput = document.getElementById('message-input');
  const sendButton = document.getElementById('send-button');
  const usernameDisplay = document.getElementById('username');
  
  // Initialize chat with a welcome message
  addMessage('bot', '👋 Welcome to the AI Health Assistant! I can help you manage your medical history and analyze your symptoms. What\'s your username?');
  
  // Event listeners
  sendButton.addEventListener('click', sendMessage);
  messageInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
          sendMessage();
      }
  });
  
  // Sidebar navigation
  document.querySelectorAll('.sidebar li').forEach(item => {
      item.addEventListener('click', function() {
          document.querySelectorAll('.sidebar li').forEach(li => li.classList.remove('active'));
          this.classList.add('active');
      });
  });
  
  // Info panel tabs
  document.querySelectorAll('.tab').forEach(tab => {
      tab.addEventListener('click', function() {
          const tabId = this.getAttribute('data-tab');
          
          // Update active tab
          document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
          this.classList.add('active');
          
          // Show corresponding tab pane
          document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
          document.getElementById(`${tabId}-pane`).classList.add('active');
      });
  });
  
  // Close info panel button (for mobile)
  document.querySelector('.close-info').addEventListener('click', function() {
      document.querySelector('.info-panel').classList.remove('open');
  });
  
  // Load chat history if available
  loadChatHistory();
  
  // Functions
  function sendMessage() {
      const message = messageInput.value.trim();
      if (message === '') return;
      
      // Add user message to the chat
      addMessage('user', message);
      
      // Clear input
      messageInput.value = '';
      
      // Send message to the backend
      fetch('/api/chat', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ message: message })
      })
      .then(response => response.json())
      .then(data => {
          // Add bot response to the chat
          addMessage('bot', data.message);
          
          // Update username if set
          if (message && !usernameDisplay.innerText !== 'Guest') {
              usernameDisplay.innerText = message;
          }
      })
      .catch(error => {
          console.error('Error:', error);
          addMessage('bot', 'Sorry, there was an error processing your request.');
      });
  }
  
  function addMessage(role, content) {
      const messageElement = document.createElement('div');
      messageElement.classList.add('message');
      messageElement.classList.add(role === 'user' ? 'user-message' : 'bot-message');
      
      // Preserve line breaks in bot messages
      if (role === 'bot') {
          content = content.replace(/\n/g, '<br>');
      }
      
      messageElement.innerHTML = `
          <div class="message-content">${content}</div>
          <div class="message-time">${formatTime(new Date())}</div>
      `;
      
      chatMessages.appendChild(messageElement);
      
      // Scroll to the bottom
      chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
  function formatTime(date) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  
  function loadChatHistory() {
      fetch('/api/history')
      .then(response => response.json())
      .then(data => {
          if (data.history && data.history.length > 0) {
              // Clear default welcome message
              chatMessages.innerHTML = '';
              
              // Add all messages from history
              data.history.forEach(item => {
                  addMessage(item.role, item.message);
              });
          }
      })
      .catch(error => {
          console.error('Error loading chat history:', error);
      });
  }
  
  // Responsive menu toggles for mobile
  document.querySelector('.user-menu').addEventListener('click', function() {
      const infoPanel = document.querySelector('.info-panel');
      infoPanel.classList.toggle('open');
  });
  
  // Add hamburger menu for mobile if needed
  // This would need a hamburger icon to be added to the HTML
});