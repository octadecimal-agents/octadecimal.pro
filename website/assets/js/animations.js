/**
 * Octadecimal Portfolio - Animations
 * Neural Network Canvas + Scroll Reveal Animations
 */

// =====================================================
// NEURAL NETWORK CANVAS ANIMATION
// =====================================================

class NeuralNetwork {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    
    this.ctx = this.canvas.getContext('2d');
    this.nodes = [];
    this.connections = [];
    this.mouse = { x: null, y: null, radius: 150 };
    this.animationFrame = null;
    
    this.config = {
      nodeCount: 40,
      connectionDistance: 300,
      nodeRadius: { min: 1.5, max: 3 },
      nodeSpeed: { min: 0.1, max: 0.3 },
      colors: {
        node: 'rgba(0, 212, 170, 0.6)',
        nodeGlow: 'rgba(0, 212, 170, 0.3)',
        connection: 'rgba(124, 58, 237, 0.15)',
        connectionActive: 'rgba(0, 212, 170, 0.3)'
      }
    };
    
    this.init();
  }
  
  init() {
    this.resize();
    this.createNodes();
    this.addEventListeners();
    this.animate();
  }
  
  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }
  
  createNodes() {
    this.nodes = [];
    const { nodeCount, nodeRadius, nodeSpeed } = this.config;
    
    for (let i = 0; i < nodeCount; i++) {
      this.nodes.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        vx: (Math.random() - 0.5) * nodeSpeed.max,
        vy: (Math.random() - 0.5) * nodeSpeed.max,
        radius: nodeRadius.min + Math.random() * (nodeRadius.max - nodeRadius.min),
        pulsePhase: Math.random() * Math.PI * 2
      });
    }
  }
  
  addEventListeners() {
    // Mouse tracking
    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      this.mouse.x = e.clientX - rect.left;
      this.mouse.y = e.clientY - rect.top;
    });
    
    this.canvas.addEventListener('mouseleave', () => {
      this.mouse.x = null;
      this.mouse.y = null;
    });
    
    // Resize handling
    let resizeTimeout;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        this.resize();
        this.createNodes();
      }, 250);
    });
  }
  
  updateNodes() {
    this.nodes.forEach(node => {
      // Update position
      node.x += node.vx;
      node.y += node.vy;
      
      // Bounce off edges with smooth transition
      if (node.x < 0 || node.x > this.canvas.width) node.vx *= -1;
      if (node.y < 0 || node.y > this.canvas.height) node.vy *= -1;
      
      // Keep in bounds
      node.x = Math.max(0, Math.min(this.canvas.width, node.x));
      node.y = Math.max(0, Math.min(this.canvas.height, node.y));
      
      // Update pulse phase
      node.pulsePhase += 0.02;
      
      // Mouse interaction - gentle repel
      if (this.mouse.x !== null && this.mouse.y !== null) {
        const dx = node.x - this.mouse.x;
        const dy = node.y - this.mouse.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < this.mouse.radius) {
          const force = (this.mouse.radius - distance) / this.mouse.radius;
          node.x += dx * force * 0.02;
          node.y += dy * force * 0.02;
        }
      }
    });
  }
  
  drawConnections() {
    const { connectionDistance, colors } = this.config;
    
    for (let i = 0; i < this.nodes.length; i++) {
      for (let j = i + 1; j < this.nodes.length; j++) {
        const nodeA = this.nodes[i];
        const nodeB = this.nodes[j];
        const dx = nodeA.x - nodeB.x;
        const dy = nodeA.y - nodeB.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < connectionDistance) {
          const opacity = 1 - (distance / connectionDistance);
          
          // Check if mouse is near this connection
          let isActive = false;
          if (this.mouse.x !== null && this.mouse.y !== null) {
            const midX = (nodeA.x + nodeB.x) / 2;
            const midY = (nodeA.y + nodeB.y) / 2;
            const mouseDistance = Math.sqrt(
              Math.pow(midX - this.mouse.x, 2) + 
              Math.pow(midY - this.mouse.y, 2)
            );
            isActive = mouseDistance < 100;
          }
          
          this.ctx.beginPath();
          this.ctx.moveTo(nodeA.x, nodeA.y);
          this.ctx.lineTo(nodeB.x, nodeB.y);
          
          if (isActive) {
            this.ctx.strokeStyle = `rgba(0, 212, 170, ${opacity * 0.4})`;
            this.ctx.lineWidth = 1.5;
          } else {
            this.ctx.strokeStyle = `rgba(124, 58, 237, ${opacity * 0.15})`;
            this.ctx.lineWidth = 1;
          }
          
          this.ctx.stroke();
        }
      }
    }
  }
  
  drawNodes() {
    const { colors } = this.config;
    
    this.nodes.forEach(node => {
      const pulse = Math.sin(node.pulsePhase) * 0.3 + 1;
      const radius = node.radius * pulse;
      
      // Glow effect
      const gradient = this.ctx.createRadialGradient(
        node.x, node.y, 0,
        node.x, node.y, radius * 4
      );
      gradient.addColorStop(0, colors.node);
      gradient.addColorStop(0.5, colors.nodeGlow);
      gradient.addColorStop(1, 'transparent');
      
      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, radius * 4, 0, Math.PI * 2);
      this.ctx.fillStyle = gradient;
      this.ctx.fill();
      
      // Core node
      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
      this.ctx.fillStyle = colors.node;
      this.ctx.fill();
    });
  }
  
  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    this.updateNodes();
    this.drawConnections();
    this.drawNodes();
    
    this.animationFrame = requestAnimationFrame(() => this.animate());
  }
  
  destroy() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }
  }
}


// =====================================================
// SCROLL REVEAL ANIMATIONS
// =====================================================

class ScrollReveal {
  constructor() {
    this.observerOptions = {
      root: null,
      rootMargin: '0px 0px -50px 0px',
      threshold: 0.1
    };
    
    this.init();
  }
  
  init() {
    // Create observer
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
          // Add staggered delay based on element's position in grid
          const element = entry.target;
          const siblings = Array.from(element.parentElement?.children || []);
          const visibleIndex = siblings.filter(el => 
            el.classList.contains('scroll-reveal')
          ).indexOf(element);
          
          // Apply staggered animation
          setTimeout(() => {
            element.classList.add('revealed');
          }, visibleIndex * 100); // 100ms stagger
          
          // Stop observing after reveal
          this.observer.unobserve(element);
        }
      });
    }, this.observerOptions);
    
    // Observe all scroll-reveal elements
    this.observeElements();
    
    // Re-observe when new elements are added (for dynamically loaded content)
    this.setupMutationObserver();
  }
  
  observeElements() {
    document.querySelectorAll('.scroll-reveal').forEach(el => {
      this.observer.observe(el);
    });
  }
  
  setupMutationObserver() {
    const mutationObserver = new MutationObserver((mutations) => {
      mutations.forEach(mutation => {
        mutation.addedNodes.forEach(node => {
          if (node.nodeType === 1) { // Element node
            if (node.classList?.contains('scroll-reveal')) {
              this.observer.observe(node);
            }
            // Also check children
            node.querySelectorAll?.('.scroll-reveal').forEach(el => {
              this.observer.observe(el);
            });
          }
        });
      });
    });
    
    mutationObserver.observe(document.body, {
      childList: true,
      subtree: true
    });
  }
}


// =====================================================
// SMOOTH PARALLAX FOR HERO ELEMENTS
// =====================================================

class ParallaxEffect {
  constructor() {
    this.elements = [];
    this.ticking = false;
    this.init();
  }
  
  init() {
    // Get parallax elements
    this.elements = document.querySelectorAll('[data-parallax]');
    
    if (this.elements.length === 0) return;
    
    window.addEventListener('scroll', () => this.onScroll(), { passive: true });
  }
  
  onScroll() {
    if (!this.ticking) {
      requestAnimationFrame(() => {
        this.updateParallax();
        this.ticking = false;
      });
      this.ticking = true;
    }
  }
  
  updateParallax() {
    const scrollY = window.scrollY;
    
    this.elements.forEach(el => {
      const speed = parseFloat(el.dataset.parallax) || 0.5;
      const yPos = -(scrollY * speed);
      el.style.transform = `translate3d(0, ${yPos}px, 0)`;
    });
  }
}


// =====================================================
// FLOATING GRADIENT ORBS (subtle background effect)
// =====================================================

class FloatingOrbs {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    if (!this.container) return;
    
    this.orbs = [];
    this.config = {
      orbCount: 3,
      colors: [
        'rgba(124, 58, 237, 0.15)',   // Purple
        'rgba(0, 212, 170, 0.12)',    // Teal
        'rgba(245, 158, 11, 0.08)'    // Amber
      ],
      sizes: [300, 400, 350]
    };
    
    this.createOrbs();
    this.animate();
  }
  
  createOrbs() {
    const { orbCount, colors, sizes } = this.config;
    
    for (let i = 0; i < orbCount; i++) {
      const orb = document.createElement('div');
      orb.className = 'floating-orb';
      orb.style.cssText = `
        position: absolute;
        width: ${sizes[i]}px;
        height: ${sizes[i]}px;
        border-radius: 50%;
        background: radial-gradient(circle, ${colors[i]} 0%, transparent 70%);
        filter: blur(60px);
        pointer-events: none;
        will-change: transform;
      `;
      
      this.container.appendChild(orb);
      
      this.orbs.push({
        element: orb,
        x: Math.random() * 100,
        y: Math.random() * 100,
        speedX: (Math.random() - 0.5) * 0.02,
        speedY: (Math.random() - 0.5) * 0.02,
        phase: Math.random() * Math.PI * 2
      });
    }
  }
  
  animate() {
    this.orbs.forEach((orb, index) => {
      orb.phase += 0.005;
      
      // Smooth floating motion
      const floatX = Math.sin(orb.phase) * 5;
      const floatY = Math.cos(orb.phase * 0.7) * 5;
      
      orb.x += orb.speedX;
      orb.y += orb.speedY;
      
      // Bounce off edges
      if (orb.x < 0 || orb.x > 100) orb.speedX *= -1;
      if (orb.y < 0 || orb.y > 100) orb.speedY *= -1;
      
      orb.element.style.left = `${orb.x + floatX}%`;
      orb.element.style.top = `${orb.y + floatY}%`;
    });
    
    requestAnimationFrame(() => this.animate());
  }
}


// =====================================================
// INITIALIZE ALL ANIMATIONS
// =====================================================

document.addEventListener('DOMContentLoaded', () => {
  // Detect mobile devices (width < 768px or touch device)
  const isMobile = window.innerWidth < 768 || 
    ('ontouchstart' in window) || 
    (navigator.maxTouchPoints > 0);
  
  let neuralNetwork = null;
  let floatingOrbs = null;
  
  // Only initialize heavy canvas animations on desktop
  if (!isMobile) {
    // Neural Network in Hero
    neuralNetwork = new NeuralNetwork('neural-canvas');
    
    // Floating Orbs
    floatingOrbs = new FloatingOrbs('hero-orbs');
    
    console.log('🎨 Desktop animations enabled');
  } else {
    // Hide canvas container on mobile
    const canvasContainer = document.querySelector('.neural-canvas-container');
    if (canvasContainer) {
      canvasContainer.style.display = 'none';
    }
    const orbsContainer = document.getElementById('hero-orbs');
    if (orbsContainer) {
      orbsContainer.style.display = 'none';
    }
    console.log('📱 Mobile detected - canvas animations disabled');
  }
  
  // Scroll Reveal Animations (works on all devices)
  const scrollReveal = new ScrollReveal();
  
  // Parallax Effects (works on all devices)
  const parallax = new ParallaxEffect();
  
  // Add scroll-reveal class to project cards when they're loaded
  const projectsGrid = document.getElementById('projects-grid');
  if (projectsGrid) {
    const observer = new MutationObserver(() => {
      projectsGrid.querySelectorAll('.project-card:not(.scroll-reveal)').forEach(card => {
        card.classList.add('scroll-reveal');
      });
    });
    observer.observe(projectsGrid, { childList: true, subtree: true });
  }
  
  // Handle resize - enable/disable animations when crossing mobile threshold
  let wasDesktop = !isMobile;
  window.addEventListener('resize', () => {
    const isNowMobile = window.innerWidth < 768;
    
    if (wasDesktop && isNowMobile) {
      // Switched to mobile - hide canvas
      const canvasContainer = document.querySelector('.neural-canvas-container');
      if (canvasContainer) canvasContainer.style.display = 'none';
      const orbsContainer = document.getElementById('hero-orbs');
      if (orbsContainer) orbsContainer.style.display = 'none';
      if (neuralNetwork) neuralNetwork.destroy();
    } else if (!wasDesktop && !isNowMobile && !neuralNetwork) {
      // Switched to desktop - show canvas (page reload recommended)
      const canvasContainer = document.querySelector('.neural-canvas-container');
      if (canvasContainer) canvasContainer.style.display = 'block';
      const orbsContainer = document.getElementById('hero-orbs');
      if (orbsContainer) orbsContainer.style.display = 'block';
    }
    
    wasDesktop = !isNowMobile;
  });
  
  console.log('🎨 Octadecimal Animations initialized');
});

