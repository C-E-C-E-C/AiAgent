<template>
  <div class="employee-page">
    <div class="toolbar">
      <div>
        <h2>角色管理</h2>
        <p>用于维护角色信息，并为角色分配访问权限。</p>
      </div>
      <div class="toolbar-actions">
        <el-input v-model="keyword" placeholder="按角色标识筛选" clearable style="width: 220px" @clear="loadList" @keyup.enter="loadList" />
        <el-button @click="loadList">刷新</el-button>
        <el-button type="primary" @click="openCreate">新增角色</el-button>
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
      <el-table-column prop="roleKey" label="角色标识" min-width="160" />
      <el-table-column prop="menuIds" label="访问权限" min-width="320">
        <template #default="scope">
          <el-tag
            v-for="menuId in (scope.row.menuIds || [])"
            :key="menuId"
            size="small"
            type="info"
            style="margin-right: 6px; margin-bottom: 4px"
            :title="getMenuPerm(menuId)"
          >
            {{ getMenuLabel(menuId) }}
          </el-tag>
          <span v-if="!scope.row.menuIds || scope.row.menuIds.length === 0">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="menuIds" label="权限数量" width="100">
        <template #default="scope">
          {{ (scope.row.menuIds || []).length }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="openEdit(scope.row)">编辑</el-button>
          <el-button link type="danger" @click="handleRemove(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="620px">
      <el-form ref="formRef" :model="form" label-width="100px">
        <el-form-item label="角色标识" prop="roleKey">
          <el-input v-model="form.roleKey" placeholder="请输入角色标识，例如 admin / hr / sales" />
        </el-form-item>
        <el-form-item label="访问权限" prop="menuIds">
          <div class="permission-box">
            <el-checkbox-group v-model="form.menuIds">
              <el-checkbox
                v-for="menu in menuOptions"
                :key="menu.id"
                :label="menu.id"
                style="display: block; margin-bottom: 10px; white-space: normal; line-height: 1.4"
              >
                  <span class="permission-title">{{ getMenuLabel(menu.id) }}</span>
                  <span class="permission-code">{{ menu.perms }}</span>
              </el-checkbox>
            </el-checkbox-group>
          </div>
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
const dialogTitle = ref('新增角色')
const keyword = ref('')
const tableData = ref([])
const menuOptions = ref([])

const permissionModuleLabels = {
  employee: '员工管理',
  dept: '部门管理',
  user: '用户管理',
  order: '订单管理',
}

const permissionActionLabels = {
  list: '查看列表',
  add: '新增',
  edit: '编辑',
  remove: '删除',
}

const formRef = ref()
const form = reactive({
  id: null,
  roleKey: '',
  menuIds: [],
})

const authHeaders = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('sa-token')}`,
})

const resetForm = () => {
  form.id = null
  form.roleKey = ''
  form.menuIds = []
}

const loadList = async () => {
  loading.value = true
  try {
    const response = await fetch('http://localhost:8080/api/role/list', {
      method: 'GET',
      headers: authHeaders(),
    })

    const data = await response.json()
    tableData.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('Error fetching role list:', error)
    ElMessage.error('加载角色数据失败')
  } finally {
    loading.value = false
  }
}

const loadMenuList = async () => {
  try {
    const response = await fetch('http://localhost:8080/api/role/menus', {
      method: 'GET',
      headers: authHeaders(),
    })

    const data = await response.json()
    menuOptions.value = Array.isArray(data)
      ? [...data].sort((left, right) => String(left.perms || '').localeCompare(String(right.perms || ''), 'zh-Hans-CN'))
      : []
  } catch (error) {
    console.error('Error fetching menu list:', error)
    ElMessage.error('加载权限数据失败')
  }
}

const getMenuLabel = (menuId) => {
  const item = menuOptions.value.find((menu) => menu.id === menuId)
  return item ? formatPermLabel(item.perms) : `#${menuId}`
}

const getMenuPerm = (menuId) => {
  const item = menuOptions.value.find((menu) => menu.id === menuId)
  return item?.perms || `#${menuId}`
}

const formatPermLabel = (perms) => {
  if (!perms || typeof perms !== 'string') {
    return '未知权限'
  }

  const [moduleKey, actionKey] = perms.split(':')
  const moduleLabel = permissionModuleLabels[moduleKey] || moduleKey || '未知模块'
  const actionLabel = permissionActionLabels[actionKey] || actionKey || '未知动作'
  return `${moduleLabel} - ${actionLabel}`
}

const filteredTableData = computed(() => {
  const text = keyword.value.trim().toLowerCase()
  if (!text) {
    return tableData.value
  }
  return tableData.value.filter((item) => String(item.roleKey || '').toLowerCase().includes(text))
})

const openCreate = () => {
  resetForm()
  dialogTitle.value = '新增角色'
  dialogVisible.value = true
}

const openEdit = (row) => {
  form.id = row.id
  form.roleKey = row.roleKey ?? ''
  form.menuIds = Array.isArray(row.menuIds) ? [...row.menuIds] : []
  dialogTitle.value = '编辑角色'
  dialogVisible.value = true
}

const handleSave = async () => {
  saving.value = true
  try {
    const isEdit = !!form.id
    const response = await fetch(`http://localhost:8080/api/role/${isEdit ? 'edit' : 'add'}`, {
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
    console.error('保存角色失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleRemove = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除角色 ${row.roleKey} 吗？`, '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const response = await fetch(`http://localhost:8080/api/role/remove/${row.id}`, {
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
      console.error('删除角色失败:', error)
    }
  }
}

onMounted(() => {
  loadList()
  loadMenuList()
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

.permission-box {
  width: 100%;
  max-height: 320px;
  overflow: auto;
  padding: 12px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
}

.permission-title {
  display: block;
  font-size: 14px;
  color: #0f172a;
}

.permission-code {
  display: block;
  font-size: 12px;
  color: #94a3b8;
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