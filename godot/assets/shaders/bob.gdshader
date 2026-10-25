shader_type canvas_item;
uniform float amp : hint_range(0.0, 8.0) = 3.0;
uniform float speed : hint_range(0.0, 6.0) = 2.2;
uniform float phase = 0.0;

void vertex() {
	VERTEX.y += sin(TIME * speed + phase) * amp;
}
