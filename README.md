# 机器人抓放工作区

原单碗入口每次处理一只碗，完成抓取、放置、释放、上退和返回固定起点后退出。目标支持左上、左下、中间、右上、右下、blue，或完整的 XYZ 释放坐标。

新增 `run_clear_table.sh` 按 [implement_new2.md](implement_new2.md) 接入收桌面模式：每轮只抓托盘外一只碗，沿用原抓放动作，返回后重新观察；托盘内已有碗用于占用判断，选择其他空位继续放置。托盘位置可在两轮之间改变。

托盘使用独立 YOLOE 分割模型和同帧 RGB-D 定位。本机已整理当前花纹托盘的视觉参考权重，默认现场配置为 `src/yolo_vision/config/clear_table_live.json`，内侧 35 × 23 cm、外侧 36 × 24 cm。碗的中心和占用范围来自点云拟合，不需要逐只填写直径；大碗优先，托盘内搜索空位，每个原始抓取候选单独计算放置 XY，连续两帧确认放好后继续。

```bash
cd /home/rob/robot_grasp_0929demo
./run_clear_table.sh                   # 相机观察和路径预览，不运动
./run_clear_table.sh --execute         # 逐只收纳；满盘或确认失败时停止
./run_clear_table.sh --offline-demo --scenario visual  # 无设备软件演示
```

在线命令沿用已启动的相机、机械臂、TF、MoveIt 和 External Control。当前模型针对已记录的花纹托盘，工作区来自本机固定相机标定；原来的 `clear_table_tray.json` 保留为示例。释放高度和姿态继续使用 blue 示教值，尚未适配所有深浅的碗。25 mm 放置误差余量会限制小托盘容量，不能通过减小余量来代替落点标定。

软件演示使用合成观察和模拟执行接口，不启动硬件。新流程的自动化测试和保存的实拍点云回放不能代替新版本实机验收。使用方式见 [收桌面模式](New_run/README.md#收桌面模式)。

- [启动顺序与控制模式](docs/startup.md)
- [完整抓放参数与日志](New_run/README.md)
- [模块、接口与当前资料索引](docs/README.md)
- [构建与部署](docs/build/linux_build.md)
- [上机检查](docs/build/robot_test_checklist.md)
- [历史资料与归档清单](docs/archive/README.md)

在项目根目录运行：

```bash
./run_pipeline_place_test.sh --target-zone 左上
# 完成现场检查后，独立运行一次真实抓放：
./run_pipeline_place_execute.sh --target-zone 左上
```

根目录脚本是实际入口，`New_run/` 中的同名脚本转发到根目录。现行代码在 `src/` 和 `tools/`；重复脚本、旧控制后端和旧方案已集中归档。历史记录不代表当前参数或已完成实机验收。
