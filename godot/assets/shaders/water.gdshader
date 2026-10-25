shader_type canvas_item;

uniform vec4 deep_color : source_color = vec4(0.05, 0.35, 0.48, 1.0);
uniform vec4 shallow_color : source_color = vec4(0.25, 0.72, 0.78, 1.0);
uniform vec4 foam_color : source_color = vec4(0.85, 0.95, 1.0, 0.55);
uniform float wave_speed : hint_range(0.1, 3.0) = 0.85;
uniform float wave_scale : hint_range(1.0, 40.0) = 12.0;
uniform float foam_amount : hint_range(0.0, 1.0) = 0.35;

void fragment() {
	vec2 uv = UV;
	float t = TIME * wave_speed;
	float w1 = sin(uv.x * wave_scale + t * 1.7) * 0.015;
	float w2 = cos(uv.y * wave_scale * 0.8 - t * 1.3) * 0.012;
	float w3 = sin((uv.x + uv.y) * wave_scale * 0.5 + t) * 0.01;
	vec2 duv = uv + vec2(w1 + w3, w2 - w3);

	float depth = 0.45 + 0.25 * sin(duv.x * 6.0 + t * 0.4) + 0.2 * cos(duv.y * 5.0 - t * 0.3);
	depth = clamp(depth, 0.0, 1.0);
	vec3 col = mix(deep_color.rgb, shallow_color.rgb, depth);

	float foam = smoothstep(0.65, 0.95, sin(duv.x * 28.0 + t * 2.0) * sin(duv.y * 22.0 - t * 1.5));
	foam *= foam_amount;
	col = mix(col, foam_color.rgb, foam);

	// soft caustic shimmer
	float caust = pow(0.5 + 0.5 * sin(duv.x * 18.0 + t) * cos(duv.y * 16.0 - t * 0.8), 3.0) * 0.12;
	col += vec3(caust * 0.6, caust, caust * 1.1);

	COLOR = vec4(col, 1.0);
}
