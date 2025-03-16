document.addEventListener("DOMContentLoaded", () => {
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector(".mobile-menu-btn")
    const navLinks = document.querySelector(".nav-links")
  
    mobileMenuBtn.addEventListener("click", () => {
      navLinks.style.display = navLinks.style.display === "flex" ? "none" : "flex"
    })
  
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", function (e) {
        e.preventDefault()
  
        const targetId = this.getAttribute("href")
        if (targetId === "#") return
  
        const targetElement = document.querySelector(targetId)
        if (targetElement) {
          window.scrollTo({
            top: targetElement.offsetTop - 80,
            behavior: "smooth",
          })
        }
      })
    })
  
    // FastAPI integration with the chatbot
    const heroChatMessages = document.getElementById("hero-chat-messages")
    const heroUserInput = document.getElementById("hero-user-input")
    const heroSendButton = document.getElementById("hero-send-button")
  
    // Store conversation ID for continued conversation
    let conversationId = null
  
    // API endpoint (replace with your actual FastAPI endpoint)
    const API_URL = "https://taz-ai.onrender.com/travel/chat"
  
    // Function to create and show typing indicator
    function showTypingIndicator() {
      const typingIndicator = document.createElement("div")
      typingIndicator.classList.add("typing-indicator")
      typingIndicator.id = "typing-indicator"
  
      for (let i = 0; i < 3; i++) {
        const dot = document.createElement("div")
        dot.classList.add("typing-dot")
        typingIndicator.appendChild(dot)
      }
  
      heroChatMessages.appendChild(typingIndicator)
      heroChatMessages.scrollTop = heroChatMessages.scrollHeight
  
      return typingIndicator
    }
  
    // Function to remove typing indicator
    function removeTypingIndicator() {
      const indicator = document.getElementById("typing-indicator")
      if (indicator) {
        indicator.remove()
      }
    }
  
    // Function to add a message to the chat
    function addHeroMessage(text, isUser) {
      // If it's a user message, add it all at once
      if (isUser) {
        const messageDiv = document.createElement("div")
        messageDiv.classList.add("message")
        messageDiv.classList.add("user-message")
        messageDiv.textContent = text
        heroChatMessages.appendChild(messageDiv)
  
        // Scroll to the bottom of the chat
        heroChatMessages.scrollTop = heroChatMessages.scrollHeight
        return
      }
  
      // For bot messages, check if it contains bullet points or numbered lists
      const lines = text.split("\n")
      const messageContainer = document.createElement("div")
      messageContainer.classList.add("bot-message-container")
      heroChatMessages.appendChild(messageContainer)
  
      // Function to add a single line with delay
      function addLineWithDelay(index) {
        if (index >= lines.length) return
  
        const line = lines[index].trim()
        if (line === "") {
          // Skip empty lines but continue to the next one
          setTimeout(() => addLineWithDelay(index + 1), 100)
          return
        }
  
        const messageDiv = document.createElement("div")
        messageDiv.classList.add("message")
        messageDiv.classList.add("bot-message")
  
        // Check if this is a new section (day header, etc.)
        if (line.startsWith("Day") || line.startsWith("Budget") || line.includes(":")) {
          messageDiv.style.fontWeight = "bold"
        }
  
        messageDiv.textContent = line
        messageContainer.appendChild(messageDiv)
  
        // Scroll to the bottom of the chat
        heroChatMessages.scrollTop = heroChatMessages.scrollHeight
  
        // Add the next line with a delay
        const delay = line.length > 50 ? 500 : 300 // Longer delay for longer lines
        setTimeout(() => addLineWithDelay(index + 1), delay)
      }
  
      // Start adding lines with delay
      addLineWithDelay(0)
    }
  
    // Function to handle user input and API call
    async function handleHeroUserInput() {
      const text = heroUserInput.value.trim()
      if (text === "") return
  
      // Add user message
      addHeroMessage(text, true)
      heroUserInput.value = ""
  
      // Show typing indicator
      showTypingIndicator()
  
      try {
        // Call FastAPI endpoint
        const response = await fetch(API_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: text,
            conversation_id: conversationId,
          }),
        })
  
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`)
        }
  
        const data = await response.json()
  
        // Store conversation ID for continued conversation
        conversationId = data.conversation_id
  
        // Remove typing indicator
        removeTypingIndicator()
  
        // Add bot response line by line
        addHeroMessage(data.response, false)
      } catch (error) {
        console.error("Error:", error)
  
        // Remove typing indicator
        removeTypingIndicator()
  
        // Add error message
        addHeroMessage("I'm sorry, I'm having trouble connecting to the server. Please try again later.", false)
      }
    }
  
    // Event listeners
    heroSendButton.addEventListener("click", handleHeroUserInput)
    heroUserInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        handleHeroUserInput()
      }
    })
  
    // Fallback responses in case the API is not available
    const fallbackResponses = [
      "I'd be happy to tell you more about our services!",
      "Our team specializes in creating beautiful, functional websites and applications.",
      "We use the latest technologies to ensure your project is fast, secure, and scalable.",
      "Would you like to see some examples of our previous work?",
      "Our design process starts with understanding your business goals and target audience.",
      "We offer ongoing support and maintenance for all our projects.",
      "Feel free to ask any questions about our design or development process!",
      "We've worked with clients across various industries including tech, healthcare, and education.",
      "What specific features are you looking for in your project?",
    ]
  
    // Function to handle API connection errors
    function handleApiError() {
      // Get random fallback response
      const randomIndex = Math.floor(Math.random() * fallbackResponses.length)
      const fallbackResponse = fallbackResponses[randomIndex]
  
      // Add fallback response
      addHeroMessage(fallbackResponse, false)
    }
  })  