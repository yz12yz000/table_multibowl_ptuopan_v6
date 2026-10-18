"""Build an editable English methods deck with plain-language Chinese notes."""
import json
import math
import shutil
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.xmlchemy import OxmlElement
from pptx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
ASSETS = OUT / 'assets'
OLD = ROOT / 'output/bowl_research_presentation_20261002/assets'
EVIDENCE = ROOT / 'debug_output/clear_table_validation/yolo_20261010'
SUMMARY = json.loads((EVIDENCE / 'summary.json').read_text())
DEMO = json.loads((EVIDENCE / 'offline_demo/result.json').read_text())
UNIT_PASSED = SUMMARY['pytest']['unit_regression_passed']
ROS_PASSED = SUMMARY['pytest']['optional_ros_subsequently_passed']
TOTAL_PASSED = SUMMARY['pytest']['total_passed']
for name in ('raw_table.png', 'detection.png', 'grasp_pose.png'):
    shutil.copy2(OLD / name, ASSETS / name)

BG, NAVY, INK, GRAY = 'F4F7FA', '112B3B', '203949', '627785'
TEAL, BLUE, AMBER, RED = '008F83', '3579C7', 'D69826', 'BF5A64'
WHITE, LINE, PALE, TINT = 'FFFFFF', 'D9E3E9', 'E6F3F0', 'EAF1F9'
FONT = 'Lato'
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
prs.core_properties.title = 'Movable-Tray Table Clearing — Methods and Validation'
prs.core_properties.subject = 'English slides with accessible Chinese speaker notes'
prs.core_properties.author = 'Robot Grasp Project'
notes = []

def rgb(c):
    return RGBColor.from_string(c)

def shape(s, x, y, w, h, fill=WHITE, stroke=None, kind=MSO_SHAPE.RECTANGLE, lw=1):
    obj = s.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    obj.fill.solid(); obj.fill.fore_color.rgb = rgb(fill)
    if stroke:
        obj.line.color.rgb = rgb(stroke); obj.line.width = Pt(lw)
    else:
        obj.line.fill.background()
    if kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        obj.adjustments[0] = .12
    style = obj._element.find(qn('p:style'))
    if style is not None:
        effect = style.find(qn('a:effectRef'))
        if effect is not None: effect.set('idx', '0')
    return obj

def text(s, value, x, y, w, h, size=20, color=INK, bold=False, align=None, font=FONT):
    obj = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = obj.text_frame; tf.clear(); tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(.015)
    tf.margin_top = tf.margin_bottom = 0
    for i, line in enumerate(value.split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line; p.font.name = font; p.font.size = Pt(size)
        p.font.bold = bold; p.font.color.rgb = rgb(color)
        p.space_after = Pt(5); p.line_spacing = 1.08
        if align is not None: p.alignment = align
    return obj

def line(s, x1, y1, x2, y2, color=LINE, width=1.5, arrow=False, dash=False):
    obj = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    obj.line.color.rgb = rgb(color); obj.line.width = Pt(width)
    if arrow:
        tail = OxmlElement('a:tailEnd'); tail.set('type', 'triangle')
        obj._element.spPr.get_or_add_ln().append(tail)
    if dash:
        from pptx.enum.dml import MSO_LINE_DASH_STYLE
        obj.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return obj

def tag(s, label, x, y, w, color=TEAL, fill=PALE):
    shape(s, x, y, w, .32, fill)
    text(s, label, x+.08, y+.055, w-.16, .23, 10, color, True)

def bullet(s, title, body, x, y, w=4.6, color=TEAL):
    shape(s, x, y+.06, .055, .28, color)
    text(s, title, x+.18, y, w-.18, .36, 20, INK, True)
    text(s, body, x+.18, y+.47, w-.18, .77, 16, GRAY)

def photo(s, filename, x, y, w, h):
    from PIL import Image
    path = ASSETS / filename
    iw, ih = Image.open(path).size
    scale = min(w / iw, h / ih)
    return s.shapes.add_picture(str(path), Inches(x+(w-iw*scale)/2), Inches(y+(h-ih*scale)/2),
                               width=Inches(iw*scale), height=Inches(ih*scale))

def note(s, title, body, sources):
    value = '【中文讲解备注｜面向非专业听众】\n' + body + '\n\n【资料来源】\n' + '\n'.join(sources)
    tf = s.notes_slide.notes_text_frame; tf.text = value
    for p in tf.paragraphs:
        p.font.name = 'Noto Sans CJK SC'; p.font.size = Pt(12)
    notes.append((title, value))

def new(title, section, caption='', dark=False):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(NAVY if dark else BG)
    text(s, section.upper(), .57, .3, 11.8, .23, 10, '60CEC3' if dark else TEAL, True)
    text(s, title, .57, .83, 12.15, .83, 31, WHITE if dark else INK, True)
    line(s, .57, 7.07, 12.77, 7.07, '36515F' if dark else LINE, .8)
    text(s, caption or 'Movable-Tray Table Clearing  |  Methods & principles', .57, 7.17, 11.3, .19,
         8.5, 'ADBFCA' if dark else GRAY)
    text(s, f'{len(prs.slides):02d}', 12.2, 7.13, .57, .24, 11,
         'ADBFCA' if dark else GRAY, align=PP_ALIGN.RIGHT)
    return s

def disk(s, x, y, r=.25, color=BLUE, label='', fill=None):
    shape(s, x-r, y-r, 2*r, 2*r, fill or WHITE, color, MSO_SHAPE.OVAL, 2)
    if label: text(s, label, x-r, y-.12, 2*r, .25, 12, color, True, PP_ALIGN.CENTER)

def tabletop(s, x, y, w, h, occupied=1, outside=3, selected=None):
    shape(s, x, y, w, h, WHITE, LINE, MSO_SHAPE.ROUNDED_RECTANGLE)
    tx, ty, tw, th = x+w*.49, y+h*.23, w*.43, h*.64
    shape(s, tx, ty, tw, th, PALE, TEAL, MSO_SHAPE.ROUNDED_RECTANGLE, 1.5)
    text(s, 'TRAY', tx+.13, ty+.08, tw-.26, .25, 10, TEAL, True)
    locs = [(tx+tw*.28,ty+th*.39),(tx+tw*.72,ty+th*.39),
            (tx+tw*.28,ty+th*.76),(tx+tw*.72,ty+th*.76)]
    for j,(cx,cy) in enumerate(locs):
        color = TEAL if j < occupied else (AMBER if j == selected else LINE)
        disk(s,cx,cy,min(w*.044,.23),color,chr(65+j),PALE if j<occupied else WHITE)
    for j in range(outside):
        disk(s,x+w*(.16+.12*(j%2)),y+h*(.31+.23*j),min(w*.045,.24),BLUE,str(j+1))
    return locs

def make_demo_charts():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Circle
    import numpy as np
    plt.rcParams['font.family'] = 'DejaVu Sans'
    for idx in range(1,6):
        observation = json.loads((EVIDENCE / f'offline_demo/round_{idx:04d}/synthetic_observation.json').read_text())
        d = DEMO['rounds'][idx-1]['decision']
        t = observation['tray']; c=np.array(t['center_xy']); theta=t['yaw']
        rot=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]])
        poly=np.array([[-.3,-.22],[.3,-.22],[.3,.22],[-.3,.22]])@rot.T+c
        fig,ax=plt.subplots(figsize=(3.2,3.2),dpi=180)
        fig.patch.set_facecolor('#FFFFFF'); ax.set_facecolor('#FFFFFF')
        ax.add_patch(Polygon(poly,facecolor='#E6F3F0',edgecolor='#008F83',lw=2))
        for obj in observation['objects']:
            p=np.array(obj['center_xy'])
            uv=(p-c)@rot
            inside=abs(uv[0])+.06 <= .3 and abs(uv[1])+.06 <= .22
            ax.add_patch(Circle(p,.06,facecolor='#008F83' if inside else '#3579C7',alpha=.9))
        if d.get('slot'):
            ax.add_patch(Circle(d['slot']['xy'],.073,facecolor='none',edgecolor='#D69826',lw=2.5,ls='--'))
            ax.text(*d['slot']['xy'],d['slot']['id'],ha='center',va='center',fontsize=10,color='#99620B',fontweight='bold')
        ax.set_xlim(-.98,.06); ax.set_ylim(-.83,.50); ax.set_aspect('equal')
        ax.axis('off'); fig.tight_layout(pad=.05)
        for ext in ('png','svg'):
            fig.savefig(ASSETS/f'observation_{idx}.{ext}',bbox_inches='tight',pad_inches=.025)
        plt.close(fig)

make_demo_charts()

# 01 — Cover
s = new('Observe. Pick. Place. Repeat.', 'Robotics / Method report', 'Project methods report  |  10 OCT 2026', True)
photo(s,'raw_table.png',6.42,1.83,6.35,4.65)
text(s,'Movable-Tray\nTable Clearing',.64,1.91,5.5,1.65,37,WHITE,True)
text(s,'YOLO tray segmentation around the\nexisting bowl grasp-and-place pipeline.',.66,3.79,5.2,1.0,21,'C9D9E3')
for i,label in enumerate(('Re-localize the tray','Reuse the grasp and motion','Verify after every placement')):
    text(s,f'0{i+1}',.68,5.06+i*.45,.45,.3,13,'60CEC3',True)
    text(s,label,1.25,5.02+i*.45,4.7,.34,17,WHITE)
text(s,'Historical project photograph • not the new tray demo',6.6,6.55,6.0,.23,10,'ADBFCA')
note(s,'Observe. Pick. Place. Repeat.',
     '这次介绍的是让现有机器人从“抓一只碗、放到固定位置”，扩展到“把桌上的碗逐只放进一个可以移动的托盘”。托盘直接用 YOLO 分割识别，抓法和放法继续沿用。可以把机器人理解成一个收桌子的人：先看、拿一只、放好、再确认。\n右边是项目以前的现场照片，只用来说明机器人与桌面环境；本次新增托盘功能的证据来自软件与模拟测试，不把这张照片当成新功能的实机验收。原来的碗模型没有托盘类别，在线识别还需要准备专门的托盘分割权重，项目没有附带该权重。接下来会讲方法、关键判断、检查结果和仍需现场验证的内容。',
     ['implement_new2.md','New_run/README.md','output/bowl_research_presentation_20261002/asset_sources.json'])

# 02 — Goal
s = new('Three decisions make the task work', '01 / Task definition')
text(s,'CURRENT SCENE',.68,1.84,5.6,.3,12,GRAY,True)
text(s,'DESIRED SCENE',7.04,1.84,5.6,.3,12,GRAY,True)
tabletop(s,.66,2.3,5.55,2.8,1,3)
tabletop(s,7.04,2.3,5.55,2.8,4,0)
line(s,6.35,3.67,6.91,3.67,TEAL,3,True)
for x,n,t,b in [( .68,'01','Where is the tray?','Update its position and orientation.'),
                  (4.88,'02','Which bowl is next?','Exclude bowls already inside.'),
                  (9.05,'03','Where can it go?','Choose an unoccupied interior slot.')]:
    text(s,n,x,5.52,.45,.3,15,TEAL,True);text(s,t,x,5.99,3.65,.4,20,INK,True)
    text(s,b,x,6.48,3.68,.4,14,GRAY)
note(s,'Three decisions make the task work',
     '左图有三只碗还在桌上，托盘里本来就有一只；右图表示希望得到的整理结果。这是说明原理的俯视示意图，不是相机截图。\n整个问题可以拆成三个很直观的问题：托盘现在在哪里、还有哪只碗没有收好、托盘里哪里还能放。只要这三个判断做好，就能继续使用原来的机械臂抓放程序。托盘里本来就有的碗以及新放进去的碗，都只算作“占用了位置”，不再作为抓取目标。托盘可以在开始任务前或两轮之间换位置，机器人会重新观察；一轮动作进行时，托盘要保持静止。',
     ['implement_new2.md §1, §4, §5, §10','tools/place_rounds.py: ClearTableSession'])

# 03 — Loop
s = new('One bowl per cycle. One fresh scene for the next decision.', '02 / Feedback principle')
items=[('01','Observe','Acquire a fresh RGB-D frame.'),('02','Measure','Locate the tray and all bowls.'),
       ('03','Verify','Check the previous placement.'),('04','Choose','One source bowl + one free slot.'),
       ('05','Pick & place','Run the existing motion sequence.'),('06','Return','Go back to the saved home pose.')]
coords=[(.72,2.0),(4.86,2.0),(9.,2.0),(9.,4.36),(4.86,4.36),(.72,4.36)]
for (n,t,b),(x,y) in zip(items,coords):
    shape(s,x,y,3.59,1.7,WHITE,LINE)
    text(s,n,x+.2,y+.2,.5,.3,13,TEAL,True)
    text(s,t,x+.2,y+.66,3.18,.4,22,INK,True)
    text(s,b,x+.2,y+1.15,3.18,.43,14,GRAY)
for a,b in [((4.36,2.83),(4.75,2.83)),((8.5,2.83),(8.89,2.83)),
            ((10.79,3.78),(10.79,4.22)),((8.89,5.18),(8.5,5.18)),
            ((4.75,5.18),(4.36,5.18)),((2.5,4.22),(2.5,3.78))]:
    line(s,*a,*b,TEAL,2.3,True)
text(s,'First cycle: no previous placement to verify. Final cycle: observe again before declaring completion.',
     .73,6.43,11.94,.38,16,GRAY)
note(s,'One bowl per cycle. One fresh scene for the next decision.',
     '这张图是整个程序的工作循环。先用新图像看桌面，再计算托盘和碗的位置；如果上一轮刚放过一只碗，就先确认它真的进了托盘。确认后，再选下一只和一个空位置，按原来的方法抓放，最后返回原起点。\n“新图像”很重要：上一轮动作结束后，桌面已经变了，旧图像里的空位可能已经放了碗，旧目标的位置也可能不适用了。第一轮没有上一只碗，不需要这一步归位核查。最后一只放完也不能直接结束，还要重新看；默认还会做连续的空源区确认。核查与下一轮选择共用同一次观察，不额外设计一套机械臂检查动作。',
     ['tools/test_live_place_pipeline.py: run_clear_table','tools/place_rounds.py: ClearTableSession.observe'])

# 04 — Architecture
s = new('Add scene decisions around the existing pipeline', '03 / Minimal architecture')
modules=[('VISION','YOLO + RGB-D','Tray mask + original bowl clouds',TEAL),
         ('GEOMETRY','Rim locator','Observed grasp candidates',BLUE),
         ('DECISION','Existing runner','Filter bowls; choose tray slot',TEAL),
         ('MOTION','Grasp executor','Plan, execute and return',BLUE)]
for i,(cap,title,body,col) in enumerate(modules):
    x=.7+i*3.16
    shape(s,x,2.08,2.94,2.1,WHITE,LINE);shape(s,x,2.08,2.94,.075,col)
    text(s,cap,x+.17,2.33,2.6,.26,11,col,True)
    text(s,title,x+.17,2.94,2.6,.42,21,INK,True)
    text(s,body,x+.17,3.52,2.6,.53,15,GRAY)
    if i<3:line(s,x+2.99,3.11,x+3.12,3.11,GRAY,1.7,True)
shape(s,.72,4.69,11.91,1.3,PALE)
text(s,'Small additions',.96,4.93,2.6,.4,21,TEAL,True)
text(s,'Tray localization  •  Bowl footprints  •  Occupancy memory  •  Placement confirmation',
     3.65,4.97,8.57,.72,19,INK)
text(s,'Shared acquisition stamp + task identity keep observations and grasp candidates aligned.',
     .73,6.45,11.9,.42,17,GRAY)
note(s,'Add scene decisions around the existing pipeline',
     '可以把程序想成四个人分工：第一个负责看图，第二个负责找碗边上哪里能夹，第三个负责决定夹哪只、放哪里，第四个负责规划和执行动作。\n视觉节点用同一张彩色图分别识别碗和托盘，碗继续使用原模型，托盘使用另一个可配置的分割模型。托盘掩膜只用于确定收纳区，不混进碗的抓取点云。定位器仍然给全部碗产生抓取候选，运行器收到完整信息后再过滤托盘内的碗。托盘位置和碗占用范围放进原有状态消息，不新增场景通信系统。时间戳好比照片的拍摄编号，任务编号好比订单号，可以防止旧照片或旧任务的数据串进当前动作。',
     ['implement_new2.md §7','src/yolo_vision/yolo_vision/main.py','tools/test_live_place_pipeline.py'])

# 05 — Vision
s = new('Turn visible bowls into physical footprints', '04 / RGB-D perception',
        'Historical segmentation image • footprint estimation is the new task-level input')
photo(s,'detection.png',.66,1.9,6.55,4.1)
tag(s,'HISTORICAL PROJECT IMAGE',.81,6.13,2.85,BLUE,TINT)
bullet(s,'RGB tells us what belongs to a bowl','YOLO provides the bowl mask.',7.65,2.02,4.97)
bullet(s,'Depth tells us where the surface is','Use registered depth from the same frame.',7.65,3.44,4.97)
bullet(s,'Use a common coordinate frame','Transform to base; estimate center and radius.',7.65,4.86,4.97)
text(s,'Bowl footprint ≠ a single rim grasp point',.79,6.55,6.21,.37,18,INK,True)
note(s,'Turn visible bowls into physical footprints',
     '普通彩色照片能告诉我们“哪些像素属于碗”，但像素本身不能直接告诉机械臂要移动多少厘米。深度图补上每个位置离相机多远的信息，两者对齐以后，就能得到碗表面的三维位置。\n程序把这些位置转换到机器人使用的统一坐标，再估计碗在桌面上的中心和保守占用范围。可以想象成给每只碗在桌面上画一个稍大一点的圆圈。这个圆圈用于判断碗是否完全在托盘内、是否会挤到别的碗。夹爪接触的某个碗沿点不等于碗中心，不能用它代替整个碗的位置。右侧三个步骤强调同一轮图像和深度必须对应；深度不足或范围不可信时会保留未确定状态。',
     ['src/yolo_vision/yolo_vision/main.py','src/yolo_vision/yolo_vision/tray_utils.py: estimate_object_position','output/bowl_research_presentation_20261002/assets/detection.png'])

# 06 — Tray pose: editable geometric illustration, not a detector result.
s = new('YOLO gives the tray a movable coordinate frame', '05 / Tray localization',
        'Explanatory diagram • trained tray segmentation weights are required and are not included')
shape(s,.72,1.97,6.2,4.7,WHITE,LINE)
text(s,'YOLO MASK / OUTER CONTOUR',1.13,2.2,5.38,.3,12,BLUE,True)
shape(s,1.12,2.75,5.36,2.8,TINT,BLUE,MSO_SHAPE.ROUNDED_RECTANGLE,2)
shape(s,1.42,3.04,4.76,2.22,PALE,TEAL,MSO_SHAPE.ROUNDED_RECTANGLE,2)
text(s,'USABLE INTERIOR',1.64,3.21,3.02,.3,12,TEAL,True)
disk(s,3.75,4.14,.08,TEAL,fill=TEAL)
line(s,3.75,4.14,5.34,4.14,TEAL,2.4,True)
line(s,3.75,4.14,3.75,3.59,TEAL,2.4,True)
text(s,'u',5.43,4.0,.35,.35,19,TEAL,True)
text(s,'v',3.31,3.58,.35,.35,19,TEAL,True)
text(s,'center',3.23,4.39,1.0,.29,13,GRAY)
disk(s,5.44,4.78,.17,AMBER,'A')
text(s,'Depth converts pixels to base XY.\nLocal slots follow the observed pose.',1.08,5.83,5.5,.69,17,INK,True)
bullet(s,'Segment the whole tray','Dedicated tray weights required; not included.',7.5,2.03,5.12)
bullet(s,'Measure center and long axis','Same-frame depth + acquisition-time TF.',7.5,3.46,5.12)
bullet(s,'Move the slots with the tray','p_slot = c_tray + R(θ) · [u, v]',7.5,4.9,5.12)
note(s,'YOLO gives the tray a movable coordinate frame',
     '现在直接让 YOLO 在照片上涂出“哪些像素属于托盘”，这块区域叫掩膜。深度图告诉程序这些像素离相机多远，再用拍摄时刻的坐标转换，得到机器人坐标下的托盘中心和长边方向。蓝色线表示识别的外轮廓，绿色线表示实际允许放碗的内侧范围；两种尺寸都要现场测量，不能把托盘边沿也当成可用空地。\n图中的 u、v 像固定在托盘上的两把尺子，A 点先跟随托盘转动，再加上托盘当前位置，这就是公式的含义。这是原理示意图，不是识别结果。当前支持一只长短边明显不同的矩形薄托盘。矩形转半圈看起来一样，程序只能在相邻轮次小幅转动的前提下保持方向连续，不能区分实际掉头或换了一只同类托盘。原碗模型没有托盘类别，必须另行提供托盘分割权重；缺少模型或看不清时不猜位置。',
     ['src/yolo_vision/yolo_vision/segmentation.py: TraySegmentationConfig, Segmenter',
      'src/yolo_vision/yolo_vision/tray_utils.py: detect_tray, slot_xy',
      'src/yolo_vision/config/clear_table_tray.json','src/yolo_vision/models/README.md'])

# 07 — Classification
s = new('A bowl is handled only when its footprint is inside', '06 / Target selection')
shape(s,.72,1.99,6.18,4.67,WHITE,LINE)
shape(s,3.15,2.61,3.14,3.24,PALE,TEAL,MSO_SHAPE.ROUNDED_RECTANGLE,2)
text(s,'TRAY INTERIOR',3.36,2.81,2.67,.27,11,TEAL,True)
disk(s,4.77,3.71,.45,TEAL,'IN',PALE)
disk(s,1.72,3.55,.46,BLUE,'OUT',TINT)
disk(s,3.17,5.16,.47,AMBER,'?', 'FBF1DD')
text(s,'Boundary overlap',.99,5.97,4.9,.38,18,AMBER,True)
bullet(s,'Inside → keep as occupancy','Do not submit this bowl for grasping.',7.45,2.13,5.12,TEAL)
bullet(s,'Outside + in source region → candidate','Choose one using the existing ordering.',7.45,3.59,5.12,BLUE)
bullet(s,'Uncertain → observe again','Boundary overlap or unreliable depth stays unresolved.',7.45,5.05,5.12,AMBER)
note(s,'A bowl is handled only when its footprint is inside',
     '这里判断的不是“碗中心碰到了托盘就算完成”，而是碗的保守占用范围是否完全落在托盘里。绿色碗已经完全在里面，所以不再抓它，但它占的位置要被记住。蓝色碗在托盘外，而且在允许收拾的桌面范围里，所以可以作为待抓目标。\n黄色碗压着托盘边界，或者深度不清楚时，就先不下结论。程序会有限次重新观察，而不是把它当成已经收好，也不是把相关区域当作空位。这里依据的是空间位置和范围，不依赖 YOLO 每一帧给碗分配的临时编号。因此下一轮碗的检测编号变了，已经在托盘里的碗也不会因为编号变化而再次被抓。',
     ['src/yolo_vision/yolo_vision/tray_utils.py: classify_object','tools/place_rounds.py: ClearTableSession.observe'])

# 08 — Occupancy
s = new('Select space for the actual bowl being carried', '07 / Occupancy and slot choice')
shape(s,.71,1.98,6.2,4.72,WHITE,LINE)
shape(s,1.09,2.37,5.42,3.3,PALE,TEAL,MSO_SHAPE.ROUNDED_RECTANGLE,2)
for cx,cy,l,col,fill in [(2.49,3.33,'A',TEAL,PALE),(5.05,3.33,'B',AMBER,'FBF1DD'),
                        (2.49,4.8,'C',GRAY,'E9EEF2'),(5.05,4.8,'D',BLUE,WHITE)]:
    disk(s,cx,cy,.43,col,l,fill)
text(s,'occupied',1.82,3.89,1.36,.24,12,TEAL,align=PP_ALIGN.CENTER)
text(s,'selected',4.38,3.89,1.36,.24,12,AMBER,align=PP_ALIGN.CENTER)
text(s,'reserved',1.83,5.38,1.34,.24,12,GRAY,align=PP_ALIGN.CENTER)
text(s,'available',4.39,5.38,1.34,.24,12,BLUE,align=PP_ALIGN.CENTER)
text(s,'Used or uncertain slots are not immediately freed.',1.0,6.04,5.7,.48,17,INK,True)
bullet(s,'Check the tray edge','distance to edge ≥ bowl radius + margin',7.42,2.03,5.14)
bullet(s,'Check nearby bowls','center distance > both radii + clearance',7.42,3.42,5.14)
bullet(s,'Keep a small occupancy record','Reserve used slots; refresh observed occupancy.',7.42,4.83,5.14)
note(s,'Select space for the actual bowl being carried',
     '最简单的放置方案是在托盘里预先安排几个宽松的位置，比如 A、B、C、D，不做复杂的自动堆叠。每轮都根据托盘当前位置，重新计算这些点在哪里。\n选位置时有两把尺子：一是离托盘边缘够不够远，二是离已有碗够不够远。间隔要根据这次选中的碗实际有多大来算，不能所有碗都当作同样的小碗。半径就是碗宽度的一半，程序还加上误差余量。A 已经有碗，C 表示已用或保留的位置，B 是这次选中的空位。即使下一张图暂时漏掉一只刚放下的碗，也不能立刻把那里当成空的。图中 A 到 D 的状态用于解释判断规则，不是某一帧实机结果。',
     ['src/yolo_vision/yolo_vision/tray_utils.py: choose_slot','tools/place_rounds.py: known_inside, used_positions'])

# 09 — Retained grasp
s = new('Reuse the existing rim-grasp method', '08 / Grasp geometry',
        'Historical grasp-target overlay • a planned/selected pose is not proof of a successful physical grasp')
photo(s,'grasp_pose.png',.67,1.91,6.62,4.14)
tag(s,'EXISTING GRASP PIPELINE',.82,6.16,3.02,BLUE,TINT)
bullet(s,'Use observed rim contacts','Fit reliable bowl geometry; retain measured contact points.',7.62,2.04,5.0,BLUE)
bullet(s,'Keep finger direction consistent','Radial direction assigns the outside finger; tool Z points down.',7.62,3.55,5.0,BLUE)
bullet(s,'Preserve candidate fallback','Supported-wall fallback and pre-motion planning checks remain.',7.62,5.08,5.0,BLUE)
text(s,'New task decisions do not redesign the grasp.',.81,6.59,6.39,.32,17,INK,True)
note(s,'Reuse the existing rim-grasp method',
     '这次没有改变碗怎么夹。原程序先根据真实看到的碗沿和局部碗壁找接触位置。圆弧信息足够可靠时，用圆心指向接触点的方向来确定夹爪朝向，让同一根手指在碗外、另一根在碗内，工具保持向下。\n如果只是可见圆弧不够，原程序允许在已有的局部碗壁证据可靠时使用备用方法。它不是对所有识别失败都强行抓取。每只碗可能有多个候选位置，动作开始前会检查完整路径能否规划；尚未运动时可以换候选。一旦运动发生失败，不会自动再抓一次。左图是历史的抓取目标可视化，十字和坐标轴表示程序选定的位置与方向，不能仅凭这个图判断碗已被抓牢。',
     ['docs/圆碗径向抓取修改_20260928.md','src/rim_locator/rim_locator/rim_detection.py','src/grasp_executor/grasp_executor/candidates.py','output/bowl_research_presentation_20261002/assets/grasp_pose.png'])

# 10 — Seven segments
s = new('Keep the motion sequence; update the destination XY', '09 / Placement principle')
labels=['Approach','Descend\nto grasp','Lift','Transfer to\npre-release','Descend\nand release','Retreat','Return\nhome']
heights=[3.0,4.22,3.0,3.0,4.22,3.0,3.0]
for i in range(6):
    line(s,1.28+i*1.79,heights[i],1.28+(i+1)*1.79,heights[i+1],TEAL if i>1 else BLUE,2.3,True)
for i,(label,yy) in enumerate(zip(labels,heights)):
    xx=1.28+i*1.79
    disk(s,xx,yy,.24,BLUE if i<3 else TEAL,str(i+1),WHITE)
    text(s,label,xx-.72,4.84,1.44,.77,15,INK,True,PP_ALIGN.CENTER)
tag(s,'SCHEMATIC MOTION ORDER • NOT A ROBOT TRAJECTORY',.74,1.85,5.68,GRAY,'E9EEF2')
line(s,.91,4.59,12.38,4.59,LINE,1.3)
shape(s,.74,6.04,11.88,.68,PALE)
text(s,'tool release XY = selected slot XY + fixed offset',.99,6.22,7.18,.35,20,INK,True)
text(s,'Same Z • orientation • descent • home',8.46,6.25,3.9,.28,14,TEAL,True)
note(s,'Keep the motion sequence; update the destination XY',
     '原动作顺序继续使用：先到碗上方，再下降夹住、抬起、搬到放置准备点、下降释放、上退，最后回到保存的起点。一共七段，实际路径由原来的规划系统计算。图里的折线只表示动作先后，并不是机械臂真的走这样一条折线。\n薄托盘可以沿用原桌面释放高度，所以本次主要更换水平位置，也就是左右和前后的位置。要注意，夹爪的位置和碗最后落下的中心不一定重合，因此可以通过一次实际测量设置固定的水平偏移。这里没有针对每个抓取候选重新计算复杂的三维放置姿态。原 blue 基准的高度、方向、下降距离和返回姿态在任务开始时固定，整轮任务都沿用它们；实际落点误差仍要接设备后测量。',
     ['tools/place_rounds.py: _release_coordinates, tray_release_config','src/grasp_executor/grasp_executor/grasp.py','src/grasp_executor/config/place_zones.json'])

# 11 — Confirmation
s = new('Confirm a changed scene before starting the next pick', '10 / Placement verification')
tabletop(s,.73,2.17,5.29,2.54,1,1,1)
tabletop(s,7.16,2.17,5.29,2.54,2,0)
text(s,'BEFORE THE ACTION',.83,1.82,5.0,.28,12,GRAY,True)
text(s,'FRESH OBSERVATION AFTER RETURN',7.23,1.82,5.1,.28,12,TEAL,True)
line(s,6.21,3.4,6.92,3.4,TEAL,2.4,True)
checks=[('1','Source bowl is gone'),('2','New occupancy at the chosen slot'),('3','Previous tray occupancy remains')]
for i,(num,label) in enumerate(checks):
    x=.83+i*4.15
    tag(s,num,x,5.14,.4,TEAL,PALE)
    text(s,label,x,5.69,3.74,.85,20,INK,True)
text(s,'An action acknowledgment reserves the slot. A fresh observation confirms placement.',
     .82,6.64,11.9,.29,15,GRAY)
note(s,'Confirm a changed scene before starting the next pick',
     '机器人报告“动作执行完了”，只表示控制流程走完，并不自动证明碗落到了预想的位置。所以程序把两件事分开记：第一件是动作完成，先把那个位置保留；第二件是下一张图确认归位，才增加真正确认收好的数量。\n核查时看三点：原来的源位置是否还留着那只碗、选中的空位附近是否出现了新的碗、托盘里原有的碗是否还能对应上。三点一起判断，比只看到托盘里“有一只碗”可靠，因为那只碗可能本来就在里面。只要上一只的结果不清楚，就有限次重新观察，不继续搬下一只。图示为了容易理解只画了一只待收碗，实际程序每轮可以观察多只，但只执行一只。',
     ['tools/place_rounds.py: ClearTableSession.observe, record_motion','tools/test_clear_table_policy.py'])

# 12 — Actual offline sequence
s = new('Three placements, five observations', '11 / Recorded software result',
        'Plots reconstructed from saved synthetic observations • all sensing and actuator feedback are simulated')
text(s,'Blue: pending bowls   •   Teal: inside tray   •   Amber ring: selected destination',
     .76,1.64,11.9,.26,13,GRAY)
steps=['Pick → B','Confirm 1\nPick → C','Confirm 2\nPick → D','Confirm 3\nCheck empty','Confirm empty\nComplete']
for i,label in enumerate(steps):
    x=.62+i*2.55
    shape(s,x,2.01,2.38,3.77,WHITE,LINE)
    text(s,f'OBSERVATION {i+1}',x+.14,2.19,2.1,.25,11,TEAL,True)
    photo(s,f'observation_{i+1}.png',x+.08,2.54,2.22,2.18)
    text(s,label,x+.14,4.97,2.1,.64,16,INK,True,PP_ALIGN.CENTER)
shape(s,.65,6.1,12.0,.62,PALE)
text(s,'3 bowls confirmed   /   Slots B, C, D used   /   Existing slot A preserved',.91,6.27,11.48,.32,20,TEAL,True)
note(s,'The offline run completed three placements in five observations',
     '这一页不是随意画的流程，而是从本次保存的离线演示结果重新绘制的。蓝色圆表示托盘外的待收碗，绿色圆表示托盘内的碗，黄色虚线圈标出当轮选中的位置。所有图都使用同一坐标范围，所以能看出托盘在轮次间有轻微移动和转动。\n第一张图选 B 放第一只；第二张图先确认第一只，再选 C；第三张图确认第二只，再选 D。第四张图确认第三只已经进托盘，并第一次看到待收区域为空；第五张图再次确认空了，任务才结束。最初 A 位置已有一只碗，因此一直没有被重复使用。结果是三次抓放、三只确认归位、五次观察。这里输入图像位置和机械臂反馈都是模拟的，不能当作真实抓取成功率。',
     ['debug_output/clear_table_validation/yolo_20261010/offline_demo/result.json',
      'debug_output/clear_table_validation/yolo_20261010/offline_demo/round_0001..0005/synthetic_observation.json'])

# 13 — Debugging
s = new('Four checks protect the YOLO tray workflow', '12 / Debugging findings')
cards=[('01','Model contract','The existing bowl model has no tray class.',
        'Require local tray segmentation weights and the correct class.'),
       ('02','Full visibility','A tray detection does not prove the whole scene is visible.',
        'Check contour, depth and the full tray / source view.'),
       ('03','Axis continuity','A rectangular mask can reverse its reported axis.',
        'Align equivalent axes; preserve occupied and reserved slots.'),
       ('04','Actual bowl size','A fixed small-bowl assumption can select a tight slot.',
        'Check this bowl against the edge and neighboring bowls.')]
for i,(num,title,problem,fix) in enumerate(cards):
    x=.73+(i%2)*6.31;y=1.97+(i//2)*2.38
    shape(s,x,y,5.96,2.1,WHITE,LINE);shape(s,x,y,.065,2.1,TEAL)
    text(s,num,x+.2,y+.18,.4,.3,13,TEAL,True)
    text(s,title,x+.8,y+.15,4.9,.38,22,INK,True)
    text(s,problem,x+.22,y+.75,5.48,.48,16,GRAY)
    text(s,fix,x+.22,y+1.38,5.48,.6,16,TEAL,True)
note(s,'Four checks protect the YOLO tray workflow',
     '这次重点检查四类容易出错的地方。第一，原模型会识别碗，不代表会识别托盘；程序会检查托盘模型文件、类别和分割能力，不能只把名字改成 tray 就认为成功。第二，检测到托盘不代表整个托盘都看清了，还要检查边界、深度，以及完整托盘和待收区域是否都在碗检测的视野里。\n第三，矩形的长轴可能在相邻图像中突然反向。如果直接照用，A、B 等位置就可能对调；程序会选择与上一轮最接近的等价方向，使占用记录连续，超过 45 度的最小等价变化会拒绝。真实转半圈或替换托盘仍不支持。第四，继续按本次要搬的碗的实际大小检查空位，不能只按最小碗尺寸估计。这些检查由合成数据和模型接口测试覆盖，没有把假的检测输出说成真实模型识别成功。',
     ['debug_output/clear_table_validation/yolo_20261010/summary.json',
      'src/yolo_vision/test/test_tray_models.py','tools/test_clear_table_policy.py',
      'src/yolo_vision/test/test_tray_utils.py','src/yolo_vision/test/test_tray_observation.py'])

# 14 — Verification levels
s = new('Validation covers logic, ROS contracts and motion planning', '13 / Checks and evidence',
        'Validation run: 10 OCT 2026 • no physical camera or robot connected')
shape(s,.74,1.99,3.56,4.71,NAVY)
text(s,str(TOTAL_PASSED),1.05,2.43,2.95,1.0,68,WHITE,True)
text(s,'automated tests passed',1.07,3.65,2.95,.6,21,WHITE,True)
text(s,f'{UNIT_PASSED} unit / regression\n+ {ROS_PASSED} isolated ROS control tests',1.08,4.61,2.93,.83,17,'B6CFDA')
text(s,f"{len(SUMMARY['build']['packages'])} ROS packages built",1.08,6.07,2.92,.36,18,'60CEC3',True)
entries=[('ros_transport','ROS transport','Fresh stamps, identities and retained messages.'),
         ('launch_contract','Launch contracts','Correct topics, namespaces and runtime parameters.'),
         ('signal_cleanup','Interruption cleanup','SIGTERM / SIGHUP leave no owned workers running.'),
         ('moveit','MoveIt integration','Planning, candidate fallback and simulated return home.')]
for i,(key,title,body) in enumerate(entries):
    yy=2.01+i*1.18
    text(s,str(SUMMARY['integration'][key]['checks']),4.82,yy,.93,.65,36,TEAL,True)
    text(s,title,6.12,yy+.05,6.26,.4,21,INK,True)
    text(s,body,6.12,yy+.56,6.23,.43,15,GRAY)
note(s,'Validation covers logic, ROS contracts and motion planning',
     '检查分几个层次。普通逻辑测试确认空位判断、状态变化和异常处理；ROS 通信和启动检查确认模块之间的消息正确，旧数据不会串进来，退出时不会留下后台程序；最外层使用真正的 MoveIt 规划程序配合模拟关节和夹爪反馈检查动作链。\n'
     f'本次共 {UNIT_PASSED} 项普通回归通过，另有 {ROS_PASSED} 项控制测试在隔离的 ROS 环境里通过，合计 {TOTAL_PASSED} 项。右侧是另外几个集成检查组，不把不同类型的数字混在一起算成功率。三个 ROS 包重新构建成功。托盘模型接口和几何测试使用合成掩膜或模拟模型，没有加载真实托盘权重来证明识别准确率。真实识别是否稳定、碗是否滑动、最终偏多少毫米，仍需现场实验。',
     ['debug_output/clear_table_validation/yolo_20261010/summary.json',
      'debug_output/clear_table_validation/yolo_20261010/validation.log',
      'run_pipeline_place_offline_test.sh'])

# 15 — Next hardware
s = new('From software validation to hardware trials', '14 / Deployment boundaries')
for i,(title,body) in enumerate([
    ('Prepare','Provide tray segmentation weights;\nmeasure outer / usable tray sizes.'),
    ('Preview','Calibrate the source and release;\ncheck full visibility and the path.'),
    ('Measure','Test one bowl first; record actual\nplacement error and repeatability.')]):
    xx=.76+i*4.22
    text(s,f'0{i+1}',xx,2.0,.65,.4,20,TEAL,True)
    line(s,xx,2.7,xx+3.69,2.7,TEAL,2)
    text(s,title,xx,3.0,3.74,.57,28,INK,True)
    text(s,body,xx,3.85,3.72,1.28,20,GRAY)
shape(s,.76,5.65,11.91,1.04,PALE)
text(s,'Operating assumptions',1.0,5.83,3.36,.36,20,TEAL,True)
text(s,'One non-square rectangular tray • stationary during each action\nNo abrupt half-turns or tray swaps • no new 3D collision scene.',
     4.31,5.83,8.01,.73,17,INK)
note(s,'Move from software validation to measured hardware trials',
     '软件检查通过后，上机还有三步。第一步准备包含托盘类别的分割权重，并测量托盘外轮廓和内侧可放区域。项目没有提供托盘模型，已有碗模型也不能直接识别托盘；需要用真实画面验证光照、位置和遮挡变化下的效果。\n第二步标定允许收拾的桌面区域、工具与实际碗落点的偏移，先做只规划预览，确认整个托盘和待收区域都可见，抓放与返回路径能规划。配置中 calibrated 默认是假，验证前不能直接把示例数值用于动作。第三步从一只碗开始实测落点误差，再逐渐测试多只碗。当前只支持一只长短边明显不同的矩形薄托盘；动作时保持静止，不在任务中换托盘或大幅掉头。本次没有增加桌面、托盘和碗的三维碰撞场景。',
     ['New_run/README.md: 收桌面模式','src/yolo_vision/config/clear_table_tray.json','implement_new2.md §10–11'])

# 16 — Takeaway
s = new('A simple loop with explicit evidence at every step', '15 / Key takeaways',
        'Software and simulation validated • physical recognition and placement accuracy remain to be measured',True)
takeaways=[('Re-localize','Use the tray pose from the current observation.'),
           ('Reserve space','Check real footprints and remember occupied slots.'),
           ('Verify before continuing','Confirm the last bowl before picking the next one.')]
for i,(title,body) in enumerate(takeaways):
    y=2.03+i*1.3
    text(s,f'0{i+1}',.77,y,.62,.43,21,'60CEC3',True)
    text(s,title,1.75,y-.03,10.49,.47,28,WHITE,True)
    text(s,body,1.76,y+.62,10.43,.49,20,'C5D7E0')
line(s,.8,6.29,12.47,6.29,'36515F',1)
text(s,'The original grasp and placement motion remain the execution backbone.',.83,6.52,11.5,.33,20,'60CEC3',True)
note(s,'A simple loop with explicit evidence at every step',
     '最后记住三句话就够了：托盘位置每次重新看；空位要按碗的大小和已有占用来选；上一只没有确认放好，就不继续搬下一只。\n托盘使用 YOLO 分割加深度定位，机械臂怎么夹、怎么下降释放、怎么回到起点，仍然沿用原流程。修改范围比较集中，出现问题时也容易知道是在识别、选择、执行还是核查这一步。当前有构建、自动化回归、ROS 通信和 MoveIt 模拟结果作为软件证据。下一阶段还需提供并验证实际托盘模型，连接设备测量识别稳定性和实际放置精度，不能用模拟成功代替实机测量。',
     ['implement_new2.md','debug_output/clear_table_validation/yolo_20261010/summary.json'])

# 17 — Appendix
s = new('Evidence, assets and reproducible entry points', 'Appendix / Traceability')
text(s,'DESIGN & IMPLEMENTATION',.76,1.99,5.6,.31,12,TEAL,True)
for i,(title,path) in enumerate([
    ('Minimal-change design','implement_new2.md'),
    ('Operational guide','New_run/README.md'),
    ('Tray localization and occupancy','src/yolo_vision/yolo_vision/tray_utils.py'),
    ('Round decisions and placement mapping','tools/place_rounds.py')]):
    y=2.54+i*.88
    text(s,title,.77,y,5.62,.33,18,INK,True);text(s,path,.77,y+.39,5.63,.31,12,GRAY)
text(s,'RECORDED EVIDENCE',7.1,1.99,5.55,.31,12,TEAL,True)
text(s,'Validation summary, test log and offline run',7.1,2.56,5.45,.7,20,INK,True)
text(s,'debug_output/clear_table_validation/\nyolo_20261010/',7.1,3.38,5.46,.84,18,GRAY)
text(s,'Historical photographs and overlays',7.1,4.58,5.44,.36,18,INK,True)
text(s,'Reused from the project’s earlier presentation assets;\nall are labeled as historical in this deck.',7.1,5.06,5.48,.72,16,GRAY)
shape(s,.76,6.12,11.91,.61,PALE)
text(s,'Offline demo: ./run_clear_table.sh --offline-demo',.98,6.29,11.48,.3,18,TEAL,True)
note(s,'Evidence, assets and reproducible entry points',
     '这一页是给需要复查的人看的资料索引，不需要在口头报告中逐条念代码路径。设计方案解释为什么这么做，使用说明解释怎么运行，代码实现具体判断，结果目录保存本次测试日志和每轮演示数据。\n运行 ./run_clear_table.sh --offline-demo，可以不连接相机和机械臂重现三只碗的模拟收纳，它跳过实际模型推理。完整构建和隔离测试使用 ./run_pipeline_place_offline_test.sh。PPT 中托盘、空位和流程图是可编辑示意图；五轮演示图由保存的模拟观察数据绘制；现场照片与抓取叠加图来自以前的项目资料。任何说明图都不作为真实实验测量。实际托盘模型依赖和配置见 src/yolo_vision/models/README.md；各页详细来源保存在备注里。',
     ['README.md','run_clear_table.sh','run_pipeline_place_offline_test.sh','output/bowl_research_presentation_20261002/asset_sources.json',
      'src/yolo_vision/models/README.md','debug_output/clear_table_validation/yolo_20261010/summary.json'])

path=OUT/'Movable_Tray_Table_Clearing_EN_CN.pptx'
prs.save(path)
with (OUT/'中文讲解备注.txt').open('w',encoding='utf-8') as f:
    f.write('可移动薄托盘收桌面：英文PPT逐页中文讲解\n日期：2026-10-10\n建议时长：约15–20分钟；第17页为资料附录。\n备注也已写入PPT每页的“备注”区域。\n\n')
    for idx,(title,body) in enumerate(notes,1):
        f.write(f'\n{"="*56}\n第{idx:02d}页  {title}\n{"="*56}\n{body}\n')
assets_manifest={
    'historical_images':{n:str((OLD/n).relative_to(ROOT)) for n in ('raw_table.png','detection.png','grasp_pose.png')},
    'diagrams':'Editable native PowerPoint shapes; explanatory, not measured experimental images.',
    'tray_diagram':'Editable YOLO mask, outer contour, usable interior and local axes; explanatory, not model output.',
    'sequence_charts':'Plotted from yolo_20261010/offline_demo/round_0001..0005/synthetic_observation.json',
    'validation_source':str((EVIDENCE/'summary.json').relative_to(ROOT)),
    'generative_images_used':False,
}
(OUT/'asset_sources.json').write_text(json.dumps(assets_manifest,ensure_ascii=False,indent=2)+'\n')
print(path)
print('Slides:',len(prs.slides),'Notes:',len(notes))
