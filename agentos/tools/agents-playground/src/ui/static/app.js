// app.js

document.addEventListener('DOMContentLoaded', () => {
    console.log('App initialized.');

    // Add interactive glow effect to glass containers
    const containers = document.querySelectorAll('.glass-container');
    
    containers.forEach(container => {
        container.addEventListener('mousemove', (e) => {
            const rect = container.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Calculate a subtle background gradient change based on mouse position
            const xPercent = (x / rect.width) * 100;
            const yPercent = (y / rect.height) * 100;
            
            container.style.background = `
                radial-gradient(
                    circle at ${xPercent}% ${yPercent}%, 
                    rgba(255, 255, 255, 0.12), 
                    rgba(255, 255, 255, 0.05) 50%
                )
            `;
        });
        
        container.addEventListener('mouseleave', () => {
            // Reset background when mouse leaves
            container.style.background = 'rgba(255, 255, 255, 0.05)';
        });
    });

    // Add a simple entrance animation
    const elementsToAnimate = document.querySelectorAll('.glass-container, .glass-card, h1, p, .btn');
    
    elementsToAnimate.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 100 * index);
    });
});
