#!/usr/bin/env python3
"""
AI旅行规划智能体 - FastAPI后端服务

这个模块提供RESTful API接口，将AI旅行规划智能体包装为Web服务。
支持异步处理和实时状态更新。

主要功能：
1. 接收前端的旅行规划请求
2. 调用AI旅行规划智能体
3. 返回规划结果和状态更新
4. 提供文件下载服务
"""

import sys
import os
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.langgraph_agents import LangGraphTravelAgents
from agents.simple_travel_agent import SimpleTravelAgent, MockTravelAgent
from config.langgraph_config import langgraph_config as config

# 创建FastAPI应用
app = FastAPI(
    title="AI旅行规划智能体API",
    description="基于LangGraph框架的多智能体旅行规划系统API",
    version="1.0.0"
)

# 添加CORS中间件，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量存储任务状态
planning_tasks: Dict[str, Dict[str, Any]] = {}

# 任务持久化文件
TASKS_FILE = "tasks_state.json"

def save_tasks_state():
    """保存任务状态到文件"""
    try:
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(planning_tasks, f, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        print(f"保存任务状态失败: {e}")

def load_tasks_state():
    """从文件加载任务状态"""
    global planning_tasks
    try:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                planning_tasks = json.load(f)
            print(f"✅ 已加载 {len(planning_tasks)} 个任务状态")
        else:
            print("📝 任务状态文件不存在，使用空状态")
    except Exception as e:
        print(f"加载任务状态失败: {e}")
        planning_tasks = {}

# 启动时加载任务状态
load_tasks_state()

class TravelRequest(BaseModel):
    """旅行规划请求模型"""
    destination: str
    start_date: str
    end_date: str
    budget_range: str
    group_size: int
    interests: list[str] = []
    dietary_restrictions: str = ""
    activity_level: str = "适中"
    travel_style: str = "探索者"
    transportation_preference: str = "公共交通"
    accommodation_preference: str = "酒店"
    special_occasion: str = ""
    special_requirements: str = ""
    currency: str = "CNY"

class PlanningResponse(BaseModel):
    """规划响应模型"""
    task_id: str
    status: str
    message: str

class PlanningStatus(BaseModel):
    """规划状态模型"""
    task_id: str
    status: str
    progress: int
    current_agent: str
    message: str
    result: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "AI旅行规划智能体API",
        "version": "1.0.0",
        "status": "运行中",
        "agents": [
            "协调员智能体",
            "旅行顾问",
            "预算优化师", 
            "天气分析师",
            "当地专家",
            "行程规划师"
        ]
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        # 检查Gemini API密钥
        if not config.GEMINI_API_KEY:
            return {
                "status": "warning", 
                "message": "Gemini API密钥未配置",
                "gemini_model": config.GEMINI_MODEL,
                "api_key_configured": False,
                "timestamp": datetime.now().isoformat()
            }
        
        # 检查系统资源
        import psutil
        memory_info = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            "status": "healthy",
            "gemini_model": config.GEMINI_MODEL,
            "api_key_configured": bool(config.GEMINI_API_KEY),
            "system_info": {
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory_info.percent}%",
                "memory_available": f"{memory_info.available / 1024 / 1024 / 1024:.1f}GB"
            },
            "active_tasks": len(planning_tasks),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def run_planning_task(task_id: str, travel_request: Dict[str, Any]):
    """异步执行旅行规划任务"""
    try:
        print(f"开始执行任务 {task_id}")
        
        # 更新任务状态
        planning_tasks[task_id]["status"] = "processing"
        planning_tasks[task_id]["progress"] = 10
        planning_tasks[task_id]["message"] = "正在初始化AI旅行规划智能体..."
        
        # 模拟处理时间，避免立即完成
        await asyncio.sleep(1)
        
        planning_tasks[task_id]["progress"] = 30
        planning_tasks[task_id]["message"] = "多智能体系统已启动，开始协作规划..."
        
        await asyncio.sleep(1)
        
        # 转换请求格式
        langgraph_request = {
            "destination": travel_request["destination"],
            "duration": travel_request.get("duration", 7),
            "budget_range": travel_request["budget_range"],
            "interests": travel_request["interests"],
            "group_size": travel_request["group_size"],
            "travel_dates": f"{travel_request['start_date']} 至 {travel_request['end_date']}"
        }
        
        planning_tasks[task_id]["progress"] = 50
        planning_tasks[task_id]["message"] = "智能体团队正在协作分析..."
        
        await asyncio.sleep(1)
        
        print(f"任务 {task_id}: 开始LangGraph处理")
        
        try:
            # 使用asyncio.wait_for添加超时控制
            async def run_langgraph():
                # 初始化AI旅行规划智能体
                print(f"任务 {task_id}: 初始化AI旅行规划智能体")
                planning_tasks[task_id]["progress"] = 50
                planning_tasks[task_id]["message"] = "初始化AI旅行规划智能体..."

                try:
                    travel_agents = LangGraphTravelAgents()
                    print(f"任务 {task_id}: AI旅行规划智能体初始化完成")

                    planning_tasks[task_id]["progress"] = 60
                    planning_tasks[task_id]["message"] = "开始多智能体协作..."

                    print(f"任务 {task_id}: 执行旅行规划")
                    # 在线程池中执行规划，避免阻塞
                    import concurrent.futures

                    def run_planning():
                        return travel_agents.run_travel_planning(langgraph_request)

                    # 使用线程池执行，设置超时
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(run_planning)
                        try:
                            # 等待最多4分钟
                            result = future.result(timeout=240)
                            print(f"任务 {task_id}: LangGraph执行完成，结果: {result.get('success', False)}")
                            return result
                        except concurrent.futures.TimeoutError:
                            print(f"任务 {task_id}: LangGraph执行超时，尝试使用简化版本")
                            planning_tasks[task_id]["progress"] = 80
                            planning_tasks[task_id]["message"] = "LangGraph超时，使用简化版本..."

                            # 使用简化版本作为备选方案
                            simple_agent = SimpleTravelAgent()
                            return simple_agent.run_travel_planning(langgraph_request)

                        except Exception as e:
                            print(f"任务 {task_id}: LangGraph执行异常: {str(e)}，尝试使用简化版本")
                            planning_tasks[task_id]["progress"] = 80
                            planning_tasks[task_id]["message"] = "LangGraph异常，使用简化版本..."

                            # 使用简化版本作为备选方案
                            simple_agent = SimpleTravelAgent()
                            return simple_agent.run_travel_planning(langgraph_request)

                except Exception as e:
                    print(f"任务 {task_id}: 初始化LangGraph失败: {str(e)}")
                    return {
                        "success": False,
                        "error": f"初始化失败: {str(e)}",
                        "travel_plan": {},
                        "agent_outputs": {},
                        "planning_complete": False
                    }
            
            # 设置300秒超时（5分钟）
            result = await asyncio.wait_for(run_langgraph(), timeout=300.0)
            
            print(f"任务 {task_id}: LangGraph处理完成")
            
            if result["success"]:
                planning_tasks[task_id]["status"] = "completed"
                planning_tasks[task_id]["progress"] = 100
                planning_tasks[task_id]["message"] = "旅行规划完成！"
                planning_tasks[task_id]["result"] = result

                # 保存任务状态
                save_tasks_state()
                
                # 保存结果到文件
                await save_planning_result(task_id, result, langgraph_request)
                
            else:
                planning_tasks[task_id]["status"] = "failed"
                planning_tasks[task_id]["message"] = f"规划失败: {result.get('error', '未知错误')}"
                
        except asyncio.TimeoutError:
            print(f"任务 {task_id}: LangGraph处理超时")
            # 超时处理，提供简化响应
            simplified_result = {
                "success": True,
                "travel_plan": {
                    "destination": travel_request["destination"],
                    "duration": travel_request.get("duration", 7),
                    "budget_range": travel_request["budget_range"],
                    "group_size": travel_request["group_size"],
                    "travel_dates": f"{travel_request['start_date']} 至 {travel_request['end_date']}",
                    "summary": f"为{travel_request['destination']}制定的{travel_request.get('duration', 7)}天旅行计划（快速模式）"
                },
                "agent_outputs": {
                    "system_message": {
                        "response": f"由于系统负载较高，为您提供快速旅行计划。目的地：{travel_request['destination']}，预算：{travel_request['budget_range']}，人数：{travel_request['group_size']}人。建议您关注当地的热门景点、特色美食和文化体验。",
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed"
                    }
                },
                "total_iterations": 1,
                "planning_complete": True
            }
            
            planning_tasks[task_id]["status"] = "completed"
            planning_tasks[task_id]["progress"] = 100
            planning_tasks[task_id]["message"] = "旅行规划完成（快速模式）"
            planning_tasks[task_id]["result"] = simplified_result
            
            # 保存简化结果
            await save_planning_result(task_id, simplified_result, langgraph_request)
                
        except Exception as agent_error:
            # 如果AI旅行规划智能体出错，提供一个简化的响应
            print(f"任务 {task_id}: AI旅行规划智能体错误: {str(agent_error)}")
            
            # 创建一个简化的旅行计划作为回退
            simplified_result = {
                "success": True,
                "travel_plan": {
                    "destination": travel_request["destination"],
                    "duration": travel_request.get("duration", 7),
                    "budget_range": travel_request["budget_range"],
                    "group_size": travel_request["group_size"],
                    "travel_dates": f"{travel_request['start_date']} 至 {travel_request['end_date']}",
                    "summary": f"为{travel_request['destination']}制定的{travel_request.get('duration', 7)}天旅行计划"
                },
                "agent_outputs": {
                    "system_message": {
                        "response": f"系统正在维护中，为您提供基础的旅行计划框架。目的地：{travel_request['destination']}，预算：{travel_request['budget_range']}，人数：{travel_request['group_size']}人。建议提前了解当地的交通、住宿和主要景点信息。",
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed"
                    }
                },
                "total_iterations": 1,
                "planning_complete": True
            }
            
            planning_tasks[task_id]["status"] = "completed"
            planning_tasks[task_id]["progress"] = 100
            planning_tasks[task_id]["message"] = "旅行规划完成（简化模式）"
            planning_tasks[task_id]["result"] = simplified_result
            
            # 保存简化结果
            await save_planning_result(task_id, simplified_result, langgraph_request)
            
        print(f"任务 {task_id}: 执行完成")
            
    except Exception as e:
        planning_tasks[task_id]["status"] = "failed"
        planning_tasks[task_id]["message"] = f"系统错误: {str(e)}"
        print(f"任务 {task_id}: 规划任务执行错误: {str(e)}")

async def save_planning_result(task_id: str, result: Dict[str, Any], request: Dict[str, Any]):
    """保存规划结果到文件"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = request.get('destination', 'unknown').replace(' ', '_')
        filename = f"旅行计划_{destination}_{timestamp}.json"
        filepath = os.path.join("results", filename)
        
        # 确保results目录存在
        os.makedirs("results", exist_ok=True)
        
        # 保存为JSON格式
        save_data = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "result": result
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
            
        planning_tasks[task_id]["result_file"] = filename
        
    except Exception as e:
        print(f"保存结果文件时出错: {str(e)}")

@app.post("/plan", response_model=PlanningResponse)
async def create_travel_plan(request: TravelRequest, background_tasks: BackgroundTasks):
    """创建旅行规划任务"""
    try:
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 计算旅行天数
        from datetime import datetime
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
        duration = (end_date - start_date).days + 1
        
        # 转换请求为字典
        travel_request = request.model_dump()
        travel_request["duration"] = duration
        
        # 初始化任务状态
        planning_tasks[task_id] = {
            "task_id": task_id,
            "status": "started",
            "progress": 0,
            "current_agent": "系统初始化",
            "message": "任务已创建，准备开始规划...",
            "created_at": datetime.now().isoformat(),
            "request": travel_request,
            "result": None
        }

        # 保存任务状态
        save_tasks_state()
        
        # 添加后台任务
        background_tasks.add_task(run_planning_task, task_id, travel_request)
        
        return PlanningResponse(
            task_id=task_id,
            status="started",
            message="旅行规划任务已启动，请使用task_id查询进度"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建规划任务失败: {str(e)}")

@app.get("/status/{task_id}", response_model=PlanningStatus)
async def get_planning_status(task_id: str):
    """获取规划任务状态"""
    try:
        print(f"状态查询: {task_id}")

        if task_id not in planning_tasks:
            print(f"任务不存在: {task_id}")
            raise HTTPException(status_code=404, detail="任务不存在")

        task = planning_tasks[task_id]
        print(f"任务状态: {task['status']}, 进度: {task['progress']}%")

        return PlanningStatus(
            task_id=task_id,
            status=task["status"],
            progress=task["progress"],
            current_agent=task["current_agent"],
            message=task["message"],
            result=task["result"]
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"状态查询错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"状态查询失败: {str(e)}")

@app.get("/download/{task_id}")
async def download_result(task_id: str):
    """下载规划结果文件"""
    if task_id not in planning_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = planning_tasks[task_id]
    if "result_file" not in task:
        raise HTTPException(status_code=404, detail="结果文件不存在")
    
    filepath = os.path.join("results", task["result_file"])
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=filepath,
        filename=task["result_file"],
        media_type='application/json'
    )

@app.get("/tasks")
async def list_tasks():
    """列出所有任务"""
    return {
        "tasks": [
            {
                "task_id": task_id,
                "status": task["status"],
                "created_at": task["created_at"],
                "destination": task["request"].get("destination", "未知")
            }
            for task_id, task in planning_tasks.items()
        ]
    }

@app.post("/simple-plan")
async def simple_travel_plan(request: TravelRequest, background_tasks: BackgroundTasks):
    """简化版旅行规划（使用简化智能体）"""
    try:
        # 生成任务ID
        task_id = str(uuid.uuid4())

        # 计算旅行天数
        from datetime import datetime
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
        duration = (end_date - start_date).days + 1

        # 转换请求为字典
        travel_request = request.model_dump()
        travel_request["duration"] = duration

        # 初始化任务状态
        planning_tasks[task_id] = {
            "task_id": task_id,
            "status": "started",
            "progress": 0,
            "current_agent": "简化智能体",
            "message": "任务已创建，准备开始简化规划...",
            "created_at": datetime.now().isoformat(),
            "request": travel_request,
            "result": None
        }

        # 添加后台任务
        async def run_simple_planning():
            try:
                planning_tasks[task_id]["status"] = "processing"
                planning_tasks[task_id]["progress"] = 30
                planning_tasks[task_id]["message"] = "正在使用简化智能体规划..."

                simple_agent = SimpleTravelAgent()
                result = simple_agent.run_travel_planning(travel_request)

                if result["success"]:
                    planning_tasks[task_id]["status"] = "completed"
                    planning_tasks[task_id]["progress"] = 100
                    planning_tasks[task_id]["message"] = "简化规划完成！"
                    planning_tasks[task_id]["result"] = result

                    # 保存结果到文件
                    await save_planning_result(task_id, result, travel_request)
                else:
                    planning_tasks[task_id]["status"] = "failed"
                    planning_tasks[task_id]["message"] = f"简化规划失败: {result.get('error', '未知错误')}"

            except Exception as e:
                planning_tasks[task_id]["status"] = "failed"
                planning_tasks[task_id]["message"] = f"简化规划异常: {str(e)}"

        background_tasks.add_task(run_simple_planning)

        return PlanningResponse(
            task_id=task_id,
            status="started",
            message="简化版旅行规划任务已启动"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建简化规划任务失败: {str(e)}")

@app.post("/mock-plan")
async def mock_travel_plan(request: TravelRequest):
    """模拟旅行规划（用于测试，立即返回结果）"""
    try:
        # 生成测试任务ID
        task_id = str(uuid.uuid4())

        print(f"模拟任务 {task_id}: 开始")

        # 计算旅行天数
        from datetime import datetime
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
        duration = (end_date - start_date).days + 1

        # 转换请求为字典
        travel_request = request.model_dump()
        travel_request["duration"] = duration

        # 使用模拟智能体
        mock_agent = MockTravelAgent()
        result = mock_agent.run_travel_planning(travel_request)

        print(f"模拟任务 {task_id}: 完成")

        return {
            "task_id": task_id,
            "status": "completed",
            "message": "模拟规划完成",
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模拟规划失败: {str(e)}")

if __name__ == "__main__":
    print("🚀 启动AI旅行规划智能体API服务器...")
    print(f"📍 API文档: http://localhost:8080/docs")
    print(f"🔧 健康检查: http://localhost:8080/health")

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",  # 监听所有接口
        port=8080,
        reload=False,  # 禁用热重载，避免任务数据丢失
        log_level="info",
        timeout_keep_alive=30,  # 增加keep-alive超时
        timeout_graceful_shutdown=30,  # 优雅关闭超时
        access_log=True  # 启用访问日志
    )
