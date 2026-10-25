extends Node2D
class_name LevelRoot
## Level 1 — ocean raft survival vertical slice.

const WORLD := Vector2(900, 1400)
const DebrisScript = preload("res://scripts/systems/debris.gd")

@onready var water: ColorRect = $World/Water
@onready var sky: Sprite2D = $Parallax/Sky
@onready var raft: Node2D = $World/Raft
@onready var player: Sprite2D = $World/Raft/Player
@onready var hook: HookController = $World/Raft/HookController
@onready var debris_root: Node2D = $World/DebrisRoot
@onready var shark: Shark = $World/Shark
@onready var camera: Camera2D = $Camera2D
@onready var survival: SurvivalSystem = $SurvivalSystem
@onready var hud: CanvasLayer = $HUD
@onready var coral_a: Sprite2D = $World/CoralA
@onready var coral_b: Sprite2D = $World/CoralB

var _spawn_acc: float = 0.0
var _hurt_flash: float = 0.0
var _touch_id: int = -1
var _cloud_sprites: Array[Sprite2D] = []

func _ready() -> void:
	add_to_group("level_root")
	raft.add_to_group("raft")
	_setup_water_shader()
	_setup_raft_props()
	_setup_clouds()
	coral_a.texture = load("res://assets/art/coral.png")
	coral_b.texture = load("res://assets/art/coral.png")
	coral_a.modulate = Color(1, 1, 1, 0.55)
	coral_b.modulate = Color(1, 1, 1, 0.4)
	coral_a.position = Vector2(220, 980)
	coral_b.position = Vector2(680, 520)
	sky.texture = load("res://assets/art/sky.png")
	sky.centered = false
	sky.position = Vector2(0, -80)
	sky.scale = Vector2(WORLD.x / 720.0 * 1.1, 1.15)
	player.texture = load("res://assets/art/player.png")
	player.position = Vector2(8, -18)
	player.scale = Vector2(0.55, 0.55)
	shark.raft_path = shark.get_path_to(raft)
	shark.position = Vector2(200, 200)
	shark.bit_raft.connect(_on_shark_bite)
	hook.loot_retrieved.connect(_on_loot)
	survival.died.connect(_on_died)
	GameState.run_ended.connect(_on_run_ended)
	# Idle preview debris
	_ensure_debris(true)
	camera.position = raft.position
	if hud.has_method("bind"):
		hud.bind(survival, self)

func _setup_water_shader() -> void:
	var mat := ShaderMaterial.new()
	mat.shader = load("res://assets/shaders/water.gdshader")
	water.material = mat
	water.size = WORLD
	water.position = Vector2.ZERO
	water.color = Color(0.15, 0.55, 0.65, 1)

func _setup_raft_props() -> void:
	var raft_sprite: Sprite2D = raft.get_node("RaftSprite")
	raft_sprite.texture = load("res://assets/art/raft.png")
	raft_sprite.centered = true
	for item in [
		["Sail", "res://assets/art/sail.png", Vector2(-20, -70), Vector2(0.7, 0.7)],
		["Grill", "res://assets/art/grill.png", Vector2(48, 10), Vector2(0.7, 0.7)],
		["Chest", "res://assets/art/chest.png", Vector2(-50, 28), Vector2(0.75, 0.75)],
		["Purifier", "res://assets/art/purifier.png", Vector2(40, -36), Vector2(0.65, 0.65)],
		["Bed", "res://assets/art/bed.png", Vector2(-10, 40), Vector2(0.7, 0.7)],
	]:
		var s := Sprite2D.new()
		s.name = item[0]
		s.texture = load(item[1])
		s.position = item[2]
		s.scale = item[3]
		s.centered = true
		raft.add_child(s)
	# gentle raft bob
	var tw := create_tween().set_loops()
	tw.tween_property(raft, "position:y", raft.position.y + 4.0, 1.6).set_ease(Tween.EASE_IN_OUT).set_trans(Tween.TRANS_SINE)
	tw.tween_property(raft, "position:y", raft.position.y - 4.0, 1.6).set_ease(Tween.EASE_IN_OUT).set_trans(Tween.TRANS_SINE)

func _setup_clouds() -> void:
	var tex: Texture2D = load("res://assets/art/cloud.png")
	for i in 3:
		var c := Sprite2D.new()
		c.texture = tex
		c.modulate = Color(1, 1, 1, 0.75)
		c.position = Vector2(120 + i * 280, 40 + i * 30)
		c.scale = Vector2(0.9 + i * 0.1, 0.9)
		$Parallax.add_child(c)
		_cloud_sprites.append(c)

func start_fresh() -> void:
	GameState.reset_run()
	survival.reset_stats()
	survival.active = true
	_clear_debris()
	_ensure_debris(true)
	for i in 3:
		_spawn_debris(DebrisScript.Kind.WOOD)
	raft.position = WORLD * 0.5
	shark.position = Vector2(180, 240)
	shark.aggro = 0.0
	hook.phase = HookController.Phase.IDLE
	hook.target = null
	SaveService.enable_autosave(true)
	GameState.start_run()
	GameState.show_hint("按住拖动瞄准，松手抛钩 · 打捞 5 块浮木", 3.8)
	if hud.has_method("show_gameplay"):
		hud.show_gameplay()

func start_from_save() -> void:
	var data := SaveService.load_save()
	if data.is_empty():
		GameState.show_toast("没有存档")
		return
	GameState.reset_run()
	GameState.wood = int(data.get("wood", 0))
	GameState.food = int(data.get("food", 0))
	GameState.water = int(data.get("water", 0))
	GameState.time_left = float(data.get("time_left", GameState.LEVEL_TIME))
	GameState.play_time = float(data.get("play_time", 0.0))
	GameState.hooked_count = int(data.get("hooked_count", 0))
	GameState.wood_changed.emit(GameState.wood)
	survival.import_data(data)
	survival.active = true
	_clear_debris()
	var debris_data: Array = data.get("debris", [])
	if debris_data.is_empty():
		_ensure_debris(true)
	else:
		for d in debris_data:
			_spawn_from_dict(d)
	if data.has("raft"):
		var r: Dictionary = data["raft"]
		raft.position = Vector2(float(r.get("x", WORLD.x * 0.5)), float(r.get("y", WORLD.y * 0.5)))
	if data.has("shark"):
		var s: Dictionary = data["shark"]
		shark.position = Vector2(float(s.get("x", 200)), float(s.get("y", 200)))
		shark.aggro = float(s.get("aggro", 0))
	hook.phase = HookController.Phase.IDLE
	SaveService.enable_autosave(true)
	GameState.start_run()
	GameState.show_hint("已读取存档，继续求生", 2.5)
	GameState.show_toast("已读取存档")
	if hud.has_method("show_gameplay"):
		hud.show_gameplay()

func export_save() -> Dictionary:
	var debris_arr: Array = []
	for d in debris_root.get_children():
		if d is Debris and not d.hooked:
			debris_arr.append({
				"type": d.loot_label(),
				"x": d.position.x, "y": d.position.y,
				"vx": d.velocity.x, "vy": d.velocity.y,
			})
	var data := survival.export_data()
	data.merge({
		"wood": GameState.wood,
		"food": GameState.food,
		"water": GameState.water,
		"time_left": GameState.time_left,
		"play_time": GameState.play_time,
		"hooked_count": GameState.hooked_count,
		"raft": {"x": raft.position.x, "y": raft.position.y},
		"shark": {"x": shark.position.x, "y": shark.position.y, "aggro": shark.aggro},
		"debris": debris_arr,
	})
	return data

func _process(delta: float) -> void:
	# clouds drift
	for i in _cloud_sprites.size():
		_cloud_sprites[i].position.x += (8.0 + i * 4.0) * delta
		if _cloud_sprites[i].position.x > WORLD.x + 100:
			_cloud_sprites[i].position.x = -120
	camera.position = camera.position.lerp(raft.position, 1.0 - pow(0.001, delta))
	if _hurt_flash > 0.0:
		_hurt_flash -= delta
		if hud.has_method("set_hurt_flash"):
			hud.set_hurt_flash(_hurt_flash)
	if not GameState.running or GameState.paused or GameState.ended:
		return
	GameState.play_time += delta
	GameState.time_left = maxf(0.0, GameState.time_left - delta)
	_spawn_acc += delta
	if _spawn_acc > 2.8:
		_spawn_acc = 0.0
		_ensure_debris(false)
	if GameState.time_left <= 0.0 and GameState.wood < GameState.WIN_WOOD:
		GameState.lose("时间耗尽，救援未至…")

func _unhandled_input(event: InputEvent) -> void:
	if hud and hud.has_method("blocks_world_input") and hud.blocks_world_input():
		return
	if event is InputEventScreenTouch:
		var st := event as InputEventScreenTouch
		if st.pressed:
			_touch_id = st.index
			hook.begin_aim(_screen_to_world(st.position))
		elif st.index == _touch_id:
			hook.release_aim()
			_touch_id = -1
	elif event is InputEventScreenDrag:
		var sd := event as InputEventScreenDrag
		if sd.index == _touch_id:
			hook.update_aim(_screen_to_world(sd.position))
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if event.pressed:
			hook.begin_aim(_screen_to_world(event.position))
		else:
			hook.release_aim()
	elif event is InputEventMouseMotion and Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
		hook.update_aim(_screen_to_world(event.position))

func _screen_to_world(screen_pos: Vector2) -> Vector2:
	var canvas_xform := get_viewport().get_canvas_transform()
	return canvas_xform.affine_inverse() * screen_pos

func _ensure_debris(force_min: bool) -> void:
	var count := 0
	for d in debris_root.get_children():
		if d is Debris and not d.hooked:
			count += 1
	var target := 8 if force_min else 10
	while count < target:
		_spawn_debris()
		count += 1

func _spawn_debris(forced: int = -1) -> void:
	var kinds := [
		DebrisScript.Kind.WOOD, DebrisScript.Kind.WOOD, DebrisScript.Kind.WOOD,
		DebrisScript.Kind.BARREL, DebrisScript.Kind.CRATE, DebrisScript.Kind.FISH, DebrisScript.Kind.BOTTLE,
	]
	var k: int = forced if forced >= 0 else kinds[randi() % kinds.size()]
	var angle := randf() * TAU
	var dist := 180.0 + randf() * 320.0
	var pos := raft.position + Vector2(cos(angle), sin(angle)) * dist
	pos.x = clampf(pos.x, 40, WORLD.x - 40)
	pos.y = clampf(pos.y, 40, WORLD.y - 40)
	var vel := Vector2(randf() - 0.5, randf() - 0.5) * (12.0 + randf() * 22.0)
	var node := Area2D.new()
	node.set_script(DebrisScript)
	var spr := Sprite2D.new()
	spr.name = "Sprite2D"
	node.add_child(spr)
	var cs := CollisionShape2D.new()
	cs.name = "CollisionShape2D"
	node.add_child(cs)
	debris_root.add_child(node)
	node.setup(k, pos, vel)

func _spawn_from_dict(d: Dictionary) -> void:
	var map := {
		"wood": DebrisScript.Kind.WOOD, "barrel": DebrisScript.Kind.BARREL,
		"crate": DebrisScript.Kind.CRATE, "fish": DebrisScript.Kind.FISH, "bottle": DebrisScript.Kind.BOTTLE,
	}
	var k: int = map.get(str(d.get("type", "wood")), DebrisScript.Kind.WOOD)
	var node := Area2D.new()
	node.set_script(DebrisScript)
	var spr := Sprite2D.new()
	spr.name = "Sprite2D"
	node.add_child(spr)
	var cs := CollisionShape2D.new()
	cs.name = "CollisionShape2D"
	node.add_child(cs)
	debris_root.add_child(node)
	node.setup(k, Vector2(float(d.get("x", 100)), float(d.get("y", 100))), Vector2(float(d.get("vx", 0)), float(d.get("vy", 0))))

func _clear_debris() -> void:
	for c in debris_root.get_children():
		c.queue_free()

func _on_loot(kind_name: String) -> void:
	GameState.hooked_count += 1
	match kind_name:
		"wood":
			GameState.add_wood(1)
			GameState.show_toast("浮木 %d/%d" % [GameState.wood, GameState.WIN_WOOD])
			if GameState.wood >= GameState.WIN_WOOD:
				GameState.win("收集到足够浮木，加固了木筏！")
		"barrel", "bottle":
			GameState.water += 1
			GameState.show_toast("获得淡水")
		"crate", "fish":
			GameState.food += 1
			GameState.show_toast("钓到鱼！" if kind_name == "fish" else "获得食物")

func _on_shark_bite(amount: float) -> void:
	survival.hurt(amount)
	_hurt_flash = 0.35
	GameState.show_toast("鲨鱼撞击！")
	var away := (raft.position - shark.position).normalized()
	raft.position += away * -12.0

func _on_died(reason: String) -> void:
	GameState.lose(reason)

func _on_run_ended(_won: bool, _msg: String) -> void:
	SaveService.enable_autosave(false)
	if _won:
		SaveService.save_manual(false)

func consume_eat() -> void:
	if GameState.ended or not GameState.running:
		return
	if GameState.food <= 0 and GameState.water <= 0:
		GameState.show_toast("没有食物或淡水")
		return
	if survival.thirst <= survival.hunger and GameState.water > 0:
		GameState.water -= 1
		survival.drink(40.0)
		GameState.show_toast("喝了淡水 +口渴")
	elif GameState.food > 0:
		GameState.food -= 1
		survival.eat(35.0)
		GameState.show_toast("吃了食物 +饥饿")
	elif GameState.water > 0:
		GameState.water -= 1
		survival.drink(40.0)
		GameState.show_toast("喝了淡水 +口渴")

func reel_hook() -> void:
	hook.reel(true)
