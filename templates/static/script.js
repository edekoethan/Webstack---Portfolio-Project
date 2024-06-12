document.addEventListener("DOMContentLoaded", function() {
    const totalDecks = document.getElementById('total-decks');
    const totalCards = document.getElementById('total-cards');
    const recentActivity = document.getElementById('recent-activity');
    const deckList = document.getElementById('deck-list');

    // Mock data for demonstration
    const userDecks = [
        { name: 'Math', cards: 25 },
        { name: 'Science', cards: 40 },
        { name: 'History', cards: 30 }
    ];

    function populateDashboard() {
        totalDecks.textContent = userDecks.length;
        totalCards.textContent = userDecks.reduce((total, deck) => total + deck.cards, 0);
        recentActivity.textContent = `Studied ${userDecks[0].name} deck`;

        userDecks.forEach(deck => {
            const li = document.createElement('li');
            li.textContent = `${deck.name} - ${deck.cards} cards`;
            deckList.appendChild(li);
        });
    }

    populateDashboard();
});
