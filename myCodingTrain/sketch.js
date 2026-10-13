function setup() {
  // Creates a canvas that fills the preview window
  createCanvas(600, 400);
}

function draw() {
  // Dark grey background (Coding Train style)
  background(51); 
  
  // Draw a bright circle that follows your mouse
  fill(199, 200, 255);
  noStroke();
  circle(mouseX, mouseY, 64);
}

