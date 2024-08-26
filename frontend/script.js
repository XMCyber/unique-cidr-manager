const background = document.querySelector('.background');
const numDots = 250; // Increase this number as needed

for (let i = 0; i < numDots; i++) {
  const dot = document.createElement('div');
  dot.classList.add('dot');
  background.appendChild(dot);
}

document.addEventListener('mousemove', (e) => {
  const mouseX = e.clientX;
  const mouseY = e.clientY;

  const dots = document.querySelectorAll('.dot');
  dots.forEach((dot, i) => {
    const x = Math.random() * window.innerWidth;
    const y = Math.random() * window.innerHeight;
    dot.style.left = `${x}px`;
    dot.style.top = `${y}px`;
  });
});