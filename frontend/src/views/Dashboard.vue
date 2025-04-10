<template>
  <div class="dashboard-container">
    <!-- Header with document tabs -->
    <div class="header p-3 flex align-items-center justify-content-between">
      <h1 class="text-xl font-bold">PDF Chat</h1>
      <div class="flex gap-2">
        <Button label="Upload Document" icon="pi pi-upload" @click="showUploadDialog = true" />
        <Button label="Logout" icon="pi pi-sign-out" severity="danger" text @click="logout" />
      </div>
    </div>

    <!-- Main content area with split view -->
    <div class="content-container">
      <!-- Document tabs -->
      <TabView v-if="documents.length > 0" class="document-tabs">
        <TabPanel v-for="doc in documents" :key="doc.id" :header="doc.title">
          <div class="split-view">
            <!-- PDF Viewer -->
            <div class="pdf-container">
              <div v-if="loadingPdf" class="flex align-items-center justify-content-center h-full">
                <ProgressSpinner />
              </div>
              <div v-else-if="currentDocument && !currentDocument.processed" class="flex flex-column align-items-center justify-content-center h-full gap-3">
                <ProgressSpinner />
                <Message severity="info" :closable="false">Document is being processed. This may take a few moments.</Message>
              </div>
              <div v-else-if="currentDocument" class="pdf-viewer-container">
                <div id="pdf-viewer" class="pdf-viewer"></div>
                <div class="pdf-controls p-3 flex align-items-center justify-content-between">
                  <div class="zoom-controls flex gap-2">
                    <Button icon="pi pi-search-minus" text rounded @click="zoomOut" :disabled="pdfScale <= 0.5" />
                    <Button icon="pi pi-search-plus" text rounded @click="zoomIn" />
                    <Button icon="pi pi-download" text rounded @click="downloadPdf" title="Download PDF" />
                  </div>
                  <div class="page-controls flex align-items-center gap-2">
                    <Button icon="pi pi-chevron-left" text rounded @click="prevPage" :disabled="currentPage <= 1" />
                    <span>{{ currentPage }} / {{ totalPages }}</span>
                    <Button icon="pi pi-chevron-right" text rounded @click="nextPage" :disabled="currentPage >= totalPages" />
                  </div>
                </div>
              </div>
              <div v-else class="flex align-items-center justify-content-center h-full">
                <Message severity="info" :closable="false">Select a document to view</Message>
              </div>
            </div>

            <!-- Chat Interface -->
            <div class="chat-container">
              <div class="chat-header p-3 flex align-items-center justify-content-between">
                <h2 class="text-lg font-bold">Chat with {{ currentDocument?.title }}</h2>
                <Button v-if="currentConversation" icon="pi pi-refresh" text rounded @click="createNewConversation" />
              </div>
              
              <div class="chat-messages" ref="chatMessagesRef">
                <div v-if="!currentConversation" class="flex flex-column align-items-center justify-content-center h-full gap-3">
                  <Message severity="info" :closable="false">Start a new conversation</Message>
                  <Button label="New Conversation" @click="createNewConversation" />
                </div>
                <div v-else>
                  <div v-for="(message, index) in messages" :key="index" class="message-container p-3" :class="{'user-message surface-100 border-round-xl ml-4': message.role === 'user', 'assistant-message surface-50 border-round-xl mr-4': message.role === 'assistant'}">
                    <div class="message-content">
                      <p>{{ message.content }}</p>
                      <small class="message-timestamp">{{ new Date(message.created_at).toLocaleTimeString() }}</small>
                    </div>
                  </div>
                  <div v-if="loading" class="message-container assistant-message">
                    <div class="message-content">
                      <ProgressSpinner style="width: 30px; height: 30px" />
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="chat-input p-3">
                <div class="p-inputgroup">
                  <Textarea v-model="messageInput" placeholder="Type your message..." class="w-full" rows="2" @keydown.enter.prevent="sendMessage" />
                  <Button icon="pi pi-send" @click="sendMessage" :disabled="loading || !messageInput.trim()" />
                </div>
              </div>
            </div>
          </div>
        </TabPanel>
      </TabView>
      
      <!-- Empty state when no documents -->
      <div v-else class="flex flex-column align-items-center justify-content-center h-full gap-3">
        <Message severity="info" :closable="false">No documents found. Please upload a document to get started.</Message>
        <Button label="Upload Document" icon="pi pi-upload" @click="showUploadDialog = true" />
      </div>
    </div>

    <!-- Upload Document Dialog -->
    <Dialog v-model:visible="showUploadDialog" header="Upload Document" :style="{width: '35rem', borderRadius: '1rem'}" :modal="true" class="upload-dialog">
      <div class="flex flex-column gap-4 p-5">
        <div class="field">
          <label for="title" class="block mb-3 font-semibold text-lg">Document Title</label>
          <InputText id="title" v-model="uploadForm.title" class="w-full p-3 text-base" placeholder="Enter document title" />
        </div>
        <div class="field">
          <label for="file" class="block mb-3 font-semibold text-lg">PDF File</label>
          <div class="upload-input p-4 border-2 surface-border border-round-lg hover:border-primary transition-colors duration-200">
            <input type="file" id="file" @change="handleFileChange" accept=".pdf" class="w-full" />
          </div>
          <small v-if="uploadError" class="p-error mt-3 block">{{ uploadError }}</small>
        </div>
      </div>
      <template #footer>
        <div class="flex justify-content-end gap-3 pt-4 border-top-1 surface-border">
          <Button label="Cancel" icon="pi pi-times" text @click="showUploadDialog = false" class="w-auto" />
          <Button label="Upload" icon="pi pi-upload" severity="primary" @click="uploadDocument" :loading="uploading" class="w-auto" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useToast } from 'primevue/usetoast'
import Dialog from 'primevue/dialog'

// PDF.js imports
import * as pdfjsLib from 'pdfjs-dist'
import { GlobalWorkerOptions } from 'pdfjs-dist'

// Set worker path for PDF.js
GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`

const router = useRouter()
const toast = useToast()

// State variables
const documents = ref([])
const currentDocument = ref(null)
const currentConversation = ref(null)
const messages = ref([])
const messageInput = ref('')
const loading = ref(false)
const loadingPdf = ref(false)
const chatMessagesRef = ref(null)

// PDF viewer state
const pdfDoc = ref(null)
const currentPage = ref(1)
const totalPages = ref(0)
const pdfScale = ref(1.5)

// Upload dialog state
const showUploadDialog = ref(false)
const uploadForm = ref({ title: '', file: null })
const uploadError = ref('')
const uploading = ref(false)

// Fetch documents on component mount
onMounted(async () => {
  try {
    await fetchDocuments()
    
    // Set up polling for document processing status
    if (documents.value.length > 0) {
      const unprocessedDocs = documents.value.filter(doc => !doc.processed)
      if (unprocessedDocs.length > 0) {
        startProcessingStatusPolling()
      }
    }
  } catch (error) {
    console.error('Error fetching documents:', error)
    if (error.response && error.response.status === 401) {
      logout()
    }
  }
})

// Poll for document processing status
let pollingInterval = null
function startProcessingStatusPolling() {
  // Clear any existing interval
  if (pollingInterval) {
    clearInterval(pollingInterval)
  }
  
  // Check every 5 seconds
  pollingInterval = setInterval(async () => {
    try {
      await fetchDocuments()
      
      // If all documents are processed, stop polling
      const unprocessedDocs = documents.value.filter(doc => !doc.processed)
      if (unprocessedDocs.length === 0 && pollingInterval) {
        clearInterval(pollingInterval)
        pollingInterval = null
      }
    } catch (error) {
      console.error('Error polling document status:', error)
      // Stop polling on error
      if (pollingInterval) {
        clearInterval(pollingInterval)
        pollingInterval = null
      }
    }
  }, 5000)
}

// Cleanup polling when component is unmounted
onUnmounted(() => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
})

// Watch for changes to scroll chat to bottom when messages change
watch(messages, () => {
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  })
})

// Fetch user's documents
async function fetchDocuments() {
  try {
    const response = await axios.get('/api/documents/', {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    documents.value = response.data.results || []
    
    // Set current document to first document if available
    if (documents.value.length > 0 && !currentDocument.value) {
      currentDocument.value = documents.value[0]
      loadPdf(currentDocument.value.file)
      await fetchConversations(currentDocument.value.id)
    }
  } catch (error) {
    console.error('Error fetching documents:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load documents', life: 3000 })
  }
}

// Load PDF document
async function loadPdf(pdfUrl) {
  loadingPdf.value = true
  try {
    const loadingTask = pdfjsLib.getDocument(pdfUrl)
    pdfDoc.value = await loadingTask.promise
    totalPages.value = pdfDoc.value.numPages
    await renderPage(currentPage.value)
  } catch (error) {
    console.error('Error loading PDF:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load PDF document', life: 3000 })
  } finally {
    loadingPdf.value = false
  }
}

// Render a specific page of the PDF
async function renderPage(pageNumber) {
  if (!pdfDoc.value) return
  
  try {
    // Get the page
    const page = await pdfDoc.value.getPage(pageNumber)
    const viewport = page.getViewport({ scale: pdfScale.value })
    
    // Prepare canvas for rendering
    const container = document.getElementById('pdf-viewer')
    if (!container) return
    
    // Clear previous content
    container.innerHTML = ''
    
    // Create canvas element
    const canvas = document.createElement('canvas')
    const context = canvas.getContext('2d')
    canvas.height = viewport.height
    canvas.width = viewport.width
    container.appendChild(canvas)
    
    // Render PDF page
    const renderContext = {
      canvasContext: context,
      viewport: viewport
    }
    await page.render(renderContext).promise
    
    // Update current page
    currentPage.value = pageNumber
  } catch (error) {
    console.error('Error rendering PDF page:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to render PDF page', life: 3000 })
  }
}

// Navigate to the previous page
function prevPage() {
  if (currentPage.value > 1) {
    renderPage(currentPage.value - 1)
  }
}

// Navigate to the next page
function nextPage() {
  if (currentPage.value < totalPages.value) {
    renderPage(currentPage.value + 1)
  }
}

// Zoom in the PDF
function zoomIn() {
  pdfScale.value += 0.25
  renderPage(currentPage.value)
}

// Zoom out the PDF
function zoomOut() {
  if (pdfScale.value > 0.5) {
    pdfScale.value -= 0.25
    renderPage(currentPage.value)
  }
}

// Fetch conversations for a document
async function fetchConversations(documentId) {
  try {
    const response = await axios.get('/api/conversations/', {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      params: { document: documentId }
    })
    
    const conversations = response.data.results || []
    if (conversations.length > 0) {
      currentConversation.value = conversations[0]
      messages.value = currentConversation.value.messages || []
    } else {
      currentConversation.value = null
      messages.value = []
    }
  } catch (error) {
    console.error('Error fetching conversations:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load conversations', life: 3000 })
  }
}

// Create a new conversation
async function createNewConversation() {
  if (!currentDocument.value) return
  
  try {
    const response = await axios.post('/api/conversations/', 
      { document: currentDocument.value.id },
      { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
    )
    
    currentConversation.value = response.data
    messages.value = []
    toast.add({ severity: 'success', summary: 'Success', detail: 'New conversation created', life: 3000 })
  } catch (error) {
    console.error('Error creating conversation:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to create new conversation', life: 3000 })
  }
}

// Send a message in the current conversation
async function sendMessage() {
  if (!messageInput.value.trim() || !currentConversation.value || loading.value) return
  
  const userMessage = messageInput.value.trim()
  messageInput.value = ''
  
  // Add user message to the chat
  messages.value.push({
    role: 'user',
    content: userMessage,
    created_at: new Date().toISOString()
  })
  
  loading.value = true
  
  try {
    const response = await axios.post(
      `/api/conversations/${currentConversation.value.id}/chat/`,
      { message: userMessage },
      { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
    )
    
    // Add assistant response to the chat
    messages.value.push(response.data)
  } catch (error) {
    console.error('Error sending message:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to send message', life: 3000 })
  } finally {
    loading.value = false
  }
}

// Handle file selection for upload
function handleFileChange(event) {
  uploadForm.value.file = event.target.files[0]
  uploadError.value = ''
}

// Download the current PDF document
async function downloadPdf() {
  if (!currentDocument.value || !currentDocument.value.file) return
  
  try {
    // Create a link element
    const link = document.createElement('a')
    link.href = currentDocument.value.file
    link.download = `${currentDocument.value.title}.pdf`
    
    // Append to the document and trigger click
    document.body.appendChild(link)
    link.click()
    
    // Clean up
    document.body.removeChild(link)
    
    toast.add({ severity: 'success', summary: 'Success', detail: 'PDF download started', life: 3000 })
  } catch (error) {
    console.error('Error downloading PDF:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to download PDF', life: 3000 })
  }
}

// Upload a new document
async function uploadDocument() {
  if (!uploadForm.value.title || !uploadForm.value.file) {
    uploadError.value = 'Please provide both title and file'
    return
  }
  
  if (uploadForm.value.file.type !== 'application/pdf') {
    uploadError.value = 'Only PDF files are supported'
    return
  }
  
  uploading.value = true
  
  try {
    const formData = new FormData()
    formData.append('title', uploadForm.value.title)
    formData.append('file', uploadForm.value.file)
    
    const response = await axios.post('/api/documents/', formData, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'multipart/form-data'
      }
    })
    
    // Reset form and close dialog
    uploadForm.value = { title: '', file: null }
    showUploadDialog.value = false
    
    // Refresh documents list
    await fetchDocuments()
    
    toast.add({ severity: 'success', summary: 'Success', detail: 'Document uploaded successfully', life: 3000 })
  } catch (error) {
    console.error('Error uploading document:', error)
    uploadError.value = error.response?.data?.detail || 'Failed to upload document'
  } finally {
    uploading.value = false
  }
}

// Logout function
function logout() {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #121212;
  color: #ffffff;
}

.header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1.5rem;
  background: #1e1e1e;
}

.content-container {
  flex: 1;
  overflow: hidden;
}

.document-tabs {
  height: 100%;
  background: #1e1e1e;
}

.split-view {
  display: flex;
  height: calc(100vh - 130px);
  gap: 2rem;
  padding: 2rem;
  background: #121212;
}

.pdf-container {
  flex: 1;
  background-color: #1e1e1e;
  border-radius: 1rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #1e1e1e;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message-container {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.message-content {
  padding: 1.25rem;
  max-width: 80%;
  line-height: 1.6;
  font-size: 1rem;
}

.user-message {
  justify-content: flex-end;
  
  .message-content {
    background: #2c2c2c;
    color: #ffffff;
    border-radius: 1rem 1rem 0 1rem;
  }
}

.assistant-message {
  justify-content: flex-start;
  
  .message-content {
    background: #363636;
    color: #ffffff;
    border-radius: 1rem 1rem 1rem 0;
  }
}

.chat-input {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: #1e1e1e;
  border-radius: 0 0 1rem 1rem;
  padding: 1.5rem;
}

.upload-dialog {
  :deep(.p-dialog-header) {
    padding: 1.75rem;
    background: #1e1e1e;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  :deep(.p-dialog-content) {
    padding: 0;
    background: #1e1e1e;
  }

  :deep(.p-dialog-footer) {
    padding: 1.75rem;
    background: #1e1e1e;
  }

  .field {
    .p-inputtext {
      background: #2c2c2c;
      border: 2px solid rgba(255, 255, 255, 0.1);
      transition: all 0.3s ease;
      color: #ffffff;
      font-size: 1rem;

      &:hover, &:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 1px var(--primary-color);
      }
    }
  }

  .upload-input {
    background: #2c2c2c;
    transition: all 0.3s ease;

    &:hover {
      border-color: var(--primary-color);
    }

    input[type="file"] {
      color: #ffffff;
      font-size: 1rem;
    }
  }
}

.pdf-viewer-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #2c2c2c;
}

.pdf-controls {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: #1e1e1e;
  border-radius: 0 0 1rem 1rem;
  padding: 1.5rem;
}

:deep(.p-tabview-nav-link) {
  color: #ffffff !important;
  background: #2c2c2c !important;
  border: none !important;
  border-radius: 0.5rem !important;
  margin: 0 0.5rem !important;
  transition: all 0.3s ease !important;
}

:deep(.p-tabview-selected) {
  background: #4a90e2 !important;
}

:deep(.p-inputtext) {
  background: #2c2c2c !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: #ffffff !important;
  border-radius: 0.5rem !important;
}

:deep(.p-inputtext::placeholder) {
  color: rgba(255, 255, 255, 0.5) !important;
}

:deep(.p-button) {
  background: #2c2c2c !important;
  color: #ffffff !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 0.75rem !important;
  transition: all 0.3s ease !important;
  font-weight: 500 !important;
  padding: 0.75rem 1.25rem !important;
  height: auto !important;
  line-height: 1.5 !important;
}

:deep(.p-button:hover) {
  background: #363636 !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
}

:deep(.p-button:active) {
  transform: translateY(0);
  box-shadow: none !important;
}

:deep(.p-button.p-button-text) {
  background: transparent !important;
  color: #ffffff !important;
  border: none !important;
  padding: 0.5rem !important;
}

:deep(.p-button.p-button-text:hover) {
  background: rgba(255, 255, 255, 0.1) !important;
  transform: none;
  box-shadow: none !important;
}

:deep(.p-button[disabled]) {
  opacity: 0.5 !important;
  cursor: not-allowed !important;
  transform: none !important;
  box-shadow: none !important;
}
</style>