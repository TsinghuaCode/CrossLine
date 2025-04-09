import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from copy import deepcopy
import threading
import queue
import time

class ModernVisualizer(tk.Tk):
    def __init__(self):
        """
        初始化 ModernVisualizer 类的实例。
        设置窗口的基本属性，如标题、大小和背景颜色，
        初始化样式、控件、状态变量，并设置窗口关闭协议。
        """
        super().__init__()
        
        # 设置窗口
        self.title("Line Matching Visualizer")
        self.geometry("900x900")  # 稍微增加高度以适应新模式
        self.configure(bg='#f5f6fa')
        
        # 颜色方案，用于绘制不同的线路
        self.colors = ['#e74c3c', '#2ecc71', '#3498db', '#f1c40f',
                      '#9b59b6', '#1abc9c', '#e67e22', '#34495e',
                      '#2c3e50', '#7f8c8d']
        
        self.create_styles()
        self.create_widgets()
        
        # 初始化状态变量
        self.pair_frames = []  # 存储线路对输入框的框架列表
        self.running = False  # 标记搜索是否正在运行
        self.paused = False  # 标记搜索是否暂停
        self.current_step = 0  # 当前搜索步骤
        self.search_thread = None  # 搜索线程对象
        self.queue = queue.Queue()  # 用于线程间通信的队列
        self.delay = 0.1  # 动画延迟时间
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_styles(self):
        """
        创建并配置 ttk 控件的样式。
        包括主框架、标题、按钮、输入框、标签和状态栏的样式。
        """
        style = ttk.Style()
        style.theme_use('clam')
        
        # 主框架样式
        style.configure('Main.TFrame', background='#f5f6fa')
        
        # 标题样式
        style.configure('Title.TLabel', 
                      font=('Helvetica', 18, 'bold'),
                      foreground='#2c3e50',
                      background='#f5f6fa')
        
        # 按钮样式
        style.configure('Primary.TButton', 
                       font=('Arial', 10, 'bold'),
                       borderwidth=0,
                       foreground='white',
                       background='#3498db',
                       padding=10)
        style.map('Primary.TButton',
                background=[('active', '#2980b9'), ('pressed', '#2471a3')])
        
        style.configure('Success.TButton', 
                       background='#2ecc71',
                       padding=10)
        style.map('Success.TButton',
                background=[('active', '#27ae60'), ('pressed', '#219a52')])
        
        # 输入框样式
        style.configure('Modern.TEntry',
                      bordercolor='#bdc3c7',
                      lightcolor='#ecf0f1',
                      darkcolor='#bdc3c7',
                      padding=5,
                      relief='flat')
        
        # 标签样式
        style.configure('Bold.TLabel',
                      font=('Arial', 10, 'bold'),
                      foreground='#34495e',
                      background='#f5f6fa')
        
        # 状态栏样式
        style.configure('Status.TFrame',
                      background='#2c3e50')
        style.configure('Status.TLabel',
                      font=('Arial', 9),
                      foreground='#ecf0f1',
                      background='#2c3e50')

    def create_widgets(self):
        """
        创建并布局窗口中的所有控件。
        包括主容器、标题、输入区域、控制区域、画布和状态栏。
        """
        # 主容器
        self.main_container = ttk.Frame(self, style='Main.TFrame')
        self.main_container.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # 标题
        title = ttk.Label(self.main_container, 
                         text="LINE MATCHING VISUALIZER",
                         style='Title.TLabel')
        title.pack(pady=(0, 20))
        
        # 输入区域
        self.create_input_section()
        
        # 控制区域
        self.create_control_section()
        
        # 画布
        self.create_canvas()
        
        # 状态栏
        self.create_status_bar()

    def create_input_section(self):
        """
        创建输入区域的控件。
        包括网格设置输入框、模式选择按钮、线路对输入框和应用设置按钮。
        """
        input_frame = ttk.Frame(self.main_container)
        input_frame.pack(fill=tk.X, pady=10)
        
        # 网格设置
        settings_frame = ttk.Frame(input_frame)
        settings_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(settings_frame, text="Grid Settings", style='Bold.TLabel').pack(anchor=tk.W)
        
        # 输入控件容器
        grid_frame = ttk.Frame(settings_frame)
        grid_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(grid_frame, text="Size (n):", style='Bold.TLabel').pack(side=tk.LEFT, padx=5)
        self.n_entry = ttk.Entry(grid_frame, width=8, style='Modern.TEntry')
        self.n_entry.pack(side=tk.LEFT, padx=5)
        self.n_entry.insert(0, "4")
        
        ttk.Label(grid_frame, text="Pairs (m):", style='Bold.TLabel').pack(side=tk.LEFT, padx=10)
        self.m_entry = ttk.Entry(grid_frame, width=8, style='Modern.TEntry')
        self.m_entry.pack(side=tk.LEFT, padx=5)
        self.m_entry.insert(0, "2")
        
        # 模式选择
        mode_frame = ttk.Frame(grid_frame)
        mode_frame.pack(side=tk.LEFT, padx=15)
        self.mode_var = tk.StringVar(value="mode1")
        ttk.Radiobutton(mode_frame, text="Mode 1", variable=self.mode_var, 
                       value="mode1").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Mode 2", variable=self.mode_var,
                       value="mode2").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(grid_frame, text="Apply Settings", 
                 command=self.confirm_input, 
                 style='Success.TButton').pack(side=tk.LEFT, padx=15)
        
        # 坐标输入区域
        self.pairs_frame = ttk.Frame(self.main_container)
        self.pairs_frame.pack(fill=tk.X, pady=10)

    def create_control_section(self):
        """
        创建控制区域的控件。
        包括开始、暂停、重置按钮和动画速度滑块。
        """
        control_frame = ttk.Frame(self.main_container)
        control_frame.pack(fill=tk.X, pady=15)
        
        # 按钮容器
        btn_container = ttk.Frame(control_frame)
        btn_container.pack(expand=True)
        
        self.start_btn = ttk.Button(btn_container, text="Start", 
                                  command=self.start_search, 
                                  style='Primary.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=8)
        
        self.pause_btn = ttk.Button(btn_container, text="Pause", 
                                  command=self.toggle_pause, 
                                  style='Primary.TButton')
        self.pause_btn.pack(side=tk.LEFT, padx=8)
        
        self.reset_btn = ttk.Button(btn_container, text="Reset", 
                                  command=self.reset, 
                                  style='Primary.TButton')
        self.reset_btn.pack(side=tk.LEFT, padx=8)
        
        # 速度控制
        speed_frame = ttk.Frame(control_frame)
        speed_frame.pack(fill=tk.X, padx=50, pady=10)
        
        ttk.Label(speed_frame, text="Animation Speed:", style='Bold.TLabel').pack(side=tk.LEFT)
        self.speed_scale = ttk.Scale(speed_frame, from_=1, to=100, 
                                   orient=tk.HORIZONTAL, command=self.update_speed)
        self.speed_scale.set(50)
        self.speed_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10)

    def create_canvas(self):
        """
        创建用于绘制网格和线路的画布。
        """
        canvas_container = ttk.Frame(self.main_container)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_container, bg='white', bd=0, highlightthickness=0)
        self.canvas.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    def create_status_bar(self):
        """
        创建状态栏，显示当前搜索步骤和路径成本。
        """
        self.status_frame = ttk.Frame(self.main_container, style='Status.TFrame')
        self.status_frame.pack(fill=tk.X, pady=(10,0))
        
        self.step_var = tk.StringVar(value="Step: 0")
        self.cost_var = tk.StringVar(value="Path Cost: 0")
        
        ttk.Label(self.status_frame, textvariable=self.step_var, 
                 style='Status.TLabel').pack(side=tk.LEFT, padx=15)
        ttk.Label(self.status_frame, textvariable=self.cost_var, 
                 style='Status.TLabel').pack(side=tk.RIGHT, padx=15)

    def confirm_input(self):
        """
        确认用户输入的网格大小和线路对数量。
        验证输入的合法性，清除现有线路对输入框，创建新的输入框，
        调整画布大小，并启用控制按钮。
        """
        try:
            n = int(self.n_entry.get())
            m = int(self.m_entry.get())
            
            if n < 2 or n > 10:
                raise ValueError("Grid size must be between 2 and 10")
            if m < 1 or m > 10:
                raise ValueError("Number of pairs must be between 1 and 10")
            
            # 清除现有的对输入框
            for frame in self.pair_frames:
                frame.destroy()
            self.pair_frames = []
            
            # 创建新的对输入框
            for i in range(m):
                self.create_pair_input(i)
            
            # 调整画布大小
            cell_size = min(400 // n, 60)
            canvas_size = n * cell_size
            self.canvas.config(width=canvas_size, height=canvas_size)
            
            # 启用控制按钮
            self.start_btn.config(state=tk.NORMAL)
            self.reset_btn.config(state=tk.NORMAL)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def create_pair_input(self, index):
        """
        创建一个线路对的输入框。
        包括起点和终点的行、列输入框。
        :param index: 线路对的索引
        :return: 起点行、起点列、终点行、终点列的输入框对象
        """
        frame = ttk.Frame(self.pairs_frame, style='Modern.TFrame')
        frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text=f"Pair {index + 1}", 
                 style='Modern.TLabel').pack(side=tk.LEFT, padx=5)
        
        # 起点输入
        start_frame = ttk.Frame(frame)
        start_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(start_frame, text="Start:", 
                 style='Modern.TLabel').pack(side=tk.LEFT)
        start_row = ttk.Entry(start_frame, width=5)
        start_row.pack(side=tk.LEFT, padx=2)
        start_col = ttk.Entry(start_frame, width=5)
        start_col.pack(side=tk.LEFT, padx=2)
        
        # 终点输入
        end_frame = ttk.Frame(frame)
        end_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(end_frame, text="End:", 
                 style='Modern.TLabel').pack(side=tk.LEFT)
        end_row = ttk.Entry(end_frame, width=5)
        end_row.pack(side=tk.LEFT, padx=2)
        end_col = ttk.Entry(end_frame, width=5)
        end_col.pack(side=tk.LEFT, padx=2)
        
        self.pair_frames.append(frame)
        return start_row, start_col, end_row, end_col

    def update_speed(self, value):
        """
        根据速度滑块的值更新动画延迟时间。
        :param value: 速度滑块的值
        """
        self.delay = (100 - float(value)) / 100

    def toggle_pause(self):
        """
        切换搜索的暂停和继续状态。
        更新暂停按钮的文本。
        """
        self.paused = not self.paused
        self.pause_btn.config(text="Resume" if self.paused else "Pause")

    def reset(self):
        """
        重置搜索状态。
        停止搜索线程，清空队列，重置状态变量，
        重绘画布为初始状态。
        """
        if self.running:
            self.running = False
            if self.search_thread and self.search_thread.is_alive():
                self.search_thread.join()
        
        # 清空队列
        with self.queue.mutex:
            self.queue.queue.clear()
        
        self.current_step = 0
        self.step_var.set("Step: 0")
        self.cost_var.set("Path Cost: 0")
        self.paused = False
        self.pause_btn.config(text="Pause", state=tk.DISABLED)
        self.start_btn.config(state=tk.NORMAL)
        self.last_node = None  # 新增状态重置
        
        # 重绘画布
        self.draw_initial_state()

    def start_search(self):
        """
        开始搜索过程。
        获取用户输入，验证其合法性，清空队列，
        设置问题并启动搜索线程，开始处理队列中的节点。
        """
        try:
            # 获取输入并验证
            n = int(self.n_entry.get())
            init_state = self.get_initial_state()
            
            # 清空之前的队列数据
            with self.queue.mutex:
                self.queue.queue.clear()
            
            # 设置问题并开始搜索（新增模式参数）
            self.problem = MatchProblem(
                n, 
                init_state, 
                h_function=h_function_method1, 
                path_cost=int(self.m_entry.get()),
                mode=self.mode_var.get()  # 新增模式参数
            )
            
            self.running = True
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            
            self.search_thread = threading.Thread(target=self.run_search)
            self.search_thread.start()
            
            self.after(100, self.process_queue)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def get_initial_state(self):
        """
        获取初始状态。
        从用户输入的线路对坐标创建网格和线路列表，
        找到第一个未完成的线路作为活动线路。
        :return: 初始状态列表，包含网格、线路列表和活动线路索引
        """
        n = int(self.n_entry.get())
        grid = [[0 for _ in range(n)] for _ in range(n)]
        lines = []
        for i, frame in enumerate(self.pair_frames):
            entries = frame.winfo_children()
            start_row = int(entries[1].winfo_children()[1].get()) - 1
            start_col = int(entries[1].winfo_children()[2].get()) - 1
            end_row = int(entries[2].winfo_children()[1].get()) - 1
            end_col = int(entries[2].winfo_children()[2].get()) - 1
            
            if not (0 <= start_row < n and 0 <= start_col < n and 
                   0 <= end_row < n and 0 <= end_col < n):
                raise ValueError(f"Invalid coordinates for pair {i+1}")
            
            lines.append([[start_row, start_col], [end_row, end_col]])
            grid[start_row][start_col] = i + 1
            grid[end_row][end_col] = i + 1
        
        # 找到第一个未完成的线路作为active_line
        active_line = None
        for idx, (start, end) in enumerate(lines):
            if start != end:
                active_line = idx
                break
        return [grid, lines, active_line]

    def run_search(self):
        """
        运行搜索过程。
        使用搜索生成器生成节点，将节点放入队列，
        根据暂停状态和延迟时间控制节点的生成速度。
        搜索结束后，将 None 放入队列表示结束。
        """
        gen = search_generator(self.problem)
        for node in gen:
            while self.paused and self.running:
                time.sleep(0.1)
            if not self.running:
                break
            self.queue.put(node)
            time.sleep(self.delay)
        self.queue.put(None)

    def process_queue(self):
        """
        处理队列中的节点。
        从队列中获取节点，更新状态信息，绘制节点状态，
        直到队列为空或搜索结束。
        """
        try:
            while True:
                node = self.queue.get_nowait()
                if node is None:
                    self.running = False
                    self.pause_btn.config(state=tk.DISABLED)
                    # 添加对last_node的存在性检查
                    if self.last_node and self.problem.is_goal(self.last_node.state):
                        messagebox.showinfo("Success", "Solution found!")
                    else:
                        messagebox.showinfo("Info", "No solution found.")
                    break
                
                self.last_node = node
                self.current_step += 1
                self.step_var.set(f"Step: {self.current_step}")
                self.cost_var.set(f"Path Cost: {node.path_cost:.2f}")
                self.draw_state(node.state)
                
        except queue.Empty:
            pass
        
        if self.running:
            self.after(100, self.process_queue)

    def draw_state(self, state):
        """
        绘制当前状态的网格和线路。
        清空画布，绘制网格、线路的起点、终点和连接线。
        :param state: 当前状态列表，包含网格、线路列表和活动线路索引
        """
        self.canvas.delete("all")
        n = len(state[0])
        cell_size = min(int(self.canvas.winfo_width() / n), 60)
        
        # 绘制网格
        for i in range(n):
            for j in range(n):
                x, y = j * cell_size, i * cell_size
                value = state[0][i][j]
                color = self.colors[value-1] if value > 0 else '#ffffff'
                self.canvas.create_rectangle(
                    x, y, x + cell_size, y + cell_size,
                    fill=color, outline='#ecf0f1', width=2
                )
        
        # 绘制连接线和端点
        for idx, (start, end) in enumerate(state[1]):
            color = self.colors[idx]
            
            # 起点
            sx = start[1] * cell_size + cell_size/2
            sy = start[0] * cell_size + cell_size/2
            self.canvas.create_oval(
                sx-10, sy-10, sx+10, sy+10,
                fill=color, outline='#2c3e50', width=2
            )
            
            # 终点
            ex = end[1] * cell_size + cell_size/2
            ey = end[0] * cell_size + cell_size/2
            self.canvas.create_rectangle(
                ex-10, ey-10, ex+10, ey+10,
                outline=color, width=2, fill='white'
            )
            
            # 路径线
            if start != end:
                self.canvas.create_line(
                    sx, sy, ex, ey,
                    fill=color, width=3, capstyle=tk.ROUND,
                    dash=(6,4) if idx % 2 == 0 else (4,2)
                )

    def draw_initial_state(self):
        """
        绘制初始状态。
        尝试获取初始状态并绘制，如果输入无效则忽略。
        """
        try:
            init_state = self.get_initial_state()
            self.draw_state(init_state)
        except ValueError:
            pass

    def on_close(self):
        """
        处理窗口关闭事件。
        停止搜索线程，销毁窗口。
        """
        self.running = False
        if self.search_thread and self.search_thread.is_alive():
            self.search_thread.join()
        self.destroy()

class PriorityQueue:
    def __init__(self, initial=None):
        """
        初始化优先队列。
        :param initial: 初始元素
        """
        self.elements = []
        if initial:
            self.push(initial)

    def empty(self):
        """
        判断队列是否为空。
        :return: 队列为空返回 True，否则返回 False
        """
        return len(self.elements) == 0

    def push(self, item):
        """
        向队列中添加元素，并按路径成本排序。
        :param item: 要添加的元素
        """
        self.elements.append(item)
        self.elements.sort(key=lambda x: x.path_cost)

    def pop(self):
        """
        从队列中移除并返回路径成本最小的元素。
        :return: 路径成本最小的元素
        """
        return self.elements.pop(0)

    def find(self, item):
        """
        查找元素在队列中的索引。
        :param item: 要查找的元素
        :return: 元素的索引，如果未找到返回 -1
        """
        for i, e in enumerate(self.elements):
            if e == item:
                return i
        return -1

    def compare_and_replace(self, index, new_item):
        """
        如果新元素的路径成本更小，则替换队列中指定索引的元素。
        :param index: 要替换的元素的索引
        :param new_item: 新元素
        """
        if 0 <= index < len(self.elements):
            if new_item.path_cost < self.elements[index].path_cost:
                self.elements[index] = new_item
                self.elements.sort(key=lambda x: x.path_cost)

class Set:
    def __init__(self):
        """
        初始化集合。
        """
        self.elements = []

    def add(self, item):
        """
        向集合中添加元素，如果元素不存在。
        :param item: 要添加的元素
        """
        if item not in self.elements:
            self.elements.append(item)

    def include(self, item):
        """
        判断集合中是否包含指定元素。
        :param item: 要判断的元素
        :return: 包含返回 True，否则返回 False
        """
        return item in self.elements

def Manhattan_distance(loc1, loc2):
    """
    计算两个位置之间的曼哈顿距离。
    :param loc1: 第一个位置，格式为 [行, 列]
    :param loc2: 第二个位置，格式为 [行, 列]
    :return: 曼哈顿距离
    """
    return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])

def h_function_null(state):
    """
    空启发函数，始终返回 0。
    :param state: 当前状态
    :return: 0
    """
    return 0

def h_function_method1(state):
    """
    启发函数方法 1，计算所有线路起点到终点的曼哈顿距离之和。
    :param state: 当前状态，包含网格、线路列表和活动线路索引
    :return: 曼哈顿距离之和
    """
    ans = 0
    for i in range(len(state[1])):
        ans += Manhattan_distance(state[1][i][0], state[1][i][1])
    return ans

def generate_horizontal_path(start, end):
    """
    生成横向优先的曼哈顿路径。
    先横向移动，再纵向移动。
    :param start: 起点，格式为 [行, 列]
    :param end: 终点，格式为 [行, 列]
    :return: 路径列表，每个元素为 [行, 列]
    """
    path = []
    sx, sy = start
    ex, ey = end
    
    # 横向移动（X轴）
    step_x = 1 if ex > sx else -1
    for x in range(sx, ex, step_x):
        path.append((x, sy))
    path.append((ex, sy))
    
    # 纵向移动（Y轴）
    step_y = 1 if ey > sy else -1
    for y in range(sy, ey, step_y):
        path.append((ex, y))
    return path

def generate_vertical_path(start, end):
    """
    生成纵向优先的曼哈顿路径。
    先纵向移动，再横向移动。
    :param start: 起点，格式为 [行, 列]
    :param end: 终点，格式为 [行, 列]
    :return: 路径列表，每个元素为 [行, 列]
    """
    path = []
    sx, sy = start
    ex, ey = end
    
    # 纵向移动（Y轴）
    step_y = 1 if ey > sy else -1
    for y in range(sy, ey, step_y):
        path.append((sx, y))
    path.append((sx, ey))
    
    # 横向移动（X轴）
    step_x = 1 if ex > sx else -1
    for x in range(sx, ex, step_x):
        path.append((x, ey))
    return path

def count_obstacles(grid, path, end, line_idx):
    """
    统计路径中其他线路的障碍物数量。
    排除终点和当前线路自身的路径。
    :param grid: 网格
    :param path: 路径列表，每个元素为 [行, 列]
    :param end: 终点，格式为 [行, 列]
    :param line_idx: 当前线路的索引
    :return: 障碍物数量
    """
    count = 0
    line_value = line_idx + 1  # 当前线路在grid中的标识
    for (x, y) in path:
        # 排除终点和当前线路自身的路径
        if (x, y) == end or grid[x][y] == line_value:
            continue
        if grid[x][y] != 0:  # 被其他线路占据
            count += 1
    return count

def h_function_method2(state):
    """
    改进的启发函数：曼哈顿距离 + 障碍物惩罚。
    对于每条未完成的线路，计算其曼哈顿距离和障碍物最少的路径的障碍物数量，
    并将障碍物数量乘以惩罚系数（2）加到曼哈顿距离上。
    :param state: 当前状态，包含网格、线路列表和活动线路索引
    :return: 启发函数值
    """
    grid = state[0]
    lines = state[1]
    total = 0
    
    for line_idx, (start, end) in enumerate(lines):
        if start == end:
            continue  # 线路已完成
        
        # 基础曼哈顿距离
        md = Manhattan_distance(start, end)
        
        # 生成两种曼哈顿路径
        path_h = generate_horizontal_path(start, end)
        path_v = generate_vertical_path(start, end)
        
        # 计算障碍物数量
        obstacles_h = count_obstacles(grid, path_h, end, line_idx)
        obstacles_v = count_obstacles(grid, path_v, end, line_idx)
        
        # 取障碍较少的路径，并添加惩罚（每个障碍+2）
        min_obstacles = min(obstacles_h, obstacles_v)
        total += md + 2 * min_obstacles
    
    return total

class Node(object):
    def __init__(self, state, parent=None, action=None, path_cost=0, directions=None, depth=0):
        """
        初始化节点对象。
        :param state: 当前状态
        :param parent: 父节点
        :param action: 导致当前状态的动作
        :param path_cost: 从初始状态到当前状态的路径成本
        :param directions: 各线路的最后移动方向，字典格式 {线路索引: 方向}
        :param depth: 节点的深度
        """
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = path_cost
        # 使用字典记录各线路的最后方向 {line_index: direction}
        self.directions = directions if directions is not None else {}
        if parent:
            self.depth = depth

    def child_node(self, problem, action):
        """
        根据当前节点和动作生成子节点。
        计算新的状态、路径成本、移动方向等信息。
        :param problem: 问题对象
        :param action: 动作，格式为 [线路索引, 新位置]
        :return: 子节点对象
        """
        next_state = problem.move(self.state, action)
        line_idx, new_loc = action
        original_start = self.state[1][line_idx][0]
        
        # 计算移动方向
        delta_row = new_loc[0] - original_start[0]
        delta_col = new_loc[1] - original_start[1]
        
        if delta_row == -1:
            current_direction = 'up'
        elif delta_row == 1:
            current_direction = 'down'
        elif delta_col == 1:
            current_direction = 'right'
        elif delta_col == -1:
            current_direction = 'left'
        else:
            current_direction = None
        
        # 复制父节点的方向记录并更新当前线路
        new_directions = self.directions.copy()
        new_directions[line_idx] = current_direction
        
        # 计算新路径成本
        new_cost = problem.g(self, action, next_state, line_idx, current_direction) + problem.h(next_state)
        new_depth = problem.g(self, action, next_state, line_idx, current_direction)
        
        return Node(
            next_state, 
            self, 
            action, 
            new_cost,
            new_directions,
            new_depth
        )

    def path(self):
        """
        从当前节点回溯到初始节点的路径。
        :return: 节点列表，从初始节点到当前节点
        """
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    def __repr__(self):
        """
        返回节点状态的字符串表示。
        :return: 节点状态的字符串表示
        """
        state_map = self.state[0]
        ans = "##########\n"
        n = len(state_map)
        for i in range(n):
            for j in range(n):
                ans += str(state_map[i][j]) + " "
            ans += "\n"
        ans += "##########\n"
        return ans

    def __lt__(self, other):
        """
        比较两个节点的路径成本。
        :param other: 另一个节点
        :return: 当前节点的路径成本小于另一个节点返回 True，否则返回 False
        """
        return self.path_cost < other.path_cost

    def __eq__(self, other):
        """
        比较两个节点的状态是否相等。
        :param other: 另一个节点
        :return: 状态相等返回 True，否则返回 False
        """
        return self.state == other.state

class Problem(object):
    def __init__(self, init_state=None, h_function=None, path_cost=0):
        """
        初始化问题对象。
        :param init_state: 初始状态
        :param h_function: 启发函数
        :param path_cost: 初始路径成本
        """
        self.init_state = Node(init_state, path_cost=path_cost)
        self.h = h_function

    def actions(self, state):
        """
        获取当前状态下的可用动作。
        子类需要实现该方法。
        :param state: 当前状态
        :return: 可用动作列表
        """
        pass

    def move(self, state, action):
        """
        根据动作移动到下一个状态。
        子类需要实现该方法。
        :param state: 当前状态
        :param action: 动作
        :return: 下一个状态
        """
        pass

    def is_goal(self, state):
        """
        判断当前状态是否为目标状态。
        子类需要实现该方法。
        :param state: 当前状态
        :return: 是目标状态返回 True，否则返回 False
        """
        pass

    def g(self, cost, from_state, action, to_state):
        """
        计算从一个状态到另一个状态的路径成本。
        子类需要实现该方法。
        :param cost: 当前路径成本
        :param from_state: 起始状态
        :param action: 动作
        :param to_state: 目标状态
        :return: 路径成本
        """
        pass

    def solution(self, goal):
        """
        获取从初始状态到目标状态的解决方案。
        :param goal: 目标节点
        :return: 动作列表，从初始状态到目标状态的解决方案
        """
        if goal.state is None:
            return None
        return [node.action for node in goal.path()[1:]]

    def expand(self, node):
        """
        扩展节点，生成所有可能的子节点。
        :param node: 当前节点
        :return: 子节点列表
        """
        return [node.child_node(self, action) for action in self.actions(node.state)]

class MatchProblem(Problem):
    def __init__(self, n, init_state, h_function=h_function_null, path_cost=0, mode="mode1"):
        """
        初始化线路匹配问题对象。
        :param n: 网格大小
        :param init_state: 初始状态，包含网格、线路列表和活动线路索引
        :param h_function: 启发函数，默认为 h_function_null
        :param path_cost: 初始路径成本
        :param mode: 搜索模式，默认为 "mode1"
        """
        super().__init__(init_state, h_function, path_cost)
        self.n = n
        self.mode = mode

    def g(self, parent_node, action, to_state, line_idx, current_direction):
        """
        计算从父节点通过某个动作到达新状态的路径成本。
        :param parent_node: 父节点
        :param action: 动作，包含线路索引和新位置
        :param to_state: 到达的新状态
        :param line_idx: 动作对应的线路索引
        :param current_direction: 当前移动方向
        :return: 新的路径成本
        """
        base_cost = 1
        if self.mode == "mode2":
            # 获取该线路上次移动方向
            last_dir = parent_node.directions.get(line_idx)
            
            # 只有当该线路有历史方向时才比较
            if last_dir is not None and current_direction != last_dir:
                base_cost += 2  # 转向惩罚
        return parent_node.depth + base_cost
    
    def is_valid(self, loc):
        """
        判断给定位置是否在网格内。
        :param loc: 位置，格式为 [行, 列]
        :return: 如果位置在网格内返回 True，否则返回 False
        """
        return 0 <= loc[0] < self.n and 0 <= loc[1] < self.n

    def find_next_active_line(self, lines, current_line):
        """
        找到下一个活动线路（未完成的线路）。
        先从当前线路的下一个开始查找，若未找到则从头开始查找。
        :param lines: 线路列表，每个元素为 [起点, 终点]
        :param current_line: 当前线路的索引
        :return: 下一个活动线路的索引，如果所有线路都已完成则返回 None
        """
        n = len(lines)
        # 从current_line+1开始循环查找
        for i in range(current_line + 1, n):
            if lines[i][0] != lines[i][1]:
                return i
        # 如果后面没有，从头开始找
        for i in range(0, current_line + 1):
            if lines[i][0] != lines[i][1]:
                return i
        return None  # 所有线路已完成

    def actions(self, state):
        """
        获取当前状态下的所有可用动作。
        对于当前活动线路，找到其周围的有效移动位置，并生成对应的动作。
        :param state: 当前状态，包含网格、线路列表和活动线路索引
        :return: 可用动作列表，每个动作格式为 [线路索引, 新位置]
        """
        candidates = []
        grid = state[0]
        lines = state[1]
        active_line = state[2]
        if active_line is None:
            return []
        
        start = lines[active_line][0]
        end = lines[active_line][1]
        if start == end:
            return []
        
        candidates_near = [
            [start[0]-1, start[1]],
            [start[0]+1, start[1]],
            [start[0], start[1]-1],
            [start[0], start[1]+1]
        ]
        valid_moves = []
        for loc in candidates_near:
            if self.is_valid(loc) and (grid[loc[0]][loc[1]] == 0 or loc == end):
                valid_moves.append(loc)
        return [[active_line, loc] for loc in valid_moves]

    def move(self, state, action):
        """
        根据给定动作移动到下一个状态。
        更新网格中线路的位置，修改线路列表，更新活动线路索引。
        :param state: 当前状态，包含网格、线路列表和活动线路索引
        :param action: 动作，格式为 [线路索引, 新位置]
        :return: 下一个状态，包含更新后的网格、线路列表和活动线路索引
        """
        new_state = deepcopy(state)
        grid = new_state[0]
        lines = new_state[1]
        active_line = new_state[2]
        
        line_idx, new_loc = action
        grid[new_loc[0]][new_loc[1]] = line_idx + 1
        lines[line_idx][0] = new_loc
        
        # 更新active_line
        new_active_line = self.find_next_active_line(lines, line_idx)
        new_state[2] = new_active_line
        return new_state

    def is_goal(self, state):
        """
        判断当前状态是否为目标状态。
        目标状态为没有活动线路且所有线路的起点和终点相同。
        :param state: 当前状态，包含网格、线路列表和活动线路索引
        :return: 如果是目标状态返回 True，否则返回 False
        """
        if state[2] is not None:
            return False
        for start, end in state[1]:
            if start != end:
                return False
        return True

def search_generator(problem):
    """
    搜索生成器函数，使用优先队列进行搜索。
    从初始状态开始，不断扩展节点，直到找到目标状态或队列为空。
    :param problem: 问题对象
    :yield: 生成搜索过程中的节点
    """
    openPQ = PriorityQueue(problem.init_state)
    closed = Set()

    while not openPQ.empty():
        current = openPQ.pop()
        yield current

        if problem.is_goal(current.state):
            yield current
            break

        closed.add(str(current.state))
        for child in problem.expand(current):
            idx = openPQ.find(child)
            if not (closed.include(str(child.state)) or idx != -1):
                openPQ.push(child)
            elif idx != -1 and child.path_cost < openPQ.elements[idx].path_cost:
                openPQ.compare_and_replace(idx, child)
    yield None

if __name__ == "__main__":
    app = ModernVisualizer()
    app.mainloop()