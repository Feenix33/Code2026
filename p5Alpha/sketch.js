function setup() {
  createCanvas(400, 400);
}

function draw() {
  background(220);
  fill(255, 0, 0);
  // Draw a hexagon
  beginShape();
  for (let i = 0; i < 6; i++) {
    let angle = TWO_PI / 6 * i;
    let x = 200 + cos(angle) * 50;
    let y = 200 + sin(angle) * 50;
    vertex(x, y);
  }
  endShape(CLOSE);
}