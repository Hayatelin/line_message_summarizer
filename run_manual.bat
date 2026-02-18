@echo off
REM Windows 批處理腳本 - 手動執行一次管道
REM 使用方法: 雙擊此文件或在命令提示符中執行 run_manual.bat

setlocal enabledelayedexpansion

echo.
echo ================================================
echo  LINE 訊息摘要系統 - 手動執行管道
echo ================================================
echo.

REM 檢查虛擬環境
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [OK] 虛擬環境已激活
) else (
    echo [錯誤] 虛擬環境不存在！
    echo 請先運行 setup_windows.ps1
    pause
    exit /b 1
)

echo.
echo [INFO] 執行一次完整管道...
echo [INFO] 這可能需要 2-5 分鐘時間
echo.

REM 執行管道
python -c "^
import asyncio^
import sys^
from datetime import datetime^
^
print(f'[開始時間] {datetime.now().strftime(\"%%Y-%%m-%%d %%H:%%M:%%S\")}'  ^
^
try:^
    from src.agent_scheduler import execute_pipeline^
    result = asyncio.run(execute_pipeline())^
    print(f'[完成] {result}'  ^
    print(f'[結束時間] {datetime.now().strftime(\"%%Y-%%m-%%d %%H:%%M:%%S\")}'  ^
except Exception as e:^
    print(f'[錯誤] {str(e)}'  ^
    sys.exit(1)^
"

if %ERRORLEVEL% equ 0 (
    echo.
    echo [OK] 管道執行完成！
    echo.
    echo 查看日誌：
    echo   • 日誌文件位置: logs\execution_YYYY-MM-DD.log
) else (
    echo.
    echo [錯誤] 管道執行失敗！
    echo.
    echo 請檢查：
    echo   • .env 文件是否正確配置
    echo   • 網路連接是否正常
    echo   • API Token 是否有效
)

echo.
pause
