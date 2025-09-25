// Galactic Background with Planets and Stars
class GalacticBackground {
    constructor() {
        this.background = document.querySelector('.background');
        this.planets = [];
        this.stars = [];
        this.mouse = { x: 0, y: 0 };
        this.animationId = null;
        
        this.init();
        this.setupEventListeners();
        this.animate();
    }
    
    init() {
        this.createStarField();
        this.createPlanets();
        this.createGalaxies();
    }
    
    createStarField() {
        const numStars = 200;
        for (let i = 0; i < numStars; i++) {
            const star = document.createElement('div');
            star.classList.add('star');
            
            // Random star types for variety
            const starType = Math.random();
            if (starType > 0.9) star.classList.add('star-large');
            else if (starType > 0.7) star.classList.add('star-medium');
            else star.classList.add('star-small');
            
            star.style.left = Math.random() * window.innerWidth + 'px';
            star.style.top = Math.random() * window.innerHeight + 'px';
            
            star.starData = {
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight,
                twinklePhase: Math.random() * Math.PI * 2,
                twinkleSpeed: 0.01 + Math.random() * 0.02
            };
            
            this.stars.push(star);
            this.background.appendChild(star);
        }
    }
    
    createPlanets() {
        const planetTypes = [
            { class: 'planet-earth', emoji: '🌍' },
            { class: 'planet-mars', emoji: '🔴' },
            { class: 'planet-jupiter', emoji: '🪐' },
            { class: 'planet-saturn', emoji: '🪐' },
            { class: 'planet-uranus', emoji: '🔵' },
            { class: 'planet-sun', emoji: '☀️' }
        ];
        
        const numPlanets = 7;
        for (let i = 0; i < numPlanets; i++) {
            const planet = document.createElement('div');
            const planetType = planetTypes[Math.floor(Math.random() * planetTypes.length)];
            
            planet.classList.add('planet', planetType.class);
            planet.textContent = planetType.emoji;
            
            planet.style.left = Math.random() * window.innerWidth + 'px';
            planet.style.top = Math.random() * window.innerHeight + 'px';
            
            planet.planetData = {
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight,
                vx: (Math.random() - 0.5) * 0.2,
                vy: (Math.random() - 0.5) * 0.2,
                rotation: 0,
                rotationSpeed: (Math.random() - 0.5) * 0.5,
                orbitRadius: 50 + Math.random() * 100,
                orbitAngle: Math.random() * Math.PI * 2,
                orbitSpeed: 0.005 + Math.random() * 0.01,
                pulsePhase: Math.random() * Math.PI * 2,
                pulseSpeed: 0.02 + Math.random() * 0.02
            };
            
            this.planets.push(planet);
            this.background.appendChild(planet);
        }
    }
    
    createGalaxies() {
        const numGalaxies = 4;
        for (let i = 0; i < numGalaxies; i++) {
            const galaxy = document.createElement('div');
            galaxy.classList.add('galaxy');
            
            galaxy.style.left = Math.random() * window.innerWidth + 'px';
            galaxy.style.top = Math.random() * window.innerHeight + 'px';
            
            galaxy.galaxyData = {
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight,
                rotation: 0,
                rotationSpeed: 0.1 + Math.random() * 0.2,
                scale: 0.5 + Math.random() * 0.5
            };
            
            this.background.appendChild(galaxy);
        }
    }
    
    setupEventListeners() {
        document.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
            this.createStardust(e.clientX, e.clientY);
        });
        
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }
    
    createStardust(x, y) {
        // Create temporary stardust trail effect
        const stardust = document.createElement('div');
        stardust.classList.add('stardust');
        stardust.style.left = x + 'px';
        stardust.style.top = y + 'px';
        this.background.appendChild(stardust);
        
        setTimeout(() => {
            if (stardust.parentNode) {
                stardust.parentNode.removeChild(stardust);
            }
        }, 1500);
    }
    
    animate() {
        this.updateStars();
        this.updatePlanets();
        this.updateGalaxies();
        
        this.animationId = requestAnimationFrame(() => this.animate());
    }
    
    updateStars() {
        const stars = document.querySelectorAll('.star');
        stars.forEach(star => {
            const data = star.starData;
            
            data.twinklePhase += data.twinkleSpeed;
            const twinkle = 0.3 + Math.sin(data.twinklePhase) * 0.7;
            
            star.style.opacity = twinkle;
        });
    }
    
    updatePlanets() {
        const planets = document.querySelectorAll('.planet');
        planets.forEach(planet => {
            const data = planet.planetData;
            
            // Gentle orbital movement
            data.orbitAngle += data.orbitSpeed;
            data.x += Math.cos(data.orbitAngle) * 0.1;
            data.y += Math.sin(data.orbitAngle) * 0.1;
            
            // Mouse interaction - gentle attraction
            const dx = this.mouse.x - data.x;
            const dy = this.mouse.y - data.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < 150) {
                const force = (150 - distance) / 1500;
                data.vx += (dx / distance) * force;
                data.vy += (dy / distance) * force;
            }
            
            // Update position with gentle movement
            data.x += data.vx;
            data.y += data.vy;
            
            // Gentle bounce off edges
            if (data.x < 0 || data.x > window.innerWidth) data.vx *= -0.8;
            if (data.y < 0 || data.y > window.innerHeight) data.vy *= -0.8;
            
            // Apply space friction
            data.vx *= 0.98;
            data.vy *= 0.98;
            
            // Rotation
            data.rotation += data.rotationSpeed;
            
            // Pulse effect
            data.pulsePhase += data.pulseSpeed;
            const pulse = 0.8 + Math.sin(data.pulsePhase) * 0.2;
            
            planet.style.left = data.x + 'px';
            planet.style.top = data.y + 'px';
            planet.style.transform = `rotate(${data.rotation}deg) scale(${pulse})`;
        });
    }
    
    updateGalaxies() {
        const galaxies = document.querySelectorAll('.galaxy');
        galaxies.forEach(galaxy => {
            const data = galaxy.galaxyData;
            
            data.rotation += data.rotationSpeed;
            
            galaxy.style.transform = `rotate(${data.rotation}deg) scale(${data.scale})`;
        });
    }
    
    handleResize() {
        // Update positions on resize
        this.planets.forEach(planet => {
            planet.planetData.x = Math.min(planet.planetData.x, window.innerWidth);
            planet.planetData.y = Math.min(planet.planetData.y, window.innerHeight);
        });
        
        this.stars.forEach(star => {
            star.starData.x = Math.min(star.starData.x, window.innerWidth);
            star.starData.y = Math.min(star.starData.y, window.innerHeight);
        });
    }
}

// Initialize the galactic background when page loads
document.addEventListener('DOMContentLoaded', () => {
    new GalacticBackground();
});