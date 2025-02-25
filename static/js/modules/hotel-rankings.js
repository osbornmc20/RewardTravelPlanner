class HotelRankingsModule {
    constructor() {
        this.usaGrid = document.querySelector('.usa-hotels-grid');
        this.mexicoGrid = document.querySelector('.mexico-hotels-grid');
        this.worldGrid = document.querySelector('.world-hotels-grid');
        this.hotels = [];
        this.init();
    }

    init() {
        this.loadHotels();
        this.initializeCollapsibleSections();
    }

    initializeCollapsibleSections() {
        const sectionHeaders = document.querySelectorAll('.section-header');
        sectionHeaders.forEach(header => {
            header.addEventListener('click', () => {
                // Only handle collapse on mobile
                if (window.innerWidth <= 576) {
                    const targetId = header.getAttribute('data-target');
                    const content = document.querySelector(targetId);
                    const isExpanded = header.getAttribute('aria-expanded') === 'true';

                    // Toggle aria-expanded
                    header.setAttribute('aria-expanded', !isExpanded);

                    // Toggle content visibility
                    if (isExpanded) {
                        content.classList.remove('show');
                    } else {
                        content.classList.add('show');
                    }
                }
            });
        });
    }

    loadHotels() {
        fetch('/api/hotel-rankings')
            .then(response => response.json())
            .then(data => {
                this.hotels = data;
                this.renderHotels();
            })
            .catch(error => console.error('Error loading hotels:', error));
    }

    renderHotels(hotels = this.hotels) {
        const usaHotels = hotels.filter(h => h.country === 'USA')
            .sort((a, b) => b.rating - a.rating)
            .slice(0, 10);
        const mexicoHotels = hotels.filter(h => h.country === 'Mexico')
            .sort((a, b) => b.rating - a.rating)
            .slice(0, 10);
        const worldHotels = hotels.filter(h => !['USA', 'Mexico'].includes(h.country))
            .sort((a, b) => b.rating - a.rating)
            .slice(0, 10);

        this.usaGrid.innerHTML = usaHotels.map(hotel => this.createHotelCard(hotel)).join('');
        this.mexicoGrid.innerHTML = mexicoHotels.map(hotel => this.createHotelCard(hotel)).join('');
        this.worldGrid.innerHTML = worldHotels.map(hotel => this.createHotelCard(hotel)).join('');
    }

    getHotelWebsite(hotel) {
        // Map of hotel names to their official websites
        const websiteMap = {
            'Makanyi Lodge': 'https://makanyilodge.com',
            'La Ventana Big Sur': 'https://www.ventanabigsur.com',
            'El Silenco': 'https://www.elsilenciolodge.com',
            'Casa Chamelon': 'https://casachameleon.com/las-catalinas',
            'Raffles Europejeski': 'https://www.raffles.com/warsaw/',
            'Cougar Ridge': 'https://cougarridge.com/',
            'Rosewood Mirimar Beach': 'https://www.rosewoodhotels.com/en/miramar-beach-montecito',
            'Tengile River Lodge': 'https://www.andbeyond.com/our-lodges/africa/south-africa/sabi-sand-game-reserve/andbeyond-tengile-river-lodge',
            'Fontsanta Hotel & Thermal Spa': 'https://www.fontsantahotel.com/index.php?lang=en',
            'Art Hotel Riposo': 'https://www.hotelriposo.ch/en/',
            'Ojai Valley Inn': 'https://www.ojaivalleyinn.com',
            'Lo Soreno De La Playa': 'https://www.losereno.com/',
            'Casa Cacao': 'https://casacacaogirona.com/en',
            'Hotel Moessy': 'https://moeesy.com/',
            'Cuixmala': 'https://www.cuixmala.com',
            'Four Seasons Chicago': 'https://www.fourseasons.com/chicago',
            'Art Hotel Villa Fiorella': 'https://arthotelvillafiorella.com/?lang=en',
            'St Regis Mexico City': 'https://www.marriott.com/en-us/hotels/mexxr-the-st-regis-mexico-city/overview/',
            'Kenwood Inn & Spa': 'https://www.kenwoodinn.com',
            'The Springs Arenal': 'https://www.thespringscostarica.com',
            'Hotel Bellevue': 'https://www.adriaticluxuryhotels.com/hotel-bellevue-dubrovnik',
            'Solaz Luxury Collection': 'https://www.marriott.com/en-us/hotels/sjdlc-solaz-a-luxury-collection-resort-los-cabos/overview/',
            'Hotel MOTTO': 'https://www.hotel-motto.at/en',
            'Mystique': 'https://www.mystique.gr/en',
            'Las Alcobas': 'https://www.lasalcobas.com/',
            'El Ganzo': 'https://www.elganzo.com/',
            'Villa Santa Cruz': 'https://villasantacruzbaja.com/',
            'Edition Miami': 'https://www.editionhotels.com/miami-beach/',
            'Hotel Healdsburg': 'https://hotelhealdsburg.com/',
            'Calamigos Guest Ranch': 'https://www.calamigosguestranch.com/',
            'The Drake': 'https://www.thedrakeoakbrookhotel.com/',
            'Thompson Zihuatanejo': 'https://viceroy.hotelszihuatanejo.com/en/',
            'W Amsterdam': 'https://www.marriott.com/en-us/hotels/amswhw-w-amsterdam',
            'The Winchester': 'https://winchester.co.za',
            'Houghton Hotel': 'https://thehoughtonhotel.com',
            'Hacienda San Angel': 'https://haciendasanangel.com'
        };

        return websiteMap[hotel.name] || `https://www.google.com/search?q=${encodeURIComponent(hotel.name + ' ' + hotel.city + ' hotel official website')}`;
    }

    createHotelCard(hotel) {
        const hotelUrl = this.getHotelWebsite(hotel);
        
        return `
            <article class="hotel-card">
                <a href="${hotelUrl}" class="hotel-card-link" target="_blank" rel="noopener noreferrer">
                <div class="hotel-content">
                    <h3 class="hotel-name">${hotel.name}</h3>
                    <div class="hotel-location">
                        <i class="fas fa-map-marker-alt"></i>
                        ${hotel.city}, ${hotel.country}
                    </div>

                    <div class="hotel-rating">
                        <span class="rating-number">${hotel.rating.toFixed(2)}</span>
                        <span class="rating-text">/ 10</span>
                        <span class="price-range">${hotel.priceRange}</span>
                    </div>
                </div>
                </a>
            </article>
        `;
    }
}

// Initialize the module
document.addEventListener('DOMContentLoaded', () => {
    new HotelRankingsModule();
});
