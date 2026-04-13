<template>
  <div class="employee-page">
    <div class="toolbar">
      <div>
        <h2>部门管理</h2>
        <p>用于维护部门信息，并支持增删改查。</p>
      </div>
      <div class="toolbar-actions">
        <el-input v-model="keyword" placeholder="按部门名称筛选" clearable style="width: 220px" @clear="loadList" @keyup.enter="loadList" />
        <el-button @click="loadList">刷新</el-button>
        <el-button type="primary" @click="openCreate" v-permission="'dept:add'">新增部门</el-button>
      </div>
    </div>

    <el-table v-loading="loading" :data="filteredTableData" row-key="id" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="deptName" label="部门名称" min-width="160" />
      <el-table-column prop="parentId" label="上级部门" min-width="120">
        <template #default="scope">
          {{ getParentDeptName(scope.row.parentId) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="90">
        <template #default="scope">
          {{ scope.row.status === 1 ? '正常' : '停用' }}
        </template>
      </el-table-column>
      <el-table-column prop="createTime" label="创建时间" min-width="170" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="openEdit(scope.row)" v-permission="'dept:edit'">编辑</el-button>
          <el-button link type="danger" @click="handleRemove(scope.row)" v-permission="'dept:remove'">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px">
      <el-form ref="formRef" :model="form" label-width="90px">
        <el-form-item label="部门名称" prop="deptName">
          <el-input v-model="form.deptName" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="上级部门" prop="parentId">
          <el-select v-model="form.parentId" placeholder="请选择上级部门" style="width: 100%">
            <el-option :value="0" label="无上级部门" />
            <el-option v-for="dept in deptOptions" :key="dept.id" :label="dept.deptName" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="正常" :value="1" />
            <el-option label="停用" :value="0" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增部门')
const keyword = ref('')
const tableData = ref([])
const deptOptions = ref([])

const formRef = ref()
const form = reactive({
  id: null,
  deptName: '',
  parentId: 0,
  status: 1,
})

const authHeaders = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('sa-token')}`,
})

const resetForm = () => {
  form.id = null
  form.deptName = ''
  form.parentId = 0
  form.status = 1
}

const loadList = async () => {
  loading.value = true
  try {
    const response = await fetch('http://localhost:8080/dept/list', {
      method: 'GET',
      headers: authHeaders(),
    })
    const data = await response.json()
    tableData.value = Array.isArray(data) ? data : []
    deptOptions.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('Error fetching dept list:', error)
    ElMessage.error('加载部门数据失败')
  } finally {
    loading.value = false
  }
}

const getParentDeptName = (parentId) => {
  if (!parentId || parentId === 0) {
    return '无上级部门'
  }
  const parent = deptOptions.value.find((dept) => dept.id === parentId)
  return parent?.deptName || `#${parentId}`
}

const filteredTableData = computed(() => {
  const text = keyword.value.trim().toLowerCase()
  if (!text) {
    return tableData.value
  }
  return tableData.value.filter((item) => String(item.deptName || '').toLowerCase().includes(text))
})

const openCreate = () => {
  resetForm()
  dialogTitle.value = '新增部门'
  dialogVisible.value = true
}

const openEdit = (row) => {
  form.id = row.id
  form.deptName = row.deptName ?? ''
  form.parentId = row.parentId ?? 0
  form.status = row.status ?? 1
  dialogTitle.value = '编辑部门'
  dialogVisible.value = true
}

const handleSave = async () => {
  saving.value = true
  try {
    const isEdit = !!form.id
    const response = await fetch(`http://localhost:8080/dept/${isEdit ? 'edit' : 'add'}`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(form),
    })
    const text = await response.text()
    if (!response.ok) {
      throw new Error(text || '保存失败')
    }
    ElMessage.success(isEdit ? '修改成功' : '新增成功')
    dialogVisible.value = false
    await loadList()
  } catch (error) {
    console.error('保存部门失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleRemove = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除部门 ${row.deptName} 吗？`, '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    const response = await fetch(`http://localhost:8080/dept/remove/${row.id}`, {
      method: 'GET',
      headers: authHeaders(),
    })
    const text = await response.text()
    if (!response.ok) {
      throw new Error(text || '删除失败')
    }
    ElMessage.success('删除成功')
    await loadList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除部门失败:', error)
    }
  }
}

onMounted(() => {
  loadList()
})
</script>

<style scoped>
.employee-page {
  min-height: 100%;
  padding: 24px;
  background: #f8fafc;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.toolbar h2 {
  margin: 0 0 6px;
  color: #0f172a;
}

.toolbar p {
  margin: 0;
  color: #64748b;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

@media (max-width: 960px) {
  .toolbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .toolbar-actions {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>