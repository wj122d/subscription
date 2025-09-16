#!/bin/bash

# 订阅转换便捷脚本
# 使用方法: ./convert.sh [订阅链接] [选项]

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo -e "${BLUE}订阅转换工具 - 便捷脚本${NC}"
    echo ""
    echo "使用方法:"
    echo "  $0 [订阅链接] [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示此帮助信息"
    echo "  -t, --template      配置模板 (minimal/standard/advanced) [默认: standard]"
    echo "  -f, --format        输出格式 (clash/v2ray) [默认: clash]"
    echo "  -o, --output        输出文件名"
    echo "  --no-filter         不过滤信息节点"
    echo "  --compatible        兼容模式，转换不支持的协议为兼容格式（默认启用）"
    echo "  --no-compatible     禁用兼容模式，保持原始协议"
    echo "  --test              测试模式"
    echo "  --generate-timed    生成带时效的SS链接"
    echo "  --expire            链接过期时间（小时）[默认: 24]"
    echo "  --server            启动订阅服务器"
    echo "  --port              订阅服务器端口 [默认: 8080]"
    echo "  --file              从本地文件读取节点内容"
    echo ""
    echo "示例:"
    echo "  $0 \"https://example.com/subscribe\""
    echo "  $0 \"https://example.com/subscribe\" -t advanced -o my_config.yaml"
    echo "  $0 \"https://example.com/subscribe\" --compatible -o clash_x_config.yaml"
    echo "  $0 --test"
    echo "  $0 \"ss://...\" --generate-timed --expire 48 -o timed_link.txt"
    echo "  $0 \"nodes.txt\" --file --generate-timed --expire 72"
    echo "  $0 \"https://example.com/subscribe\" --server --port 8888"
    echo ""
}

# 检查Python和依赖
check_dependencies() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 未安装${NC}"
        exit 1
    fi
    
    if ! python3 -c "import yaml" &> /dev/null; then
        echo -e "${YELLOW}⚠️  PyYAML 未安装，正在安装...${NC}"
        pip3 install PyYAML --break-system-packages
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ PyYAML 安装失败${NC}"
            exit 1
        fi
    fi
}

# 主函数
main() {
    # 检查是否有参数
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi
    
    # 检查依赖
    check_dependencies
    
    # 构建命令
    cmd="python3 subscription_converter.py"
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            --test)
                cmd="$cmd --test"
                shift
                ;;
            -t|--template)
                cmd="$cmd -t $2"
                shift 2
                ;;
            -f|--format)
                cmd="$cmd -f $2"
                shift 2
                ;;
            -o|--output)
                cmd="$cmd -o $2"
                shift 2
                ;;
            --no-filter)
                cmd="$cmd --no-filter"
                shift
                ;;
            --compatible)
                cmd="$cmd --compatible"
                shift
                ;;
            --no-compatible)
                cmd="$cmd --no-compatible"
                shift
                ;;
            --generate-timed)
                cmd="$cmd --generate-timed"
                shift
                ;;
            --expire)
                cmd="$cmd --expire $2"
                shift 2
                ;;
            --server)
                cmd="$cmd --server"
                shift
                ;;
            --port)
                cmd="$cmd --port $2"
                shift 2
                ;;
            --file)
                cmd="$cmd --file"
                shift
                ;;
            -*)
                echo -e "${RED}❌ 未知选项: $1${NC}"
                show_help
                exit 1
                ;;
            *)
                # 这应该是订阅链接
                cmd="$cmd \"$1\""
                shift
                ;;
        esac
    done
    
    # 执行命令
    echo -e "${GREEN}🚀 执行命令: $cmd${NC}"
    eval $cmd
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 转换完成！${NC}"
    else
        echo -e "${RED}❌ 转换失败！${NC}"
        exit 1
    fi
}

# 运行主函数
main "$@" 