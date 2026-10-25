extends Area2D
class_name Shark

signal bit_raft(amount: float)

var velocity: Vector2 = Vector2(40, 20)
var aggro: float = 0.0
var bite_cd: float = 0.0
var raft_path: NodePath

@onready var sprite: Sprite2D = $Sprite2D

func _ready() -> void:
	sprite.texture = load("res://assets/art/shark.png")
	add_to_group("shark")

func _process(delta: float) -> void:
	if not GameState.running or GameState.paused or GameState.ended:
		return
	bite_cd = maxf(0.0, bite_cd - delta)
	var raft: Node2D = get_node_or_null(raft_path) as Node2D
	if raft == null:
		raft = get_tree().get_first_node_in_group("raft") as Node2D
	if raft == null:
		return
	var to_raft := raft.global_position - global_position
	var dist := to_raft.length()
	if dist < 1.0:
		dist = 1.0
	var aggro_time := GameState.play_time > 45.0 or GameState.wood >= 2
	if aggro_time:
		aggro = minf(1.0, aggro + delta * 0.15)
	else:
		aggro = maxf(0.0, aggro - delta * 0.05)
	var speed := 55.0 + aggro * 90.0
	if aggro > 0.2:
		velocity = to_raft / dist * speed
	else:
		velocity += Vector2(randf() - 0.5, randf() - 0.5) * 40.0 * delta
		var sp := velocity.length()
		if sp > 1.0:
			velocity = velocity / sp * 50.0
	global_position += velocity * delta
	global_position.x = clampf(global_position.x, 40.0, 860.0)
	global_position.y = clampf(global_position.y, 40.0, 1360.0)
	rotation = velocity.angle()
	modulate = Color(1.15, 0.85, 0.85) if aggro > 0.3 else Color.WHITE
	if dist < 55.0 and bite_cd <= 0.0 and aggro > 0.3:
		bite_cd = 2.2
		bit_raft.emit(18.0)
