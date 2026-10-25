extends Node
## Manual + autosave (default 60s) to user:// JSON.

const SAVE_PATH := "user://raft_survive_l1.json"
signal saved(manual: bool)
signal loaded

@export var autosave_seconds: float = 60.0
var _acc: float = 0.0
var _enabled: bool = false

func _process(delta: float) -> void:
	if not _enabled:
		return
	if not GameState.running or GameState.paused or GameState.ended:
		return
	_acc += delta
	if _acc >= autosave_seconds:
		_acc = 0.0
		if save_manual(false):
			GameState.show_toast("自动存档", 0.9)

func enable_autosave(on: bool = true) -> void:
	_enabled = on
	_acc = 0.0

func has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH)

func save_manual(manual: bool = true) -> bool:
	var level := get_tree().get_first_node_in_group("level_root")
	var data: Dictionary = {}
	if level and level.has_method("export_save"):
		data = level.export_save()
	else:
		data = {
			"health": 100.0, "hunger": 100.0, "thirst": 100.0,
			"wood": GameState.wood, "food": GameState.food, "water": GameState.water,
			"time_left": GameState.time_left, "play_time": GameState.play_time,
			"hooked_count": GameState.hooked_count,
		}
	var payload := {"v": 2, "saved_at": Time.get_unix_time_from_system(), "state": data}
	var ok := _write(payload)
	if ok:
		saved.emit(manual)
		if manual:
			GameState.show_toast("已保存 ✓")
	elif manual:
		GameState.show_toast("存档失败")
	return ok

func load_save() -> Dictionary:
	if not has_save():
		return {}
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY:
		return {}
	var st: Variant = parsed.get("state", {})
	if typeof(st) != TYPE_DICTIONARY:
		return {}
	loaded.emit()
	return st

func _write(data: Dictionary) -> bool:
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(JSON.stringify(data))
	return true

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_PAUSED or what == NOTIFICATION_WM_CLOSE_REQUEST:
		if GameState.running and not GameState.ended:
			save_manual(false)
