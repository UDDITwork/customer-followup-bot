import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const fetchTickets = async (status = null) => {
  const params = status ? { status } : {}
  const response = await api.get('/tickets/', { params })
  return response.data
}

export const fetchTicketDetails = async (id) => {
  const response = await api.get(`/tickets/${id}`)
  return response.data
}

export const updateTicket = async (id, data) => {
  const response = await api.patch(`/tickets/${id}`, data)
  return response.data
}

export const sendFollowup = async (id, subject, body) => {
  const response = await api.post(`/tickets/${id}/send-email`, null, {
    params: { subject, body },
  })
  return response.data
}

export const simulateEmail = async (emailData) => {
  const response = await api.post('/dev/receive-email', emailData)
  return response.data
}

export const getSentEmails = async () => {
  const response = await api.get('/dev/sent-emails')
  return response.data
}

export default api
