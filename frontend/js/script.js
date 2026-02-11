// frontend/script.js

// --- 1. DOM Element References ---
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const orderItemsDiv = document.getElementById('order-items');
const orderTotalDiv = document.getElementById('order-total');

// --- 2. State Management ---
let conversationHistory = [];

// --- 3. Core Functions ---

/**
 * Adds a message to the chat window.
 * @param {string} sender - 'user' or 'bot'.
 * @param {string} text - The message content.
 */
function addMessage(sender, text) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message');
    messageElement.textContent = text;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Updates the order summary panel based on the received cart state.
 * @param {object} cart - The cart object from the backend.
 */
function updateOrderSummary(cart) {
    if (!cart || !cart.items || cart.items.length === 0) {
        orderItemsDiv.innerHTML = '<p class="empty-cart-message">Tu carrito está vacío</p>';
        orderTotalDiv.innerHTML = '';
        return;
    }

    const { items, total_price } = cart;

    let tableHTML = '<table><tr><th>Item</th><th class="price-col">Precio/u</th></tr>';
    items.forEach(item => {
        tableHTML += `
            <tr>
                <td>${item.quantity} x ${item.name}</td>
                <td class="price-col">${item.price.toFixed(2)}€</td>
            </tr>
        `;
    });
    tableHTML += '</table>';

    orderItemsDiv.innerHTML = tableHTML;
    orderTotalDiv.innerHTML = `Total: ${total_price.toFixed(2)}€`;
}

/**
 * Handles the logic of sending a message.
 */
async function handleSendMessage() {
    const messageText = messageInput.value.trim();
    if (messageText === '') return;

    addMessage('user', messageText);
    // We add the user message to the history BEFORE sending.
    conversationHistory.push({ role: 'user', content: messageText });
    messageInput.value = '';

    try {
        const response = await fetch('http://127.0.0.1:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                conversation_history: conversationHistory
            } ),
        });

        if (!response.ok) { throw new Error('Server response was not ok.'); }

        const data = await response.json();
        
        const botResponseText = data.response_for_user;
        const newCart = data.cart;

        addMessage('bot', botResponseText);
        
        // The frontend is "dumb", it just renders what the backend sends.
        updateOrderSummary(newCart);
        
        // We add the full AI response to the history so it remembers its own JSON.
        conversationHistory.push({ role: 'assistant', content: JSON.stringify(data) });

    } catch (error) {
        console.error('Error al enviar mensaje:', error);
        addMessage('bot', 'Lo siento, algo salió mal. Por favor, inténtalo de nuevo.');
    }
}

// --- 4. Event Listeners ---
sendButton.addEventListener('click', handleSendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') { handleSendMessage(); }
});

// --- 5. Initial Call ---
// We need to send an empty message on load to get the welcome message.
window.onload = () => {
    // We create a dummy entry to kickstart the conversation
    conversationHistory.push({role: 'user', content: 'Inicio de la conversación'});
    fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversation_history: conversationHistory } ),
    }).then(res => res.json()).then(data => {
        addMessage('bot', data.response_for_user);
        updateOrderSummary(data.cart);
        conversationHistory.push({ role: 'assistant', content: JSON.stringify(data) });
    });
};