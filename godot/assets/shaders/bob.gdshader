shader_type canvas_item;
uniform float amp : hint_range(0.0, 8.0) = 3.0;
uniform float speed : hint_range(0.1, 4.0) = 1.2;
uniform float phase : hint_range(0.0, 6.28) = 0.0;

void vertex() {
	VERTEX.y += sin(TIME * speed + phase + VERTEX.x * 0.02) * amp;
}
