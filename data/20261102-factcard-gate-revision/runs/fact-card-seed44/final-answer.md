# 设计稿送审与客户确认工具：实验设计

## 一、业务理解
系统围绕「设计稿版本演进」构建核心流程：
1. **版本演进链**：设计稿→初稿→多版本迭代→发布→冻结
2. **权限分层**：设计师（上传）→负责人（审核）→客户（意见/确认）→客户确认人（特殊确认权限）
3. **状态机**：
   - 设计稿：待审核/已审核/已发布
   - 版本：草稿/已审核/已发布/已冻结
   - 意见：待处理/已处理/已驳回
   - 确认：未确认/已确认/已驳回

## 二、规则与未知
### 已确认规则
- **F01-F10**（见事实卡）
- 版本冻结后客户只能查看已发布版本
- 修改申请需记录"原确认人+新版本ID+处理时间"
- 意见绑定规则：`opinion.version_id = version.id AND opinion.design_id = version.design_id`

### 待确认问题
- Q1：客户确认后需修改时，是否允许客户直接提交新版本？（当前方案需先提交修改申请）
- Q2：历史版本的只读权限是否包含设计稿编辑权限？（当前方案仅限制版本状态变更）
- Q3：客户确认人是否拥有查看所有历史版本的权限？（当前方案仅允许查看已发布版本）

## 三、关键状态及权限矩阵
| 权限类型       | 设计师 | 负责人 | 客户（非确认人） | 客户确认人 |
|----------------|--------|--------|------------------|------------|
| 上传设计稿     | ✅     | ❌     | ❌               | ❌         |
| 审核版本       | ❌     | ✅     | ❌               | ❌         |
| 发布版本       | ❌     | ✅     | ❌               | ❌         |
| 提交意见       | ❌     | ❌     | ✅               | ✅         |
| 处理意见       | ❌     | ✅     | ❌               | ❌         |
| 确认版本       | ❌     | ❌     | ❌               | ✅         |
| 查看历史版本   | ❌     | ✅     | ✅（已发布）     | ✅（含未发布）|

## 四、数据模型与接口
### 核心实体
```python
class Project:
    id: str
    name: str
    client_confirmer_id: str  # F09

class Design:
    id: str
    project_id: str
    files: List[File]  # 初稿/更新稿

class Version:
    id: str
    design_id: str
    status: Enum('draft', 'reviewed', 'published', 'frozen')  # F02
    files: List[File]  # 各版本文件

class Opinion:
    id: str
    version_id: str  # F06
    design_id: str
    content: str
    page: Optional[int]  # PDF页码
    status: Enum('pending', 'processed', 'rejected')  # F08

class Confirmation:
    id: str
    version_id: str  # F03
    client_id: str
    confirm_time: datetime
    status: Enum('unconfirmed', 'confirmed', 'rejected')  # F07
```

### 接口清单
1. **[POST] /projects**  
   - 参数：项目名称、客户确认人ID  
   - 响应：Project对象

2. **[POST] /designs**  
   - 参数：Project ID、文件列表  
   - 响应：Design对象

3. **[POST] /versions**  
   - 参数：Design ID、文件列表  
   - 响应：Version对象（含status=draft）

4. **[POST] /versions/{id}/review**  
   - 参数：审核结果（pass/fail）  
   - 响应：Version对象（status=reviewed/published）

5. **[POST] /versions/{id}/opinions**  
   - 参数：content, page  
   - 响应：Opinion对象（status=pending）

6. **[PUT] /opinions/{id}/process**  
   - 参数：处理结果（accept/reject）  
   - 响应：Opinion对象（status=processed/rejected）

7. **[POST] /versions/{id}/confirm**  
   - 参数：client_id  
   - 响应：Confirmation对象（status=confirmed）

## 五、实施任务
1. **前端模块**  
   - 项目管理面板（含客户确认人指定功能）  
   - 设计稿版本历史视图（含只读标记）  
   - 意见提交表单（绑定PDF页码）  
   - 确认操作按钮（仅客户确认人可见）

2. **后端服务**  
   - 版本状态机引擎（自动触发F01）  
   - 意见处理状态追踪（F08）  
   - 权限验证中间件（F10）

3. **数据存储**  
   - 版本历史快照（F04）  
   - 确认记录时间戳（F08）  
   - 文件元数据（含下载时间戳）

## 六、可验证验收场景
1. **版本发布验证**  
   - [操作] 审核通过后  
   - [验证] 旧版本状态变为frozen，新版本状态为published，客户仅可见published版本

2. **意见绑定验证**  
   - [操作] 提交意见时未选择版本  
   - [验证] 系统返回400错误，提示"必须绑定具体版本"

3. **确认权限验证**  
   - [操作] 非确认人尝试确认  
   - [验证] 按钮禁用，提示"仅客户确认人可执行此操作"

4. **历史保留验证**  
   - [操作] 发布新版本后  
   - [验证] 旧版本仍可查看且不可编辑，意见记录完整保留

## 七、产品与技术自检
### 产品完整性
- ✅ 覆盖F01-F10全部约束
- ✅ 实现"审核→发布"原子操作
- ✅ 状态机满足F02/F07

### 技术合规性
- ✅ 权限矩阵区分客户确认人与其他客户
- ✅ 接口参数强制绑定version_id
- ✅ 数据模型包含版本冻结状态字段

### 候选建议（不进入本期范围）
- 建议：增加版本对比视图（需确认F02边界）
- 建议：添加修改申请流程（需确认Q1）
- 建议：实现下载时间戳追踪（F10） [end of text]
