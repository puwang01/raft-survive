extends Node
class_name SurvivalSystem
## Health / Hunger / Thirst — thirst empties ~75s, hunger ~140s.

signal health_changed(value: float)
signal hunger_changed(value: float)
signal thirst_changed(value: float)
signal died(reason: String)

@export var health: float = 100.0
@export var hunger: float = 100.0
@export var thirst: float = 100.0
@export var thirst_empty_seconds: float = 75.0
@export var hunger_empty_seconds: float = 140.0

var active: bool = false

func reset_stats(h: float = 100.0, g: float = 100.0, t: float = 100.0) -> void:
	health = h
	hunger = g
	thirst = t
	_emit_all()

func _process(delta: float) -> void:
	if not active:
		return
	if not GameState.running or GameState.paused or GameState.ended:
		return
	thirst = maxf(0.0, thirst - (100.0 / thirst_empty_seconds) * delta)
	hunger = maxf(0.0, hunger - (100.0 / hunger_empty_seconds) * delta)
	if thirst <= 0.0:
		health -= 8.0 * delta
	if hunger <= 0.0:
		health -= 5.0 * delta
	health = maxf(0.0, health)
	_emit_all()
	if health <= 0.0:
		active = false
		var reason := "口渴难忍，倒下了…" if thirst <= 0.0 else "饥饿虚弱，倒下了…"
		if thirst > 0.0 and hunger > 0.0:
			reason = "生命耗尽…葬身波涛。"
		died.emit(reason)

func hurt(amount: float) -> void:
	health = maxf(0.0, health - amount)
	health_changed.emit(health)
	if health <= 0.0:
		active = false
		died.emit("生命耗尽…葬身波涛。")

func drink(amount: float = 40.0) -> void:
	thirst = minf(100.0, thirst + amount)
	thirst_changed.emit(thirst)

func eat(amount: float = 35.0) -> void:
	hunger = minf(100.0, hunger + amount)
	hunger_changed.emit(hunger)

func _emit_all() -> void:
	health_changed.emit(health)
	hunger_changed.emit(hunger)
	thirst_changed.emit(thirst)

func export_data() -> Dictionary:
	return {"health": health, "hunger": hunger, "thirst": thirst}

func import_data(d: Dictionary) -> void:
	health = float(d.get("health", 100.0))
	hunger = float(d.get("hunger", 100.0))
	thirst = float(d.get("thirst", 100.0))
	_emit_all()
