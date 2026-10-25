shader_type canvas_item;

// Polished tropical ocean — depth, waves, foam, caustics, specular
uniform vec4 deep_color : source_color = vec4(0.02, 0.28, 0.42, 1.0);
uniform vec4 mid_color : source_color = vec4(0.08, 0.52, 0.62, 1.0);
uniform vec4 shallow_color : source_color = vec4(0.28, 0.78, 0.82, 1.0);
uniform vec4 foam_color : source_color = vec4(0.92, 0.98, 1.0, 0.85);
uniform vec4 specular_color : source_color = vec4(1.0, 0.98, 0.92, 0.55);
uniform float wave_speed : hint_range(0.05, 3.0) = 0.7;
uniform float wave_scale : hint_range(1.0, 60.0) = 18.0;
uniform float foam_amount : hint_range(0.0, 1.0) = 0.42;
uniform float caustic_strength : hint_range(0.0, 0.5) = 0.16;
uniform float depth_contrast : hint_range(0.2, 2.0) = 1.15;
uniform sampler2D underlay_tex : source_color, hint_default_black;
uniform float underlay_mix : hint_range(0.0, 1.0) = 0.35;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	float a = hash(i);
	float b = hash(i + vec2(1.0, 0.0));
	float c = hash(i + vec2(0.0, 1.0));
	float d = hash(i + vec2(1.0, 1.0));
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

float fbm(vec2 p) {
	float v = 0.0;
	float a = 0.5;
	for (int i = 0; i < 4; i++) {
		v += a * noise(p);
		p *= 2.05;
		a *= 0.5;
	}
	return v;
}

void fragment() {
	vec2 uv = UV;
	float t = TIME * wave_speed;

	// Multi-layer wave distortion
	float n1 = fbm(uv * wave_scale * 0.35 + vec2(t * 0.15, -t * 0.08));
	float n2 = fbm(uv * wave_scale * 0.7 + vec2(-t * 0.12, t * 0.18));
	vec2 warp = vec2(n1 - 0.5, n2 - 0.5) * 0.028;
	vec2 duv = uv + warp;

	// Depth field — soft patches of shallow/deep turquoise
	float depth = fbm(duv * 3.2 + vec2(t * 0.04, t * 0.03));
	depth = pow(clamp(depth * depth_contrast, 0.0, 1.0), 1.1);
	vec3 col = mix(deep_color.rgb, mid_color.rgb, smoothstep(0.2, 0.55, depth));
	col = mix(col, shallow_color.rgb, smoothstep(0.5, 0.9, depth));

	// Underwater underlay (coral/sand silhouettes)
	vec4 under = texture(underlay_tex, duv * vec2(1.0, 1.15) + warp * 2.0);
	col = mix(col, mix(col, under.rgb, under.a), underlay_mix * (0.4 + 0.6 * depth));

	// Caustic shimmer (sun through water)
	float cau1 = fbm(duv * 14.0 + vec2(t * 0.6, -t * 0.4));
	float cau2 = fbm(duv * 18.0 + vec2(-t * 0.5, t * 0.7));
	float caust = pow(max(0.0, cau1 * cau2), 2.2) * caustic_strength;
	col += vec3(caust * 0.55, caust * 0.95, caust * 1.15);

	// Surface foam streaks / whitecaps
	float foam_n = fbm(duv * 22.0 + vec2(t * 0.9, t * 0.55));
	float foam_band = smoothstep(0.62, 0.92, foam_n) * foam_amount;
	// secondary fine foam
	float foam2 = smoothstep(0.75, 0.95, noise(duv * 40.0 + t * 1.5)) * foam_amount * 0.45;
	float foam = clamp(foam_band + foam2, 0.0, 1.0);
	col = mix(col, foam_color.rgb, foam * foam_color.a);

	// Soft specular sun glints
	float spec = pow(max(0.0, 1.0 - abs(n1 - 0.55) * 3.5), 8.0);
	spec *= 0.35 + 0.65 * smoothstep(0.4, 0.8, depth);
	col = mix(col, specular_color.rgb, spec * specular_color.a);

	// Horizon brightening (top of screen slightly lighter)
	float horizon = smoothstep(0.55, 0.0, uv.y);
	col = mix(col, shallow_color.rgb * 1.08, horizon * 0.18);

	// Subtle vignette cool tint at bottom (deeper feel)
	float deep_v = smoothstep(0.45, 1.0, uv.y);
	col = mix(col, deep_color.rgb, deep_v * 0.12);

	COLOR = vec4(col, 1.0);
}
