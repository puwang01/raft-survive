shader_type canvas_item;
render_mode blend_mix, unshaded;

// See-through tropical ocean — ripples, reflections, seafloor + creatures visible
uniform vec4 deep_color : source_color = vec4(0.04, 0.35, 0.48, 0.55);
uniform vec4 mid_color : source_color = vec4(0.12, 0.58, 0.68, 0.42);
uniform vec4 shallow_color : source_color = vec4(0.35, 0.82, 0.85, 0.32);
uniform vec4 foam_color : source_color = vec4(0.94, 0.99, 1.0, 0.75);
uniform vec4 specular_color : source_color = vec4(1.0, 0.99, 0.94, 0.7);
uniform float wave_speed : hint_range(0.05, 3.0) = 0.75;
uniform float wave_scale : hint_range(1.0, 60.0) = 16.0;
uniform float foam_amount : hint_range(0.0, 1.0) = 0.38;
uniform float caustic_strength : hint_range(0.0, 0.5) = 0.22;
uniform float depth_contrast : hint_range(0.2, 2.0) = 1.05;
uniform sampler2D underlay_tex : source_color, hint_default_black;
uniform float underlay_mix : hint_range(0.0, 1.0) = 0.72;
uniform float surface_alpha : hint_range(0.15, 0.9) = 0.48;
uniform float ripple_strength : hint_range(0.0, 0.08) = 0.038;
uniform float reflection_strength : hint_range(0.0, 1.0) = 0.45;

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
	for (int i = 0; i < 5; i++) {
		v += a * noise(p);
		p *= 2.05;
		a *= 0.5;
	}
	return v;
}

void fragment() {
	vec2 uv = UV;
	float t = TIME * wave_speed;

	// Multi-layer wave / ripple distortion (surface undulation)
	float n1 = fbm(uv * wave_scale * 0.32 + vec2(t * 0.18, -t * 0.1));
	float n2 = fbm(uv * wave_scale * 0.75 + vec2(-t * 0.14, t * 0.2));
	float n3 = fbm(uv * wave_scale * 1.6 + vec2(t * 0.35, t * 0.28));
	vec2 warp = vec2(n1 - 0.5, n2 - 0.5) * ripple_strength
		+ vec2(n3 - 0.5, n1 - 0.5) * ripple_strength * 0.45;
	vec2 duv = uv + warp;

	// Depth field — soft patches of shallow/deep turquoise
	float depth = fbm(duv * 3.0 + vec2(t * 0.035, t * 0.028));
	depth = pow(clamp(depth * depth_contrast, 0.0, 1.0), 1.05);
	vec3 col = mix(deep_color.rgb, mid_color.rgb, smoothstep(0.18, 0.52, depth));
	col = mix(col, shallow_color.rgb, smoothstep(0.48, 0.88, depth));

	// Refracted seafloor / underlay — clearly visible through water
	vec2 under_uv = duv * vec2(1.0, 1.12) + warp * 2.4;
	vec4 under = texture(underlay_tex, under_uv);
	float see_through = underlay_mix * (0.55 + 0.45 * depth);
	col = mix(col, under.rgb, under.a * see_through);

	// Caustic shimmer (sun through water onto seafloor)
	float cau1 = fbm(duv * 12.0 + vec2(t * 0.55, -t * 0.38));
	float cau2 = fbm(duv * 17.0 + vec2(-t * 0.48, t * 0.62));
	float caust = pow(max(0.0, cau1 * cau2), 2.0) * caustic_strength;
	col += vec3(caust * 0.5, caust * 0.95, caust * 1.2);

	// Surface ripple ridges (wave crests)
	float ridge = abs(sin((duv.x * 28.0 + duv.y * 9.0) + t * 1.4 + n1 * 4.0));
	ridge = pow(1.0 - ridge, 6.0) * 0.18;
	float ridge2 = abs(sin((duv.x * -14.0 + duv.y * 22.0) - t * 1.1 + n2 * 3.0));
	ridge2 = pow(1.0 - ridge2, 7.0) * 0.12;
	col += vec3(0.55, 0.85, 0.95) * (ridge + ridge2);

	// Foam / whitecaps on crest peaks
	float foam_n = fbm(duv * 20.0 + vec2(t * 0.85, t * 0.5));
	float foam_band = smoothstep(0.66, 0.94, foam_n) * foam_amount;
	float foam2 = smoothstep(0.78, 0.96, noise(duv * 38.0 + t * 1.4)) * foam_amount * 0.4;
	float foam = clamp(foam_band + foam2, 0.0, 1.0);
	col = mix(col, foam_color.rgb, foam * foam_color.a);

	// Specular sun glints / surface reflections
	float spec = pow(max(0.0, 1.0 - abs(n1 - 0.52) * 3.2), 10.0);
	spec += pow(max(0.0, 1.0 - abs(n2 - 0.48) * 4.0), 14.0) * 0.55;
	spec *= reflection_strength * (0.4 + 0.6 * smoothstep(0.35, 0.85, depth));
	col = mix(col, specular_color.rgb, clamp(spec * specular_color.a, 0.0, 1.0));

	// Soft sky reflection band near top (horizon)
	float horizon = smoothstep(0.6, 0.0, uv.y);
	vec3 sky_reflect = vec3(0.55, 0.78, 0.92);
	col = mix(col, sky_reflect, horizon * 0.22 * reflection_strength);

	// Deeper cool tint toward bottom
	float deep_v = smoothstep(0.5, 1.0, uv.y);
	col = mix(col, deep_color.rgb, deep_v * 0.15);

	// Watery feel: alpha so underlay sprite + swimming fish show through
	float a = mix(surface_alpha + 0.12, surface_alpha - 0.08, depth);
	a = clamp(a + foam * 0.25 + spec * 0.15, 0.28, 0.78);
	COLOR = vec4(col, a);
}
