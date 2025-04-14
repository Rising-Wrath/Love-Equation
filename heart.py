from manim import *
from manim.opengl import *
import numpy as np

class HeartConfig:
    HEART_COLOR = "#FF4081"
    GLOW_COLOR = "#FF9E80"
    TEXT_COLOR = "#F44336"
    ACCENT_COLOR = "#FF7043"
    HIGHLIGHT_COLOR = "#FFAB40"
    BACKGROUND_COLOR = "#000000"
    
    LIGHT_AXIS_COLOR = "#42A5F5"
    DARK_AXIS_COLOR = "#FFFFFF"
    
    ANIMATION_SPEED = 1.0
    PULSE_INTENSITY = 1.2
    
    AXES_X_LENGTH = 7
    AXES_Y_LENGTH = 5
    HEART_SCALE = 0.8

class HeartEquationIntegrated(Scene):
    def setup(self):
        self.is_paused = False
        self.loop_enabled = False
        self.current_time = 0
        self.total_duration = 0
        self.animations = []
        self.k_tracker = ValueTracker(0.0)
        self.particles = None
        self.heart_points = []
        self.traces = VGroup()
        self.quit_interaction = False

    def on_key_press(self, symbol, modifiers):
        if symbol == ord('p'):
            self.is_paused = not self.is_paused
            print("Playing" if not self.is_paused else "Paused")
        elif symbol == ord('l'):
            self.loop_enabled = not self.loop_enabled
            print(f"Looping: {'On' if self.loop_enabled else 'Off'}")
        elif symbol == ord('r'):
            print("Resetting")
            self.reset_animation()
        elif symbol == ord('q'):
            self.quit_interaction = True
        return True

    def reset_animation(self):
        self.current_time = 0
        self.is_paused = False
        self.k_tracker.set_value(0.0)
        self.clear()
        self.camera.background_color = HeartConfig.BACKGROUND_COLOR
        self.setup_scene()
        self.add_initial_objects()
        self.play_animations()

    def setup_scene(self):
        self.axes = Axes(
            x_range=(-3, 3, 1),
            y_range=(-2.5, 2.5, 1),
            axis_config={"color": HeartConfig.LIGHT_AXIS_COLOR, "include_tip": False},
            x_length=HeartConfig.AXES_X_LENGTH,
            y_length=HeartConfig.AXES_Y_LENGTH
        )
        self.axes.shift(UP * 0.5)
        
        self.x_arrow_pos = Arrow(
            start=self.axes.c2p(2.8, 0),
            end=self.axes.c2p(3.2, 0),
            color=HeartConfig.DARK_AXIS_COLOR,
            buff=0,
            max_stroke_width_to_length_ratio=10
        )
        self.y_arrow_pos = Arrow(
            start=self.axes.c2p(0, 2.3),
            end=self.axes.c2p(0, 2.7),
            color=HeartConfig.DARK_AXIS_COLOR,
            buff=0,
            max_stroke_width_to_length_ratio=10
        )
        self.x_arrow_neg = Arrow(
            start=self.axes.c2p(-2.8, 0),
            end=self.axes.c2p(-3.2, 0),
            color=HeartConfig.DARK_AXIS_COLOR,
            buff=0,
            max_stroke_width_to_length_ratio=10
        )
        self.y_arrow_neg = Arrow(
            start=self.axes.c2p(0, -2.3),
            end=self.axes.c2p(0, -2.7),
            color=HeartConfig.DARK_AXIS_COLOR,
            buff=0,
            max_stroke_width_to_length_ratio=10
        )

        scale_factor = HeartConfig.HEART_SCALE
        
        def get_heart_curve(k_val):
            def heart_param(t):
                x = 2 * np.sin(t)
                y = (
                    np.power(np.abs(x), 2/3) +
                    (0.9 * np.sin(k_val * x) * np.sqrt(3 - x**2) if (3 - x**2) > 0 else 0)
                ) * scale_factor
                return np.array([x, y, 0])
            return ParametricFunction(
                heart_param, t_range=[-PI, PI, 0.01],
                color=HeartConfig.HEART_COLOR, stroke_width=3
            )

        self.heart_graph = always_redraw(lambda: get_heart_curve(self.k_tracker.get_value()))
        self.heart_glow = always_redraw(lambda: get_heart_curve(self.k_tracker.get_value()).set_stroke(
            color=HeartConfig.GLOW_COLOR, width=6, opacity=0.3
        ))
        
        self.heart_points = []
        for i in range(15):
            x = -2 + i * 4 / 14
            y = (
                np.power(np.abs(x), 2/3) +
                (0.9 * np.sin(3.42 * x) * np.sqrt(3 - x**2) if (3 - x**2) > 0 else 0)
            ) * scale_factor
            point = self.axes.c2p(x, y)
            self.heart_points.append(point)
        
        self.particles = VGroup()
        for i in range(15):
            angle = i * TAU / 15
            radius = 1.0
            position = np.array([radius * np.cos(angle), radius * np.sin(angle), 0])
            color = interpolate_color(PINK, ORANGE, i/15)
            particle = Dot(position, radius=0.03, color=color).set_opacity(0.7)
            self.particles.add(particle)
        
        self.stars = VGroup(
            *[Dot(
                point=[np.random.uniform(-7, 7), np.random.uniform(-4, 4), 0],
                radius=np.random.uniform(0.01, 0.03),
                color=RED_E if np.random.random() > 0.5 else PINK
            ).set_opacity(np.random.uniform(0.2, 0.7))
            for _ in range(50)]
        )
        
        self.title = Text("Heart Equation", font_size=32)
        self.title.set_color_by_gradient(PINK, RED, ORANGE)
        self.title.to_edge(UP)
        
        self.equation = MathTex(
            r"y = |x|^{\frac{2}{3}} + 0.9\sin(kx)\sqrt{3-x^2}",
            font_size=32,
        )
        self.equation.set_color_by_gradient(PINK, RED, ORANGE)
        self.equation.to_edge(DOWN).shift(UP * 0.4)
        
        self.k_value_template = DecimalNumber(
            0.0,
            num_decimal_places=2,
            font_size=28,
        )
        self.k_value_template.add_updater(lambda m: m.set_value(self.k_tracker.get_value()))
        self.k_value_template.add_updater(lambda m: m.set_color_by_gradient(PINK, ORANGE))
        def update_k_color(m):
            color = interpolate_color(PINK, ORANGE, self.k_tracker.get_value() / 100)
            for subm in m.submobjects:
                subm.set_color(color)
        self.k_value_template.add_updater(update_k_color)
        
        self.k_label = MathTex("k = ", font_size=28, color=RED)
        self.k_group = VGroup(self.k_label, self.k_value_template).arrange(RIGHT, buff=0.2)
        self.k_group.next_to(self.equation, DOWN, buff=0.2)
        
        self.instructions = Text(
            "P: Play/Pause | L: Loop On/Off | R: Reset | Q: Quit",
            font_size=16,
            color=WHITE
        ).to_edge(DOWN)

    def add_initial_objects(self):
        self.add(
            self.axes, self.x_arrow_pos, self.y_arrow_pos,
            self.x_arrow_neg, self.y_arrow_neg,
            self.stars, self.heart_glow, self.heart_graph,
            self.particles, self.title, self.equation,
            self.k_group, self.instructions, self.traces
        )

    def add_trace(self, k_val):
        if len(self.traces) > 10:
            self.traces.remove(self.traces[0])
        trace = self.axes.plot(
            lambda x: (
                np.power(np.abs(x), 2/3) +
                (0.9 * np.sin(k_val * x) * np.sqrt(3 - x**2) if (3 - x**2) > 0 else 0)
            ) * HeartConfig.HEART_SCALE,
            x_range=[-2, 2, 0.01],
            color=PINK,
            stroke_width=1,
            stroke_opacity=0.2
        )
        self.traces.add(trace)
        return trace

    def pulse_heart(self, intensity=1.2, duration=0.4):
        return AnimationGroup(
            self.heart_graph.animate.set_stroke(width=5*intensity, color=PINK),
            self.heart_glow.animate.set_stroke(width=10*intensity, opacity=0.5),
            run_time=duration
        )

    def get_scatter_points(self, k_val, num_points=15):
        points = []
        for _ in range(num_points):
            x = np.random.uniform(-1.5, 1.5)
            y = (
                np.power(np.abs(x), 2/3) +
                (0.9 * np.sin(k_val * x) * np.sqrt(3 - x**2) if (3 - x**2) > 0 else 0)
            ) * HeartConfig.HEART_SCALE
            points.append(self.axes.c2p(x, y))
        return points

    def play_animations(self):
        self.animations = []
        k_values_to_trace = [10, 25, 50, 75]
        for k_val in k_values_to_trace:
            scatter_points = self.get_scatter_points(k_val)
            self.animations.append((
                AnimationGroup(
                    self.k_tracker.animate.set_value(k_val),
                    *[self.particles[i].animate.move_to(scatter_points[i]) for i in range(len(self.particles))]
                ), 0.8
            ))
            self.animations.append((FadeIn(self.add_trace(k_val)), 0.2))

        self.animations.extend([
            (self.k_tracker.animate.set_value(100), 1.5),
            (FadeIn(self.add_trace(100)), 0.3),
            (AnimationGroup(
                self.k_tracker.animate.set_value(3.42),
                *[self.particles[i].animate.move_to(self.heart_points[i]) for i in range(len(self.particles))]
            ), 1.5, there_and_back_with_pause),
            (self.pulse_heart(1.2, 0.5), 0.5),
            (AnimationGroup(
                self.heart_graph.animate.set_stroke(width=3, color=HeartConfig.HEART_COLOR),
                self.heart_glow.animate.set_stroke(width=6, opacity=0.3)
            ), 0.5),
            (Wait(), 1.0),
        ])

        self.total_duration = sum(run_time for _, run_time, *_ in self.animations)

        for anim, run_time, *rate_func in self.animations:
            if self.quit_interaction:
                break
            if not self.is_paused:
                rate = rate_func[0] if rate_func else smooth
                self.play(anim, run_time=run_time, rate_func=rate)
                self.current_time += run_time
            else:
                self.wait()
            if self.current_time >= self.total_duration and self.loop_enabled:
                self.reset_animation()

    def construct(self):
        self.camera.background_color = HeartConfig.BACKGROUND_COLOR
        self.setup_scene()
        self.add_initial_objects()

        initial_animations = [
            (AnimationGroup(
                Create(self.axes),
                Create(self.x_arrow_pos),
                Create(self.y_arrow_pos),
                Create(self.x_arrow_neg),
                Create(self.y_arrow_neg)
            ), 0.7),
            (FadeIn(self.stars), 0.7),
            (Create(self.heart_glow), 0.7),
            (Create(self.heart_graph), 0.8),
            (FadeIn(self.particles), 0.5),
            (Write(self.title), 0.8),
            (Write(self.equation), 0.7),
            (Write(self.k_group), 0.7),
            (Wait(), 0.5),
            (AnimationGroup(
                *[s.animate.shift(
                    np.random.uniform(-1, 0.1) * UP +
                    np.random.uniform(-0.1, 0.1) * RIGHT
                ) for s in self.stars]
            ), 1.5, there_and_back),
            (FadeIn(self.add_trace(0.0)), 0.3),
            (AnimationGroup(
                self.k_tracker.animate.set_value(3.42),
                *[self.particles[i].animate.move_to(self.heart_points[i]) for i in range(len(self.particles))]
            ), 2.0),
            (FadeIn(self.add_trace(3.42)), 0.3),
            (self.pulse_heart(1.0, 0.4), 0.4),
            (AnimationGroup(
                self.heart_graph.animate.set_stroke(width=3, color=HeartConfig.HEART_COLOR),
                self.heart_glow.animate.set_stroke(width=6, opacity=0.3)
            ), 0.4),
        ]

        for anim, run_time, *rate_func in initial_animations:
            rate = rate_func[0] if rate_func else smooth
            self.play(anim, run_time=run_time, rate_func=rate)

        self.play_animations()
        self.interactive_embed()