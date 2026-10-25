extends Area2D
class_name Debris
## Floating loot: wood / barrel / crate / fish / bottle.

enum Kind { WOOD, BARREL, CRATE, FISH, BOTTLE }

var kind: Kind = Kind.WOOD
var velocity: Vector2 = Vector2.ZERO
var bob_phase: float = 0.0
var hooked: bool = false
var radius: float = 18.0

@onready var sprite: Sprite2D = $Sprite2D

const TEX := {
	Kind.WOOD: "res://assets/art/debris_wood.png",
	Kind.BARREL: "res://assets/art/debris_barrel.png",
	Kind.CRATE: "res://assets/art/debris_crate.png",
	Kind.FISH: "res://assets/art/debris_fish.png",
	Kind.BOTTLE: "res://assets/art/debris_bottle.png",
}

func setup(k: Kind, pos: Vector2, vel: Vector2) -> void:
	kind = k
	global_position = pos
	velocity = vel
	bob_phase = randf() * TAU
	radius = 16.0 if k == Kind.WOOD else (12.0 if k == Kind.FISH else 18.0)
	add_to_group("debris")
	_apply_tex()

func _ready() -> void:
	_apply_tex()
	var cs := get_node_or_null("CollisionShape2D")
	if cs and cs.shape == null:
		var circle := CircleShape2D.new()
		circle.radius = radius
		cs.shape = circle

func _apply_tex() -> void:
	if sprite == null:
		sprite = get_node_or_null("Sprite2D")
	if sprite:
		sprite.texture = load(TEX[kind])
		sprite.centered = true

func _process(delta: float) -> void:
	if hooked:
		return
	if not GameState.running or GameState.paused or GameState.ended:
		# still bob visually on title
		bob_phase += delta * 2.2
		if sprite:
			sprite.position.y = sin(bob_phase) * 3.0
		return
	bob_phase += delta * 2.2
	position += velocity * delta
	if sprite:
		sprite.position.y = sin(bob_phase) * 3.0
	# soft world bounds
	var world_size := Vector2(900, 1400)
	if position.x < 30.0 or position.x > world_size.x - 30.0:
		velocity.x *= -1.0
	if position.y < 30.0 or position.y > world_size.y - 30.0:
		velocity.y *= -1.0
	position.x = clampf(position.x, 20.0, world_size.x - 20.0)
	position.y = clampf(position.y, 20.0, world_size.y - 20.0)

func loot_label() -> String:
	match kind:
		Kind.WOOD: return "wood"
		Kind.BARREL: return "barrel"
		Kind.CRATE: return "crate"
		Kind.FISH: return "fish"
		Kind.BOTTLE: return "bottle"
	return "wood"
