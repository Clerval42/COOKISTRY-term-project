document.addEventListener('DOMContentLoaded', function() {

    // ----- Sticky Header Padding -----
    const header = document.querySelector('.sticky-header');
    const mainContent = document.querySelector('main');
    
    function adjustMainPadding() {
        if (header && mainContent) {
            const headerHeight = header.offsetHeight;
            mainContent.style.paddingTop = headerHeight + 'px';
        }
    }
    adjustMainPadding(); // İlk yüklemede ayarla
    window.addEventListener('resize', adjustMainPadding); // Pencere boyutu değiştiğinde ayarla

    // ----- Filter Popup -----
    const filterBtn = document.querySelector('.filter-icon-btn'); // Header'daki filtre ikonu
    const filterPopup = document.querySelector('.filter-popup');   // Header'daki filtre popup'ı
    const applyHeaderFilterBtn = document.getElementById('applyHeaderFilterBtn'); // Header'daki popup'ın "Uygula" butonu

    if (filterBtn && filterPopup) {
        filterBtn.addEventListener('click', function(event) {
            event.stopPropagation(); 
            filterPopup.classList.toggle('active');
        });

        // Popup dışına tıklayınca kapat
        document.addEventListener('click', function(event) {
            // Sadece header'daki filterPopup için kontrol
            if (filterPopup.classList.contains('active') && 
                !filterPopup.contains(event.target) && 
                event.target !== filterBtn && 
                !filterBtn.contains(event.target)) {
                filterPopup.classList.remove('active');
            }
        });
    }

    if (applyHeaderFilterBtn) {
        applyHeaderFilterBtn.addEventListener('click', function() {
            console.log("Header filtresi uygulanıyor...");
            // Gerçek filtreleme mantığı burada backend'e istek göndererek veya
            // sayfadaki elementleri manipüle ederek yapılabilir.
            // Şimdilik sadece popup'ı kapatıyoruz.
            if (filterPopup) {
                filterPopup.classList.remove('active'); 
            }
        });
    }

    // ----- Recipe Carousel -----
    const carousels = document.querySelectorAll('.recipe-carousel');
    carousels.forEach(carousel => {
        const container = carousel.querySelector('.recipe-cards-container');
        const prevBtn = carousel.querySelector('.prev-arrow');
        const nextBtn = carousel.querySelector('.next-arrow');
        
        if (!container || !prevBtn || !nextBtn ) return;
        
        // Carousel'deki kartları seçmek için daha esnek bir yol veya HTML'de ortak sınıf kullanımı
        // Örn: '.recipe-card, .featured-user-card, .ingredient-details-card'
        // Şimdilik sadece '.recipe-card' varsayımıyla devam ediyor.
        // Eğer trends.html'deki .featured-user-card'lara da .recipe-card sınıfını eklerseniz bu kod çalışır.
        const cards = Array.from(container.children).filter(child => child.classList.contains('recipe-card') || child.classList.contains('featured-user-card') || child.classList.contains('ingredient-details-card'));
        
        if (cards.length === 0) return;

        function updateCarouselState() {
            if (cards.length === 0 || !container) return; // Ekstra güvenlik kontrolü
            prevBtn.disabled = container.scrollLeft <= 1; // Hafif bir tolerans
            // Tam sona ulaşıldığında next butonunu devre dışı bırakmak için scrollWidth, clientWidth ve scrollLeft kullanılır
            nextBtn.disabled = Math.ceil(container.scrollLeft) + container.clientWidth >= container.scrollWidth -1;
        }
        
        function getScrollAmount() {
            if (cards.length === 0 || !container) return 0; // Ekstra güvenlik kontrolü
            
            // İlk kartın genişliğini ve gap'i alarak kaydırma miktarını hesapla
            const firstCard = cards[0];
            const cardStyle = window.getComputedStyle(firstCard);
            const cardMarginLeft = parseFloat(cardStyle.marginLeft) || 0;
            const cardMarginRight = parseFloat(cardStyle.marginRight) || 0;
            
            const containerStyle = window.getComputedStyle(container);
            const gap = parseFloat(containerStyle.gap) || 20; // Varsayılan gap 20px

            const cardWidthWithMarginsAndGap = firstCard.offsetWidth + cardMarginLeft + cardMarginRight + gap;
            
            const visibleWidth = container.clientWidth;
            // Görünür alana sığan kart sayısına yakın bir miktar kaydır
            // Eğer tek kart kaydırmak istenirse doğrudan cardWidthWithMarginsAndGap kullanılabilir
            let cardsToScroll = Math.floor(visibleWidth / cardWidthWithMarginsAndGap);
            if (cardsToScroll < 1) cardsToScroll = 1; // En az 1 kart kaydır

            return cardWidthWithMarginsAndGap * cardsToScroll;
        }

        prevBtn.addEventListener('click', () => {
            if(container) container.scrollLeft -= getScrollAmount();
        });

        nextBtn.addEventListener('click', () => {
            if(container) container.scrollLeft += getScrollAmount();
        });

        if(container) container.addEventListener('scroll', updateCarouselState);
        window.addEventListener('resize', () => { // Resize'da durumu ve kaydırma miktarını yeniden hesapla
             updateCarouselState();
        }); 
        updateCarouselState(); 
    });


    // ----- Login/Signup Page Tab Functionality -----
    const showLoginBtn = document.getElementById('showLoginBtn');
    const showSignupBtn = document.getElementById('showSignupBtn');
    const loginFormEl = document.getElementById('loginForm'); 
    const signupFormEl = document.getElementById('signupForm'); 

    if (showLoginBtn && showSignupBtn && loginFormEl && signupFormEl) {
        showLoginBtn.addEventListener('click', () => {
            loginFormEl.style.display = 'block';
            signupFormEl.style.display = 'none';
            showLoginBtn.classList.add('active');
            showSignupBtn.classList.remove('active');
        });

        showSignupBtn.addEventListener('click', () => {
            loginFormEl.style.display = 'none';
            signupFormEl.style.display = 'block';
            showSignupBtn.classList.add('active');
            showLoginBtn.classList.remove('active');
        });

        loginFormEl.addEventListener('submit', function(event) {
            // Remove static demo: allow normal form submit to backend
        });

        signupFormEl.addEventListener('submit', function(event) {
            const passwordInput = document.getElementById('signupPassword');
            const confirmPasswordInput = document.getElementById('signupConfirmPassword');
            if (!passwordInput || !confirmPasswordInput) return;
            const password = passwordInput.value;
            const confirmPassword = confirmPasswordInput.value;
            if (password !== confirmPassword) {
                event.preventDefault();
                alert('Şifreler eşleşmiyor!');
                return;
            }
            // Remove static demo: allow normal form submit to backend
        });
    }

    // ----- Live Search -----
    const searchInput = document.getElementById('mainSearchInput');
    const searchResults = document.getElementById('mainSearchResults');
    let allSuggestions = null;

    function highlightTerm(text, term) {
        if (!term) return text;
        const re = new RegExp('(' + term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig');
        return text.replace(re, '<mark>$1</mark>');
    }

    function getTypeIcon(type) {
        if (type === 'Recipe') return '<i class="fas fa-utensils"></i>';
        if (type === 'Meal Plan') return '<i class="fas fa-calendar-alt"></i>';
        if (type === 'User') return '<i class="fas fa-user"></i>';
        return '';
    }

    if (searchInput && searchResults) {
        searchInput.addEventListener('input', async function() {
            const query = searchInput.value.trim().toLowerCase();
            if (!allSuggestions) {
                // Fetch all suggestions once
                const resp = await fetch('/search_suggestions');
                allSuggestions = await resp.json();
            }
            if (!query) {
                searchResults.style.display = 'none';
                searchResults.innerHTML = '';
                return;
            }
            let results = [];
            // Recipes
            results = results.concat(
                allSuggestions.recipes.filter(r => r.name && r.name.toLowerCase().includes(query)).map(r => ({
                    type: 'Recipe',
                    name: r.name,
                    // Correct URL: /recipe/slug-1234
                    url: `/recipe/${r.name.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-').replace(/-+/g, '-')}-${r.id}`
                }))
            );
            // Meal Plans
            results = results.concat(
                allSuggestions.mealplans.filter(m => m.name && m.name.toLowerCase().includes(query)).map(m => ({
                    type: 'Meal Plan',
                    name: m.name,
                    url: `/meals/meal-plan/${m.id}`
                }))
            );
            // Users
            results = results.concat(
                allSuggestions.users.filter(u => u.name && u.name.toLowerCase().includes(query)).map(u => ({
                    type: 'User',
                    name: u.name,
                    url: `/user-profile/${u.id}`
                }))
            );
            if (results.length === 0) {
                searchResults.innerHTML = '<div class="search-no-result">No results found.</div>';
            } else {
                // Group by type
                let grouped = { 'Recipe': [], 'Meal Plan': [], 'User': [] };
                results.forEach(r => grouped[r.type].push(r));
                let html = '';
                for (const type of ['Recipe', 'Meal Plan', 'User']) {
                    if (grouped[type].length > 0) {
                        html += `<div class="search-group-title">${getTypeIcon(type)} ${type}s</div>`;
                        grouped[type].forEach(r => {
                            html += `<div class="search-result-item"><a href="${r.url}">${getTypeIcon(type)} ${highlightTerm(r.name, query)}</a></div>`;
                        });
                    }
                }
                searchResults.innerHTML = html;
            }
            searchResults.style.display = 'block';
        });
        let isResultClick = false;
        if (searchResults) {
            searchResults.addEventListener('mousedown', function(e) {
                const link = e.target.closest('a');
                if (link) {
                    isResultClick = true;
                    window.location = link.href;
                    e.preventDefault();
                }
            });
        }
        searchInput.addEventListener('blur', function() {
            setTimeout(() => {
                if (!isResultClick) {
                    searchResults.style.display = 'none';
                }
                isResultClick = false;
            }, 200);
        });
        searchInput.addEventListener('focus', function() {
            if (searchInput.value.trim()) searchResults.style.display = 'block';
        });
    }
});