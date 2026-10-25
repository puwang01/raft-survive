extends CanvasLayer
class_name GameHUD

var survival: SurvivalSystem
var level: LevelRoot

@onready var hp_bar: ProgressBar = $Root/Top/Bars/Health/Bar
@onready var hunger_bar: ProgressBar = $Root/Top/Bars/Hunger/Bar
@onready var thirst_bar: ProgressBar = $Root/Top/Bars/Thirst/Bar
@onready var hp_lbl: Label = $Root/Top/Bars/Health/Label
@onready var hunger_lbl: Label = $Root/Top/Bars/Hunger/Label
@onready var thirst_lbl: Label = $Root/Top/Bars/Thirst/Label
@onready var day_lbl: Label = $Root/Top/DayChip/DayText
@onready var obj_lbl: Label = $Root/Top/Objective/ObjText
@onready var toast_lbl: Label = $Root/Toast
@onready var hint_lbl: Label = $Root/Hint
@onready var hurt: ColorRect = $Root/HurtFlash
@onready var inv: HBoxContainer = $Root/Bottom/Inventory
@onready var btn_eat: Button = $Root/Bottom/Actions/Eat
@onready var btn_reel: Button = $Root/Bottom/Actions/Reel
@onready var gameplay_root: Control = $Root/Top
@onready var bottom_root: Control = $Root/Bottom
@onready var root: Control = $Root

var title: ColorRect
var pause_panel: ColorRect
var end_panel: ColorRect
var end_title: Label
var end_msg: Label
var end_stats: Label
var btn_continue: Button
var _toast_t: float = 0.0
var _hint_t: float = 0.0

func _ready() -> void:
	_build_overlays()
	GameState.toast.connect(_on_toast)
	GameState.hint.connect(_on_hint)
	GameState.wood_changed.connect(_on_wood)
	GameState.run_ended.connect(_on_end)
	GameState.run_paused.connect(_on_paused)
	gameplay_root.modulate.a = 0.35
	bottom_root.visible = false
	hurt.mouse_filter = Control.MOUSE_FILTER_IGNORE
	toast_lbl.modulate.a = 0.0
	hint_lbl.modulate.a = 0.0
	_style_bars()
	_build_inventory_slots()
	$Root/Bottom/Actions/Pause.pressed.connect(func(): GameState.set_paused(true))
	btn_reel.pressed.connect(_on_reel)
	btn_eat.pressed.connect(_on_eat)
	_update_day()

func _build_overlays() -> void:
	title = _make_dim("Title")
	var tp := _make_panel(title)
	_add_lbl(tp, "Raft Survive", 28)
	_add_lbl(tp, "第 1 关 · 海上残骸", 18)
	_add_lbl(tp, "拖动瞄准、松手抛钩，打捞 5 块浮木。盯住口渴。避开鲨鱼。", 14, true)
	var start := _add_btn(tp, "开始游戏")
	btn_continue = _add_btn(tp, "继续存档")
	start.pressed.connect(_on_start)
	btn_continue.pressed.connect(_on_continue)
	btn_continue.visible = SaveService.has_save()

	pause_panel = _make_dim("Pause")
	pause_panel.visible = false
	var pp := _make_panel(pause_panel)
	_add_lbl(pp, "暂停", 22)
	_add_btn(pp, "继续游戏").pressed.connect(func(): GameState.set_paused(false))
	_add_btn(pp, "手动存档").pressed.connect(func(): SaveService.save_manual(true))
	_add_btn(pp, "读取存档").pressed.connect(func():
		if level: level.start_from_save()
		GameState.set_paused(false)
	)
	_add_btn(pp, "重开本关").pressed.connect(func():
		pause_panel.visible = false
		if level: level.start_fresh()
	)

	end_panel = _make_dim("End")
	end_panel.visible = false
	var ep := _make_panel(end_panel)
	end_title = _add_lbl(ep, "通关！", 24)
	end_msg = _add_lbl(ep, "", 14, true)
	end_stats = _add_lbl(ep, "", 13)
	_add_btn(ep, "再来一局").pressed.connect(func():
		end_panel.visible = false
		if level: level.start_fresh()
	)
	_add_btn(ep, "回标题").pressed.connect(_on_menu)

func _make_dim(n: String) -> ColorRect:
	var c := ColorRect.new()
	c.name = n
	c.color = Color(0.02, 0.05, 0.1, 0.75)
	c.set_anchors_preset(Control.PRESET_FULL_RECT)
	c.mouse_filter = Control.MOUSE_FILTER_STOP
	root.add_child(c)
	return c

func _make_panel(parent: Control) -> VBoxContainer:
	var pc := PanelContainer.new()
	pc.set_anchors_preset(Control.PRESET_CENTER)
	pc.offset_left = -180
	pc.offset_top = -190
	pc.offset_right = 180
	pc.offset_bottom = 190
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.09, 0.16, 0.26, 0.96)
	sb.border_color = Color(0.55, 0.42, 0.22)
	sb.set_border_width_all(2)
	sb.set_corner_radius_all(16)
	sb.content_margin_left = 18
	sb.content_margin_right = 18
	sb.content_margin_top = 16
	sb.content_margin_bottom = 16
	pc.add_theme_stylebox_override("panel", sb)
	parent.add_child(pc)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 10)
	pc.add_child(vb)
	return vb

func _add_lbl(parent: VBoxContainer, text: String, size: int, wrap: bool = false) -> Label:
	var l := Label.new()
	l.text = text
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.add_theme_font_size_override("font_size", size)
	if wrap:
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	parent.add_child(l)
	return l

func _add_btn(parent: VBoxContainer, text: String) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(0, 46)
	parent.add_child(b)
	return b

func bind(s: SurvivalSystem, lvl: LevelRoot) -> void:
	survival = s
	level = lvl
	survival.health_changed.connect(func(v): _set_bar(hp_bar, hp_lbl, v, "生命"))
	survival.hunger_changed.connect(func(v): _set_bar(hunger_bar, hunger_lbl, v, "饥饿"))
	survival.thirst_changed.connect(func(v): _set_bar(thirst_bar, thirst_lbl, v, "口渴"))
	_set_bar(hp_bar, hp_lbl, survival.health, "生命")
	_set_bar(hunger_bar, hunger_lbl, survival.hunger, "饥饿")
	_set_bar(thirst_bar, thirst_lbl, survival.thirst, "口渴")

func show_gameplay() -> void:
	title.visible = false
	pause_panel.visible = false
	end_panel.visible = false
	gameplay_root.modulate.a = 1.0
	bottom_root.visible = true
	_on_wood(GameState.wood)
	_refresh_inv()

func blocks_world_input() -> bool:
	return title.visible or pause_panel.visible or end_panel.visible

func set_hurt_flash(t: float) -> void:
	hurt.color = Color(0.8, 0.1, 0.1, clampf(t * 0.45, 0.0, 0.45))

func _process(delta: float) -> void:
	if _toast_t > 0.0:
		_toast_t -= delta
		toast_lbl.modulate.a = clampf(_toast_t * 3.0, 0.0, 1.0)
	if _hint_t > 0.0:
		_hint_t -= delta
		hint_lbl.modulate.a = clampf(_hint_t, 0.0, 1.0)
	if GameState.running and not GameState.paused and not GameState.ended:
		_update_day()
		btn_eat.text = "吃喝 (%d)" % (GameState.food + GameState.water)
		btn_eat.disabled = GameState.food + GameState.water <= 0
		btn_reel.disabled = level == null or level.hook.phase == HookController.Phase.IDLE
		_refresh_inv()

func _style_bars() -> void:
	_set_fill(hp_bar, Color(0.9, 0.25, 0.35))
	_set_fill(hunger_bar, Color(0.95, 0.65, 0.2))
	_set_fill(thirst_bar, Color(0.25, 0.7, 0.95))

func _set_fill(bar: ProgressBar, col: Color) -> void:
	var sb := StyleBoxFlat.new()
	sb.bg_color = col
	sb.set_corner_radius_all(6)
	bar.add_theme_stylebox_override("fill", sb)
	var bg := StyleBoxFlat.new()
	bg.bg_color = Color(0.05, 0.1, 0.18, 0.7)
	bg.set_corner_radius_all(6)
	bar.add_theme_stylebox_override("background", bg)
	bar.show_percentage = false
	bar.max_value = 100

func _set_bar(bar: ProgressBar, lbl: Label, v: float, title_txt: String) -> void:
	bar.value = v
	lbl.text = "%s  %d" % [title_txt, int(round(v))]
	bar.modulate = Color(1.3, 0.8, 0.8) if v < 25.0 else Color.WHITE

func _update_day() -> void:
	var t := 8.0 * 60.0 + GameState.play_time
	var hh := int(t / 60.0) % 24
	var mm := int(t) % 60
	day_lbl.text = "DAY 1   %02d:%02d   晴" % [hh, mm]
	var m := int(GameState.time_left) / 60
	var s := int(GameState.time_left) % 60
	obj_lbl.text = "目标  收集浮木  %d/%d    ⏱ %d:%02d" % [GameState.wood, GameState.WIN_WOOD, m, s]

func _on_wood(_c: int) -> void:
	_update_day()
	obj_lbl.modulate = Color(0.5, 1.0, 0.6) if GameState.wood >= GameState.WIN_WOOD else Color.WHITE

func _on_toast(msg: String, dur: float) -> void:
	toast_lbl.text = msg
	_toast_t = dur

func _on_hint(msg: String, dur: float) -> void:
	hint_lbl.text = msg
	_hint_t = dur

func _on_end(won: bool, message: String) -> void:
	end_panel.visible = true
	bottom_root.visible = false
	end_title.text = "通关！" if won else "失败"
	end_msg.text = message
	end_stats.text = "用时 %s · 浮木 %d/%d\n打捞 %d 次 · 生命 %d" % [
		"%d:%02d" % [int(GameState.play_time) / 60, int(GameState.play_time) % 60],
		GameState.wood, GameState.WIN_WOOD, GameState.hooked_count,
		int(survival.health) if survival else 0,
	]

func _on_paused(p: bool) -> void:
	pause_panel.visible = p

func _on_menu() -> void:
	end_panel.visible = false
	title.visible = true
	bottom_root.visible = false
	gameplay_root.modulate.a = 0.35
	btn_continue.visible = SaveService.has_save()
	GameState.running = false

func _build_inventory_slots() -> void:
	for c in inv.get_children():
		c.queue_free()
	for i in 8:
		var slot := PanelContainer.new()
		slot.custom_minimum_size = Vector2(52, 52)
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(0.08, 0.16, 0.28, 0.85)
		sb.border_color = Color(0.55, 0.4, 0.22)
		sb.set_border_width_all(2)
		sb.set_corner_radius_all(8)
		slot.add_theme_stylebox_override("panel", sb)
		var tex := TextureRect.new()
		tex.name = "Icon"
		tex.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tex.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		tex.custom_minimum_size = Vector2(40, 40)
		slot.add_child(tex)
		inv.add_child(slot)

func _refresh_inv() -> void:
	var icons := [
		"res://assets/art/hook.png",
		"res://assets/art/debris_wood.png",
		"res://assets/art/debris_bottle.png",
		"res://assets/art/debris_fish.png",
	]
	var counts := [1, GameState.wood, GameState.water, GameState.food]
	for i in inv.get_child_count():
		var slot: PanelContainer = inv.get_child(i)
		var icon: TextureRect = slot.get_node("Icon")
		if i < icons.size() and counts[i] > 0:
			icon.texture = load(icons[i])
			icon.modulate = Color.WHITE
		else:
			icon.texture = null


func _on_reel() -> void:
	if level:
		level.reel_hook()

func _on_eat() -> void:
	if level:
		level.consume_eat()

func _on_start() -> void:
	if level:
		level.start_fresh()

func _on_continue() -> void:
	if level:
		level.start_from_save()
