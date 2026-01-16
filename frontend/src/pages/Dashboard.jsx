import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchTickets } from '../services/api'
import { RefreshCw } from 'lucide-react'
import { format } from 'date-fns'

const statusColors = {
  NEW: 'bg-blue-100 text-blue-800',
  WAITING_ON_CUSTOMER: 'bg-yellow-100 text-yellow-800',
  READY: 'bg-green-100 text-green-800',
}

function Dashboard() {
  const [statusFilter, setStatusFilter] = useState(null)

  const { data: tickets = [], isLoading, refetch } = useQuery({
    queryKey: ['tickets', statusFilter],
    queryFn: () => fetchTickets(statusFilter),
  })

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Quote Request Dashboard
        </h1>
        <p className="text-gray-600">
          Manage customer laptop quote requests
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6 flex items-center justify-between">
        <div className="flex gap-2">
          <button
            onClick={() => setStatusFilter(null)}
            className={`px-4 py-2 rounded-md ${
              statusFilter === null
                ? 'bg-gray-900 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setStatusFilter('NEW')}
            className={`px-4 py-2 rounded-md ${
              statusFilter === 'NEW'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            New
          </button>
          <button
            onClick={() => setStatusFilter('WAITING_ON_CUSTOMER')}
            className={`px-4 py-2 rounded-md ${
              statusFilter === 'WAITING_ON_CUSTOMER'
                ? 'bg-yellow-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Waiting
          </button>
          <button
            onClick={() => setStatusFilter('READY')}
            className={`px-4 py-2 rounded-md ${
              statusFilter === 'READY'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Ready
          </button>
        </div>

        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-md text-gray-700"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {/* Tickets Grid */}
      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Loading...</div>
      ) : tickets.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-500 text-lg">No tickets found</p>
          <p className="text-gray-400 text-sm mt-2">
            Send a test email to /dev/receive-email to create a ticket
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {tickets.map((ticket) => (
            <Link
              key={ticket.id}
              to={`/tickets/${ticket.id}`}
              className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="text-sm font-mono text-gray-500">
                    {ticket.ticket_number}
                  </p>
                  <h3 className="text-lg font-semibold text-gray-900 mt-1">
                    {ticket.customer_name || 'Unknown Customer'}
                  </h3>
                </div>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${
                    statusColors[ticket.status]
                  }`}
                >
                  {ticket.status.replace(/_/g, ' ')}
                </span>
              </div>

              <p className="text-sm text-gray-600 mb-4">{ticket.customer_email}</p>

              {ticket.extracted_data && (
                <div className="text-xs text-gray-500">
                  {ticket.extracted_data.laptop_model && (
                    <p className="truncate">
                      📱 {ticket.extracted_data.laptop_model}
                    </p>
                  )}
                  {ticket.extracted_data.quantity && (
                    <p>📦 Qty: {ticket.extracted_data.quantity}</p>
                  )}
                </div>
              )}

              <p className="text-xs text-gray-400 mt-4">
                Created {format(new Date(ticket.created_at), 'MMM d, yyyy')}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default Dashboard
