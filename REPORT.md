# MCP Agent 项目技术报告

## 项目概述
MCP Agent是一个基于NVIDIA NIM AI的智能代理系统，旨在提供一个简单但功能强大的用户界面来与AI代理进行交互。该项目的主要目标是构建一个易用的AI助手界面，使用户能够方便地与AI进行对话和任务处理。

### 背景
随着AI技术的快速发展，需要一个简单直观的界面来让用户与AI代理进行交互。本项目正是为了满足这一需求而开发的。

### 要解决的问题
- 简化AI代理的使用流程
- 提供直观的用户界面
- 确保系统的可靠性和稳定性

## 技术栈概述
- AI框架：
  - LangChain：用于AI应用程序的开发框架
  - NVIDIA NIM：提供底层LLM模型支持
- 任务编排：自定义任务链实现
- 虚拟环境：Python venv
- 用户界面：Gradio UI
- 部署工具：Bash脚本(setup.sh)

## 系统架构与实现

### MCP服务与客户端构建
1. 基于LangChain框架构建AI应用逻辑
2. 集成NVIDIA NIM提供的LLM能力

### Agentic AI平台框架实现
- mcp_tools.py 管理所有 mcp tool 方法
- agent_gr_ui.py 调用 mcp_tools.py 实现 agentic AI
- 基于LangChain实现智能任务链
- 利用NVIDIA NIM模型处理自然语言交互
- 采用模块化设计，便于扩展和维护
- 实现了基础的对话功能: web_seach 功能

### 技术创新点
1. 可扩展的架构设计
   - 基于LangChain的模块化任务链
   - 灵活的模型接入机制, 依赖于 NVIDIA NIM 提供的开箱即用的模型


## 团队贡献
- 架构设计：Alan
- MCP tools：Alan, Yvonne
- Agentic UI：Yvonne
- 测试与部署：Alan

## 未来展望

### 目标
1. 增强AI代理的功能
2. 优化用户界面体验
3. 添加更多 mcp tool
4. 优化 mcp tool 注册与调用机制
5. 优化 agentic UI 的交互体验

## 总结
MCP Agent 该项目通过使用LangChain框架和NVIDIA NIM模型，实现了智能任务链和自然语言交互。通过模块化设计，该项目具有良好的可扩展性和维护性。