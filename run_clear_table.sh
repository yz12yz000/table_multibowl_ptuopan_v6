#!/usr/bin/env bash
# Thin entry point: the offline branch never loads or discovers ROS/hardware.
set -euo pipefail
clear_table_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
clear_table_offline=false
clear_table_has_config=false
clear_table_has_vision=false
clear_table_args=()
for arg in "$@"; do
    case "$arg" in
        --help|-h)
            cat <<'EOF'
用法：
  ./run_clear_table.sh --offline-demo [--scenario normal|visual|tray_full|missing|unverified] [--output-dir 目录]
  ./run_clear_table.sh [--tray-config 托盘配置.json] [--output-dir 目录] [运行器参数]
  ./run_clear_table.sh --execute [--tray-config 托盘配置.json] [运行器参数]

--offline-demo：无需相机、机械臂或 ROS 环境，用合成观察和模拟接口演示完整循环。
  复用正式任务策略和原抓放执行逻辑；不启动设备、不连接 ROS、不发硬件指令。
  normal 演示三只碗、已有占用、托盘移动和检测编号变化；其他场景演示有限失败退出。
  所有演示数据和结果均为软件模拟，不能代替现场标定或实机验收。
默认在线模式：只规划一只托盘外目标，不移动机械臂或驱动夹爪。
--execute：执行每轮一只抓放，返回后重新观察、确认归位，再处理下一只。
默认现场配置：src/yolo_vision/config/clear_table_live.json（35×23 cm 内侧托盘）。
视觉估计碗尺寸，搜索空位，每个抓取候选计算放置 XY，连续两帧确认放置。
本机附带当前花纹托盘的 YOLOE 视觉参考权重；更换托盘或相机后需重新核验。
原碗模型不含 tray 类别；纯软件演示无需模型，不验证实际识别效果。
在线模式沿用现有相机、TF、MoveIt、返程位姿和已准备好的机器人环境；本脚本不启动硬件。
不能混用 --target-zone、手动 --x/--y/--z 或 --legacy-multi。
EOF
            exit 0
            ;;
        --offline-demo) clear_table_offline=true ;;
        --tray-config|--tray-config=*) clear_table_has_config=true; clear_table_args+=("$arg") ;;
        --vision-config|--vision-config=*) clear_table_has_vision=true; clear_table_args+=("$arg") ;;
        *) clear_table_args+=("$arg") ;;
    esac
done
# Keep ROS/cv_bridge and OpenCV on the system Python dependency set.
export PYTHONNOUSERSITE=1
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"
if "$clear_table_offline"; then
    exec /usr/bin/python3 -B "$clear_table_root/tools/clear_table_offline.py" "${clear_table_args[@]}"
fi
source "$clear_table_root/tools/robot_startup_common.sh"
load_robot_environment
source_setup "$ROBOT_WORKSPACE/install/setup.bash"
if ! "$clear_table_has_config"; then
    clear_table_args+=(--tray-config "$ROBOT_WORKSPACE/src/yolo_vision/config/clear_table_live.json")
fi
if ! "$clear_table_has_vision"; then
    clear_table_args+=(--vision-config "$ROBOT_WORKSPACE/src/yolo_vision/config/clear_table_vision.json")
fi
exec "$ROBOT_PYTHON" -B "$ROBOT_WORKSPACE/tools/test_live_place_pipeline.py" --clear-table "${clear_table_args[@]}"
