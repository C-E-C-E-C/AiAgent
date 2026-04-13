<template>
  <div class="employee-page">
    <div class="toolbar">
      <div>
        <h2>员工管理</h2>
        <p>用于测试员工表的增删改查权限。</p>
      </div>
      <div class="toolbar-actions">
        <el-input v-model="keyword" placeholder="按员工姓名筛选" clearable style="width: 220px" @clear="loadList" @keyup.enter="loadList" />
        <el-button @click="loadList">刷新</el-button>
        <el-button type="primary" @click="openCreate" v-permission="'employee:add'">新增员工</el-button>
      </div>
    </div>

    <el-table
      v-loading="loading"
      :data="filteredTableData"
      row-key="id"
      border
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="empName" label="员工姓名" min-width="120" />
      <el-table-column prop="gender" label="性别" width="80">
        <template #default="scope">
          {{ scope.row.gender === 1 ? '男' : '女' }}
        </template>
      </el-table-column>
      <el-table-column prop="age" label="年龄" width="80" />
      <el-table-column prop="deptName" label="所属部门" min-width="120">
        <template #default="scope">
          {{ scope.row.deptName || scope.row.deptId || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="salary" label="薪资" width="120" />
      <el-table-column prop="status" label="状态" width="90">
        <template #default="scope">
          {{ scope.row.status === 1 ? '在职' : '离职' }}
        </template>
      </el-table-column>
      <el-table-column prop="createTime" label="创建时间" min-width="170" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="openEdit(scope.row)" v-permission="'employee:edit'">编辑</el-button>
          <el-button link type="danger" @click="handleRemove(scope.row)" v-permission="'employee:remove'">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px">
      <el-form ref="formRef" :model="form" label-width="90px">
        <el-form-item label="员工姓名" prop="empName">
          <el-input v-model="form.empName" placeholder="请输入员工姓名" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="form.gender" placeholder="请选择性别" style="width: 100%">
            <el-option label="男" :value="1" />
            <el-option label="女" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="年龄" prop="age">
          <el-input-number v-model="form.age" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="所属部门" prop="deptId">
          <el-select v-model="form.deptId" placeholder="请选择部门" style="width: 100%">
            <el-option
              v-for="dept in deptOptions"
              :key="dept.id"
              :label="dept.deptName"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="薪资" prop="salary">
          <el-input-number v-model="form.salary" :min="0" :precision="2" :step="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="在职" :value="1" />
            <el-option label="离职" :value="0" />
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
const dialogTitle = ref('新增员工')
const keyword = ref('')
const tableData = ref([])
const deptOptions = ref([])

const formRef = ref()
const form = reactive({
  id: null,
  empName: '',
  gender: 1,
  age: 0,
  deptId: 1,
  salary: 0,
  status: 1,
})

const authHeaders = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('sa-token')}`,
})

const resetForm = () => {
  form.id = null
  form.empName = ''
  form.gender = 1
  form.age = 0
  form.deptId = 1
  form.salary = 0
  form.status = 1
}

const loadList = async () => {
  loading.value = true
  try {
    const response = await fetch('http://localhost:8080/api/employee/list', {
      method: 'GET',
      headers: authHeaders(),
    })

    const data = await response.json()
    console.log('员工数据:', data)
    tableData.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('Error fetching employee list:', error)
    ElMessage.error('加载员工数据失败')
  } finally {
    loading.value = false
  }
}

const loadDeptList = async () => {
  try {
    const response = await fetch('http://localhost:8080/dept/list', {
      method: 'GET',
      headers: authHeaders(),
    })

    const data = await response.json()
    deptOptions.value = Array.isArray(data) ? data : []
    if (!form.deptId && deptOptions.value.length > 0) {
      form.deptId = deptOptions.value[0].id
    }
  } catch (error) {
    console.error('Error fetching dept list:', error)
    ElMessage.error('加载部门数据失败')
  }
}

const filteredTableData = computed(() => {
  const text = keyword.value.trim().toLowerCase()
  if (!text) {
    return tableData.value
  }
  return tableData.value.filter((item) => String(item.empName || '').toLowerCase().includes(text))
})

const openCreate = () => {
  resetForm()
  dialogTitle.value = '新增员工'
  dialogVisible.value = true
}

const openEdit = (row) => {
  form.id = row.id
  form.empName = row.empName ?? ''
  form.gender = row.gender ?? 1
  form.age = row.age ?? 0
  form.deptId = row.deptId ?? form.deptId ?? 1
  form.salary = row.salary ?? 0
  form.status = row.status ?? 1
  dialogTitle.value = '编辑员工'
  dialogVisible.value = true
}

const handleSave = async () => {
  saving.value = true
  try {
    const isEdit = !!form.id
    const response = await fetch(`http://localhost:8080/api/employee/${isEdit ? 'edit' : 'add'}`, {
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
    console.error('保存员工失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleRemove = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除员工 ${row.empName} 吗？`, '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const response = await fetch(`http://localhost:8080/api/employee/remove/${row.id}`, {
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
      console.error('删除员工失败:', error)
    }
  }
}

onMounted(() => {
  loadList()
  loadDeptList()
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