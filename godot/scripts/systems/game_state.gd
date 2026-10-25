extends Node
## Global run flags / signals for Level 1.

signal run_started
signal run_paused(paused: bool)
signal run_ended(won: bool, message: String)
signal wood_changed(count: int)
signal toast(message: String, duration: float)
signal hint(message: String, duration: float)

const WIN_WOOD := 5
const LEVEL_TIME := 240.0

var running: bool = false
var paused: bool = false
var ended: bool = false
var wood: int = 0
var food: int = 1
var water: int = 1
var time_left: float = LEVEL_TIME
var play_time: float = 0.0
var hooked_count: int = 0

func reset_run() -> void:
	running = false
	paused = false
	ended = false
	wood = 0
	food = 1
	water = 1
	time_left = LEVEL_TIME
	play_time = 0.0
	hooked_count = 0
	wood_changed.emit(wood)

func start_run() -> void:
	running = true
	paused = false
	ended = false
	run_started.emit()

func set_paused(p: bool) -> void:
	if ended or not running:
		return
	paused = p
	run_paused.emit(p)

func add_wood(n: int = 1) -> void:
	wood += n
	wood_changed.emit(wood)

func win(msg: String) -> void:
	if ended:
		return
	ended = true
	running = false
	run_ended.emit(true, msg)

func lose(msg: String) -> void:
	if ended:
		return
	ended = true
	running = false
	run_ended.emit(false, msg)

func show_toast(msg: String, dur: float = 1.6) -> void:
	toast.emit(msg, dur)

func show_hint(msg: String, dur: float = 3.5) -> void:
	hint.emit(msg, dur)
