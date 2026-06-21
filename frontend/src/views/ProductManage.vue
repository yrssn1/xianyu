<template>
  <div class="product-manage">
    <div class="page-header">
      <h2>商品管理</h2>
      <a-button type="primary" @click="showCreateModal">
        <template #icon><PlusOutlined /></template>
        新建素材
      </a-button>
    </div>

    <!-- 搜索筛选 -->
    <div class="filter-bar">
      <a-input-search
        v-model:value="searchKeyword"
        placeholder="搜索商品标题"
        style="width: 250px"
        @search="fetchProducts"
      />
      <a-select
        v-model:value="filterCategory"
        placeholder="商品分类"
        allowClear
        style="width: 150px; margin-left: 12px"
        @change="fetchProducts"
      >
        <a-select-option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</a-select-option>
      </a-select>
      <a-select
        v-model:value="filterStatus"
        placeholder="状态"
        allowClear
        style="width: 120px; margin-left: 12px"
        @change="fetchProducts"
      >
        <a-select-option value="draft">草稿</a-select-option>
        <a-select-option value="published">已发布</a-select-option>
        <a-select-option value="offline">已下架</a-select-option>
      </a-select>
    </div>

    <!-- 商品列表 -->
    <a-table
      :columns="columns"
      :data-source="products"
      :loading="loading"
      :pagination="pagination"
      row-key="id"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'title'">
          <div class="product-title">
            <a-avatar
              v-if="record.images && record.images.length > 0"
              :src="record.images[0].image_url"
              shape="square"
              :size="40"
            />
            <a-avatar v-else shape="square" :size="40">
              <template #icon><ShopOutlined /></template>
            </a-avatar>
            <span class="title-text">{{ record.title }}</span>
          </div>
        </template>
        <template v-if="column.key === 'price'">
          <span class="price">¥{{ record.price.toFixed(2) }}</span>
        </template>
        <template v-if="column.key === 'status'">
          <a-tag :color="statusColor(record.status)">{{ statusText(record.status) }}</a-tag>
        </template>
        <template v-if="column.key === 'created_at'">
          {{ formatDate(record.created_at) }}
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="link" size="small" @click="showEditModal(record)">编辑</a-button>
            <a-popconfirm title="确定删除该商品？" @confirm="handleDelete(record.id)">
              <a-button type="link" size="small" danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 新建/编辑弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEdit ? '编辑素材' : '新建素材'"
      :width="700"
      :footer="null"
      @cancel="resetForm"
    >
      <a-form
        :model="formData"
        :rules="formRules"
        ref="formRef"
        layout="vertical"
      >
        <a-form-item label="商品标题" name="title" required>
          <a-input v-model:value="formData.title" placeholder="请输入商品标题" :maxlength="200" />
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="售价（元）" name="price" required>
              <a-input-number
                v-model:value="formData.price"
                :min="0"
                :precision="2"
                placeholder="0.00"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="原价（划线价，选填）" name="original_price">
              <a-input-number
                v-model:value="formData.original_price"
                :min="0"
                :precision="2"
                placeholder="0.00"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="商品分类" name="category">
              <a-select v-model:value="formData.category" placeholder="请选择分类" allowClear>
                <a-select-option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="成色" name="condition">
              <a-select v-model:value="formData.condition">
                <a-select-option value="全新">全新</a-select-option>
                <a-select-option value="几乎全新">几乎全新</a-select-option>
                <a-select-option value="轻微使用痕迹">轻微使用痕迹</a-select-option>
                <a-select-option value="明显使用痕迹">明显使用痕迹</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="品牌（选填）" name="brand">
              <a-input v-model:value="formData.brand" placeholder="请输入品牌" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="发货方式" name="shipping_method">
              <a-select v-model:value="formData.shipping_method">
                <a-select-option value="快递发货">快递发货</a-select-option>
                <a-select-option value="同城面交">同城面交</a-select-option>
                <a-select-option value="虚拟发货">虚拟发货</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="邮费（元，0=包邮）" name="shipping_fee">
              <a-input-number
                v-model:value="formData.shipping_fee"
                :min="0"
                :precision="2"
                placeholder="0"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="宝贝所在地" name="location">
              <a-input v-model:value="formData.location" placeholder="如：北京市朝阳区；仅做素材记录，发布时场" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="商品描述" name="description" required>
          <a-textarea
            v-model:value="formData.description"
            placeholder="请详细描述商品状态、配件、使用情况等"
            :rows="4"
          />
        </a-form-item>

        <a-form-item label="备注（内部使用，不公开）" name="notes">
          <a-input v-model:value="formData.notes" placeholder="选填" />
        </a-form-item>

        <a-form-item label="商品图片（最多9张）">
          <div style="margin-bottom: 12px; font-size: 12px; color: #999">
            支持上传图片、文件夹或压缩包（.zip/.rar）
          </div>
          <div style="display: flex; gap: 12px; margin-bottom: 12px">
            <a-button @click="triggerImageUpload">
              上传图片/压缩包
            </a-button>
            <a-button @click="triggerFolderUpload">
              上传文件夹
            </a-button>
          </div>
          <input
            ref="imageInputRef"
            type="file"
            multiple
            accept="image/*,.zip,.rar"
            style="display: none"
            @change="handleFileSelect"
          />
          <input
            ref="folderInputRef"
            type="file"
            webkitdirectory
            style="display: none"
            @change="handleFolderSelect"
          />
          <a-upload
            v-model:file-list="fileList"
            list-type="picture-card"
            :before-upload="beforeUpload"
            :multiple="false"
          >
            <div v-if="fileList.length < 9">
              <plus-outlined />
              <div style="margin-top: 8px">预览</div>
            </div>
          </a-upload>
        </a-form-item>

        <a-form-item>
          <div style="display: flex; justify-content: flex-end; gap: 12px">
            <a-button @click="resetForm">取消</a-button>
            <a-button type="primary" :loading="submitting" @click="handleSubmit">
              {{ isEdit ? '保存修改' : '创建素材' }}
            </a-button>
          </div>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined, ShopOutlined } from '@ant-design/icons-vue'
import { getProducts, createProduct, updateProduct, deleteProduct, uploadImages } from '../api/product'
import dayjs from 'dayjs'
import JSZip from 'jszip'

const categoryOptions = [
  '数码家电', '服饰鞋包', '家居日用', '图书音像',
  '美妆个护', '母婴用品', '运动户外', '食品生鲜',
  '虚拟商品', '其他',
]

const columns = [
  { title: '商品', key: 'title', dataIndex: 'title', width: 280 },
  { title: '价格', key: 'price', dataIndex: 'price', width: 100 },
  { title: '分类', key: 'category', dataIndex: 'category', width: 100 },
  { title: '状态', key: 'status', dataIndex: 'status', width: 80 },
  { title: '创建时间', key: 'created_at', dataIndex: 'created_at', width: 160 },
  { title: '操作', key: 'action', width: 150 },
]

const products = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const filterCategory = ref(undefined)
const filterStatus = ref(undefined)
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`,
})

const modalVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const formRef = ref(null)
const fileList = ref([])
const imageInputRef = ref(null)
const folderInputRef = ref(null)

const formData = reactive({
  title: '',
  price: 4.88,
  original_price: null,
  category: '虚拟商品',
  condition: '全新',
  brand: '',
  shipping_method: '虚拟发货',
  shipping_fee: 0,
  location: '',
  description: '',
  notes: '',
})

const formRules = {
  title: [{ required: true, message: '请输入商品标题', trigger: 'blur' }],
  price: [{ required: true, message: '请输入售价', trigger: 'blur' }],
  description: [{ required: true, message: '请输入商品描述', trigger: 'blur' }],
}

function statusColor(status) {
  const map = { draft: 'default', published: 'green', offline: 'red' }
  return map[status] || 'default'
}

function statusText(status) {
  const map = { draft: '草稿', published: '已发布', offline: '已下架' }
  return map[status] || status
}

function formatDate(dateStr) {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

async function fetchProducts() {
  loading.value = true
  try {
    const res = await getProducts({
      page: pagination.current,
      page_size: pagination.pageSize,
      keyword: searchKeyword.value || undefined,
      category: filterCategory.value || undefined,
      status: filterStatus.value || undefined,
    })
    products.value = res.data.items
    pagination.total = res.data.total
  } catch (err) {
    message.error('获取商品列表失败')
  } finally {
    loading.value = false
  }
}

function handleTableChange(pag) {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchProducts()
}

function showCreateModal() {
  isEdit.value = false
  editingId.value = null
  modalVisible.value = true
}

function showEditModal(record) {
  isEdit.value = true
  editingId.value = record.id
  Object.assign(formData, {
    title: record.title,
    price: record.price,
    original_price: record.original_price,
    category: record.category,
    condition: record.condition,
    brand: record.brand,
    shipping_method: record.shipping_method,
    shipping_fee: record.shipping_fee,
    location: record.location,
    description: record.description,
    notes: record.notes,
  })
  fileList.value = (record.images || []).map((img) => ({
    uid: `image-${img.id}`,
    name: img.image_url.split('/').pop(),
    status: 'done',
    url: img.image_url,
  }))
  modalVisible.value = true
}

function resetForm() {
  modalVisible.value = false
  Object.assign(formData, {
    title: '',
    price: 4.88,
    original_price: null,
    category: '虚拟商品',
    condition: '全新',
    brand: '',
    shipping_method: '虚拟发货',
    shipping_fee: 0,
    location: '',
    description: '',
    notes: '',
  })
  fileList.value = []
  formRef.value?.resetFields()
}

function beforeUpload(file) {
  return false
}

function triggerImageUpload() {
  imageInputRef.value?.click()
}

function triggerFolderUpload() {
  folderInputRef.value?.click()
}

async function handleFileSelect(event) {
  const files = Array.from(event.target.files || [])
  for (const file of files) {
    const isZip = file.name.endsWith('.zip') || file.name.endsWith('.rar')
    const isImage = file.type.startsWith('image/')

    if (isZip) {
      try {
        await extractImagesFromZip(file)
      } catch (err) {
        message.error(`解析 ${file.name} 失败：${err.message}`)
      }
    } else if (isImage) {
      addImageFile(file)
    }
  }
  event.target.value = ''
}

async function handleFolderSelect(event) {
  const files = Array.from(event.target.files || [])
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
  
  for (const file of files) {
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
    if (imageExtensions.includes(ext)) {
      addImageFile(file)
    }
  }
  event.target.value = ''
}

function addImageFile(file) {
  if (fileList.value.length >= 9) {
    message.warning('最多上传9张图片')
    return
  }

  const newFile = {
    uid: `${Date.now()}-${Math.random()}`,
    name: file.name,
    status: 'done',
    originFileObj: file,
    url: URL.createObjectURL(file),
  }
  
  fileList.value.push(newFile)
}

async function extractImagesFromZip(zipFile) {
  const zip = new JSZip()
  const zipContent = await zip.loadAsync(zipFile)
  
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
  const imageFiles = []

  zipContent.forEach((relativePath, file) => {
    if (!file.dir) {
      const ext = relativePath.substring(relativePath.lastIndexOf('.')).toLowerCase()
      if (imageExtensions.includes(ext)) {
        imageFiles.push({ path: relativePath, file })
      }
    }
  })

  if (imageFiles.length === 0) {
    message.warning(`${zipFile.name} 中没有找到图片文件`)
    return
  }

  let addedCount = 0
  for (const { path, file } of imageFiles) {
    if (fileList.value.length >= 9) {
      break
    }
    
    const blob = await file.async('blob')
    const filename = path.split('/').pop()
    
    const newFile = {
      uid: `${Date.now()}-${Math.random()}`,
      name: filename,
      status: 'done',
      originFileObj: new File([blob], filename, { type: blob.type }),
      url: URL.createObjectURL(blob),
    }
    
    fileList.value.push(newFile)
    addedCount++
  }

  if (addedCount < imageFiles.length) {
    message.warning(`${zipFile.name} 中有 ${imageFiles.length} 张图片，只添加了前 ${addedCount} 张（最多9张）`)
  } else {
    message.success(`成功从 ${zipFile.name} 提取 ${addedCount} 张图片`)
  }
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    const payload = { ...formData }
    if (!payload.original_price) payload.original_price = null
    if (!payload.brand) payload.brand = null
    if (!payload.location) payload.location = null
    if (!payload.notes) payload.notes = null

    let productId
    if (isEdit.value) {
      await updateProduct(editingId.value, payload)
      productId = editingId.value
      message.success('修改成功')
    } else {
      const res = await createProduct(payload)
      productId = res.data.id
      message.success('创建成功')
    }

    // 上传新图片（排除已存在的图片）
    const newFiles = fileList.value
      .filter((f) => !f.uid.toString().startsWith('image-'))
      .map((f) => f.originFileObj)
    if (newFiles.length > 0) {
      await uploadImages(productId, newFiles)
    }

    resetForm()
    fetchProducts()
  } catch (err) {
    message.error(isEdit.value ? '修改失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id) {
  try {
    await deleteProduct(id)
    message.success('删除成功')
    fetchProducts()
  } catch {
    message.error('删除失败')
  }
}

fetchProducts()
</script>

<style scoped>
.product-manage {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
}

.filter-bar {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.product-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

.price {
  color: #f5222d;
  font-weight: 500;
}
</style>
