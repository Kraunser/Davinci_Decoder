// DaVinci Decoder - Animations

// Add subtle parallax effect to background pattern
document.addEventListener('mousemove', (e) => {
    const pattern = document.querySelector('.davinci-pattern');
    const x = e.clientX / window.innerWidth;
    const y = e.clientY / window.innerHeight;

    pattern.style.transform = `translate(${x * 10}px, ${y * 10}px)`;
});

// Animate cards on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeIn 0.6s ease forwards';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.card').forEach(card => {
    card.style.opacity = '0';
    observer.observe(card);
});

// Add hover effect to gear animations
document.querySelectorAll('.gear').forEach((gear, index) => {
    gear.addEventListener('mouseenter', () => {
        gear.style.transform = `scale(1.2) rotate(${index * 120}deg)`;
        gear.style.borderColor = 'var(--davinci-gold)';
    });

    gear.addEventListener('mouseleave', () => {
        gear.style.transform = 'scale(1) rotate(0deg)';
        gear.style.borderColor = 'var(--davinci-bronze)';
    });
});

// Smooth scroll for all anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Add ripple effect to button
document.querySelector('.btn-primary').addEventListener('click', function (e) {
    const ripple = document.createElement('span');
    const rect = this.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    ripple.style.cssText = `
        position: absolute;
        width: 20px;
        height: 20px;
        background: rgba(255, 255, 255, 0.6);
        border-radius: 50%;
        transform: translate(-50%, -50%) scale(0);
        animation: ripple 0.6s ease-out;
        pointer-events: none;
        left: ${x}px;
        top: ${y}px;
    `;

    this.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
});

// Add CSS for ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: translate(-50%, -50%) scale(20);
            opacity: 0;
        }
    }
    
    .btn-primary {
        position: relative;
        overflow: hidden;
    }
`;
document.head.appendChild(style);
