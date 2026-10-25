extends Node2D
class_name HookController
## Drag aim + release throw; reel on grab or button.

signal loot_retrieved(kind_name: String)

enum Phase { IDLE, FLY, REEL }

var phase: Phase = Phase.IDLE
var hook_pos: Vector2 = Vector2.ZERO
var hook_vel: Vector2 = Vector2.ZERO
var max_dist: float = 340.0
var target: Debris = null
var aiming: bool = false
var aim_world: Vector2 = Vector2.ZERO

@onready var line: Line2D = $Line
@onready var hook_sprite: Sprite2D = $HookSprite
@onready var aim_line: Line2D = $AimLine

var _origin_offset := Vector2(36, -28)

func _ready() -> void:
	line.width = 2.5
	line.default_color = Color(0.9, 0.93, 0.97, 0.9)
	aim_line.width = 2.0
	aim_line.default_color = Color(1.0, 0.86, 0.35, 0.75)
	hook_sprite.texture = load("res://assets/art/hook.png")
	hook_sprite.visible = false
	aim_line.visible = false

func origin_global() -> Vector2:
	return global_position + _origin_offset

func _process(delta: float) -> void:
	_update_visuals()
	if not GameState.running or GameState.paused or GameState.ended:
		return
	match phase:
		Phase.FLY:
			hook_pos += hook_vel * delta
			hook_vel *= 1.0 - 0.35 * delta
			var dist := hook_pos.distance_to(origin_global())
			for d in get_tree().get_nodes_in_group("debris"):
				if d is Debris and not d.hooked:
					if hook_pos.distance_to(d.global_position) < d.radius + 12.0:
						d.hooked = true
						target = d
						phase = Phase.REEL
						break
			if dist > max_dist or hook_pos.x < 0 or hook_pos.y < 0 or hook_pos.x > 900 or hook_pos.y > 1400:
				phase = Phase.REEL
		Phase.REEL:
			var o := origin_global()
			if target and is_instance_valid(target):
				var dir := (o - target.global_position)
				var dist := dir.length()
				if dist < 1.0:
					dist = 1.0
				target.global_position += dir / dist * 280.0 * delta
				hook_pos = target.global_position
				if dist < 42.0:
					var kind_name: String = target.loot_label()
					target.queue_free()
					target = null
					phase = Phase.IDLE
					loot_retrieved.emit(kind_name)
			else:
				var dir2 := (o - hook_pos)
				var dist2 := dir2.length()
				if dist2 < 1.0:
					dist2 = 1.0
				hook_pos += dir2 / dist2 * 400.0 * delta
				if dist2 < 24.0:
					phase = Phase.IDLE

func _update_visuals() -> void:
	var o := origin_global()
	if phase == Phase.IDLE:
		hook_sprite.visible = false
		line.points = PackedVector2Array()
	else:
		hook_sprite.visible = true
		hook_sprite.global_position = hook_pos
		line.points = PackedVector2Array([to_local(o), to_local(hook_pos)])
	if aiming and phase == Phase.IDLE:
		aim_line.visible = true
		var dx := aim_world - o
		var len := dx.length()
		if len < 1.0:
			len = 1.0
		var reach := minf(340.0, len)
		var endp := o + dx / len * reach
		aim_line.points = PackedVector2Array([to_local(o), to_local(endp)])
	else:
		aim_line.visible = false

func begin_aim(world: Vector2) -> void:
	if phase != Phase.IDLE or not GameState.running or GameState.paused or GameState.ended:
		return
	aiming = true
	aim_world = world

func update_aim(world: Vector2) -> void:
	if aiming:
		aim_world = world

func release_aim() -> void:
	if not aiming:
		return
	aiming = false
	if phase == Phase.IDLE:
		throw_to(aim_world)

func throw_to(world: Vector2) -> void:
	if phase != Phase.IDLE:
		return
	var o := origin_global()
	var dx := world - o
	var len := dx.length()
	if len < 1.0:
		len = 1.0
	var speed := 520.0
	var scale := minf(1.0, 340.0 / len)
	phase = Phase.FLY
	hook_pos = o
	hook_vel = dx / len * speed * scale
	target = null
	max_dist = minf(340.0, len * 0.95 + 80.0)

func reel(force: bool = true) -> void:
	if phase == Phase.IDLE:
		return
	if phase == Phase.FLY or force:
		phase = Phase.REEL
		if force and target == null:
			pass
