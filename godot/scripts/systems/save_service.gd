extends Node
## Placeholder save service. HTML prototype uses localStorage; here use user:// JSON.
const SAVE_PATH := "user://raft_survive_l1.json"
@export var autosave_seconds: float = 60.0
var _acc: float = 0.0

func _process(delta: float) -> void:
	_acc += delta
	if _acc >= autosave_seconds:
		_acc = 0.0
		autosave({})

func save_manual(data: Dictionary) -> bool:
	return _write(data)

func autosave(data: Dictionary) -> bool:
	return _write(data)

func load_save() -> Dictionary:
	if not FileAccess.file_exists(SAVE_PATH):
		return {}
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if typeof(parsed) == TYPE_DICTIONARY else {}

func _write(data: Dictionary) -> bool:
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(JSON.stringify(data))
	return true
