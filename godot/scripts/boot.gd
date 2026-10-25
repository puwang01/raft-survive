extends Control

func _ready() -> void:
	await get_tree().create_timer(0.35).timeout
	get_tree().change_scene_to_file("res://scenes/level/level_1.tscn")
