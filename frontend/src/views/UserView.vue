<template>
  <div class="employee-page">
    <div class="toolbar">
      <div>
        <h2>用户管理</h2>
        <p>用于维护用户信息，并支持分配部门和角色。</p>
      </div>
      <div class="toolbar-actions">
        <el-input v-model="keyword" placeholder="按用户名筛选" clearable style="width: 220px" @clear="loadList" @keyup.enter="loadList" />
        <el-button @click="loadList">刷新</el-button>
        <el-button type="primary" @click="openCreate" v-permission="'sys:user:add'">新增用户</el-button>
      </div>
    </div>

    <el-table v-loading="loading" :data="filteredTableData" row-key="id" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" min-width="140" />
      <el-table-column prop="nickName" label="昵称" min-width="140" />
      <el-table-column prop="deptName" label="所属部门" min-width="120">
        <template #default="scope">
          {{ scope.row.deptName || scope.row.deptId || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="roleKey" label="角色" min-width="120">
        <template #default="scope">
          {{ scope.row.roleKey || scope.row.roleId || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="90">
        <template #default="scope">
          {{ scope.row.status === 1 ? '正常' : '禁用' }}
        </template>
      </el-table-column>
      <el-table-column prop="createTime" label="创建时间" min-width="170" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="openEdit(scope.row)" v-permission="'sys:user:edit'">编辑</el-button>
          <el-button link type="danger" @click="handleRemove(scope.row)" v-permission="'sys:user:remove'">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="560px">
      <el-form ref="formRef" :model="form" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" :placeholder="isEditMode ? '留空表示不修改密码' : '请输入密码'" show-password />
        </el-form-item>
        <el-form-item label="昵称" prop="nickName">
          <el-input v-model="form.nickName" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="所属部门" prop="deptId">
          <el-select v-model="form.deptId" placeholder="请选择部门" style="width: 100%">
            <el-option v-for="dept in deptOptions" :key="dept.id" :label="dept.deptName" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="roleId">
          <el-select v-model="form.roleId" placeholder="请选择角色" style="width: 100%">
            <el-option v-for="role in roleOptions" :key="role.id" :label="role.roleKey" :value="role.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="正常" :value="1" />
            <el-option label="禁用" :value="0" />
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
const dialogTitle = ref('新增用户')
const keyword = ref('')
const tableData = ref([])
const deptOptions = ref([])
const roleOptions = ref([])

const formRef = ref()
const form = reactive({
  id: null,
  username: '',
  password: '',
  nickName: '',
  deptId: 0,
  roleId: null,
  status: 1,
})

const isEditMode = computed(() => !!form.id)

const authHeaders = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('sa-token')}`,
})

const resetForm = () => {
  form.id = null
  form.username = ''
  form.password = ''
  form.nickName = ''
  form.deptId = 0
  form.roleId = null
  form.status = 1
}

const loadList = async () => {
  loading.value = true
  try {
    const response = await fetch('http://localhost:8080/user/list', {
      method: 'GET',
      headers: authHeaders(),
    })
    const data = await response.json()
    tableData.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('Error fetching user list:', error)
    ElMessage.error('加载用户数据失败')
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

const loadRoleList = async () => {
  try {
    const response = await fetch('http://localhost:8080/api/role/list', {
      method: 'GET',
      headers: authHeaders(),
    })
    const data = await response.json()
    roleOptions.value = Array.isArray(data) ? data : []
    if (!form.roleId && roleOptions.value.length > 0) {
      form.roleId = roleOptions.value[0].id
    }
  } catch (error) {
    console.error('Error fetching role list:', error)
    ElMessage.error('加载角色数据失败')
  }
}

const filteredTableData = computed(() => {
  const text = keyword.value.trim().toLowerCase()
  if (!text) {
    return tableData.value
  }
  return tableData.value.filter((item) => String(item.username || '').toLowerCase().includes(text))
})

const openCreate = () => {
  resetForm()
  if (deptOptions.value.length > 0) {
    form.deptId = deptOptions.value[0].id
  }
  if (roleOptions.value.length > 0) {
    form.roleId = roleOptions.value[0].id
  }
  dialogTitle.value = '新增用户'
  dialogVisible.value = true
}

const openEdit = (row) => {
  form.id = row.id
  form.username = row.username ?? ''
  form.password = ''
  form.nickName = row.nickName ?? ''
  form.deptId = row.deptId ?? 0
  form.roleId = row.roleId ?? null
  form.status = row.status ?? 1
  dialogTitle.value = '编辑用户'
  dialogVisible.value = true
}

const handleSave = async () => {
  saving.value = true
  try {
    const isEdit = !!form.id
    const payload = { ...form }

    if (isEdit && !payload.password) {
      delete payload.password
    }

    if (!isEdit && !payload.password) {
      ElMessage.warning('新增用户时必须填写密码')
      saving.value = false
      return
    }

    const response = await fetch(`http://localhost:8080/user/${isEdit ? 'edit' : 'add'}`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload),
    })
    const text = await response.text()
    if (!response.ok) {
      throw new Error(text || '保存失败')
    }
    ElMessage.success(isEdit ? '修改成功' : '新增成功')
    dialogVisible.value = false
    await loadList()
  } catch (error) {
    console.error('保存用户失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleRemove = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除用户 ${row.username} 吗？`, '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const response = await fetch(`http://localhost:8080/user/remove/${row.id}`, {
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
      console.error('删除用户失败:', error)
    }
  }
}

onMounted(() => {
  loadList()
  loadDeptList()
  loadRoleList()
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