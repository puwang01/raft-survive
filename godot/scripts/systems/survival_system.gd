extends Node
## Placeholder: Health / Hunger / Thirst tick. Port from play/index.html.
signal health_changed(value: float)
signal hunger_changed(value: float)
signal thirst_changed(value: float)
signal died(reason: String)

@export var health: float = 100.0
@export var hunger: float = 100.0
@export var thirst: float = 100.0
@export var thirst_empty_seconds: float = 75.0
@export var hunger_empty_seconds: float = 140.0

func _process(delta: float) -> void:
	thirst = maxf(0.0, thirst - (100.0 / thirst_empty_seconds) * delta)
	hunger = maxf(0.0, hunger - (100.0 / hunger_empty_seconds) * delta)
	thirst_changed.emit(thirst)
	hunger_changed.emit(hunger)
	if thirst <= 0.0:
		health -= 8.0 * delta
	if hunger <= 0.0:
		health -= 5.0 * delta
	health = maxf(0.0, health)
	health_changed.emit(health)
	if health <= 0.0:
		died.emit("survival")
